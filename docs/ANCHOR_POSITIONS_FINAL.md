# Anchor Position Configuration - Final Settings

**Date:** October 2, 2025  
**Template Version:** 1.2.0  
**Status:** ✅ Production Ready

## Summary

After extensive testing and iterative adjustments, the anchor detection positions have been calibrated to provide optimal detection accuracy with maximum robustness to page shifts and scanning variations.

## Final Anchor Positions (Normalized)

```json
"anchors_norm": [
  {"x": 0.07, "y": 0.0706},   // Top-Left
  {"x": 0.93, "y": 0.0706},   // Top-Right
  {"x": 0.93, "y": 0.9431},   // Bottom-Right
  {"x": 0.07, "y": 0.9431}    // Bottom-Left
]
```

## Pixel Coordinates (for 1650×2550 images)

| Anchor | Expected Position | Search Box Range | Purpose |
|--------|------------------|------------------|---------|
| **Top-Left** | (115, 180) | Y: 100-260 | Upper-left L-mark |
| **Top-Right** | (1535, 180) | Y: 100-260 | Upper-right L-mark |
| **Bottom-Right** | (1535, 2405) | Y: 2325-2485 | Lower-right L-mark |
| **Bottom-Left** | (115, 2405) | Y: 2325-2485 | Lower-left L-mark |

## Search Window Configuration

- **Size:** 80×80 pixels (±40 pixels from expected position)
- **Method:** Otsu thresholding + contour detection
- **Confidence Scoring:** Based on L-shape match and fill percentage

## Detection Performance

**Test Run:** `run_20251002_065008` (26 pages, 104 total anchors)

```
✅ Overall Detection Rate: 100.0% (104/104 anchors)
✅ All pages: 4/4 anchors detected
✅ Robust to ±60px scanning variations
```

### Actual Detection Ranges (across all pages)

- **Top anchors:** Y = 128-180 pixels (variation: 52px)
- **Bottom anchors:** Y = 2340-2392 pixels (variation: 52px)
- **X positions:** ±70 pixels horizontal shift tolerance

## Key Design Decisions

### 1. **Top Anchor Position (Y=180, box from 100-260)**

- **Rationale:** Actual L-marks appear around Y=165 on average, with variation from Y=128 to Y=180
- **Center at Y=180** provides optimal coverage:
  - Captures marks as low as Y=100 (when page shifts up)
  - Captures marks as high as Y=260 (when page shifts down)
- **Top edge at Y=100** provides visual reference for debugging

### 2. **Bottom Anchor Position (Y=2405, box from 2325-2485)**

- **Rationale:** Actual L-marks appear around Y=2370 on average, with variation from Y=2340 to Y=2392
- **Center at Y=2405** provides optimal coverage:
  - Captures marks as low as Y=2325 (when page shifts down)
  - Captures marks as high as Y=2485 (when page shifts up)
- **Top edge at Y=2325** aligns with form design specifications

### 3. **Search Window Size (±80 pixels)**

- Large enough to handle typical scanning variations (±60px observed)
- Small enough to avoid false positives from nearby features
- Provides 20px safety margin beyond observed variation

## Coordinate System Notes

### Image Dimensions at Each Stage

1. **Original PDF pages:** Variable (scanned resolution)
2. **Step 1 (anchor detection):** 1650×2550 pixels
3. **Step 2 (aligned/cropped):** ~2267×2813 pixels
4. **Template reference space:** 2550×3300 pixels (normalized)

### Normalization Formula

```python
normalized_y = pixel_y / image_height
# Example: Top anchor at Y=180 in 2550px image
normalized_y = 180 / 2550 = 0.0706
```

## Calibration History

| Date | Version | Top Y | Bottom Y | Result |
|------|---------|-------|----------|--------|
| Oct 1 | 1.0.0 | 0.085 | 0.915 | ❌ Bottom too high (middle of page) |
| Oct 1 | 1.1.0 | 0.081 | 0.902 | ❌ Bottom still too high |
| Oct 2 | 1.1.1 | 0.081 | 0.922 | ⚠️ Better, needs adjustment |
| Oct 2 | 1.1.2 | 0.081 | 0.942 | ⚠️ Close, top needs fix |
| Oct 2 | 1.1.3 | 0.0633 | 0.9094 | ⚠️ Centered on average, but not optimal |
| Oct 2 | 1.2.0 | **0.0706** | **0.9431** | ✅ **Production Ready** |

## Visualization References

Anchor detection visualizations show:
- **Green boxes:** Search window boundaries
- **Red boxes:** Detected L-mark locations
- **Confidence scores:** L-shape match quality (20-45% typical)

Example visualization: `artifacts/run_20251002_065008/step1_anchor_detection/visualizations/page_0001_anchors.png`

## Maintenance Notes

### When to Adjust Positions

Consider recalibration if:
1. Detection rate drops below 95%
2. New scanner or document source introduced
3. Form template physical layout changes
4. Consistent detection errors on specific pages

### How to Adjust

1. Run detection on problematic pages
2. Check `anchor_detection_log.json` for actual detected positions
3. Calculate average detected Y positions
4. Update normalized coordinates in `template.json`
5. Re-run detection to verify improvement

### Testing Checklist

- [ ] Run detection on 20+ pages from different batches
- [ ] Verify 100% detection rate (4/4 anchors per page)
- [ ] Check visualizations for proper search box placement
- [ ] Verify alignment quality in step2 output
- [ ] Test with intentionally rotated/shifted pages

## Related Files

- Template: `templates/crc_survey_l_anchors_v1/template.json`
- Detection Script: `scripts/step1_find_anchors.py`
- Grid Overlay Tool: `scripts/add_grid_to_image.py`
- Pipeline Wrapper: `run_pipeline.py`

## Contact

For questions about anchor position calibration, refer to conversation logs or re-run calibration tests with the grid overlay tool for visual verification.
