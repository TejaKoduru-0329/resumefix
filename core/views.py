from pydoc import plain

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
import os
import re
import json
import time
from .models import ResumeAnalysis
from .utils import extract_text_from_pdf, get_ai_optimized_resume, generate_ats_pdf, extract_text_from_docx, get_cover_letter, render_resume_html, generate_cover_letter_pdf
from django.contrib.messages import get_messages

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from payments.models import UserPlan


# ── CREDIT HELPERS (DB based) ──
FREE_LIMIT = 2

def get_or_create_plan(user):
    plan, _ = UserPlan.objects.get_or_create(user=user)
    return plan

def get_credits(request):
    plan = get_or_create_plan(request.user)
    return plan.resumes_remaining()

def use_credit(request):
    plan = get_or_create_plan(request.user)
    plan.use_resume()

def has_credits(request):
    plan = get_or_create_plan(request.user)
    return plan.can_generate()


# ── ATS SCORE CALCULATOR ──
def calculate_ats_score(before_text, after_text, job_desc):
    stop_words = {
        'that', 'this', 'with', 'from', 'will', 'have', 'been', 'they',
        'your', 'also', 'more', 'must', 'work', 'able', 'about', 'after',
        'their', 'when', 'which', 'would', 'should', 'could', 'other',
        'these', 'those', 'such', 'into', 'over', 'then', 'than', 'very',
        'what', 'some', 'team', 'role', 'good', 'well', 'each', 'both',
        'make', 'take', 'come', 'know', 'like', 'time', 'just', 'need',
        'here', 'even', 'back', 'only', 'best', 'many', 'much', 'high',
        'them', 'were', 'said', 'same', 'want', 'look', 'right', 'next',
        'bake', 'abap', 'amdp', 'assemble', 'approximately', 'assets',
        'across', 'accelerate', 'anticipate', 'accenture'
    }

    def extract_keywords(text):
        words = set(re.findall(r'\b[a-zA-Z]{5,}\b', text.lower()))
        extended_stops = stop_words | {
            'basic', 'below', 'broad', 'basis', 'cases', 'carry', 'being',
            'shall', 'while', 'since', 'where', 'there', 'under', 'using',
            'given', 'place', 'point', 'range', 'level', 'local', 'large',
            'small', 'short', 'check', 'might', 'light', 'along', 'every',
            'never', 'still', 'again', 'often', 'early', 'least', 'among',
            'above', 'below', 'between', 'through', 'during', 'before',
            'having', 'making', 'taking', 'giving', 'coming', 'going',
            'working', 'looking', 'getting', 'including', 'following',
            'carried', 'approximately', 'assemble', 'anticipate', 'accelerate',
            # extra common words
            'ability', 'aptitude', 'citizen', 'change', 'analyze', 'analysis',
            'businesses', 'capability', 'challenging', 'clients', 'client',
            'deliver', 'delivery', 'apply', 'agility', 'faster', 'build',
            'design', 'designs', 'associate', 'application', 'applications'
        }
        return words - extended_stops

    jd_keywords  = extract_keywords(job_desc)
    before_words = extract_keywords(before_text)
    after_words  = extract_keywords(after_text)

    matched_before = jd_keywords & before_words
    matched_after  = jd_keywords & after_words
    missing        = jd_keywords - after_words
    added          = matched_after - matched_before

    before_score = round((len(matched_before) / len(jd_keywords)) * 100) if jd_keywords else 0
    after_score  = round((len(matched_after)  / len(jd_keywords)) * 100) if jd_keywords else 0

    return {
        "before_score":          min(before_score, 100),
        "after_score":           min(after_score, 100),
        "matched_keywords":      sorted(list(matched_after))[:15],
        "missing_keywords":      sorted(list(missing))[:10],
        "added_keywords":        sorted(list(added))[:10],
        "keyword_match_percent": min(after_score, 100)
    }


# LANDING + HOME PAGES
def home(request):
    return render(request, 'core/index.html')


@login_required(login_url='login')
def main_home(request):
    return render(request, 'core/home.html')


# AUTHENTICATION VIEWS
def login_view(request):
    
    list(get_messages(request))

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
        firstname  = request.POST.get("firstname")
        lastname   = request.POST.get("lastname")
        username   = request.POST.get("username")
        email      = request.POST.get("email")
        password1  = request.POST.get("password1")
        password2  = request.POST.get("password2")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        # Create user but inactive until email verified
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.first_name = firstname
        user.last_name  = lastname
        user.is_active  = False  # inactive until verified
        user.save()

        # Generate verification token
        token = default_token_generator.make_token(user)
        uid   = urlsafe_base64_encode(force_bytes(user.pk))

        # Verification link
        verification_link = f"http://127.0.0.1:8000/verify-email/{uid}/{token}/"

        # Send email
        send_mail(
            subject="Verify your ResumeFix.ai account",
            message=f"""Hi {firstname},

Welcome to ResumeFix.ai!

Please click the link below to verify your email address:

{verification_link}

This link will expire after some time.

If you did not create an account, please ignore this email.

Thanks,
ResumeFix.ai Team""",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Account created! Please check your email to verify your account.")
        return redirect("login")

    return render(request, 'core/signup.html')


def verify_email(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified successfully! You can now login.")
        return redirect("login")
    else:
        messages.error(request, "Verification link is invalid or expired.")
        return redirect("signup")

@login_required
def logout_view(request):
    list(get_messages(request)) 
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# UPLOAD PAGE (HTML ONLY)
@login_required(login_url='login')
def upload_view(request):
    last_analysis = ResumeAnalysis.objects.filter(user=request.user).last()
    plan = get_or_create_plan(request.user) 
    return render(request, "core/upload_page.html", {
        "before_text":    last_analysis.before_text        if last_analysis else "",
        "optimized_text": last_analysis.optimized_content  if last_analysis else "",
        "analysis_id":    last_analysis.id                 if last_analysis else None,
        "credits":        plan.resumes_remaining(),
    })


# FIX RESUME API (AI ONLY)
@login_required(login_url='login')
def fix_resume_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    resume_file = request.FILES.get("resume")
    job_desc    = request.POST.get("job_description", "")

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

    # ── GROQ API CALL ──
    optimized_content = None

    try:
        start = time.time()
        optimized_content = get_ai_optimized_resume(raw_text, job_desc)
        print("AI OUTPUT FIRST 500 CHARS:", optimized_content[:500])
        print(f"GROQ TIME: {time.time() - start:.2f}s")
    except Exception as e:
        print("GROQ ERROR:", str(e))
        time.sleep(5)
        try:
            optimized_content = get_ai_optimized_resume(raw_text, job_desc)
            print("AI OUTPUT FIRST 500 CHARS:", optimized_content[:500])
        except Exception as e2:
            print("GROQ RETRY FAILED:", str(e2))

    if not optimized_content:
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

    # ── ATS SCORE ──
    ats_data = calculate_ats_score(raw_text, optimized_content, job_desc)

    return JsonResponse({
        "success":        True,
        "before_text":    analysis.before_text,
        "optimized_text": analysis.optimized_content,
        "analysis_id":    analysis.id,
        "ats_score":      ats_data
    })


@login_required(login_url='login')
def download_resume(request, analysis_id):
    # ── Credit Check ──
    if not has_credits(request):
        return redirect('payments:payment_page')

    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)
    pdf_filename = f"resume_{analysis.id}.pdf"
    pdf_path = os.path.join("media", "generated", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    template = request.session.get("selected_template", "classic")
    generate_ats_pdf(analysis.optimized_content, pdf_path, template)
    request.session.pop("selected_template", None)

    # ── Use 1 Credit ──
    use_credit(request)

    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        return response


def resume_preview(request):
    template    = request.GET.get("template", "classic")
    analysis_id = request.session.get("analysis_id")
    analysis    = ResumeAnalysis.objects.get(id=analysis_id)
    html        = render_resume_html(analysis.optimized_content, template)
    return HttpResponse(html)


def select_template(request):
    body = json.loads(request.body)
    request.session["selected_template"] = body["template"]
    return HttpResponse("OK")


def template_preview_page(request):
    analysis_id = request.session.get("analysis_id")
    analysis    = ResumeAnalysis.objects.get(id=analysis_id)

    return render(request, "core/template_preview.html", {
        "classic_html": render_resume_html(analysis.optimized_content, "classic"),
        "modern_html":  render_resume_html(analysis.optimized_content, "modern"),
        "compact_html": render_resume_html(analysis.optimized_content, "compact"),
        "minimal_html": render_resume_html(analysis.optimized_content, "minimal"),
        "analysis_id":  analysis_id
    })

@login_required(login_url='login')
def download_from_template(request, analysis_id):
    # ── Credit Check ──
    if not has_credits(request):
        return redirect('payments:payment_page')

    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)
    template = request.GET.get('template', 'classic')

    pdf_filename = f"resume_{analysis.id}_{template}.pdf"
    pdf_path = os.path.join("media", "generated", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    generate_ats_pdf(analysis.optimized_content, pdf_path, template)

    # ── Use 1 Credit ──
    use_credit(request)

    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        return response

@login_required(login_url='login')
def generate_cover_letter_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    analysis_id = request.session.get("analysis_id")
    if not analysis_id:
        return JsonResponse({"success": False, "message": "No resume found"})

    analysis = ResumeAnalysis.objects.get(id=analysis_id)
    
    try:
        cover_letter = get_cover_letter(analysis.optimized_content, analysis.job_description)
    except Exception as e:
        print("COVER LETTER ERROR:", str(e))
        return JsonResponse({"success": False, "message": "Failed to generate cover letter"})

    return JsonResponse({
        "success": True,
        "cover_letter": cover_letter
    })


@login_required(login_url='login')  
def download_cover_letter(request):
    analysis_id = request.session.get("analysis_id")
    analysis = ResumeAnalysis.objects.get(id=analysis_id)
    
    cover_letter = request.POST.get("cover_letter", "")
    
    pdf_filename = f"cover_letter_{analysis.id}.pdf"
    pdf_path = os.path.join("media", "generated", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    from .utils import generate_cover_letter_pdf
    generate_cover_letter_pdf(cover_letter, pdf_path)
    
    with open(pdf_path, "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        return response


@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")

        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        request.user.set_password(new_password1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully!")
        return redirect("main_home")

    return render(request, 'core/change_password.html')
