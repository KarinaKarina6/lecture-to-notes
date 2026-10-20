import argparse
from pathlib import Path
import yaml
from dotenv import load_dotenv

from src.audio import convert_to_wav
from src.transcribe import transcribe_long_audio


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config", default="config.yaml", type=Path)
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    out_dir = Path(cfg["paths"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = args.input.stem
    wav_path = out_dir / f"{stem}.wav"
    txt_path = out_dir / f"{stem}_transcript.txt"

    convert_to_wav(args.input, wav_path, cfg["audio"]["sample_rate"])
    transcribe_long_audio(wav_path, cfg, txt_path)


if __name__ == "__main__":
    main()
