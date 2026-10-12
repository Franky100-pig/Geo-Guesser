#!/usr/bin/env bash
# gg_prep_batch.sh — parallel preps for a batch of overseas photos.
#
# Usage:
#   bash gg_prep_batch.sh [--stagger 8] photo1.jpg [photo2.jpg ...]
#   STAGGER=12 bash gg_prep_batch.sh *.jpg
#
# global_accuracy.sh preps are independent; running them in parallel cuts
# batch wall time from ~105s/photo to ~70-80s/photo (measured v3-style).
# Launches are staggered so baidu uploads do not fire simultaneously
# (simultaneous reverse-search uploads trip captchas).
# REGION=sea|eu|na|full is passed through to each run.
set -euo pipefail

STAGGER="${STAGGER:-8}"
PHOTOS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --stagger) STAGGER="$2"; shift 2 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) PHOTOS+=("$1"); shift ;;
  esac
done
if [ ${#PHOTOS[@]} -lt 1 ]; then
  sed -n '2,12p' "$0"
  exit 1
fi

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$(cd "$(dirname "${PHOTOS[0]}")" && pwd)"
RUNS=()
T0=$(date +%s)
for p in "${PHOTOS[@]}"; do
  name="$(basename "${p%.*}")"
  rd="$BASE/gg_batch_${name}_$(date +%H%M%S)"
  RUNS+=("$rd")
  echo "launch $(basename "$p") -> $rd (REGION=${REGION:-auto})"
  (
    s=$(date +%s)
    bash "$SELF/global_accuracy.sh" "$p" "$rd" > "$rd.log" 2>&1
    echo "$(basename "$p") done in $(( $(date +%s) - s ))s"
  ) &
  sleep "$STAGGER"
done
wait
echo "== batch summary (wall $(( $(date +%s) - T0 ))s for ${#PHOTOS[@]} photos) =="
for rd in "${RUNS[@]}"; do
  printf "  %-40s " "$(basename "$rd")"
  grep -h "total prep time" "$rd.log" 2>/dev/null | tail -1 || echo "FAILED (see $rd.log)"
done
