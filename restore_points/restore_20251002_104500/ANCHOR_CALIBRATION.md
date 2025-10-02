# Anchor Position Calibration Guide

## Final Calibrated Positions

**Last Updated:** October 2, 2025  
**Status:** ✅ Validated - 100% detection rate (104/104 anchors across 26 pages)

### Anchor Coordinates in template.json

```json
{
  "anchors_norm": [
    {"x": 0.07, "y": 0.0706},   // Top-Left
    {"x": 0.93, "y": 0.0706},   // Top-Right  
    {"x": 0.93, "y": 0.9431},   // Bottom-Right
    {"x": 0.07, "y": 0.9431}    // Bottom-Left
  ],
  "anchor_search_window_px": 80
}
```

## Understanding the Coordinate System

### Key Concepts

1. **Template Coordinates are CENTER positions** - Not edges!
2. **Search Window** - Algorithm searches ±80 pixels from center (160px total window)
3. **Image Dimensions** - Step1 images are 1650×2550 pixels
4. **Normalization Formula** - `normalized_value = pixels / 2550`

### Search Box Positioning

The search box extends **±80 pixels** from the center point:
- **Box Top Edge** = Center Y - 80
- **Box Bottom Edge** = Center Y + 80
- **Box Height** = 160 pixels

### Final Calibration Details

#### Top Anchors (Y = 0.0706)
- **Normalized:** 0.0706
- **Pixel Center:** 180px (0.0706 × 2550)
- **Search Box:** Y = 100px (top) to Y = 260px (bottom)
- **Calculation:** 
  - Desired top edge: 100px
  - Required center: 100 + 80 = 180px
  - Normalized: 180 / 2550 = 0.0706

#### Bottom Anchors (Y = 0.9431)
- **Normalized:** 0.9431
- **Pixel Center:** 2405px (0.9431 × 2550)
- **Search Box:** Y = 2325px (top) to Y = 2485px (bottom)
- **Calculation:**
  - Desired top edge: 2325px
  - Required center: 2325 + 80 = 2405px
  - Normalized: 2405 / 2550 = 0.9431

#### X Positions
- **Left Anchors (X = 0.07):** 115.5px center (35.5-195.5px search box)
- **Right Anchors (X = 0.93):** 1534.5px center (1454.5-1614.5px search box)

## Validation Results

**Test Run:** `run_20251002_065008`  
**Date:** October 2, 2025, 6:50 AM

### Detection Statistics
- **Total Pages:** 26
- **Expected Anchors:** 104 (26 pages × 4 anchors)
- **Detected Anchors:** 104
- **Detection Rate:** 100.0%

### Detection Ranges
All detected anchors fell within their search windows:

- **Top Anchors:** Y = 128-180 pixels (within 100-260 window) ✓
- **Bottom Anchors:** Y = 2340-2392 pixels (within 2325-2485 window) ✓

### Sample Detection Data

| Page | Top-Left Y | Top-Right Y | Bottom-Right Y | Bottom-Left Y |
|------|-----------|-------------|----------------|---------------|
| 0001 | 166.1     | 166.4       | 2377.6         | 2376.1        |
| 0013 | 160.8     | 160.6       | 2378.9         | 2375.3        |
| 0026 | 157.7     | 157.8       | 2391.8         | 2380.3        |

All values within expected ±80 pixel tolerance.

## Calibration History

### Iteration Process

1. **Initial Template** - Top (Y=0.086), Bottom (Y=0.915)
   - Result: Bottom anchors too high
   
2. **First Adjustment** - Bottom → 0.697
   - Result: Bottom anchors in middle of page
   
3. **Second Adjustment** - Bottom → 0.902, 0.922, 0.942
   - Result: Moving closer but still not right
   
4. **Top Adjustment** - Top → 0.081, 0.082, 0.0633
   - Result: Top moving up appropriately
   
5. **Edge Confusion** - Top → 0.0549, 0.0569
   - Issue: Confusing center position with edge position
   
6. **Edge Clarification** - Realized need to calculate center from edge
   - Understanding: To get top edge at Y=100, center must be Y=180
   
7. **Final Calibration**
   - Top: 0.0706 (100px top edge requirement met)
   - Bottom: 0.9431 (2325px top edge requirement met)
   - Result: ✅ 100% detection rate

### Lessons Learned

1. **Template stores centers, not edges** - Always add/subtract 80px
2. **User requirements often specify edges** - Convert to centers before updating template
3. **Test incrementally** - Small changes, verify results
4. **Use visualization tools** - Grid overlay (`add_grid_to_image.py`) helped significantly
5. **Understand tolerance** - ±80px search window provides robust detection

## Tools for Calibration

### Grid Overlay Tool

Use `scripts/add_grid_to_image.py` to visualize exact pixel positions:

```bash
.venv/bin/python scripts/add_grid_to_image.py \
  --image artifacts/run_20251002_065008/images/page_0001.png \
  --output page_0001_with_grid.png \
  --grid-size 50 \
  --thick-grid 100
```

Features:
- 50px fine grid
- 100px thick grid with coordinate labels
- 30% opacity blend
- Helps identify exact pixel positions of anchor marks

### Anchor Detection with Visualization

```bash
.venv/bin/python scripts/step1_find_anchors.py \
  --run-dir artifacts/run_YYYYMMDD_HHMMSS \
  --template templates/crc_survey_l_anchors_v1/template.json
```

Outputs:
- `step1_anchor_detection/anchor_detection_log.json` - Detailed detection data
- `step1_anchor_detection/visualizations/` - Images with search boxes and detections
- Console summary with detection rates

## Troubleshooting

### Problem: Anchors not detecting

**Check:**
1. Are the L-shaped marks clearly visible on scanned pages?
2. Is the search window large enough? (Current: 80px = ±40 from center)
3. Are the template coordinates in the right ballpark?

**Solution:**
- Use grid overlay to identify actual pixel positions of L-marks
- Adjust `anchors_norm` values accordingly
- Remember: template uses centers, add 80 to get from desired top edge to center

### Problem: Anchors detecting but in wrong location

**Check:**
1. Are you confusing center position vs edge position?
2. Did you account for the ±80px search window?
3. Are you using the correct image dimensions (2550px height)?

**Solution:**
- Desired top edge + 80 = center position
- Normalize: center_pixels / 2550 = normalized_value
- Update template with normalized center value

### Problem: Detection rate < 100%

**Check:**
1. Are some pages skewed or rotated beyond tolerance?
2. Are some L-marks obscured or poorly scanned?
3. Is the search window too small for the variation?

**Solution:**
- Review visualization images to see which anchors failed
- Consider increasing `anchor_search_window_px` if consistent near-misses
- May need to rescan problematic pages with better quality

## Reference Formulas

### Convert edge position to template value
```
desired_top_edge_px = 100  # Example: top of search box at Y=100
center_px = desired_top_edge_px + 80
normalized = center_px / 2550
# Result: 0.0706
```

### Convert template value to edge positions
```
normalized = 0.9431  # Example: bottom anchor
center_px = normalized * 2550  # = 2405
top_edge = center_px - 80      # = 2325
bottom_edge = center_px + 80   # = 2485
```

### Calculate X positions (width = 1650)
```
normalized_x = pixel_x / 1650
pixel_x = normalized_x * 1650
```

## Maintenance

When updating anchor positions:

1. **Document the reason** - What problem are you solving?
2. **Make incremental changes** - Don't jump around wildly
3. **Test immediately** - Run step1_find_anchors.py after each change
4. **Check visualizations** - Look at the search box overlays
5. **Validate fully** - Run on all pages before finalizing
6. **Update this document** - Keep calibration history current

## See Also

- `templates/crc_survey_l_anchors_v1/template.json` - Current template
- `scripts/step1_find_anchors.py` - Anchor detection implementation
- `scripts/add_grid_to_image.py` - Grid overlay tool
- `docs/USAGE.md` - General usage guide
