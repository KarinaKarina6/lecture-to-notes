import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioConversionError(RuntimeError):
    """Ошибка конвертации медиафайла через FFmpeg."""


def check_ffmpeg() -> None:
    """Проверяет, что ffmpeg доступен в PATH."""
    if shutil.which("ffmpeg") is None:
        raise AudioConversionError(
            "ffmpeg не найден в PATH. Установите FFmpeg и добавьте его в PATH "
            "(Windows: https://ffmpeg.org/download.html)."
        )


def convert_to_wav(
    input_path: Path, output_path: Path, sample_rate: int = 16000
) -> Path:
    """Конвертирует любой медиафайл в моно WAV 16 кГц через FFmpeg."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise AudioConversionError(f"Входной файл не найден: {input_path}")
    if not input_path.is_file():
        raise AudioConversionError(f"Входной путь не файл: {input_path}")

    check_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vn", "-ar", str(sample_rate), "-ac", "1",
        "-c:a", "pcm_s16le", str(output_path),
    ]
    logger.info("FFmpeg: %s → %s", input_path.name, output_path.name)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or b"").decode("utf-8", errors="replace")
        logger.error("FFmpeg завершился с кодом %s:\n%s", e.returncode, stderr)
        raise AudioConversionError(
            f"FFmpeg не смог конвертировать {input_path.name} (код {e.returncode}). "
            "Подробности в логе."
        ) from e

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise AudioConversionError(f"FFmpeg не создал WAV: {output_path}")

    logger.info("WAV готов: %s (%.1f МБ)", output_path.name,
                output_path.stat().st_size / 1024 / 1024)
    return output_path