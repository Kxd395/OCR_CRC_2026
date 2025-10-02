# CRC OCR Drop‑in (Homography + Checkbox + ML Detection + Gemma Routing)

**What this is**
- A production-ready forms OCR system with per‑page **homography** alignment from **anchors (L‑marks)**,
  **machine learning checkbox detection (98.62% accuracy)**, visual overlays, CI validation, and optional
  **Gemma 4B/12B/27B multimodal** routing for VQA/structure repair.

**🎯 Performance: 98.62% Accuracy (Premium Tier OMR)**
- Machine Learning: Edge detection + 7 feature engineering (Canny, Harris, morphology)
- Error Rate: Only 9 errors in 650 checkboxes (62.5% reduction from baseline)
- False Negatives: 3 (82% reduction - only 3 faint marks missed)
- Industry Tier: Premium (approaching Scantron/DRC 99%+ tier)
- See `docs/ML_IMPLEMENTATION.md` and `docs/OPTIMIZATION_SUMMARY.md` for details

**Quick start - Automated Pipeline (macOS, Apple Silicon OK)**
```bash
make setup

# Automated full pipeline (✅ Correct step order: ingest→anchors→alignment→OCR→export)
python3 run_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --threshold 11.5 \
  --notes "Production run"
```

**Pipeline Status: ✅ FULLY OPERATIONAL (Oct 2, 2025)**
- ✅ Anchor Detection: 100% success rate (104/104 anchors on 26-page survey)
- ✅ Checkbox Detection: FIXED - Direct extraction from cropped images
- ✅ Overlay Alignment: FIXED - All steps use consistent coordinates
- ✅ Detection Results: 128 marked checkboxes detected successfully
- ✅ Coordinates: Verified X=[280,690,1100,1505,1915], Y=[1290,1585,1875,2150,2440]
- See `CHECKBOX_FIX_2025-01.md` for complete fix documentation

**Manual step-by-step (for debugging)**
```bash
make setup
# put your PDF at data/review/training_data/scans.pdf
make run-initial            # ingest → align → overlays
make ocr                    # warp to template space, OCR + checkbox
python scripts/qa_overlay_from_results.py --template templates/crc_survey_l_anchors_v1/template.json
python scripts/validate_run.py --template templates/crc_survey_l_anchors_v1/template.json --fail-on-error
```

**Documentation**
- **Usage Guide:** See `docs/USAGE.md` for detailed instructions
- **ML Implementation:** See `docs/ML_IMPLEMENTATION.md` for machine learning details
- **Optimization Journey:** See `docs/OPTIMIZATION_SUMMARY.md` for 83.85% → 98.62% improvement
- **Testing Practices:** See `docs/TESTING.md` for QA procedures and validation
- **Current Status:** See `docs/PIPELINE_STATUS.md` for operational status
- **Best Practices:** See `docs/BEST_PRACTICES.md` for tips and troubleshooting
- **Complete Docs:** See `docs/README.md` for full documentation index
- **Latest Fix:** See `docs/fixes/CHECKBOX_FIX_2025-01.md` for October 2, 2025 improvements

**Optional Gemma (multimodal)**
- Gemma **4B/12B/27B** variants accept **image+text**; use `scripts/gemma_router.py` to call your endpoint.
- Configure `configs/models.yaml` and export `GEMMA_*` env vars. See `docs/GEMMA_SETUP.md`.

© 2025-10-02
