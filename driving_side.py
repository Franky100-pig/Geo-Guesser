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
  python driving_side.py --country Japan    # look up one place -> left/right
  python driving_side.py --list             # print the LHT territory set
  python driving_side.py --how              # how to read the side in a photo
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


def canonical(name: str) -> str:
    """Resolve a spelling variant to the canonical LHT-set name."""
    key = " ".join(name.strip().lower().split())
    if key in ALIASES:
        return ALIASES[key]
    for place in LEFT_DRIVE:
        if place.lower() == key:
            return place
    return name.strip()


def lookup(country: str) -> dict:
    """Look up ONE place instead of eliminating from an observed side."""
    place = canonical(country)
    is_lht = place in LEFT_DRIVE
    return {
        "place": place,
        "side": "left" if is_lht else "right",
        "in_lht_set": is_lht,
        "note": ("Listed as LHT; still confirm in the photo."
                 if is_lht else
                 "Not in the LHT set → RHT. The set is non-exhaustive for tiny "
                 "dependencies, so verify an unusual territory externally."),
        "exceptions": NEAR_BORDER_EXCEPTIONS,
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
        "exceptions": NEAR_BORDER_EXCEPTIONS,
    }


HOW_TO_OBSERVE = """How to read the driving side when the steering wheel is not visible:

1. Parked cars: which direction do they nose into the kerb? Cars parked
   against the flow are the exception, so read several, not one.
2. A bus / truck on the far carriageway shows the driver-seat side, and bus
   doors face the kerb the bus serves.
3. Windscreen wipers and door mirrors are biased toward the driver's side.
4. Roundabout circulation: clockwise = LHT. Roundabouts are rare in North
   America and mainland China, common in the UK, France and Australia.
5. One-way arrows, lane arrows at a junction, and which lane a turning
   vehicle occupies all reveal the flow direction.
6. Toll booths / drive-through windows sit on the driver's side.
7. Pedestrian "look left / look right" road markings (tourist areas) name the
   side explicitly.
8. A photo or video may be MIRRORED — check reversed text and plates first.

Report 'left' or 'right'. Then combine with a second independent clue
(script, plate format, road-sign family in ROAD_SIGNS.md) before excluding
any candidate. Border cases: """ + NEAR_BORDER_EXCEPTIONS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--side", choices=["left", "right"], help="observed traffic side")
    ap.add_argument("--country", help="look up one place -> left/right")
    ap.add_argument("--list", action="store_true", help="print LHT territories")
    ap.add_argument("--how", action="store_true", help="how to read the side in a photo")
    args = ap.parse_args()
    if args.list:
        print(json.dumps(sorted(LEFT_DRIVE), ensure_ascii=False, indent=2))
        return
    if args.country:
        print(json.dumps(lookup(args.country), ensure_ascii=False, indent=2))
        return
    if args.side:
        print(json.dumps(eliminate(args.side), ensure_ascii=False, indent=2))
        return
    if args.how:
        print(HOW_TO_OBSERVE)
        return
    print(HOW_TO_OBSERVE)


if __name__ == "__main__":
    main()
