# Folder Naming Convention

**Last Updated:** October 2, 2025

## Run Directory Structure

Each pipeline run creates a timestamped directory: `artifacts/run_YYYYMMDD_HHMMSS/`

### Step Folders (In Processing Order)

```
artifacts/run_YYYYMMDD_HHMMSS/
│
├── step0_images/                    # Step 0: PDF Ingestion
│   ├── page_0001.png               # Original extracted page images (1650×2550px)
│   ├── page_0002.png
│   └── ...
│
├── step1_anchor_detection/          # Step 1: Anchor Detection
│   ├── anchor_detection_log.json   # Detection results with positions
│   └── visualizations/             # Visual confirmation images
│       ├── page_0001_anchors.png   # Green boxes = search windows
│       ├── page_0002_anchors.png   # Red boxes = detected anchors
│       └── ...
│
├── step2_alignment_and_crop/        # Step 2: Alignment & Cropping
│   ├── aligned_full/               # Full aligned pages (2550×3300px)
│   │   ├── page_0001_aligned.png
│   │   ├── page_0002_aligned.png
│   │   └── ...
│   └── aligned_cropped/            # Cropped checkbox regions (~2267×2813px)
│       ├── page_0001_cropped.png
│       ├── page_0002_cropped.png
│       └── ...
│
├── step3_overlays/                  # Step 4: Checkbox Overlays (visualization)
│   ├── page_0001_overlay.png       # Orange boxes showing checkbox ROIs
│   ├── page_0002_overlay.png
│   └── ...
│
├── step4_ocr_results/               # Step 5: OCR Detection Results
│   └── results.json                # Checkbox detection data
│
├── step5_qa_overlays/               # Step 6: QA Validation Overlays
│   ├── page_0001_qa.png            # Green boxes = detected checkboxes
│   ├── page_0002_qa.png
│   └── ...
│
├── configs_snapshot/                # Configuration Snapshots
│   ├── template.json               # Template used for this run
│   ├── ocr.yaml                    # OCR config used
│   ├── models.yaml                 # Model config used
│   └── checksums.txt               # File integrity checksums
│
├── scripts_archive/                 # Script Snapshots
│   ├── ingest_pdf.py               # Exact scripts used for this run
│   ├── step1_find_anchors.py
│   ├── step2_align_and_crop.py
│   └── ...
│
├── env/                            # Environment Information
│   ├── python.txt                  # Python version
│   ├── pip_freeze.txt              # Installed packages
│   ├── os.txt                      # Operating system
│   └── tools.txt                   # Tool versions (tesseract, opencv)
│
├── input/                          # Input Files
│   └── survey.pdf                  # Copy of original PDF
│
├── logs/                           # Processing Logs
│   ├── steps.jsonl                 # Step execution log
│   ├── homography.json             # Homography transformations per page
│   └── ocr_results.json            # OCR results (also in step4/)
│
├── MANIFEST.json                   # Run Metadata
└── README.md                       # Run Summary
```

### Export Location

Excel reports are exported to:
```
exports/run_YYYYMMDD_HHMMSS.xlsx
```

## Folder Purpose Descriptions

### step0_images/
**Purpose:** Original page images extracted from PDF  
**Format:** PNG, grayscale, 1650×2550 pixels  
**Script:** `scripts/ingest_pdf.py`  
**Notes:** These are the "as-scanned" images before any processing

### step1_anchor_detection/
**Purpose:** L-shaped anchor mark detection results  
**Script:** `scripts/step1_find_anchors.py`  
**Key Files:**
- `anchor_detection_log.json` - Detected vs expected positions, confidence scores
- `visualizations/` - Visual confirmation with search boxes

**Validation:** Check for 100% detection rate before proceeding

### step2_alignment_and_crop/
**Purpose:** Aligned and perspective-corrected pages  
**Script:** `scripts/step2_align_and_crop.py`  
**Subdirectories:**
- `aligned_full/` - Full page aligned to template space (2550×3300px)
- `aligned_cropped/` - Cropped to checkbox region only (~2267×2813px)

**Notes:** Uses homography transform calculated from detected anchors

### step3_overlays/
**Purpose:** Visual reference showing checkbox detection regions  
**Script:** `scripts/make_overlays.py`  
**Format:** Original images with orange boxes overlaid  
**Notes:** For human verification only, not used in OCR processing

### step4_ocr_results/
**Purpose:** Checkbox detection results  
**Script:** `scripts/run_ocr.py`  
**Key Files:**
- `results.json` - Per-page, per-checkbox detection results with scores

**Data Structure:**
```json
{
  "page": "page_0001.png",
  "checkboxes": [
    {"id": "Q1_1", "score": 0.823, "checked": true},
    {"id": "Q1_2", "score": 0.042, "checked": false}
  ]
}
```

### step5_qa_overlays/
**Purpose:** QA validation showing detected checkboxes  
**Script:** `scripts/qa_overlay_from_results.py`  
**Format:** Images with green boxes on detected (checked) checkboxes  
**Notes:** Compare with step3_overlays to validate detection accuracy

## Naming Rationale

### Why "step0", "step1", etc.?
- **Sequential Processing:** Numbers indicate processing order
- **Sortability:** Folders appear in execution order when listed alphabetically
- **Clarity:** No ambiguity about which step comes first
- **Debugging:** Easy to identify where in pipeline issues occurred

### Why Descriptive Names?
- **Self-Documenting:** Name describes content without documentation
- **Searchability:** Easy to find specific outputs
- **Maintainability:** New team members understand structure immediately

## Historical Folder Names (Legacy)

Previous runs may use different folder names:

| Old Name | New Name | Notes |
|----------|----------|-------|
| `images/` | `step0_images/` | More descriptive |
| `step1_anchor_detection/` | *(unchanged)* | Already clear |
| `step2_alignment/` | `step2_alignment_and_crop/` | Reflects both operations |
| `overlays/` | `step3_overlays/` | Numbered for sequence |
| *(none)* | `step4_ocr_results/` | New dedicated location |
| *(none)* | `step5_qa_overlays/` | Separated from step3 |

## Script Updates

Scripts updated to use new folder structure:

1. **`scripts/ingest_pdf.py`**
   - Creates: `step0_images/`

2. **`scripts/step1_find_anchors.py`**
   - Reads: `step0_images/`
   - Creates: `step1_anchor_detection/`

3. **`scripts/step2_align_and_crop.py`**
   - Reads: `step0_images/`, `step1_anchor_detection/`
   - Creates: `step2_alignment_and_crop/`

4. **`scripts/make_overlays.py`**
   - Reads: `step2_alignment_and_crop/aligned_cropped/`
   - Creates: `step3_overlays/`

5. **`scripts/run_ocr.py`**
   - Reads: `step2_alignment_and_crop/aligned_cropped/`
   - Creates: `step4_ocr_results/`

6. **`scripts/qa_overlay_from_results.py`**
   - Reads: `step2_alignment_and_crop/aligned_cropped/`, `step4_ocr_results/`
   - Creates: `step5_qa_overlays/`

## Best Practices

### When Debugging
1. Check folders in numerical order (step0 → step1 → step2 → ...)
2. Look for missing folders to identify where pipeline failed
3. Check visualizations in step1 and step5 for quality issues

### When Archiving
- Keep entire run directory intact for reproducibility
- Scripts archive and config snapshot allow exact reproduction
- Environment info enables debugging platform-specific issues

### When Cleaning Up
- Can safely delete old run directories after validation
- Keep successful reference runs for comparison
- Exported Excel files are in separate `exports/` directory

## Migration Guide

If you have old runs with previous folder structure:

**Option 1: Leave as-is**
- Old runs still valid with their original structure
- Only new runs use new naming

**Option 2: Rename manually**
```bash
cd artifacts/run_YYYYMMDD_HHMMSS/
mv images step0_images
mv overlays step3_overlays
# etc.
```

**Option 3: Re-run pipeline**
- Most reliable option
- Ensures consistency
- Validates current code matches results

---

**For questions about specific folders, see:**
- PDF Ingestion: `docs/01_PDF_INGESTION.md`
- Anchor Detection: `docs/02_ANCHOR_DETECTION.md`
- Alignment: `docs/03_ALIGNMENT_CROPPING.md`
- Checkbox Detection: `docs/04_CHECKBOX_DETECTION.md`
- Data Export: `docs/05_DATA_EXPORT.md`
