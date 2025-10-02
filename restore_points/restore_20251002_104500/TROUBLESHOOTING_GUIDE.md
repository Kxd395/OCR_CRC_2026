# Troubleshooting Guide

## Overview

This guide covers common issues encountered in the CRC OCR Pipeline, their symptoms, root causes, and solutions.

## Quick Diagnostic Commands

```bash
# Check Python environment
python --version
pip list | grep -E "opencv|pytesseract|pdf2image"

# Check Tesseract installation
tesseract --version

# Check OpenCV installation
python -c "import cv2; print(cv2.__version__)"

# Validate run structure
ls -la artifacts/run_YYYYMMDD_HHMMSS/

# Check last processing logs
tail -n 50 artifacts/run_YYYYMMDD_HHMMSS/*.log
```

## Issue Categories

1. [Environment Setup Issues](#environment-setup-issues)
2. [Anchor Detection Problems](#anchor-detection-problems)
3. [Alignment and Cropping Issues](#alignment-and-cropping-issues)
4. [OCR Extraction Problems](#ocr-extraction-problems)
5. [Performance Issues](#performance-issues)
6. [File and Path Issues](#file-and-path-issues)

---

## Environment Setup Issues

### Issue: ModuleNotFoundError: No module named 'cv2'

**Symptoms**:
```
ModuleNotFoundError: No module named 'cv2'
```

**Root Cause**: OpenCV not installed or not in Python path

**Solution**:
```bash
pip install opencv-python
# Verify installation
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

**Prevention**: Always activate virtual environment before running scripts

---

### Issue: pytesseract.TesseractNotFoundError

**Symptoms**:
```
pytesseract.pytesseract.TesseractNotFoundError: tesseract is not installed
```

**Root Cause**: Tesseract OCR engine not installed on system

**Solution**:

macOS:
```bash
brew install tesseract
```

Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

Windows:
```powershell
# Download installer from GitHub
# https://github.com/UB-Mannheim/tesseract/wiki
```

**Verification**:
```bash
tesseract --version
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

**Prevention**: Include Tesseract in environment setup checklist

---

### Issue: poppler not found (pdf2image error)

**Symptoms**:
```
PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?
```

**Root Cause**: Poppler utilities not installed

**Solution**:

macOS:
```bash
brew install poppler
```

Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils
```

Windows:
```powershell
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Add to PATH
```

**Verification**:
```bash
pdftoppm -v
pdfinfo -v
```

---

## Anchor Detection Problems

### Issue: No anchors detected on page

**Symptoms**:
- `anchor_log.json` shows empty arrays for some corners
- Error message: "Could not find anchor for corner TL on page 5"

**Root Cause**:
1. Low quality scan
2. Anchors obscured or damaged
3. Detection threshold too strict
4. Wrong template

**Diagnostic Steps**:
```bash
# Check anchor detection output
python scripts/step1_find_anchors.py --run-dir artifacts/run_YYYYMMDD_HHMMSS --debug

# Visual inspection
open artifacts/run_YYYYMMDD_HHMMSS/step1_anchors/page_01.png
```

**Solution 1**: Adjust detection threshold
```python
# In step1_find_anchors.py
DETECTION_THRESHOLD = 0.6  # Lower from default 0.7
```

**Solution 2**: Check template quality
```bash
# Verify templates exist and are correct size
ls -lh templates/crc_survey_l_anchors_v1/*.png
```

**Solution 3**: Manual anchor placement
```python
# Edit anchor_log.json manually
{
  "page_05": {
    "TL": {"x": 98, "y": 95, "confidence": 0.0, "area": 0},
    "TR": {"x": 2182, "y": 95, "confidence": 0.0, "area": 0},
    "BL": {"x": 98, "y": 2377, "confidence": 0.0, "area": 0},
    "BR": {"x": 2182, "y": 2377, "confidence": 0.0, "area": 0}
  }
}
```

**Prevention**: Pre-scan PDFs for quality before processing

---

### Issue: Non-deterministic anchor detection

**Symptoms**:
- Same PDF produces different anchor coordinates on different runs
- Slight variations in detected positions (±5px)

**Root Cause**: Multiple candidate anchors with similar scores; non-deterministic tie-breaking

**Diagnostic Steps**:
```bash
# Compare anchor logs from two runs
diff artifacts/run_A/step1_anchors/anchor_log.json \
     artifacts/run_B/step1_anchors/anchor_log.json
```

**Solution 1**: Copy known-good anchor log
```bash
# Use baseline run's anchors
cp artifacts/run_20251001_181157/step1_anchors/anchor_log.json \
   artifacts/run_20251001_185300/step1_anchors/
```

**Solution 2**: Fix tie-breaking logic
```python
# In step1_find_anchors.py
# Sort candidates by composite score, then by distance to expected position
candidates.sort(key=lambda c: (
    -c['composite_score'],  # Higher score first
    abs(c['x'] - expected_x) + abs(c['y'] - expected_y)  # Then by distance
))
```

**Prevention**: Archive anchor logs from validated runs

---

### Issue: Anchor detected in wrong location

**Symptoms**:
- Cropped images misaligned
- Grid overlay shows systematic offset
- Anchor coordinates outside expected range

**Root Cause**:
1. False positive detection
2. Similar-looking artifacts on page
3. Detection algorithm picked wrong contour

**Diagnostic Steps**:
```bash
# Visual inspection with overlays
python scripts/qa_overlay_from_results.py artifacts/run_YYYYMMDD_HHMMSS

# Check detection confidence
jq '.page_01.TL.confidence' artifacts/run_YYYYMMDD_HHMMSS/step1_anchors/anchor_log.json
```

**Solution 1**: Increase detection threshold
```python
DETECTION_THRESHOLD = 0.8  # Stricter matching
```

**Solution 2**: Add spatial constraints
```python
# In step1_find_anchors.py
EXPECTED_POSITIONS = {
    'TL': (100, 100, 50),   # (x, y, tolerance)
    'TR': (2180, 100, 50),
    'BL': (100, 2375, 50),
    'BR': (2180, 2375, 50)
}

# Filter candidates outside expected region
def is_in_expected_region(x, y, corner):
    exp_x, exp_y, tol = EXPECTED_POSITIONS[corner]
    return abs(x - exp_x) <= tol and abs(y - exp_y) <= tol
```

**Solution 3**: Manual correction
```bash
# Edit anchor_log.json with correct coordinates
# Then rerun Step 2 and Step 3
```

**Prevention**: Implement spatial constraints in detection algorithm

---

## Alignment and Cropping Issues

### Issue: Cropped images have wrong dimensions

**Symptoms**:
- Expected: 2267×2813px
- Actual: Different dimensions

**Root Cause**:
1. Wrong cropping strategy (inward inset vs outward margin)
2. Incorrect margin calculation
3. Anchor positions off

**Diagnostic Steps**:
```bash
# Check actual dimensions
identify artifacts/run_YYYYMMDD_HHMMSS/step2_cropped/page_01.png

# Check expected dimensions in template
jq '.expected_dimensions' templates/crc_survey_l_anchors_v1/template.json
```

**Solution 1**: Verify cropping strategy
```python
# In step2_align_and_crop.py
# Should be outward margin, not inward inset
crop_region = compute_outward_margin(anchors, margin_inches=0.125)
```

**Solution 2**: Check margin calculation
```python
# At 300 DPI: 0.125 inches = 37.5 pixels
MARGIN_INCHES = 0.125
MARGIN_PX = MARGIN_INCHES * DPI  # Should be 37.5
```

**Solution 3**: Verify anchor positions
```bash
# Compare with baseline run
jq '.page_01' artifacts/run_baseline/step1_anchors/anchor_log.json
jq '.page_01' artifacts/run_current/step1_anchors/anchor_log.json
```

**Prevention**: Always validate dimensions after Step 2

---

### Issue: Grid overlay misaligned

**Symptoms**:
- `qa_overlay_from_results.py` shows grid lines not matching content
- Mean error > 2 pixels
- Visual inspection shows systematic offset

**Root Cause**:
1. Wrong anchor coordinates
2. Incorrect homography transformation
3. Template grid.json not matching actual form

**Diagnostic Steps**:
```bash
# Run validation
python scripts/qa_overlay_from_results.py artifacts/run_YYYYMMDD_HHMMSS

# Check validation metrics
cat artifacts/run_YYYYMMDD_HHMMSS/diagnostics/validation_report.json
```

**Solution 1**: Use baseline anchor log
```bash
cp artifacts/run_baseline/step1_anchors/anchor_log.json \
   artifacts/run_current/step1_anchors/
# Rerun Step 2
python scripts/step2_align_and_crop.py --run-dir artifacts/run_current
```

**Solution 2**: Adjust grid definition
```bash
# Edit templates/crc_survey_l_anchors_v1/grid.json
# Verify line positions match actual form
```

**Solution 3**: Compare with baseline
```bash
# Check cropped image differences
compare artifacts/run_baseline/step2_cropped/page_01.png \
        artifacts/run_current/step2_cropped/page_01.png \
        artifacts/diff_page_01.png
```

**Prevention**: Always validate against known-good baseline

---

### Issue: Transformation causes distortion

**Symptoms**:
- Cropped images appear skewed
- Text looks stretched or compressed
- Lines not straight

**Root Cause**:
1. Poor anchor detection (anchors not in corners)
2. Homography transformation inappropriate for simple affine case
3. Source image severely skewed

**Diagnostic Steps**:
```bash
# Visual inspection
open artifacts/run_YYYYMMDD_HHMMSS/step2_cropped/page_01.png

# Check anchor positions form rectangle
python -c "
import json
with open('artifacts/run_YYYYMMDD_HHMMSS/step1_anchors/anchor_log.json') as f:
    anchors = json.load(f)['page_01']
    print('TL:', anchors['TL'])
    print('TR:', anchors['TR'])
    print('BL:', anchors['BL'])
    print('BR:', anchors['BR'])
"
```

**Solution 1**: Use affine transformation instead
```python
# In step2_align_and_crop.py
# Replace cv2.getPerspectiveTransform with cv2.getAffineTransform
# Use only 3 anchor points
```

**Solution 2**: Re-scan source document
```bash
# If distortion is in source, no processing can fix it
# Re-scan with better alignment
```

**Prevention**: Check source PDF quality before processing

---

## OCR Extraction Problems

### Issue: Poor OCR accuracy

**Symptoms**:
- Extracted text has many errors
- Gibberish characters
- Missing text

**Root Cause**:
1. Low quality cropped images
2. Wrong Tesseract PSM mode
3. Wrong language setting
4. Image preprocessing needed

**Diagnostic Steps**:
```bash
# Check cropped image quality
identify -verbose artifacts/run_YYYYMMDD_HHMMSS/step2_cropped/page_01.png

# Test OCR on single image
tesseract artifacts/run_YYYYMMDD_HHMMSS/step2_cropped/page_01.png stdout
```

**Solution 1**: Adjust Tesseract PSM mode
```python
# In step3_extract_text.py
custom_config = r'--oem 3 --psm 6'  # Try different modes
# PSM 3: Fully automatic (default)
# PSM 4: Single column of text
# PSM 6: Uniform block of text
```

**Solution 2**: Add preprocessing
```python
# In step3_extract_text.py
import cv2

def preprocess_for_ocr(image):
    """Enhance image before OCR."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    # Threshold
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary
```

**Solution 3**: Increase DPI
```python
# In step1_find_anchors.py and step2_align_and_crop.py
DPI = 600  # Higher resolution for better OCR
```

**Prevention**: Validate OCR quality on sample pages before full run

---

### Issue: Missing text in grid cells

**Symptoms**:
- Some grid cells have empty or partial text
- Expected content not extracted

**Root Cause**:
1. Grid cell coordinates wrong
2. Text outside grid boundaries
3. OCR failed on specific region

**Diagnostic Steps**:
```bash
# Check grid overlay
open artifacts/run_YYYYMMDD_HHMMSS/diagnostics/grid_overlays/page_01.png

# Extract specific cell
python -c "
import cv2
img = cv2.imread('artifacts/run_YYYYMMDD_HHMMSS/step2_cropped/page_01.png')
cell = img[100:200, 100:300]  # Adjust coordinates
cv2.imwrite('cell_debug.png', cell)
"
tesseract cell_debug.png stdout
```

**Solution 1**: Adjust grid coordinates
```json
// In templates/crc_survey_l_anchors_v1/grid.json
{
  "rows": [100, 200, 300, ...],
  "cols": [100, 250, 400, ...]
}
```

**Solution 2**: Add padding to grid cells
```python
# In step3_extract_text.py
CELL_PADDING = 5  # pixels
x1 = col_start - CELL_PADDING
y1 = row_start - CELL_PADDING
x2 = col_end + CELL_PADDING
y2 = row_end + CELL_PADDING
```

**Solution 3**: Extract full page text instead
```python
# Fallback to full-page OCR if grid extraction fails
full_text = pytesseract.image_to_string(image)
```

**Prevention**: Validate grid definition against sample pages

---

## Performance Issues

### Issue: Processing very slow

**Symptoms**:
- Step 1 takes >5 minutes per page
- Step 2 takes >10 seconds per page
- Full run takes hours

**Root Cause**:
1. High DPI (>300)
2. Large PDF (>100 pages)
3. Inefficient processing
4. No parallelization

**Diagnostic Steps**:
```bash
# Profile script
python -m cProfile -o profile.stats scripts/step1_find_anchors.py
python -m pstats profile.stats
> sort time
> stats 10
```

**Solution 1**: Optimize DPI
```python
# Use 300 DPI instead of 600
DPI = 300  # Balance between quality and speed
```

**Solution 2**: Parallel processing
```python
# In step1_find_anchors.py
from multiprocessing import Pool

def process_page(page_num):
    # Process single page
    pass

with Pool(processes=4) as pool:
    results = pool.map(process_page, range(1, num_pages + 1))
```

**Solution 3**: Batch processing
```bash
# Process in chunks
python scripts/step1_find_anchors.py --pages 1-10
python scripts/step1_find_anchors.py --pages 11-20
```

**Solution 4**: Use GPU acceleration
```python
# OpenCV with CUDA support
import cv2
cv2.cuda.getCudaEnabledDeviceCount()  # Check GPU available
```

**Prevention**: Profile before processing large batches

---

### Issue: Out of memory errors

**Symptoms**:
```
MemoryError: Unable to allocate array
```

**Root Cause**:
1. Too many images in memory
2. High DPI images
3. Memory leak in loop

**Diagnostic Steps**:
```bash
# Monitor memory usage
python scripts/step1_find_anchors.py &
PID=$!
while kill -0 $PID 2>/dev/null; do
    ps -o rss= -p $PID
    sleep 5
done
```

**Solution 1**: Process page-by-page
```python
# Don't load all pages at once
for page_num in range(1, num_pages + 1):
    image = load_page(page_num)
    process_page(image)
    del image  # Free memory immediately
```

**Solution 2**: Reduce DPI
```python
DPI = 200  # Lower resolution if memory constrained
```

**Solution 3**: Use generators
```python
def page_generator(pdf_path):
    """Generate pages one at a time."""
    for page_num in range(1, num_pages + 1):
        yield load_page(page_num)

for image in page_generator(pdf_path):
    process_page(image)
```

**Prevention**: Monitor memory usage during development

---

## File and Path Issues

### Issue: FileNotFoundError: No such file or directory

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'templates/...'
```

**Root Cause**:
1. Wrong working directory
2. Relative path issue
3. Missing files

**Diagnostic Steps**:
```bash
# Check current directory
pwd

# Check file exists
ls -la templates/crc_survey_l_anchors_v1/template.json

# Check Python working directory
python -c "import os; print(os.getcwd())"
```

**Solution 1**: Use absolute paths
```python
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'templates', 'crc_survey_l_anchors_v1')
```

**Solution 2**: Run from project root
```bash
cd /Users/VScode_Projects/projects/crc_ocr_dropin
python scripts/step1_find_anchors.py
```

**Solution 3**: Set PYTHONPATH
```bash
export PYTHONPATH=/Users/VScode_Projects/projects/crc_ocr_dropin
```

**Prevention**: Always use absolute paths in production scripts

---

### Issue: Permission denied errors

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: 'artifacts/...'
```

**Root Cause**:
1. Insufficient file permissions
2. File open in another process
3. Directory not writable

**Diagnostic Steps**:
```bash
# Check permissions
ls -la artifacts/

# Check if file is locked
lsof artifacts/run_YYYYMMDD_HHMMSS/output.txt
```

**Solution 1**: Fix permissions
```bash
chmod -R 755 artifacts/
```

**Solution 2**: Close other processes
```bash
# Close any programs using the files
lsof | grep artifacts
```

**Solution 3**: Use different output directory
```python
# Write to temp directory first, then move
import tempfile
import shutil

with tempfile.TemporaryDirectory() as tmpdir:
    output_path = os.path.join(tmpdir, 'output.txt')
    # Write to output_path
    shutil.move(output_path, final_path)
```

**Prevention**: Check write permissions before starting processing

---

## Escalation Procedures

### When to Escalate

1. **Critical**: Production run failed, data loss risk
2. **Major**: Systematic issues affecting multiple runs
3. **Minor**: One-off issues with workarounds

### Escalation Checklist

- [ ] Documented symptoms and error messages
- [ ] Collected diagnostic outputs
- [ ] Tried documented solutions
- [ ] Identified impact and urgency
- [ ] Prepared reproduction steps
- [ ] Backed up affected data

### Contact Information

**Technical Lead**: [Name/Email]
**Team Channel**: [Slack/Teams channel]
**Issue Tracker**: [GitHub Issues URL]

---

## Appendix: Common Commands

### Validation
```bash
# Full validation
python scripts/qa_overlay_from_results.py artifacts/run_YYYYMMDD_HHMMSS

# Quick dimension check
identify artifacts/run_YYYYMMDD_HHMMSS/step2_cropped/*.png | grep "2267x2813"

# Anchor consistency check
jq '.page_01.TL' artifacts/run_*/step1_anchors/anchor_log.json
```

### Comparison
```bash
# Compare two runs
diff -r artifacts/run_A/step2_cropped/ artifacts/run_B/step2_cropped/

# Image comparison
compare -metric RMSE artifacts/run_A/step2_cropped/page_01.png \
                      artifacts/run_B/step2_cropped/page_01.png \
                      null: 2>&1
```

### Cleanup
```bash
# Remove failed run
rm -rf artifacts/run_YYYYMMDD_HHMMSS

# Clean intermediate files
find artifacts/ -name "*.log" -mtime +30 -delete
```

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
