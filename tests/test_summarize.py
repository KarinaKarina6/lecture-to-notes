from pathlib import Path
import pytest
from src import summarize

def test_summarize_disabled(tmp_path: Path):
    cfg = {"summarize": {"enabled": False}}
    txt_path = tmp_path / "transcript.txt"
    notes_path = tmp_path / "notes.md"
    
    # Не должно вызывать ошибок или делать запросы, если выключено
    summarize.summarize_transcript(txt_path, notes_path, cfg)
    assert not notes_path.exists()
