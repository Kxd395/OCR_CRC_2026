#!/usr/bin/env python3
import argparse, sys
from rich.table import Table
from rich.console import Console
from scripts.common import read_json, latest_run_dir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--fail-on-error", action="store_true")
    args = ap.parse_args()

    latest = latest_run_dir("artifacts")
    
    # Try new alignment_results.json format first
    align_file = latest/"step2_alignment_and_crop"/"alignment_results.json"
    if align_file.exists():
        align = read_json(align_file)
        warn_px = float(align.get("thresholds", {}).get("warn_px", 4.5))
        fail_px = float(align.get("thresholds", {}).get("ok_px", 6.0))
        
        rows = []; bad = 0
        for rec in align["pages"]:
            page = str(rec["page"])
            res = float(rec["mean_error_px"])
            qual = rec.get("status", "OK").lower()
            rows.append((page, f"{res:.2f}", qual))
            if res > fail_px: bad += 1
    else:
        # Fall back to old homography.json format
        hom = read_json(latest/"logs"/"homography.json")
        warn_px = float(hom.get("thresholds", {}).get("warn_px", 4.5))
        fail_px = float(hom.get("thresholds", {}).get("fail_px", 6.0))
        
        rows = []; bad = 0
        for page, rec in hom["pages"].items():
            res = float(rec["residual_px"]); qual = rec.get("quality","ok")
            rows.append((page, f"{res:.2f}", qual))
            if res > fail_px: bad += 1

    t = Table(title=f"Alignment residuals (warn={warn_px}px fail={fail_px}px)")
    t.add_column("Page"); t.add_column("Residual px"); t.add_column("Quality")
    for r in rows: t.add_row(*r)
    Console().print(t)
    if args.fail_on_error and bad>0:
        print(f"FAIL: {bad} page(s) exceed fail threshold {fail_px}px."); sys.exit(1)

if __name__=="__main__":
    main()
