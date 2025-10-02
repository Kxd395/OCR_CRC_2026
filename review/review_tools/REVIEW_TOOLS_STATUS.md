# Review Tools - Status & Update Plan

**Location**: `review/review_tools/`  
**Date Reviewed**: October 2, 2025  
**Status**: ⚠️ **OUTDATED - NEEDS UPDATES**

---

## 📦 What's In This Directory

### 1. `build_review_queue.py` (84 lines)
**Purpose**: Creates a triage queue for human review
- Identifies conflicts (multiple checkboxes checked per question)
- Identifies missing answers (no checkboxes checked)
- Flags near-threshold boxes (ambiguous fill percentages)
- Flags high alignment residuals

**Outputs**: 
- `review/review_queue.csv`
- `review/review_queue.xlsx` (with raw checkbox data)

### 2. `montage_from_run.py` (80 lines)
**Purpose**: Creates visual montages for manual review
- Generates a 5×5 grid showing all checkbox crops per page
- Rows = Questions (Q1-Q5)
- Columns = Answer options (1-5)

**Outputs**: `review/montage/<page>_montage.png`

### 3. `threshold_sweep.py` (68 lines)
**Purpose**: Helps decide on ambiguous checkboxes
- For near-threshold boxes, shows multiple binarization thresholds
- Displays 9 different threshold values (0.35-0.75)
- Helps human reviewers determine if a box should be marked

**Outputs**: `review/threshold_sweeps/<page>_<checkbox_id>_sweep.png`

### 4. `README.md`
**Purpose**: Quick start guide for using the tools

---

## ⚠️ Issues Found

### All Scripts Have Directory Structure Problems

#### Old Paths → New Paths
| Old Path | New Path | Status |
|----------|----------|--------|
| `logs/ocr_results.json` | `step4_ocr_results/results.json` | ❌ Wrong |
| `logs/homography.json` | Still exists, but format changed | ⚠️ Partial |
| `02_step2_alignment_and_crop/` | `step2_alignment_and_crop/` | ❌ Wrong |
| `images/` | `step0_images/` | ❌ Wrong |

#### Data Format Changes
- **Alignment Results**: Changed from dict-based to list-based structure
  - Old: `homography["pages"][page_name]` (dict)
  - New: `alignment["pages"][i]` (list with page numbers)
- **Field Names**: `residual_px` → `mean_error_px`, `max_error_px`

---

## 🔧 Required Updates

### 1. `build_review_queue.py` Updates

```python
# OLD CODE (Lines 22-23):
ocr  = load_json(logs/"ocr_results.json")
hom  = load_json(logs/"homography.json")

# NEW CODE NEEDED:
ocr_file = run/"step4_ocr_results"/"results.json"
align_file = run/"step2_alignment_and_crop"/"alignment_results.json"
ocr = load_json(ocr_file)
align = load_json(align_file)

# OLD CODE (Lines 46-49):
if "pages" in hom and page in hom["pages"]:
    res = hom["pages"][page].get("residual_px")
    qual = hom["pages"][page].get("quality")

# NEW CODE NEEDED:
# Find page in list structure
page_rec = next((p for p in align["pages"] if p["page"] == int(page.split("_")[1].replace(".png",""))), None)
if page_rec:
    res = page_rec.get("mean_error_px")
    qual = page_rec.get("status", "").lower()
```

### 2. `montage_from_run.py` Updates

```python
# OLD CODE (Line 33):
aligned_dir = run/"02_step2_alignment_and_crop"/"aligned_full"
src_dir = run/"images"

# NEW CODE NEEDED:
aligned_dir = run/"step2_alignment_and_crop"/"aligned_full"
src_dir = run/"step0_images"

# OLD CODE (Line 43):
H = np.array(M_by_page[page_name]["M"], dtype=np.float32)

# NEW CODE NEEDED:
# Load alignment results differently
align = load_json(run/"step2_alignment_and_crop"/"alignment_results.json")
# Find page and extract homography matrix
```

### 3. `threshold_sweep.py` Updates

```python
# OLD CODE (Lines 23-25):
pages = load_json(run/"logs/ocr_results.json")
Hpages = load_json(run/"logs/homography.json")["pages"]
src_dir = run/"images"

# NEW CODE NEEDED:
ocr_file = run/"step4_ocr_results"/"results.json"
align_file = run/"step2_alignment_and_crop"/"alignment_results.json"
pages = load_json(ocr_file)
align = load_json(align_file)
src_dir = run/"step0_images"
```

---

## 🎯 Compatibility Issues

### Template Structure
All scripts assume old template structure with `checkbox_rois_norm` list.

**Current template has**:
- `checkboxes` (list of 25 items)
- Each with `id`, `x`, `y`, `w`, `h` (normalized coordinates)

**Scripts expect**:
- `checkbox_rois_norm` (flat list indexed 0-24)

This might still work if field names match.

### Threshold Configuration
Scripts hardcode threshold as `0.55` but current pipeline uses `11.5` (percentage).

Need to normalize:
- Script uses: `0.55` (0-1 scale)
- Pipeline uses: `11.5` (0-100 scale)
- Conversion: `threshold / 100.0`

---

## ✅ Recommended Action Plan

### Priority 1: Fix Critical Path Issues
1. Update all `logs/` paths to new structure
2. Update `images/` to `step0_images/`
3. Update `02_step2_alignment_and_crop/` to `step2_alignment_and_crop/`

### Priority 2: Fix Data Format Issues
1. Update alignment results access (dict → list)
2. Update field names (`residual_px` → `mean_error_px`)
3. Update status field (`quality` → `status`)

### Priority 3: Threshold Normalization
1. Read threshold from configs or args consistently
2. Normalize to 0-1 scale for comparisons
3. Document expected format

### Priority 4: Testing
1. Test with `run_20251002_103645` (known good run)
2. Verify all outputs generate correctly
3. Check montages and sweep images look correct

---

## 💡 Enhancement Opportunities

### Additional Features to Consider
1. **Color-coded montages** - Highlight checked boxes in green
2. **Confidence scores** - Show fill percentage on montage
3. **Batch export** - Generate review package for multiple runs
4. **HTML report** - Interactive review interface
5. **Integration with pipeline** - Auto-generate review materials

### Modernization
1. Use `pathlib.Path` consistently
2. Add type hints
3. Add comprehensive docstrings
4. Create tests
5. Add CLI help text

---

## 📝 Testing Checklist

After updates, verify:
- [ ] `build_review_queue.py` runs without errors
- [ ] Review queue CSV/Excel generated correctly
- [ ] Correct number of flagged issues
- [ ] `montage_from_run.py` generates 5×5 grids
- [ ] Montages show all 25 checkboxes per page
- [ ] `threshold_sweep.py` generates threshold panels
- [ ] Sweep images show 9 different thresholds
- [ ] All outputs in correct directories

---

## 🚀 Quick Fix Script

To quickly update paths in all three files:

```bash
cd review/review_tools

# Backup originals
cp build_review_queue.py build_review_queue.py.backup
cp montage_from_run.py montage_from_run.py.backup
cp threshold_sweep.py threshold_sweep.py.backup

# Apply path fixes (do manually or with careful sed)
# Then test with:
python3 build_review_queue.py --run-dir ../../artifacts/run_20251002_103645
```

---

## 📖 Usage Examples (After Fixes)

```bash
# Generate review queue
python3 review/review_tools/build_review_queue.py \
  --run-dir artifacts/run_20251002_103645 \
  --threshold 11.5 \
  --near 3.0

# Create visual montages
python3 review/review_tools/montage_from_run.py \
  --run-dir artifacts/run_20251002_103645 \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --limit 26

# Generate threshold sweeps for ambiguous boxes
python3 review/review_tools/threshold_sweep.py \
  --run-dir artifacts/run_20251002_103645 \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --limit 50
```

---

**Status**: ⚠️ **REQUIRES UPDATES BEFORE USE**  
**Estimated Fix Time**: 2-3 hours  
**Complexity**: Medium  
**Value**: High (useful for quality assurance and human review)

**Recommendation**: Update these tools and integrate into the main pipeline as optional QA steps.
