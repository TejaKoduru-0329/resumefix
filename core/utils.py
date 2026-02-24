# import re
# import os
# import pdfplumber
# from docx import Document
# from docx2pdf import convert
# from collections import defaultdict
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.units import inch
# from reportlab.lib.enums import TA_LEFT, TA_CENTER
# from io import BytesIO

# # =====================================================
# # 1. TEXT EXTRACTION
# # =====================================================

# def extract_text_from_pdf(path):
#     text = ""
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text


# def extract_text_from_docx(path):
#     doc = Document(path)
#     return "\n".join(p.text for p in doc.paragraphs)


# # =====================================================
# # 2. CLEAN TEXT
# # =====================================================

# def clean_resume_text(text):
#     text = text.replace("\r", "\n")
#     text = re.sub(r"\n{2,}", "\n", text)
#     text = re.sub(r"[ \t]{2,}", " ", text)
#     return text.strip()


# # =====================================================
# # 3. DOCX → PDF
# # =====================================================

# def convert_docx_to_pdf(docx_path):
#     pdf_path = docx_path.replace(".docx", ".pdf")
#     if not os.path.exists(pdf_path):
#         convert(docx_path, pdf_path)
#     return pdf_path


# # =====================================================
# # 4. HEADER PARSER
# # =====================================================

# def parse_header(lines):
#     header = {
#         "name": lines[0] if lines else "",
#         "phone": "",
#         "email": "",
#         "dob": "",
#         "location": ""
#     }

#     joined = " ".join(lines[:6])

#     phone = re.search(r"(\+91[\s-]?)?\d{10}", joined)
#     if phone:
#         num = phone.group()
#         header["phone"] = num if num.startswith("+91") else "+91 " + num[-10:]

#     email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", joined)
#     if email:
#         header["email"] = email.group()

#     dob = re.search(r"\d{2}/\d{2}/\d{4}", joined)
#     if dob:
#         header["dob"] = dob.group()

#     if "india" in joined.lower():
#         header["location"] = "India"

#     return header


# # =====================================================
# # 5. SECTION SPLITTER
# # =====================================================

# SECTION_MAP = {
#     "objective": ["career objective", "profile", "summary"],
#     "education": ["education", "academic credentials"],
#     "work_experience": ["work experience", "experience", "intern"],
#     "projects": ["projects", "project"],
#     "technical_skills": ["technical skills", "skills"],
#     "languages": ["languages"]
# }


# def split_into_sections(lines):
#     sections = defaultdict(list)
#     current = None

#     for line in lines:
#         lower = line.lower()
#         for key, titles in SECTION_MAP.items():
#             if any(t in lower for t in titles):
#                 current = key
#                 break
#         else:
#             if current:
#                 sections[current].append(line)

#     return sections


# # =====================================================
# # 6. EDUCATION PARSER (CORRECT PAIRING)
# # =====================================================

# def parse_education(lines):
#     entries = []
#     i = 0

#     while i < len(lines):
#         line = lines[i]

#         # Detect institution
#         if any(k in line.lower() for k in ["university", "college", "school"]):
#             institution = line
#             qualification = ""

#             # Look ahead for qualification (next line)
#             if i + 1 < len(lines):
#                 next_line = lines[i + 1]

#                 # If next line is NOT another institution, treat as qualification
#                 if not any(k in next_line.lower() for k in ["university", "college", "school"]):
#                     qualification = next_line
#                     i += 1  # consume qualification line

#             # Fallback only for schools
#             if not qualification and "school" in institution.lower():
#                 qualification = "Secondary Education"

#             entries.append({
#                 "institution": institution,
#                 "qualification": qualification
#             })

#         i += 1

#     return entries





# def format_education_html(entries):
#     html = ""

#     for edu in entries:
#         html += "<div class='edu-entry'>"
#         html += f"<div class='edu-inst'><strong>{edu['institution']}</strong></div>"

#         if edu["qualification"]:
#             html += f"<div class='edu-qual'>{edu['qualification']}</div>"

#         html += "</div>"

#     return html





# # =====================================================
# # 7. BULLET NORMALIZER (PDF SAFE)
# # =====================================================

# BULLET_REGEX = r"^(\•|\-|\–|\→|\d+[\.\)]|[IVX]+[\.\)]|[a-zA-Z][\.\)])\s+"

# def normalize_bullets(lines):
#     fixed = []
#     buffer = ""

#     for line in lines:
#         if re.match(BULLET_REGEX, line):
#             if buffer:
#                 fixed.append(buffer.strip())
#             buffer = line
#         else:
#             buffer += " " + line.strip()

#     if buffer:
#         fixed.append(buffer.strip())

#     return fixed


# # =====================================================
# # 8. PROJECT PARSER
# # =====================================================

# def parse_projects(lines):
#     projects = []
#     current = None

#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue

#         if line.lower().startswith("title"):
#             if current:
#                 projects.append(current)
#             current = {
#                 "title": line.replace("Title:", "").strip(),
#                 "bullets": []
#             }

#         elif re.match(BULLET_REGEX, line):
#             if current:
#                 bullet = re.sub(BULLET_REGEX, "", line).strip()
#                 current["bullets"].append(bullet)

#         else:
#             # Append ONLY to previous bullet (PDF wrap)
#             if current and current["bullets"]:
#                 current["bullets"][-1] += " " + line

#     if current:
#         projects.append(current)

#     return projects



# def format_projects_html(projects):
#     html = ""
#     for p in projects:
#         html += f"<p><strong>{p['title']}</strong></p><ul>"
#         for b in p["bullets"]:
#             html += f"<li>{b}</li>"
#         html += "</ul>"
#     return html


# # =====================================================
# # 9. SKILLS
# # =====================================================

# SOFT_SKILL_HINTS = [
#     "self", "motivated", "adaptable", "leadership",
#     "responsibility", "team", "communication"
# ]


# def split_skills(text):
#     skills = [s.strip() for s in re.split(r"[•,|]", text) if s.strip()]
#     technical, soft = [], []

#     for s in skills:
#         if any(h in s.lower() for h in SOFT_SKILL_HINTS):
#             soft.append(s)
#         else:
#             technical.append(s)

#     return technical, soft


# # =====================================================
# # 11. JD ANALYSIS
# # =====================================================

# def extract_jd_keywords(job_description):
#     """Extract key skills, technologies, and requirements from JD"""
#     jd_lower = job_description.lower()
    
#     # Common tech skills and keywords
#     tech_keywords = [
#         'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
#         'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
#         'spring', 'hibernate', 'mysql', 'postgresql', 'mongodb', 'redis',
#         'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
#         'linux', 'windows', 'agile', 'scrum', 'kanban', 'ci/cd', 'api', 'rest',
#         'graphql', 'microservices', 'machine learning', 'ai', 'data science',
#         'tensorflow', 'pytorch', 'pandas', 'numpy', 'sql', 'nosql'
#     ]
    
#     found_keywords = []
#     for keyword in tech_keywords:
#         if keyword in jd_lower:
#             found_keywords.append(keyword.title() if keyword.islower() else keyword)
    
#     # Extract years of experience if mentioned
#     exp_match = re.search(r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', jd_lower)
#     experience_years = exp_match.group(1) if exp_match else None
    
#     # Extract role keywords
#     role_keywords = []
#     role_patterns = [
#         r'(?:senior|junior|lead|principal)\s*(?:software|full.?stack|backend|frontend|devops|data)\s*(?:engineer|developer|analyst)',
#         r'(?:software|full.?stack|backend|frontend|devops|data)\s*(?:engineer|developer|analyst)',
#         r'(?:product|project)\s*manager',
#         r'(?:data|business)\s*analyst'
#     ]
    
#     for pattern in role_patterns:
#         matches = re.findall(pattern, jd_lower)
#         role_keywords.extend(matches)
    
#     return {
#         'tech_keywords': list(set(found_keywords)),
#         'role_keywords': list(set(role_keywords)),
#         'experience_years': experience_years,
#         'raw_jd': job_description
#     }


# # =====================================================
# # 12. RESUME OPTIMIZATION
# # =====================================================

# def optimize_professional_summary(objective, jd_keywords):
#     """Create ATS-optimized professional summary"""
#     base_summary = objective if objective else "Experienced professional seeking new opportunities."
    
#     # Add relevant keywords from JD
#     tech_keywords = jd_keywords.get('tech_keywords', [])[:5]  # Limit to 5
#     role_keywords = jd_keywords.get('role_keywords', [])[:2]  # Limit to 2
    
#     if tech_keywords or role_keywords:
#         all_skills = tech_keywords + role_keywords
#         skills_text = ", ".join(all_skills)
#         optimized = f"Results-driven {skills_text} professional with expertise in {skills_text}. {base_summary}"
#     else:
#         optimized = base_summary
    
#     return optimized


# def optimize_technical_skills(existing_skills, jd_keywords):
#     """Optimize technical skills section with JD keywords"""
#     jd_tech = set(jd_keywords.get('tech_keywords', []))
#     existing = set(existing_skills)
    
#     # Combine existing skills with JD keywords (only add if not already present)
#     optimized = list(existing) + [skill for skill in jd_tech if skill.lower() not in [s.lower() for s in existing]]
    
#     return optimized


# def optimize_work_experience(work_exp_lines, jd_keywords):
#     """Rephrase work experience to include JD keywords"""
#     tech_keywords = [k.lower() for k in jd_keywords.get('tech_keywords', [])]
    
#     optimized_lines = []
#     for line in work_exp_lines:
#         # Add relevant keywords if they fit naturally
#         if any(tech in line.lower() for tech in ['developed', 'built', 'created', 'implemented']):
#             # Add a tech keyword if not present
#             missing_tech = [t for t in tech_keywords if t not in line.lower()][:1]  # Add max 1
#             if missing_tech:
#                 line = line + f" using {missing_tech[0]}"
        
#         optimized_lines.append(line)
    
#     return optimized_lines


# def optimize_projects(projects, jd_keywords):
#     """Optimize project descriptions with JD keywords"""
#     tech_keywords = jd_keywords.get('tech_keywords', [])
    
#     optimized_projects = []
#     for project in projects:
#         opt_project = {
#             'title': project['title'],
#             'bullets': []
#         }
        
#         for bullet in project['bullets']:
#             # Add relevant tech keywords
#             missing_tech = [t for t in tech_keywords if t.lower() not in bullet.lower()][:2]  # Max 2 per bullet
#             if missing_tech:
#                 bullet = bullet + f" (Utilized {', '.join(missing_tech)})"
            
#             opt_project['bullets'].append(bullet)
        
#         optimized_projects.append(opt_project)
    
#     return optimized_projects


# def generate_ats_resume_text(sections, jd_keywords):
#     """Generate complete ATS-optimized resume text"""
#     lines = []
    
#     # Header
#     lines.append(sections['name'])
#     lines.append(f"{sections['phone']} | {sections['email']}")
#     if sections['location']:
#         lines.append(sections['location'])
#     lines.append("")
    
#     # Professional Summary
#     lines.append("PROFESSIONAL SUMMARY")
#     summary = optimize_professional_summary(sections['objective'], jd_keywords)
#     lines.append(summary)
#     lines.append("")
    
#     # Technical Skills
#     if sections['technical_skills']:
#         lines.append("TECHNICAL SKILLS")
#         optimized_skills = optimize_technical_skills(sections['technical_skills'], jd_keywords)
#         lines.append(", ".join(optimized_skills))
#         lines.append("")
    
#     # Work Experience
#     if sections['work_experience']:
#         lines.append("WORK EXPERIENCE")
#         optimized_exp = optimize_work_experience(sections['work_experience'], jd_keywords)
#         lines.extend(optimized_exp)
#         lines.append("")
    
#     # Projects
#     if sections.get('projects'):
#         lines.append("PROJECTS")
#         optimized_projects = optimize_projects(sections['projects'], jd_keywords)
#         for project in optimized_projects:
#             lines.append(f"• {project['title']}")
#             for bullet in project['bullets']:
#                 lines.append(f"  - {bullet}")
#         lines.append("")
    
#     # Education
#     if sections.get('education_entries'):
#         lines.append("EDUCATION")
#         for edu in sections['education_entries']:
#             lines.append(edu['institution'])
#             if edu['qualification']:
#                 lines.append(edu['qualification'])
#         lines.append("")
    
#     # Languages
#     if sections['languages']:
#         lines.append("LANGUAGES")
#         lines.append(sections['languages'])
    
#     return "\n".join(lines)


# # =====================================================
# # 13. PDF GENERATION
# # =====================================================

# def generate_ats_pdf(sections, jd_keywords, output_path):
#     """Generate ATS-friendly PDF resume"""
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     styles = getSampleStyleSheet()
    
#     # Custom styles
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Heading1'],
#         fontSize=16,
#         spaceAfter=10,
#         alignment=TA_CENTER
#     )
    
#     section_style = ParagraphStyle(
#         'Section',
#         parent=styles['Heading2'],
#         fontSize=12,
#         spaceAfter=5,
#         fontName='Helvetica-Bold'
#     )
    
#     normal_style = styles['Normal']
#     normal_style.fontSize = 10
#     normal_style.leading = 12
    
#     story = []
    
#     # Header
#     story.append(Paragraph(sections['name'], title_style))
#     contact = f"{sections['phone']} | {sections['email']}"
#     if sections['location']:
#         contact += f" | {sections['location']}"
#     story.append(Paragraph(contact, ParagraphStyle('Contact', parent=normal_style, alignment=TA_CENTER)))
#     story.append(Spacer(1, 0.2*inch))
    
#     # Professional Summary
#     story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
#     summary = optimize_professional_summary(sections['objective'], jd_keywords)
#     story.append(Paragraph(summary, normal_style))
#     story.append(Spacer(1, 0.1*inch))
    
#     # Technical Skills
#     if sections['technical_skills']:
#         story.append(Paragraph("TECHNICAL SKILLS", section_style))
#         optimized_skills = optimize_technical_skills(sections['technical_skills'], jd_keywords)
#         story.append(Paragraph(", ".join(optimized_skills), normal_style))
#         story.append(Spacer(1, 0.1*inch))
    
#     # Work Experience
#     if sections['work_experience']:
#         story.append(Paragraph("WORK EXPERIENCE", section_style))
#         optimized_exp = optimize_work_experience(sections['work_experience'], jd_keywords)
#         for line in optimized_exp:
#             story.append(Paragraph(f"• {line}", normal_style))
#         story.append(Spacer(1, 0.1*inch))
    
#     # Projects
#     if sections.get('projects'):
#         story.append(Paragraph("PROJECTS", section_style))
#         optimized_projects = optimize_projects(sections['projects'], jd_keywords)
#         for project in optimized_projects:
#             story.append(Paragraph(f"<b>{project['title']}</b>", normal_style))
#             for bullet in project['bullets']:
#                 story.append(Paragraph(f"  - {bullet}", normal_style))
#         story.append(Spacer(1, 0.1*inch))
    
#     # Education
#     if sections.get('education_entries'):
#         story.append(Paragraph("EDUCATION", section_style))
#         for edu in sections['education_entries']:
#             story.append(Paragraph(f"<b>{edu['institution']}</b>", normal_style))
#             if edu['qualification']:
#                 story.append(Paragraph(edu['qualification'], normal_style))
#         story.append(Spacer(1, 0.1*inch))
    
#     # Languages
#     if sections['languages']:
#         story.append(Paragraph("LANGUAGES", section_style))
#         story.append(Paragraph(sections['languages'], normal_style))
    
#     doc.build(story)
#     buffer.seek(0)
    
#     with open(output_path, 'wb') as f:
#         f.write(buffer.getvalue())
    
#     buffer.close()


# # =====================================================
# # 14. MAIN PARSER
# # =====================================================

# def parse_resume_sections(text):
#     lines = [l.strip() for l in text.split("\n") if l.strip()]

#     header = parse_header(lines)
#     blocks = split_into_sections(lines)

#     education_entries = parse_education(blocks.get("education", []))
#     project_entries = parse_projects(blocks.get("projects", []))
#     technical, soft = split_skills(" ".join(blocks.get("technical_skills", [])))

#     return {
#         "name": header["name"],
#         "phone": header["phone"],
#         "email": header["email"],
#         "dob": header["dob"],
#         "location": header["location"],

#         "objective": " ".join(blocks.get("objective", [])),
#         "education_html": format_education_html(education_entries),
#         "projects_html": format_projects_html(project_entries),
#         "technical_skills": technical,
#         "soft_skills": soft,
#         "languages": " ".join(blocks.get("languages", [])),
#         "work_experience": blocks.get("work_experience", []),
#         "education_entries": education_entries,
#         "projects": project_entries
#     }






# Gemini ai

# import os
# import pdfplumber

# from docx import Document
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet



# # 1. TEXT EXTRACTION (KEEP THESE)
# def extract_text_from_pdf(path):
#     text = ""
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text: text += page_text + "\n"
#     return text

# def extract_text_from_docx(path):
#     doc = Document(path)
#     return "\n".join(p.text for p in doc.paragraphs)

# # 2. THE AI BRAIN (THE NEW PART)
# def get_ai_optimized_resume(resume_text, job_description):
#     model = genai.GenerativeModel('models/gemini-pro')
#     prompt = f"""
#     Act as an ATS Optimizer. Rewrite the resume to match the Job Description.
#     Return the result in this EXACT structure:
#     SUMMARY: [Rewritten summary]
#     SKILLS: [Optimized skills list]
#     EXPERIENCE: [Rewritten bullet points]
    
#     RESUME: {resume_text}
#     JD: {job_description}
#     """
#     response = model.generate_content(prompt)
#     return response.text # This returns the optimized text

# # 3. PDF GENERATOR (SIMPLIFIED)
# def generate_ats_pdf(optimized_text, output_path):
#     doc = SimpleDocTemplate(output_path)
#     styles = getSampleStyleSheet()
#     story = [Paragraph(optimized_text.replace('\n', '<br/>'), styles['Normal'])]
#     doc.build(story)


# utils.py
import os
import pdfplumber
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
from google import genai


# Configure Gemini ONCE
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Use SUPPORTED model



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
        


# 3. PDF GENERATOR
# def generate_ats_pdf(optimized_text, output_path):
#     styles = getSampleStyleSheet()
#     doc = SimpleDocTemplate(output_path)
#     story = [Paragraph(optimized_text.replace("\n", "<br/>"), styles["Normal"])]
#     doc.build(story)

# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from textwrap import wrap

# def generate_ats_pdf(text, output_path):
#     c = canvas.Canvas(output_path, pagesize=A4)
#     width, height = A4

#     margin_x = 40
#     max_width = width - (2 * margin_x)
#     y = height - 40

#     for line in text.split("\n"):
#         wrapped_lines = wrap(line, 95) or [""]

#         for wline in wrapped_lines:
#             c.drawString(margin_x, y, wline)
#             y -= 14

#             if y < 40:
#                 c.showPage()
#                 y = height - 40

#     c.save()




# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import Paragraph, SimpleDocTemplate, ListFlowable, ListItem
# from reportlab.lib.units import inch
# from reportlab.lib.enums import TA_LEFT

# def generate_ats_pdf(text, output_path):
#     doc = SimpleDocTemplate(
#         output_path,
#         pagesize=A4,
#         rightMargin=40,
#         leftMargin=40,
#         topMargin=40,
#         bottomMargin=40
#     )

#     styles = getSampleStyleSheet()
#     story = []

#     body = styles["Normal"]
#     body.fontName = "Calibri"
#     body.fontSize = 11
#     body.leading = 14

#     heading = styles["Heading4"]
#     heading.fontName = "Calibri-Bold"
#     heading.fontSize = 11
#     heading.spaceAfter = 6

#     name_style = styles["Title"]
#     name_style.fontName = "Calibri-Bold"
#     name_style.fontSize = 14
#     name_style.spaceAfter = 8

#     for i, line in enumerate(text.split("\n")):

#         # Name
#         if i == 0:
#             story.append(Paragraph(line, name_style))
#             continue

#         # Heading
#         if line.startswith("**") and line.endswith("**"):
#             story.append(Paragraph(line.replace("*", ""), heading))
#             continue

#         # Bullet
#         if line.startswith("•"):
#             story.append(ListFlowable(
#                 [ListItem(Paragraph(line[1:].strip(), body))],
#                 start='bullet',
#                 leftIndent=18
#             ))
#             continue

#         # Normal text (with links auto-detected)
#         story.append(Paragraph(line, body))

#     doc.build(story)



# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import inch

# def generate_ats_pdf(text, output_path):
#     doc = SimpleDocTemplate(
#         output_path,
#         pagesize=A4,
#         leftMargin=40,
#         rightMargin=40,
#         topMargin=40,
#         bottomMargin=40
#     )

#     styles = getSampleStyleSheet()
#     story = []

#     name_style = ParagraphStyle(
#         "Name",
#         fontName="Helvetica-Bold",
#         fontSize=14,
#         spaceAfter=8
#     )

#     heading_style = ParagraphStyle(
#         "Heading",
#         fontName="Helvetica-Bold",
#         fontSize=11,
#         spaceBefore=8,
#         spaceAfter=4
#     )

#     body_style = ParagraphStyle(
#         "Body",
#         fontName="Helvetica",
#         fontSize=11,
#         spaceAfter=4
#     )

#     bullet_style = ParagraphStyle(
#         "Bullet",
#         fontName="Helvetica",
#         fontSize=11,
#         leftIndent=18
#     )

#     for i, line in enumerate(text.split("\n")):

#         # Name
#         if i == 0:
#             story.append(Paragraph(line, name_style))
#             continue

#         # Heading
#         if line.startswith("**") and line.endswith("**"):
#             story.append(Paragraph(line.replace("*", ""), heading_style))
#             story.append(Spacer(1, 4))
#             continue

#         # Project title
#         if not line.startswith("•") and line.isupper() is False and ":" not in line:
#             story.append(Paragraph(f"<b>{line}</b>", body_style))
#             continue

#         # Bullet
#         if line.startswith("•"):
#             story.append(ListFlowable(
#                 [ListItem(Paragraph(line[1:], body_style))],
#                 leftIndent=18
#             ))
#             continue

#         # Normal text
#         story.append(Paragraph(line, body_style))

#     doc.build(story)




# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.pagesizes import A4

# def generate_ats_pdf(text, output_path):
#     doc = SimpleDocTemplate(
#         output_path,
#         pagesize=A4,
#         leftMargin=40,
#         rightMargin=40,
#         topMargin=40,
#         bottomMargin=40
#     )

#     # styles = getSampleStyleSheet()
#     story = []

#     name_style = ParagraphStyle(
#         "Name", fontName="Helvetica-Bold", fontSize=14, spaceAfter=8
#     )

#     heading_style = ParagraphStyle(
#         "Heading", fontName="Helvetica-Bold", fontSize=11, spaceBefore=8, spaceAfter=4
#     )

#     body_style = ParagraphStyle(
#         "Body", fontName="Helvetica", fontSize=11, spaceAfter=4
#     )

#     # bullet_style = ParagraphStyle(
#     #     "Bullet", fontName="Helvetica", fontSize=11, leftIndent=18
#     # )

#     lines = text.split("\n")
#     currentSection = ""

#     for i, line in enumerate(lines):

#         if i == 0:
#             story.append(Paragraph(line, name_style))
#             continue

#         if line.startswith("**") and line.endswith("**"):
#             currentSection = line.replace("*", "")
#             story.append(Paragraph(currentSection, heading_style))
#             story.append(Spacer(1, 6))
#             continue

#         if line.startswith("•"):
#             story.append(
#                 ListFlowable(
#                     [ListItem(Paragraph(line[1:].strip(), body_style))],
#                     leftIndent=18
#                 )
#             )
#             continue

#         if currentSection == "PROJECTS" and line.strip():
#             story.append(Paragraph(f"<b>{line}</b>", body_style))
#             continue

#         story.append(Paragraph(line, body_style))

#     doc.build(story)




from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    Indenter,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4

# --------------------------------------------------
# PDF GENERATION (HELVETICA – PRODUCTION SAFE)
# --------------------------------------------------

def generate_ats_pdf(text, output_path):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story = []

    # -----------------------------
    # STYLES
    # -----------------------------

    name_style = ParagraphStyle(
        "Name",
        fontName="Helvetica-Bold",
        fontSize=14,
        spaceAfter=8,
    )

    heading_style = ParagraphStyle(
        "Heading",
        fontName="Helvetica-Bold",
        fontSize=11,
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=11,
        spaceAfter=4,
    )

    project_title_style = ParagraphStyle(
        "ProjectTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        spaceBefore=4,
        spaceAfter=2,
    )

    # -----------------------------
    # PARSING STATE
    # -----------------------------

    lines = text.split("\n")
    current_section = ""
    buffer_bullets = []

    # -----------------------------
    # HELPER: FLUSH BULLETS
    # -----------------------------

    def flush_bullets(parent_indent=18):
        nonlocal buffer_bullets
        if buffer_bullets:
            story.append(Indenter(left=parent_indent, right=0))
            story.append(
                ListFlowable(
                    [
                        ListItem(Paragraph(item, body_style))
                        for item in buffer_bullets
                    ],
                    bulletType="bullet",
                    start="•",
                    leftIndent=0,  # parent-based indentation
                )
            )
            story.append(Indenter(left=-parent_indent, right=0))
            buffer_bullets = []

    # -----------------------------
    # MAIN LOOP
    # -----------------------------

    for index, line in enumerate(lines):

        line = line.strip()
        if not line:
            continue

        # NAME (FIRST LINE)
        if index == 0:
            story.append(Paragraph(line, name_style))
            continue

        # SECTION HEADING
        if line.startswith("**") and line.endswith("**"):
            flush_bullets()
            current_section = line.replace("*", "")
            story.append(Paragraph(current_section, heading_style))
            continue

        # BULLET LINE
        if line.startswith("•"):
            buffer_bullets.append(line[1:].strip())
            continue

        # PROJECT / WORK EXPERIENCE TITLE
        if current_section in ("PROJECTS", "WORK EXPERIENCE"):
            flush_bullets()
            story.append(Paragraph(line, project_title_style))
            continue

        # NORMAL PARAGRAPH
        flush_bullets()
        story.append(Paragraph(line, body_style))

    # Flush any remaining bullets
    flush_bullets()

    # -----------------------------
    # BUILD PDF
    # -----------------------------

    doc.build(story)