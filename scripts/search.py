import os
import pickle
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def search_index(query: str, vector_store_dir: str = "vector_store", top_k: int = 3):
    """
    Выполняет семантический поиск по FAISS индексу.
    """
    vs_path = Path(vector_store_dir)
    index_file = vs_path / "faiss.index"
    metadata_file = vs_path / "metadata.pkl"

    if not index_file.exists() or not metadata_file.exists():
        raise FileNotFoundError(f"Vector store not found in {vector_store_dir}. Please run build_index.py first.")

    print(f"Loading index from {index_file}...")
    index = faiss.read_index(str(index_file))

    print(f"Loading metadata from {metadata_file}...")
    with open(metadata_file, "rb") as f:
        chunks = pickle.load(f)

    print("Loading embedding model...")
    model = SentenceTransformer("intfloat/multilingual-e5-small")

    # Для моделей e5 запрос должен содержать префикс "query: "
    query_text = f"query: {query}"
    print(f"Encoding query: '{query}'...")
    query_vector = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)

    print(f"Searching top {top_k} results...")
    distances, indices = index.search(query_vector, top_k)

    results = []
    for score, idx in zip(distances[0], indices[0]):
        if idx < len(chunks):
            results.append({
                "score": float(score),
                "text": chunks[idx]["text"],
                "start_word": chunks[idx]["start_word"],
                "end_word": chunks[idx]["end_word"]
            })
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Search in FAISS vector index.")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument("--vector_store", type=str, default="vector_store", help="Path to vector store directory")
    parser.add_argument("--top_k", type=int, default=3, help="Number of top results to return")
    args = parser.parse_args()

    results = search_index(args.query, args.vector_store, args.top_k)
    print(f"\n--- Search Results for: '{args.query}' ---")
    for i, res in enumerate(results, 1):
        print(f"\n[{i}] Score: {res['score']:.4f}")
        print(f"Text: {res['text']}")
