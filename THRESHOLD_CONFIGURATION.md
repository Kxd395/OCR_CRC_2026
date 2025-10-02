# Detection Threshold Configuration - Complete Guide

**Date**: October 2, 2025  
**Status**: ✅ **FULLY CONFIGURABLE AND INTEGRATED**

---

## 🎯 OVERVIEW

The detection threshold is now **fully configurable** with multiple levels of precedence, ensuring flexibility for different use cases while maintaining sensible defaults.

---

## 📊 THRESHOLD PRIORITY HIERARCHY

The system uses the following priority order (highest to lowest):

```
1. CLI Argument (--threshold)        [HIGHEST PRIORITY]
   ↓
2. Template detection_settings
   ↓
3. Config file (configs/ocr.yaml)
   ↓
4. Hardcoded default (11.5%)        [FALLBACK]
```

### Priority Explanation:

1. **CLI Argument**: Override everything (for testing/one-off runs)
2. **Template**: Document-specific calibration (per form type)
3. **Config File**: System-wide default
4. **Hardcoded**: Safety fallback

---

## ⚙️ CONFIGURATION LOCATIONS

### 1. Config File (System Default)

**File**: `configs/ocr.yaml`

```yaml
checkbox:
  fill_threshold: 0.115  # 11.5% - calibrated for light marks
  min_margin: 2
```

**Format**: Decimal (0.0 - 1.0)
**When to use**: Set your organization's standard threshold here
**Affects**: All runs unless overridden

### 2. Template (Document-Specific)

**File**: `templates/crc_survey_l_anchors_v1/template.json`

```json
{
  "version": "1.2.0",
  "detection_settings": {
    "fill_threshold_percent": 11.5,
    "method": "otsu",
    "description": "Calibrated for light checkbox marks"
  }
}
```

**Format**: Percentage (0 - 100)
**When to use**: Different form types need different thresholds
**Affects**: Runs using this template (unless CLI override)

### 3. CLI Argument (Runtime Override)

**Scripts**:
- `scripts/run_ocr.py --threshold 11.5`
- `scripts/export_to_excel.py --threshold 11.5`
- `wrapper/app.py --threshold 11.5`

**Format**: Percentage (0 - 100)
**When to use**: Testing, debugging, one-off adjustments
**Affects**: Only the current run

---

## 🚀 USAGE EXAMPLES

### Example 1: Using Wrapper with Custom Threshold

```bash
# Use 12% threshold instead of default
python3 wrapper/app.py \
  --pdf surveys.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --export results.xlsx \
  --threshold 12.0 \
  --notes "Testing 12% threshold"
```

**Flow**:
1. Wrapper passes `--threshold 12.0` to `run_ocr.py`
2. `run_ocr.py` uses 12% (0.12) for detection
3. Wrapper passes `--threshold 12.0` to `export_to_excel.py`
4. Excel report shows "Detection Threshold: 12.0%"
5. MANIFEST.json records threshold used

### Example 2: Using Wrapper with Template Default

```bash
# Use threshold from template (11.5%)
python3 wrapper/app.py \
  --pdf surveys.pdf \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --export results.xlsx
```

**Flow**:
1. No `--threshold` argument
2. `run_ocr.py` reads from template: 11.5%
3. `export_to_excel.py` reads from template: 11.5%
4. Consistent threshold throughout pipeline

### Example 3: Manual Script Execution

```bash
# Run OCR with specific threshold
python scripts/run_ocr.py \
  --template templates/crc_survey_l_anchors_v1/template.json \
  --threshold 10.5

# Export with matching threshold
python scripts/export_to_excel.py \
  artifacts/run_20251002_120000 \
  10.5
```

### Example 4: Testing Multiple Thresholds

```bash
# Compare results across thresholds
for threshold in 10.0 10.5 11.0 11.5 12.0 12.5; do
  python3 wrapper/app.py \
    --pdf test_survey.pdf \
    --template templates/crc_survey_l_anchors_v1/template.json \
    --export "exports/threshold_${threshold}.xlsx" \
    --threshold $threshold \
    --notes "Threshold testing: ${threshold}%"
done

# Compare the Excel reports to find optimal threshold
```

---

## 🔧 CHANGES MADE

### 1. Updated `configs/ocr.yaml`

**Before**:
```yaml
checkbox:
  fill_threshold: 0.55  # 55% - too high!
```

**After**:
```yaml
checkbox:
  fill_threshold: 0.115  # 11.5% - calibrated for light marks
```

### 2. Updated `scripts/run_ocr.py`

**Added**:
- `--threshold` CLI argument
- Priority logic: CLI > Template > Config > Default
- Console output: "Using fill threshold: 11.5%"

**Code**:
```python
ap.add_argument("--threshold", type=float, default=None,
               help="Checkbox fill threshold (0-100%). Overrides config/template.")

# Threshold priority: CLI arg > template > config > default
if args.threshold is not None:
    fill_th = args.threshold / 100.0  # Convert % to decimal
elif "detection_settings" in tpl and "fill_threshold_percent" in tpl["detection_settings"]:
    fill_th = tpl["detection_settings"]["fill_threshold_percent"] / 100.0
else:
    fill_th = float((cfg.get("checkbox") or {}).get("fill_threshold", 0.115))

print(f"Using fill threshold: {fill_th*100:.1f}%")
```

### 3. Updated `wrapper/app.py`

**Added**:
- Pass `--threshold` to `run_ocr.py` when specified
- Ensures consistent threshold across OCR detection and Excel export

**Code**:
```python
# Run OCR with optional threshold override
ocr_cmd = f"{sys.executable} scripts/run_ocr.py --template \"{args.template}\""
if args.threshold is not None:
    ocr_cmd += f" --threshold {args.threshold}"
d,_ = sh(ocr_cmd)
```

---

## 📋 VERIFICATION CHECKLIST

### ✅ Test 1: CLI Override Works
```bash
python scripts/run_ocr.py --template template.json --threshold 15.0
# Should output: "Using fill threshold: 15.0%"
```

### ✅ Test 2: Template Reading Works
```bash
# Remove --threshold argument
python scripts/run_ocr.py --template template.json
# Should output: "Using fill threshold: 11.5%" (from template)
```

### ✅ Test 3: Config Fallback Works
```bash
# Use template without detection_settings
python scripts/run_ocr.py --template old_template.json
# Should output: "Using fill threshold: 11.5%" (from config)
```

### ✅ Test 4: Wrapper Integration Works
```bash
python3 wrapper/app.py \
  --pdf test.pdf \
  --template template.json \
  --export test.xlsx \
  --threshold 12.5

# Verify in artifacts/run_*/MANIFEST.json:
# Should show threshold: 12.5 or similar metadata
```

### ✅ Test 5: End-to-End Consistency
```bash
# Run full pipeline
python3 wrapper/app.py \
  --pdf test.pdf \
  --template template.json \
  --export test.xlsx \
  --threshold 11.5

# Check Excel report - Summary sheet should show "Detection Threshold: 11.5%"
# Check artifacts/run_*/logs/ocr_results.json - checkbox scores should reflect 11.5%
```

---

## 🎓 BEST PRACTICES

### 1. **Set Organization Default**
```yaml
# configs/ocr.yaml
checkbox:
  fill_threshold: 0.115  # Your calibrated value
```

### 2. **Document-Specific Calibration**
```json
// templates/heavy_marks/template.json
{
  "detection_settings": {
    "fill_threshold_percent": 20.0,  // Heavier marks
    "description": "Survey filled with heavy pen marks"
  }
}

// templates/light_marks/template.json
{
  "detection_settings": {
    "fill_threshold_percent": 10.0,  // Light pencil marks
    "description": "Survey filled with light pencil"
  }
}
```

### 3. **Runtime Testing**
```bash
# Test threshold before production run
python3 wrapper/app.py --pdf sample.pdf --template template.json \
  --export test.xlsx --threshold 11.5

# Review Excel report, adjust if needed
python3 wrapper/app.py --pdf sample.pdf --template template.json \
  --export test2.xlsx --threshold 12.0

# Once satisfied, update template or config with optimal value
```

### 4. **Batch Processing with Different Thresholds**
```bash
# Light marks batch
python3 wrapper/app.py --pdf light_surveys.pdf --threshold 10.5 --export light_results.xlsx

# Heavy marks batch
python3 wrapper/app.py --pdf heavy_surveys.pdf --threshold 15.0 --export heavy_results.xlsx

# Normal marks batch (use template default)
python3 wrapper/app.py --pdf normal_surveys.pdf --export normal_results.xlsx
```

---

## 🔍 TROUBLESHOOTING

### Problem: "Too many false positives (empty boxes marked as filled)"

**Solution**: Increase threshold
```bash
# Current: 11.5%
# Try: 12.0%, 12.5%, 13.0%
python3 wrapper/app.py --pdf input.pdf --template template.json \
  --export output.xlsx --threshold 12.5
```

### Problem: "Missing filled checkboxes (not detecting light marks)"

**Solution**: Decrease threshold
```bash
# Current: 11.5%
# Try: 11.0%, 10.5%, 10.0%
python3 wrapper/app.py --pdf input.pdf --template template.json \
  --export output.xlsx --threshold 10.5
```

### Problem: "Inconsistent results between runs"

**Check**:
```bash
# 1. Check config file
cat configs/ocr.yaml | grep fill_threshold

# 2. Check template
cat templates/crc_survey_l_anchors_v1/template.json | grep fill_threshold

# 3. Check run logs
grep "Using fill threshold" artifacts/run_*/logs/*.log

# 4. Check MANIFEST.json for recorded threshold
cat artifacts/run_*/MANIFEST.json | grep threshold
```

### Problem: "Don't know which threshold was used"

**Solution**: Check multiple sources
```bash
# 1. Excel report Summary sheet shows threshold
open exports/results.xlsx

# 2. Terminal output from run_ocr.py
# Look for: "Using fill threshold: X.X%"

# 3. MANIFEST.json (if threshold was passed to wrapper)
cat artifacts/run_*/MANIFEST.json

# 4. OCR results JSON (checkbox scores)
cat artifacts/run_*/logs/ocr_results.json
```

---

## 📊 THRESHOLD TUNING GUIDE

### Step 1: Analyze Sample Data
```bash
# Identify filled checkboxes on representative pages
python scripts/identify_filled_checkboxes.py 0004 11.5
python scripts/identify_filled_checkboxes.py 0007 11.5
python scripts/identify_filled_checkboxes.py 0013 11.5
```

### Step 2: Review Fill Percentages
```
Empty boxes: 9.8% - 11.4%
Filled boxes: 11.5% - 40%+
```

### Step 3: Set Threshold
```
Threshold = max(empty) + small_margin
Example: 11.4% + 0.1% = 11.5%
```

### Step 4: Validate
```bash
# Test on full dataset
python3 wrapper/app.py --pdf all_surveys.pdf --template template.json \
  --export validation.xlsx --threshold 11.5

# Review Excel report
# - Check "near threshold" warnings
# - Spot-check pages with borderline fills
# - Adjust if needed
```

### Step 5: Update Configuration
```bash
# If 11.5% works well, update config:
# Edit configs/ocr.yaml → fill_threshold: 0.115

# Or update template:
# Edit template.json → detection_settings.fill_threshold_percent: 11.5

# Or continue using CLI argument for flexibility
```

---

## 📈 SUMMARY

| Aspect | Value |
|--------|-------|
| **Current Default** | 11.5% (0.115) |
| **Config File** | `configs/ocr.yaml` |
| **Template Field** | `detection_settings.fill_threshold_percent` |
| **CLI Format** | `--threshold 11.5` (percentage) |
| **Internal Format** | 0.0 - 1.0 (decimal) |
| **Priority** | CLI > Template > Config > Default |
| **Calibrated For** | Light checkbox marks (pencil/light pen) |
| **Range** | Empty: 9.8-11.4%, Filled: 11.5-40%+ |

---

## ✅ INTEGRATION COMPLETE

All threshold configuration is now:
- ✅ **Flexible**: Multiple configuration methods
- ✅ **Documented**: Clear priority hierarchy
- ✅ **Testable**: CLI override for experimentation
- ✅ **Auditable**: Threshold recorded in outputs
- ✅ **Production-Ready**: Sensible defaults, easy to tune

**Usage**:
```bash
# Standard production run (uses template/config default)
python3 wrapper/app.py --pdf input.pdf --template template.json --export output.xlsx

# Custom threshold run
python3 wrapper/app.py --pdf input.pdf --template template.json --export output.xlsx --threshold 12.0
```

---

*For questions about threshold selection, see `docs/DETECTION_THRESHOLD.md`*
