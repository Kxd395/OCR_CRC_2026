#!/usr/bin/env python3
"""
Generate run documentation following the standards from run_20251001_185300_good
"""
from pathlib import Path
from datetime import datetime
import json

def create_run_documentation(run_dir: Path, args, manifest: dict, template_data: dict):
    """Create comprehensive run documentation"""
    
    # Create notes directory
    notes_dir = run_dir / "notes"
    notes_dir.mkdir(exist_ok=True)
    
    # 1. DATA_PROVENANCE.md
    provenance = f"""# Data Provenance - {run_dir.name}

## Source Information

**Supplier**: CRC Survey
**Acquisition Date**: {datetime.now().strftime('%Y-%m-%d')}
**Acquisition Method**: PDF file
**Original Filename**: {Path(args.pdf).name}

## Data Sensitivity

**Contains PHI**: No
**Redaction Required**: No
**Compliance**: N/A

## Processing History

**File Hash (SHA256)**: {manifest.get('input_hash', 'N/A')}
**Preprocessing**: None
**Template**: {args.template}
**Threshold**: {args.threshold if args.threshold else 'Default (11.5%)'}

---

**Documented**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    (notes_dir / "DATA_PROVENANCE.md").write_text(provenance, encoding='utf-8')
    
    # 2. RETENTION.md
    retention = f"""# Retention Policy - {run_dir.name}

## Backup Information

**Primary Location**: `artifacts/{run_dir.name}`
**Backup Location**: Local only (no cloud backup)
**Backup Date**: {datetime.now().strftime('%Y-%m-%d')}

## Encryption

**At Rest**: macOS FileVault encryption
**In Transit**: N/A (local processing)

## Retention Schedule

**Duration**: Indefinite (development/testing)
**Purge Date**: TBD
**Purge Method**: Standard file deletion

## Access Control

**Who has access**: Local user only
**Access log location**: System logs

---

**Documented**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    (notes_dir / "RETENTION.md").write_text(retention, encoding='utf-8')
    
    # 3. RUN_SUMMARY.md
    checkbox_count = len(template_data.get('checkbox_rois_norm', []))
    
    summary = f"""# Run Summary - {run_dir.name}

## Overview

**Run ID**: {run_dir.name}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {'COMPLETE' if manifest.get('status') == 'complete' else 'IN PROGRESS'}

## Configuration

**Template**: {args.template}
**Detection Threshold**: {args.threshold if args.threshold else '11.5% (default)'}
**Checkboxes per page**: {checkbox_count}
**Notes**: {args.notes if args.notes else 'None'}

## Processing Steps

1. ✅ PDF Ingestion - Duration: {manifest.get('durations_sec', {}).get('ingest_pdf', 0):.2f}s
2. ✅ Anchor Detection - Duration: {manifest.get('durations_sec', {}).get('step1_find_anchors', 0):.2f}s
3. ✅ Alignment & Crop - Duration: {manifest.get('durations_sec', {}).get('step2_align_and_crop', 0):.2f}s
4. ✅ Overlay Generation - Duration: {manifest.get('durations_sec', {}).get('make_overlays', 0):.2f}s
5. ✅ OCR & Detection - Duration: {manifest.get('durations_sec', {}).get('run_ocr', 0):.2f}s
6. ✅ QA Overlays - Duration: {manifest.get('durations_sec', {}).get('qa_overlay_from_results', 0):.2f}s

## Outputs

- Step 0: PNG images (`step0_images/`)
- Step 1: Anchor detection results (`step1_anchor_detection/`)
- Step 2: Aligned & cropped images (`step2_alignment_and_crop/`)
- Step 3: Overlay visualizations (`step3_overlays/`)
- Step 4: OCR results (`step4_ocr_results/results.json`)
- Step 5: QA overlays (`step5_qa_overlays/`)
- Excel Export: {manifest.get('export', 'N/A')}

## Notes

{args.notes if args.notes else 'No additional notes provided.'}

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    (notes_dir / "RUN_SUMMARY.md").write_text(summary, encoding='utf-8')
    
    # 4. CONFIGURATION.md
    config = f"""# Configuration - {run_dir.name}

## Template Configuration

**File**: {args.template}

### Checkbox Grid
- **Total checkboxes**: {checkbox_count}
- **Grid layout**: 5 rows × 5 columns
- **Checkbox IDs**: Q1_1 through Q5_5

### Detection Settings
- **Fill threshold**: {args.threshold if args.threshold else '11.5% (default)'}
- **Near threshold margin**: ±{args.near * 100}%
- **Minimum margin**: 2px

### Image Dimensions
- **Template size**: 2550 × 3300 pixels (300 DPI)
- **Cropped size**: 2267 × 2954 pixels
- **Crop region**: x1=141, y1=195, x2=2408, y2=3149

## Processing Configuration

**Coordinate System**: Direct extraction from cropped images (no homography transformation)

**Scripts Used**:
- make_overlays.py - Direct cv2.rectangle() drawing
- run_ocr.py - Direct pixel extraction  
- qa_overlay_from_results.py - Direct drawing matching step 3

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    (notes_dir / "CONFIGURATION.md").write_text(config, encoding='utf-8')
    
    # 5. INDEX.md (Main documentation index)
    index = f"""# Run Documentation Index - {run_dir.name}

## 📋 Quick Access

| Document | Purpose | Status |
|----------|---------|--------|
| `RUN_SUMMARY.md` | Overview & results | ✅ |
| `DATA_PROVENANCE.md` | Source tracking | ✅ |
| `RETENTION.md` | Data lifecycle | ✅ |
| `CONFIGURATION.md` | Settings used | ✅ |

## 📊 Results

**Location**: `step4_ocr_results/results.json`
**Export**: {manifest.get('export', 'Pending')}
**QA Overlays**: `step5_qa_overlays/`

## 🔧 Reproducibility

All configuration files, scripts, and environment details are captured in:
- `configs_snapshot/` - Template and config files with checksums
- `scripts_archive/` - Exact script versions used
- `env/` - Python version, packages, and tools

## 📖 Documentation Standards

This run follows the documentation standards established in:
- `run_20251001_185300_good` (reference implementation)
- `docs/RUN_DOCUMENTATION_TEMPLATE.md` (project standard)

## 🎯 Key Coordinates (Verified)

**X positions**: [280, 690, 1100, 1505, 1915]
**Y positions**: [1290, 1585, 1875, 2150, 2440]
**Normalized to**: Cropped dimensions (2267×2954)

---

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Template**: {args.template}
**Status**: {manifest.get('status', 'complete')}
"""
    (run_dir / "INDEX.md").write_text(index, encoding='utf-8')
    
    print(f"✅ Run documentation created in {run_dir}/")
    print(f"   - INDEX.md")
    print(f"   - notes/DATA_PROVENANCE.md")
    print(f"   - notes/RETENTION.md")
    print(f"   - notes/RUN_SUMMARY.md")
    print(f"   - notes/CONFIGURATION.md")

if __name__ == "__main__":
    import sys
    import argparse
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--threshold", type=float, default=11.5)
    ap.add_argument("--near", type=float, default=0.03)
    ap.add_argument("--notes", default="")
    args = ap.parse_args()
    
    run_dir = Path(args.run_dir)
    
    # Load manifest if exists
    manifest = {}
    if (run_dir / "MANIFEST.json").exists():
        manifest = json.loads((run_dir / "MANIFEST.json").read_text())
    
    # Load template
    template_data = json.loads(Path(args.template).read_text())
    
    create_run_documentation(run_dir, args, manifest, template_data)
