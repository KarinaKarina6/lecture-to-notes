from pathlib import Path

import pytest

from src import audio


def test_check_ffmpeg_raises_when_missing(monkeypatch):
    monkeypatch.setattr(audio.shutil, "which", lambda _: None)
    with pytest.raises(audio.AudioConversionError, match="ffmpeg не найден"):
        audio.check_ffmpeg()


def test_convert_missing_input(tmp_path: Path):
    with pytest.raises(audio.AudioConversionError, match="не найден"):
        audio.convert_to_wav(tmp_path / "nope.mp4", tmp_path / "out.wav")