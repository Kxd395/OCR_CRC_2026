# Quick Restore Reference Card

**Restore Point**: `restore_20251002_104500`  
**Date**: October 2, 2025 @ 10:45  
**Status**: ✅ Production-Ready

---

## 🚀 Quick Restore (Full)

```bash
cd /Users/VScode_Projects/projects/crc_ocr_dropin
cp -r restore_points/restore_20251002_104500/scripts/ .
cp -r restore_points/restore_20251002_104500/templates/ .
cp -r restore_points/restore_20251002_104500/configs/ .
cp -r restore_points/restore_20251002_104500/docs/ .
cp restore_points/restore_20251002_104500/*.py .
echo "✅ Restored from restore_20251002_104500"
```

---

## 🎯 Restore Individual Components

### Restore One Script
```bash
cp restore_points/restore_20251002_104500/scripts/run_ocr.py scripts/
```

### Restore Template
```bash
cp restore_points/restore_20251002_104500/templates/crc_survey_l_anchors_v1/template.json \
   templates/crc_survey_l_anchors_v1/
```

### Restore Pipeline
```bash
cp restore_points/restore_20251002_104500/run_pipeline.py .
```

### Restore All Documentation
```bash
cp -r restore_points/restore_20251002_104500/docs/ .
```

---

## ✅ Verify Restore

```bash
# Check files exist
ls scripts/run_ocr.py templates/crc_survey_l_anchors_v1/template.json

# Verify checksums (optional)
shasum -a 256 scripts/make_overlays.py scripts/run_ocr.py

# Test pipeline
python3 run_pipeline.py --help
```

---

## 📦 What's Included

- ✅ All 40+ Python scripts (fixed versions)
- ✅ Templates with verified coordinates
- ✅ Complete documentation
- ✅ Pipeline files
- ✅ Configuration files

---

## 🔑 Key Working Values

```
Coordinates: X=[280,690,1100,1505,1915], Y=[1290,1585,1875,2150,2440]
Threshold: 11.5%
Cropped Size: 2267×2954
Last Successful Run: run_20251002_103645 (128 checkboxes, 26 pages)
```

---

## 📝 What Changed

- ✅ Fixed homography transformation (3 scripts)
- ✅ Created automated documentation system
- ✅ Excel files now archived in runs
- ✅ Organized all documentation
- ✅ 100% detection rate verified

---

## 🆘 Emergency Restore

If everything is broken:
```bash
cd /Users/VScode_Projects/projects/crc_ocr_dropin
rm -rf scripts/ templates/ configs/ docs/ *.py
cp -r restore_points/restore_20251002_104500/* .
echo "🔧 Emergency restore complete"
```

---

**Git Commit**: `59b0802d41ee3ef05e0d845d15d69cdd46cc416a`  
**Full Manifest**: `restore_points/restore_20251002_104500/RESTORE_POINT_MANIFEST.md`
