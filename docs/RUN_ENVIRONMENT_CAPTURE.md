# Run Environment Capture Guide

## Overview

Capturing the complete environment for each run ensures reproducibility, auditability, and debugging capability. This guide covers automated environment snapshot generation.

## Directory Structure

```
artifacts/run_YYYYMMDD_HHMMSS/
└── env/
    ├── python.txt           # Python version
    ├── pip_freeze.txt       # Exact package versions
    ├── os.txt               # Operating system info
    ├── tools.txt            # External tool versions
    ├── locale.txt           # Locale settings
    ├── hardware.json        # Hardware specifications
    └── checksums.txt        # Environment snapshot checksums
```

## Automated Environment Capture Script

Save this as `scripts/capture_environment.sh`:

```bash
#!/bin/bash
# Capture complete environment for a processing run

RUN_DIR="${1:-artifacts/run_$(date +%Y%m%d_%H%M%S)}"
ENV_DIR="$RUN_DIR/env"

echo "Capturing environment to: $ENV_DIR"
mkdir -p "$ENV_DIR"

# Python version
python --version > "$ENV_DIR/python.txt" 2>&1

# Exact package versions (frozen)
pip freeze > "$ENV_DIR/pip_freeze.txt"

# Operating system
if command -v uname &> /dev/null; then
    uname -a > "$ENV_DIR/os.txt" 2>&1
elif command -v sw_vers &> /dev/null; then
    sw_vers > "$ENV_DIR/os.txt" 2>&1
    system_profiler SPSoftwareDataType >> "$ENV_DIR/os.txt" 2>&1
fi

# External tools
{
    echo "=== Tesseract ==="
    tesseract --version 2>&1 || echo "Not installed"
    echo ""
    echo "=== Poppler ==="
    pdftoppm -v 2>&1 || echo "Not installed"
    pdfinfo -v 2>&1 || echo "Not installed"
    echo ""
    echo "=== OpenCV ==="
    python -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>&1 || echo "Not installed"
    echo ""
    echo "=== pdf2image ==="
    python -c "import pdf2image; print(f'pdf2image: {pdf2image.__version__}')" 2>&1 || echo "Not installed"
    echo ""
    echo "=== NumPy ==="
    python -c "import numpy; print(f'NumPy: {numpy.__version__}')" 2>&1 || echo "Not installed"
} > "$ENV_DIR/tools.txt"

# Locale settings
{
    echo "LANG: ${LANG:-not set}"
    echo "LC_ALL: ${LC_ALL:-not set}"
    echo "LC_CTYPE: ${LC_CTYPE:-not set}"
} > "$ENV_DIR/locale.txt"

# Hardware specifications
python - <<'PY' > "$ENV_DIR/hardware.json"
import json
import os
import platform
import sys

hardware = {
    "platform": platform.platform(),
    "python_version": sys.version,
    "cpu_count": os.cpu_count(),
    "architecture": platform.machine(),
    "processor": platform.processor()
}

# Try to get memory info
try:
    import psutil
    mem = psutil.virtual_memory()
    hardware["memory_total_gb"] = round(mem.total / 1e9, 2)
    hardware["memory_available_gb"] = round(mem.available / 1e9, 2)
except ImportError:
    hardware["memory_note"] = "Install psutil for memory info"

# Try to get GPU info
try:
    import cv2
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        hardware["gpu_cuda_devices"] = cv2.cuda.getCudaEnabledDeviceCount()
    else:
        hardware["gpu_cuda_devices"] = 0
except:
    hardware["gpu_cuda_devices"] = 0

print(json.dumps(hardware, indent=2))
PY

# Generate checksums of environment files
if command -v shasum &> /dev/null; then
    shasum -a 256 "$ENV_DIR"/*.txt "$ENV_DIR"/*.json 2>/dev/null > "$ENV_DIR/checksums.txt"
elif command -v sha256sum &> /dev/null; then
    sha256sum "$ENV_DIR"/*.txt "$ENV_DIR"/*.json 2>/dev/null > "$ENV_DIR/checksums.txt"
fi

echo "✅ Environment captured successfully"
echo "Files created:"
ls -lh "$ENV_DIR"
```

Make it executable:

```bash
chmod +x scripts/capture_environment.sh
```

## Python-based Environment Capture

Alternative: `scripts/capture_environment.py`:

```python
#!/usr/bin/env python3
"""Capture complete environment for a processing run."""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


def capture_environment(run_dir: Path) -> None:
    """Capture complete environment to run directory."""
    env_dir = run_dir / "env"
    env_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Capturing environment to: {env_dir}")
    
    # Python version
    (env_dir / "python.txt").write_text(
        f"Python {sys.version}\n"
        f"Executable: {sys.executable}\n"
    )
    
    # Exact package versions
    pip_freeze = run_command([sys.executable, "-m", "pip", "freeze"])
    (env_dir / "pip_freeze.txt").write_text(pip_freeze)
    
    # Operating system
    os_info = [
        f"System: {platform.system()}",
        f"Release: {platform.release()}",
        f"Version: {platform.version()}",
        f"Machine: {platform.machine()}",
        f"Processor: {platform.processor()}",
    ]
    (env_dir / "os.txt").write_text("\n".join(os_info))
    
    # External tools
    tools_info = []
    
    # Tesseract
    tools_info.append("=== Tesseract ===")
    tools_info.append(run_command(["tesseract", "--version"]))
    
    # Poppler
    tools_info.append("\n=== Poppler ===")
    tools_info.append(run_command(["pdftoppm", "-v"]))
    tools_info.append(run_command(["pdfinfo", "-v"]))
    
    # Python packages
    tools_info.append("\n=== Python Packages ===")
    try:
        import cv2
        tools_info.append(f"OpenCV: {cv2.__version__}")
    except ImportError:
        tools_info.append("OpenCV: Not installed")
    
    try:
        import pytesseract
        tools_info.append(f"pytesseract: {pytesseract.__version__}")
        tools_info.append(f"Tesseract version: {pytesseract.get_tesseract_version()}")
    except ImportError:
        tools_info.append("pytesseract: Not installed")
    
    try:
        import pdf2image
        tools_info.append(f"pdf2image: {pdf2image.__version__}")
    except ImportError:
        tools_info.append("pdf2image: Not installed")
    
    try:
        import numpy
        tools_info.append(f"NumPy: {numpy.__version__}")
    except ImportError:
        tools_info.append("NumPy: Not installed")
    
    (env_dir / "tools.txt").write_text("\n".join(tools_info))
    
    # Locale settings
    locale_info = [
        f"LANG: {os.environ.get('LANG', 'not set')}",
        f"LC_ALL: {os.environ.get('LC_ALL', 'not set')}",
        f"LC_CTYPE: {os.environ.get('LC_CTYPE', 'not set')}",
    ]
    (env_dir / "locale.txt").write_text("\n".join(locale_info))
    
    # Hardware specifications
    hardware = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.platform(),
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }
    
    # Memory info
    try:
        import psutil
        mem = psutil.virtual_memory()
        hardware["memory_total_gb"] = round(mem.total / 1e9, 2)
        hardware["memory_available_gb"] = round(mem.available / 1e9, 2)
        hardware["memory_percent_used"] = mem.percent
    except ImportError:
        hardware["memory_note"] = "Install psutil for memory info"
    
    # GPU info
    try:
        import cv2
        cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
        hardware["gpu_cuda_devices"] = cuda_devices
        if cuda_devices > 0:
            hardware["gpu_cuda_available"] = True
    except:
        hardware["gpu_cuda_devices"] = 0
        hardware["gpu_cuda_available"] = False
    
    (env_dir / "hardware.json").write_text(
        json.dumps(hardware, indent=2)
    )
    
    # Generate checksums
    import hashlib
    checksums = []
    for file_path in env_dir.glob("*.txt"):
        sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
        checksums.append(f"{sha256}  {file_path.name}")
    for file_path in env_dir.glob("*.json"):
        sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
        checksums.append(f"{sha256}  {file_path.name}")
    
    (env_dir / "checksums.txt").write_text("\n".join(checksums))
    
    print("✅ Environment captured successfully")
    print("\nFiles created:")
    for file_path in sorted(env_dir.iterdir()):
        size = file_path.stat().st_size
        print(f"  {file_path.name:20s} {size:>8,d} bytes")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_dir = Path(sys.argv[1])
    else:
        run_dir = Path("artifacts") / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    capture_environment(run_dir)
```

## Usage in Pipeline

Add to the beginning of your processing pipeline:

```bash
# At the start of processing
RUN_DIR="artifacts/run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RUN_DIR"

# Capture environment
./scripts/capture_environment.sh "$RUN_DIR"

# Continue with normal processing
python scripts/step1_find_anchors.py --run-dir "$RUN_DIR"
# ... rest of pipeline
```

Or in Python:

```python
from scripts.capture_environment import capture_environment

run_dir = Path("artifacts") / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
run_dir.mkdir(parents=True, exist_ok=True)

# Capture environment first
capture_environment(run_dir)

# Continue with processing
```

## Environment Comparison

Compare environments between two runs:

```bash
#!/bin/bash
# scripts/compare_environments.sh

RUN_A="$1"
RUN_B="$2"

echo "=== Python Version Diff ==="
diff "$RUN_A/env/python.txt" "$RUN_B/env/python.txt" || echo "No differences"

echo -e "\n=== Package Diff ==="
diff "$RUN_A/env/pip_freeze.txt" "$RUN_B/env/pip_freeze.txt" || echo "No differences"

echo -e "\n=== OS Diff ==="
diff "$RUN_A/env/os.txt" "$RUN_B/env/os.txt" || echo "No differences"

echo -e "\n=== Tools Diff ==="
diff "$RUN_A/env/tools.txt" "$RUN_B/env/tools.txt" || echo "No differences"

echo -e "\n=== Hardware Diff ==="
python - <<'PY'
import json, sys
with open(f"{sys.argv[1]}/env/hardware.json") as f: hw_a = json.load(f)
with open(f"{sys.argv[2]}/env/hardware.json") as f: hw_b = json.load(f)
for key in set(hw_a.keys()) | set(hw_b.keys()):
    val_a = hw_a.get(key, "N/A")
    val_b = hw_b.get(key, "N/A")
    if val_a != val_b:
        print(f"{key}:")
        print(f"  A: {val_a}")
        print(f"  B: {val_b}")
PY "$RUN_A" "$RUN_B"
```

## Validation Checklist

For each run, verify:

- [ ] `env/python.txt` exists and shows correct Python version
- [ ] `env/pip_freeze.txt` has all required packages
- [ ] `env/tools.txt` shows Tesseract, Poppler, OpenCV versions
- [ ] `env/hardware.json` has CPU, memory info
- [ ] `env/checksums.txt` validates all environment files

## Troubleshooting

**Missing psutil**: Install with `pip install psutil` for memory info

**Missing GPU info**: Install `opencv-contrib-python` for CUDA support

**Permission errors**: Ensure run directory is writable

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
