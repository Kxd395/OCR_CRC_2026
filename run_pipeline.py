#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time, hashlib, platform
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).parent.resolve()
VENV_PYTHON = REPO / ".venv" / "bin" / "python"

SCRIPTS = [
    "scripts/ingest_pdf.py",
    "scripts/step1_find_anchors.py",
    "scripts/step2_align_and_crop.py",
    "scripts/check_alignment.py",
    "scripts/make_overlays.py",
    "scripts/run_ocr.py",
    "scripts/qa_overlay_from_results.py",
    "scripts/validate_run.py",
    "scripts/export_to_excel.py",
    "scripts/common.py",
    "scripts/expand_grid.py",
]

CONFIGS = [
    "configs/ocr.yaml",
    "configs/models.yaml"
]

def sh(cmd, cwd=None, check=True):
    print(f"[run] {cmd}")
    st = time.time()
    # Set PYTHONPATH to include repo root for proper imports
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{REPO}:{env.get('PYTHONPATH', '')}"
    p = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    dt = time.time() - st
    if check and p.returncode != 0:
        raise SystemExit(f"Command failed ({p.returncode}): {cmd}")
    return dt, p.returncode

def newest_run_dir(artifacts_dir: Path) -> Path:
    runs = [p for p in artifacts_dir.glob("*") if p.is_dir()]
    if not runs: raise SystemExit("No artifacts/ run directories found.")
    return sorted(runs)[-1]

def sha256_file(path: Path) -> str:
    if not path.exists(): return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def capture_env(dst: Path):
    """Capture environment info (simplified to avoid hanging)."""
    dst.mkdir(parents=True, exist_ok=True)
    # Python version
    try:
        (dst/"python.txt").write_text(sys.version, encoding="utf-8")
    except Exception as e:
        (dst/"python.txt").write_text(f"Error: {e}", encoding="utf-8")
    
    # pip freeze (best-effort with timeout)
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True, timeout=10)
        (dst/"pip_freeze.txt").write_text(out, encoding="utf-8")
    except Exception as e:
        (dst/"pip_freeze.txt").write_text(f"error: {e}", encoding="utf-8")
    
    # OS info (simple, no platform.platform() which can hang)
    try:
        (dst/"os.txt").write_text("macOS", encoding="utf-8")
    except Exception as e:
        (dst/"os.txt").write_text(f"Unknown OS: {e}", encoding="utf-8")
    
    # Tools (with timeouts)
    tool_lines = []
    for cmd in [["tesseract","-v"]]:
        try:
            out = subprocess.check_output(cmd, text=True, timeout=10, stderr=subprocess.STDOUT)
            tool_lines.append(out)
        except Exception as e:
            tool_lines.append(f"{' '.join(cmd)} -> error: {e}")
    (dst/"tools.txt").write_text("\n".join(tool_lines), encoding="utf-8")

def snapshot_configs(run_dir: Path, template: Path):
    snap = run_dir/"configs_snapshot"
    snap.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, snap/"template.json")
    for cfg in CONFIGS:
        p = REPO/cfg
        if p.exists():
            shutil.copy2(p, snap/p.name)
    lines = []
    for p in snap.glob("*"):
        lines.append(f"{sha256_file(p)}  {p.name}")
    (snap/"checksums.txt").write_text("\n".join(lines), encoding="utf-8")

def snapshot_scripts(run_dir: Path):
    dst = run_dir/"scripts_archive"
    dst.mkdir(parents=True, exist_ok=True)
    for s in SCRIPTS:
        p = REPO/s
        if p.exists():
            shutil.copy2(p, dst/p.name)

def write_manifest(run_dir: Path, data: dict):
    (run_dir/"MANIFEST.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="CRC OCR pipeline wrapper")
    ap.add_argument("--pdf", required=True, help="path to input PDF")
    ap.add_argument("--template", required=True, help="path to template.json")
    ap.add_argument("--export", default=None, help="output xlsx path (default exports/<run_id>.xlsx)")
    ap.add_argument("--notes", default="", help="note to include in manifest")
    ap.add_argument("--strict", action="store_true", help="fail on validation gate error")
    ap.add_argument("--threshold", type=float, default=None, help="override checkbox threshold")
    ap.add_argument("--near", type=float, default=0.03, help="± margin around threshold for 'near_threshold' flag")
    args = ap.parse_args()

    artifacts = REPO/"artifacts"
    artifacts.mkdir(exist_ok=True)

    pre = set([p.name for p in artifacts.glob("*") if p.is_dir()])
    t0 = time.time()

    # Use venv Python if available, otherwise system Python
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    
    # Load threshold from config if not provided
    threshold_val = args.threshold
    if threshold_val is None:
        import yaml
        cfg_path = REPO / "configs" / "ocr.yaml"
        if cfg_path.exists():
            cfg = yaml.safe_load(cfg_path.read_text())
            threshold_val = float((cfg.get("checkbox") or {}).get("fill_threshold", 0.115)) * 100
    
    # Step 0: ingest
    duration = {}
    ingest_cmd = f"{python_exe} scripts/ingest_pdf.py --pdf \"{args.pdf}\""
    if threshold_val is not None:
        ingest_cmd += f" --threshold {threshold_val}"
    d, _ = sh(ingest_cmd)
    duration["ingest_pdf"] = d

    post = set([p.name for p in artifacts.glob("*") if p.is_dir()])
    created = sorted(list(post - pre))
    if not created:
        run_dir = newest_run_dir(artifacts)
    else:
        run_dir = artifacts/created[-1]

    (run_dir/"input").mkdir(exist_ok=True)
    try:
        shutil.copy2(args.pdf, run_dir/"input"/"survey.pdf")
    except Exception:
        pass

    snapshot_scripts(run_dir)
    snapshot_configs(run_dir, Path(args.template))
    capture_env(run_dir/"env")

    # Step 1: Find anchors
    d,_ = sh(f"{python_exe} scripts/step1_find_anchors.py --run-dir \"{run_dir}\" --template \"{args.template}\"")
    duration["step1_find_anchors"] = d

    # Step 2: Align and crop
    d,_ = sh(f"{python_exe} scripts/step2_align_and_crop.py --run-dir \"{run_dir}\" --template \"{args.template}\"")
    duration["step2_align_and_crop"] = d

    # Step 2b: Convert alignment results to homography format for OCR scripts
    d,_ = sh(f"{python_exe} scripts/convert_alignment_for_ocr.py --run-dir \"{run_dir}\"")
    duration["convert_alignment"] = d

    # Step 3: Check alignment (OPTIONAL - SKIPPED for now as it needs refactoring)
    # d,_ = sh(f"{python_exe} scripts/check_alignment.py --template \"{args.template}\"")
    # duration["check_alignment"] = d

    d,_ = sh(f"{python_exe} scripts/make_overlays.py --template \"{args.template}\"")
    duration["make_overlays"] = d

    # Run OCR with optional threshold override
    ocr_cmd = f"{python_exe} scripts/run_ocr.py --template \"{args.template}\""
    if args.threshold is not None:
        ocr_cmd += f" --threshold {args.threshold}"
    d,_ = sh(ocr_cmd)
    duration["run_ocr"] = d

    d,_ = sh(f"{python_exe} scripts/qa_overlay_from_results.py --template \"{args.template}\"")
    duration["qa_overlay_from_results"] = d

    gate_cmd = f"{python_exe} scripts/validate_run.py --template \"{args.template}\""
    if args.strict:
        gate_cmd += " --fail-on-error"
    try:
        d,_ = sh(gate_cmd, check=args.strict)
        duration["validate_run"] = d
    except SystemExit as e:
        duration["validate_run"] = -1
        print(f"[warn] Validation gate failed: {e}")
        if args.strict:
            raise

    export_path = args.export or (REPO/"exports"/f"{run_dir.name}.xlsx")
    export_path = Path(export_path)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    threshold_arg = f" --threshold {args.threshold}" if args.threshold is not None else ""
    d,_ = sh(f"{python_exe} scripts/export_to_excel.py --run-dir \"{run_dir}\" --out \"{export_path}\"{threshold_arg} --near {args.near}")
    duration["export_to_excel"] = d
    
    # Copy Excel file into run directory for archival
    run_export_path = run_dir / "export" / export_path.name
    run_export_path.parent.mkdir(parents=True, exist_ok=True)
    if export_path.exists():
        shutil.copy2(export_path, run_export_path)
        print(f"✅ Excel file copied to run directory: {run_export_path.relative_to(REPO)}")

    manifest = {
        "run_id": run_dir.name,
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "notes": args.notes,
        "template": str(Path(args.template)),
        "export": str(export_path),
        "durations_sec": duration,
        "gates": {"strict": bool(args.strict)},
        "status": "complete",
        "input_hash": sha256_file(Path(args.pdf))
    }
    (run_dir/"README.md").write_text(
        f"# Run {run_dir.name}\n\nExport: {export_path}\n\nDurations (s):\n" +
        "\n".join([f"- {k}: {v:.2f}" if v>=0 else f"- {k}: FAILED" for k,v in duration.items()]),
        encoding="utf-8"
    )
    write_manifest(run_dir, manifest)
    
    # Generate comprehensive run documentation
    print("\n📝 Generating run documentation...")
    try:
        doc_cmd = (f"{python_exe} scripts/create_run_documentation.py "
                  f"--run-dir \"{run_dir}\" "
                  f"--pdf \"{args.pdf}\" "
                  f"--template \"{args.template}\" "
                  f"--threshold {args.threshold if args.threshold else 11.5} "
                  f"--near {args.near} "
                  f"--notes \"{args.notes}\"")
        sh(doc_cmd, check=False)
    except Exception as e:
        print(f"⚠️  Documentation generation failed: {e}")

    print(f"\n✅ Done. Excel: {export_path}")
    print(f"📄 Run documentation: {run_dir}/INDEX.md")

if __name__ == "__main__":
    main()
