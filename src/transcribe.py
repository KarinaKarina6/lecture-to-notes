import os
import time
from pathlib import Path
import numpy as np
import soundfile as sf
import gigaam
from src.config import load_secrets

load_secrets()


def transcribe_long_audio(audio_path: Path, cfg: dict, out_txt: Path) -> None:
    model = gigaam.load_model(cfg["model"]["name"])
    data, sr = sf.read(audio_path, dtype="float32")

    chunk_size = sr * cfg["audio"]["chunk_seconds"]
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    temp_dir = Path(cfg["paths"]["temp_dir"])
    temp_dir.mkdir(exist_ok=True)

    start_time = time.time()
    with open(out_txt, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            if np.max(np.abs(chunk)) < cfg["audio"]["silence_threshold"]:
                continue

            time_str = _format_timestamp(i * cfg["audio"]["chunk_seconds"])
            temp_file = temp_dir / f"chunk_{i:04d}.wav"
            sf.write(temp_file, chunk, sr)

            try:
                result = model.transcribe(str(temp_file))
                text = result.text if hasattr(result, "text") else str(result)
                f.write(f"[{time_str}] {text.strip()}\n")
                f.flush()
            except Exception as e:
                f.write(f"[{time_str}] [ОШИБКА: {e}]\n")
            finally:
                temp_file.unlink(missing_ok=True)

    print(f"Готово за {round((time.time() - start_time) / 60, 1)} мин → {out_txt}")


def _format_timestamp(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s:02}"
