# Lecture to Notes

Транскрибация длинных видеолекций в текст с таймкодами и автоматический конспект. Оптимизировано под ноутбук с 4 ГБ VRAM (NVIDIA RTX 3050 Ti, Windows 11).

## Пайплайн

1. FFmpeg → моно WAV 16 кГц
2. Нарезка на 20-секундные чанки (обход ограничений GigaAM на длинных файлах)
3. Инференс GigaAM-v3 (e2e_rnnt) с восстановлением таймкодов
4. (опционально) Конспект через LLM API

## Результат

- `output/<name>_transcript.txt` — транскрипт с таймкодами
- `output/<name>_notes.md` — конспект

## Установка

```bash
git clone <repo>
cd lecture-to-notes
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Запуск

```bash
python -m scripts.run_pipeline --input test.mp4
```
