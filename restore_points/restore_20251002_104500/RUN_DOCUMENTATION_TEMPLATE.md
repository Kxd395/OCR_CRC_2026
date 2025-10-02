# Run Documentation Template

## Overview

Every processing run should have a dedicated folder structure with complete documentation. This ensures reproducibility, traceability, and consistent quality across all runs.

## Directory Structure

```
artifacts/
└── run_YYYYMMDD_HHMMSS/
    ├── README.md                    # This template filled out
    ├── MANIFEST.json                # Auto-generated run metadata
    ├── input/                       # Input files
    │   └── survey.pdf
    ├── scripts_archive/             # Exact scripts used
    │   ├── step1_find_anchors.py
    │   ├── step2_align_and_crop.py
    │   ├── step3_extract_text.py
    │   └── common.py
    ├── step1_anchors/              # Step 1 outputs
    │   ├── anchor_log.json
    │   └── page_*.png
    ├── step2_cropped/              # Step 2 outputs
    │   └── page_*.png
    ├── step3_text/                 # Step 3 outputs
    │   ├── combined_text.txt
    │   └── page_*.txt
    ├── diagnostics/                # Validation outputs
    │   ├── grid_overlays/
    │   └── validation_report.json
    └── notes/                      # Additional documentation
        ├── ISSUES.md
        ├── CHANGES.md
        └── VALIDATION.md
```

## README.md Template

Copy this template to `artifacts/run_YYYYMMDD_HHMMSS/README.md` and fill it out:

---

```markdown
# Run YYYYMMDD_HHMMSS - [Brief Description]

## Run Information

**Date**: YYYY-MM-DD HH:MM:SS
**Operator**: [Your Name]
**Template**: crc_survey_l_anchors_v1
**Git Commit**: [commit hash]
**Branch**: [branch name]

## Input Description

**Source**: [Where did the PDF come from?]
**File**: `survey.pdf`
**Pages**: [number]
**Quality**: [Good/Fair/Poor - describe any issues]
**Special Notes**: [Any unusual characteristics]

## Processing Parameters

### Step 1: Find Anchors
- DPI: 300
- Anchor Templates: TL, TR, BL, BR
- Detection Method: Template matching with contour refinement
- Thresholds: [Any custom thresholds]

### Step 2: Align and Crop
- Crop Strategy: Outward margin 0.125 inches (37.5px)
- Expected Dimensions: 2267×2813px
- Alignment Method: Homography transformation

### Step 3: Extract Text
- OCR Engine: Tesseract [version]
- Language: eng
- PSM Mode: [page segmentation mode]
- Grid Regions: [number of regions]

## Execution Log

### Step 1: Find Anchors
**Command**: `python scripts/step1_find_anchors.py --run-dir artifacts/run_YYYYMMDD_HHMMSS`
**Start Time**: HH:MM:SS
**End Time**: HH:MM:SS
**Duration**: [seconds]
**Status**: ✅ SUCCESS / ❌ FAILED
**Notes**: [Any issues or observations]

### Step 2: Align and Crop
**Command**: `python scripts/step2_align_and_crop.py --run-dir artifacts/run_YYYYMMDD_HHMMSS`
**Start Time**: HH:MM:SS
**End Time**: HH:MM:SS
**Duration**: [seconds]
**Status**: ✅ SUCCESS / ❌ FAILED
**Notes**: [Any issues or observations]

### Step 3: Extract Text
**Command**: `python scripts/step3_extract_text.py --run-dir artifacts/run_YYYYMMDD_HHMMSS`
**Start Time**: HH:MM:SS
**End Time**: HH:MM:SS
**Duration**: [seconds]
**Status**: ✅ SUCCESS / ❌ FAILED
**Notes**: [Any issues or observations]

## Validation Results

### Anchor Detection Quality
| Page | TL | TR | BL | BR | Status |
|------|----|----|----|----|--------|
| 01   | ✅ | ✅ | ✅ | ✅ | OK     |
| 02   | ✅ | ✅ | ✅ | ✅ | OK     |
| ...  | ...| ...| ...| ...| ...    |

**Summary**:
- Total Pages: [number]
- Perfect Anchors: [number] ([percentage]%)
- Partial Anchors: [number]
- Failed Pages: [number]

### Cropping Quality
**Validation Command**: `python scripts/qa_overlay_from_results.py artifacts/run_YYYYMMDD_HHMMSS`

| Metric | Value |
|--------|-------|
| Mean Error (px) | 0.00 |
| Max Error (px) | 0.00 |
| Pages OK | 26/26 (100%) |
| Pages Warning | 0/26 (0%) |
| Pages Error | 0/26 (0%) |

### OCR Quality
**Sample Extraction Check**:
- Grid cell (0,0) expected: "Question 1" → Found: "Question 1" ✅
- Grid cell (5,10) expected: "Response" → Found: "Response" ✅
- Overall accuracy: [percentage]%

## Issues and Resolutions

### Issue 1: [Brief Description]
**Severity**: Critical / Major / Minor
**Symptoms**: [What went wrong]
**Root Cause**: [Why it happened]
**Resolution**: [How it was fixed]
**Prevention**: [How to avoid in future]

### Issue 2: [Brief Description]
...

## Changes from Standard Process

**Change 1**: [Description]
- **Reason**: [Why this change was needed]
- **Impact**: [What effect it had]
- **Files Modified**: [Which scripts were changed]

**Change 2**: [Description]
...

## Quality Assessment

### Overall Quality: ✅ Excellent / ⚠️ Good / ❌ Poor

**Strengths**:
- [What went well]
- [Positive outcomes]

**Weaknesses**:
- [What could be improved]
- [Any remaining issues]

**Recommendations**:
- [Suggestions for future runs]
- [Process improvements]

## Output Files

### Deliverables
- [ ] Cropped images: `step2_cropped/page_*.png` (26 files)
- [ ] Extracted text: `step3_text/combined_text.txt`
- [ ] Grid overlays: `diagnostics/grid_overlays/page_*.png`
- [ ] Validation report: `diagnostics/validation_report.json`

### Archive Location
**Backup**: [Location of backup copy]
**Cloud Storage**: [S3/Azure/GCP path if applicable]
**Retention**: [How long to keep]

## Reproducibility Checklist

- [ ] All scripts archived in `scripts_archive/`
- [ ] Git commit hash recorded
- [ ] Input files preserved
- [ ] Parameters documented
- [ ] Environment details recorded (Python version, package versions)
- [ ] Validation passed
- [ ] Known issues documented
- [ ] Output files verified

## Environment Details

```bash
Python: 3.13.7
OpenCV: 4.x.x
Tesseract: 5.x.x
Platform: macOS / Linux / Windows
```

**Key Dependencies**:
```
opencv-python==4.x.x
pytesseract==0.3.x
pdf2image==1.x.x
numpy==1.x.x
```

## References

**Related Runs**: [Links to similar or baseline runs]
**Documentation**: [Links to relevant docs]
**Issues**: [Links to GitHub issues]

---

**Prepared by**: [Your Name]
**Date**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
```

---

## MANIFEST.json Schema

This file is auto-generated by the pipeline:

```json
{
  "run_id": "run_20251001_181157",
  "timestamp": "2025-10-01T18:11:57Z",
  "operator": "username",
  "git_commit": "59b0802d4",
  "git_branch": "mexico-city-clean",
  "template": {
    "name": "crc_survey_l_anchors_v1",
    "version": "1.0"
  },
  "input": {
    "file": "survey.pdf",
    "pages": 26,
    "md5": "abc123..."
  },
  "parameters": {
    "step1": {
      "dpi": 300,
      "anchor_detection_threshold": 0.7
    },
    "step2": {
      "crop_margin_inches": 0.125,
      "expected_width_px": 2267,
      "expected_height_px": 2813
    },
    "step3": {
      "tesseract_psm": 6,
      "language": "eng"
    }
  },
  "execution": {
    "step1": {
      "start": "2025-10-01T18:11:57Z",
      "end": "2025-10-01T18:12:30Z",
      "duration_sec": 33,
      "status": "success"
    },
    "step2": {
      "start": "2025-10-01T18:12:30Z",
      "end": "2025-10-01T18:13:15Z",
      "duration_sec": 45,
      "status": "success"
    },
    "step3": {
      "start": "2025-10-01T18:13:15Z",
      "end": "2025-10-01T18:15:00Z",
      "duration_sec": 105,
      "status": "success"
    }
  },
  "validation": {
    "anchors": {
      "total_pages": 26,
      "perfect_anchors": 26,
      "partial_anchors": 0,
      "failed_pages": 0
    },
    "cropping": {
      "mean_error_px": 0.00,
      "max_error_px": 0.00,
      "pages_ok": 26,
      "pages_warning": 0,
      "pages_error": 0
    },
    "ocr": {
      "sample_checks": 10,
      "sample_passed": 10,
      "accuracy_pct": 100.0
    }
  },
  "outputs": {
    "step1_anchors": {
      "anchor_log": "step1_anchors/anchor_log.json",
      "anchor_images": 26
    },
    "step2_cropped": {
      "cropped_images": 26,
      "dimensions": "2267x2813"
    },
    "step3_text": {
      "combined_text": "step3_text/combined_text.txt",
      "individual_pages": 26
    }
  },
  "issues": [],
  "notes": "Baseline run with perfect anchor detection"
}
```

## ISSUES.md Template

Document problems encountered during the run:

```markdown
# Issues Log - Run YYYYMMDD_HHMMSS

## Issue #1: [Title]

**Date**: YYYY-MM-DD HH:MM
**Severity**: Critical / Major / Minor / Info
**Step**: Step 1 / Step 2 / Step 3 / Other
**Status**: Open / Resolved / Workaround / Won't Fix

### Description
[Detailed description of the issue]

### Impact
[How this affected the run]

### Root Cause
[Technical explanation of why it happened]

### Resolution
[How it was fixed, or workaround applied]

### Prevention
[How to avoid this in future runs]

### Related Files
- [List of affected files]
- [Scripts that were changed]

---

## Issue #2: [Title]
...
```

## CHANGES.md Template

Document modifications from standard process:

```markdown
# Changes Log - Run YYYYMMDD_HHMMSS

## Change #1: [Title]

**Date**: YYYY-MM-DD HH:MM
**Type**: Script Modification / Parameter Change / Process Change
**Author**: [Your Name]

### Rationale
[Why this change was necessary]

### Description
[What was changed]

### Files Modified
```diff
# scripts/step2_align_and_crop.py
- crop_region = compute_inward_inset(anchors, inset_pct=0.125)
+ crop_region = compute_outward_margin(anchors, margin_inches=0.125)
```

### Testing
[How the change was validated]

### Results
[Impact on output quality]

---

## Change #2: [Title]
...
```

## VALIDATION.md Template

Detailed validation results:

```markdown
# Validation Report - Run YYYYMMDD_HHMMSS

## Validation Date
YYYY-MM-DD HH:MM:SS

## Validation Method
**Script**: `scripts/qa_overlay_from_results.py`
**Command**: `python scripts/qa_overlay_from_results.py artifacts/run_YYYYMMDD_HHMMSS`

## Anchor Detection Validation

### Detection Summary
- Total Pages: 26
- Pages with 4/4 anchors: 26 (100%)
- Pages with 3/4 anchors: 0 (0%)
- Pages with <3 anchors: 0 (0%)

### Per-Page Details
| Page | TL | TR | BL | BR | TL Coords | TR Coords | BL Coords | BR Coords |
|------|----|----|----|----|-----------|-----------|-----------| --------- |
| 01   | ✅ | ✅ | ✅ | ✅ | (98,95) | (2182,95) | (98,2377) | (2182,2377) |
| 02   | ✅ | ✅ | ✅ | ✅ | (98,95) | (2182,95) | (98,2377) | (2182,2377) |
| ...  | ...| ...| ...| ...| ...       | ...       | ...       | ...        |

### Anchor Consistency Check
**Standard Deviation Analysis**:
- TL X: 0.5px (excellent)
- TL Y: 0.3px (excellent)
- TR X: 0.4px (excellent)
- TR Y: 0.3px (excellent)
- BL X: 0.6px (excellent)
- BL Y: 0.5px (excellent)
- BR X: 0.5px (excellent)
- BR Y: 0.4px (excellent)

**Assessment**: ✅ All anchors highly consistent across pages

## Cropping Validation

### Grid Alignment Check
**Method**: Overlay expected grid lines on cropped images

| Page | Mean Error | Max Error | Status |
|------|-----------|-----------|--------|
| 01   | 0.00px    | 0.00px    | ✅ OK  |
| 02   | 0.00px    | 0.00px    | ✅ OK  |
| ...  | ...       | ...       | ...    |

**Aggregate Statistics**:
- Mean of means: 0.00px
- Max of maxes: 0.00px
- Pages OK (error <2px): 26/26 (100%)
- Pages Warning (2-5px): 0/26 (0%)
- Pages Error (>5px): 0/26 (0%)

**Assessment**: ✅ Perfect alignment achieved

### Dimension Validation
**Expected**: 2267×2813px
**Actual**: All pages match expected dimensions
**Margin Check**: 37.5px margin verified on all sides

## OCR Validation

### Sample Extraction Checks
**Grid Cells Validated**: 10 per page × 26 pages = 260 samples

| Page | Region | Expected | Actual | Match |
|------|--------|----------|--------|-------|
| 01   | (0,0)  | "Q1"     | "Q1"   | ✅    |
| 01   | (5,10) | "Resp"   | "Resp" | ✅    |
| ...  | ...    | ...      | ...    | ...   |

**Results**:
- Exact matches: 258/260 (99.2%)
- Minor variations: 2/260 (0.8%)
- Major errors: 0/260 (0%)

**Assessment**: ✅ OCR quality excellent

## Overall Assessment

**Quality Grade**: A+ / A / B / C / D / F
**Recommendation**: Approve for use / Needs review / Reprocess required

### Strengths
- Perfect anchor detection
- Pixel-perfect alignment
- High OCR accuracy

### Issues
- None identified

### Sign-off
**Validated by**: [Your Name]
**Date**: YYYY-MM-DD
**Approved**: Yes / No / Conditional
```

## Quick Start Checklist

When starting a new run:

1. [ ] Create run directory: `artifacts/run_$(date +%Y%m%d_%H%M%S)`
2. [ ] Copy input PDF to `input/`
3. [ ] Run pipeline steps
4. [ ] Scripts auto-archive to `scripts_archive/`
5. [ ] Fill out README.md from template
6. [ ] Run validation: `qa_overlay_from_results.py`
7. [ ] Document any issues in ISSUES.md
8. [ ] Document any changes in CHANGES.md
9. [ ] Complete validation in VALIDATION.md
10. [ ] Generate MANIFEST.json (auto or manual)
11. [ ] Commit to git with descriptive message
12. [ ] Backup to cloud storage (if applicable)

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
