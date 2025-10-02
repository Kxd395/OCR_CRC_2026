#!/usr/bin/env python3
import argparse, json, cv2, numpy as np
from pathlib import Path

def load_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def crop(warped, roi, tpl_w, tpl_h, margin=2):
    x = int(roi["x"]*tpl_w)+margin
    y = int(roi["y"]*tpl_h)+margin
    w = int(roi["w"]*tpl_w)-2*margin
    h = int(roi["h"]*tpl_h)-2*margin
    x=max(0,x); y=max(0,y); w=max(1,w); h=max(1,h)
    return warped[y:y+h, x:x+w]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()

    run = Path(args.run_dir)
    tpl = json.loads(Path(args.template).read_text(encoding="utf-8"))
    tpl_w = tpl["page_size"]["width_px"]; tpl_h = tpl["page_size"]["height_px"]
    rois = tpl["checkbox_rois_norm"]
    pages = load_json(run/"logs/ocr_results.json")
    Hpages = load_json(run/"logs/homography.json")["pages"]

    out_dir = run/"review"/"threshold_sweeps"
    out_dir.mkdir(parents=True, exist_ok=True)
    src_dir = run/"images"

    count = 0
    for rec in pages:
        if count >= args.limit: break
        page = rec["page"]
        near = [b for b in rec["checkboxes"] if abs(b.get("score",0)-0.55)<=0.03]  # default; adjust if needed
        if not near: continue
        H = np.array(Hpages[page]["M"], dtype=np.float32)
        img = cv2.imread(str(src_dir/page), cv2.IMREAD_GRAYSCALE)
        if img is None: continue
        warped = cv2.warpPerspective(img, H, (tpl_w, tpl_h))

        for b in near[:3]:  # up to 3 per page
            # roi find
            q, idx = b["id"].split("_")
            rid = (int(q[1:])-1)*5 + int(idx)
            roi = rois[rid]
            patch = crop(warped, roi, tpl_w, tpl_h, 2)
            # build panel
            thresholds = [0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75]
            h,w = patch.shape
            gap = 4
            cols = len(thresholds)
            panel = np.full((h+2*gap, cols*(w+gap)+gap), 255, np.uint8)
            for i,t in enumerate(thresholds):
                # simple global threshold on inverted patch proxying "fill"
                inv = 255 - patch
                _, bw = cv2.threshold(inv, int(255*t), 255, cv2.THRESH_BINARY)
                x0 = gap + i*(w+gap)
                panel[gap:gap+h, x0:x0+w] = bw
                cv2.putText(panel, f"{t:.2f}", (x0+2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1, cv2.LINE_AA)
            out = out_dir/f"{Path(page).stem}_{b['id']}_sweep.png"
            cv2.imwrite(str(out), panel)
        count += 1

    print("Wrote sweeps to", out_dir)

if __name__ == "__main__":
    main()
