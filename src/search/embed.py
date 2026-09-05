import numpy as np
from sentence_transformers import SentenceTransformer



EMBED_MODEL = "all-MiniLM-L6-v2"

# all-MiniLM-L6-v2 produces 384-dimensional embeddings
EMBED_DIM = 384


model = SentenceTransformer(EMBED_MODEL)


def get_embedding(text: str):
    """
    Convert text into a local semantic embedding vector.
    """

    embedding = model.encode(
        text,
        convert_to_numpy=True
    )

    embedding = np.array(
        embedding,
        dtype="float32"
    )

    return embedding


def get_embeddings(texts):
    """
    Convert multiple texts into embeddings efficiently.
    """

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return np.array(
        embeddings,
        dtype="float32"
    )


def normalize_embedding(embedding):
    """
    Normalize embedding for cosine similarity.
    """

    norm = np.linalg.norm(embedding)

    if norm == 0:
        return embedding

    return embedding / norm