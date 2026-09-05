import re


def check_input(question):
    """
    Basic guardrail for the AI Career Mentor.
    Returns (True, "") when the question is allowed.
    Returns (False, message) when it should be rejected.
    """

    if not question or not question.strip():
        return False, "Please enter a question."

    question = question.lower().strip()

    # Unsafe topics
    blocked_words = [
        "hack",
        "malware",
        "ransomware",
        "phishing",
        "password",
        "credit card",
        "weapon",
        "bomb",
        "kill"
    ]

    # Check complete words/phrases only
    for word in blocked_words:
        if re.search(r"\b" + re.escape(word) + r"\b", question):
            return False, "Sorry, I can only help with safe career-related questions."

    # Career-related topics
    career_words = [
        "career",
        "job",
        "resume",
        "cv",
        "skill",
        "skills",
        "interview",
        "employment",
        "developer",
        "development",
        "data analyst",
        "data science",
        "software",
        "learning",
        "course",
        "project",
        "full stack",
"fullstack",
"dev",
    ]

    if any(word in question for word in career_words):
        return True, ""

    return False, "Please ask a career-related question."
def is_resume_specific_question(question):
    """
    Check whether the user is asking for a personalized
    assessment based on their own resume.
    """
    question = question.lower().strip()

    resume_specific_words = [
        "am i suitable",
        "am i eligible",
        "do i qualify",
        "is my resume",
        "my resume",
        "my skills",
        "my experience",
        "my profile",
        "based on my",
        "for me",
        "can i get this job",
        "can i apply"
    ]

    return any(
        phrase in question
        for phrase in resume_specific_words
    )