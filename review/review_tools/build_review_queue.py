#!/usr/bin/env python3
import argparse, json, math
from pathlib import Path
import pandas as pd
import yaml

def load_json(p): 
    p=Path(p); 
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--threshold", type=float, default=None)
    ap.add_argument("--near", type=float, default=0.03)
    ap.add_argument("--residual_fail_px", type=float, default=6.0)
    args = ap.parse_args()

    run = Path(args.run_dir)
    logs = run/"logs"
    ocr  = load_json(logs/"ocr_results.json")
    hom  = load_json(logs/"homography.json")

    # threshold
    th = args.threshold
    cfg_p = Path("configs/ocr.yaml")
    if th is None and cfg_p.exists():
        cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
        th = float((cfg.get("checkbox") or {}).get("fill_threshold", 0.55))
    if th is None:
        th = 0.55

    rows = []
    raw_rows = []
    for page_rec in ocr:
        page = page_rec.get("page")
        boxes = page_rec.get("checkboxes", [])
        for b in boxes:
            raw_rows.append({"page": page, **b})
        # per-question conflict/missing/near
        flags = {"conflict":0,"missing":0,"near":0}
        for qi in range(1,6):
            prefix = f"Q{qi}_"
            q = [b for b in boxes if b["id"].startswith(prefix)]
            checked = [b for b in q if b.get("checked")]
            if len(checked)>1: flags["conflict"] += 1
            if len(checked)==0: flags["missing"]  += 1
            near_any = any(abs(b.get("score",0)-th)<=args.near for b in q)
            flags["near"] += int(near_any)
        res = None
        qual = None
        if "pages" in hom and page in hom["pages"]:
            res = hom["pages"][page].get("residual_px")
            qual = hom["pages"][page].get("quality")
        bad = []
        if flags["conflict"]>0: bad.append("conflict")
        if flags["missing"]>0:  bad.append("missing")
        if flags["near"]>0:     bad.append("near-threshold")
        if res is not None and res > args.residual_fail_px: bad.append("high-residual")
        if bad:
            rows.append({
                "page": page, "quality": qual, "residual_px": res,
                "flags_conflict": flags["conflict"],
                "flags_missing": flags["missing"],
                "flags_near_threshold": flags["near"],
                "issues": ", ".join(bad),
                "recommended_action": "Manual review"
            })

    dfq = pd.DataFrame(rows, columns=["page","quality","residual_px","flags_conflict","flags_missing","flags_near_threshold","issues","recommended_action"])
    dfraw = pd.DataFrame(raw_rows)

    outdir = run/"review"
    outdir.mkdir(parents=True, exist_ok=True)
    dfq.to_csv(outdir/"review_queue.csv", index=False)
    with pd.ExcelWriter(outdir/"review_queue.xlsx", engine="openpyxl") as xl:
        dfq.to_excel(xl, index=False, sheet_name="Queue")
        if not dfraw.empty:
            dfraw.to_excel(xl, index=False, sheet_name="CheckboxRaw")

    print("Wrote:", outdir/"review_queue.csv")
    print("Wrote:", outdir/"review_queue.xlsx")

if __name__ == "__main__":
    main()
