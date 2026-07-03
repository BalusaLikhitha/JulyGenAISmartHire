"""Module 1 — Resume parser.

Read an uploaded resume (via loader.load_text), send it to the LLM with a strict
prompt, and get back clean JSON: name, skills, experience, education, target_role.
Validate the JSON before returning it. Build this in notebook 01, then move the
working function here. Use structured output (the JSON-parser technique from class).
"""
