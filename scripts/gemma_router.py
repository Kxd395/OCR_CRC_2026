#!/usr/bin/env python3
import argparse, base64, json, os, requests
from pathlib import Path

def b64_image(path):
    b = Path(path).read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("utf-8")

def call_openai_like(endpoint, api_key, model, prompt, image_path, timeout=60):
    url = endpoint.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": [
            {"role":"user","content":[
                {"type":"text","text": prompt},
                {"type":"image_url","image_url":{"url": b64_image(image_path)}}
            ]}
        ],
        "temperature": 0.0
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
    r.raise_for_status()
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=os.getenv("GEMMA_MODEL_ID","gemma-3-12b-it"))
    ap.add_argument("--endpoint", default=os.getenv("GEMMA_ENDPOINT","http://localhost:8000/v1"))
    ap.add_argument("--api_key", default=os.getenv("GEMMA_API_KEY",""))
    ap.add_argument("--timeout", type=int, default=int(os.getenv("GEMMA_TIMEOUT","60")))
    args = ap.parse_args()

    text = call_openai_like(args.endpoint, args.api_key, args.model, args.prompt, args.image, timeout=args.timeout)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"Wrote {args.out}")

if __name__=="__main__":
    main()
