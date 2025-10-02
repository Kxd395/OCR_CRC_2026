#!/usr/bin/env python3
"""
Archive Scripts to Run Directory

Copies all scripts used in processing to the run directory for future reference.
This ensures we can always reproduce results and understand what code was run.

Usage:
    python scripts/archive_run_scripts.py <run_directory>
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

def archive_scripts(run_dir):
    """
    Copy all scripts to run directory for archival.
    
    Args:
        run_dir: Path to run directory
    """
    RUN_DIR = Path(run_dir)
    SCRIPTS_DIR = Path("scripts")
    ARCHIVE_DIR = RUN_DIR / "scripts_archive"
    
    # Create archive directory
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create manifest
    manifest = {
        "archived_at": datetime.now().isoformat(),
        "scripts": []
    }
    
    print("=" * 80)
    print("ARCHIVING SCRIPTS TO RUN DIRECTORY")
    print("=" * 80)
    print(f"\nRun directory: {run_dir}")
    print(f"Archive location: {ARCHIVE_DIR}\n")
    
    # Copy all Python scripts
    script_files = list(SCRIPTS_DIR.glob("*.py"))
    
    for script_file in sorted(script_files):
        dest = ARCHIVE_DIR / script_file.name
        shutil.copy2(script_file, dest)
        
        # Get file size
        size = script_file.stat().st_size
        
        manifest["scripts"].append({
            "name": script_file.name,
            "size_bytes": size,
            "original_path": str(script_file)
        })
        
        print(f"✅ Copied: {script_file.name} ({size:,} bytes)")
    
    # Copy configs
    configs_to_copy = [
        "configs/ocr.yaml",
        "configs/models.yaml",
        "templates/crc_survey_l_anchors_v1/template.json",
        "templates/crc_survey_l_anchors_v1/grid.json"
    ]
    
    print("\nCopying configuration files...")
    for config_path in configs_to_copy:
        config_file = Path(config_path)
        if config_file.exists():
            # Preserve directory structure
            relative_path = config_file.relative_to(".")
            dest = ARCHIVE_DIR / relative_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config_file, dest)
            
            size = config_file.stat().st_size
            manifest["scripts"].append({
                "name": str(relative_path),
                "size_bytes": size,
                "original_path": str(config_file)
            })
            
            print(f"✅ Copied: {relative_path} ({size:,} bytes)")
    
    # Save manifest
    import json
    manifest_file = ARCHIVE_DIR / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create README
    readme_content = f"""# Scripts Archive

This directory contains copies of all scripts and configurations used for this processing run.

**Archived:** {manifest['archived_at']}

## Purpose

Preserving these scripts ensures:
1. **Reproducibility** - Can rerun with exact same code
2. **Debugging** - Can review what code was actually executed
3. **Version tracking** - Know which algorithm version was used
4. **Documentation** - Understand processing decisions

## Contents

### Scripts ({len([s for s in manifest['scripts'] if s['name'].endswith('.py')])})
"""
    
    for script in sorted(manifest['scripts'], key=lambda x: x['name']):
        if script['name'].endswith('.py'):
            readme_content += f"- `{script['name']}` ({script['size_bytes']:,} bytes)\n"
    
    readme_content += f"\n### Configuration Files ({len([s for s in manifest['scripts'] if not s['name'].endswith('.py')])})\n"
    for script in sorted(manifest['scripts'], key=lambda x: x['name']):
        if not script['name'].endswith('.py'):
            readme_content += f"- `{script['name']}` ({script['size_bytes']:,} bytes)\n"
    
    readme_content += """
## Usage

To review what script was used:
```bash
cat scripts_archive/step2_align_and_crop.py
```

To compare with current version:
```bash
diff scripts_archive/step2_align_and_crop.py scripts/step2_align_and_crop.py
```

## Note

These are **snapshots** of the scripts at the time of processing.
Current versions in the main `scripts/` directory may have changed.
"""
    
    readme_file = ARCHIVE_DIR / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print("\n" + "=" * 80)
    print("ARCHIVE COMPLETE")
    print("=" * 80)
    print(f"Total files: {len(manifest['scripts'])}")
    print(f"Location: {ARCHIVE_DIR}")
    print(f"Manifest: {manifest_file}")
    print(f"README: {readme_file}")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/archive_run_scripts.py <run_directory>")
        print("Example: python scripts/archive_run_scripts.py artifacts/run_20251001_181157")
        sys.exit(1)
    
    run_dir = sys.argv[1]
    archive_scripts(run_dir)
