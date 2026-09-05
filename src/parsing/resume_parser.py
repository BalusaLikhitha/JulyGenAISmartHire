import json
import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in .env")


client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash-lite"

def parse_resume(resume_text: str):

    prompt = f"""
You are a Resume Parser.

Extract structured information from the resume below.

IMPORTANT:
Read the entire resume carefully before producing the JSON.

RULES:
1. Extract ONLY information explicitly present in the resume.
2. NEVER invent, assume, or guess information.
3. If a single value is missing, use null.
4. If a list has no information, use [].
5. Preserve the actual education institute, year and score when they
   are present in the resume.
6. Preserve the actual company, role and duration when present.
7. Preserve project names, descriptions and technologies when present.
8. Extract all clearly mentioned skills.
9. Normalize Indian phone numbers to +91XXXXXXXXXX whenever possible.
10. The summary must contain exactly one sentence.
11. Return ONLY valid JSON.
12. Do not include markdown or explanations.

EDUCATION EXTRACTION:

For every education entry:
- degree = degree/course name
- institute = college/university/institute name
- year = year or year range
- score = CGPA, percentage, grade or score

For example, if the resume contains:

B.Tech in Computer Science and Engineering
ABC Institute of Technology
2023 - 2027
CGPA: 8.4/10

you MUST return:

{{
    "degree": "B.Tech in Computer Science and Engineering",
    "institute": "ABC Institute of Technology",
    "year": "2023 - 2027",
    "score": "8.4/10"
}}

Do not replace available values with null.

Return JSON with exactly these keys:

{{
    "name": null,
    "email": null,
    "phone": null,
    "linkedin_url": null,

    "education": [
        {{
            "degree": null,
            "institute": null,
            "year": null,
            "score": null
        }}
    ],

    "skills": [],

    "experience": [
        {{
            "company": null,
            "role": null,
            "duration": null,
            "highlights": []
        }}
    ],

    "projects": [
        {{
            "name": null,
            "description": null,
            "tech_stack": []
        }}
    ],

    "total_experience_years": null,

    "summary": null
}}

RESUME:
{resume_text}

JSON:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.1,
            "max_output_tokens": 2048
        }
    )

    data = json.loads(response.text)

    required_fields = [
        "name",
        "email",
        "phone",
        "linkedin_url",
        "education",
        "skills",
        "experience",
        "projects",
        "total_experience_years",
        "summary"
    ]

    for field in required_fields:
        data.setdefault(field, None)

    return data