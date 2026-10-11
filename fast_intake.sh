#!/usr/bin/env bash
# Fast geo-sleuth intake for China: Baidu-only reverse image search, skip OCR.
#
# The full `intake.py` takes ~190s (OCR 119s + baidu 55s + yandex 16s). For a
# country/city/area answer you only need the Baidu reverse search (the OCR and
# Yandex are near-useless for Chinese screenshots / inside China). This cuts
# intake to ~60s.
#
# Run it in the BACKGROUND so you can do board.py init / imgprep.py edges in
# parallel (the foreground work costs ~10-15s and does not block on intake):
#
#     bash fast_intake.sh photo.jpg intake/ &
#     # ... board.py init / country / clue + imgprep.py edges ...
#     wait   # or just read intake/intake.md once it finishes
#
# Usage: fast_intake.sh <photo> [out-dir=intake]
set -euo pipefail

SKILL="${GEO_SLEUTH_SKILL:-$HOME/.workbuddy/skills/geo-sleuth}"
export CLAUDE_SKILL_DIR="$SKILL"

PHOTO="$1"
OUT="${2:-intake}"

if [ ! -f "$PHOTO" ]; then
  echo "usage: fast_intake.sh <photo> [out-dir]" >&2
  exit 2
fi

uv run "$SKILL/scripts/intake.py" "$PHOTO" --out-dir "$OUT" --no-ocr --engines baidu
