# Complete Run Documentation Quick Reference

## Overview

This guide provides a quick reference for comprehensive run documentation covering all five critical pillars:
1. **Environment Capture** - Reproducibility
2. **Config Snapshots** - Exact inputs used  
3. **Metrics & QA Gates** - Quantitative validation
4. **Iteration Diffs** - Change tracking
5. **Provenance & Retention** - Data governance

## Quick Start: Initialize a New Run

```bash
# Create a new run with complete structure
python scripts/initialize_run.py --input data/survey.pdf

# Or specify run ID
python scripts/initialize_run.py --run-id run_20251001_185300 --input data/survey.pdf
```

This creates:
```
artifacts/run_YYYYMMDD_HHMMSS/
├── README.md                    # Run documentation
├── MANIFEST.json                # Metadata and parameters
├── input/                       # Input files
├── scripts_archive/             # Exact scripts used
├── env/                         # ✨ Environment snapshot
├── configs_snapshot/            # ✨ Config files + checksums
├── metrics/                     # ✨ Machine-readable metrics
├── diffs/                       # ✨ Comparison with previous runs
└── notes/                       # ✨ Documentation templates
    ├── ISSUES.md
    ├── CHANGES.md
    ├── VALIDATION.md
    ├── DATA_PROVENANCE.md
    └── RETENTION.md
```

## Processing Workflow

### Standard Pipeline

```bash
RUN_DIR="artifacts/run_$(date +%Y%m%d_%H%M%S)"

# Step 0: Initialize run (automated)
python scripts/initialize_run.py --input data/survey.pdf --run-id "$RUN_DIR"

# Step 1: Find anchors
python scripts/step1_find_anchors.py --run-dir "$RUN_DIR"

# Step 2: Align and crop
python scripts/step2_align_and_crop.py --run-dir "$RUN_DIR"

# Step 3: Extract text
python scripts/step3_extract_text.py --run-dir "$RUN_DIR"

# Step 4: Validate alignment
python scripts/qa_overlay_from_results.py "$RUN_DIR"

# Step 5: Generate metrics
python scripts/generate_metrics.py "$RUN_DIR"

# Step 6: Compare with previous run (optional)
PREV_RUN=$(ls -d artifacts/run_* | tail -2 | head -1)
python scripts/compare_runs.py "$PREV_RUN" "$RUN_DIR"
```

### Verify Run Completeness

```bash
# Check all required files exist
python - <<'PY'
from pathlib import Path
import sys

run_dir = Path(sys.argv[1])
required = [
    "README.md",
    "MANIFEST.json",
    "env/python.txt",
    "env/pip_freeze.txt",
    "env/hardware.json",
    "configs_snapshot/metadata.json",
    "configs_snapshot/checksums.txt",
    "notes/DATA_PROVENANCE.md",
    "notes/RETENTION.md"
]

missing = [f for f in required if not (run_dir / f).exists()]
if missing:
    print(f"❌ Missing files:\n" + "\n".join(f"  - {f}" for f in missing))
    sys.exit(1)
else:
    print("✅ All required files present")
PY "artifacts/run_20251001_185300"
```

## 1. Environment Capture

### Automatic (Included in initialize_run.py)

Environment is captured automatically when using `initialize_run.py`.

### Manual

```bash
python scripts/capture_environment.py artifacts/run_20251001_185300
```

### Files Created

- `env/python.txt` - Python version
- `env/pip_freeze.txt` - Exact package versions
- `env/os.txt` - Operating system info
- `env/tools.txt` - Tesseract, OpenCV, Poppler versions
- `env/locale.txt` - Locale settings
- `env/hardware.json` - CPU, RAM, GPU
- `env/checksums.txt` - Verification checksums

### Compare Environments

```bash
python scripts/capture_environment.py artifacts/run_A --verify
scripts/compare_environments.sh artifacts/run_A artifacts/run_B
```

## 2. Config Snapshots

### Automatic (Included in initialize_run.py)

Configs are snapshotted automatically when using `initialize_run.py`.

### Manual

```bash
python scripts/snapshot_configs.py artifacts/run_20251001_185300
```

### Files Created

- `configs_snapshot/template_template.json` - Template definition
- `configs_snapshot/template_grid.json` - Grid definition
- `configs_snapshot/ocr.yaml` - OCR configuration
- `configs_snapshot/models.yaml` - Model configuration
- `configs_snapshot/metadata.json` - Snapshot metadata
- `configs_snapshot/checksums.txt` - SHA256 checksums

### Verify Checksums

```bash
python scripts/snapshot_configs.py artifacts/run_20251001_185300 --verify
```

### Compare Configs

```bash
python scripts/snapshot_configs.py \
    artifacts/run_A \
    --compare artifacts/run_B
```

## 3. Metrics & QA Gates

### Generate Metrics

```bash
python scripts/generate_metrics.py artifacts/run_20251001_185300
```

### Files Created

- `metrics/alignment.jsonl` - Per-page alignment metrics
- `metrics/ocr.jsonl` - Per-page OCR metrics
- `metrics/summaries.json` - Aggregated metrics + gates

### Check QA Gates

```bash
# Check if all gates passed
python -c "
import json, sys
from pathlib import Path
summaries = json.loads(Path(sys.argv[1]).read_text())
if summaries['overall']['all_gates_pass']:
    print('✅ All QA gates passed')
    sys.exit(0)
else:
    print('❌ QA gates failed:', summaries['overall']['failed_gates'])
    sys.exit(1)
" "artifacts/run_20251001_185300/metrics/summaries.json"
```

### View Metrics Summary

```bash
# Pretty print summary
python -c "
import json, sys
s = json.loads(open(sys.argv[1]).read())
print(f\"Alignment: {s['alignment']['mean_error_px']:.2f}px mean, {s['alignment']['pages_ok']}/{s['total_pages']} OK\")
print(f\"OCR: {s['ocr']['pages_with_text']}/{s['total_pages']} pages with text\")
print(f\"Gates: {'✅ PASS' if s['overall']['all_gates_pass'] else '❌ FAIL'}\")
" "artifacts/run_20251001_185300/metrics/summaries.json"
```

## 4. Iteration Diffs

### Compare Two Runs

```bash
# Compare with previous run
python scripts/compare_runs.py \
    artifacts/run_20251001_181157 \
    artifacts/run_20251001_185300
```

### Files Created

- `diffs/against_run_PREV/config_diff.json` - Config changes
- `diffs/against_run_PREV/metrics_delta.json` - Metric changes
- `diffs/against_run_PREV/environment_diff.json` - Environment changes
- `diffs/against_run_PREV/DIFF_SUMMARY.md` - Human-readable summary

### View Diff Summary

```bash
cat artifacts/run_20251001_185300/diffs/against_run_20251001_181157/DIFF_SUMMARY.md
```

### Compare All Recent Runs

```bash
# Trend analysis
python - <<'PY'
import json
from pathlib import Path

print(f"{'Run ID':<25} {'Align Mean':<12} {'Align Max':<12} {'OCR Pages':<12} {'Gates':<8}")
print("-" * 75)

for run_dir in sorted(Path("artifacts").glob("run_*"))[-5:]:
    summaries_file = run_dir / "metrics" / "summaries.json"
    if summaries_file.exists():
        s = json.loads(summaries_file.read_text())
        print(f"{run_dir.name:<25} "
              f"{s['alignment']['mean_error_px']:<12.2f} "
              f"{s['alignment']['max_error_px']:<12.2f} "
              f"{s['ocr']['pages_with_text']:<12} "
              f"{'✅' if s['overall']['all_gates_pass'] else '❌':<8}")
PY
```

## 5. Provenance & Retention

### Document Data Source

Edit `notes/DATA_PROVENANCE.md`:

```markdown
## Source Information
**Supplier**: Mexico City Health Department
**Acquisition Date**: 2025-10-01
**Acquisition Method**: Email attachment
**Scan Device**: HP ScanJet Pro 3000 s4

## Data Sensitivity
**Contains PHI**: No
**Redaction Required**: No
**Compliance**: N/A
```

### Document Retention Policy

Edit `notes/RETENTION.md`:

```markdown
## Backup Information
**Primary Location**: `artifacts/run_20251001_185300`
**Backup Location**: `s3://crc-ocr-backups/2025/10/run_20251001_185300`
**Backup Date**: 2025-10-01

## Retention Schedule
**Duration**: 3 years
**Purge Date**: 2028-10-01
**Purge Method**: Secure deletion (shred + verify)
```

## Complete Run Checklist

### Before Processing

- [ ] Run initialized with `initialize_run.py`
- [ ] Input PDF copied to `input/`
- [ ] Environment captured in `env/`
- [ ] Configs snapshotted in `configs_snapshot/`
- [ ] DATA_PROVENANCE.md filled out
- [ ] RETENTION.md policy documented

### During Processing

- [ ] Step 1 completed successfully
- [ ] Step 2 completed successfully
- [ ] Step 3 completed successfully
- [ ] Any issues documented in `notes/ISSUES.md`
- [ ] Any changes documented in `notes/CHANGES.md`

### After Processing

- [ ] Validation run: `qa_overlay_from_results.py`
- [ ] Metrics generated: `generate_metrics.py`
- [ ] QA gates checked and passed
- [ ] Validation results in `notes/VALIDATION.md`
- [ ] Comparison with previous run (if applicable)
- [ ] README.md completed with final status
- [ ] MANIFEST.json updated with execution times
- [ ] Git commit with descriptive message
- [ ] Backup to cloud storage (if applicable)

## Troubleshooting

### Missing Environment Files

```bash
# Re-capture environment
python scripts/capture_environment.py artifacts/run_20251001_185300
```

### Missing Config Snapshots

```bash
# Re-snapshot configs
python scripts/snapshot_configs.py artifacts/run_20251001_185300
```

### Missing Metrics

```bash
# Generate metrics (requires completed processing)
python scripts/generate_metrics.py artifacts/run_20251001_185300
```

### Verify Run Integrity

```bash
# Check all checksums
python scripts/snapshot_configs.py artifacts/run_20251001_185300 --verify

# Check environment checksums
cd artifacts/run_20251001_185300/env
shasum -c checksums.txt
```

## Automation Script Example

Complete automated run with all documentation:

```bash
#!/bin/bash
# run_complete_pipeline.sh

set -e  # Exit on error

INPUT_PDF="$1"
if [ -z "$INPUT_PDF" ]; then
    echo "Usage: $0 <input.pdf>"
    exit 1
fi

# Initialize run
RUN_DIR=$(python scripts/initialize_run.py --input "$INPUT_PDF" | grep "Run Directory:" | awk '{print $3}')
echo "Processing run: $RUN_DIR"

# Process
python scripts/step1_find_anchors.py --run-dir "$RUN_DIR"
python scripts/step2_align_and_crop.py --run-dir "$RUN_DIR"
python scripts/step3_extract_text.py --run-dir "$RUN_DIR"

# Validate
python scripts/qa_overlay_from_results.py "$RUN_DIR"
python scripts/generate_metrics.py "$RUN_DIR"

# Compare with previous
PREV_RUN=$(ls -d artifacts/run_* | grep -v "$RUN_DIR" | tail -1)
if [ -n "$PREV_RUN" ]; then
    python scripts/compare_runs.py "$PREV_RUN" "$RUN_DIR"
fi

# Check gates
python -c "
import json, sys
s = json.loads(open('$RUN_DIR/metrics/summaries.json').read())
if not s['overall']['all_gates_pass']:
    print('❌ QA gates failed')
    sys.exit(1)
print('✅ All QA gates passed')
"

echo "✅ Complete pipeline finished successfully"
echo "   Run directory: $RUN_DIR"
```

## References

- **Full Template**: `docs/RUN_DOCUMENTATION_TEMPLATE.md`
- **Environment Capture**: `docs/RUN_ENVIRONMENT_CAPTURE.md`
- **Metrics & Gates**: `docs/RUN_METRICS_QA_GATES.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING_GUIDE.md`
- **Contributing**: `.github/CONTRIBUTING.md`

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
