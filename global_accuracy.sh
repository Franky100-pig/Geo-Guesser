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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Region profiles (speed optimization, measured v3) ----------------------
# REGION=sea|eu|na|full|auto (default auto = decide from OCR text routing).
# Rationale (v3 blind test + v2): baidu variant reverse search is high-yield
# for SE/East Asia (Chinese travel blogs cover it) but near-zero for NA/EU
# web photos, where source-hunt is the only real lever. Full profile keeps
# every variant as the safe default for unknown photos.
#   full : baidu on photo (intake) + flip + gray + wb   [most recall, slowest]
#   sea  : baidu on photo (intake) + flip                (gray/wb redundant)
#   eu/na: baidu on photo (intake) only                  (variants add ~40s
#          of baidu calls that returned noise for every NA/EU photo so far)
REGION="${REGION:-auto}"

T_START=$(date +%s)
step_time() { echo "   [$1] $(( $(date +%s) - $2 ))s"; }

mkdir -p "$RUN"
cp "$PHOTO" "$RUN/photo.jpg"
cd "$RUN"

echo "== [1/4] full intake (OCR on, baidu+yandex) =="
t=$(date +%s)
uv run "$SKILL/scripts/intake.py" photo.jpg --out-dir intake/ "$@" 2>&1 | tail -3 || true
step_time intake "$t"

if [ "$REGION" = "auto" ]; then
  REGION=$(python3 "$SCRIPT_DIR/script_route.py" --ocr intake/intake.json 2>/dev/null | python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception: print('full'); sys.exit()
regs=' '.join(d.get('candidate_regions') or [])
if any(k in regs for k in ('SE-Asia','South-Asia','East-Asia')): print('sea')
elif 'Europe' in regs: print('eu')
elif 'America' in regs: print('na')
else: print('full')
")
fi
case "$REGION" in
  sea)   VARIANTS="variants/photo_flip.jpg" ;;
  eu|na) VARIANTS="" ;;
  *)     REGION=full; VARIANTS="variants/photo_flip.jpg variants/photo_gray.jpg variants/photo_wb.jpg" ;;
esac
echo "== region profile: $REGION (set REGION=sea|eu|na|full to override) =="

echo "== [2/4] fine OCR pass (3x3 tiles, upscale 3) =="
t=$(date +%s)
uv run "$SKILL/scripts/ocr.py" photo.jpg --tiles 3x3 --upscale 3 \
  --out ocr_fine.json --draw ocr_fine.png 2>&1 | tail -2 || true
step_time fine-ocr "$t"

echo "== [3/4] variants + baidu reverse search ($REGION profile) =="
t=$(date +%s)
uv run "$SKILL/scripts/imgprep.py" variants photo.jpg --out-dir variants/ 2>&1 | tail -1 || true
if [ -n "$VARIANTS" ]; then
  # shellcheck disable=SC2086
  uv run "$SKILL/scripts/revimg.py" $VARIANTS --out-dir rev_vars/ --engines baidu 2>&1 | tail -3 || true
else
  echo "   skipped variant reverse search ($REGION profile: baidu variants are noise here)"
fi
step_time variants+rev "$t"

echo "== [4/4] board init =="
uv run "$SKILL/scripts/board.py" init --photo photo.jpg 2>&1 | tail -1 || true

echo "== [5/5] routing: script->region, sun/hemisphere, driving side =="
OCR_SRC="ocr_fine.json"
[ -s "$OCR_SRC" ] || OCR_SRC="intake/intake.json"
if python3 "$SCRIPT_DIR/script_route.py" --ocr "$OCR_SRC" > routing.json 2>/dev/null && [ -s routing.json ]; then
  echo "  script routing : $(python3 -c "import json,sys;d=json.load(open('routing.json'));print(d.get('routing_hint','?'))" 2>/dev/null || echo 'see routing.json')"
else
  echo "  script routing : no text extracted yet — re-run script_route.py after reading signs"
fi
if python3 "$SCRIPT_DIR/sun_hint.py" --exif intake/exif.json > sun_hint.json 2>/dev/null && [ -s sun_hint.json ]; then
  python3 - <<'PY' 2>/dev/null || echo "  sun/hemisphere : see sun_hint.json"
import json
d = json.load(open("sun_hint.json"))
if d.get("hemisphere"):
    print(f"  sun/hemisphere : {d['hemisphere']} hemisphere, {d.get('latitude_band')}")
    if d.get("verdict"):
        print(f"                   {d['verdict']}")
else:
    print("  sun/hemisphere : no GPS/time in EXIF -> measure shadows manually (sun_hint.py --manual)")
PY
else
  echo "  sun/hemisphere : exif empty (screenshots/forwarded images) — measure shadows manually"
fi
echo "  driving side   : which side does traffic keep to? (UK/JP/IN/AU/ID/KE=LEFT; rest=RIGHT)"
echo "                   -> python3 $SCRIPT_DIR/driving_side.py --side left|right   (eliminates half the planet)"

cat <<'SOP'

== prep done. Now follow GLOBAL_ACCURACY_SOP.md (accuracy first, no clock) ==
  -1. FIRST ANSWER (T+0, FIRST_ANSWER.md): you already did the 10s glance
             when the photo arrived -> country/city + confidence + one-line
             why, written down. Every step below classifies new evidence as
             confirms / refines / overturns (record what overturned it).
  0. ROUTE : read routing.json (script -> candidate regions) + sun_hint.json
             (hemisphere/band) BEFORE deep reading; they cut the search space
             first, then driving_side.py --side <observed> eliminates further
  1. READ  : photo.jpg, intake/edges/*, ocr_fine.json, each rev_vars/*_baidu.json
             + consult VISION_CLUES.md while reading
  2. TEXT  : any text found? -> phone_lookup.py (numbers)
             -> WebSearch / Yandex-text (WebFetch) / revimg.py --query bing
  3. SOURCE: any URL / filename / watermark / EXIF hint?
             -> WebSearch + WebFetch the source page; captions name places
             -> python3 $SCRIPT_DIR/pin_title_mine.py .   (mines rev source
                page titles for place names, ~30s, often the fastest hit)
  4. VERIFY: hypothesis -> poi.py (OSM/so.com) + sat_global.py (needs GEO_PROXY)
  5. RECORD: board.py clue/add/rank/report + evidence_sheet.py
SOP

echo "== file map =="
echo "  routing.json                script->region routing (path 1)"
echo "  sun_hint.json               hemisphere/band + shadow sanity check (path 5)"
echo "  intake/intake.md            baidu vote + OCR + metadata"
echo "  ocr_fine.json               fine-pass OCR text (small signage)"
echo "  rev_vars/                   per-variant baidu guesses + contact sheets"
echo "  variants/                   flip/gray/up/wb search variants"
echo "  board.json                  evidence board"
echo ""
echo "== total prep time: $(( $(date +%s) - T_START ))s (region=$REGION) =="
