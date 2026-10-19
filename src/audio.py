import subprocess
from pathlib import Path


def convert_to_wav(
    input_path: Path, output_path: Path, sample_rate: int = 16000
) -> Path:
    """Конвертирует любой медиафайл в моно WAV 16 кГц через FFmpeg."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
