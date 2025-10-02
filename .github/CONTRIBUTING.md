# Contributing Guidelines

## Overview

This document outlines the standards and practices for contributing to the CRC OCR Pipeline project. Following these guidelines ensures consistency, reproducibility, and maintainability across all development efforts.

## Code of Conduct

- Be respectful and professional in all interactions
- Prioritize reproducibility and documentation
- Test thoroughly before committing
- Keep commit messages clear and descriptive

## Development Workflow

### 1. Branch Naming Convention

```
feature/<feature-name>       # New features
bugfix/<bug-description>     # Bug fixes
hotfix/<critical-fix>        # Production hotfixes
experiment/<experiment-name> # Experimental changes
docs/<doc-update>            # Documentation only
```

**Examples**:
- `feature/step3-checkbox-extraction`
- `bugfix/anchor-detection-nondeterministic`
- `docs/update-processing-instructions`

### 2. Commit Message Standards

Use the following format:

```
<type>(<scope>): <short summary>

<detailed description>

<breaking changes if any>

<validation results>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Example**:
```
fix(step2): Change cropping from inward inset to outward margin

PROBLEM: Cropping was shrinking pages instead of expanding
SOLUTION: Changed to OUTWARD margin expansion (0.125")
RESULT: Perfect alignment with 2267x2813px output

VALIDATION:
✅ 26/26 pages aligned with 0.00px error
✅ Pixel-perfect match with reference run
```

### 3. Pull Request Process

1. **Create Feature Branch**: Branch from `main` or `develop`
2. **Implement Changes**: Follow coding standards
3. **Test Thoroughly**: Run all validation steps
4. **Document Changes**: Update relevant docs
5. **Create PR**: Use PR template
6. **Code Review**: Address all feedback
7. **Merge**: Squash and merge when approved

## Development Standards

### Python Code Style

- **Formatting**: Black (line length: 100)
- **Linting**: Ruff
- **Type Checking**: MyPy
- **Docstrings**: Google style

```python
def compute_crop_region(
    template_anchors: dict[str, tuple[int, int]],
    margin_inches: float = 0.125,
    dpi: int = 300
) -> tuple[int, int, int, int]:
    """
    Compute crop region with outward margin expansion from anchors.
    
    Args:
        template_anchors: Dictionary mapping anchor IDs to (x, y) positions
        margin_inches: Physical margin in inches to expand outward (default 0.125)
        dpi: Dots per inch for conversion (default 300)
    
    Returns:
        Tuple of (x1, y1, x2, y2) crop coordinates
        
    Example:
        >>> anchors = {"TL": (178, 280), "BR": (2371, 3016)}
        >>> x1, y1, x2, y2 = compute_crop_region(anchors)
        >>> print(f"Crop: ({x1}, {y1}) -> ({x2}, {y2})")
    """
    # Implementation...
```

### File Organization

```
scripts/
  stepN_*.py           # Processing scripts (numbered by pipeline order)
  common.py            # Shared utilities
  analyze_*.py         # Analysis/validation tools
  
docs/
  PROCESSING_INSTRUCTIONS.md    # Main pipeline documentation
  TROUBLESHOOTING.md            # Common issues and solutions
  <FEATURE>_SUMMARY.md          # Major feature documentation
  
configs/
  ocr.yaml             # OCR configuration
  models.yaml          # Model settings
  
templates/
  <template_name>/
    template.json      # Form structure definition
    grid.json          # Grid layout
    README.md          # Template-specific docs
```

### Configuration Management

- **Use YAML for configs**: Easy to read and edit
- **Document all parameters**: Inline comments required
- **Version configs**: Include version numbers
- **Validate on load**: Check for required fields

Example:
```yaml
# OCR Pipeline Configuration v1.0.0
dpi: 300  # Resolution for PDF conversion

alignment:
  ransac_threshold_px: 3.0      # RANSAC outlier threshold
  quality_threshold_ok_px: 4.5  # "OK" alignment quality
  quality_threshold_warn_px: 6.0  # "WARN" alignment quality
```

## Testing Requirements

### Before Committing

1. **Run linters**: `ruff check scripts/`
2. **Format code**: `black scripts/`
3. **Type check**: `mypy scripts/`
4. **Test functionality**: Run on sample dataset
5. **Validate output**: Check metrics and visualizations

### Test Coverage

- **Unit tests**: For utility functions
- **Integration tests**: For full pipeline steps
- **Validation tests**: Compare against known-good runs
- **Edge cases**: Test with problematic inputs

Example test structure:
```python
def test_compute_crop_region_basic():
    """Test basic outward margin expansion."""
    anchors = {"TL": (100, 100), "BR": (200, 200)}
    x1, y1, x2, y2 = compute_crop_region(anchors, margin_inches=0.1, dpi=300)
    
    # Verify expansion (0.1" * 300 DPI = 30px)
    assert x1 == 70  # 100 - 30
    assert y1 == 70
    assert x2 == 230  # 200 + 30
    assert y2 == 230
```

## Documentation Standards

### Code Documentation

Every script must include:

1. **File-level docstring**: Purpose, usage, examples
2. **Function docstrings**: Args, returns, raises, examples
3. **Inline comments**: Explain complex logic
4. **Type hints**: All function signatures

### Run Documentation

Every processing run must create:

1. **README.md** in run directory:
   ```markdown
   # Run: 20251001_185300
   
   ## Input
   - PDF: test_survey.pdf (26 pages)
   - Template: crc_survey_l_anchors_v1
   
   ## Processing Steps
   1. Step 0: PDF Ingestion ✅
   2. Step 1: Anchor Detection ✅ (104/104 anchors)
   3. Step 2: Alignment & Cropping ✅ (26/26 pages OK)
   
   ## Results
   - Output: aligned_cropped/ (2267×2813px)
   - Quality: 0.00px mean error
   - Status: SUCCESS
   
   ## Notes
   - All anchors detected correctly
   - Perfect alignment on all pages
   - Used correct outward margin expansion
   ```

2. **scripts_archive/**: Copy of all scripts used
3. **CHANGES.md**: Document any deviations or issues
4. **metrics.json**: Quantitative results

### Feature Documentation

When implementing a new feature, create `<FEATURE>_SUMMARY.md`:

```markdown
# Feature: Checkbox Extraction

**Date**: YYYY-MM-DD
**Author**: Name
**Status**: ✅ Complete / 🚧 In Progress / ❌ Failed

## Problem
What issue does this solve?

## Solution
How does it solve it?

## Implementation
Key technical details

## Testing
How was it validated?

## Results
What were the outcomes?

## Future Work
What could be improved?
```

## Run Archival Process

### Automatic Archival

Every run should automatically:

1. **Copy all scripts** to `scripts_archive/`
2. **Copy all configs** to `scripts_archive/`
3. **Generate manifest.json** with file metadata
4. **Create README.md** with run summary

Use the provided script:
```bash
python scripts/archive_run_scripts.py <run_directory>
```

### Manual Documentation

After each run, document:

1. **Input characteristics**: PDF source, page count, quality
2. **Processing parameters**: Any non-default settings
3. **Quality metrics**: Detection rates, alignment errors
4. **Issues encountered**: And how they were resolved
5. **Output validation**: Visual checks, metric checks

### Troubleshooting Log

Create `TROUBLESHOOTING.md` in run directory if issues occur:

```markdown
# Troubleshooting Log

## Issue 1: Poor Anchor Detection on Page 5

**Symptom**: Only 2/4 anchors detected
**Root Cause**: Low scan quality, faint L-marks
**Investigation Steps**:
1. Checked visualization: page_0005_anchors.png
2. Examined binary threshold
3. Tested different search windows

**Solution**: Manually reviewed - marks barely visible, accepted 2/4
**Outcome**: Used affine transform, alignment OK (3.2px error)
```

## Version Control Best Practices

### What to Commit

✅ **DO commit**:
- Source code (scripts, configs)
- Documentation (markdown files)
- Templates (JSON, YAML)
- Small test files (<1MB)
- Requirements/dependencies

❌ **DON'T commit**:
- Large data files (PDFs, images)
- Processing outputs (artifacts/)
- Virtual environments (.venv/)
- Cache files (__pycache__, .pyc)
- Credentials or secrets
- Temporary files

### .gitignore Template

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.egg-info/

# OCR Artifacts
artifacts/*/
!artifacts/.gitkeep
data/*/
!data/.gitkeep
*.png
*.jpg
*.pdf

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Sensitive
*.key
*.pem
secrets/
.env
```

## Code Review Checklist

### For Reviewers

- [ ] Code follows style guide (Black, Ruff)
- [ ] Type hints present and correct
- [ ] Docstrings complete and accurate
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No hardcoded paths or credentials
- [ ] Error handling appropriate
- [ ] Logging sufficient for debugging
- [ ] Performance acceptable
- [ ] Breaking changes documented

### For Contributors

Before requesting review:

- [ ] All tests pass locally
- [ ] Linters pass (ruff, mypy)
- [ ] Code formatted (black)
- [ ] Commit messages descriptive
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] Branch up to date with main

## Release Process

### Version Numbering

Use Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. [ ] Update version in all relevant files
2. [ ] Update CHANGELOG.md
3. [ ] Run full test suite
4. [ ] Update documentation
5. [ ] Create git tag: `v1.2.3`
6. [ ] Create GitHub release with notes
7. [ ] Archive release artifacts

## Questions?

If you have questions about these guidelines:
1. Check existing documentation
2. Review similar past implementations
3. Ask in team discussion
4. Update this document with clarifications

---

**Last Updated**: October 1, 2025
**Version**: 1.0.0
