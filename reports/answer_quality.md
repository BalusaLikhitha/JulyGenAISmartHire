
Fill this in during Week 3. Do not just demo the app — measure it.

## 1. Retrieval relevance (semantic job search)
For a few sample profiles, list the top-5 jobs the search returned and mark each
relevant (yes) or not (no). Report the hit rate.

| Sample profile            | Top jobs returned | Relevant? (y/n) | Hit rate |
|----------------           |-------------------|-----------------|----------|
| e.g. Python + SQL fresher |  Python Developer/lead |      Yes   |   100%    |

## 2. Answer quality (AI Career Mentor)
Score mentor answers on a small set of test questions.

| Question | Correct? | Grounded in notes? | Helpful? | Notes |
|----------|----------|--------------------|----------|-------|
| e.g. "How do I switch to Data Analyst?" | | | | |

## 3. Prompt comparison (before / after)
Show at least one prompt you improved and the effect on the output.

**Before:**
You are an AI Career Mentor.

Answer the user's question.

Context:
{context}

Question:
{question}

Give a helpful answer.

**After:**
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
  skills, interviews and professional development.
- When the user asks whether they are suitable for a role,
  use the resume profile and job data to assess their suitability.

**What changed and why:**
The prompt was improved by adding context-only answering, preventing invented
facts, restricting answers to the career domain, and including the resume
profile for personalized career questions.

## 4. Hallucination check
Ask the mentor something that is NOT in the career notes. It should refuse or say
"I don't know", not make something up.

| Out-of-scope question | Did it refuse? (y/n) |
|-----------------------|----------------------|
| e.g. "Who is the Prime Minister of India?" | yes|
