#!/usr/bin/env bash
# gg_fast.sh — one-command fast lane for geo-sleuth (China network)
#
# What it does in ONE call (so the agent spends zero orchestration time):
#   1. copies the photo into a fresh run dir
#   2. starts Baidu-only, no-OCR intake in the BACKGROUND (~55s)
#   3. inits the candidate board (country=cn)
#   4. crops the two likely signboard regions + edge crops
#   5. prints the wait command and next actions
#
# Usage:
#   bash gg_fast.sh <photo> [run_dir]
#
# Env:
#   GEO_SLEUTH_SKILL  path to geo-sleuth skill (default ~/.workbuddy/skills/geo-sleuth)
#
# macOS-only: uses sips for image dimensions.
set -euo pipefail

PHOTO="$1"
RUN="${2:-gg_run_$(date +%H%M%S)}"
SKILL="${GEO_SLEUTH_SKILL:-$HOME/.workbuddy/skills/geo-sleuth}"
S="$SKILL/scripts"

mkdir -p "$RUN"
cp "$PHOTO" "$RUN/photo.jpg"
cd "$RUN"

# 1) background intake — the ONLY long step, and it must never block us
uv run "$S/intake.py" photo.jpg --out-dir intake/ --no-ocr --engines baidu > intake.log 2>&1 &
INTAKE_PID=$!

# 2) board + crops while intake runs
uv run "$S/board.py" init --photo photo.jpg >/dev/null
uv run "$S/board.py" country cn >/dev/null 2>&1 || true

W=$(sips -g pixelWidth photo.jpg | awk '/pixelWidth/{print $2}')
H=$(sips -g pixelHeight photo.jpg | awk '/pixelHeight/{print $2}')

# right and left thirds of the shop-line band (signboards live there in most pano shots)
uv run "$S/imgprep.py" zoom photo.jpg --box "$((W*62/100)),$((H*22/100)),$W,$((H*48/100))" --scale 4 --out z_sign_right.png >/dev/null
uv run "$S/imgprep.py" zoom photo.jpg --box "0,$((H*22/100)),$((W*38/100)),$((H*48/100))" --scale 4 --out z_sign_left.png >/dev/null
uv run "$S/imgprep.py" edges photo.jpg --out-dir edges/ >/dev/null

echo "run dir : $RUN"
echo "intake  : pid $INTAKE_PID (~55s, log intake.log)"
echo "crops   : z_sign_right.png  z_sign_left.png  edges/"
echo
echo "NEXT (agent SOP):"
echo "  T+15s  Read z_sign_right.png / z_sign_left.png -> extract any phone numbers + addresses"
echo "  T+20s  Fire ALL verification searches in ONE parallel batch:"
echo "           - '<full phone number>'            (business listing)"
echo "           - '<7-digit prefix> 归属地'         (carrier region)"
echo "           - '<road+number> 邮编/登记'         (address registry)"
echo "  T+60s  Read intake/intake.md + intake/rev/photo_baidu_similar.jpg (baidu vote)"
echo "         -> treat generic tags (老街/街景) as WEAK; near-duplicates only"
echo "  T+90s  Cross-lock evidence -> conclude -> write report"
echo "  then:  wait $INTAKE_PID   (only if intake results still needed)"
