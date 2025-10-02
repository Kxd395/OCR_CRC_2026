#!/usr/bin/env python3
import argparse, json, pathlib, numpy as np, cv2
from scripts.common import read_json, latest_run_dir, sorted_pages, tpl_size, roi_to_poly, apply_h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    args = ap.parse_args()

    tpl = read_json(args.template)
    rois = tpl.get("checkbox_rois_norm", [])
    tpl_w, tpl_h = tpl_size(tpl)

    latest = latest_run_dir("artifacts")
    images_dir = latest/"step2_alignment_and_crop"/"aligned_cropped"
    overlays_dir = latest/"step3_overlays"
    overlays_dir.mkdir(exist_ok=True)
    logs_dir = latest/"logs"

    hmap_path = logs_dir/"homography.json"
    if not hmap_path.exists(): raise SystemExit("homography.json not found. Run step2_align_and_crop first.")
    hmap = read_json(hmap_path)

    for img_path in sorted_pages(images_dir):
        img = cv2.imread(str(img_path)); ov = img.copy()
        img_h, img_w = img.shape[:2]
        # Draw checkboxes directly on cropped image without homography
        # The coordinates are already normalized to the cropped image dimensions
        for r in rois:
            x = int(r['x'] * img_w)
            y = int(r['y'] * img_h)
            w = int(r['w'] * img_w)
            h = int(r['h'] * img_h)
            cv2.rectangle(ov, (x, y), (x+w, y+h), (0,165,255), 2)
        cv2.imwrite(str(overlays_dir/f"{img_path.stem}_overlay.png"), ov)

    with open(logs_dir/"steps.jsonl","a") as f:
        f.write(json.dumps({"step":"overlays","run_dir":str(latest)})+"\n")

if __name__=="__main__":
    main()
