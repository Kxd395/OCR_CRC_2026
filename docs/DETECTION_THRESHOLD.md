# Checkbox Detection Threshold Configuration

## Overview
This document describes the optimized detection threshold for checkbox OCR in the CRC survey forms.

## Current Settings (v1.2.0)

### Detection Threshold: **11.5%**

After extensive testing across multiple pages, we determined that **11.5%** is the optimal threshold for detecting filled checkboxes in these forms.

### Why 11.5%?

**Empty Checkbox Baseline:**
- Empty checkboxes typically show: **9.8% - 11.4%** fill
- This baseline is due to:
  - Printed checkbox borders
  - Paper texture and scanning artifacts
  - Minor variations in alignment

**Filled Checkbox Range:**
- Lightly filled checkboxes: **11.5% - 15%**
- Moderately filled: **15% - 30%**
- Heavily filled: **30% - 40%+**

**Threshold Selection:**
- Set at **11.5%** to cleanly separate empty (≤11.4%) from filled (≥11.5%)
- Provides reliable detection for light pencil marks
- Avoids false positives from empty checkboxes

## Detection Method

**Method:** Otsu Thresholding
- Automatically determines optimal binary threshold
- Separates dark pixels (marks) from light pixels (background)
- Robust across varying mark intensities

**Process:**
1. Extract checkbox ROI (120px × 110px)
2. Apply Otsu thresholding to binarize
3. Count dark pixels (potential marks)
4. Calculate: `fill_percent = (dark_pixels / total_pixels) × 100`
5. Compare to threshold: `filled = (fill_percent >= 11.5)`

## Testing Results

### Page 4 Results (11.5% threshold)
- **Empty boxes:** 9.8% - 11.4% fill
- **Filled boxes:**
  - Q2_3: 11.9% ✓
  - Q3_2: 13.0% ✓
  - Q4_1: 12.5% ✓
  - Q5_0: 13.4% ✓

### Page 7 Results (11.5% threshold)
- **Filled boxes:**
  - Q2_1: 12.7% ✓
  - Q3_3: 12.4% ✓
  - Q4_2: 12.4% ✓
  - Q5_4: 13.8% ✓

### Page 13 Results (11.5% threshold)
- **Filled boxes:**
  - Q1_4: 24.5% ✓
  - Q2_3: 35.2% ✓
  - Q3_4: 31.6% ✓
  - Q4_3: 30.2% ✓
  - Q5_4: 39.9% ✓

## Configuration

### Template Configuration
Located in: `templates/crc_survey_l_anchors_v1/template.json`

```json
{
  "version": "1.2.0",
  "detection_settings": {
    "fill_threshold_percent": 11.5,
    "method": "otsu",
    "description": "Threshold calibrated for light checkbox marks. Empty boxes typically show 9.8-11.4% fill, checked boxes show 11.5%+ fill."
  }
}
```

### Script Usage

**Identify filled checkboxes on a specific page:**
```bash
python scripts/identify_filled_checkboxes.py <page_number> <threshold>

# Examples:
python scripts/identify_filled_checkboxes.py 0004 11.5
python scripts/identify_filled_checkboxes.py 0013 11.5
```

**Run detection across all pages:**
```bash
python scripts/rerun_detection_with_threshold.py artifacts/run_YYYYMMDD_HHMMSS 11.5
```

## Historical Notes

### Previous Thresholds
- **Original:** 55% (too high, missed light marks)
- **First adjustment:** 25% (worked for heavier marks)
- **Second adjustment:** 12% (close, but some false positives)
- **Final optimized:** 11.5% (clean separation)

### Threshold Evolution
1. Started with 55% (standard for heavy pen marks)
2. Discovered user's forms had lighter marks (25-40%)
3. Tested multiple thresholds: 25%, 12%, 11.7%
4. Settled on 11.5% based on empty box distribution

## Troubleshooting

### False Positives (Empty boxes detected as filled)
- **Symptom:** Boxes with 11.0-11.4% showing as filled
- **Solution:** Increase threshold slightly (try 11.7% or 12%)
- **Check:** Review empty box distribution on your pages

### False Negatives (Filled boxes not detected)
- **Symptom:** Lightly marked boxes not detected
- **Solution:** Decrease threshold (try 11.0% or 10.5%)
- **Warning:** May increase false positives

### Adjusting for Different Forms
If using different survey forms:
1. Run identification on several pages
2. Note the fill % of empty boxes (typically 9-12%)
3. Note the fill % of your lightest filled boxes
4. Set threshold between these ranges
5. Test on multiple pages to validate

## Related Documentation
- `docs/CHECKBOX_COORDINATES.md` - Coordinate documentation
- `docs/BEST_PRACTICES.md` - General best practices
- `templates/crc_survey_l_anchors_v1/template.json` - Template configuration

---
*Last Updated: October 1, 2025*
*Version: 1.2.0*
