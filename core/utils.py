
import re
import pdfplumber
from docx import Document
from pyparsing import line
from reportlab.platypus import ListItem, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
# from google import genai
import google.generativeai as genai

import re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, ListFlowable, Spacer, KeepTogether, ListItem
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4

from .template_config import RESUME_TEMPLATES

# Configure Gemini ONCE
# client = genai.Client(api_key=settings.GEMINI_API_KEY)
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# 1. TEXT EXTRACTION
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


# 2. AI BRAIN

import requests
from django.conf import settings

def get_ai_optimized_resume(resume_text, job_description):
    url = (
        "https://generativelanguage.googleapis.com/v1/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )

    prompt = f"""
You are an ATS-optimized resume rewriting engine.

Your task is to rewrite the given resume content to match the provided Job Description.
Return ONLY the resume content. Do NOT add explanations, comments, introductions, or titles.

==============================
GLOBAL RULES (STRICT)
==============================

- Output PLAIN TEXT ONLY
- Do NOT use HTML, CSS, emojis, or markdown lists
- Use **double asterisks** ONLY for section headings (example: **EDUCATION**)
- Use normal line breaks only
- Do NOT add extra blank lines between sections
- Start directly with the candidate’s NAME (first line)
- Preserve and include ALL contact details exactly as present in the original resume
  (phone, email, DOB, nationality, links, etc.)
- Do NOT include phrases like “Here is a rewritten resume”

==============================
CANDIDATE TYPE DETECTION (CRITICAL)
==============================

Analyze the resume content and determine the candidate type:

1) FRESHER
- No full-time work experience
- May have academic projects
- May or may not have internships
- Keywords may include: Fresher, Graduate, Student, Entry-Level

2) INTERN / EARLY-CAREER
- Has internships, traineeships, or apprenticeship experience
- No full-time employment yet

3) EXPERIENCED
- Has one or more full-time roles
- Company names, job titles, and durations present

==============================
SUMMARY HEADING AUTO-SWITCH
==============================

- If candidate is FRESHER or INTERN:
  Use heading EXACTLY as: **CAREER OBJECTIVE**

- If candidate is EXPERIENCED:
  Use heading EXACTLY as: **PROFESSIONAL SUMMARY**

==============================
WORK EXPERIENCE RULES
==============================

- Create a **WORK EXPERIENCE** section if the resume contains:
  - Internships, traineeships, or apprenticeships
  - OR full-time professional roles

- INTERN / EARLY-CAREER:
  - List internships under **WORK EXPERIENCE**
  - Clearly label roles as Intern / Trainee

- EXPERIENCED:
  - List all professional roles under **WORK EXPERIENCE**

- Do NOT create WORK EXPERIENCE section for pure freshers with no internships

==============================
SECTION HEADINGS (EXACT ORDER)
==============================

Use ONLY these headings, in this exact order (include only applicable sections):

**CAREER OBJECTIVE** or **PROFESSIONAL SUMMARY**
**WORK EXPERIENCE** (only if applicable)
**EDUCATION**
**TECHNICAL SKILLS**
**PROJECTS**
**SOFT SKILLS**
**LANGUAGES KNOWN**
**CERTIFICATIONS**

Do NOT use generic headings like “SKILLS”.

==============================
SUMMARY CONTENT RULES
==============================

FRESHER / INTERN (CAREER OBJECTIVE):
- 2–3 concise lines
- Focus on fundamentals, academic projects, internships, learning ability
- Align with the Job Description
- Do NOT exaggerate experience
- Do NOT use bullet points

EXPERIENCED (PROFESSIONAL SUMMARY):
- 3–4 concise lines
- Highlight years of experience, core skills, domain impact
- Strongly align with the Job Description
- Do NOT fabricate experience
- Do NOT use bullet points

==============================
EDUCATION FORMAT (MANDATORY)
==============================

For EACH education entry, output EXACTLY TWO LINES:

Line 1:
<Institution Name>, <Location> <Year>

Line 2:
<Degree / Qualification> | GPA or CGPA: <value>

Rules:
- Year MUST be on the same line as institution and location
- Degree/qualification MUST be on the next line
- Preserve whether it is GPA or CGPA exactly as in the original resume
- Do NOT convert GPA to CGPA or vice versa
- Do NOT show scale (/10, out of 10)
- Follow this format strictly for ALL education entries

==============================
BULLET NORMALIZATION (CRITICAL)
==============================

- Convert ALL bullet styles into a single bullet character: "•"
- This includes:
  - Hyphens (-)
  - Numbers (1., 2.)
  - Roman numerals (i, ii, iii)
  - Alphabet bullets (a, b, c)
  - Special MS Word symbols
- Do NOT use numbered lists
- Use ONLY the "•" bullet symbol everywhere

==============================
TECHNICAL SKILLS RULES
==============================

- Always create a **TECHNICAL SKILLS** section
- Present skills in this exact categorized format (single line per category):

Programming Languages: <comma-separated values>
Frameworks & Libraries: <comma-separated values>
Databases: <comma-separated values>
Tools & Platforms: <comma-separated values>

Rules:
- If skills are missing or poorly structured:
  - Extract relevant keywords from the Job Description
- Do NOT invent unrelated skills
- Do NOT include soft skills here
- Do NOT split category names and values into separate lines

==============================
PROJECTS FORMAT
==============================

- Project title on ONE line (no bullets)
- Follow with bullet points using "•"
- Bullet points should describe:
  - What was built
  - Technologies used
  - Functionality or impact
- Do NOT include dates unless explicitly present in the original resume
- Do NOT merge multiple projects into one

==============================
SOFT SKILLS RULES
==============================

- Always create a **SOFT SKILLS** section
- If soft skills are missing:
  - Infer role-relevant soft skills from the Job Description
- Present soft skills ONLY as bullet points using "•"
- Do NOT include technical skills here

==============================
LANGUAGES KNOWN RULES
==============================

- Always create a **LANGUAGES KNOWN** section
- Use ONLY languages explicitly mentioned in the original resume
- Do NOT infer or assume languages
- Do NOT include proficiency levels
- Present each language as a bullet point using "•"
- Do NOT mix languages with skills

==============================
CERTIFICATIONS RULES
==============================

- Include certifications only if present in the original resume
- Preserve certification names exactly
- Do NOT invent certifications

==============================
FINAL CONSTRAINTS
==============================

- Do NOT change factual details (education, years, institutions, scores)
- Improve clarity and ATS keyword relevance
- Keep language professional and concise
- Ensure structure is consistent and predictable
- Do NOT add or remove sections arbitrarily

==============================
INPUT
==============================

Resume:
{resume_text}

Job Description:
{job_description}
"""
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(url, json=payload, timeout=60)
    data = response.json()

    if "candidates" not in data:
        raise Exception(data)

    return data["candidates"][0]["content"]["parts"][0]["text"]
        

# 3. PDF GENERATION
def generate_ats_pdf(text, output_path, template_key="classic"):

    # ✅ template config (SAFE)
    style_cfg = RESUME_TEMPLATES.get(template_key, RESUME_TEMPLATES["classic"])

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story = []

    # ---------- STYLES ----------
    name_style = ParagraphStyle(
        "Name",
        fontName=f"{style_cfg['font']}-Bold" if style_cfg["font"] == "Helvetica" else style_cfg["font"],
        fontSize=14,
        spaceAfter=6
    )

    heading_style = ParagraphStyle(
        "Heading",
        fontName=f"{style_cfg['font']}-Bold",
        fontSize=style_cfg["heading_size"]
    )

    body_style = ParagraphStyle(
        "Body",
        fontName=style_cfg["font"],
        fontSize=style_cfg["body_size"],
        spaceAfter=6
    )

    bold_style = ParagraphStyle(
        "Bold",
        fontName=f"{style_cfg['font']}-Bold",
        fontSize=style_cfg["body_size"]
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        fontName=style_cfg["font"],
        fontSize=style_cfg["body_size"],
        leftIndent=15,
        firstLineIndent=0,
        spaceAfter=3
    )

    project_title_style = ParagraphStyle(
        "ProjectTitle",
        fontName=f"{style_cfg['font']}-Bold",
        fontSize=style_cfg["body_size"]
    )

    lines = text.split("\n")

    current_section = None
    section_elements = []
    bullets = []

    
    def flush_bullets_into_section():
        nonlocal bullets, section_elements

        if not bullets:
            return

        clean_items = []

        for b in bullets:

            text_content = re.sub(r"^[\s]*([0-9A-Za-z]+[\.\)]|[•\-\s]+)", "", b).strip()

            clean_items.append(
                ListItem(
                    Paragraph(text_content, bullet_style),
                    bulletText="•", 
                    leftIndent=15,
                    bulletColor='black',
                )
            )

        section_elements.append(
            ListFlowable(
                clean_items,
                bulletType='bullet',
                leftIndent=00,
                bulletIndent=0,
                # bulletFontSize=10,
                spaceAfter=6
            )
        )

        bullets = []

    def flush_section():
        nonlocal section_elements
        if section_elements:
            story.append(KeepTogether(section_elements))
            section_elements = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # NAME
        if i == 0:
            story.append(Paragraph(line, name_style))
            i += 1
            continue

        # SECTION HEADING
        if line.startswith("**") and line.endswith("**"):
            flush_bullets_into_section()
            flush_section()

            current_section = line.replace("*", "")

            section_elements = [
                Paragraph(current_section, heading_style),
                HRFlowable(width="100%", thickness=0.7),
                Spacer(1, 4)
            ]
            i += 1
            continue

        # EDUCATION
        if current_section == "EDUCATION":
            line1 = line
            line2 = lines[i + 1].strip() if i + 1 < len(lines) else ""

            section_elements.append(Paragraph(line1, bold_style))
            section_elements.append(Paragraph(line2, body_style))
            section_elements.append(Spacer(1, 8))

            i += 2
            continue

        # BULLETS
        bullet_match = re.match(r"^(\d+[\.\)]\s+|[A-Za-z][\.\)]\s+|[•\-]\s*)(.+)", line)

        if bullet_match:
            bullets.append(line)
            i += 1
            continue

        # PROJECT / EXPERIENCE TITLE
        if current_section in ("PROJECTS", "WORK EXPERIENCE"):
            flush_bullets_into_section()
            section_elements.append(Paragraph(line, project_title_style))
            i += 1
            continue

        # TECHNICAL SKILLS
        if current_section == "TECHNICAL SKILLS" and ":" in line:
            left, right = line.split(":", 1)
            section_elements.append(
                Paragraph(f"<b>{left}:</b> {right.strip()}", body_style)
            )
            i += 1
            continue

        # NORMAL TEXT
        flush_bullets_into_section()
        section_elements.append(Paragraph(line, body_style))
        i += 1

    flush_bullets_into_section()
    flush_section()

    doc.build(story)


# 4. HTML RENDERING (FOR PREVIEW)
from .template_config import RESUME_TEMPLATES

def render_resume_html(data, template_key):
    style = RESUME_TEMPLATES.get(template_key, RESUME_TEMPLATES["classic"])

    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: {style['font']};
                font-size: {style['body_size']}px;
            }}
            h2 {{
                font-size: {style['heading_size']}px;
                font-weight: bold;
                border-bottom: 1px solid #000;
                margin-bottom: {style['line_gap']}px;
            }}
            ul {{
                margin-left: {style['bullet_indent']}px;
            }}
        </style>
    </head>
    <body>
        <h2>Education</h2>
        <p>{data['education']}</p>

        <h2>Skills</h2>
        <ul>
            {''.join(f"<li>{s}</li>" for s in data['skills'])}
        </ul>
    </body>
    </html>
    """