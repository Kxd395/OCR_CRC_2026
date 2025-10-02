# Best Practices (short)
- Use **four** high-contrast anchors (TL, TR, BR, BL) near page corners.
- 300–400 DPI; homography residuals: ok≤4.5 px; warn 4.5–6; fail>6.
- Draw overlays in **image space** with `Minv`; crop checkboxes in **template space** after warping with `M`.
- **Detection threshold:** 11.5% for checkbox fill detection (calibrated for light marks). See `docs/DETECTION_THRESHOLD.md`.
- Keep PHI out of git (`data/`, `artifacts/` are ignored).
