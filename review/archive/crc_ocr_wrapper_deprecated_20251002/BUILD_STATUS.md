# CRC OCR Wrapper - Status & Build Report

**Location**: `review/crc_ocr_wrapper/`  
**Date Reviewed**: October 2, 2025  
**Status**: ⚠️ **OUTDATED - SUPERSEDED BY run_pipeline.py**

---

## 🎯 Executive Summary

The wrapper in `review/crc_ocr_wrapper/` was an earlier attempt to create a unified pipeline orchestrator. It has been **SUPERSEDED** by the production `run_pipeline.py` in the project root, which is more complete, tested, and actively maintained.

**Recommendation**: ✅ **Use `run_pipeline.py` instead** - It includes all wrapper functionality plus:
- Comprehensive run documentation generation
- Excel file archival in run directories
- Updated directory structure (step0, step1, step2, etc.)
- Better error handling
- Input file hashing (SHA256)
- Complete environment capture

---

## 📦 What's in the Wrapper Directory

### Files Present
1. **`app.py`** (197 lines) - Old pipeline orchestrator
2. **`README.md`** - Documentation with ASCII architecture
3. **`config.yaml`** - Simple config file (mostly unused)
4. **`run.sh`** - Bash wrapper script
5. **`ASCII_DESIGN.txt`** - Architecture diagram

---

## ❌ Problems with Current Wrapper

### 1. Missing Critical Steps
The wrapper calls outdated scripts:

| Wrapper Script | Status | Current Equivalent |
|---------------|--------|-------------------|
| `check_alignment.py` | ⚠️ Old | `step1_find_anchors.py` + `step2_align_and_crop.py` |
| `make_overlays.py` | ✅ Still used | Same |
| `run_ocr.py` | ✅ Still used | Same |
| `qa_overlay_from_results.py` | ✅ Still used | Same |
| `validate_run.py` | ✅ Still used | Same |
| `export_to_excel.py` | ✅ Still used | Same |

**Missing Steps**:
- ❌ `step1_find_anchors.py` - Anchor detection
- ❌ `step2_align_and_crop.py` - Alignment & cropping
- ❌ `convert_alignment_for_ocr.py` - Alignment format conversion
- ❌ `create_run_documentation.py` - Automated documentation

### 2. Wrong Directory Structure
```python
# Wrapper expects:
artifacts/<run>/
  images/              # Wrong - should be step0_images
  logs/homography.json # Wrong - now step2_alignment_and_crop/alignment_results.json

# Current pipeline uses:
artifacts/<run>/
  step0_images/
  step1_anchor_detection/
  step2_alignment_and_crop/
  step3_overlays/
  step4_ocr_results/
  step5_qa_overlays/
  export/
  notes/
```

### 3. Missing Features
- ❌ No comprehensive documentation generation
- ❌ No Excel file archival in run directory
- ❌ No input file hash capture
- ❌ No status field in manifest
- ❌ No notes/ directory structure

---

## ✅ Current Production Pipeline

### Use This Instead: `run_pipeline.py`

**Location**: `/Users/VScode_Projects/projects/crc_ocr_dropin/run_pipeline.py`

**Usage**:
```bash
python3 run_pipeline.py \
  --pdf artifacts/run_20251002_081927/input/survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --threshold 11.5 \
  --notes "Production run with comprehensive documentation"
```

**Features**:
- ✅ Complete 6-step pipeline (ingest → anchors → align → overlays → OCR → QA → export)
- ✅ Automatic comprehensive documentation generation
- ✅ Excel file copied to run directory
- ✅ Input file SHA256 hash
- ✅ Status tracking ("complete")
- ✅ Environment capture (Python version, packages, OS)
- ✅ Script version archival
- ✅ Config snapshot with checksums
- ✅ Duration tracking for each step

**Output Structure**:
```
artifacts/run_20251002_103645/
├── INDEX.md                        # Main documentation
├── notes/                          # Comprehensive docs
│   ├── DATA_PROVENANCE.md
│   ├── RETENTION.md
│   ├── RUN_SUMMARY.md
│   └── CONFIGURATION.md
├── export/
│   └── run_20251002_103645.xlsx   # Excel file
├── input/
│   └── survey.pdf
├── step0_images/                   # PNG conversions
├── step1_anchor_detection/         # Anchor results
├── step2_alignment_and_crop/       # Aligned images
├── step3_overlays/                 # Template overlays
├── step4_ocr_results/              # Checkbox detection
├── step5_qa_overlays/              # Visual verification
├── configs_snapshot/
├── scripts_archive/
├── env/
├── logs/
├── MANIFEST.json
└── README.md
```

---

## 📊 Feature Comparison

| Feature | Wrapper (Old) | run_pipeline.py (Current) | Winner |
|---------|--------------|---------------------------|--------|
| Steps | 6 | 8 (includes anchor detection & alignment) | ✅ Current |
| Documentation | Basic README | INDEX.md + 4 notes/ files | ✅ Current |
| Excel Archival | No | Yes (copied to run/) | ✅ Current |
| Input Hash | No | Yes (SHA256) | ✅ Current |
| Status Field | No | Yes | ✅ Current |
| Directory Structure | Old | New (step0-5) | ✅ Current |
| Error Handling | Basic | Enhanced | ✅ Current |
| Tested | No | Yes (run_20251002_103645) | ✅ Current |
| Maintained | No | Yes | ✅ Current |

---

## 🔧 Options for Wrapper Directory

### Option 1: Archive It (RECOMMENDED)
```bash
# Move to archive directory
mkdir -p review/archive
mv review/crc_ocr_wrapper review/archive/crc_ocr_wrapper_deprecated_20251002
echo "Deprecated - Use run_pipeline.py instead" > review/archive/README.md
```

### Option 2: Update It to Match Current Pipeline
**Effort**: 4-6 hours  
**Value**: Low (duplicates run_pipeline.py)  
**Recommendation**: ❌ Not worth it

Changes needed:
1. Add `step1_find_anchors.py` call
2. Add `step2_align_and_crop.py` call
3. Add `convert_alignment_for_ocr.py` call
4. Update directory paths (step0, step1, etc.)
5. Add `create_run_documentation.py` call
6. Add Excel copy to run directory
7. Add input hash calculation
8. Add status field to manifest
9. Update README and documentation

### Option 3: Delete It
**Risk**: Lose historical reference  
**Recommendation**: ⚠️ Archive instead

### Option 4: Convert to Utility Tool
Keep as a **simplified single-command launcher** that just calls `run_pipeline.py`:

```python
#!/usr/bin/env python3
# Simple wrapper that calls the production pipeline
import sys, subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
cmd = [sys.executable, str(REPO / "run_pipeline.py")] + sys.argv[1:]
subprocess.run(cmd)
```

---

## 📝 Migration Guide

### From Wrapper to run_pipeline.py

**Old Command**:
```bash
python3 review/crc_ocr_wrapper/app.py \
  --pdf data/survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --export exports/output.xlsx \
  --notes "My notes" \
  --strict \
  --threshold 11.5
```

**New Command** (same functionality):
```bash
python3 run_pipeline.py \
  --pdf data/survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --export exports/output.xlsx \
  --notes "My notes" \
  --strict \
  --threshold 11.5
```

**Benefits of Switch**:
- ✅ More complete pipeline (8 steps vs 6)
- ✅ Comprehensive documentation auto-generated
- ✅ Excel file archived in run directory
- ✅ Better error handling
- ✅ Tested and verified
- ✅ Actively maintained

---

## 🎯 Build Status Assessment

### Current State: ⚠️ OUTDATED

**What Works**:
- ✅ Basic structure is sound
- ✅ Argument parsing is good
- ✅ Environment capture works
- ✅ Script/config snapshotting works

**What Doesn't Work**:
- ❌ Missing critical pipeline steps (anchor detection, alignment)
- ❌ Wrong directory structure
- ❌ No documentation generation
- ❌ No Excel archival
- ❌ Not tested with current data

**Can It Run?**: ❌ NO - Will fail on missing scripts and wrong paths

**Should It Run?**: ❌ NO - Use `run_pipeline.py` instead

---

## ✅ Recommended Actions

### Immediate (Today)
1. ✅ **Document status** (this file)
2. ✅ **Update review_tools scripts** (already documented in REVIEW_TOOLS_STATUS.md)
3. ✅ **Create archive plan** for outdated wrapper

### Short Term (This Week)
1. 📋 Move wrapper to `review/archive/crc_ocr_wrapper_deprecated_20251002/`
2. 📋 Add deprecation notice to wrapper README
3. 📋 Update any documentation that references the wrapper

### Long Term (Optional)
1. 📋 Create a simple launcher script that calls run_pipeline.py
2. 📋 Update run.sh to point to run_pipeline.py
3. 📋 Archive or delete old wrapper code

---

## 📖 Documentation Updates Needed

### Files to Update
1. **This file**: `review/crc_ocr_wrapper/BUILD_STATUS.md` ✅ (this document)
2. **Wrapper README**: Add deprecation notice
3. **Main README**: Remove wrapper references (if any)
4. **docs/USAGE.md**: Confirm it references run_pipeline.py only

---

## 🔍 Conclusion

**Build Status**: ⚠️ **OUTDATED - DO NOT USE**

**Why It Exists**: Historical artifact from earlier development phase

**What to Do**: ✅ **Use `run_pipeline.py` instead**

The wrapper was a good proof of concept but has been superseded by a more complete, tested, and maintained production pipeline. The production `run_pipeline.py` includes all the wrapper's functionality plus additional features, better structure, and comprehensive documentation.

**No fixes needed** - Just use the current production pipeline.

---

**Assessment Date**: October 2, 2025  
**Assessed By**: GitHub Copilot  
**Status**: ⚠️ DEPRECATED  
**Replacement**: `run_pipeline.py` (production-ready, fully tested)
