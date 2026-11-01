# AGENTS.md

## Project Overview
Pipeline for transcribing long video lectures (GigaAM-v3) and generating notes (LLM).
Environment: **Windows 11**, Python.
Hardware constraint: **4 GB VRAM** (RTX 3050 Ti). Do not suggest solutions requiring more VRAM or large batch sizes.

## Commands
- **Setup:**
  `python -m venv .venv`
  `.venv\Scripts\activate` (Windows-specific)
  `pip install -r requirements.txt`
- **Run Pipeline:** `python -m scripts.run_pipeline --input <path_to_video>`
- **Run Tests:** `pytest tests/`

## Architecture & Entrypoints
- `scripts/run_pipeline.py`: Main executable entrypoint.
- `src/`: Core business logic (audio conversion, transcription).
- `config.yaml`: Pipeline settings and model parameters.

## Critical Gotchas & Quirks
- **FFmpeg:** Must be installed and available in the system `PATH`. The pipeline will fail otherwise.
- **GigaAM-v3 Chunking:** The model cannot process long files directly. The pipeline *must* slice audio into **20-second chunks** and restore timestamps during concatenation.
- **Testing:** Tests specifically check for FFmpeg availability and audio conversion error handling.

## Notes & Gotchas
- **Secrets:** Copy `.env.example` to `.env`; it must contain `HF_TOKEN` (required at import time of `src.transcribe`) and `DEEPSEEK_API_KEY`.
- **Summarization:** `summarize.enabled: true` (provider: deepseek) is set in `config.yaml`, but the LLM summarization step is **not implemented** yet — the pipeline currently produces only the transcript.
- **Model version:** GigaAM is installed from a pinned git commit in `requirements.txt`; do not bump it casually.
- **requirements.txt encoding:** UTF-8.
- **Outputs:** Transcript → `output/<stem>_transcript.txt`; log → `output/pipeline.log`; temp chunks in `temp_chunks/` (auto-deleted after processing).
- **Tooling:** No CI, lint, typecheck, or additional test configuration exists; verification today is `pytest tests/`.
- **Windows paths:** Use `\` path separators in scripts/shell commands; be mindful of encoding issues.
