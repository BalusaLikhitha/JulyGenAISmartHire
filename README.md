# SmartHire GenAI — Resume Matching & AI Career Mentor

SmartHire GenAI is a Generative AI-powered career portal that helps users analyze their resumes, discover relevant jobs, improve their CVs, and receive personalized career guidance through an AI Career Mentor.

The system combines resume parsing, semantic job matching, Retrieval-Augmented Generation (RAG), FAISS vector search, Gemini, LangChain, and safety guardrails into a single Streamlit application.

---

## Features

### 1. Resume Parser

Users can upload resumes in:

- PDF
- DOCX
- TXT

The resume is processed using Gemini and converted into a structured profile containing:

- Name
- Email
- Phone
- LinkedIn URL
- Education
- Skills
- Experience
- Projects
- Total experience
- Professional summary

The parser is designed to extract information only from the uploaded resume and avoid inventing missing details.

---

### 2. Semantic Job Search

SmartHire uses semantic similarity to match resumes with relevant job descriptions.

The job descriptions are converted into vector embeddings using the Sentence Transformers model:

`all-MiniLM-L6-v2`

The embeddings are stored in a FAISS index.

The matching process works as follows:

1. The user uploads and analyzes a resume.
2. The resume information is converted into text.
3. The resume text is converted into an embedding.
4. FAISS compares the resume embedding with the job embeddings.
5. The most semantically similar jobs are retrieved.
6. The application displays the top matching jobs with similarity scores.

This allows the system to identify jobs based on the meaning and skills in the resume rather than relying only on exact keyword matching.

---

### 3. AI CV Improvement

The CV Improvement module analyzes the user's resume and provides AI-generated suggestions.

The system provides suggestions for:

- Skills improvement
- Weak resume sections
- Professional summary
- Project descriptions
- Experience descriptions
- Overall resume improvement

The AI is instructed not to invent:

- Work experience
- Achievements
- Education
- Skills
- Projects
- Other unsupported information

---

### 4. AI Career Mentor

SmartHire includes an AI Career Mentor powered by Retrieval-Augmented Generation (RAG).

The mentor can answer supported career-related questions about topics such as:

- Career development
- Software development
- Full-stack development
- Data analytics
- Resume improvement
- Interview preparation
- Skills
- Projects
- Job-related guidance

The mentor uses curated career notes and job information as its knowledge source.

The RAG workflow is:

1. The user asks a question.
2. Guardrails check the question.
3. The question is converted into an embedding.
4. Relevant career notes are retrieved using FAISS.
5. Relevant job information is retrieved.
6. The retrieved information is provided as context to Gemini.
7. Gemini generates the final response.

The Mentor is instructed to answer using only the retrieved context.

If the required information is not available, the system responds:

> "The information is not available in the provided career notes or job data."

This helps reduce unsupported or hallucinated answers.

---

### 5. Resume-Specific Career Guidance

SmartHire can distinguish between general career questions and questions that require the user's own resume.

For example:

- "What skills should a data analyst learn?" → General career question
- "Am I suitable for this data analyst job?" → Resume-specific question
- "Are my skills enough for a software developer role?" → Resume-specific question

For personalized questions, the system asks the user to upload and analyze their resume first if a resume profile is not available.

When a resume is available, the mentor can use the resume profile together with retrieved career and job information.

---

### 6. Guardrails

Guardrails are applied before sending questions to the LLM.

The system:

- Rejects empty questions
- Rejects unsafe questions
- Rejects unrelated questions
- Allows supported career-related questions
- Detects resume-specific questions
- Prevents the Career Mentor from operating outside the supported career domain

This provides an additional safety layer before the LLM is called.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web application interface |
| Gemini API | Resume parsing, CV suggestions and Career Mentor |
| Gemini 3.5 Flash Lite | Generative AI model |
| Sentence Transformers | Local semantic embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| FAISS | Vector similarity search |
| LangChain | LLM and RAG pipeline |
| RAG | Grounded career question answering |
| Pandas | Dataset processing |
| PDF/DOCX/TXT processing | Resume extraction |

---

## System Architecture

Resume Upload
     ↓
PDF / DOCX / TXT Extraction
     ↓
Gemini Resume Parser
     ↓
Structured Resume Profile
     ↓
┌──────────────────────┐
│                      │
↓                      ↓
Job Matching       CV Improvement
│                      │
↓                      ↓
FAISS Search        Gemini
│                      │
↓                      ↓
Matching Jobs       Suggestions