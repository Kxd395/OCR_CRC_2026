# CRC OCR Wrapper

⚠️ **DEPRECATED** - This wrapper is outdated. Use `run_pipeline.py` in the project root instead.

See `BUILD_STATUS.md` for details and migration guide.

---

## Original Documentation (Historical Reference)

One command to run the full pipeline: ingest → align → overlays → OCR → QA → Excel.

**Date:** 2025-10-02  
**Status:** Deprecated (superseded by run_pipeline.py)

## Quick start
```bash
# Run from repo root (that contains scripts/, configs/, templates/)
python3 wrapper/app.py \  --pdf data/review/training_data/scans.pdf \  --template templates/crc_survey_l_anchors_v1/template.json \  --export exports/surveys_latest.xlsx
```

- `--notes` adds a human note to the run manifest
- `--strict` makes alignment failures stop the run (non‑zero exit code)

## ASCII Design

======================  CRC OCR WRAPPER – ARCHITECTURE  ======================

                       +------------------------------+
Input PDF  ───────────▶|  CLI Wrapper (app.py)        |
                       |  - arg parsing               |
                       |  - run folder creation       |
                       |  - logging & error handling  |
                       +---------------┬--------------+
                                       │
                                       ▼
      +--------------------------- Pipeline Orchestration --------------------+
      |                                                                      |
      |  Step 0  ingest_pdf.py  → artifacts/<run>/images/                    |
      |  Step 1  check_alignment.py → logs/homography.json                   |
      |  Step 2  make_overlays.py   → overlays/*_overlay.png                 |
      |  Step 3  run_ocr.py        → logs/ocr_results.json                   |
      |  Step 4  qa_overlay_from_results.py → *_overlay_checked.png          |
      |  Step 5  validate_run.py    (gate: ok/warn/fail)                     |
      |  Step 6  export_to_excel.py → exports/<run>.xlsx                     |
      |                                                                      |
      +----------------------------------------------------------------------+
                                       │
                                       ▼
                       +------------------------------+
                       |  Run Normalizer              |
                       |  - scripts snapshot          |
                       |  - config/template snapshot  |
                       |  - env capture               |
                       |  - manifest.json             |
                       +------------------------------+

Contract (repo root expected)
-----------------------------
repo/
  scripts/*.py
  configs/*.yaml
  templates/<template>/template.json
  artifacts/
  exports/

Wrapper writes under artifacts/<run>/ :
  input/survey.pdf
  scripts_archive/*
  configs_snapshot/{template.json, ocr.yaml, models.yaml}
  env/{python.txt, pip_freeze.txt, os.txt, tools.txt}
  MANIFEST.json
  README.md (auto-filled)

=============================================================================

