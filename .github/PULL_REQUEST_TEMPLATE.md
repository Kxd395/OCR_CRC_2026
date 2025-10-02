# Pull Request Template

## Description

<!-- Provide a clear and concise description of the changes -->

## Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that causes existing functionality to change)
- [ ] 📝 Documentation update
- [ ] 🎨 Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test addition or update

## Related Issues

<!-- Link to related issues using #issue_number -->

Fixes #
Relates to #

## Changes Made

<!-- List the specific changes made in this PR -->

### Modified Files
- `scripts/file1.py` - Description of changes
- `docs/file2.md` - Description of changes

### New Files
- `scripts/new_feature.py` - Purpose and functionality

### Deleted Files
- `scripts/deprecated.py` - Reason for removal

## Testing Performed

### Test Environment
- Python version: 
- OS: 
- Dependencies: (list any new or updated dependencies)

### Test Cases
<!-- Describe the tests you ran -->

- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing on sample data
- [ ] Validation against reference run

### Test Results
```
# Paste relevant test output here
```

### Validation Metrics
<!-- If applicable, include processing metrics -->

- Pages processed: X/Y
- Anchor detection rate: X%
- Alignment quality: Mean X.Xpx, Max X.Xpx
- Processing time: Xs per page

## Visual Evidence

<!-- Include screenshots, visualizations, or links to output files -->

### Before
<!-- Screenshot or description of behavior before changes -->

### After
<!-- Screenshot or description of behavior after changes -->

## Documentation Updates

- [ ] Code comments updated
- [ ] Docstrings added/updated
- [ ] README.md updated
- [ ] PROCESSING_INSTRUCTIONS.md updated
- [ ] Feature summary document created
- [ ] CHANGELOG.md updated

## Breaking Changes

<!-- If this is a breaking change, describe the impact and migration path -->

**Impact**: 
**Migration Guide**: 

## Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Self-review of code performed
- [ ] Code is properly commented
- [ ] Type hints added to all functions
- [ ] No hardcoded paths or credentials

### Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Edge cases considered and tested
- [ ] Performance impact assessed

### Documentation
- [ ] All changes documented
- [ ] Run documentation created (if applicable)
- [ ] Troubleshooting notes added (if applicable)
- [ ] Examples provided for new features

### Repository
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] Linting passes (ruff)
- [ ] Formatting passes (black)
- [ ] Type checking passes (mypy)

## Deployment Notes

<!-- Any special deployment considerations -->

- [ ] Requires configuration changes
- [ ] Requires new dependencies
- [ ] Requires data migration
- [ ] Requires environment variable changes

## Additional Context

<!-- Add any other context, screenshots, or information about the PR here -->

## Reviewer Notes

<!-- Anything specific you want reviewers to focus on -->

---

**PR Checklist for Reviewers**:
- [ ] Code quality and style
- [ ] Test coverage adequate
- [ ] Documentation complete
- [ ] No security concerns
- [ ] Performance acceptable
- [ ] Breaking changes properly handled
