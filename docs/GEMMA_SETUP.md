# Gemma multimodal setup (options)

This drop‑in does **not** ship weights. You can call Gemma 4B/12B/27B via:

## Option A — OpenAI‑compatible HTTP endpoint
Set:
```
export GEMMA_ENDPOINT=https://your-endpoint/v1
export GEMMA_API_KEY=sk-...        # if your endpoint requires a key
export GEMMA_MODEL_ID=gemma-3-27b-it
```
Use `scripts/gemma_router.py` (OpenAI chat‑completions style).

## Option B — Google GenAI SDK
Install `pip install google-generativeai` and adapt `gemma_router.py` with your specific client call.

### Example
```
python scripts/gemma_router.py --image artifacts/<run>/images/page_0001.png   --prompt "Which answer is selected for Q1..Q5? Return JSON."   --out artifacts/<run>/logs/gemma_qas.json
```
