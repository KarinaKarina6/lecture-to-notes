import os
from pathlib import Path
import pytest
from unittest.mock import patch
from src import config


def test_load_secrets_missing(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with patch("src.config.load_dotenv"):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="HF_TOKEN не найден"):
                config.load_secrets()
