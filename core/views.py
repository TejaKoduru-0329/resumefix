from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
import os
from .models import ResumeAnalysis

from .utils import extract_text_from_pdf, get_ai_optimized_resume, generate_ats_pdf, extract_text_from_docx


# lANDING + HOME PAGES

def home(request):
    return render(request, 'core/index.html')


@login_required(login_url='login')
def main_home(request):
    return render(request, 'core/home.html')


# AUTHENTICATION VIEWS

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



# # UPLOAD + PARSE RESUME

# @login_required(login_url='login')
# def upload_view(request):

#     if request.method == "POST":
#         resume_file = request.FILES.get("resume")
#         job_desc = request.POST.get("job_description", "")

#         file_name = resume_file.name.lower()

#         if file_name.endswith(".pdf"):
#             raw_text = extract_text_from_pdf(resume_file)
#         elif file_name.endswith(".docx"):
#             raw_text = extract_text_from_docx(resume_file)
#         else:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Unsupported file format. Please upload PDF or DOCX."
#             })

        
#         # Check if same resume + JD already processed
#         existing_analysis = ResumeAnalysis.objects.filter(
#             user=request.user,
#             before_text=raw_text,
#             job_description=job_desc
#         ).last()

#         if existing_analysis:
#             # Reuse old AI result (NO Gemini call)
#             optimized_content = existing_analysis.optimized_content
#             analysis = existing_analysis
#         else:
#             # Gemini call with SAFE error handling
#             try:
#                 optimized_content = get_ai_optimized_resume(raw_text, job_desc)
#             except Exception:
#                 return JsonResponse({
#                     "success": False,
#                     "messasge": "AI usage limit reached. Please wait a minute and try again."
#                 }, status=429)

#             analysis = ResumeAnalysis.objects.create(
#                 user=request.user,
#                 resume_file=resume_file,
#                 job_description=job_desc,
#                 before_text=raw_text,
#                 optimized_content=optimized_content
#             )

#         # Generate PDF
#         pdf_filename = f"optimized_{analysis.id}.pdf"
#         output_path = os.path.join('media', 'resumes', pdf_filename)
#         generate_ats_pdf(optimized_content, output_path)

#         return render(request, "core/upload_page.html", {
#             "optimized_text": optimized_content,
#             "analysis_id": analysis.id
#         })

#     # GET request (page reload / back arrow)
#     last_analysis = ResumeAnalysis.objects.filter(user=request.user).last()

#     return render(request, "core/upload_page.html", {
#         "optimized_text": last_analysis.optimized_content if last_analysis else "",
#         "analysis_id": last_analysis.id if last_analysis else None
#     })
    

# @login_required(login_url='login')
# def fix_resume_api(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "Invalid request method"})

#     resume_file = request.FILES.get("resume")
#     job_desc = request.POST.get("job_description", "")

#     if not resume_file or not job_desc:
#         return JsonResponse({"success": False, "error": "Missing resume or job description"})

#     try:
#         file_name = resume_file.name.lower()

#         if file_name.endswith(".pdf"):
#             raw_text = extract_text_from_pdf(resume_file)
#         elif file_name.endswith(".docx"):
#             raw_text = extract_text_from_docx(resume_file)
#         else:
#             return JsonResponse({
#                 "success": False,
#                 "error": "Only PDF or DOCX files are supported"
#             })

#         optimized_content = get_ai_optimized_resume(raw_text, job_desc)

#         analysis = ResumeAnalysis.objects.create(
#             user=request.user,
#             resume_file=resume_file,
#             job_description=job_desc,
#             before_text=raw_text,
#             optimized_content=optimized_content
#         )

#         return JsonResponse({
#             "success": True,
#             "before_text": raw_text,
#             "optimized_content": optimized_content,
#             "analysis_id": analysis.id
#         })

#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})


# @login_required(login_url='login')
# def download_resume(request, analysis_id):
#     analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)

#     pdf_filename = f"resume_{analysis.id}.pdf"
#     pdf_path = os.path.join("media", "generated", pdf_filename)

#     os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    
#     # NEW: get selected template OR fallback to default
#     # template = request.session.get("selected_template", "classic")

#     # Generate ATS-safe PDF
#     generate_ats_pdf(analysis.optimized_content, pdf_path)

#     with open(pdf_path, "rb") as pdf:
#         response = HttpResponse(pdf.read(), content_type="application/pdf")
#         response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
#         request.session.pop("selected_template", None)
#         return response












### New upload + parse view with better error handling and caching of results

# UPLOAD PAGE (HTML ONLY)

@login_required(login_url='login')
def upload_view(request):
    # Load last analysis for preview (back arrow / refresh safe)
    last_analysis = ResumeAnalysis.objects.filter(user=request.user).last()

    return render(request, "core/upload_page.html", {
        "before_text": last_analysis.before_text if last_analysis else "",
        "optimized_text": last_analysis.optimized_content if last_analysis else "",
        "analysis_id": last_analysis.id if last_analysis else None
    })


# FIX RESUME API (AI ONLY)

@login_required(login_url='login')
def fix_resume_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    resume_file = request.FILES.get("resume")
    job_desc = request.POST.get("job_description", "")

    if not resume_file:
        return JsonResponse({"success": False, "message": "Resume file missing"})

    file_name = resume_file.name.lower()

    if file_name.endswith(".pdf"):
        raw_text = extract_text_from_pdf(resume_file)
    elif file_name.endswith(".docx"):
        raw_text = extract_text_from_docx(resume_file)
    else:
        return JsonResponse({
            "success": False,
            "message": "Only PDF or DOCX files are supported"
        })

    # 🔥 CACHE CHECK (Gemini only once)
    existing_analysis = ResumeAnalysis.objects.filter(
        user=request.user,
        # before_text=raw_text,
        resume_file__icontains=resume_file.name,
        job_description=job_desc
    ).last()

    if existing_analysis:
        analysis = existing_analysis
    else:
        try:
            optimized_content = get_ai_optimized_resume(raw_text, job_desc)
        except Exception:
            return JsonResponse({
                "success": False,
                "message": "AI usage limit reached. Please wait a minute and try again."
            }, status=429)

        analysis = ResumeAnalysis.objects.create(
            user=request.user,
            resume_file=resume_file,
            job_description=job_desc,
            before_text=raw_text,
            optimized_content=optimized_content
        )

    request.session["analysis_id"] = analysis.id

    return JsonResponse({
        "success": True,
        "before_text": analysis.before_text,
        "optimized_text": analysis.optimized_content,
        "analysis_id": analysis.id
    })


@login_required(login_url='login')
def download_resume(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)

    pdf_filename = f"resume_{analysis.id}.pdf"
    pdf_path = os.path.join("media", "generated", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    template = request.session.get("selected_template", "classic")

    generate_ats_pdf(
        analysis.optimized_content,
        pdf_path,
        template
    )

    request.session.pop("selected_template", None)

    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        return response
    

from django.http import HttpResponse
from .utils import render_resume_html
import json

def resume_preview(request):

    template = request.GET.get("template", "classic")

    analysis_id = request.session.get("analysis_id")

    analysis = ResumeAnalysis.objects.get(id=analysis_id)

    optimized_text = analysis.optimized_resume

    html = render_resume_html(optimized_text, template)

    return HttpResponse(html)


def select_template(request):
    body = json.loads(request.body)
    request.session["selected_template"] = body["template"]
    return HttpResponse("OK")

# def template_preview_page(request):
#     analysis = ResumeAnalysis.objects.filter(user=request.user).last()
#     return render(request, "core/template_preview.html", {
#         "analysis_id": analysis.id if analysis else None
#     })

def template_preview_page(request):
    analysis_id = request.session.get("analysis_id")
    analysis = ResumeAnalysis.objects.get(id=analysis_id)

    return render(request, "core/template_preview.html", {
        "optimized_text": analysis.optimized_resume,
        "analysis_id": analysis_id
    })