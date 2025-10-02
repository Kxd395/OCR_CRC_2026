# Manual – From zero to aligned OCR with L‑anchors

1) **Create/Update Template**
   - Edit `templates/crc_survey_l_anchors_v1/template.json`:
     - Set normalized `anchors_norm` for TL, TR, BR, BL (0..1).
     - Keep / adjust `checkbox_rois_norm` or build from `grid.json` via `scripts/expand_grid.py`.

2) **Run**
```
make ingest
make align
make overlays
make ocr
python scripts/qa_overlay_from_results.py --template templates/crc_survey_l_anchors_v1/template.json
python scripts/validate_run.py --template templates/crc_survey_l_anchors_v1/template.json --fail-on-error
```

3) **Tune**
   - If orange ROI boxes miss, nudge `grid.json` origin/spacing or anchors.
   - Thresholds live in `configs/ocr.yaml`.
   - Use your post‑run EST/EDT rename step outside this repo to add a human note.
