import os
import logging
from pathlib import Path
from google import genai
from google.genai import errors

logger = logging.getLogger(__name__)


def summarize_transcript(transcript_path: Path, output_path: Path, cfg: dict) -> None:
    """Генерирует конспект лекции по транскрипту с помощью Gemini 3.5 Flash Lite."""
    sum_cfg = cfg.get("summarize", {})
    if not sum_cfg.get("enabled", False):
        logger.info("Суммаризация отключена в конфигурации.")
        return

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY (или GOOGLE_API_KEY) не найден в переменных окружения. Укажите его в .env"
        )

    if not transcript_path.exists():
        raise FileNotFoundError(f"Файл транскрипта не найден: {transcript_path}")

    transcript_text = transcript_path.read_text(encoding="utf-8")
    if not transcript_text.strip():
        logger.warning("Транскрипт пуст, суммаризация пропущена.")
        return

    model_name = sum_cfg.get("model_name", "gemini-3.5-flash-lite")
    prompt_template = sum_cfg.get("prompt", "Составь конспект:\n\n{transcript}")
    prompt = prompt_template.format(transcript=transcript_text)

    logger.info("Отправка транскрипта в Gemini (%s) для генерации конспекта...", model_name)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        
        notes_content = response.text
        output_path.write_text(notes_content, encoding="utf-8")
        logger.info("Конспект успешно сохранен в %s", output_path)

    except errors.APIError as e:
        logger.error("Ошибка Gemini API при генерации конспекта: %s", e)
        raise
    except Exception as e:
        logger.exception("Непредвиденная ошибка при суммаризации: %s", e)
        raise
