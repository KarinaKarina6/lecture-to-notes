from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from src import summarize


def test_summarize_disabled(tmp_path: Path):
    cfg = {"summarize": {"enabled": False}}
    txt_path = tmp_path / "transcript.txt"
    notes_path = tmp_path / "notes.md"
    
    summarize.summarize_transcript(txt_path, notes_path, cfg)
    assert not notes_path.exists()


def test_summarize_empty_transcript(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    cfg = {"summarize": {"enabled": True}}
    txt_path = tmp_path / "transcript.txt"
    txt_path.write_text("   \n", encoding="utf-8")
    notes_path = tmp_path / "notes.md"
    
    summarize.summarize_transcript(txt_path, notes_path, cfg)
    assert not notes_path.exists()


@patch("src.summarize.genai")
def test_summarize_success(mock_genai, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    cfg = {
        "summarize": {
            "enabled": True,
            "model_name": "gemini-3.5-flash-lite",
            "prompt": "Конспект:\n{transcript}"
        }
    }
    txt_path = tmp_path / "transcript.txt"
    txt_path.write_text("[00:00:00] Лекция началась", encoding="utf-8")
    notes_path = tmp_path / "notes.md"

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "# Конспект\n- Начало лекции"
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client

    summarize.summarize_transcript(txt_path, notes_path, cfg)

    assert notes_path.exists()
    assert "# Конспект" in notes_path.read_text(encoding="utf-8")
    mock_client.models.generate_content.assert_called_once()
