#!/usr/bin/env python3
import argparse, json

def expand_grid(grid):
    origin = grid["origin"]; cell = grid["cell"]
    rspace = grid["row_spacing"]; cspace = grid["col_spacing"]
    rows = grid["rows"]; cols = grid["cols"]; labels = grid["labels"]
    roi_frac = grid.get("roi_fraction_of_cell", {"w":0.28,"h":0.60})

    rois = []
    for r in range(rows):
        for c in range(cols):
            cx = origin["x"] + c * cspace
            cy = origin["y"] + r * rspace
            rx = cx + (cell["width"] - cell["width"]*roi_frac["w"])/2.0
            ry = cy + (cell["height"] - cell["height"]*roi_frac["h"])/2.0
            rw = cell["width"] * roi_frac["w"]
            rh = cell["height"] * roi_frac["h"]
            rois.append({"id": f"{labels[r]}_{c}", "x": round(rx,3), "y": round(ry,3), "w": round(rw,3), "h": round(rh,3)})
    return rois

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--doc_id", default="crc_survey_l_anchors_v1")
    ap.add_argument("--version", default="1.0.0")
    args = ap.parse_args()

    src = json.load(open(args.inp))
    rois = expand_grid(src["checkbox_grid"])
    tpl = {
        "document_type_id": args.doc_id,
        "version": args.version,
        "description": src.get("description","expanded grid"),
        "page_size": src.get("page"),
        "anchors_norm": src["anchors"],
        "checkbox_rois_norm": rois
    }
    json.dump(tpl, open(args.out,"w"), indent=2)
    print(f"Wrote {args.out} with {len(rois)} rois.")

if __name__=="__main__":
    main()
