from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
import os
from .models import ResumeAnalysis

from .utils import extract_text_from_pdf, get_ai_optimized_resume, generate_ats_pdf, extract_text_from_docx


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
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        job_desc = request.POST.get("job_description", "")

        # 1. Get raw text
        # raw_text = extract_text_from_pdf(resume_file)
        file_name = resume_file.name.lower()

        if file_name.endswith(".pdf"):
            raw_text = extract_text_from_pdf(resume_file)
        elif file_name.endswith(".docx"):
            raw_text = extract_text_from_docx(resume_file)
        else:
            return JsonResponse({
                "success": False,
                "error": "Unsupported file format. Please upload PDF or DOCX."
            })
        
        # 2. Let Gemini fix it (The AI Brain)
        optimized_content = get_ai_optimized_resume(raw_text, job_desc)
        
        # 3. Save to your existing model
        analysis = ResumeAnalysis.objects.create(
            user=request.user,
            resume_file=resume_file,
            job_description=job_desc,
            before_text=raw_text,
            optimized_content=optimized_content
        )
        
        # 4. Generate the new PDF
        pdf_filename = f"optimized_{analysis.id}.pdf"
        output_path = os.path.join('media', 'resumes', pdf_filename)
        generate_ats_pdf(optimized_content, output_path)

        return render(request, "core/upload_page.html", {
            "optimized_text": optimized_content,
            "analysis_id": analysis.id
        })
    return render(request, "core/upload_page.html")
    

@login_required(login_url='login')
def fix_resume_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    resume_file = request.FILES.get("resume")
    job_desc = request.POST.get("job_description", "")

    if not resume_file or not job_desc:
        return JsonResponse({"success": False, "error": "Missing resume or job description"})

    try:
        file_name = resume_file.name.lower()

        if file_name.endswith(".pdf"):
            raw_text = extract_text_from_pdf(resume_file)
        elif file_name.endswith(".docx"):
            raw_text = extract_text_from_docx(resume_file)
        else:
            return JsonResponse({
                "success": False,
                "error": "Only PDF or DOCX files are supported"
            })

        optimized_content = get_ai_optimized_resume(raw_text, job_desc)

        analysis = ResumeAnalysis.objects.create(
            user=request.user,
            resume_file=resume_file,
            job_description=job_desc,
            before_text=raw_text,
            optimized_content=optimized_content
        )

        return JsonResponse({
            "success": True,
            "before_text": raw_text,
            "optimized_content": optimized_content,
            "analysis_id": analysis.id
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# def download_resume(request, analysis_id):
#     analysis = ResumeAnalysis.objects.get(id=analysis_id)

#     response = HttpResponse(
#         analysis.optimized_content,
#         content_type='text/plain'
#     )
#     response['Content-Disposition'] = 'attachment; filename="optimized_resume.txt"'
#     return response

@login_required(login_url='login')
def download_resume(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)

    pdf_filename = f"resume_{analysis.id}.pdf"
    pdf_path = os.path.join("media", "generated", pdf_filename)

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Generate ATS-safe PDF
    generate_ats_pdf(analysis.optimized_content, pdf_path)

    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        return response