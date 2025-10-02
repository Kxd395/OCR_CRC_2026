# scripts/common.py
from __future__ import annotations
import json, pathlib, tempfile, os
import numpy as np, cv2

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_atomic(path, obj, indent=2):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent)) as tf:
        json.dump(obj, tf, indent=indent)
        tmp = tf.name
    os.replace(tmp, path)

def latest_run_dir(root="artifacts"):
    root = pathlib.Path(root)
    runs = sorted([p for p in root.glob("*") if p.is_dir()])
    if not runs: raise FileNotFoundError("No artifacts runs found")
    return runs[-1]

def sorted_pages(images_dir):
    return sorted(pathlib.Path(images_dir).glob("page_*.png"))

def tpl_size(tpl):
    page = tpl.get("page_size", {"width_px": 2550, "height_px": 3300})
    return int(page["width_px"]), int(page["height_px"])

def anchors_norm(tpl):
    return tpl["anchors_norm"] if "anchors_norm" in tpl else tpl["anchors"]

def roi_to_poly(roi, tpl_w, tpl_h):
    tx = roi["x"] * tpl_w; ty = roi["y"] * tpl_h
    tw = roi["w"] * tpl_w; th = roi["h"] * tpl_h
    return np.float32([[tx, ty],[tx+tw, ty],[tx+tw, ty+th],[tx, ty+th]])

def apply_h(M, pts):
    pts_h = np.hstack([pts, np.ones((pts.shape[0],1))])
    out = (M @ pts_h.T).T
    return out[:,:2] / out[:,2:3]

def residual_l2(M, src, dst):
    src_h = np.hstack([src, np.ones((src.shape[0],1))])
    proj = (M @ src_h.T).T
    proj = proj[:,:2] / proj[:,2:3]
    return float(np.linalg.norm(proj - dst, axis=1).mean())
