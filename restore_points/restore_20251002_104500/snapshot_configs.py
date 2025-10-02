#!/usr/bin/env python3
"""
Snapshot configuration files for a run to ensure exact reproducibility.

This script copies all config files and templates used by the processing
pipeline into the run directory and generates checksums for verification.
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def snapshot_configs(run_dir: Path, template_name: str = "crc_survey_l_anchors_v1") -> Dict[str, Any]:
    """
    Snapshot all configuration files for a run.
    
    Args:
        run_dir: Run directory path
        template_name: Name of template being used
        
    Returns:
        Dictionary of file paths and their checksums
    """
    snapshot_dir = run_dir / "configs_snapshot"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    project_root = Path(__file__).parent.parent
    checksums = {}
    
    print(f"Snapshotting configs to: {snapshot_dir}")
    
    # Template files
    template_dir = project_root / "templates" / template_name
    if template_dir.exists():
        for file_name in ["template.json", "grid.json"]:
            src = template_dir / file_name
            if src.exists():
                dst = snapshot_dir / f"template_{file_name}"
                shutil.copy2(src, dst)
                checksums[f"template_{file_name}"] = compute_sha256(dst)
                print(f"  ✅ Copied {file_name}")
    
    # Config files
    configs_dir = project_root / "configs"
    if configs_dir.exists():
        for config_file in ["ocr.yaml", "models.yaml"]:
            src = configs_dir / config_file
            if src.exists():
                dst = snapshot_dir / config_file
                shutil.copy2(src, dst)
                checksums[config_file] = compute_sha256(dst)
                print(f"  ✅ Copied {config_file}")
    
    # Write checksums file
    checksums_file = snapshot_dir / "checksums.txt"
    with open(checksums_file, "w") as f:
        for file_name, checksum in sorted(checksums.items()):
            f.write(f"{checksum}  {file_name}\n")
    
    print(f"  ✅ Wrote checksums.txt ({len(checksums)} files)")
    
    # Create snapshot metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "template_name": template_name,
        "files": checksums,
        "note": "Exact configs used for this run"
    }
    
    (snapshot_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2)
    )
    print(f"  ✅ Wrote metadata.json")
    
    return checksums


def compare_configs(run_a: Path, run_b: Path) -> Dict[str, Any]:
    """
    Compare config snapshots between two runs.
    
    Args:
        run_a: First run directory
        run_b: Second run directory
        
    Returns:
        Dictionary describing differences
    """
    snapshot_a = run_a / "configs_snapshot"
    snapshot_b = run_b / "configs_snapshot"
    
    if not snapshot_a.exists() or not snapshot_b.exists():
        return {"error": "One or both runs missing config snapshots"}
    
    # Load checksums
    checksums_a = {}
    checksums_b = {}
    
    if (snapshot_a / "checksums.txt").exists():
        for line in (snapshot_a / "checksums.txt").read_text().splitlines():
            checksum, filename = line.split(None, 1)
            checksums_a[filename] = checksum
    
    if (snapshot_b / "checksums.txt").exists():
        for line in (snapshot_b / "checksums.txt").read_text().splitlines():
            checksum, filename = line.split(None, 1)
            checksums_b[filename] = checksum
    
    # Compare
    all_files = set(checksums_a.keys()) | set(checksums_b.keys())
    
    differences = {
        "identical": [],
        "modified": [],
        "only_in_a": [],
        "only_in_b": []
    }
    
    for filename in sorted(all_files):
        checksum_a = checksums_a.get(filename)
        checksum_b = checksums_b.get(filename)
        
        if checksum_a and checksum_b:
            if checksum_a == checksum_b:
                differences["identical"].append(filename)
            else:
                differences["modified"].append(filename)
        elif checksum_a:
            differences["only_in_a"].append(filename)
        else:
            differences["only_in_b"].append(filename)
    
    return differences


def verify_checksums(run_dir: Path) -> bool:
    """
    Verify checksums of snapshot files.
    
    Args:
        run_dir: Run directory path
        
    Returns:
        True if all checksums match, False otherwise
    """
    snapshot_dir = run_dir / "configs_snapshot"
    checksums_file = snapshot_dir / "checksums.txt"
    
    if not checksums_file.exists():
        print(f"❌ No checksums file found")
        return False
    
    print(f"Verifying checksums in {snapshot_dir}...")
    
    all_valid = True
    for line in checksums_file.read_text().splitlines():
        expected_checksum, filename = line.split(None, 1)
        file_path = snapshot_dir / filename
        
        if not file_path.exists():
            print(f"  ❌ {filename}: File missing")
            all_valid = False
            continue
        
        actual_checksum = compute_sha256(file_path)
        if actual_checksum == expected_checksum:
            print(f"  ✅ {filename}: Valid")
        else:
            print(f"  ❌ {filename}: Checksum mismatch")
            print(f"     Expected: {expected_checksum}")
            print(f"     Actual:   {actual_checksum}")
            all_valid = False
    
    return all_valid


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Snapshot configuration files for a run"
    )
    parser.add_argument(
        "run_dir",
        type=Path,
        help="Run directory path"
    )
    parser.add_argument(
        "--template",
        default="crc_survey_l_anchors_v1",
        help="Template name (default: crc_survey_l_anchors_v1)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing checksums instead of creating snapshot"
    )
    parser.add_argument(
        "--compare",
        type=Path,
        help="Compare with another run directory"
    )
    
    args = parser.parse_args()
    
    if args.verify:
        # Verify existing checksums
        if verify_checksums(args.run_dir):
            print("\n✅ All checksums valid")
            sys.exit(0)
        else:
            print("\n❌ Some checksums invalid")
            sys.exit(1)
    
    elif args.compare:
        # Compare two runs
        differences = compare_configs(args.run_dir, args.compare)
        
        if "error" in differences:
            print(f"❌ {differences['error']}")
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"CONFIG COMPARISON")
        print(f"{'='*60}")
        print(f"Run A: {args.run_dir.name}")
        print(f"Run B: {args.compare.name}")
        print(f"{'='*60}\n")
        
        if differences["identical"]:
            print(f"✅ Identical ({len(differences['identical'])} files):")
            for filename in differences["identical"]:
                print(f"   - {filename}")
            print()
        
        if differences["modified"]:
            print(f"⚠️  Modified ({len(differences['modified'])} files):")
            for filename in differences["modified"]:
                print(f"   - {filename}")
            print()
        
        if differences["only_in_a"]:
            print(f"📁 Only in {args.run_dir.name} ({len(differences['only_in_a'])} files):")
            for filename in differences["only_in_a"]:
                print(f"   - {filename}")
            print()
        
        if differences["only_in_b"]:
            print(f"📁 Only in {args.compare.name} ({len(differences['only_in_b'])} files):")
            for filename in differences["only_in_b"]:
                print(f"   - {filename}")
            print()
        
        if differences["modified"] or differences["only_in_a"] or differences["only_in_b"]:
            print("⚠️  Configurations differ between runs")
            sys.exit(1)
        else:
            print("✅ Configurations identical")
            sys.exit(0)
    
    else:
        # Create snapshot
        checksums = snapshot_configs(args.run_dir, args.template)
        print(f"\n✅ Snapshot complete ({len(checksums)} files)")
