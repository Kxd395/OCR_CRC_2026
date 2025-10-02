# Manual Grading & Accuracy Tracking System

**Date**: October 2, 2025  
**Purpose**: Track OCR accuracy with human review and corrections

---

## 🎯 Overview

The manual grading system allows you to:

1. **Review OCR results** - Verify what the pipeline detected
2. **Mark accuracy** - Flag correct vs incorrect detections
3. **Provide corrections** - Record what the actual answer should be
4. **Track reviewers** - Know who reviewed what
5. **Build training data** - Use corrections to improve the model

---

## 📊 Two Files with Grading Columns

### 1. **Detailed Results** (Main Excel Export)

**File**: `exports/run_XXXXXX_XXXXXX.xlsx` → **"Detailed Results"** sheet

**Purpose**: Grade every single checkbox detection

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **A-F: OCR Results** ||||
| Page | Auto | Page number | Page 5 |
| Checkbox ID | Auto | Question and option | Q3_2 |
| Row | Auto | Question number (1-5) | 3 |
| Column | Auto | Option number (1-5) | 2 |
| Fill % | Auto | Fill percentage | 12.3% |
| OCR Status | Auto | What OCR detected | ✓ Checked / Empty |
| **G-K: Manual Grading** ||||
| Manual Review? | **Your input** | Does this need review? | YES/NO (dropdown) |
| OCR Correct? | **Your input** | Was OCR accurate? | CORRECT/INCORRECT/UNCERTAIN (dropdown) |
| Actual Status | **Your input** | What it really is | Checked/Empty (dropdown) |
| Reviewer | **Your input** | Who reviewed this | JD, Sarah, etc. |
| Notes | **Your input** | Any comments | "Faint mark, hard to tell" |

**Features**:
- ✅ **Dropdown menus** for consistent data entry
- ✅ **Auto-flagging** of near-threshold items (column G)
- ✅ **Color coding** - OCR columns (blue), Manual columns (orange)
- ✅ **223 rows** - One per checkbox (26 pages × ~8.5 checkboxes/page)

### 2. **Review Queue** (QA System)

**File**: `artifacts/run_XXXXXX_XXXXXX/review/review_queue.xlsx` → **"Queue"** sheet

**Purpose**: Grade only pages that need review (conflicts, missing, uncertain)

**Columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **A-K: QA Analysis** ||||
| priority | Auto | Review urgency | HIGH/MEDIUM/LOW |
| page | Auto | Page filename | page_0005_aligned_cropped.png |
| quality | Auto | Alignment quality | ok/warn/fail |
| residual_px | Auto | Alignment error | 0.00 |
| conflicts | Auto | # conflicts | 2 |
| missing | Auto | # missing | 1 |
| near_threshold | Auto | # uncertain | 5 |
| low_confidence | Auto | # very uncertain | 18 |
| issues | Auto | Issue types | conflict, near-threshold |
| details | Auto | Specific problems | Q1: Multiple selections (Q1_A, Q1_C) |
| recommended_action | Auto | What to do | Manual review required |
| **L-Q: Manual Grading** ||||
| reviewed | **Your input** | Have you reviewed this? | YES/NO (dropdown) |
| ocr_accurate | **Your input** | Was OCR accurate? | CORRECT/INCORRECT/PARTIAL (dropdown) |
| corrected_conflicts | **Your input** | Correct answers for conflicts | Q1: A is correct, Q5: both correct |
| reviewer_name | **Your input** | Who reviewed | JD |
| review_date | **Your input** | When reviewed | 2025-10-02 |
| review_notes | **Your input** | Comments | "Page 5: Q1_A very faint but visible" |

**Features**:
- ✅ **Priority sorted** - HIGH priority first
- ✅ **Focused** - Only 26 pages (those needing review)
- ✅ **Context-rich** - Includes issue details
- ✅ **Page-level** - One row per page

---

## 🚀 Recommended Workflow

### Option A: Grade Everything (Thorough)

**Use**: Detailed Results sheet

**Steps**:
1. Open Excel: `exports/run_XXXXXX_XXXXXX.xlsx`
2. Go to **"Detailed Results"** sheet
3. Review each checkbox (223 rows)
4. For each row:
   - Check if "Manual Review?" = YES (auto-flagged)
   - Compare OCR Status vs QA overlay image
   - Fill in "OCR Correct?" (CORRECT/INCORRECT/UNCERTAIN)
   - If incorrect, fill in "Actual Status"
   - Add your name and notes
5. Save file

**Time**: ~1-2 hours for 26 pages  
**Best for**: Building comprehensive training data

### Option B: Grade Only Issues (Efficient)

**Use**: Review Queue sheet

**Steps**:
1. Open Excel: `artifacts/run_*/review/review_queue.xlsx`
2. Go to **"Queue"** sheet
3. Sort by "priority" (HIGH first)
4. For each page:
   - Open QA overlay: `artifacts/run_*/step5_qa_overlays/page_XXXX.png`
   - Read "details" column (tells you which checkboxes have issues)
   - Visually verify the problem checkboxes
   - Fill in grading columns:
     - reviewed: YES
     - ocr_accurate: CORRECT/INCORRECT/PARTIAL
     - corrected_conflicts: Document correct answers
     - reviewer_name: Your initials
     - review_date: Today's date
     - review_notes: Any observations
5. Save file

**Time**: ~30 minutes for 26 pages (reviewing only flagged items)  
**Best for**: Quick QA, catching major errors

---

## 📝 Grading Guidelines

### How to Determine "OCR Correct?"

**CORRECT**: OCR matches reality
- Checkbox is checked, OCR says "✓ Checked" → CORRECT
- Checkbox is empty, OCR says "Empty" → CORRECT

**INCORRECT**: OCR made a mistake
- Checkbox is checked, OCR says "Empty" → INCORRECT (false negative)
- Checkbox is empty, OCR says "✓ Checked" → INCORRECT (false positive)

**UNCERTAIN**: Can't tell from image
- Mark is very faint, ambiguous
- Scan quality too poor
- Possible erasure
- Needs secondary review or better scan

**PARTIAL** (Review Queue only): Some correct, some incorrect
- Page has 5 questions, 4 are correct, 1 is wrong → PARTIAL

### Common Scenarios

#### Scenario 1: Conflict (Multiple Selections)

```
OCR Result:
  Q1_A: ✓ Checked (15.2%)
  Q1_C: ✓ Checked (12.8%)
  
QA Overlay: Both boxes appear marked

Your Grading:
  ocr_accurate: CORRECT (OCR detected both correctly)
  corrected_conflicts: "Q1: Both A and C are actually marked - data issue, not OCR error"
  notes: "Survey has two marks, OCR is correct. Might be respondent error."
```

#### Scenario 2: Near-Threshold (Uncertain)

```
OCR Result:
  Q2_B: ✓ Checked (11.7%)  [threshold: 11.5%]
  
QA Overlay: Very faint pencil mark

Your Grading:
  ocr_accurate: CORRECT (faint mark is real)
  notes: "Faint but intentional mark, OCR correct"
  
OR

  ocr_accurate: INCORRECT (it's just a smudge)
  actual_status: Empty
  notes: "Scan artifact, not a real mark"
```

#### Scenario 3: Missing Selection

```
OCR Result:
  Q3: No checkboxes detected
  
QA Overlay: All boxes appear empty

Your Grading:
  ocr_accurate: CORRECT (legitimately blank)
  notes: "Question left blank, OCR correct"
  
OR

  ocr_accurate: INCORRECT (very faint mark missed)
  actual_status: Q3_D should be Checked
  notes: "Very light pencil mark in Q3_D, OCR threshold too high"
```

---

## 📈 Generating Accuracy Statistics

### After Grading

Once you've filled in the manual grading columns, you can calculate OCR accuracy:

```python
import pandas as pd

# Load graded results
df = pd.read_excel("exports/run_20251002_124257.xlsx", sheet_name="Detailed Results")

# Filter to only reviewed items
reviewed = df[df['OCR Correct?'].notna()]

# Calculate accuracy
total_reviewed = len(reviewed)
correct = len(reviewed[reviewed['OCR Correct?'] == 'CORRECT'])
incorrect = len(reviewed[reviewed['OCR Correct?'] == 'INCORRECT'])
uncertain = len(reviewed[reviewed['OCR Correct?'] == 'UNCERTAIN'])

accuracy = (correct / total_reviewed) * 100

print(f"Accuracy: {accuracy:.1f}%")
print(f"Correct: {correct}/{total_reviewed}")
print(f"Incorrect: {incorrect}/{total_reviewed}")
print(f"Uncertain: {uncertain}/{total_reviewed}")

# Find common error patterns
errors = reviewed[reviewed['OCR Correct?'] == 'INCORRECT']
print("\nError breakdown:")
print(errors.groupby('Fill %').size())
```

### Example Output

```
Accuracy: 94.2%
Correct: 210/223
Incorrect: 8/223
Uncertain: 5/223

Error breakdown:
Most errors occur at:
  10.5-12.5% (near threshold): 6 errors
  2.0-5.0% (very light marks): 2 errors
```

---

## 🎯 Using Grading Data to Improve Pipeline

### 1. Adjust Threshold

If you find many false negatives (missed marks):

```bash
# Lower threshold to catch fainter marks
python3 run_pipeline.py --threshold 9.0
```

If you find many false positives (noise detected as marks):

```bash
# Raise threshold to be more conservative
python3 run_pipeline.py --threshold 14.0
```

### 2. Build Training Data

Export graded results for machine learning:

```python
import pandas as pd

# Load graded data
df = pd.read_excel("exports/run_20251002_124257.xlsx", sheet_name="Detailed Results")

# Filter to reviewed items with corrections
training_data = df[
    (df['OCR Correct?'] == 'INCORRECT') & 
    (df['Actual Status'].notna())
]

# Export for training
training_data[['Checkbox ID', 'Fill %', 'OCR Status', 'Actual Status', 'Notes']].to_csv(
    'data/training/corrections_20251002.csv', 
    index=False
)

print(f"Exported {len(training_data)} corrections for training")
```

### 3. Create Feedback Loop

Use corrections to retrain or fine-tune:

1. **Collect corrections** from multiple runs
2. **Identify patterns** (e.g., always misses 10-11% range)
3. **Adjust algorithm** or threshold
4. **Re-run pipeline** on same images
5. **Compare new accuracy** to previous

---

## 📋 Best Practices

### 1. **Grade in Batches**
- Do HIGH priority first (conflicts are critical)
- Take breaks (mental fatigue reduces accuracy)
- Grade 5-10 pages at a time

### 2. **Use Visual Aids**
- Always open QA overlay when uncertain
- Zoom in on checkbox images
- Compare similar fill percentages

### 3. **Be Consistent**
- Define your own threshold for "faint but real"
- Document edge cases in notes
- Have multiple reviewers cross-check

### 4. **Track Patterns**
```
Common notes to track:
  - "Erasure - previous mark visible"
  - "Scan artifact looks like mark"
  - "Intentional check but very light"
  - "Multiple marks - respondent error not OCR error"
```

### 5. **Use Notes Field**
```
Good notes:
  ✅ "Q2_B: Faint pencil, OCR missed it"
  ✅ "Q5: Respondent marked 2 boxes (conflict), OCR correct"
  ✅ "Page slightly skewed but alignment OK"

Bad notes:
  ❌ "Wrong"
  ❌ "Check this"
  ❌ (empty)
```

---

## 🔄 Sample Review Session

### Setup (5 minutes)
```bash
# 1. Open Excel files
open exports/run_20251002_124257.xlsx
open artifacts/run_20251002_124257/review/review_queue.xlsx

# 2. Open QA overlays folder
open artifacts/run_20251002_124257/step5_qa_overlays/
```

### Review (30 minutes)

**Review Queue approach**:

1. **Page 1** (HIGH priority - conflict in Q5)
   - Open: `page_0001.png`
   - See: Q5_1 and Q5_4 both marked
   - Grade:
     - reviewed: YES
     - ocr_accurate: CORRECT (both really are marked)
     - corrected_conflicts: Q5_1 appears darker, probably intended answer
     - reviewer_name: JD
     - review_date: 2025-10-02
     - notes: "Both marked but Q5_1 darker - possible erasure on Q5_4"

2. **Page 8** (MEDIUM - missing selections)
   - Open: `page_0008.png`
   - See: Q1-Q4 all blank
   - Grade:
     - reviewed: YES
     - ocr_accurate: CORRECT (legitimately blank)
     - notes: "Questions 1-4 intentionally left blank"

3. **Continue** for remaining HIGH priority pages...

### Save & Report (5 minutes)
- Save Excel files
- Generate accuracy stats (if desired)
- Share with team

**Total time**: ~40 minutes for 26 pages using Review Queue

---

## ✅ Summary

**What You Have**:
- ✅ Manual grading columns in **Detailed Results** sheet (all checkboxes)
- ✅ Manual grading columns in **Review Queue** sheet (flagged pages only)
- ✅ Dropdown menus for consistent data entry
- ✅ Auto-flagging of items needing review
- ✅ Color-coded columns (OCR vs Manual)

**How to Use**:
1. **Quick QA**: Grade Review Queue only (~30 min)
2. **Thorough**: Grade all Detailed Results (~1-2 hours)
3. **Calculate accuracy** from graded data
4. **Improve pipeline** based on patterns

**ROI**:
- Track OCR accuracy over time
- Identify systematic errors
- Build training data for improvements
- Audit trail for compliance
- Continuous improvement feedback loop

---

**Status**: ✅ Fully implemented  
**Files updated**:
- `scripts/export_to_excel.py` - Added 5 grading columns to Detailed sheet
- `scripts/build_review_queue.py` - Added 6 grading columns to Queue sheet

**Ready to use immediately!**
