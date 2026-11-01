import argparse
import logging
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.audio import AudioConversionError, convert_to_wav
from src.logging_setup import setup_logging
from src.summarize import summarize_transcript
from src.transcribe import transcribe_long_audio

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lecture to Notes pipeline")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config", default="config.yaml", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.config.exists():
        print(f"Конфиг не найден: {args.config}", file=sys.stderr)
        return 2

    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    out_dir = Path(cfg["paths"]["output_dir"])
    setup_logging(log_file=out_dir / "pipeline.log")

    load_dotenv()
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = args.input.stem
    wav_path = out_dir / f"{stem}.wav"
    txt_path = out_dir / f"{stem}_transcript.txt"
    notes_path = out_dir / f"{stem}_notes.md"

    try:
        convert_to_wav(args.input, wav_path, cfg["audio"]["sample_rate"])
        transcribe_long_audio(wav_path, cfg, txt_path)
        summarize_transcript(txt_path, notes_path, cfg)
    except AudioConversionError as e:
        logger.error("Конвертация не удалась: %s", e)
        return 1
    except Exception:
        logger.exception("Необработанная ошибка пайплайна")
        return 1

    logger.info("Готово: транскрипт -> %s, конспект -> %s", txt_path, notes_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
