import os
import faiss
import pandas as pd
import numpy as np

from src.config import JOBS_INDEX_DIR
from src.search.embed import get_embedding, normalize_embedding


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


def search_jobs(resume_text, top_k=5):

    
    index, jobs = load_job_index()

    
    resume_embedding = get_embedding(resume_text)

    
    resume_embedding = normalize_embedding(
        resume_embedding
    )

   
    resume_embedding = np.array(
        [resume_embedding],
        dtype="float32"
    )

    
    scores, indices = index.search(
        resume_embedding,
        min(top_k, index.ntotal)
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        job = jobs.iloc[idx].to_dict()

        job["similarity_score"] = float(score)

        results.append(job)

    return results