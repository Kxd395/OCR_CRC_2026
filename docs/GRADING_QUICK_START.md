# Manual Grading System - Quick Reference

**Date**: October 2, 2025  
**Status**: ✅ Ready to use

---

## 🎯 What You Asked For

> "Can we add another column for the manual grading on what was correct and what was inaccurate. What's the best way to do that?"

**Answer**: ✅ **Done!** Added grading columns to **both** Excel files.

---

## 📊 Two Options for Grading

### Option 1: Detailed Results (Grade Everything)

**File**: `exports/run_XXXXXX_XXXXXX.xlsx` → Sheet: "Detailed Results"  
**Rows**: 223 (every checkbox)

**Added Columns** (G-K):
| Column | Purpose | Dropdown Options |
|--------|---------|------------------|
| G - Manual Review? | Flag items needing review | YES / NO |
| H - OCR Correct? | Grade OCR accuracy | CORRECT / INCORRECT / UNCERTAIN |
| I - Actual Status | What it really is (if OCR wrong) | Checked / Empty |
| J - Reviewer | Who reviewed this | (type your name) |
| K - Notes | Comments | (type your notes) |

### Option 2: Review Queue (Grade Only Problems)

**File**: `artifacts/run_XXXXXX_XXXXXX/review/review_queue.xlsx` → Sheet: "Queue"  
**Rows**: 26 (only pages with issues)

**Added Columns** (L-Q):
| Column | Purpose | Dropdown Options |
|--------|---------|------------------|
| L - reviewed | Have you reviewed this page? | YES / NO |
| M - ocr_accurate | Was OCR accurate? | CORRECT / INCORRECT / PARTIAL |
| N - corrected_conflicts | Document correct answers | (type corrections) |
| O - reviewer_name | Who reviewed | (type your name) |
| P - review_date | When reviewed | (type date) |
| Q - review_notes | Comments | (type notes) |

---

## 🚀 How to Use

### Quick Start (30 minutes)

1. **Open file**: 
   ```bash
   open artifacts/run_20251002_124257/review/review_queue.xlsx
   ```

2. **Go to "Queue" sheet**

3. **For each HIGH priority page**:
   - Read "details" column (tells you what's wrong)
   - Open QA overlay: `artifacts/run_*/step5_qa_overlays/page_XXXX.png`
   - Visually verify
   - Fill in columns L-Q

4. **Save file**

### Example Grading

**Page 1 has conflict in Q5**:

```
OCR Results (columns A-K):
  priority: HIGH
  page: page_0001.png
  details: Q5: Multiple selections (Q5_1, Q5_4)

Your Grading (columns L-Q):
  reviewed: YES
  ocr_accurate: CORRECT (both really are marked)
  corrected_conflicts: Q5_1 appears darker, likely intended
  reviewer_name: JD
  review_date: 2025-10-02
  review_notes: Both marked but Q5_1 darker
```

---

## 📈 Calculate Accuracy

After grading, you can calculate OCR accuracy:

```python
import pandas as pd

# Load graded file
df = pd.read_excel(
    "exports/test_with_grading_columns.xlsx", 
    sheet_name="Detailed Results"
)

# Filter to reviewed items
reviewed = df[df['OCR Correct?'].notna()]

# Calculate accuracy
correct = len(reviewed[reviewed['OCR Correct?'] == 'CORRECT'])
total = len(reviewed)
accuracy = (correct / total) * 100

print(f"Accuracy: {accuracy:.1f}%")
print(f"Correct: {correct}/{total}")
```

**Example output**:
```
Accuracy: 94.2%
Correct: 210/223
Incorrect: 8/223
Uncertain: 5/223

Most errors at 10.5-12.5% (near threshold)
```

---

## ✅ What This Enables

1. **Track accuracy** - Know how well OCR is performing
2. **Find patterns** - Identify systematic errors
3. **Improve pipeline** - Adjust threshold based on data
4. **Build training data** - Use corrections for ML
5. **Audit trail** - Document who reviewed what
6. **Quality control** - Multi-reviewer validation

---

## 🎯 Real-World Workflow

**Week 1**: Run pipeline, grade results, find accuracy is 92%  
**Week 2**: Notice errors at 11-12% range, adjust threshold  
**Week 3**: Re-run, grade again, accuracy improves to 96%  
**Week 4**: Use new threshold in production, continue monitoring

---

## 📂 Files Created/Updated

```
scripts/
├── export_to_excel.py           ← Added 5 grading columns (G-K)
└── build_review_queue.py        ← Added 6 grading columns (L-Q)

docs/
└── MANUAL_GRADING_GUIDE.md      ← Complete guide with examples

exports/
└── test_with_grading_columns.xlsx  ← Test file with grading columns

artifacts/run_20251002_124257/review/
└── review_queue.xlsx            ← Updated with grading columns
```

---

## 🚀 Test It Now

```bash
# Open the test file
open exports/test_with_grading_columns.xlsx

# Go to "Detailed Results" sheet
# See columns G-K (Manual Grading) in orange
# Try the dropdowns!
```

---

## 📚 Documentation

**Complete Guide**: `docs/MANUAL_GRADING_GUIDE.md`

Includes:
- Detailed column descriptions
- Grading scenarios and examples
- Best practices
- Accuracy calculation code
- Workflow recommendations

---

## ✨ Key Features

✅ **Dropdown menus** - No typing errors  
✅ **Color-coded** - OCR (blue) vs Manual (orange)  
✅ **Auto-flagging** - Near-threshold items highlighted  
✅ **Two options** - Grade everything or just issues  
✅ **Audit trail** - Reviewer name, date, notes  
✅ **Data analysis** - Calculate accuracy, find patterns  

---

**Status**: ✅ Fully implemented and tested  
**Ready**: Yes - use on next run immediately!

---

## Quick Examples

### Example 1: OCR Was Correct
```
H - OCR Correct?: CORRECT
I - Actual Status: (leave blank)
K - Notes: "Faint mark but real"
```

### Example 2: OCR Missed a Mark
```
H - OCR Correct?: INCORRECT
I - Actual Status: Checked
K - Notes: "Very light pencil, OCR threshold too high"
```

### Example 3: Can't Tell
```
H - OCR Correct?: UNCERTAIN
I - Actual Status: (leave blank)
K - Notes: "Scan quality too poor, needs rescan"
```

---

**Your question answered**: Yes! We added grading columns to track what was correct and what was inaccurate. You can use **Detailed Results** sheet (grade every checkbox) or **Review Queue** sheet (grade only problem pages). Both have dropdown menus for easy data entry! 🎉
