import os
import faiss
import numpy as np
import pandas as pd

from src.config import JOBS_CSV, JOBS_INDEX_DIR, JOB_TEXT_COLUMNS
from src.search.embed import get_embeddings, EMBED_DIM


BATCH_SIZE = 32


def build_job_index():

    # Load complete dataset
    df = pd.read_csv(JOBS_CSV)

    print(f"Total jobs in dataset: {len(df)}")

    # Use ALL jobs
    df = df.copy()

    print(f"Jobs selected for FAISS: {len(df)}")

    # Combine job title + skills + description
    job_texts = []

    for _, row in df.iterrows():

        text_parts = []

        for column in JOB_TEXT_COLUMNS:

            value = row.get(column, "")

            if pd.notna(value):
                text_parts.append(str(value))

        job_texts.append(" ".join(text_parts))

    # Create embeddings in batches
    embeddings = []

    total_batches = (
        len(job_texts) + BATCH_SIZE - 1
    ) // BATCH_SIZE

    for start in range(0, len(job_texts), BATCH_SIZE):

        end = min(
            start + BATCH_SIZE,
            len(job_texts)
        )

        batch_texts = job_texts[start:end]

        batch_number = (start // BATCH_SIZE) + 1

        print(
            f"Embedding batch {batch_number}/{total_batches} "
            f"({start + 1}-{end})"
        )

        batch_embeddings = get_embeddings(batch_texts)

        # Normalize each embedding
        for embedding in batch_embeddings:

            norm = np.linalg.norm(embedding)

            if norm != 0:
                embedding = embedding / norm

            embeddings.append(embedding)

    # Convert embeddings to NumPy array
    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    print(
        f"\nTotal embeddings created: "
        f"{len(embeddings)}"
    )

    # Create FAISS index
    index = faiss.IndexFlatIP(
        EMBED_DIM
    )

    # Add ALL embeddings
    index.add(embeddings)

    # Create directory
    os.makedirs(
        JOBS_INDEX_DIR,
        exist_ok=True
    )

    # Save FAISS index
    index_path = os.path.join(
        JOBS_INDEX_DIR,
        "jobs.index"
    )

    faiss.write_index(
        index,
        index_path
    )

    # Save corresponding ALL job data
    data_path = os.path.join(
        JOBS_INDEX_DIR,
        "jobs.csv"
    )

    df.to_csv(
        data_path,
        index=False
    )

    print("\n--------------------------------")
    print("FAISS INDEX CREATED SUCCESSFULLY")
    print("--------------------------------")
    print(f"Index: {index_path}")
    print(f"Jobs:  {data_path}")
    print(f"Vectors: {index.ntotal}")


if __name__ == "__main__":
    build_job_index()