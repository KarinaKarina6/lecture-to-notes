from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
import sys

# Мокаем gigaam перед импортом src.transcribe, если он не установлен в легкой тестовой среде
if "gigaam" not in sys.modules:
    sys.modules["gigaam"] = MagicMock()

from src import transcribe


def test_format_timestamp():
    assert transcribe._format_timestamp(0) == "00:00:00"
    assert transcribe._format_timestamp(65) == "00:01:05"
    assert transcribe._format_timestamp(3665) == "01:01:05"


@patch("src.transcribe.gigaam")
@patch("src.transcribe.sf")
def test_transcribe_long_audio_chunks(mock_sf, mock_gigaam, tmp_path: Path):
    sr = 16000
    fake_audio = [0.1] * (sr * 40)
    mock_sf.read.return_value = (fake_audio, sr)

    mock_model = MagicMock()
    mock_model.transcribe.return_value = MagicMock(text="Привет мир")
    mock_gigaam.load_model.return_value = mock_model

    cfg = {
        "model": {"name": "v3_e2e_rnnt"},
        "audio": {
            "chunk_seconds": 20,
            "silence_threshold": 0.01,
        },
        "paths": {
            "temp_dir": str(tmp_path / "temp_chunks"),
        }
    }

    audio_path = tmp_path / "test.wav"
    audio_path.write_text("dummy")
    out_txt = tmp_path / "output" / "test_transcript.txt"

    transcribe.transcribe_long_audio(audio_path, cfg, out_txt)

    assert out_txt.exists()
    content = out_txt.read_text(encoding="utf-8")
    assert "[00:00:00] Привет мир" in content
    assert "[00:00:20] Привет мир" in content
