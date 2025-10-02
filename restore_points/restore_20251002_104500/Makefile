SHELL := /bin/bash

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install -U pip && $(PIP) install -r requirements.txt
	@echo "Environment ready."

run-initial: ingest align overlays

ingest:
	$(PY) scripts/ingest_pdf.py --pdf data/review/training_data/scans.pdf

align:
	$(PY) scripts/check_alignment.py --template templates/crc_survey_l_anchors_v1/template.json

overlays:
	$(PY) scripts/make_overlays.py --template templates/crc_survey_l_anchors_v1/template.json

ocr:
	$(PY) scripts/run_ocr.py --template templates/crc_survey_l_anchors_v1/template.json

qa:
	$(PY) scripts/qa_overlay_from_results.py --template templates/crc_survey_l_anchors_v1/template.json

validate:
	$(PY) scripts/validate_run.py --template templates/crc_survey_l_anchors_v1/template.json --fail-on-error

expand-grid:
	$(PY) scripts/expand_grid.py --in templates/crc_survey_l_anchors_v1/grid.json --out templates/crc_survey_l_anchors_v1/template.json --doc_id crc_survey_l_anchors_v1 --version 1.0.0

clean-artifacts:
	rm -rf artifacts/* || true
