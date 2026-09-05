import os
import faiss
import numpy as np
import pandas as pd

from dotenv import load_dotenv


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.safety.guardrails import check_input
from src.config import NOTES_INDEX_DIR, JOBS_INDEX_DIR
from src.search.embed import get_embedding, normalize_embedding




load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in .env")



MODEL_NAME = "gemini-3.5-flash-lite"

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY
)




mentor_prompt = ChatPromptTemplate.from_template(
    """
You are an AI Career Mentor.

Answer the user's career-related question using ONLY the
information provided in the context.
RESUME PROFILE:
{resume_profile}

CONTEXT:
{context}

USER QUESTION:
{question}

RULES:
- Use only information available in the context.
- Do not invent facts.
- Do not use outside knowledge.
- If the answer is not available in the context, clearly say:
  "The information is not available in the provided career
  notes or job data."
- Give a clear and helpful answer.
- Keep the answer relevant to career, jobs, resumes,
  skills, interviews, learning and professional development.
- When the user asks whether they are suitable for a role, use the resume profile and job data to assess their suitability.
"""
)



mentor_chain = (
    mentor_prompt
    | llm
    | StrOutputParser()
).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)




def load_notes_index():

    index_path = os.path.join(
        NOTES_INDEX_DIR,
        "notes.index"
    )

    data_path = os.path.join(
        NOTES_INDEX_DIR,
        "notes_data.txt"
    )

    index = faiss.read_index(index_path)

    with open(
        data_path,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    blocks = content.split(
        "\n\n====================\n\n"
    )

    notes = []

    for block in blocks:

        if not block.strip():
            continue

        text_start = block.find("TEXT:\n")

        if text_start != -1:

            text = block[
                text_start + len("TEXT:\n"):
            ]

            notes.append(text)

    return index, notes


# =

def retrieve_notes(question, top_k=3):

    allowed, message = check_input(question)

    if not allowed:
        return []

    index, notes = load_notes_index()

    question_embedding = get_embedding(question)

    question_embedding = normalize_embedding(
        question_embedding
    )

    question_embedding = np.array(
        [question_embedding],
        dtype="float32"
    )

    scores, indices = index.search(
        question_embedding,
        min(top_k, index.ntotal)
    )

    relevant_notes = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx == -1:
            continue

        relevant_notes.append(
            notes[idx]
        )

    return relevant_notes




def load_job_index():

    index_path = os.path.join(
        JOBS_INDEX_DIR,
        "jobs.index"
    )

    jobs_path = os.path.join(
        JOBS_INDEX_DIR,
        "jobs.csv"
    )

    index = faiss.read_index(index_path)

    jobs = pd.read_csv(jobs_path)

    return index, jobs



def retrieve_jobs(question, top_k=3):

    try:

        index, jobs = load_job_index()

    except Exception:
        return []

    if index.ntotal == 0:
        return []

    question_embedding = get_embedding(question)

    question_embedding = normalize_embedding(
        question_embedding
    )

    question_embedding = np.array(
        [question_embedding],
        dtype="float32"
    )

    scores, indices = index.search(
        question_embedding,
        min(top_k, index.ntotal)
    )

    relevant_jobs = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx == -1:
            continue

        job = jobs.iloc[idx].to_dict()

        job["similarity_score"] = float(score)

        relevant_jobs.append(job)

    return relevant_jobs



def create_context(
    relevant_notes,
    relevant_jobs
):

    context_parts = []

    # Career notes
    if relevant_notes:

        context_parts.append(
            "CAREER NOTES:\n"
            + "\n\n".join(relevant_notes)
        )

    # Job data
    if relevant_jobs:

        job_text = []

        for i, job in enumerate(
            relevant_jobs,
            start=1
        ):

            title = job.get(
                "jobtitle",
                ""
            )

            company = job.get(
                "company",
                ""
            )

            skills = job.get(
                "skills",
                ""
            )

            description = job.get(
                "jobdescription",
                ""
            )

            # Keep context reasonably small
            description = str(description)[:1200]

            job_text.append(
                f"""
Job {i}:
Title: {title}
Company: {company}
Skills: {skills}
Description: {description}
"""
            )

        context_parts.append(
            "JOB DATA:\n"
            + "\n".join(job_text)
        )

    if not context_parts:

        return "No relevant career notes or job data were found."

    return "\n\n====================\n\n".join(
        context_parts
    )




def create_mentor_response(
    question,
    relevant_notes,
    resume_profile=None
):

    

    allowed, message = check_input(question)

    if not allowed:
        return message


   

    relevant_jobs = retrieve_jobs(
        question,
        top_k=3
    )



    context = create_context(
        relevant_notes,
        relevant_jobs
    )


   

    response = mentor_chain.invoke(
    {
        "context": context,
        "question": question,
        "resume_profile": resume_profile
    }
)

    return response