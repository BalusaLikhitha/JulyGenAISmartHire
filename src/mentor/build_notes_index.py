import os
import faiss
import numpy as np

from src.config import CAREER_NOTES_DIR, NOTES_INDEX_DIR
from src.parsing.loader import load_folder
from src.search.embed import get_embedding, normalize_embedding


def build_notes_index():

    notes = load_folder(CAREER_NOTES_DIR)

    print(f"Total note chunks: {len(notes)}")

   
    print(f"Using note chunks: {len(notes)}")

    # item[0] = actual chunk text
    # item[1] = source filename
    note_texts = [item[0] for item in notes]
    source_names = [item[1] for item in notes]

    embeddings = []

    for i, text in enumerate(note_texts):

        print(f"Embedding note {i + 1}/{len(note_texts)}")

        embedding = get_embedding(text)
        embedding = normalize_embedding(embedding)

        embeddings.append(embedding)

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    index = faiss.IndexFlatIP(
        embeddings.shape[1]
    )

    index.add(embeddings)

    os.makedirs(
        NOTES_INDEX_DIR,
        exist_ok=True
    )

    index_path = os.path.join(
        NOTES_INDEX_DIR,
        "notes.index"
    )

    faiss.write_index(
        index,
        index_path
    )

    # Save text and source information together
    notes_data_path = os.path.join(
        NOTES_INDEX_DIR,
        "notes_data.txt"
    )

    with open(
        notes_data_path,
        "w",
        encoding="utf-8"
    ) as file:

        for i, (text, source) in enumerate(
            zip(note_texts, source_names)
        ):

            file.write(f"INDEX: {i}\n")
            file.write(f"SOURCE: {source}\n")
            file.write("TEXT:\n")
            file.write(text)
            file.write("\n\n====================\n\n")

    print("\n--------------------------------")
    print("CAREER NOTES FAISS INDEX CREATED")
    print("--------------------------------")
    print(f"Index: {index_path}")
    print(f"Data:  {notes_data_path}")
    print(f"Vectors: {index.ntotal}")


if __name__ == "__main__":
    build_notes_index()