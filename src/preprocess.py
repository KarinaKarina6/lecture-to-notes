import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def clean_transcript_text(raw_text: str) -> str:
    """
    Очищает сырой транскрипт от таймкодов [HH:MM:SS] или [MM:SS], слов-паразитов,
    заиканий и мусорных звуков, приводя текст к чистому виду для RAG.
    """
    if not raw_text:
        return ""

    # 1. Удаление таймкодов вида [00:42:20], [01:26:20], [12:34]
    text = re.sub(r'\[\d{1,2}:\d{2}(?::\d{2})?\]', '', raw_text)

    # 2. Удаление повторяющихся слогов/слов-заиканий вроде "ту-ту-ту", "вот-вот-вот"
    text = re.sub(r'\b([а-яёА-ЯЁ]{1,6})(?:-\1)+\b', r'\1', text, flags=re.IGNORECASE)

    # 3. Удаление повторяющихся слов через пробел (например, "про про", "вот вот")
    text = re.sub(r'\b([а-яёА-ЯЁ]{2,})\s+\1\b', r'\1', text, flags=re.IGNORECASE)

    # 4. Удаление фиксированных слов-паразитов двойных
    text = re.sub(r'\b(вот|ну|и|а|да|так)\s+\1\b', r'\1', text, flags=re.IGNORECASE)

    # 5. Удаление звуковых мусорных вставок и междометий (например, э-э-э, эм, хм)
    text = re.sub(r'\b[эеумх]+(?:-[эеумх]+)*\b', '', text, flags=re.IGNORECASE)

    # 6. Очистка лишних пробелов и знаков препинания перед ними
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)

    return text.strip()


def preprocess_transcript_file(input_path: Path, output_path: Path = None, cfg: dict = None) -> Path:
    """
    Читает файл сырого транскрипта, очищает от таймкодов и мусора, и сохраняет результат.
    """
    if cfg:
        prep_cfg = cfg.get("preprocess", {})
        if not prep_cfg.get("enabled", True):
            logger.info("Предобработка транскрипта отключена в конфигурации.")
            return None

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {input_path}")

    logger.info("Reading raw transcript from %s...", input_path)
    raw_text = path.read_text(encoding="utf-8")

    logger.info("Cleaning transcript text and removing timestamps...")
    cleaned_text = clean_transcript_text(raw_text)

    if output_path is None:
        output_path = path.with_name(path.stem + "_rag_clean.txt")
    
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info("Saving RAG-clean transcript to %s...", out_path)
    out_path.write_text(cleaned_text, encoding="utf-8")
    logger.info("Pre-processing completed successfully!")

    return out_path
