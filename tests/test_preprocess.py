from pathlib import Path
import pytest
from src.preprocess import clean_transcript_text, preprocess_transcript_file


def test_clean_transcript_text_basic():
    raw = "[00:01:23] Всем привет, [00:01:25] сегодня мы изучаем вот-вот Python про программирование."
    cleaned = clean_transcript_text(raw)
    assert "[00:01:23]" not in cleaned
    assert "вот-вот" not in cleaned
    assert "Всем привет, сегодня мы изучаем вот Python про программирование." in cleaned


def test_clean_transcript_text_timestamps_and_noise():
    raw = "[01:20:10] Э-э-э, ну вот, значит, [00:15] мы изучили это."
    cleaned = clean_transcript_text(raw)
    assert "[01:20:10]" not in cleaned
    assert "[00:15]" not in cleaned
    assert "Э-э-э" not in cleaned
    assert "ну" in cleaned
    assert "значит, мы изучили это." in cleaned


def test_clean_transcript_text_empty():
    assert clean_transcript_text("") == ""
    assert clean_transcript_text(None) == ""


def test_preprocess_transcript_file_success(tmp_path: Path):
    txt_path = tmp_path / "lecture_transcript.txt"
    txt_path.write_text("[00:00:05] Тестовая лекция. Э-э-э привет.", encoding="utf-8")
    
    cfg = {"preprocess": {"enabled": True}}
    out_path = preprocess_transcript_file(txt_path, cfg=cfg)

    assert out_path.exists()
    assert out_path.name == "lecture_transcript_rag_clean.txt"
    content = out_path.read_text(encoding="utf-8")
    assert "[00:00:05]" not in content
    assert "Э-э-э" not in content
    assert "Тестовая лекция. привет." in content


def test_preprocess_transcript_file_disabled(tmp_path: Path):
    txt_path = tmp_path / "lecture_transcript.txt"
    txt_path.write_text("[00:00:05] Тестовая лекция.", encoding="utf-8")
    
    cfg = {"preprocess": {"enabled": False}}
    out_path = preprocess_transcript_file(txt_path, cfg=cfg)

    assert out_path is None


def test_preprocess_transcript_file_custom_output(tmp_path: Path):
    txt_path = tmp_path / "lecture_transcript.txt"
    txt_path.write_text("[00:00:05] Тестовая лекция. Эм, проверка.", encoding="utf-8")
    custom_out = tmp_path / "custom_subdir" / "my_clean_notes.txt"

    out_path = preprocess_transcript_file(txt_path, output_path=custom_out)

    assert out_path == custom_out
    assert custom_out.exists()
    content = custom_out.read_text(encoding="utf-8")
    assert "[00:00:05]" not in content
    assert "Эм" not in content


def test_preprocess_transcript_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        preprocess_transcript_file(tmp_path / "nonexistent.txt")
