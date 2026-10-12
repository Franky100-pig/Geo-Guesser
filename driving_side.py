#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""左右行 (left/right-hand traffic) — a cheap, decisive regional-elimination clue.

If you can tell which side traffic flows on (from a dashcam, the position of the
driver's seat, or which side pedestrians/vehicles keep to), you instantly split
the planet. This module is a static reference + an elimination helper.

Data source: standard LHT/RHT country lists (kept as a compact set; ~70 LHT
territories, the rest of the world is RHT). Used as a *narrowing* clue, not a
proof — a handful of borders are ambiguous and some territories are exceptions.

Usage:
  python driving_side.py --side left        # we observed LEFT-hand traffic
  python driving_side.py --side right
  python driving_side.py --list             # print the LHT territory set
"""
from __future__ import annotations

import argparse
import json

# Territories that drive on the LEFT (LHT). Everything not listed is RHT.
LEFT_DRIVE = {
    # Asia
    "India", "Pakistan", "Bangladesh", "Nepal", "Bhutan", "Sri Lanka", "Maldives",
    "Indonesia", "Thailand", "Malaysia", "Singapore", "Brunei", "East Timor",
    "Japan", "Hong Kong", "Macau",
    # Oceania
    "Australia", "New Zealand", "Fiji", "Papua New Guinea", "Solomon Islands",
    "Vanuatu", "Samoa", "Tonga", "Kiribati", "Tuvalu", "Nauru",
    # Africa
    "Kenya", "Tanzania", "Uganda", "South Africa", "Zimbabwe", "Botswana",
    "Zambia", "Malawi", "Mozambique", "Lesotho", "Swaziland", "Namibia",
    "Lesotho", "Seychelles", "Mauritius", "Madagascar", "Comoros",
    # Europe
    "United Kingdom", "Ireland", "Cyprus", "Malta",
    # Americas
    "Guyana", "Suriname", "Jamaica", "Trinidad and Tobago", "Barbados",
    "Bahamas", "Belize", "Antigua and Barbuda", "Dominica", "Grenada",
    "Saint Lucia", "Saint Vincent", "Saint Kitts",
}


def eliminate(side: str) -> dict:
    """Given the observed side, return the opposite set as 'eliminated'."""
    side = side.strip().lower()
    if side not in ("left", "right"):
        return {"error": "side must be 'left' or 'right'"}
    observed_lht = side == "left"
    if observed_lht:
        eliminated = "everywhere except the LHT territories below"
        kept = sorted(LEFT_DRIVE)
    else:
        eliminated = "all LHT territories (left-driving countries)"
        kept = "the rest of the world (right-hand traffic)"
    return {
        "observed_side": side,
        "eliminated": eliminated,
        "kept_lht_territories": kept if observed_lht else None,
        "note": "Narrowing clue only — verify with a second independent clue (script, plates, architecture).",
    }


VISION_PROMPT = (
    "Driving side: which side of the road do vehicles keep to? "
    "Driver seat on the RIGHT + traffic on the LEFT → LEFT-hand-traffic countries "
    "(UK, Ireland, India, Japan, Thailand, Indonesia, Australia, NZ, Singapore, "
    "Malaysia, Kenya, South Africa, …). Driver seat on the LEFT + traffic on the "
    "RIGHT → the rest of the world. Report 'left' or 'right'."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--side", choices=["left", "right"], help="observed traffic side")
    ap.add_argument("--list", action="store_true", help="print LHT territories")
    args = ap.parse_args()
    if args.list:
        print(json.dumps(sorted(LEFT_DRIVE), ensure_ascii=False, indent=2))
        return
    if args.side:
        print(json.dumps(eliminate(args.side), ensure_ascii=False, indent=2))
        return
    print(VISION_PROMPT)


if __name__ == "__main__":
    main()
