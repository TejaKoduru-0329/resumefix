from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
import os
from .models import ResumeAnalysis
from .utils import (
    clean_resume_text,
    extract_text_from_pdf,
    extract_text_from_docx,
    convert_docx_to_pdf,
    parse_resume_sections,
    extract_jd_keywords,
    generate_ats_resume_text,
    generate_ats_pdf
)


# =====================================================
# BASIC PAGES
# =====================================================

def home(request):
    return render(request, 'core/index.html')


@login_required(login_url='login')
def main_home(request):
    return render(request, 'core/home.html')


# =====================================================
# AUTH
# =====================================================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password1")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("main_home")

        messages.error(request, "Invalid Username or Password")

    return render(request, 'core/login.html')


def signup_view(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, 'core/signup.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# =====================================================
# UPLOAD + PARSE RESUME
# =====================================================

@login_required(login_url='login')
def upload_view(request):
    context = {}

    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        job_desc = request.POST.get("job_description", "").strip()

        if not resume_file or not job_desc:
            messages.error(request, "Resume and Job Description are required.")
            return render(request, "core/upload_page.html", context)

        analysis = ResumeAnalysis.objects.create(
            user=request.user,
            resume_file=resume_file,
            job_description=job_desc
        )

        file_path = analysis.resume_file.path

        # -----------------------------
        # FILE HANDLING
        # -----------------------------
        if file_path.endswith(".docx"):
            convert_docx_to_pdf(file_path)
            preview_pdf_url = analysis.resume_file.url.replace(".docx", ".pdf")
            raw_text = extract_text_from_docx(file_path)

        elif file_path.endswith(".pdf"):
            preview_pdf_url = analysis.resume_file.url
            raw_text = extract_text_from_pdf(file_path)

        else:
            messages.error(request, "Unsupported file format.")
            return render(request, "core/upload_page.html", context)

        # -----------------------------
        # CLEAN + PARSE
        # -----------------------------
        cleaned_text = clean_resume_text(raw_text)
        sections = parse_resume_sections(cleaned_text)

        # -----------------------------
        # ANALYZE JD & OPTIMIZE
        # -----------------------------
        jd_keywords = extract_jd_keywords(job_desc)
        optimized_text = generate_ats_resume_text(sections, jd_keywords)

        analysis.before_text = cleaned_text
        analysis.after_text = optimized_text
        analysis.save()

        # -----------------------------
        # GENERATE OPTIMIZED PDF
        # -----------------------------
        optimized_pdf_path = os.path.join('media', 'resumes', f"optimized_{analysis.id}.pdf")
        generate_ats_pdf(sections, jd_keywords, optimized_pdf_path)

        # -----------------------------
        # PREPARE OPTIMIZED SECTIONS FOR DISPLAY
        # -----------------------------
        from .utils import (
            optimize_professional_summary,
            optimize_technical_skills,
            optimize_work_experience,
            optimize_projects,
            format_projects_html
        )

        optimized_summary = optimize_professional_summary(sections['objective'], jd_keywords)
        optimized_skills = optimize_technical_skills(sections['technical_skills'], jd_keywords)
        optimized_experience = optimize_work_experience(sections['work_experience'], jd_keywords)
        optimized_projects = optimize_projects(sections['projects'], jd_keywords)
        optimized_projects_html = format_projects_html(optimized_projects)

        # -----------------------------
        # CONTEXT
        # -----------------------------
        context.update({
            "analysis": analysis,
            "preview_pdf_url": preview_pdf_url,
            "file_type": "pdf",
            "show_preview": True,

            "name": sections["name"],
            "phone": sections["phone"],
            "email": sections["email"],
            "dob": sections["dob"],
            "location": sections["location"],

            "objective": optimized_summary,
            "education": sections["education_html"],
            "projects": optimized_projects_html,

            "technical_skills": ", ".join(optimized_skills),
            "soft_skills": ", ".join(sections["soft_skills"]),
            "languages": sections["languages"],
            "work_experience": optimized_experience,

            "optimized_pdf_url": f"/media/resumes/optimized_{analysis.id}.pdf"
        })

    return render(request, "core/upload_page.html", context)


@login_required(login_url='login')
def download_optimized_resume(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, user=request.user)
    
    pdf_path = os.path.join('media', 'resumes', f"optimized_{analysis.id}.pdf")
    if not os.path.exists(pdf_path):
        raise Http404("Optimized resume not found")
    
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ATS_Optimized_Resume.pdf"'
        return response
