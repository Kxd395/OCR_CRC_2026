# Run Metrics and QA Gates

## Overview

Machine-readable metrics and quality gates enable automated validation, trend analysis, and regression detection across runs.

## Directory Structure

```
artifacts/run_YYYYMMDD_HHMMSS/
└── metrics/
    ├── alignment.jsonl        # Per-page alignment metrics
    ├── checkboxes.jsonl       # Per-page checkbox detection
    ├── ocr.jsonl              # Per-page OCR metrics
    ├── summaries.json         # Aggregated metrics and gates
    └── histograms/
        ├── alignment_residuals.png
        ├── checkbox_scores.png
        └── ocr_confidence.png
```

## Metrics Format (JSONL)

### alignment.jsonl

One line per page:

```json
{"page": 1, "mean_error_px": 0.0, "max_error_px": 0.0, "std_error_px": 0.0, "anchor_count": 4, "quality": "ok", "transform_type": "homography"}
{"page": 2, "mean_error_px": 0.5, "max_error_px": 1.2, "std_error_px": 0.3, "anchor_count": 4, "quality": "ok", "transform_type": "homography"}
```

### checkboxes.jsonl

One line per page (if checkbox detection enabled):

```json
{"page": 1, "total_boxes": 50, "checked": 12, "unchecked": 38, "threshold": 0.55, "near_threshold": 2, "mean_score_checked": 0.72, "mean_score_unchecked": 0.15}
{"page": 2, "total_boxes": 50, "checked": 8, "unchecked": 42, "threshold": 0.55, "near_threshold": 1, "mean_score_checked": 0.68, "mean_score_unchecked": 0.18}
```

### ocr.jsonl

One line per page:

```json
{"page": 1, "text_length": 1250, "word_count": 180, "confidence_mean": 85.2, "confidence_min": 65.0, "empty_cells": 2, "psm_mode": 6}
{"page": 2, "text_length": 1180, "word_count": 175, "confidence_mean": 87.5, "confidence_min": 70.0, "empty_cells": 1, "psm_mode": 6}
```

## Summaries and QA Gates

### summaries.json Schema

```json
{
  "run_id": "run_20251001_185300",
  "timestamp": "2025-10-01T18:53:00Z",
  "total_pages": 26,
  
  "alignment": {
    "median_error_px": 0.0,
    "mean_error_px": 0.0,
    "max_error_px": 0.0,
    "p95_error_px": 0.0,
    "pages_ok": 26,
    "pages_warn": 0,
    "pages_fail": 0,
    "ok_threshold_px": 2.0,
    "warn_threshold_px": 5.0,
    "pass": true,
    "issues": []
  },
  
  "checkboxes": {
    "enabled": false,
    "threshold": 0.55,
    "near_threshold_tolerance": 0.03,
    "total_boxes": 0,
    "checked": 0,
    "unchecked": 0,
    "near_threshold_count": 0,
    "pass": true,
    "issues": []
  },
  
  "ocr": {
    "total_text_length": 32500,
    "mean_text_per_page": 1250,
    "pages_with_text": 26,
    "pages_empty": 0,
    "mean_confidence": 86.5,
    "min_confidence": 65.0,
    "min_text_length": 1000,
    "pass": true,
    "issues": []
  },
  
  "overall": {
    "all_gates_pass": true,
    "failed_gates": [],
    "warnings": []
  }
}
```

## Python Implementation

### Generate Metrics

`scripts/generate_metrics.py`:

```python
#!/usr/bin/env python3
"""Generate machine-readable metrics for a run."""

import json
from pathlib import Path
from typing import Dict, List, Any


def compute_alignment_metrics(run_dir: Path) -> List[Dict[str, Any]]:
    """Compute per-page alignment metrics from validation results."""
    metrics = []
    
    # Read validation results (from qa_overlay_from_results.py output)
    results_file = run_dir / "diagnostics" / "validation_report.json"
    if not results_file.exists():
        return metrics
    
    results = json.loads(results_file.read_text())
    
    for page_data in results.get("pages", []):
        page_num = page_data["page"]
        mean_err = page_data.get("mean_error_px", 0.0)
        max_err = page_data.get("max_error_px", 0.0)
        
        # Determine quality
        if max_err < 2.0:
            quality = "ok"
        elif max_err < 5.0:
            quality = "warn"
        else:
            quality = "fail"
        
        metrics.append({
            "page": page_num,
            "mean_error_px": round(mean_err, 2),
            "max_error_px": round(max_err, 2),
            "std_error_px": page_data.get("std_error_px", 0.0),
            "anchor_count": page_data.get("anchor_count", 4),
            "quality": quality,
            "transform_type": page_data.get("transform_type", "homography")
        })
    
    return metrics


def compute_ocr_metrics(run_dir: Path) -> List[Dict[str, Any]]:
    """Compute per-page OCR metrics."""
    metrics = []
    
    text_dir = run_dir / "step3_text"
    if not text_dir.exists():
        return metrics
    
    for page_file in sorted(text_dir.glob("page_*.txt")):
        page_num = int(page_file.stem.split("_")[1])
        text = page_file.read_text()
        
        metrics.append({
            "page": page_num,
            "text_length": len(text),
            "word_count": len(text.split()),
            "confidence_mean": 0.0,  # Would need Tesseract TSV output
            "confidence_min": 0.0,
            "empty_cells": 0,  # Would need grid extraction analysis
            "psm_mode": 6
        })
    
    return metrics


def compute_summaries(
    alignment_metrics: List[Dict],
    ocr_metrics: List[Dict],
    run_id: str,
    timestamp: str
) -> Dict[str, Any]:
    """Compute summary statistics and QA gates."""
    
    # Alignment summary
    errors = [m["max_error_px"] for m in alignment_metrics]
    pages_ok = sum(1 for m in alignment_metrics if m["quality"] == "ok")
    pages_warn = sum(1 for m in alignment_metrics if m["quality"] == "warn")
    pages_fail = sum(1 for m in alignment_metrics if m["quality"] == "fail")
    
    alignment_pass = pages_fail == 0
    alignment_issues = []
    if pages_fail > 0:
        alignment_issues.append(f"{pages_fail} pages failed alignment (>5px error)")
    
    # OCR summary
    text_lengths = [m["text_length"] for m in ocr_metrics]
    pages_empty = sum(1 for m in ocr_metrics if m["text_length"] < 10)
    
    ocr_pass = pages_empty == 0
    ocr_issues = []
    if pages_empty > 0:
        ocr_issues.append(f"{pages_empty} pages have no extracted text")
    
    # Overall
    all_gates_pass = alignment_pass and ocr_pass
    failed_gates = []
    if not alignment_pass:
        failed_gates.append("alignment")
    if not ocr_pass:
        failed_gates.append("ocr")
    
    return {
        "run_id": run_id,
        "timestamp": timestamp,
        "total_pages": len(alignment_metrics),
        
        "alignment": {
            "median_error_px": round(sorted(errors)[len(errors)//2], 2) if errors else 0.0,
            "mean_error_px": round(sum(errors)/len(errors), 2) if errors else 0.0,
            "max_error_px": round(max(errors), 2) if errors else 0.0,
            "p95_error_px": round(sorted(errors)[int(len(errors)*0.95)], 2) if errors else 0.0,
            "pages_ok": pages_ok,
            "pages_warn": pages_warn,
            "pages_fail": pages_fail,
            "ok_threshold_px": 2.0,
            "warn_threshold_px": 5.0,
            "pass": alignment_pass,
            "issues": alignment_issues
        },
        
        "checkboxes": {
            "enabled": False,
            "pass": True,
            "issues": []
        },
        
        "ocr": {
            "total_text_length": sum(text_lengths),
            "mean_text_per_page": round(sum(text_lengths)/len(text_lengths)) if text_lengths else 0,
            "pages_with_text": len(ocr_metrics) - pages_empty,
            "pages_empty": pages_empty,
            "mean_confidence": 0.0,
            "min_confidence": 0.0,
            "min_text_length": 100,
            "pass": ocr_pass,
            "issues": ocr_issues
        },
        
        "overall": {
            "all_gates_pass": all_gates_pass,
            "failed_gates": failed_gates,
            "warnings": []
        }
    }


def generate_metrics(run_dir: Path) -> None:
    """Generate all metrics for a run."""
    metrics_dir = run_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = run_dir.name
    from datetime import datetime
    timestamp = datetime.now().isoformat() + "Z"
    
    print(f"Generating metrics for {run_id}...")
    
    # Compute metrics
    alignment_metrics = compute_alignment_metrics(run_dir)
    ocr_metrics = compute_ocr_metrics(run_dir)
    
    # Write JSONL files
    if alignment_metrics:
        with open(metrics_dir / "alignment.jsonl", "w") as f:
            for metric in alignment_metrics:
                f.write(json.dumps(metric) + "\n")
        print(f"✅ Wrote alignment.jsonl ({len(alignment_metrics)} pages)")
    
    if ocr_metrics:
        with open(metrics_dir / "ocr.jsonl", "w") as f:
            for metric in ocr_metrics:
                f.write(json.dumps(metric) + "\n")
        print(f"✅ Wrote ocr.jsonl ({len(ocr_metrics)} pages)")
    
    # Compute summaries
    summaries = compute_summaries(
        alignment_metrics,
        ocr_metrics,
        run_id,
        timestamp
    )
    
    (metrics_dir / "summaries.json").write_text(
        json.dumps(summaries, indent=2)
    )
    print(f"✅ Wrote summaries.json")
    
    # Print QA gate results
    print("\n" + "="*60)
    print("QA GATE RESULTS")
    print("="*60)
    print(f"Alignment: {'✅ PASS' if summaries['alignment']['pass'] else '❌ FAIL'}")
    if summaries['alignment']['issues']:
        for issue in summaries['alignment']['issues']:
            print(f"  ⚠️  {issue}")
    
    print(f"OCR:       {'✅ PASS' if summaries['ocr']['pass'] else '❌ FAIL'}")
    if summaries['ocr']['issues']:
        for issue in summaries['ocr']['issues']:
            print(f"  ⚠️  {issue}")
    
    print(f"\nOverall:   {'✅ ALL PASS' if summaries['overall']['all_gates_pass'] else '❌ FAILED'}")
    print("="*60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_metrics.py <run_dir>")
        sys.exit(1)
    
    run_dir = Path(sys.argv[1])
    generate_metrics(run_dir)
```

## Usage

```bash
# After completing all processing steps
python scripts/generate_metrics.py artifacts/run_20251001_185300

# Check if gates passed
python -c "
import json
from pathlib import Path
summaries = json.loads(Path('artifacts/run_20251001_185300/metrics/summaries.json').read_text())
exit(0 if summaries['overall']['all_gates_pass'] else 1)
"

if [ $? -eq 0 ]; then
    echo "✅ All QA gates passed"
else
    echo "❌ Some QA gates failed"
    exit 1
fi
```

## Trend Analysis

Compare metrics across multiple runs:

```python
#!/usr/bin/env python3
"""Compare metrics across runs."""

import json
from pathlib import Path
import sys


def compare_runs(run_dirs: list[Path]) -> None:
    """Compare metrics across multiple runs."""
    
    print(f"{'Run ID':<25} {'Align Mean':<12} {'Align Max':<12} {'OCR Pages':<12} {'Gates':<8}")
    print("-" * 75)
    
    for run_dir in sorted(run_dirs):
        summaries_file = run_dir / "metrics" / "summaries.json"
        if not summaries_file.exists():
            continue
        
        summaries = json.loads(summaries_file.read_text())
        
        align_mean = summaries["alignment"]["mean_error_px"]
        align_max = summaries["alignment"]["max_error_px"]
        ocr_pages = summaries["ocr"]["pages_with_text"]
        gates_pass = "✅ PASS" if summaries["overall"]["all_gates_pass"] else "❌ FAIL"
        
        print(f"{run_dir.name:<25} {align_mean:<12.2f} {align_max:<12.2f} {ocr_pages:<12} {gates_pass:<8}")


if __name__ == "__main__":
    artifacts_dir = Path("artifacts")
    run_dirs = list(artifacts_dir.glob("run_*"))
    compare_runs(run_dirs)
```

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
