#!/usr/bin/env python3
"""
Complete OCR Pipeline Automation
==================================

This script runs the full OCR pipeline in the correct order, ensuring all steps
are executed properly with no steps skipped.

Pipeline Steps:
1. PDF Ingestion - Extract pages to images
2. Anchor Detection - Find alignment anchors (Step 1)
3. Alignment & Cropping - Warp and crop pages (Step 2)
4. Alignment Check - Verify homography
5. Create Overlays - Visual checkbox overlays
6. Run OCR - Detect filled checkboxes
7. QA Overlays - Visual verification of results
8. Validation - Check for errors
9. Export to Excel - Generate final report

Usage:
    python run_full_pipeline.py --pdf review/test_survey.pdf --template templates/crc_survey_l_anchors_v1/template.json
    
    # With custom threshold:
    python run_full_pipeline.py --pdf review/test_survey.pdf --template templates/crc_survey_l_anchors_v1/template.json --threshold 11.5
    
    # With custom output path:
    python run_full_pipeline.py --pdf review/test_survey.pdf --template templates/crc_survey_l_anchors_v1/template.json --export results/my_survey.xlsx
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import hashlib
import platform
from pathlib import Path
from datetime import datetime

# Repository root
REPO = Path(__file__).parent.resolve()

# Required scripts
REQUIRED_SCRIPTS = [
    "scripts/ingest_pdf.py",
    "scripts/step1_find_anchors.py",     # Step 1: Anchor detection
    "scripts/step2_align_and_crop.py",  # Step 2: Alignment and cropping
    "scripts/check_alignment.py",        # Verify alignment
    "scripts/make_overlays.py",
    "scripts/run_ocr.py",
    "scripts/qa_overlay_from_results.py",
    "scripts/validate_run.py",
    "scripts/export_to_excel.py",
]

# Config files to snapshot
CONFIGS = [
    "configs/ocr.yaml",
    "configs/models.yaml",
]


class Colors:
    """ANSI color codes for pretty terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(step_num: int, total: int, name: str):
    """Print a formatted step header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}STEP {step_num}/{total}: {name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")


def print_success(msg: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg: str):
    """Print an error message"""
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def print_warning(msg: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def run_command(cmd: str, cwd: Path = None, check: bool = True) -> tuple[float, int]:
    """
    Run a shell command and return (duration, exit_code)
    
    Args:
        cmd: Command to run
        cwd: Working directory (default: REPO)
        check: Raise exception on non-zero exit code
        
    Returns:
        Tuple of (duration_seconds, exit_code)
    """
    cwd = cwd or REPO
    print(f"{Colors.BLUE}[RUN]{Colors.ENDC} {cmd}")
    
    start = time.time()
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    duration = time.time() - start
    
    if check and result.returncode != 0:
        print_error(f"Command failed with exit code {result.returncode}")
        raise SystemExit(1)
    
    return duration, result.returncode


def find_latest_run(artifacts_dir: Path) -> Path:
    """Find the most recent run directory"""
    runs = [p for p in artifacts_dir.glob("run_*") if p.is_dir()]
    if not runs:
        raise FileNotFoundError("No run directories found in artifacts/")
    return sorted(runs)[-1]


def sha256_file(path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def capture_environment(run_dir: Path, python_exe: str):
    """Capture environment information (Python, packages, OS, tools)"""
    env_dir = run_dir / "env"
    env_dir.mkdir(parents=True, exist_ok=True)
    
    # Python version
    (env_dir / "python.txt").write_text(sys.version, encoding="utf-8")
    
    # pip freeze
    try:
        pip_output = subprocess.check_output(
            [python_exe, "-m", "pip", "freeze"],
            text=True
        )
        (env_dir / "pip_freeze.txt").write_text(pip_output, encoding="utf-8")
    except Exception as e:
        (env_dir / "pip_freeze.txt").write_text(f"Error: {e}", encoding="utf-8")
    
    # OS/Platform
    (env_dir / "os.txt").write_text(platform.platform(), encoding="utf-8")
    
    # Tools (OpenCV, Tesseract, etc.)
    tool_checks = []
    for cmd in [
        ["tesseract", "--version"],
        [python_exe, "-c", "import cv2; print('OpenCV:', cv2.__version__)"],
    ]:
        try:
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
            tool_checks.append(output)
        except Exception as e:
            tool_checks.append(f"{' '.join(cmd)} -> Error: {e}")
    
    (env_dir / "tools.txt").write_text("\n\n".join(tool_checks), encoding="utf-8")


def snapshot_configs(run_dir: Path, template_path: Path):
    """Create snapshots of config files and template"""
    snap_dir = run_dir / "configs_snapshot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template
    shutil.copy2(template_path, snap_dir / "template.json")
    
    # Copy config files
    for cfg_path in CONFIGS:
        cfg = REPO / cfg_path
        if cfg.exists():
            shutil.copy2(cfg, snap_dir / cfg.name)
    
    # Generate checksums
    checksums = []
    for file in snap_dir.glob("*"):
        if file.is_file():
            checksums.append(f"{sha256_file(file)}  {file.name}")
    
    (snap_dir / "checksums.txt").write_text("\n".join(checksums), encoding="utf-8")


def snapshot_scripts(run_dir: Path):
    """Create snapshots of all scripts used"""
    scripts_dir = run_dir / "scripts_archive"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    for script_path in REQUIRED_SCRIPTS:
        script = REPO / script_path
        if script.exists():
            shutil.copy2(script, scripts_dir / script.name)


def write_manifest(run_dir: Path, manifest_data: dict):
    """Write MANIFEST.json with run metadata"""
    manifest_path = run_dir / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest_data, indent=2, sort_keys=True),
        encoding="utf-8"
    )


def write_readme(run_dir: Path, export_path: Path, durations: dict):
    """Write README.md for the run"""
    readme_content = f"""# Run {run_dir.name}

## Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Export**: `{export_path}`

## Pipeline Steps

"""
    for step, duration in durations.items():
        if duration >= 0:
            readme_content += f"- ✅ {step}: {duration:.2f}s\n"
        else:
            readme_content += f"- ❌ {step}: FAILED\n"
    
    (run_dir / "README.md").write_text(readme_content, encoding="utf-8")


def get_python_executable() -> str:
    """Get the correct Python executable (prefer venv if available)"""
    venv_python = REPO / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return python_exe


def main():
    parser = argparse.ArgumentParser(
        description="Run the complete OCR pipeline from PDF to Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to input PDF file"
    )
    
    parser.add_argument(
        "--template",
        required=True,
        help="Path to template.json"
    )
    
    parser.add_argument(
        "--export",
        default=None,
        help="Output Excel path (default: exports/<run_id>.xlsx)"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Checkbox fill threshold percentage (default: from template/config)"
    )
    
    parser.add_argument(
        "--near",
        type=float,
        default=0.03,
        help="Margin around threshold for 'near' warnings (default: 0.03)"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail immediately on validation errors"
    )
    
    parser.add_argument(
        "--notes",
        default="",
        help="Notes to include in MANIFEST.json"
    )
    
    args = parser.parse_args()
    
    # Verify paths
    pdf_path = Path(args.pdf)
    template_path = Path(args.template)
    
    if not pdf_path.exists():
        print_error(f"PDF not found: {pdf_path}")
        return 1
    
    if not template_path.exists():
        print_error(f"Template not found: {template_path}")
        return 1
    
    # Print header
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}")
    print("CRC OCR PIPELINE - FULL AUTOMATION")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    print(f"📄 PDF: {pdf_path}")
    print(f"📋 Template: {template_path}")
    if args.threshold:
        print(f"🎯 Threshold: {args.threshold}%")
    print()
    
    # Set up Python path
    os.environ["PYTHONPATH"] = f"{REPO}:{os.environ.get('PYTHONPATH', '')}"
    
    # Get correct Python executable
    python_exe = get_python_executable()
    print(f"🐍 Using Python: {python_exe}\n")
    
    artifacts_dir = REPO / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    # Track durations
    durations = {}
    total_steps = 9
    
    try:
        # STEP 1: Ingest PDF
        print_step(1, total_steps, "Ingest PDF")
        duration, _ = run_command(
            f'{python_exe} scripts/ingest_pdf.py --pdf "{pdf_path}"'
        )
        durations["1_ingest_pdf"] = duration
        print_success(f"PDF ingested in {duration:.2f}s")
        
        # Find the newly created run directory
        run_dir = find_latest_run(artifacts_dir)
        print(f"📁 Run directory: {run_dir.name}")
        
        # Copy PDF to run directory
        input_dir = run_dir / "input"
        input_dir.mkdir(exist_ok=True)
        shutil.copy2(pdf_path, input_dir / "survey.pdf")
        
        # Capture environment and configs
        print("📸 Capturing environment...")
        capture_environment(run_dir, python_exe)
        snapshot_configs(run_dir, template_path)
        snapshot_scripts(run_dir)
        
        # STEP 2: Find Anchors (Step 1)
        print_step(2, total_steps, "Find Anchors (Step 1)")
        step1_cmd = f'{python_exe} scripts/step1_find_anchors.py --run-dir "{run_dir}" --template "{template_path}"'
        duration, _ = run_command(step1_cmd)
        durations["2_find_anchors"] = duration
        print_success(f"Anchors found in {duration:.2f}s")
        
        # STEP 3: Align and Crop (Step 2)
        print_step(3, total_steps, "Align and Crop Pages (Step 2)")
        step2_cmd = f'{python_exe} scripts/step2_align_and_crop.py "{run_dir}"'
        duration, _ = run_command(step2_cmd)
        durations["3_align_and_crop"] = duration
        print_success(f"Pages aligned and cropped in {duration:.2f}s")
        
        # STEP 4: Check Alignment
        print_step(4, total_steps, "Verify Alignment")
        duration, _ = run_command(
            f'{python_exe} scripts/check_alignment.py --template "{template_path}"'
        )
        durations["4_check_alignment"] = duration
        print_success(f"Alignment verified in {duration:.2f}s")
        
        # STEP 5: Create Overlays
        print_step(5, total_steps, "Create Visual Overlays")
        duration, _ = run_command(
            f'{python_exe} scripts/make_overlays.py --template "{template_path}"'
        )
        durations["5_make_overlays"] = duration
        print_success(f"Overlays created in {duration:.2f}s")
        
        # STEP 6: Run OCR
        print_step(6, total_steps, "Run OCR Detection")
        ocr_cmd = f'{python_exe} scripts/run_ocr.py --template "{template_path}"'
        if args.threshold:
            ocr_cmd += f" --threshold {args.threshold}"
        duration, _ = run_command(ocr_cmd)
        durations["6_run_ocr"] = duration
        print_success(f"OCR completed in {duration:.2f}s")
        
        # STEP 7: QA Overlays
        print_step(7, total_steps, "Generate QA Overlays")
        duration, _ = run_command(
            f'{python_exe} scripts/qa_overlay_from_results.py --template "{template_path}"'
        )
        durations["7_qa_overlays"] = duration
        print_success(f"QA overlays generated in {duration:.2f}s")
        
        # STEP 8: Validation
        print_step(8, total_steps, "Validate Results")
        validate_cmd = f'{python_exe} scripts/validate_run.py --template "{template_path}"'
        if args.strict:
            validate_cmd += " --fail-on-error"
        try:
            duration, _ = run_command(validate_cmd, check=args.strict)
            durations["8_validation"] = duration
            print_success(f"Validation completed in {duration:.2f}s")
        except SystemExit:
            durations["8_validation"] = -1
            print_warning("Validation failed")
            if args.strict:
                raise
        
        # STEP 9: Export to Excel
        print_step(9, total_steps, "Export to Excel")
        
        # Determine export path
        export_path = args.export or (REPO / "exports" / f"{run_dir.name}.xlsx")
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_cmd = f'{python_exe} scripts/export_to_excel.py --run-dir "{run_dir}" --out "{export_path}"'
        if args.threshold:
            export_cmd += f" --threshold {args.threshold}"
        export_cmd += f" --near {args.near}"
        
        duration, _ = run_command(export_cmd)
        durations["9_export_excel"] = duration
        print_success(f"Excel exported in {duration:.2f}s")
        
        # Write manifest and README
        manifest = {
            "run_id": run_dir.name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pdf": str(pdf_path),
            "template": str(template_path),
            "export": str(export_path),
            "threshold": args.threshold,
            "near_margin": args.near,
            "strict_mode": args.strict,
            "notes": args.notes,
            "durations_sec": durations,
        }
        write_manifest(run_dir, manifest)
        write_readme(run_dir, export_path, durations)
        
        # Final summary
        total_time = sum(d for d in durations.values() if d >= 0)
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}")
        print("✅ PIPELINE COMPLETE!")
        print(f"{'='*70}{Colors.ENDC}\n")
        print(f"📊 Excel Report: {Colors.BOLD}{export_path}{Colors.ENDC}")
        print(f"📁 Run Directory: {Colors.BOLD}{run_dir}{Colors.ENDC}")
        print(f"⏱️  Total Time: {Colors.BOLD}{total_time:.2f}s{Colors.ENDC}")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print_error("\nPipeline interrupted by user")
        return 130
    except Exception as e:
        print_error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
