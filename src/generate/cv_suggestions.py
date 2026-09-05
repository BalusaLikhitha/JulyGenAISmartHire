import os
from dotenv import load_dotenv
from google import genai


# Load API key
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in .env")


# Create Gemini client
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash-lite"


def get_cv_suggestions(resume_text):

    prompt = f"""
You are an AI Career Mentor and Resume Improvement Assistant.

Analyze the following resume and provide useful suggestions
to improve it.

Focus on:

1. Skills that could be improved or added based only on the
   information already present in the resume.
2. Weak or unclear areas in the resume.
3. Suggestions to improve the professional summary.
4. Suggestions to improve project descriptions.
5. Suggestions to improve experience descriptions.
6. General resume improvement suggestions.

Rules:
- Do not invent experience, education, projects or achievements.
- Do not claim that the candidate has a skill they do not mention.
- Give practical and clear suggestions.
- Keep the suggestions relevant to the candidate's resume.

Resume:
{resume_text}

Return the suggestions in a clear format with headings.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0.3,
            "max_output_tokens": 1500
        }
    )

    return response.text