"""
Evaluation utilities for SmartHire GenAI.

This module provides simple functions to evaluate:
1. Semantic job retrieval
2. AI Career Mentor guardrails
3. Mentor answer quality
"""


# ============================================================
# 1. RETRIEVAL EVALUATION
# ============================================================

def retrieval_hit_rate(relevant_flags):
    """
    Calculate retrieval hit rate.

    relevant_flags should contain True for relevant jobs
    and False for irrelevant jobs.

    Example:
        [True, False, True, False, True]

    Returns:
        0.6
    """

    if not relevant_flags:
        return 0.0

    relevant_count = sum(bool(flag) for flag in relevant_flags)

    return relevant_count / len(relevant_flags)


def print_retrieval_evaluation(profile, jobs, relevant_flags):
    """
    Print the retrieved jobs and calculate hit rate.
    """

    print("\n==============================")
    print("RETRIEVAL EVALUATION")
    print("==============================")

    print(f"\nSample Profile:")
    print(profile)

    print("\nRetrieved Jobs:")

    for i, (job, relevant) in enumerate(
        zip(jobs, relevant_flags),
        start=1
    ):
        title = job.get("jobtitle", "Unknown Job")
        company = job.get("company", "Unknown Company")

        status = "Yes" if relevant else "No"

        print(
            f"{i}. {title} | "
            f"{company} | "
            f"Relevant: {status}"
        )

    hit_rate = retrieval_hit_rate(relevant_flags)

    print(f"\nHit Rate: {hit_rate:.1%}")


# ============================================================
# 2. GUARDRAIL EVALUATION
# ============================================================

def evaluate_guardrail(check_input, questions):
    """
    Test the guardrail against a list of questions.

    Parameters:
        check_input:
            The guardrail function from guardrails.py

        questions:
            List of questions to test.
    """

    print("\n==============================")
    print("GUARDRAIL EVALUATION")
    print("==============================")

    for question in questions:

        allowed, message = check_input(question)

        if allowed:
            status = "ALLOWED"
        else:
            status = "REJECTED"

        print(f"\nQuestion: {question}")
        print(f"Status: {status}")

        if message:
            print(f"Message: {message}")


# ============================================================
# 3. MENTOR ANSWER EVALUATION
# ============================================================

def evaluate_answer(answer, expected_keywords=None):
    """
    Perform a simple keyword-based evaluation of a Mentor answer.

    This is only a basic evaluation helper.
    Human evaluation should still be used for correctness,
    grounding and helpfulness.
    """

    if not answer:
        return {
            "correct": False,
            "helpful": False
        }

    answer_lower = answer.lower()

    if not expected_keywords:
        return {
            "correct": True,
            "helpful": True
        }

    matched = 0

    for keyword in expected_keywords:

        if keyword.lower() in answer_lower:
            matched += 1

    correct = matched > 0

    return {
        "correct": correct,
        "helpful": correct
    }


# ============================================================
# 4. PRINT MENTOR EVALUATION
# ============================================================

def print_mentor_evaluation(
    question,
    answer,
    grounded=True,
    helpful=True
):
    """
    Print a Mentor evaluation result.
    """

    print("\n==============================")
    print("MENTOR ANSWER EVALUATION")
    print("==============================")

    print(f"\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)

    print("\nEvaluation:")
    print(f"Correct: {'Yes' if grounded else 'No'}")
    print(f"Grounded in notes: {'Yes' if grounded else 'No'}")
    print(f"Helpful: {'Yes' if helpful else 'No'}")


# ============================================================
# 5. HALLUCINATION / REFUSAL CHECK
# ============================================================

def check_refusal(answer):
    """
    Check whether the Mentor produced a refusal response
    when information is unavailable.
    """

    if not answer:
        return False

    refusal_phrases = [
        "information is not available",
        "i don't know",
        "not available in the provided",
        "please ask a career-related question"
    ]

    answer_lower = answer.lower()

    return any(
        phrase in answer_lower
        for phrase in refusal_phrases
    )


# ============================================================
# 6. SIMPLE DEMONSTRATION
# ============================================================

if __name__ == "__main__":

    print("==============================")
    print("SMART HIRE EVALUATION")
    print("==============================")

    sample_flags = [
        True,
        False,
        True,
        False,
        False
    ]

    rate = retrieval_hit_rate(sample_flags)

    print(f"\nSample Retrieval Hit Rate: {rate:.1%}")

    sample_questions = [
        "What skills are important for a data analyst?",
        "How do I become a software developer?",
        "Who is the Prime Minister of India?",
        "What is the weather today?"
    ]

    print("\nSample evaluation questions:")

    for question in sample_questions:
        print(f"- {question}")

    print("\nEvaluation module loaded successfully.")