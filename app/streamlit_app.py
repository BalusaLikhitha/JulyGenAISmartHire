import sys
import re
import tempfile
import zipfile
from pathlib import Path

import gdown
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VECTORSTORE_URL = (
    "https://drive.google.com/uc?id="
    "1q7A_EDqiTbHrPv_L3U3llPUdVHUPWT6L"
)

VECTORSTORE_ZIP = PROJECT_ROOT / "vectorstore.zip"


if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def ensure_vectorstore():
    """
    Make sure the FAISS vectorstore is available.

    If the vectorstore is missing, download the ZIP from
    Google Drive and extract it into the project directory.
    """

    jobs_index = (
        PROJECT_ROOT
        / "vectorstore"
        / "jobs_faiss"
        / "jobs.index"
    )

    notes_index = (
        PROJECT_ROOT
        / "vectorstore"
        / "notes_faiss"
        / "notes.index"
    )

    # Vectorstore already exists.
    if jobs_index.exists() and notes_index.exists():
        return

    with st.spinner(
        "Preparing SmartHire search database..."
    ):
        try:

            # Remove old/incomplete ZIP.
            if VECTORSTORE_ZIP.exists():
                VECTORSTORE_ZIP.unlink()

            # Download ZIP from Google Drive.
            downloaded_file = gdown.download(
                url=VECTORSTORE_URL,
                output=str(VECTORSTORE_ZIP),
                quiet=False
            )

            if downloaded_file is None:
                raise RuntimeError(
                    "Google Drive download failed."
                )

            if not VECTORSTORE_ZIP.exists():
                raise FileNotFoundError(
                    "Downloaded ZIP file was not created."
                )

            # Check that the downloaded file is a valid ZIP.
            if not zipfile.is_zipfile(
                VECTORSTORE_ZIP
            ):
                raise RuntimeError(
                    "The downloaded file is not a valid ZIP file."
                )

            # Extract the vectorstore.
            with zipfile.ZipFile(
                VECTORSTORE_ZIP,
                "r"
            ) as zip_ref:

                for original_file_name in zip_ref.namelist():

                    # Convert Windows "\" paths to Linux "/" paths.
                    file_name = original_file_name.replace(
                        "\\",
                        "/"
                    )

                    # Skip directories.
                    if file_name.endswith("/"):
                        continue

                    # Only process vectorstore files.
                    if not file_name.startswith(
                        "vectorstore/"
                    ):
                        continue

                    output_path = (
                        PROJECT_ROOT
                        / Path(file_name)
                    )

                    # Create required folders.
                    output_path.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    # Extract file contents.
                    with zip_ref.open(
                        original_file_name
                    ) as source:

                        with open(
                            output_path,
                            "wb"
                        ) as target:

                            target.write(
                                source.read()
                            )

        except Exception as e:

            st.error(
                "❌ Could not prepare the SmartHire "
                f"search database: {e}"
            )

            st.stop()

    # Verify both FAISS indexes.
    if (
        not jobs_index.exists()
        or not notes_index.exists()
    ):

        st.error(
            "❌ Vectorstore files were downloaded "
            "but could not be found after extraction."
        )

        st.write(
            "Project root:",
            str(PROJECT_ROOT)
        )

        st.write(
            "ZIP exists:",
            VECTORSTORE_ZIP.exists()
        )

        if VECTORSTORE_ZIP.exists():

            try:

                with zipfile.ZipFile(
                    VECTORSTORE_ZIP,
                    "r"
                ) as zip_ref:

                    st.write(
                        "ZIP contents:"
                    )

                    st.code(
                        "\n".join(
                            zip_ref.namelist()
                        )
                    )

            except Exception as e:

                st.write(
                    "Could not inspect ZIP:",
                    str(e)
                )

        st.write(
            "Expected jobs index:",
            str(jobs_index)
        )

        st.write(
            "Expected notes index:",
            str(notes_index)
        )

        st.stop()

    # Verify that the two required FAISS indexes exist.
    if (
        not jobs_index.exists()
        or not notes_index.exists()
    ):

        st.error(
            "❌ Vectorstore files were downloaded "
            "but could not be found after extraction."
        )

        st.write(
            "Project root:",
            str(PROJECT_ROOT)
        )

        st.write(
            "ZIP exists:",
            VECTORSTORE_ZIP.exists()
        )

        if VECTORSTORE_ZIP.exists():

            try:
                with zipfile.ZipFile(
                    VECTORSTORE_ZIP,
                    "r"
                ) as zip_ref:

                    st.write("ZIP contents:")

                    st.code(
                        "\n".join(
                            zip_ref.namelist()
                        )
                    )

            except Exception as e:

                st.write(
                    "Could not inspect ZIP:",
                    str(e)
                )

        st.write(
            "Expected jobs index:",
            str(jobs_index)
        )

        st.write(
            "Expected notes index:",
            str(notes_index)
        )

        st.stop()


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from src.parsing.loader import load_text
from src.parsing.resume_parser import parse_resume
from src.safety.guardrails import (
    is_resume_specific_question
)
from src.search.job_search import search_jobs

from src.generate.cv_suggestions import (
    get_cv_suggestions
)

from src.mentor.rag_chain import (
    retrieve_notes,
    create_mentor_response
)


# Make sure the vectorstore exists before the application
# attempts to search jobs or retrieve career notes.
ensure_vectorstore()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SmartHire GenAI",
    layout="wide"
)


# ============================================================
# RESUME VALIDATION
# ============================================================

def is_likely_resume(text):
    """
    Check whether uploaded text looks like an actual resume.

    This is intentionally strict so that project documents,
    assignments, reports and other PDFs are not treated as resumes.
    """

    if not text:
        return False, "The document is empty."

    text_clean = text.strip()

    if len(text_clean) < 150:
        return False, "The document contains too little text."

    text_lower = text_clean.lower()

    strong_non_resume_phrases = [
        "capstone project",
        "project guidelines",
        "project requirements",
        "project brief",
        "project overview",
        "system architecture",
        "project directory structure",
        "techniques you will use",
        "datasets & knowledge base",
        "build timeline",
        "minimum scope to pass",
        "deliverables",
        "stretch goals",
        "evaluation",
        "notes & constraints",
        "implementation guidelines",
        "table of contents",
        "course material",
        "assignment",
        "documentation"
    ]

    non_resume_matches = [
        phrase
        for phrase in strong_non_resume_phrases
        if phrase in text_lower
    ]

    if len(non_resume_matches) >= 1:

        return (
            False,
            "The uploaded document appears to be a project, "
            "assignment, report, or documentation rather than a resume."
        )

    has_email = bool(
        re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text_clean
        )
    )

    phone_text = re.sub(
        r"[\s().-]",
        "",
        text_clean
    )

    has_phone = bool(
        re.search(
            r"(?:\+91|91)?[6-9]\d{9}\b",
            phone_text
        )
    )

    has_linkedin_url = bool(
        re.search(
            r"(https?://)?(www\.)?linkedin\.com/[A-Za-z0-9_\-/]+",
            text_lower
        )
    )

    has_contact = (
        has_email
        or has_phone
        or has_linkedin_url
    )

    if not has_contact:

        return (
            False,
            "No valid email, phone number, or LinkedIn profile "
            "was found. The document does not appear to be a resume."
        )

    resume_sections = [
        "education",
        "skills",
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "technical skills",
        "certifications",
        "internship",
        "achievements",
        "career objective",
        "professional summary",
        "objective"
    ]

    matched_sections = [
        section
        for section in resume_sections
        if section in text_lower
    ]

    if len(matched_sections) < 3:

        return (
            False,
            "The document does not contain enough typical resume sections."
        )

    candidate_indicators = [
        "b.tech",
        "btech",
        "b.e.",
        "be ",
        "bachelor",
        "master",
        "m.tech",
        "mtech",
        "mca",
        "bca",
        "computer science",
        "information technology",
        "software developer",
        "developer",
        "intern",
        "internship",
        "analyst",
        "engineer",
        "programmer",
        "student"
    ]

    candidate_matches = sum(
        1
        for item in candidate_indicators
        if item in text_lower
    )

    if candidate_matches < 1:

        return (
            False,
            "The document does not contain enough candidate/resume information."
        )

    return True, ""


# ============================================================
# SESSION STATE
# ============================================================

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None

if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = None

if "job_matches" not in st.session_state:
    st.session_state.job_matches = []

if "cv_suggestions" not in st.session_state:
    st.session_state.cv_suggestions = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# MAIN TITLE
# ============================================================

st.title(" SmartHire GenAI")

st.subheader(
    "Resume Matching & AI Career Mentor"
)

st.write(
    "Upload your resume to get a structured profile, "
    "matching jobs, CV improvement suggestions, and "
    "AI-powered career guidance."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📄 Resume Upload")

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help=(
            "Upload a genuine resume in PDF, DOCX or TXT format."
        )
    )

    analyze_button = st.button(
        "🔍 Analyze Resume",
        use_container_width=True
    )


# ============================================================
# RESUME ANALYSIS
# ============================================================

if analyze_button:

    # Clear previous analysis.
    st.session_state.resume_text = None
    st.session_state.resume_profile = None
    st.session_state.job_matches = []
    st.session_state.cv_suggestions = None
    st.session_state.messages = []

    if uploaded_file is None:

        st.warning(
            "⚠️ Please upload a resume first."
        )

    else:

        temp_path = None

        try:

            suffix = Path(
                uploaded_file.name
            ).suffix.lower()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name

            # ------------------------------------------------
            # READ DOCUMENT
            # ------------------------------------------------

            with st.spinner(
                "📖 Reading the uploaded document..."
            ):

                document_text = load_text(
                    temp_path
                )

            # ------------------------------------------------
            # VALIDATE RESUME
            # ------------------------------------------------

            is_resume, reason = is_likely_resume(
                document_text
            )

            if not is_resume:

                st.error(
                    "❌ This document does not appear to be a resume."
                )

                st.info(
                    f"Reason: {reason}\n\n"
                    "Please upload a genuine resume containing "
                    "contact information and sections such as "
                    "Education, Skills, Experience and Projects."
                )

            else:

                # ------------------------------------------------
                # PARSE RESUME
                # ------------------------------------------------

                with st.spinner(
                    "🤖 Extracting resume information..."
                ):

                    profile = parse_resume(
                        document_text
                    )

                if not isinstance(
                    profile,
                    dict
                ):

                    st.error(
                        "❌ Resume parser did not return valid profile data."
                    )

                else:

                    st.session_state.resume_text = (
                        document_text
                    )

                    st.session_state.resume_profile = (
                        profile
                    )

                    # ------------------------------------------------
                    # JOB MATCHING
                    # ------------------------------------------------

                    with st.spinner(
                        " Finding matching jobs..."
                    ):

                        matches = search_jobs(
                            document_text,
                            top_k=5
                        )

                    st.session_state.job_matches = (
                        matches
                    )

                    st.success(
                        "✅ Resume analyzed successfully!"
                    )

        except Exception as e:

            st.error(
                "❌ Something went wrong while analyzing "
                f"the resume:\n\n{e}"
            )

        finally:

            # Remove temporary uploaded file.
            if temp_path:

                try:

                    Path(
                        temp_path
                    ).unlink(
                        missing_ok=True
                    )

                except Exception:
                    pass


# ============================================================
# RESUME PROFILE
# ============================================================

if st.session_state.resume_profile:

    st.header("👤 Resume Profile")

    profile = st.session_state.resume_profile

    # ------------------------------------------------
    # PERSONAL INFORMATION
    # ------------------------------------------------

    st.subheader("Personal Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Name:** "
            f"{profile.get('name') or 'Not available'}"
        )

        st.write(
            f"**Email:** "
            f"{profile.get('email') or 'Not available'}"
        )

        st.write(
            f"**Phone:** "
            f"{profile.get('phone') or 'Not available'}"
        )

    with col2:

        st.write(
            f"**LinkedIn:** "
            f"{profile.get('linkedin_url') or 'Not available'}"
        )

        experience_years = profile.get(
            "total_experience_years"
        )

        if experience_years is not None:

            st.write(
                f"**Total Experience:** "
                f"{experience_years} years"
            )

    # ------------------------------------------------
    # PROFESSIONAL SUMMARY
    # ------------------------------------------------

    st.subheader("📝 Professional Summary")

    summary = profile.get(
        "summary"
    )

    if summary:

        st.write(
            summary
        )

    else:

        st.write(
            "No summary available."
        )

    # ------------------------------------------------
    # SKILLS
    # ------------------------------------------------

    st.subheader("🛠️ Skills")

    skills = profile.get(
        "skills",
        []
    )

    if isinstance(
        skills,
        list
    ) and skills:

        st.write(
            " • ".join(
                str(skill)
                for skill in skills
            )
        )

    else:

        st.write(
            "No skills found."
        )

    # ------------------------------------------------
    # EDUCATION
    # ------------------------------------------------

    st.subheader("🎓 Education")

    education = profile.get(
        "education",
        []
    )

    if isinstance(
        education,
        list
    ) and education:

        for item in education:

            if not isinstance(
                item,
                dict
            ):
                continue

            degree = item.get(
                "degree"
            ) or "Not available"

            institute = item.get(
                "institute"
            ) or "Not available"

            year = item.get(
                "year"
            ) or "Not available"

            score = item.get(
                "score"
            ) or "Not available"

            st.markdown(
                f"""
**{degree}**

Institute: {institute}

Year: {year}

Score: {score}
"""
            )

    else:

        st.write(
            "No education information found."
        )

    # ------------------------------------------------
    # EXPERIENCE
    # ------------------------------------------------

    st.subheader("💼 Experience")

    experience = profile.get(
        "experience",
        []
    )

    if isinstance(
        experience,
        list
    ) and experience:

        for item in experience:

            if not isinstance(
                item,
                dict
            ):
                continue

            role = item.get(
                "role"
            ) or "Not available"

            company = item.get(
                "company"
            ) or "Not available"

            duration = item.get(
                "duration"
            ) or "Not available"

            st.markdown(
                f"""
**{role}**

Company: {company}

Duration: {duration}
"""
            )

            highlights = item.get(
                "highlights",
                []
            )

            if isinstance(
                highlights,
                list
            ):

                for highlight in highlights:

                    st.write(
                        f"- {highlight}"
                    )

    else:

        st.write(
            "No experience information found."
        )
# ============================================================
# PROJECTS
# ============================================================

    st.subheader("📁 Projects")

    projects = profile.get(
        "projects",
        []
    )

    if isinstance(
        projects,
        list
    ) and projects:

        for project in projects:

            if not isinstance(
                project,
                dict
            ):
                continue

            name = project.get(
                "name"
            ) or "Not available"

            description = project.get(
                "description"
            ) or "Not available"

            tech_stack = project.get(
                "tech_stack",
                []
            )

            st.markdown(
                f"""
**{name}**

{description}
"""
            )

            if isinstance(
                tech_stack,
                list
            ) and tech_stack:

                st.write(
                    "Tech Stack:",
                    ", ".join(
                        str(item)
                        for item in tech_stack
                    )
                )

    else:

        st.write(
            "No projects found."
        )


# ============================================================
# MATCHING JOBS
# ============================================================

if st.session_state.job_matches:

    st.header("💼 Matching Jobs")

    st.write(
        "These jobs are ranked using semantic similarity "
        "between your resume and the job descriptions."
    )

    for i, job in enumerate(
        st.session_state.job_matches,
        start=1
    ):

        if not isinstance(
            job,
            dict
        ):
            continue

        job_title = job.get(
            "jobtitle"
        ) or "Job title not available"

        company = job.get(
            "company"
        ) or "Not available"

        location = job.get(
            "joblocation_address"
        ) or "Not available"

        skills = job.get(
            "skills"
        ) or "Not available"

        description = job.get(
            "jobdescription"
        ) or "Not available"

        score = job.get(
            "similarity_score",
            0
        )

        try:

            score_percentage = round(
                float(score) * 100,
                2
            )

        except Exception:

            score_percentage = 0

        with st.expander(
            f"{i}. {job_title}"
        ):

            st.write(
                f"**Company:** {company}"
            )

            st.write(
                f"**Location:** {location}"
            )

            st.write(
                f"**Skills:** {skills}"
            )

            st.write(
                f"**Semantic Similarity:** "
                f"{score_percentage}%"
            )

            st.write(
                f"**Job Description:**\n{description}"
            )


# ============================================================
# CV IMPROVEMENT SUGGESTIONS
# ============================================================

if st.session_state.resume_text:

    st.header("✍️ CV Improvement Suggestions")

    st.write(
        "Generate AI suggestions to improve your resume."
    )

    if st.button(
        "✨ Generate CV Suggestions"
    ):

        try:

            with st.spinner(
                "Analyzing your CV..."
            ):

                suggestions = get_cv_suggestions(
                    st.session_state.resume_text
                )

            st.session_state.cv_suggestions = (
                suggestions
            )

        except Exception as e:

            st.error(
                f"❌ Could not generate CV suggestions:\n\n{e}"
            )

    if st.session_state.cv_suggestions:

        st.markdown(
            st.session_state.cv_suggestions
        )


# ============================================================
# AI CAREER MENTOR
# ============================================================

st.header("🤖 AI Career Mentor")

st.write(
    "Ask questions about careers, jobs, resumes, skills, "
    "interviews and professional development."
)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask your career question..."
)


if question:

    # --------------------------------------------------------
    # RESUME-SPECIFIC QUESTION CHECK
    # --------------------------------------------------------

    if (
        is_resume_specific_question(question)
        and not st.session_state.resume_profile
    ):

        st.warning(
            "📄 Please upload and analyze your resume first "
            "so I can assess your suitability."
        )

        st.stop()

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    # --------------------------------------------------------
    # GENERATE MENTOR RESPONSE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "🤔 Thinking..."
        ):

            try:

                relevant_notes = retrieve_notes(
                    question,
                    top_k=3
                )

                answer = create_mentor_response(
                    question,
                    relevant_notes,
                    st.session_state.resume_profile
                )

                st.markdown(
                    answer
                )

                # Save assistant response.
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                error_message = (
                    "❌ Sorry, something went wrong while "
                    "generating the answer:\n\n"
                    f"{e}"
                )

                st.exception(
                    e
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )