# Usage – Commands recap
- `make setup` — venv + deps
- `make run-initial` — ingest → align → overlays
- `make ocr` — warp to template space + OCR + checkbox scoring
- `python scripts/qa_overlay_from_results.py --template ...` — green QA overlays
- `python scripts/validate_run.py --template ... --fail-on-error` — CI-style gate
- `python scripts/expand_grid.py --in grid.json --out template.json` — compact grid → explicit ROIs
