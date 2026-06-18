# AI-Surah-Segmentation — AGENTS.md

## Environment

- **Conda env**: `nemo_quran` at `D:\AI\conda-envs\nemo_quran` (Python 3.10.20).
  **Do NOT** use the system default Python (3.9.13) — it is missing `nemo` and `textgrid`.
  Activate: `conda activate nemo_quran`
- **GPU**: Not available (CUDA: False). ASR runs on CPU.
- No `requirements.txt` or `pyproject.toml`. Dependencies: `torch`, `nemo`, `librosa`, `pydub`, `pandas`, `openpyxl`, `textgrid`, `soundfile`, `tqdm`.

## Entrypoint & Execution

- `main.py` — iterates surahs 1–114 and calls `QuranPipeline.process_surah()`.
- Run: `python main.py`
- **Gotcha**: `main.py` has `try/except` commented out — any unhandled exception during a surah crashes the entire run.
- `pipeline.py` — `QuranPipeline` class orchestrates: convert mp3→wav, detect silence, chunk long audio (>40s), ASR transcribe, align verses, export segments + TextGrid.

## Inputs & Outputs

| Path | Purpose |
|---|---|
| `data/Quran_text_db.xlsx` | Verse database (columns: `Sura number`, `Aya number`, `Aya text`) |
| `data/mp3/{nnn}.mp3` | Input recitations (3-digit surah number, zero-padded) |
| `data/wav/{nnn}.wav` | Converted WAV (16kHz mono) |
| `data/output_wav/{nnn}{aya}.wav` | Per-verse WAV segments |
| `data/output_mp3/{nnn}{aya}.mp3` | Per-verse MP3 segments |
| `data/textgrid/{nnn}.TextGrid` | Praat TextGrid with verse intervals |
| `data/temp_chunks/` | **Transient** — created by chunking logic; not auto-cleaned |
| `logs/pipeline.log` | Pipeline log |

## Key Configuration (`config.py`)

- `SAMPLE_RATE = 16000`, `MAX_WINDOW_WORDS = 50`, `SIM_THRESHOLD = 0.6`, `CHUNK_TIME = 40` (seconds)

## Architecture Notes

- `asr.py`: Uses NeMo `nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0` with word-level timestamps.
- `aligner.py`: Matches ASR words to verses via `difflib.SequenceMatcher`, then snaps boundaries to detected silences.
- `aligner_gemi.py`: Older alignment variant — **dead code** (not imported in `pipeline.py`).
- `text_utils.py`: Normalizes Arabic (remove tashkeel, unify alif/ya/ta-marbuta/hamza).
- `audio_utils.py`: Silence detection (adaptive `top_db`), chunking, audio I/O.

## Common Tasks

- **Process a single surah**: Call `QuranPipeline.process_surah(N)` from a Python shell.
- **No tests exist**. No lint/typecheck config.
- **No cleanup** of `data/temp_chunks/` — remove manually between runs.
