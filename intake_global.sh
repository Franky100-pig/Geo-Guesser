#!/usr/bin/env bash
# intake_global.sh — full-engine intake for NON-China photos.
#
# Counterpart of gg_fast.sh (which is the CN lane: baidu-only, no OCR).
# For photos taken outside China:
#   - keep OCR on: latin/other signage text is far more informative than the
#     CN-UI-only text that made us disable it in the CN lane
#   - use ALL reverse-image engines (google lens / yandex / bing are much
#     stronger than baidu outside China)
#   - from a CN machine the global engines usually need a proxy:
#       export GEO_PROXY=http://127.0.0.1:<port>   # your VPN's http proxy
#     intake.py inherits the env var automatically.
#
# Usage:
#   bash intake_global.sh <photo> [run_dir] [extra intake.py args...]
#   e.g. bash intake_global.sh paris.jpg run1 --region FR
#
# Expect a longer runtime than the CN lane (OCR + 3-4 engines); run it in the
# background and prep crops in parallel, same as gg_fast.sh does.
set -euo pipefail

if [ $# -lt 1 ]; then
  sed -n '2,25p' "$0"
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

echo "run dir : $RUN  (full engines + OCR; needs global reachability or GEO_PROXY)"
exec uv run "$SKILL/scripts/intake.py" photo.jpg --out-dir intake/ "$@"
