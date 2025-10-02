# Complete OCR Pipeline Automation

**Created**: October 2, 2025  
**File**: `run_full_pipeline.py`  
**Purpose**: Automated end-to-end OCR pipeline from PDF to Excel

---

## 🎯 Problem Solved

Previously, the pipeline had to be run manually with multiple separate commands, and it was easy to:
- Skip steps (especially the alignment/cropping steps)
- Run steps out of order
- Forget to pass the correct arguments
- Miss configuration snapshots

Now with `run_full_pipeline.py`, you run **ONE command** and get:
- All steps executed in the correct order
- Complete documentation and logs
- Environment snapshots
- Timestamped artifacts folder
- Excel report automatically generated

---

## 📋 Complete Pipeline Steps

### The Correct Order (9 Steps):

1. **PDF Ingestion** - Extract pages to PNG images
2. **Find Anchors** (Step 1) - Detect L-shaped alignment marks
3. **Align & Crop** (Step 2) - Warp and crop pages to standard size
4. **Check Alignment** - Verify homography matrices
5. **Create Overlays** - Visual checkbox boundary overlays
6. **Run OCR** - Detect filled checkboxes with threshold
7. **QA Overlays** - Visual verification of detection results
8. **Validation** - Check for errors and warnings
9. **Export to Excel** - Generate final 4-sheet report

---

## 🚀 Usage

### Basic Usage:
```bash
python3 run_full_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json
```

### With Custom Threshold:
```bash
python3 run_full_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --threshold 11.5
```

### With Custom Export Path:
```bash
python3 run_full_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --export results/my_survey_$(date +%Y%m%d).xlsx
```

### Strict Mode (Fail on Validation Errors):
```bash
python3 run_full_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --threshold 11.5 \
  --strict
```

### With Notes:
```bash
python3 run_full_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --notes "October 2025 survey batch 1"
```

---

## 📁 Output Structure

After running, you'll get a new timestamped folder in `artifacts/`:

```
artifacts/run_20251002_064920/
├── images/                    # Extracted PDF pages
│   ├── page_0001.png
│   ├── page_0002.png
│   └── ...
├── 01_step1_anchor_detection/ # Anchor detection results
│   ├── anchor_detection_log.json
│   └── visualizations/
│       └── page_*.png
├── 02_step2_alignment_and_crop/  # Aligned images
│   ├── aligned_cropped/           # Standard size (2267×2813px)
│   │   ├── page_0001_aligned_cropped.png
│   │   └── ...
│   ├── aligned_full/              # Full warped images
│   └── alignment_results.json
├── logs/                      # Pipeline logs
│   ├── homography.json        # Transformation matrices
│   └── ocr_results.json       # Detection results
├── overlays/                  # Visual overlays
│   ├── page_0001_overlay.png  # Checkbox boundaries
│   └── ...
├── qa/                        # QA overlays
│   ├── page_0001_qa.png       # Detected fills highlighted
│   └── ...
├── configs_snapshot/          # Config backups
│   ├── template.json
│   ├── ocr.yaml
│   └── checksums.txt
├── scripts_archive/           # Script snapshots
│   ├── run_ocr.py
│   ├── export_to_excel.py
│   └── ...
├── env/                       # Environment info
│   ├── python.txt             # Python version
│   ├── pip_freeze.txt         # Package versions
│   ├── os.txt                 # Operating system
│   └── tools.txt              # OpenCV, Tesseract versions
├── input/                     # Original PDF
│   └── survey.pdf
├── MANIFEST.json              # Complete run metadata
└── README.md                  # Run summary

exports/
└── run_20251002_064920.xlsx   # Final Excel report
```

---

## 📊 Excel Report (4 Sheets)

### 1. Summary Sheet
- Total pages processed
- Total checkboxes detected
- Overall statistics
- Detection rate

### 2. Detailed Results
- Page-by-page breakdown
- Checkbox ID, Row, Column
- Fill percentage
- Color-coded (green = checked)

### 3. Response Tally
- Count by question (Q1-Q5)
- Count by column (1-5)
- Distribution analysis

### 4. Raw Data
- Pivot-ready format
- All detections listed
- Easy to filter/analyze

---

## 🔧 Configuration

### Threshold Priority:
1. **CLI argument** (`--threshold 11.5`) - Highest priority
2. **Template file** (`detection_settings.fill_threshold_percent`)
3. **Config file** (`configs/ocr.yaml`)
4. **Hardcoded default** (11.5%)

### Environment:
- Automatically uses `.venv` Python if available
- Falls back to system Python if no venv
- Sets PYTHONPATH correctly for imports

---

## ✅ What Gets Captured

Every run automatically captures:

### 1. Environment Information:
- Python version (3.x.x)
- All installed packages (pip freeze)
- Operating system details
- Tool versions (OpenCV, Tesseract)

### 2. Configuration Snapshots:
- Template JSON (with SHA256 checksum)
- `ocr.yaml` config
- `models.yaml` config

### 3. Script Snapshots:
- All pipeline scripts archived
- Ensures reproducibility
- Can see exact code used

### 4. Timing Data:
- Duration of each step
- Total pipeline time
- Performance metrics

### 5. Metadata:
- Timestamp (UTC)
- Input PDF path
- Template used
- Threshold setting
- User notes

---

## 🎨 Pretty Output

The script provides colorful, easy-to-read terminal output:

```
======================================================================
CRC OCR PIPELINE - FULL AUTOMATION
======================================================================

📄 PDF: review/test_survey.pdf
📋 Template: templates/crc_survey_l_anchors_v1/template.json
🎯 Threshold: 11.5%

🐍 Using Python: /path/to/.venv/bin/python


======================================================================
STEP 1/9: Ingest PDF
======================================================================

[RUN] /path/to/.venv/bin/python scripts/ingest_pdf.py --pdf "..."
Ingested 26 pages -> artifacts/run_20251002_064920
✅ PDF ingested in 11.40s
📁 Run directory: run_20251002_064920

...

======================================================================
✅ PIPELINE COMPLETE!
======================================================================

📊 Excel Report: exports/run_20251002_064920.xlsx
📁 Run Directory: artifacts/run_20251002_064920
⏱️  Total Time: 127.45s
```

---

## 🔍 Error Handling

### Automatic Validation:
- Checks if PDF exists
- Checks if template exists
- Validates each step completion
- Reports errors clearly

### Strict Mode:
Use `--strict` to fail immediately on validation errors:
```bash
python3 run_full_pipeline.py --pdf survey.pdf --template template.json --strict
```

Without `--strict`, validation warnings are logged but pipeline continues.

---

## 📝 MANIFEST.json

Every run generates a `MANIFEST.json` with complete metadata:

```json
{
  "run_id": "run_20251002_064920",
  "timestamp": "2025-10-02T13:49:20Z",
  "pdf": "review/test_survey.pdf",
  "template": "templates/crc_survey_l_anchors_v1/template.json",
  "export": "exports/run_20251002_064920.xlsx",
  "threshold": 11.5,
  "near_margin": 0.03,
  "strict_mode": false,
  "notes": "",
  "durations_sec": {
    "1_ingest_pdf": 11.40,
    "2_find_anchors": 23.15,
    "3_align_and_crop": 31.28,
    "4_check_alignment": 2.45,
    "5_make_overlays": 18.32,
    "6_run_ocr": 28.67,
    "7_qa_overlays": 5.12,
    "8_validation": 1.23,
    "9_export_excel": 3.18
  }
}
```

---

## 🎯 Key Features

### 1. Never Skip Steps
All 9 steps run in order automatically.

### 2. Complete Audit Trail
Every file, config, and script version captured.

### 3. Reproducibility
Can recreate exact results from any run's snapshots.

### 4. Single Command
No more manual step-by-step execution.

### 5. Error Recovery
Clear error messages with exit codes.

### 6. Timestamped Artifacts
Each run in separate folder with unique timestamp.

---

## 📖 Related Documentation

- **Main Pipeline Status**: `PIPELINE_STATUS.md`
- **Checkbox Coordinates**: `docs/CHECKBOX_COORDINATES.md`
- **Detection Threshold**: `docs/DETECTION_THRESHOLD.md`
- **Checkbox ID System**: `CHECKBOX_ID_SYSTEM.md`
- **Best Practices**: `docs/BEST_PRACTICES.md`

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
Make sure you have the virtual environment activated or the script will use it automatically.

### "No run directories found"
The ingestion step failed. Check PDF path is correct.

### "Command failed with exit code X"
Check the error message above. Common issues:
- Missing dependencies
- Incorrect template path
- Corrupted PDF

### "Validation failed"
Run with `--strict` to see detailed validation errors, or check the logs in `artifacts/run_*/logs/`.

---

## 💡 Pro Tips

### 1. Use Descriptive Notes:
```bash
--notes "Q4 2024 batch 3, pages 1-26, light pencil marks"
```

### 2. Custom Output Location:
```bash
--export /path/to/shared/drive/survey_results.xlsx
```

### 3. Check Logs:
```bash
cat artifacts/run_*/logs/ocr_results.json | jq '.pages[].checkboxes[] | select(.is_filled)'
```

### 4. Compare Runs:
```bash
diff artifacts/run_A/MANIFEST.json artifacts/run_B/MANIFEST.json
```

---

## 🎉 Summary

**Before**: Manual 9-step process, easy to skip steps, no audit trail  
**After**: One command, all steps automated, complete documentation

**Command**:
```bash
python3 run_full_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --threshold 11.5
```

**Result**: Excel report in `exports/`, full audit trail in `artifacts/`

✅ **Production Ready!**
