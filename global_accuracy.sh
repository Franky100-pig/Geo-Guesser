#!/usr/bin/env bash
# global_accuracy.sh — accuracy-first intake lane for NON-China photos.
#
# Speed is explicitly NOT the goal here (that is gg_fast.sh, the CN lane).
# This lane maximizes recall for overseas photos. Measured reality from CN
# (see CHINA_NETWORK_NOTES.md, 2026-10-12):
#   - baidu reverse image : works, but only landmark/postcard scenes
#   - yandex reverse image: captcha-blocked on every variant (dead)
#   - google lens / tineye / mapillary / kartaview: unreachable (timeout)
#   - yandex WEB search via WebFetch      : WORKS (strong on foreign content)
#   - WebSearch / WebFetch (server-side)  : WORKS (source hunting, captions)
# So the accuracy comes from: full intake + fine OCR + variant reverse search
# (this script) followed by agent-side reading, text search and source
# hunting (GLOBAL_ACCURACY_SOP.md).
#
# What this script does (deterministic prep, ~3-6 min, run in background):
#   1. full intake (OCR ON)                    metadata, edges, OCR, baidu vote
#   2. fine OCR pass (3x3 tiles, 3x upscale)   catches small signage text
#   3. baidu reverse search on EACH variant    crop/flip/gray/wb rescue path
#   4. board init + country hint
# Then it prints the agent SOP pointer and the file map.
#
# Usage:
#   bash global_accuracy.sh <photo> [run_dir]
#   e.g. bash global_accuracy.sh paris.jpg run_paris
set -euo pipefail

if [ $# -lt 1 ]; then
  sed -n '2,26p' "$0"
  exit 1
fi

PHOTO="$1"; shift
RUN="gg_global_$(date +%H%M%S)"
# optional 2nd positional = run dir (not an option, not an existing file)
if [ $# -gt 0 ] && [[ "$1" != -* ]] && [ ! -e "$1" ]; then
  RUN="$1"; shift
fi

SKILL="${GEO_SLEUTH_SKILL:-$HOME/.workbuddy/skills/geo-sleuth}"

mkdir -p "$RUN"
cp "$PHOTO" "$RUN/photo.jpg"
cd "$RUN"

echo "== [1/4] full intake (OCR on, baidu+yandex) =="
uv run "$SKILL/scripts/intake.py" photo.jpg --out-dir intake/ "$@" 2>&1 | tail -3 || true

echo "== [2/4] fine OCR pass (3x3 tiles, upscale 3) =="
uv run "$SKILL/scripts/ocr.py" photo.jpg --tiles 3x3 --upscale 3 \
  --out ocr_fine.json --draw ocr_fine.png 2>&1 | tail -2 || true

echo "== [3/4] variants + baidu reverse search on each =="
uv run "$SKILL/scripts/imgprep.py" variants photo.jpg --out-dir variants/ 2>&1 | tail -1 || true
uv run "$SKILL/scripts/revimg.py" variants/*.jpg --out-dir rev_vars/ --engines baidu 2>&1 | tail -3 || true

echo "== [4/4] board init =="
uv run "$SKILL/scripts/board.py" init --photo photo.jpg 2>&1 | tail -1 || true

cat <<'SOP'

== prep done. Now follow GLOBAL_ACCURACY_SOP.md (accuracy first, no clock) ==
  1. READ  : photo.jpg, intake/edges/*, ocr_fine.json, each rev_vars/*_baidu.json
             + consult VISION_CLUES.md while reading
  2. TEXT  : any text found? -> phone_lookup.py (numbers)
             -> WebSearch / Yandex-text (WebFetch) / revimg.py --query bing
  3. SOURCE: any URL / filename / watermark / EXIF hint?
             -> WebSearch + WebFetch the source page; captions name places
  4. VERIFY: hypothesis -> poi.py (OSM/so.com) + sat_global.py (needs GEO_PROXY)
  5. RECORD: board.py clue/add/rank/report + evidence_sheet.py
SOP

echo "== file map =="
echo "  intake/intake.md            baidu vote + OCR + metadata"
echo "  ocr_fine.json               fine-pass OCR text (small signage)"
echo "  rev_vars/                   per-variant baidu guesses + contact sheets"
echo "  variants/                   flip/gray/up/wb search variants"
echo "  board.json                  evidence board"
