#!/usr/bin/env python3
import argparse, time, pathlib, json
from pdf2image import convert_from_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--threshold", type=float, default=None, help="Fill threshold to include in run name")
    args = ap.parse_args()

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    if args.threshold is not None:
        # Format threshold to avoid floating point precision issues
        # Use 2 decimal places, but strip trailing zeros and decimal point if whole number
        threshold_str = f"{args.threshold:.2f}".rstrip('0').rstrip('.')
        run_dir = pathlib.Path("artifacts") / f"run_{timestamp}_{threshold_str}"
    else:
        run_dir = pathlib.Path("artifacts") / f"run_{timestamp}"
    (run_dir/"step0_images").mkdir(parents=True, exist_ok=True)
    (run_dir/"logs").mkdir(parents=True, exist_ok=True)

    pages = convert_from_path(args.pdf, dpi=args.dpi)
    for i, img in enumerate(pages, 1):
        img.save(run_dir/"step0_images"/f"page_{i:04d}.png")
    with open(run_dir/"logs"/"steps.jsonl","a") as f:
        f.write(json.dumps({"step":"ingest","pages":len(pages),"run_dir":str(run_dir)})+"\n")
    print(f"Ingested {len(pages)} pages -> {run_dir}")

if __name__=="__main__":
    main()
