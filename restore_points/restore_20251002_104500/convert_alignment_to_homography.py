#!/usr/bin/env python3
"""
Convert alignment_results.json to homography.json format expected by run_ocr.py
"""
import json
from pathlib import Path

# Read alignment results
alignment_file = Path("artifacts/run_20251001_185300/02_step2_alignment_and_crop/alignment_results.json")
with open(alignment_file) as f:
    alignment_data = json.load(f)

# Create homography format
homography = {
    "pages": {}
}

# Convert each page
for page_data in alignment_data["pages"]:
    page_num = page_data["page"]
    page_name = f"page_{page_num:04d}.png"  # Use PNG extension
    
    if "matrix" in page_data:
        homography["pages"][page_name] = {
            "M": page_data["matrix"]
        }

# Save to logs directory
output_file = Path("artifacts/run_20251001_185300/logs/homography.json")
with open(output_file, "w") as f:
    json.dump(homography, f, indent=2)

print(f"✅ Created {output_file}")
print(f"   Pages processed: {len(homography['pages'])}")
