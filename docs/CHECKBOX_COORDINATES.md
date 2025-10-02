# Checkbox Coordinate Mapping

## Overview

This document provides the precise pixel coordinates for all checkbox locations on the CRC survey form after alignment and cropping. These coordinates are used to generate the normalized ROI coordinates in the template files.

## Reference Image Dimensions

- **Source**: Aligned and cropped page images
- **Dimensions**: 2267 × 2813 pixels (width × height)
- **DPI**: 300
- **Date Measured**: October 1, 2025
- **Run**: run_20251001_185300

## Checkbox Grid Layout

The survey contains a **5 × 5 grid** of checkboxes (25 total), arranged as:
- **5 Questions (Rows)**: Q1 through Q5
- **5 Response Options (Columns)**: Box 1 through Box 5 per question

## Physical Measurements

### Box Dimensions
- **Width**: 120 pixels
- **Height**: 110 pixels

### Spacing
- **Horizontal (Box-to-Box)**: 410 pixels (measured from left edge to left edge)
- **Vertical (Row-to-Row)**: 272 pixels (measured from top edge to top edge)

## X Coordinates (Consistent Across All Rows)

| Box Position | X Coordinate (Left Edge) | X + Width (Right Edge) |
|--------------|--------------------------|------------------------|
| Box 1        | 280                      | 400                    |
| Box 2        | 690                      | 810                    |
| Box 3        | 1100                     | 1220                   |
| Box 4        | 1505                     | 1625                   |
| Box 5        | 1915                     | 2035                   |

## Y Coordinates (By Question/Row)

| Question | Y Coordinate (Top Edge) | Y + Height (Bottom Edge) |
|----------|-------------------------|--------------------------|
| Q1       | 1228                    | 1338                     |
| Q2       | 1500                    | 1610                     |
| Q3       | 1772                    | 1882                     |
| Q4       | 2044                    | 2154                     |
| Q5       | 2316                    | 2426                     |

## Complete Coordinate Matrix

### Question 1 (Row 1, y=1228)
- **Q1_Box1**: (280, 1228) → (400, 1338)
- **Q1_Box2**: (690, 1228) → (810, 1338)
- **Q1_Box3**: (1100, 1228) → (1220, 1338)
- **Q1_Box4**: (1505, 1228) → (1625, 1338)
- **Q1_Box5**: (1915, 1228) → (2035, 1338)

### Question 2 (Row 2, y=1500)
- **Q2_Box1**: (280, 1500) → (400, 1610)
- **Q2_Box2**: (690, 1500) → (810, 1610)
- **Q2_Box3**: (1100, 1500) → (1220, 1610)
- **Q2_Box4**: (1505, 1500) → (1625, 1610)
- **Q2_Box5**: (1915, 1500) → (2035, 1610)

### Question 3 (Row 3, y=1772)
- **Q3_Box1**: (280, 1772) → (400, 1882)
- **Q3_Box2**: (690, 1772) → (810, 1882)
- **Q3_Box3**: (1100, 1772) → (1220, 1882)
- **Q3_Box4**: (1505, 1772) → (1625, 1882)
- **Q3_Box5**: (1915, 1772) → (2035, 1882)

### Question 4 (Row 4, y=2044)
- **Q4_Box1**: (280, 2044) → (400, 2154)
- **Q4_Box2**: (690, 2044) → (810, 2154)
- **Q4_Box3**: (1100, 2044) → (1220, 2154)
- **Q4_Box4**: (1505, 2044) → (1625, 2154)
- **Q4_Box5**: (1915, 2044) → (2035, 2154)

### Question 5 (Row 5, y=2316)
- **Q5_Box1**: (280, 2316) → (400, 2426)
- **Q5_Box2**: (690, 2316) → (810, 2426)
- **Q5_Box3**: (1100, 2316) → (1220, 2426)
- **Q5_Box4**: (1505, 2316) → (1625, 2426)
- **Q5_Box5**: (1915, 2316) → (2035, 2426)

## Converting to Normalized Coordinates

The template files use normalized coordinates (0.0 to 1.0 range) to be resolution-independent.

### Formula
```
normalized_x = pixel_x / image_width
normalized_y = pixel_y / image_height
normalized_w = box_width / image_width
normalized_h = box_height / image_height
```

### Constants
- **image_width** = 2267
- **image_height** = 2813
- **box_width** = 120
- **box_height** = 110

### Example: Q1_Box1
```
x = 280 / 2267 = 0.1235
y = 1228 / 2813 = 0.4365
w = 120 / 2267 = 0.0529
h = 110 / 2813 = 0.0391
```

### Template Format
```json
{
  "id": "Q1_0",
  "x": 0.1235,
  "y": 0.4365,
  "w": 0.0529,
  "h": 0.0391
}
```

## Measurement Methodology

### Tools Used
1. **Grid Overlay Script**: `scripts/create_simple_grid.py`
   - Generated 50px and 100px reference grid
   - Visual verification on aligned images

2. **Bounding Box Script**: `scripts/draw_checkbox_row.py`
   - Drew precise bounding boxes at measured coordinates
   - Iterative refinement with visual feedback

3. **Image Analysis**: OpenCV-based measurement tools
   - Pixel-perfect coordinate identification
   - Grid-based verification

### Measurement Process
1. Started with visual grid overlay (50px/100px spacing)
2. Identified Reference Point: Q2_Box2 at (690, 1500)
3. Calculated Q2_Box1 position: x = 690 - 410 = 280
4. Established vertical increment: 1500 - 1228 = 272px
5. Validated all 25 positions with visual overlay
6. Fine-tuned positions:
   - Q1-Q5 Box4: -5px adjustment
   - Q1-Q5 Box5: +5px final adjustment

### Quality Assurance
- ✅ Visual verification with color-coded overlays
- ✅ Mathematical consistency checks
- ✅ Alignment with actual form checkboxes confirmed
- ✅ OCR pipeline tested (all ROIs processed successfully)

## Visual References

Generated visual references can be found in the run directory:
- `checkbox_row_box.png`: Complete 5×5 grid with all boxes marked
- `grid_overlay_1000px.png`: Grid reference for measurement
- `checkbox_coordinates.md`: Run-specific notes with detailed breakdown

## Usage in Pipeline

These coordinates are used in:
1. **Template Generation**: Creating/updating `template.json` files
2. **OCR Processing**: Defining ROI regions for checkbox detection
3. **Validation**: Verifying alignment accuracy
4. **Overlay Generation**: Creating visual verification images

## Maintenance Notes

### When to Update
- Form layout changes
- Alignment algorithm modifications
- Image resolution changes
- Quality issues detected in OCR results

### Validation Steps
1. Run grid overlay script on new aligned images
2. Verify checkbox centers align with bounding boxes
3. Test OCR detection rates
4. Update template if needed
5. Document changes in run notes

## Related Documentation

- [Detection Threshold Configuration](./DETECTION_THRESHOLD.md) - **11.5% threshold for checkbox detection**
- [Template Structure](./TEMPLATE_STRUCTURE.md)
- [OCR Configuration](./OCR_CONFIGURATION.md)
- [Alignment Process](./ALIGNMENT_PROCESS.md)
- [Run Documentation Template](./RUN_DOCUMENTATION_TEMPLATE.md)

---

**Last Updated**: October 1, 2025  
**Validated By**: Manual measurement with grid overlay  
**Status**: ✅ Verified and tested with OCR pipeline
