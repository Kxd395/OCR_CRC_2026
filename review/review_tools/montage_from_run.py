#!/usr/bin/env python3
import argparse, json, cv2, numpy as np
from pathlib import Path

def load_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def apply_h(M, pts):
    pts_h = np.hstack([pts, np.ones((pts.shape[0],1))])
    out = (M @ pts_h.T).T
    out = out[:,:2] / out[:,2:3]
    return out

def crop_from_template(warped, roi, tpl_w, tpl_h, margin=2):
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
    ap.add_argument("--limit", type=int, default=0, help="limit number of pages")
    args = ap.parse_args()

    run = Path(args.run_dir)
    tpl = json.loads(Path(args.template).read_text(encoding="utf-8"))
    tpl_w = tpl["page_size"]["width_px"]; tpl_h = tpl["page_size"]["height_px"]
    rois = tpl["checkbox_rois_norm"]
    M_by_page = load_json(run/"logs/homography.json")["pages"]

    # prefer existing aligned pages; else compute on the fly
    aligned_dir = run/"02_step2_alignment_and_crop"/"aligned_full"
    src_dir = run/"images"
    out_dir = run/"review"/"montage"
    out_dir.mkdir(parents=True, exist_ok=True)

    pages = sorted(M_by_page.keys())
    if args.limit>0: pages = pages[:args.limit]

    for page_name in pages:
        H = np.array(M_by_page[page_name]["M"], dtype=np.float32)
        # load source
        cand = [aligned_dir/f"{Path(page_name).stem}_aligned_full.png", src_dir/page_name]
        img = None
        for c in cand:
            if c.exists():
                img = cv2.imread(str(c), cv2.IMREAD_GRAYSCALE)
                if "aligned_full" not in str(c):
                    img = cv2.warpPerspective(img, H, (tpl_w, tpl_h))
                break
        if img is None:
            continue

        # build 5x5 montage: rows = Q1..Q5, cols = options 0..4
        cell_h = max(int(0.08*tpl_h), 120)
        cell_w = max(int(0.07*tpl_w), 120)
        gap = 6
        canvas = np.full((5*cell_h + 6*gap, 5*cell_w + 6*gap), 255, np.uint8)

        for r in range(5):
            for c in range(5):
                rid = r*5+c
                crop = crop_from_template(img, rois[rid], tpl_w, tpl_h, margin=2)
                crop = cv2.resize(crop, (cell_w, cell_h), interpolation=cv2.INTER_AREA)
                y0 = gap + r*(cell_h+gap)
                x0 = gap + c*(cell_w+gap)
                canvas[y0:y0+cell_h, x0:x0+cell_w] = crop
                # border
                cv2.rectangle(canvas, (x0, y0), (x0+cell_w-1, y0+cell_h-1), 0, 2)

        # save
        out = out_dir/f"{Path(page_name).stem}_montage.png"
        cv2.imwrite(str(out), canvas)
        print("Wrote", out)

if __name__ == "__main__":
    main()
