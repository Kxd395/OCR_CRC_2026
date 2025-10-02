# Quality Assurance & Confidence System

**Date**: October 2, 2025  
**Purpose**: Automated quality assurance with confidence scoring and human review triggers

---

## 🎯 Overview

The QA system automatically identifies pages that need human review based on:

1. **Conflicts**: Multiple selections on the same question
2. **Missing**: No selection found for a question
3. **Near-threshold**: Detections close to the threshold (uncertain)
4. **Low confidence**: Very uncertain detections
5. **Poor alignment**: High alignment residual errors

---

## 🚀 Quick Start

### Run QA Analysis

```bash
# Analyze latest run
python3 scripts/build_review_queue.py

# Analyze specific run
python3 scripts/build_review_queue.py --run-dir artifacts/run_20251002_124257

# Adjust sensitivity
python3 scripts/build_review_queue.py --near 0.05 --residual-fail-px 8.0
```

### Output Files

```
artifacts/run_XXXXXX_XXXXXX/review/
├── review_queue.csv          # CSV export for analysis
└── review_queue.xlsx         # Excel with multiple sheets
    ├── Queue                 # Pages needing review
    └── AllCheckboxes         # All checkbox data with confidence
```

---

## 📊 Confidence Levels

Each checkbox detection gets a confidence score:

| Level | Distance from Threshold | Meaning |
|-------|------------------------|---------|
| **High** | >10% | Very confident - no review needed |
| **Medium** | 3-10% | Moderately confident - usually OK |
| **Low** | 1.5-3% | Somewhat uncertain - monitor |
| **Very Low** | <1.5% | Very uncertain - **needs review** |

### Example

Threshold: 11.5%

- Score: 25.0% → **High confidence** (✓ checked, no review)
- Score: 14.5% → **Medium confidence** (✓ checked, OK)
- Score: 12.8% → **Low confidence** (✓ checked, monitor)
- Score: 11.7% → **Very Low confidence** (✓ checked, **review!**)
- Score: 11.2% → **Very Low confidence** (✗ not checked, **review!**)
- Score: 8.0% → **Low confidence** (✗ not checked, monitor)
- Score: 2.0% → **High confidence** (✗ not checked, no review)

---

## 🚨 Review Priority System

### HIGH Priority (Review First)
- **Conflicts**: Multiple checkboxes marked for same question
- **Critical alignment failures**: Residual >6.0px

**Example**:
```
Page 5, Q1: Both Q1_A and Q1_C are marked (conflict!)
→ Human must decide which is correct
```

### MEDIUM Priority (Review Soon)
- **Near-threshold detections**: Score within ±3% of threshold
- **Low confidence detections**: Very uncertain (within ±1.5%)

**Example**:
```
Page 12, Q3_B: Score 11.7% (threshold 11.5%)
→ Very close to threshold, uncertain
```

### LOW Priority (Review If Time)
- **Missing selections**: No answer for a question
- **Moderate alignment issues**: Residual 4.5-6.0px

**Example**:
```
Page 8, Q2: No checkbox marked
→ Might be intentionally blank, or missed
```

---

## 📋 Review Queue Format

### Queue Sheet (review_queue.xlsx)

| Column | Description |
|--------|-------------|
| priority | HIGH / MEDIUM / LOW |
| page | Page filename (e.g., page_0005.png) |
| quality | Alignment quality (ok/warn/fail) |
| residual_px | Alignment error in pixels |
| conflicts | Number of questions with multiple selections |
| missing | Number of questions with no selection |
| near_threshold | Number of questions with near-threshold detections |
| low_confidence | Number of very uncertain detections |
| issues | Comma-separated issue types |
| details | Specific questions and values |
| recommended_action | Always "Manual review required" |

### AllCheckboxes Sheet

Every checkbox from every page with confidence level:

| Column | Description |
|--------|-------------|
| page | Page filename |
| confidence | high / medium / low / very_low |
| id | Checkbox ID (e.g., Q1_A) |
| score | Fill percentage (0.0-1.0) |
| checked | true / false |

---

## 🤖 Gemma Secondary Review (Optional)

For HIGH and MEDIUM priority items, you can run a secondary AI review using Gemma 3:

```bash
# Review HIGH priority pages only
python3 scripts/gemma_secondary_review.py --priority HIGH

# Review all uncertain detections
python3 scripts/gemma_secondary_review.py --priority ALL

# Use custom config
python3 scripts/gemma_secondary_review.py --api-config configs/gemma_custom.yaml
```

### What It Does

1. Loads review queue from `build_review_queue.py`
2. Extracts checkbox images for uncertain detections
3. Sends to Gemma 3 API with context prompt
4. Compares Gemma's decision with original OCR
5. Flags disagreements for human review

### Output

```json
{
  "page": "page_0005.png",
  "checkbox_id": "Q1_B",
  "original_score": 0.117,
  "original_checked": true,
  "gemma_checked": false,
  "gemma_confidence": 0.85,
  "gemma_reasoning": "Mark appears to be scan artifact, not intentional",
  "agreement": false  // ← DISAGREEMENT - manual review needed!
}
```

### Configuration

Create `configs/gemma.yaml`:

```yaml
# Gemma API Configuration
api_endpoint: "https://api.gemini.google.com/v1/models/gemma-3:analyze"
api_key: "YOUR_API_KEY_HERE"

model:
  name: "gemma-3-vision"
  temperature: 0.1  # Low for consistency
  max_tokens: 500

# Secondary review settings
review:
  confidence_threshold: 0.7  # Minimum confidence to accept Gemma's decision
  agreement_threshold: 0.9   # If Gemma confidence >90%, auto-accept
  
# Cost controls
limits:
  max_requests_per_run: 100
  max_cost_per_run: 5.00  # USD
```

---

## 🔧 Adjusting Thresholds

### Detection Threshold

Controls what's considered "checked":

```bash
# More conservative (fewer false positives)
python3 run_pipeline.py --threshold 15.0

# More sensitive (fewer false negatives)
python3 run_pipeline.py --threshold 8.0
```

### Near-Threshold Margin

Controls review queue sensitivity:

```bash
# More strict (only very close to threshold triggers review)
python3 scripts/build_review_queue.py --near 0.015  # 1.5%

# More loose (more items flagged for review)
python3 scripts/build_review_queue.py --near 0.05   # 5.0%
```

### Alignment Residual

Controls alignment quality threshold:

```bash
# More strict alignment requirement
python3 scripts/build_review_queue.py --residual-fail-px 4.0

# More lenient alignment requirement
python3 scripts/build_review_queue.py --residual-fail-px 10.0
```

---

## 📈 Typical Results

### High Quality Scan (Good Alignment, Clear Marks)
```
Total pages: 26
Pages needing review: 2 (8%)

By priority:
  MEDIUM: 2 pages (near-threshold detections)

By issue type:
  Near threshold: 3 questions
  Low confidence: 1 question
```

### Poor Quality Scan (Skewed Pages, Faint Marks)
```
Total pages: 26
Pages needing review: 15 (58%)

By priority:
  HIGH: 3 pages (conflicts, alignment failures)
  MEDIUM: 8 pages (near-threshold)
  LOW: 4 pages (missing selections)

By issue type:
  Conflicts: 2 questions
  Missing: 8 questions
  Near threshold: 18 questions
  Low confidence: 12 questions
```

---

## 🔄 Workflow Integration

### Option 1: Manual Review Only

```bash
# 1. Run pipeline
python3 run_pipeline.py --pdf survey.pdf --template template.json

# 2. Generate review queue
python3 scripts/build_review_queue.py

# 3. Open review_queue.xlsx in Excel
open artifacts/run_*/review/review_queue.xlsx

# 4. Review flagged pages manually using QA overlays
# Look at: artifacts/run_*/step5_qa_overlays/
```

### Option 2: Gemma-Assisted Review

```bash
# 1. Run pipeline
python3 run_pipeline.py --pdf survey.pdf --template template.json

# 2. Generate review queue
python3 scripts/build_review_queue.py

# 3. Run Gemma secondary review
python3 scripts/gemma_secondary_review.py --priority HIGH

# 4. Review only disagreements manually
# Gemma agrees with OCR → Accept
# Gemma disagrees → Manual review needed
```

### Option 3: Integrated Pipeline

Add to `run_pipeline.py`:

```python
# After validate_run.py
run_cmd([
    python_path, "scripts/build_review_queue.py",
    "--run-dir", str(run_dir),
    "--threshold", str(args.threshold / 100.0),
    "--near", str(args.near)
])

if args.use_gemma:
    run_cmd([
        python_path, "scripts/gemma_secondary_review.py",
        "--run-dir", str(run_dir),
        "--priority", "HIGH"
    ])
```

---

## 📊 Statistics & Reporting

### Get Summary Stats

```python
import pandas as pd

# Load review queue
df = pd.read_csv("artifacts/run_*/review/review_queue.csv")

# Summary
print(f"Total pages needing review: {len(df)}")
print(f"HIGH priority: {len(df[df['priority']=='HIGH'])}")
print(f"Conflict rate: {df['conflicts'].sum() / len(df) * 100:.1f}%")
print(f"Missing rate: {df['missing'].sum() / len(df) * 100:.1f}%")

# Most common issues
print(df['issues'].value_counts())

# Pages with most problems
print(df.nlargest(5, 'near_threshold'))
```

---

## 🎯 Best Practices

### 1. Run QA on Every Batch
Always generate review queue to catch issues:
```bash
python3 scripts/build_review_queue.py
```

### 2. Review HIGH Priority First
Focus on conflicts and alignment failures - these are data quality issues.

### 3. Monitor Confidence Trends
If you see many "very_low" confidence detections:
- Check scan quality
- Adjust threshold
- Consider rescanning

### 4. Use Gemma for Scale
Manual review of 100+ pages? Use Gemma to triage:
- Gemma reviews everything
- You review only disagreements
- 10x faster than full manual review

### 5. Document Decisions
In the Excel file, add a "Reviewer Decision" column:
```
| page | issues | details | decision | reviewer | date |
|------|--------|---------|----------|----------|------|
| 5    | conflict | Q1: A,C both marked | A is correct | JD | 2025-10-02 |
```

---

## 🔍 Example Review Session

### Review Queue Shows:

```
Priority: HIGH
Page: page_0012.png
Issues: conflict
Details: Q3: Multiple selections (Q3_B, Q3_D both marked)
```

### Steps:

1. **Open QA overlay**: `artifacts/run_*/step5_qa_overlays/page_0012.png`
2. **Visually inspect**: Look at Q3 checkboxes B and D
3. **Determine correct answer**: Which mark looks intentional?
4. **Update Excel results**: Correct the data manually
5. **Document decision**: Note why you chose B or D

### Common Patterns:

| Issue | Visual Clue | Decision |
|-------|-------------|----------|
| Light mark + Dark mark | One faint, one solid | Choose darker |
| Two equal marks | Both look intentional | Mark as "unclear" |
| Scan artifact | Smudge near checkbox | Ignore artifact |
| Erasure | Erased + new mark | Choose new mark |

---

## 🚀 Future Enhancements

### Coming Soon:
- [ ] Active learning: Train model from review decisions
- [ ] Automated erasure detection
- [ ] Multi-mark pattern recognition (check-all-that-apply)
- [ ] Integration with Gradio web app for web-based review
- [ ] Batch Gemma API calls for efficiency
- [ ] Cost tracking for Gemma API usage

---

## ✅ Summary

**What You Have**:
- ✅ Automated confidence scoring for every checkbox
- ✅ Priority-based review queue (HIGH/MEDIUM/LOW)
- ✅ Detection of conflicts, missing, near-threshold
- ✅ Excel export for easy review
- ✅ Optional Gemma 3 secondary verification

**When to Use**:
- **Always**: Run `build_review_queue.py` to catch issues
- **Large batches**: Use Gemma to triage (review only disagreements)
- **Critical data**: Manual review all HIGH priority items

**ROI**:
- Without QA: Manually review all 26 pages (~2 hours)
- With QA: Review only 2-3 flagged pages (~15 minutes)
- With Gemma: Review only 1-2 disagreements (~5 minutes)

**Next Steps**:
1. Run test: `python3 scripts/build_review_queue.py`
2. Open Excel: `artifacts/run_*/review/review_queue.xlsx`
3. Configure Gemma (optional): `configs/gemma.yaml`
4. Try secondary review: `python3 scripts/gemma_secondary_review.py`

---

**Status**: ✅ Fully implemented and tested  
**Last Updated**: October 2, 2025
