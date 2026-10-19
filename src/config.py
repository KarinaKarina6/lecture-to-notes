import os
from pathlib import Path
from dotenv import load_dotenv

def load_secrets() -> None:
    """Загружает .env из корня проекта в переменные окружения."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN не найден. Скопируйте .env.example в .env и вставьте токен."
        )
    os.environ["HF_TOKEN"] = token