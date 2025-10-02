#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib
import numpy as np, cv2, yaml
from scripts.common import read_json, write_json_atomic, latest_run_dir, sorted_pages, tpl_size, anchors_norm, residual_l2

def binarize(gray):
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, b = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return b

def refine_anchor(bin_img, approx_xy, win=60):
    h, w = bin_img.shape[:2]
    ax, ay = int(approx_xy[0]), int(approx_xy[1])
    x0, x1 = max(0, ax-win), min(w, ax+win)
    y0, y1 = max(0, ay-win), min(h, ay+win)
    roi = bin_img[y0:y1, x0:x1]
    if roi.size==0: return np.float32([ax, ay])
    cnts, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return np.float32([ax, ay])
    cnt = max(cnts, key=cv2.contourArea)
    M = cv2.moments(cnt)
    if M["m00"] == 0:
        cx, cy = cnt.reshape(-1,2).mean(axis=0)
    else:
        cx, cy = (M["m10"]/M["m00"], M["m01"]/M["m00"])
    return np.float32([x0+cx, y0+cy])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--search_px", type=int, default=60)
    ap.add_argument("--ransacth", type=float, default=3.0)
    args = ap.parse_args()

    tpl = read_json(args.template)
    tpl_w, tpl_h = tpl_size(tpl)
    anchors = anchors_norm(tpl)

    cfg = {}
    p = pathlib.Path("configs/ocr.yaml")
    if p.exists():
        try: cfg = yaml.safe_load(p.read_text())
        except Exception: cfg = {}
    align = (cfg or {}).get("alignment", {})
    warn_px = float(align.get("warn_residual_px", 4.5))
    fail_px = float(align.get("max_residual_px", 6.0))

    latest = latest_run_dir("artifacts")
    images_dir = latest/"images"; logs_dir = latest/"logs"; (latest/"overlays").mkdir(exist_ok=True)

    homos = {"template_size":{"w":tpl_w,"h":tpl_h},"pages":{},"thresholds":{"warn_px":warn_px,"fail_px":fail_px}}
    pages = sorted_pages(images_dir)
    if not pages: raise SystemExit("No page_*.png in images")

    for img_path in pages:
        img = cv2.imread(str(img_path)); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        b = binarize(gray); ih, iw = gray.shape[:2]

        approx = np.float32([[iw*a["x"], ih*a["y"]] for a in anchors])
        src = np.float32([refine_anchor(b, p, args.search_px) for p in approx])
        dst = np.float32([[tpl_w*a["x"], tpl_h*a["y"]] for a in anchors])

        M, _ = cv2.findHomography(src, dst, cv2.RANSAC, args.ransacth)
        if M is None or not np.all(np.isfinite(M)):
            sx, sy = tpl_w/iw, tpl_h/ih
            M = np.float32([[sx,0,0],[0,sy,0],[0,0,1]])

        residual = residual_l2(M, src, dst)
        quality = "ok" if residual <= warn_px else ("warn" if residual <= fail_px else "fail")
        Minv = np.linalg.inv(M)
        homos["pages"][img_path.name] = {"M":M.tolist(),"Minv":Minv.tolist(),"residual_px":residual,"quality":quality}

    write_json_atomic(logs_dir/"homography.json", homos)
    with open(logs_dir/"steps.jsonl","a") as f:
        f.write(json.dumps({"step":"align","run_dir":str(latest),"pages":len(homos["pages"])})+"\n")
    print(f"Wrote homography -> {logs_dir/'homography.json'}")

if __name__=="__main__":
    main()
