# Documentation Organization

This directory contains project-level documentation organized by topic.

## Structure

```
docs/
├── fixes/                    # Historical fix documentation
│   ├── CHECKBOX_FIX_2025-01.md
│   ├── ANCHOR_POSITION_FIX.md
│   └── ...
├── CURRENT_STATE.md          # Current system state
├── PIPELINE_STATUS.md        # Pipeline operational status
├── VERIFIED_WORKING.md       # Verification summary
├── USAGE.md                  # How to use the pipeline
├── BEST_PRACTICES.md         # Development guidelines
└── ...
```

## Quick Links

### For Users
- **[USAGE.md](USAGE.md)** - How to run the pipeline
- **[PIPELINE_STATUS.md](PIPELINE_STATUS.md)** - Current status
- **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - Common issues

### For Developers
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - Development guidelines
- **[CURRENT_STATE.md](CURRENT_STATE.md)** - Technical details
- **[CHECKBOX_COORDINATES.md](CHECKBOX_COORDINATES.md)** - Coordinate reference

### Fix History
- **[fixes/CHECKBOX_FIX_2025-01.md](fixes/CHECKBOX_FIX_2025-01.md)** - October 2, 2025 fix
- **[fixes/ANCHOR_POSITION_FIX.md](fixes/ANCHOR_POSITION_FIX.md)** - Anchor positioning fix

## Run Documentation

Individual run documentation is stored in:
```
artifacts/run_YYYYMMDD_HHMMSS/
├── INDEX.md                  # Run documentation index
└── notes/
    ├── DATA_PROVENANCE.md
    ├── RETENTION.md
    ├── RUN_SUMMARY.md
    └── CONFIGURATION.md
```

See `run_20251001_185300_good` for reference implementation.

## Documentation Standards

All runs should include:
1. **INDEX.md** - Main documentation index
2. **notes/DATA_PROVENANCE.md** - Source tracking
3. **notes/RETENTION.md** - Data lifecycle policy
4. **notes/RUN_SUMMARY.md** - Results and timing
5. **notes/CONFIGURATION.md** - Settings used

---

**Last Updated**: October 2, 2025
