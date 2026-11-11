import os
import pickle
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Разбивает текст на чанки с перекрытием.
    Возвращает список словарей с текстом чанка и его метаданными.
    """
    words = text.split()
    chunks = []
    if not words:
        return chunks
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "text": chunk_text,
            "start_word": start,
            "end_word": end
        })
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks

def build_index(transcript_path: str, output_dir: str = "vector_store"):
    """
    Читает файл транскрипта, разбивает на чанки, генерирует эмбеддинги 
    с помощью intfloat/multilingual-e5-small и сохраняет индекс FAISS вместе с метаданными.
    """
    path = Path(transcript_path)
    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

    print(f"Reading transcript from {transcript_path}...")
    text = path.read_text(encoding="utf-8")

    print("Chunking text...")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks.")

    if not chunks:
        print("No text found to index.")
        return

    # Для моделей семейства e5 рекомендуется добавлять префикс "passage: " для документов
    texts_to_embed = [f"passage: {c['text']}" for c in chunks]

    print("Loading embedding model (intfloat/multilingual-e5-small)...")
    model = SentenceTransformer("intfloat/multilingual-e5-small")

    print("Generating embeddings...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True, convert_to_numpy=True)
    
    # Нормализация для cosine similarity через Inner Product в FAISS
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    print(f"Creating FAISS index with dimension {dimension}...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    index_file = out_path / "faiss.index"
    metadata_file = out_path / "metadata.pkl"

    print(f"Saving index to {index_file}...")
    faiss.write_index(index, str(index_file))

    print(f"Saving metadata to {metadata_file}...")
    with open(metadata_file, "wb") as f:
        pickle.dump(chunks, f)

    print("Indexing completed successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build FAISS vector index from transcript.")
    parser.add_argument("--transcript", type=str, default="output/test2_transcript.txt", help="Path to transcript file")
    parser.add_argument("--output", type=str, default="vector_store", help="Output directory for vector store")
    args = parser.parse_args()

    build_index(args.transcript, args.output)
