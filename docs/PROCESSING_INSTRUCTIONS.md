# OCR Pipeline Processing Instructions

## Overview
This document provides step-by-step instructions for processing scanned survey forms through the OCR pipeline. The process includes anchor det**Process**:
1. **Load Anchors**: Read from Step 1 results
2. **Compute Transform**:
   - 4 anchors → Full homography (8 DOF) - handles perspective
   - 3 anchors → Affine transform (6 DOF) - handles rotation/scale/shear
3. **Warp Image**: Transform to template space (2550×3300px)
4. **Add Margin**:
   - Expands 0.125 inches (37.5px at 300 DPI) OUTWARD from anchors
   - Anchors define inner content boundary
   - Margin ensures no edge cutoff
   - Creates consistent bounding box
   - Result: 2267×2813pxgnment, cropping, checkbox extraction, and text OCR.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     OCR PROCESSING PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

Input: Scanned PDF
    ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 0: PDF Ingestion                                          │
│ - Convert PDF to PNG images (300 DPI)                         │
│ - Output: 00_input/page_XXXX.png                              │
└────────────────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 1: Anchor Detection                                       │
│ - Detect 4 L-shaped anchor marks (TL, TR, BR, BL)            │
│ - Apply position filtering and shape scoring                  │
│ - Output: 01_step1_anchor_detection/anchor_log.json          │
└────────────────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 2: Alignment & Cropping                                  │
│ - Compute homography/affine transformation                    │
│ - Warp pages to template space                               │
│ - Add margin around content (0.125" outward from anchors)    │
│ - Output: 02_step2_alignment_and_crop/                       │
│   * aligned_full/         (full 2550×3300px)                 │
│   * aligned_cropped/      (with margin 2267×2813px)          │
└────────────────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 3: Checkbox Extraction                                    │
│ - Extract checkbox ROIs from cropped images                   │
│ - Analyze fill percentage (threshold: 55%)                    │
│ - Output: 03_step3_checkbox_extraction/                       │
│   * checkbox_crops/       (individual checkbox images)        │
│   * checkbox_analysis.json                                    │
└────────────────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 4: OCR Text Extraction                                    │
│ - Run Tesseract on text regions                               │
│ - Extract form metadata                                        │
│ - Output: 04_step4_ocr/ocr_results.json                       │
└────────────────────────────────────────────────────────────────┘
    ↓
Final Output: Structured JSON with checkboxes + text
```

## Directory Structure

```
artifacts/
  run_YYYYMMDD_HHMMSS/
    00_input/
      page_0001.png                    # Original scanned images
      page_0002.png
      ...
    01_step1_anchor_detection/
      anchor_log.json                  # All anchor detections
      visualizations/
        page_0001_anchors.png          # Visual debugging
        ...
    02_step2_alignment_and_crop/
      aligned_full/
        page_0001_aligned_full.png     # Full aligned (2550×3300px)
        ...
      aligned_cropped/
        page_0001_aligned_cropped.png  # Cropped content (1645×2188px)
        ...
      visualizations/
        page_0001_alignment_check.png  # Shows crop region + errors
        ...
      alignment_results.json           # Alignment metrics
    03_step3_checkbox_extraction/
      checkbox_crops/
        page_0001/
          Q1_0.png                     # Individual checkbox images
          Q1_1.png
          ...
      visualizations/
        page_0001_checkboxes.png       # All checkboxes highlighted
        ...
      checkbox_analysis.json           # Fill percentages + results
    04_step4_ocr/
      ocr_results.json                 # Final structured output
    logs/
      step1.log
      step2.log
      ...
```

## Step-by-Step Instructions

### Step 0: PDF Ingestion

**Purpose**: Convert PDF pages to PNG images for processing.

**Command**:
```bash
cd /path/to/crc_ocr_dropin
source .venv/bin/activate
PYTHONPATH=$PWD python scripts/ingest_pdf.py <pdf_file>
```

**Example**:
```bash
PYTHONPATH=$PWD python scripts/ingest_pdf.py review/test_survey.pdf
```

**Output**:
- Creates new run directory: `artifacts/run_YYYYMMDD_HHMMSS/`
- Converts all pages to PNG at 300 DPI
- Saved in: `00_input/page_XXXX.png`

**Validation**:
```bash
# Check image count
ls -1 artifacts/run_*/00_input/*.png | wc -l

# Check first image
open artifacts/run_*/00_input/page_0001.png
```

---

### Step 1: Anchor Detection

**Purpose**: Detect 4 L-shaped anchor marks at page corners for alignment.

**Script**: `scripts/step1_find_anchors.py`

**Command**:
```bash
source .venv/bin/activate
PYTHONPATH=$PWD python scripts/step1_find_anchors.py <run_directory>
```

**Example**:
```bash
PYTHONPATH=$PWD python scripts/step1_find_anchors.py artifacts/run_20251001_181157
```

**Algorithm**:
1. **Binarization**: Otsu thresholding
2. **Contour Detection**: Find all contours
3. **Position Filtering**: Top anchors must be above expected Y, bottom below
4. **Shape Scoring**: L-marks have low compactness (0.1-0.3) vs text (0.4-1.0)
5. **Combined Scoring**: 60% shape + 40% distance from expected position

**Output**:
- `anchor_log.json`: All detections with positions, scores
- `visualizations/`: Images showing detected anchors

**Success Criteria**:
- ✅ 4/4 anchors detected (perfect - homography possible)
- ✅ 3/4 anchors detected (good - affine transform possible)
- ❌ <3 anchors (fail - page cannot be aligned)

**Validation**:
```bash
# View detection summary
python -c "import json; data=json.load(open('artifacts/run_*/01_step1_anchor_detection/anchor_log.json')); print(f\"Detected: {sum(1 for p in data.values() if p['found']>=3)}/{len(data)} pages\")"

# View first page visualization
open artifacts/run_*/01_step1_anchor_detection/visualizations/page_0001_anchors.png
```

---

### Step 2: Alignment & Cropping

**Purpose**: Warp pages to template space and crop to consistent content area.

**Script**: `scripts/step2_align_and_crop.py`

**Command**:
```bash
source .venv/bin/activate
PYTHONPATH=$PWD python scripts/step2_align_and_crop.py <run_directory>
```

**Example**:
```bash
PYTHONPATH=$PWD python scripts/step2_align_and_crop.py artifacts/run_20251001_181157
```

**Process**:
1. **Load Anchors**: Read from Step 1 results
2. **Compute Transform**:
   - 4 anchors → Full homography (8 DOF) - handles perspective
   - 3 anchors → Affine transform (6 DOF) - handles rotation/scale/shear
3. **Warp Image**: Transform to template space (2550×3300px)
4. **Crop Content**:
   - Inset 12.5% from anchor boundaries
   - Removes edge artifacts
   - Creates consistent bounding box
   - Result: ~1645×2188px

**Margin Strategy**:
```
Template anchors define INNER content boundary:
  TL: (178, 280)    TR: (2371, 283)
  BL: (178, 3019)   BR: (2371, 3016)

Anchor bounding box: 2193 × 2739 px
Margin (0.125"): 37.5px at 300 DPI

Crop region (OUTWARD expansion):
  Left:   178 - 37 = 141
  Right:  2371 + 37 = 2408
  Top:    280 - 37 = 243
  Bottom: 3019 + 37 = 3056
  
Final size: 2267 × 2813 px
```

**Output**:
- `aligned_full/`: Full template-space images (2550×3300px - debugging)
- `aligned_cropped/`: Content with margin (2267×2813px - processing)
- `visualizations/`: Alignment quality with residuals
- `alignment_results.json`: Transform matrices, errors, margin settings

**Quality Metrics**:
- **OK**: Mean residual ≤ 4.5px (excellent alignment)
- **WARN**: Mean residual ≤ 6.0px (acceptable alignment)
- **FAIL**: Mean residual > 6.0px (poor alignment)

**Validation**:
```bash
# Check alignment summary
cat artifacts/run_*/02_step2_alignment_and_crop/alignment_results.json | grep -A 5 summary

# View alignment visualization
open artifacts/run_*/02_step2_alignment_and_crop/visualizations/page_0001_alignment_check.png

# Compare full vs cropped
open artifacts/run_*/02_step2_alignment_and_crop/aligned_full/page_0001_aligned_full.png
open artifacts/run_*/02_step2_alignment_and_crop/aligned_cropped/page_0001_aligned_cropped.png
```

---

### Step 3: Checkbox Extraction

**Purpose**: Extract checkbox ROIs and determine checked/unchecked state.

**Script**: `scripts/step3_extract_checkboxes.py`

**Command**:
```bash
source .venv/bin/activate
PYTHONPATH=$PWD python scripts/step3_extract_checkboxes.py <run_directory>
```

**Example**:
```bash
PYTHONPATH=$PWD python scripts/step3_extract_checkboxes.py artifacts/run_20251001_181157
```

**Process**:
1. **Load Cropped Images**: From Step 2 output
2. **Extract ROIs**: Based on template coordinates (adjusted for crop)
3. **Binarize**: Otsu thresholding with inversion
4. **Calculate Fill**: Percentage of black pixels
5. **Threshold**: ≥55% = checked, <55% = unchecked

**ROI Coordinates**:
- Template defines 25 checkbox ROIs per page
- Coordinates are normalized (0.0-1.0)
- Adjusted for crop offset in processing
- Format: `{id, x, y, w, h}`

**Output**:
- `checkbox_crops/page_XXXX/QX_Y.png`: Individual checkbox images
- `visualizations/`: All checkboxes highlighted with fill %
- `checkbox_analysis.json`: Per-checkbox results

**Validation**:
```bash
# Check extraction summary
cat artifacts/run_*/03_step3_checkbox_extraction/checkbox_analysis.json | grep -A 5 summary

# View first page checkboxes
open artifacts/run_*/03_step3_checkbox_extraction/visualizations/page_0001_checkboxes.png

# View individual checkbox
open artifacts/run_*/03_step3_checkbox_extraction/checkbox_crops/page_0001/Q1_0.png
```

---

### Step 4: OCR Text Extraction

**Purpose**: Extract text from form fields using Tesseract.

**Script**: `scripts/step4_run_ocr.py`

**Command**:
```bash
source .venv/bin/activate
PYTHONPATH=$PWD python scripts/step4_run_ocr.py <run_directory>
```

**Example**:
```bash
PYTHONPATH=$PWD python scripts/step4_run_ocr.py artifacts/run_20251001_181157
```

**Process**:
1. **Load Cropped Images**: From Step 2 output
2. **Define Text ROIs**: From template (name, date, ID fields, etc.)
3. **Run Tesseract**: Extract text with confidence scores
4. **Post-process**: Clean/validate extracted text
5. **Merge Results**: Combine with checkbox data

**Output**:
- `ocr_results.json`: Final structured output with text + checkboxes
- `text_crops/`: Individual text region images (debugging)

**Validation**:
```bash
# View final results
cat artifacts/run_*/04_step4_ocr/ocr_results.json | jq '.pages[0]'
```

---

## Configuration Files

### `templates/crc_survey_l_anchors_v1/template.json`

Defines the form template structure:

```json
{
  "document_type_id": "crc_survey_l_anchors_v1",
  "version": "1.0.0",
  "page_size": {
    "width_px": 2550,
    "height_px": 3300,
    "dpi": 300
  },
  "anchors_norm": [
    {"x": 0.07, "y": 0.085},   // TL
    {"x": 0.93, "y": 0.086},   // TR
    {"x": 0.93, "y": 0.914},   // BR
    {"x": 0.07, "y": 0.915}    // BL
  ],
  "margin_settings": {
    "margin_inches": 0.125,
    "direction": "outward",
    "note": "1/8 inch margin OUTWARD from anchor boundaries"
  },
  "checkbox_rois_norm": [
    {
      "id": "Q1_0",
      "x": 0.257,
      "y": 0.231,
      "w": 0.021,
      "h": 0.033
    },
    ...
  ],
  "text_rois_norm": [
    ...
  ]
}
```

### `configs/ocr.yaml`

Processing configuration:

```yaml
dpi: 300
tesseract_langs: ["eng"]

alignment:
  ransac_threshold_px: 3.0
  quality_threshold_ok_px: 4.5
  quality_threshold_warn_px: 6.0

cropping:
  enabled: true
  margin_inches: 0.125
  direction: outward  # Expand beyond anchors, not inward
  save_full_images: true  # For debugging

checkbox:
  fill_threshold_percentage: 55.0
  binarization_method: "otsu"

ocr:
  psm: 6  # Assume uniform block of text
  confidence_threshold: 60
```

---

## Troubleshooting

### Issue: Anchors Not Detected

**Symptoms**: Step 1 fails to find 3+ anchors

**Solutions**:
1. Check visualization to see what was detected
2. Adjust position tolerance in `step1_find_anchors.py`
3. Check if L-marks are visible/clear in scan
4. Try different binarization threshold

### Issue: Poor Alignment

**Symptoms**: High residual errors (>6px)

**Solutions**:
1. Check anchor detection accuracy
2. Verify 3+ anchors were found
3. Check if page is warped/damaged
4. Review alignment visualization

### Issue: Wrong Checkbox Detection

**Symptoms**: Checked boxes marked as unchecked or vice versa

**Solutions**:
1. Check grid diagnostic visualization
2. Verify ROI coordinates align with actual checkboxes
3. Adjust fill threshold (currently 55%)
4. Update template.json if form layout changed

### Issue: OCR Text Incorrect

**Symptoms**: Wrong text extracted

**Solutions**:
1. Check if text regions are properly aligned
2. Verify crop didn't cut off text
3. Adjust Tesseract PSM mode
4. Try different preprocessing (blur, sharpen, etc.)

---

## Best Practices

### For Future Runs

1. **Always use timestamped run directories** - Keeps results organized
2. **Save full aligned images** - Helpful for debugging
3. **Document template changes** - Update version in template.json
4. **Validate each step** - Don't proceed if quality is poor
5. **Keep original PDFs** - For reference and reprocessing

### Updating Templates

If form layout changes:

1. Process a sample page through Step 1-2
2. Open grid diagnostic visualization
3. Manually identify checkbox positions
4. Update `template.json` with new coordinates
5. Test on multiple pages before batch processing

### Quality Control

Run validation checks:
```bash
# Check anchor detection rate
python scripts/analyze_results.py <run_dir> --step 1

# Check alignment quality
python scripts/analyze_results.py <run_dir> --step 2

# Compare results between runs
python scripts/compare_runs.py <run_dir1> <run_dir2>
```

---

## Complete Example Workflow

```bash
# 1. Setup
cd /Users/VScode_Projects/projects/crc_ocr_dropin
source .venv/bin/activate

# 2. Ingest PDF
PYTHONPATH=$PWD python scripts/ingest_pdf.py review/test_survey.pdf
# Note the run directory: artifacts/run_20251001_181157

# 3. Detect anchors
PYTHONPATH=$PWD python scripts/step1_find_anchors.py artifacts/run_20251001_181157

# 4. Review anchor detection
open artifacts/run_20251001_181157/01_step1_anchor_detection/visualizations/page_0001_anchors.png

# 5. Align and crop
PYTHONPATH=$PWD python scripts/step2_align_and_crop.py artifacts/run_20251001_181157

# 6. Review alignment
open artifacts/run_20251001_181157/02_step2_alignment_and_crop/visualizations/page_0001_alignment_check.png

# 7. Create grid diagnostic (optional)
PYTHONPATH=$PWD python scripts/create_grid_diagnostic.py artifacts/run_20251001_181157

# 8. Extract checkboxes
PYTHONPATH=$PWD python scripts/step3_extract_checkboxes.py artifacts/run_20251001_181157

# 9. Review checkbox extraction
open artifacts/run_20251001_181157/03_step3_checkbox_extraction/visualizations/page_0001_checkboxes.png

# 10. Run OCR
PYTHONPATH=$PWD python scripts/step4_run_ocr.py artifacts/run_20251001_181157

# 11. View final results
cat artifacts/run_20251001_181157/04_step4_ocr/ocr_results.json | jq '.'
```

---

## Notes

- **Coordinate System**: All template coordinates are normalized (0.0-1.0) for resolution independence
- **Margin Strategy**: 0.125 inch (1/8") OUTWARD expansion ensures no content cutoff while maintaining consistency
- **Anchor Detection**: Non-deterministic behavior can occur with similar-scoring candidates - archive good results
- **Transform Types**: Homography (4 pts) > Affine (3 pts) > fail (<3 pts)
- **Quality Thresholds**: Based on empirical testing with sample forms
- **Future Enhancements**: Deterministic anchor selection, machine learning for checkbox detection

---

**Document Version**: 1.0  
**Last Updated**: October 1, 2025  
**Author**: OCR Pipeline Team
