#!/usr/bin/env bash
# tools/rename_artifact.sh <run_dir> [NOTE="your note"]
set -euo pipefail
SRC="${1:-}"
NOTE="${NOTE:-run}"
if [[ -z "$SRC" || ! -d "$SRC" ]]; then
  echo "Usage: NOTE='your note' tools/rename_artifact.sh <artifacts/run_dir>" >&2
  exit 1
fi
BASE="$(basename "$SRC")"
ROOT="$(dirname "$SRC")"
STAMP=$(TZ="America/New_York" date -j -f "%Y%m%d_%H%M%S" "$BASE" "+%Y-%m-%d_%H-%M-%S_%Z")
SLUG=$(echo "$NOTE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')
DST="${ROOT}/${STAMP}__${SLUG}"
if [[ -e "$DST" ]]; then
  i=1; while [[ -e "${DST}--$i" ]]; do i=$((i+1)); done; DST="${DST}--$i"
fi
mv "$SRC" "$DST"
echo "$DST"
