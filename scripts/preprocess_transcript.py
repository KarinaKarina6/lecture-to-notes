import argparse
from pathlib import Path
from src.preprocess import preprocess_transcript_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess transcript for RAG (remove timestamps & noise).")
    parser.add_argument("--input", type=str, default="output/test2_transcript.txt", help="Path to raw transcript file")
    parser.add_argument("--output", type=str, default=None, help="Path to output RAG-clean transcript file")
    args = parser.parse_args()

    preprocess_transcript_file(Path(args.input), Path(args.output) if args.output else None)
