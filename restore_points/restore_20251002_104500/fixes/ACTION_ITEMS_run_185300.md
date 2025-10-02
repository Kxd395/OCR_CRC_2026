# Action Items for run_20251001_185300

## Current Status

✅ **Completed**:
- Directory structure created (`env/`, `configs_snapshot/`, `metrics/`, `diffs/`, `notes/`)
- `notes/DATA_PROVENANCE.md` created
- `notes/RETENTION.md` created

⏳ **Remaining**:
- Snapshot configurations
- Generate metrics
- Compare with baseline run

## Immediate Next Steps

### Step 1: Snapshot Configurations (2 minutes)

```bash
cd /Users/VScode_Projects/projects/crc_ocr_dropin
python scripts/snapshot_configs.py artifacts/run_20251001_185300
```

**What this does**:
- Copies `templates/crc_survey_l_anchors_v1/template.json` and `grid.json`
- Copies `configs/ocr.yaml` and `models.yaml`
- Generates SHA256 checksums for verification
- Creates `configs_snapshot/metadata.json`

**Expected output**:
```
Snapshotting configs to: artifacts/run_20251001_185300/configs_snapshot
  ✅ Copied template.json
  ✅ Copied grid.json
  ✅ Copied ocr.yaml
  ✅ Copied models.yaml
  ✅ Wrote checksums.txt (4 files)
  ✅ Wrote metadata.json

✅ Snapshot complete (4 files)
```

---

### Step 2: Generate Metrics (5 minutes)

```bash
python scripts/generate_metrics.py artifacts/run_20251001_185300
```

**What this does**:
- Reads validation results from `diagnostics/validation_report.json`
- Generates `metrics/alignment.jsonl` (per-page alignment metrics)
- Generates `metrics/ocr.jsonl` (per-page OCR metrics)
- Generates `metrics/summaries.json` (aggregated metrics + QA gates)
- Checks QA gates and reports pass/fail

**Expected output**:
```
Generating metrics for run_20251001_185300...
✅ Wrote alignment.jsonl (26 pages)
✅ Wrote ocr.jsonl (26 pages)
✅ Wrote summaries.json

============================================================
QA GATE RESULTS
============================================================
Alignment: ✅ PASS
OCR:       ✅ PASS

Overall:   ✅ ALL PASS
============================================================
```

---

### Step 3: Compare with Baseline (3 minutes)

```bash
python scripts/compare_runs.py \
    artifacts/run_20251001_181157 \
    artifacts/run_20251001_185300
```

**What this does**:
- Compares configuration snapshots
- Compares metrics (alignment, OCR)
- Compares environment (if env/ exists in both)
- Generates diff report in `run_20251001_185300/diffs/against_run_20251001_181157/`
- Creates human-readable `DIFF_SUMMARY.md`

**Expected output**:
```
Generating diff report:
  Before: run_20251001_181157
  After:  run_20251001_185300
  ✅ config_diff.json
  ✅ metrics_delta.json
  ✅ environment_diff.json
  ✅ DIFF_SUMMARY.md

✅ Diff report generated: artifacts/run_20251001_185300/diffs/against_run_20251001_181157
   View summary: artifacts/run_20251001_185300/diffs/against_run_20251001_181157/DIFF_SUMMARY.md
```

---

## Verification Steps

### After Step 1: Verify Config Snapshot

```bash
# Check files were created
ls -la artifacts/run_20251001_185300/configs_snapshot/

# Should see:
# template_template.json
# template_grid.json
# ocr.yaml (if exists)
# models.yaml (if exists)
# metadata.json
# checksums.txt

# Verify checksums
python scripts/snapshot_configs.py artifacts/run_20251001_185300 --verify
```

---

### After Step 2: Check Metrics

```bash
# View summary
cat artifacts/run_20251001_185300/metrics/summaries.json | python -m json.tool

# Check QA gates
python -c "
import json
s = json.loads(open('artifacts/run_20251001_185300/metrics/summaries.json').read())
print(f\"Alignment: {s['alignment']['mean_error_px']:.2f}px mean, {s['alignment']['pages_ok']}/{s['total_pages']} pages OK\")
print(f\"OCR: {s['ocr']['pages_with_text']}/{s['total_pages']} pages with text\")
print(f\"Gates: {'✅ PASS' if s['overall']['all_gates_pass'] else '❌ FAIL'}\")
"
```

---

### After Step 3: View Diff Summary

```bash
# Human-readable summary
cat artifacts/run_20251001_185300/diffs/against_run_20251001_181157/DIFF_SUMMARY.md

# Or all JSON diffs
ls artifacts/run_20251001_185300/diffs/against_run_20251001_181157/
```

---

## Complete Run Structure (After All Steps)

```
artifacts/run_20251001_185300/
├── README.md                     # Manual documentation (optional)
├── MANIFEST.json                 # Auto-generated metadata (future)
├── 20251001_175110/             # Original outputs
│   ├── anchors/
│   ├── cropped/
│   └── overlays/
├── step1_anchors/               # Step 1 outputs
│   ├── anchor_log.json
│   └── page_*.png
├── step2_cropped/               # Step 2 outputs
│   └── page_*.png
├── configs_snapshot/            # ✅ NEW
│   ├── template_template.json
│   ├── template_grid.json
│   ├── metadata.json
│   └── checksums.txt
├── metrics/                     # ✅ NEW
│   ├── alignment.jsonl
│   ├── ocr.jsonl
│   └── summaries.json
├── diffs/                       # ✅ NEW
│   └── against_run_20251001_181157/
│       ├── config_diff.json
│       ├── metrics_delta.json
│       ├── environment_diff.json
│       └── DIFF_SUMMARY.md
└── notes/                       # ✅ NEW
    ├── DATA_PROVENANCE.md
    └── RETENTION.md
```

---

## Optional: Create Environment Snapshot

If you want to capture the current environment (for future reference):

```bash
# Create env directory manually
mkdir -p artifacts/run_20251001_185300/env

# Capture Python version
python --version > artifacts/run_20251001_185300/env/python.txt 2>&1

# Capture package versions
pip freeze > artifacts/run_20251001_185300/env/pip_freeze.txt

# Capture OS info
sw_vers > artifacts/run_20251001_185300/env/os.txt 2>&1

# Capture tool versions
{
    echo "=== Tesseract ==="
    tesseract --version 2>&1 || echo "Not installed"
    echo ""
    echo "=== OpenCV ==="
    python -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>&1
} > artifacts/run_20251001_185300/env/tools.txt

echo "✅ Environment snapshot created"
```

---

## Timeline

**Total time**: ~10-15 minutes

- Step 1 (Config snapshot): 2 minutes
- Step 2 (Generate metrics): 5 minutes
- Step 3 (Compare runs): 3 minutes
- Verification: 2-3 minutes
- Optional environment: 2 minutes

---

## What You'll Have After This

1. **Complete documentation** of what was used in this run
2. **Quantitative metrics** showing alignment and OCR quality
3. **QA gate results** (pass/fail) for validation
4. **Comparison** showing this run matches the baseline perfectly
5. **Audit trail** for reproducibility
6. **Template** for all future runs

---

## Future Runs: Use initialize_run.py

For all new runs going forward, simply use:

```bash
python scripts/initialize_run.py --input data/new_survey.pdf
```

This automatically creates:
- ✅ Complete directory structure
- ✅ Scripts archive
- ✅ Environment snapshot
- ✅ Config snapshots
- ✅ All documentation templates
- ✅ MANIFEST.json

Then just:
1. Run Step 1, 2, 3
2. Generate metrics
3. Compare with previous run
4. Done!

---

## Questions?

- **What if a script fails?** Check the troubleshooting guide: `docs/TROUBLESHOOTING_GUIDE.md`
- **How do I customize templates?** Edit files in `docs/RUN_DOCUMENTATION_TEMPLATE.md`
- **Where's the full guide?** See `docs/RUN_DOCUMENTATION_QUICK_REFERENCE.md`
- **Need more details?** See `docs/DOCUMENTATION_SYSTEM_SUMMARY.md`

---

**Ready to proceed?** Run the 3 commands above in sequence. Should take ~10 minutes total.
