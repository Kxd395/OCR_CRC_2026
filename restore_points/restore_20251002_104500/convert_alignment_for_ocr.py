#!/usr/bin/env python3
"""
Convert alignment_results.json to homography.json format for backward compatibility.
This allows the OCR scripts to use the alignment data from step2.
"""
import json
import numpy as np
from pathlib import Path
import argparse


def convert_alignment_to_homography(run_dir):
    """
    Convert step2_alignment_and_crop/alignment_results.json 
    to logs/homography.json format expected by OCR scripts.
    """
    run_path = Path(run_dir)
    
    # Input: step2 alignment results
    alignment_file = run_path / "step2_alignment_and_crop" / "alignment_results.json"
    if not alignment_file.exists():
        raise FileNotFoundError(f"Alignment results not found: {alignment_file}")
    
    with open(alignment_file) as f:
        alignment_data = json.load(f)
    
    # Output: homography format for OCR scripts
    homography = {"pages": {}}
    
    # Convert each page
    for page_data in alignment_data["pages"]:
        page_num = page_data["page"]
        # Match the actual filename in aligned_cropped folder
        page_name = f"page_{page_num:04d}_aligned_cropped.png"
        
        if "matrix" in page_data and page_data["matrix"]:
            # Forward transformation matrix
            M = np.array(page_data["matrix"], dtype=np.float32)
            
            # Compute inverse for reverse transformation
            try:
                Minv = np.linalg.inv(M).tolist()
            except np.linalg.LinAlgError:
                print(f"Warning: Could not invert matrix for {page_name}")
                Minv = M.tolist()  # Fallback to forward matrix
            
            homography["pages"][page_name] = {
                "M": M.tolist(),
                "Minv": Minv
            }
    
    # Save to logs directory
    logs_dir = run_path / "logs"
    logs_dir.mkdir(exist_ok=True)
    output_file = logs_dir / "homography.json"
    
    with open(output_file, "w") as f:
        json.dump(homography, f, indent=2)
    
    print(f"✅ Created homography.json")
    print(f"   Input:  {alignment_file}")
    print(f"   Output: {output_file}")
    print(f"   Pages:  {len(homography['pages'])}")
    
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert alignment results to homography format"
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Run directory containing step2_alignment_and_crop/alignment_results.json"
    )
    args = parser.parse_args()
    
    convert_alignment_to_homography(args.run_dir)
