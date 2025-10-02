
# CRC OCR — Human Review Tools

## What these do
1) `build_review_queue.py` — reads a run's JSON logs and writes a triage queue
   (`review/review_queue.csv` + `.xlsx`) with issues: conflicts, missing, near-threshold,
   high residuals.
2) `montage_from_run.py` — creates review montages per page showing the five checkbox
   crops per question with the chosen answer highlighted.
3) `threshold_sweep.py` — for near-threshold boxes, generates small panels showing
   multiple binarization thresholds to help decide if it should be checked.

## Quick start
```bash
python3 scripts/review/build_review_queue.py --run-dir artifacts/run_YYYYMMDD_HHMMSS
python3 scripts/review/montage_from_run.py --run-dir artifacts/run_YYYYMMDD_HHMMSS --template templates/crc_survey_l_anchors_v1/template.json
python3 scripts/review/threshold_sweep.py --run-dir artifacts/run_YYYYMMDD_HHMMSS --limit 50
```
