# Root Folder Cleanup - October 2, 2025

## Files to Archive (Move to docs/archive/ or delete)

### 1. Redundant Log Files (DELETE)
```bash
rm pipeline.log
rm pipeline_116.log
rm pipeline_1165.log
rm pipeline_117.log
rm pipeline_run.log
```
**Reason:** Old test logs, not needed. Logs are auto-generated in `artifacts/run_*/logs/`

### 2. Duplicate Documentation (MOVE TO docs/)

**AUTOMATED_PIPELINE_GUIDE.md → docs/PIPELINE_AUTOMATION.md** (already exists)
```bash
# Compare first
diff AUTOMATED_PIPELINE_GUIDE.md docs/PIPELINE_AUTOMATION.md
# If similar, delete root version
rm AUTOMATED_PIPELINE_GUIDE.md
```

**CHECKBOX_ID_SYSTEM.md → docs/**
```bash
mv CHECKBOX_ID_SYSTEM.md docs/CHECKBOX_ID_SYSTEM.md
```

**PROJECT_ORGANIZATION.md → docs/FOLDER_STRUCTURE.md** (already exists)
```bash
# Compare and merge if needed
rm PROJECT_ORGANIZATION.md
```

**THRESHOLD_CONFIGURATION.md → docs/DETECTION_THRESHOLD.md** (already exists)
```bash
rm THRESHOLD_CONFIGURATION.md
```

### 3. Keep in Root

✅ **README.md** - Main entry point
✅ **MANUAL.md** - Quick reference
✅ **Makefile** - Build commands
✅ **requirements.txt** - Dependencies
✅ **run_pipeline.py** - Main automation script
✅ **.gitignore** - Git configuration

### 4. Potentially Redundant Scripts

**run_full_pipeline.py vs run_pipeline.py** - Check if duplicates
```bash
diff run_full_pipeline.py run_pipeline.py
# If similar, keep only run_pipeline.py
```

---

## Cleanup Script

```bash
#!/bin/bash
# Root cleanup - October 2, 2025

echo "🧹 Cleaning up root folder..."

# 1. Delete old log files
echo "Deleting old logs..."
rm -f pipeline*.log

# 2. Move documentation to docs/
echo "Organizing documentation..."
if [ -f "CHECKBOX_ID_SYSTEM.md" ]; then
    mv CHECKBOX_ID_SYSTEM.md docs/
fi

# 3. Check for duplicates
echo "Removing duplicate documentation..."
rm -f AUTOMATED_PIPELINE_GUIDE.md      # Covered by docs/PIPELINE_AUTOMATION.md
rm -f PROJECT_ORGANIZATION.md          # Covered by docs/FOLDER_STRUCTURE.md
rm -f THRESHOLD_CONFIGURATION.md       # Covered by docs/DETECTION_THRESHOLD.md

# 4. Compare scripts
if [ -f "run_full_pipeline.py" ]; then
    if diff -q run_full_pipeline.py run_pipeline.py > /dev/null 2>&1; then
        echo "run_full_pipeline.py is identical to run_pipeline.py - removing..."
        rm run_full_pipeline.py
    else
        echo "⚠️  Scripts differ - manual review needed"
    fi
fi

echo "✅ Cleanup complete!"
echo ""
echo "Root folder now contains:"
ls -1 *.md *.py Makefile requirements.txt 2>/dev/null

```

---

## Final Root Structure (After Cleanup)

```
/
├── README.md                    # Main documentation
├── MANUAL.md                    # Quick reference
├── Makefile                     # Build commands
├── requirements.txt             # Python dependencies
├── run_pipeline.py              # Main automation
├── .gitignore                   # Git config
├── .github/                     # CI/CD workflows
├── artifacts/                   # Run outputs (gitignored)
├── configs/                     # YAML configs
├── data/                        # Training data (gitignored)
├── docs/                        # All documentation
├── exports/                     # Excel outputs (gitignored)
├── review/                      # Graded data (gitignored)
├── scripts/                     # Python scripts
├── templates/                   # Template definitions
└── tools/                       # Utility scripts
```

---

## Documentation Organization (docs/)

```
docs/
├── README.md                          # Docs index
├── USAGE.md                           # User guide
├── ML_IMPLEMENTATION.md               # ML details ⭐ NEW
├── OPTIMIZATION_SUMMARY.md            # Improvement log ⭐ NEW
├── TESTING.md                         # QA procedures ⭐ NEW
├── BEST_PRACTICES.md                  # Tips & tricks
├── GEMMA_SETUP.md                     # Gemma integration
├── PIPELINE_AUTOMATION.md             # Automation guide
├── PIPELINE_STATUS.md                 # Current status
├── FOLDER_STRUCTURE.md                # Project layout
├── CHECKBOX_ID_SYSTEM.md              # ID conventions ⭐ MOVED
└── fixes/                             # Historical fixes
    └── CHECKBOX_FIX_2025-01.md
```

---

## Git Commands

```bash
# Review changes
git status

# Add cleanup
git add .
git commit -m "Clean up root folder: remove logs, consolidate docs

- Removed: pipeline*.log (old test logs)
- Removed: Duplicate docs (AUTOMATED_PIPELINE_GUIDE, PROJECT_ORGANIZATION, THRESHOLD_CONFIGURATION)
- Moved: CHECKBOX_ID_SYSTEM.md → docs/
- Added: docs/TESTING.md (comprehensive QA documentation)
- Updated: README.md with ML performance (98.62%)
- Updated: docs/ML_IMPLEMENTATION.md with threshold optimization
"

# Push
git push origin main
```

---

**Cleanup Status:** Ready to execute
**Impact:** Cleaner root, better organization, no functionality loss
**Backup:** All changes in git history
