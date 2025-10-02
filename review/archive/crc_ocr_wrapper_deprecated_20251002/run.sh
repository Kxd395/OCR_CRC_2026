#!/usr/bin/env bash
set -euo pipefail
python3 wrapper/app.py --pdf "${1:-data/review/training_data/scans.pdf}" --template "${2:-templates/crc_survey_l_anchors_v1/template.json}" --export "${3:-exports/surveys_latest.xlsx}" ${@:4}
