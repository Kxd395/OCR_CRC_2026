#!/usr/bin/env python3
"""
Complete Run Initialization and Documentation Script

This script sets up a new processing run with all required documentation,
snapshots, and structure following best practices.
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def create_run_structure(run_dir: Path) -> None:
    """Create complete directory structure for a run."""
    directories = [
        "input",
        "scripts_archive",
        "step1_anchors",
        "step2_cropped",
        "step3_text",
        "diagnostics/grid_overlays",
        "notes",
        "env",
        "configs_snapshot",
        "metrics/histograms",
        "diffs"
    ]
    
    for dir_path in directories:
        (run_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created directory structure in {run_dir.name}")


def capture_environment(run_dir: Path) -> None:
    """Capture environment using dedicated script."""
    script = Path(__file__).parent / "capture_environment.py"
    
    if script.exists():
        print("Capturing environment...")
        subprocess.run([sys.executable, str(script), str(run_dir)], check=True)
    else:
        print("⚠️  capture_environment.py not found, skipping")


def snapshot_configs(run_dir: Path, template: str = "crc_survey_l_anchors_v1") -> dict:
    """Snapshot configurations using dedicated script."""
    script = Path(__file__).parent / "snapshot_configs.py"
    
    if script.exists():
        print("Snapshotting configurations...")
        result = subprocess.run(
            [sys.executable, str(script), str(run_dir), "--template", template],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        # Load checksums
        metadata_file = run_dir / "configs_snapshot" / "metadata.json"
        if metadata_file.exists():
            return json.loads(metadata_file.read_text())
    else:
        print("⚠️  snapshot_configs.py not found, skipping")
        return {}


def archive_scripts(run_dir: Path) -> None:
    """Archive current scripts to run directory."""
    scripts_archive = run_dir / "scripts_archive"
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"
    
    scripts_to_archive = [
        "step1_find_anchors.py",
        "step2_align_and_crop.py",
        "step3_extract_text.py",
        "run_ocr.py",
        "check_alignment.py",
        "make_overlays.py",
        "qa_overlay_from_results.py",
        "validate_run.py",
        "common.py",
        "expand_grid.py"
    ]
    
    archived_count = 0
    for script_name in scripts_to_archive:
        src = scripts_dir / script_name
        if src.exists():
            shutil.copy2(src, scripts_archive / script_name)
            archived_count += 1
    
    print(f"✅ Archived {archived_count} scripts")


def create_manifest(
    run_dir: Path,
    template: str,
    config_checksums: dict,
    input_file: Optional[Path] = None
) -> None:
    """Create MANIFEST.json for the run."""
    
    run_id = run_dir.name
    
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": "America/New_York",
        "operator": "user",  # Update with actual user
        "git_commit": None,  # Will be filled during commit
        "git_branch": None,
        "template": {
            "name": template,
            "version": "1.0"
        },
        "input": {
            "file": input_file.name if input_file else "survey.pdf",
            "pages": None,  # Will be filled during processing
            "md5": None
        },
        "parameters": {
            "step1": {
                "dpi": 300,
                "anchor_detection_threshold": 0.7
            },
            "step2": {
                "crop_margin_inches": 0.125,
                "expected_width_px": 2267,
                "expected_height_px": 2813
            },
            "step3": {
                "tesseract_psm": 6,
                "language": "eng"
            }
        },
        "snapshots": config_checksums.get("files", {}),
        "execution": {
            "step1": {"status": "pending"},
            "step2": {"status": "pending"},
            "step3": {"status": "pending"}
        },
        "gates": {
            "alignment": {
                "ok_threshold_px": 2.0,
                "warn_threshold_px": 5.0,
                "pass": None
            },
            "checkbox": {
                "enabled": False,
                "threshold": 0.55,
                "pass": None
            },
            "ocr": {
                "min_text_length": 100,
                "pass": None
            }
        },
        "issues": [],
        "notes": ""
    }
    
    manifest_file = run_dir / "MANIFEST.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    print(f"✅ Created MANIFEST.json")


def create_readme(run_dir: Path, template: str) -> None:
    """Create README.md from template."""
    
    run_id = run_dir.name
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    readme_content = f"""# Run {run_id}

## Run Information

**Date**: {date_str}
**Operator**: [Your Name]
**Template**: {template}
**Git Commit**: [to be filled]
**Branch**: [to be filled]

## Input Description

**Source**: [Where did the PDF come from?]
**File**: `survey.pdf`
**Pages**: [number]
**Quality**: [Good/Fair/Poor - describe any issues]
**Special Notes**: [Any unusual characteristics]

## Processing Parameters

### Step 1: Find Anchors
- DPI: 300
- Anchor Templates: TL, TR, BL, BR
- Detection Method: Template matching with contour refinement

### Step 2: Align and Crop
- Crop Strategy: Outward margin 0.125 inches (37.5px)
- Expected Dimensions: 2267×2813px
- Alignment Method: Homography transformation

### Step 3: Extract Text
- OCR Engine: Tesseract
- Language: eng
- PSM Mode: 6

## Execution Log

### Step 1: Find Anchors
**Status**: ⏳ Pending

### Step 2: Align and Crop
**Status**: ⏳ Pending

### Step 3: Extract Text
**Status**: ⏳ Pending

## Validation Results

*To be completed after processing*

## Issues and Resolutions

*Document any issues encountered*

## Changes from Standard Process

*Document any deviations*

## Quality Assessment

*To be completed after validation*

---

**Prepared by**: [Your Name]
**Date**: {date_str}
**Last Updated**: {date_str}
"""
    
    readme_file = run_dir / "README.md"
    readme_file.write_text(readme_content)
    print(f"✅ Created README.md")


def create_notes_templates(run_dir: Path) -> None:
    """Create template files in notes/ directory."""
    
    notes_dir = run_dir / "notes"
    
    # ISSUES.md
    issues_content = f"""# Issues Log - {run_dir.name}

*Document problems encountered during processing*

## Issue #1: [Title]

**Date**: YYYY-MM-DD HH:MM
**Severity**: Critical / Major / Minor / Info
**Step**: Step 1 / Step 2 / Step 3
**Status**: Open / Resolved / Workaround

### Description
[Detailed description]

### Resolution
[How it was fixed]

---
"""
    (notes_dir / "ISSUES.md").write_text(issues_content)
    
    # CHANGES.md
    changes_content = f"""# Changes Log - {run_dir.name}

*Document modifications from standard process*

## Change #1: [Title]

**Date**: YYYY-MM-DD HH:MM
**Type**: Script / Parameter / Process
**Author**: [Your Name]

### Rationale
[Why this change was needed]

### Description
[What was changed]

---
"""
    (notes_dir / "CHANGES.md").write_text(changes_content)
    
    # VALIDATION.md
    validation_content = f"""# Validation Report - {run_dir.name}

## Validation Date
*To be completed*

## Anchor Detection Validation

*To be completed after Step 1*

## Cropping Validation

*To be completed after Step 2*

## OCR Validation

*To be completed after Step 3*

---
"""
    (notes_dir / "VALIDATION.md").write_text(validation_content)
    
    # DATA_PROVENANCE.md
    provenance_content = f"""# Data Provenance - {run_dir.name}

## Source Information

**Supplier**: [Who provided the PDF?]
**Acquisition Date**: [When received?]
**Acquisition Method**: [Email / Upload / Scan / etc.]
**Scan Device**: [Scanner model if applicable]

## Data Sensitivity

**Contains PHI**: Yes / No
**Redaction Required**: Yes / No
**Compliance**: [HIPAA / GDPR / etc.]

## Processing History

**Original Filename**: [Original name]
**File Hash (SHA256)**: [Hash]
**Preprocessing**: [Any preprocessing done]

---
"""
    (notes_dir / "DATA_PROVENANCE.md").write_text(provenance_content)
    
    # RETENTION.md
    retention_content = f"""# Retention Policy - {run_dir.name}

## Backup Information

**Primary Location**: `{run_dir}`
**Backup Location**: [S3 / Azure / GCP path]
**Backup Date**: [When backed up]

## Encryption

**At Rest**: [KMS key / encryption method]
**In Transit**: [TLS version]

## Retention Schedule

**Duration**: [How long to keep]
**Purge Date**: [When to delete]
**Purge Method**: [Secure deletion method]

## Access Control

**Who has access**: [List users/roles]
**Access log location**: [Where access is logged]

---
"""
    (notes_dir / "RETENTION.md").write_text(retention_content)
    
    print("✅ Created note templates")


def initialize_run(
    run_id: Optional[str] = None,
    template: str = "crc_survey_l_anchors_v1",
    input_file: Optional[Path] = None
) -> Path:
    """
    Initialize a complete run directory with all required structure.
    
    Args:
        run_id: Optional run ID (default: run_YYYYMMDD_HHMMSS)
        template: Template name
        input_file: Input PDF file to copy
        
    Returns:
        Path to created run directory
    """
    
    # Create run directory
    if run_id is None:
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    run_dir = artifacts_dir / run_id
    
    if run_dir.exists():
        print(f"⚠️  Run directory already exists: {run_dir}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(0)
    
    print(f"\n{'='*60}")
    print(f"INITIALIZING RUN: {run_id}")
    print(f"{'='*60}\n")
    
    # Create structure
    create_run_structure(run_dir)
    
    # Copy input file if provided
    if input_file and input_file.exists():
        shutil.copy2(input_file, run_dir / "input" / input_file.name)
        print(f"✅ Copied input file: {input_file.name}")
    
    # Archive scripts
    archive_scripts(run_dir)
    
    # Capture environment
    capture_environment(run_dir)
    
    # Snapshot configs
    config_checksums = snapshot_configs(run_dir, template)
    
    # Create manifest
    create_manifest(run_dir, template, config_checksums, input_file)
    
    # Create README
    create_readme(run_dir, template)
    
    # Create note templates
    create_notes_templates(run_dir)
    
    print(f"\n{'='*60}")
    print(f"✅ RUN INITIALIZED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"\nRun Directory: {run_dir}")
    print(f"\nNext steps:")
    print(f"1. Copy your PDF to: {run_dir}/input/")
    print(f"2. Run Step 1: python scripts/step1_find_anchors.py --run-dir {run_dir}")
    print(f"3. Run Step 2: python scripts/step2_align_and_crop.py --run-dir {run_dir}")
    print(f"4. Run Step 3: python scripts/step3_extract_text.py --run-dir {run_dir}")
    print(f"5. Validate: python scripts/qa_overlay_from_results.py {run_dir}")
    print(f"6. Generate metrics: python scripts/generate_metrics.py {run_dir}")
    print(f"\n{'='*60}\n")
    
    return run_dir


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Initialize a new processing run with complete documentation"
    )
    parser.add_argument(
        "--run-id",
        help="Run ID (default: run_YYYYMMDD_HHMMSS)"
    )
    parser.add_argument(
        "--template",
        default="crc_survey_l_anchors_v1",
        help="Template name"
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input PDF file to copy to run directory"
    )
    
    args = parser.parse_args()
    
    initialize_run(
        run_id=args.run_id,
        template=args.template,
        input_file=args.input
    )
