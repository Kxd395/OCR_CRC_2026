# Anchor Position Adjustment - October 2, 2025

## Problem
Bottom anchors were being detected in the middle of the page instead of near the bottom.

## Root Cause
Confusion between coordinate systems:
- **Template reference**: 2550×3300 pixels (full resolution)
- **Step1 images**: 1650×2550 pixels (scaled down)
- Original Y=0.697 placed anchors at ~2300px in 3300px space = ~1777px in 2550px space (middle of page)

## Solution
Updated bottom anchor Y coordinates from **0.697** to **0.902**

### Calculation:
- Target: Y=2300 pixels in the 2550px high step1 images
- In 3300px reference space: 2300 / (2550/3300) = 2976 pixels
- Normalized: 2976 / 3300 = **0.902**

## Updated Template Values

### Before (Wrong - middle of page):
```json
"anchors_norm": [
  {"x": 0.07, "y": 0.085},  // Top-Left
  {"x": 0.93, "y": 0.086},  // Top-Right  
  {"x": 0.93, "y": 0.697},  // Bottom-Right ❌ TOO HIGH
  {"x": 0.07, "y": 0.697}   // Bottom-Left ❌ TOO HIGH
]
```

### After (Correct - near bottom):
```json
"anchors_norm": [
  {"x": 0.07, "y": 0.085},  // Top-Left
  {"x": 0.93, "y": 0.086},  // Top-Right
  {"x": 0.93, "y": 0.902},  // Bottom-Right ✓ CORRECTED
  {"x": 0.07, "y": 0.902}   // Bottom-Left ✓ CORRECTED
]
```

## Coordinate System Reference

### Template (Normalized to 2550×3300):
- Width: 2550px at 300 DPI
- Height: 3300px at 300 DPI
- All coordinates normalized 0.0 to 1.0

### Step1 Images (Scaled):
- Width: 1650px (scaled by factor 0.647)
- Height: 2550px (scaled by factor 0.773)
- Bottom anchors now at: 0.902 × 2550 = ~2300px ✓

### Step2 Aligned Images (Cropped):
- Width: 2267px (cropped from template space)
- Height: 2813px (cropped from template space)
- Coordinates are in template space (2550×3300)

## Verification

To verify the fix, run:
```bash
python3 run_pipeline.py \
  --pdf review/test_survey.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json
```

The bottom anchors should now be detected near Y=2300 in the step1 visualizations.

## Files Updated
- `templates/crc_survey_l_anchors_v1/template.json` - Version 1.2.0
  - Bottom-Right anchor: Y changed from 0.697 → 0.902
  - Bottom-Left anchor: Y changed from 0.697 → 0.902

## Grid Overlay Tool
Created `scripts/add_grid_to_image.py` to help visualize anchor positions:
```bash
.venv/bin/python scripts/add_grid_to_image.py \
  artifacts/run_*/step1_anchor_detection/visualizations/page_0001_anchors.png \
  --grid-size 50 --thick-grid 100
```

This adds a measurement grid with:
- Thin lines every 50 pixels
- Thick lines every 100 pixels with coordinate labels
- Useful for precise anchor position verification
