# Documentation Index

**CRC OCR Pipeline Documentation**  
**Last Updated:** October 2, 2025

## Quick Navigation

### Getting Started
1. **[README.md](../README.md)** - Project overview and quick start
2. **[00_SETUP.md](00_SETUP.md)** - Environment setup and installation

### Pipeline Process (In Order)
3. **[01_PDF_INGESTION.md](01_PDF_INGESTION.md)** - Step 0: Converting PDFs to images
4. **[02_ANCHOR_DETECTION.md](02_ANCHOR_DETECTION.md)** - Step 1: Finding L-shaped anchor marks
5. **[03_ALIGNMENT_CROPPING.md](03_ALIGNMENT_CROPPING.md)** - Step 2: Aligning and cropping pages
6. **[04_CHECKBOX_DETECTION.md](04_CHECKBOX_DETECTION.md)** - Step 3-5: OCR and checkbox detection
7. **[05_DATA_EXPORT.md](05_DATA_EXPORT.md)** - Step 6-8: Validation and Excel export

### Reference Guides
8. **[FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)** - Output folder structure and naming conventions
9. **[ANCHOR_CALIBRATION.md](ANCHOR_CALIBRATION.md)** - Anchor position calibration guide
10. **[PIPELINE_AUTOMATION.md](PIPELINE_AUTOMATION.md)** - Complete automation reference
11. **[USAGE.md](USAGE.md)** - Detailed usage instructions
12. **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - Best practices and troubleshooting

### Technical Reference
13. **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current project status and validation results
14. **[GEMMA_SETUP.md](GEMMA_SETUP.md)** - Optional Gemma multimodal integration

## Documentation by Use Case

### "I want to run the pipeline"
→ Start with [README.md](../README.md) for quick start  
→ Then see [PIPELINE_AUTOMATION.md](PIPELINE_AUTOMATION.md) for detailed options

### "Anchors are not detecting correctly"
→ See [02_ANCHOR_DETECTION.md](02_ANCHOR_DETECTION.md) for troubleshooting  
→ Then [ANCHOR_CALIBRATION.md](ANCHOR_CALIBRATION.md) for recalibration

### "I need to understand the complete process"
→ Read docs 01-05 in order (PDF Ingestion → Export)

### "Checkboxes are detecting incorrectly"
→ See [04_CHECKBOX_DETECTION.md](04_CHECKBOX_DETECTION.md)  
→ Adjust threshold in pipeline command

### "I want to modify the template"
→ See [ANCHOR_CALIBRATION.md](ANCHOR_CALIBRATION.md) for anchor positions  
→ See [04_CHECKBOX_DETECTION.md](04_CHECKBOX_DETECTION.md) for checkbox positions

### "Something went wrong"
→ See [BEST_PRACTICES.md](BEST_PRACTICES.md) troubleshooting section  
→ Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for known issues

## Pipeline Flow Diagram

```
┌─────────────────────┐
│   Input PDF File    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Step 0: Ingestion  │ ← See 01_PDF_INGESTION.md
│  ✓ Extract pages    │
│  ✓ Convert to PNG   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Step 1: Anchors     │ ← See 02_ANCHOR_DETECTION.md
│  ✓ Find L-marks     │
│  ✓ Validate 100%    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Step 2: Alignment   │ ← See 03_ALIGNMENT_CROPPING.md
│  ✓ Compute warp     │
│  ✓ Align to template│
│  ✓ Crop region      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Step 3-5: OCR       │ ← See 04_CHECKBOX_DETECTION.md
│  ✓ Check alignment  │
│  ✓ Make overlays    │
│  ✓ Detect checkboxes│
│  ✓ QA overlays      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Step 6-8: Export    │ ← See 05_DATA_EXPORT.md
│  ✓ Validate results │
│  ✓ Generate Excel   │
│  ✓ Create reports   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Excel Report      │
│   (4 sheets)        │
└─────────────────────┘
```

## Output Folder Structure

After a complete pipeline run, you'll find:

```
artifacts/run_YYYYMMDD_HHMMSS/
├── step0_images/                    # Step 0: Original page images
├── step1_anchor_detection/          # Step 1: Anchor detection results
├── step2_alignment_and_crop/        # Step 2: Aligned and cropped images
├── step3_overlays/                  # Step 4: Checkbox overlay visualizations
├── step4_ocr_results/               # Step 5: OCR detection results
├── step5_qa_overlays/               # Step 6: QA validation overlays
├── configs_snapshot/                # Configuration snapshots
├── scripts_archive/                 # Script snapshots
├── env/                            # Environment info
├── input/                          # Original PDF copy
├── logs/                           # Processing logs
├── MANIFEST.json                   # Run metadata
└── README.md                       # Run summary
```

## Key Configuration Files

- **Template:** `templates/crc_survey_l_anchors_v1/template.json`
  - Anchor positions (calibrated to 100% detection)
  - Checkbox definitions
  - Search window parameters

- **OCR Config:** `configs/ocr.yaml`
  - Checkbox detection threshold
  - Detection method parameters
  - Confidence thresholds

- **Model Config:** `configs/models.yaml`
  - Model paths and settings
  - Gemma integration (optional)

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-02 | 1.0 | Initial production release with calibrated anchors |
| 2025-10-02 | 1.1 | Fixed pipeline step order, added complete documentation |

## Support & Troubleshooting

**Common Issues:**
- Anchor detection failures → [02_ANCHOR_DETECTION.md](02_ANCHOR_DETECTION.md)
- Alignment problems → [03_ALIGNMENT_CROPPING.md](03_ALIGNMENT_CROPPING.md)
- Checkbox errors → [04_CHECKBOX_DETECTION.md](04_CHECKBOX_DETECTION.md)
- Export issues → [05_DATA_EXPORT.md](05_DATA_EXPORT.md)

**Best Practices:**
- Always check anchor detection reaches 100%
- Review visualizations after each step
- Use consistent threshold values
- Keep run directories for validation

---

**For questions or issues, see [BEST_PRACTICES.md](BEST_PRACTICES.md) troubleshooting section.**
