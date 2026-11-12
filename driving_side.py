#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""左右行 (left/right-hand traffic) — a cheap, decisive regional-elimination clue.

If you can tell which side traffic flows on (from a dashcam, the position of the
driver's seat, or which side pedestrians/vehicles keep to), you instantly split
the planet. This module is a static reference + an elimination helper.

Data source: standard LHT/RHT country lists (a compact, non-exhaustive set of
LHT territories; the rest of the world is RHT). Used as a *narrowing* clue,
not a proof — a handful of borders are ambiguous and some territories are
exceptions.

Usage:
  python driving_side.py --side left        # we observed LEFT-hand traffic
  python driving_side.py --side right
  python driving_side.py --list             # print the LHT territory set
"""
from __future__ import annotations

import argparse
import json

# Territories that drive on the LEFT (LHT). Everything not listed is RHT.
# Non-exhaustive: a few small dependencies are omitted (see NOTE below).
# Corrected 2026-11-12 against RAC, drivingdirectionsandmaps.com, mapsofworld
# and the 道路通行方向 survey — the previous set wrongly listed Belize,
# Madagascar, Comoros and Vanuatu (all RHT) and repeated Lesotho.
LEFT_DRIVE = {
    # Asia
    "Bangladesh", "Bhutan", "Brunei", "India", "Indonesia", "Japan",
    "Malaysia", "Maldives", "Nepal", "Pakistan", "Singapore", "Sri Lanka",
    "Thailand", "Timor-Leste", "Hong Kong (China)", "Macau (China)",
    # Oceania
    "Australia", "New Zealand", "Fiji", "Papua New Guinea", "Solomon Islands",
    "Samoa", "Tonga", "Kiribati", "Tuvalu", "Nauru", "Cook Islands",
    "Niue", "Tokelau", "Christmas Island", "Cocos (Keeling) Islands",
    "Norfolk Island", "Pitcairn Islands",
    # Africa
    "Botswana", "Kenya", "Lesotho", "Malawi", "Mauritius", "Mozambique",
    "Namibia", "Seychelles", "South Africa", "Eswatini", "Tanzania",
    "Uganda", "Zambia", "Zimbabwe",
    # Europe
    "United Kingdom", "Ireland", "Cyprus", "Malta", "Isle of Man",
    "Jersey", "Guernsey", "Alderney",
    # Americas
    "Anguilla", "Antigua and Barbuda", "Bahamas", "Barbados", "Bermuda",
    "British Virgin Islands", "Cayman Islands", "Dominica", "Falkland Islands",
    "Grenada", "Guyana", "Jamaica", "Montserrat", "Saint Helena",
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines",
    "Suriname", "Trinidad and Tobago", "Turks and Caicos Islands",
    "United States Virgin Islands",
}

# Spelling variants the agent may type / read off a map.
ALIASES = {
    "swaziland": "Eswatini",
    "east timor": "Timor-Leste",
    "timor leste": "Timor-Leste",
    "hong kong": "Hong Kong (China)",
    "macau": "Macau (China)",
    "macao": "Macau (China)",
    "uk": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "st kitts": "Saint Kitts and Nevis",
    "st vincent": "Saint Vincent and the Grenadines",
    "st lucia": "Saint Lucia",
    "us virgin islands": "United States Virgin Islands",
    "british virgin islands": "British Virgin Islands",
}

# Border / sovereignty cases where the surrounding country is NOT a guide.
NEAR_BORDER_EXCEPTIONS = (
    "Mainland China is RHT while Hong Kong (China) and Macau (China) are LHT; "
    "the US is RHT while the US Virgin Islands are LHT; Gibraltar is RHT "
    "although the UK is LHT; Okinawa switched back to LHT in 1978 and Samoa "
    "switched to LHT in 2009 — old photos can show the other side."
)


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
