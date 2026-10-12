#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Path 1 — writing-system → candidate-region routing for the overseas lane.

Cheapest possible "first cut": read the scripts present in any extracted text and
use them to (a) pre-filter candidate regions and (b) pick the correct OCR language
for a re-run of ocr.py. No network, no OCR engine required — it only needs the
text that intake_global.sh already produced in intake/ocr.json.

Unicode-range detection (no external libs) covers the high-value scripts:
  Cyrillic, Arabic/Persian, Devanagari, Hangul, Japanese kana, Thai, Lao, Khmer,
  Myanmar, Greek, Hebrew, Georgian, Armenian, Bengali, Tamil, Telugu, and Latin
  (with a light diacritic→language heuristic for Europe / Vietnam / Turkey).

Usage:
  python script_route.py --ocr intake/ocr.json
  python script_route.py --text "Москва улица" 
  python script_route.py photo.txt            # plain text file

Output: JSON {scripts, dominant, candidate_regions, recommended_ocr_langs, routing_hint}
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path


# ----------------------------------------------------------------- script spans
def _script_of(ch: str) -> str | None:
    # fast path: explicit script property where it's unambiguous
    o = ord(ch)
    # Hangul
    if 0xAC00 <= o <= 0xD7A3 or 0x1100 <= o <= 0x11FF or 0x3130 <= o <= 0x318F:
        return "Hangul"
    # Japanese kana
    if 0x3040 <= o <= 0x30FF:
        return "Kana"
    # CJK — treat Hans/Hant separately via the property below, but keep a fallback
    name = unicodedata.name(ch, "")
    for tag, label in (
        ("CYRILLIC", "Cyrillic"),
        ("ARABIC", "Arabic"),
        ("DEVANAGARI", "Devanagari"),
        ("THAI", "Thai"),
        ("LAO", "Lao"),
        ("KHMER", "Khmer"),
        ("MYANMAR", "Myanmar"),
        ("GREEK", "Greek"),
        ("HEBREW", "Hebrew"),
        ("GEORGIAN", "Georgian"),
        ("ARMENIAN", "Armenian"),
        ("BENGALI", "Bengali"),
        ("TAMIL", "Tamil"),
        ("TELUGU", "Telugu"),
    ):
        if tag in name:
            return label
    # Hani (Han ideographs) — split Hans/Hant by common Hant codepoints
    if "CJK" in name or "HAN" in name:
        return "Han"
    return None


# ------------------------------------------------------------- script → regions
SCRIPT_REGIONS = {
    "Cyrillic": {
        "regions": ["Russia", "Eastern Europe", "Central Asia"],
        "langs": ["ru", "uk", "bg", "sr", "mk"],
        "ocr": "cyrillic",
    },
    "Arabic": {
        "regions": ["MENA", "North Africa", "Sahel", "Iran (Persian)"],
        "langs": ["ar", "fa"],
        "ocr": "arabic",
    },
    "Devanagari": {
        "regions": ["India (Hindi/Marathi)", "Nepal"],
        "langs": ["hi", "mr", "ne"],
        "ocr": "devanagari",
    },
    "Hangul": {"regions": ["Korea"], "langs": ["ko"], "ocr": "ko"},
    "Kana": {"regions": ["Japan"], "langs": ["ja"], "ocr": "ja"},
    "Thai": {"regions": ["Thailand"], "langs": ["th"], "ocr": "thai"},
    "Lao": {"regions": ["Laos"], "langs": ["lo"], "ocr": "lao"},
    "Khmer": {"regions": ["Cambodia"], "langs": ["km"], "ocr": "khmer"},
    "Myanmar": {"regions": ["Myanmar"], "langs": ["my"], "ocr": "myanmar"},
    "Greek": {"regions": ["Greece"], "langs": ["el"], "ocr": "greek"},
    "Hebrew": {"regions": ["Israel"], "langs": ["he"], "ocr": "hebrew"},
    "Georgian": {"regions": ["Georgia"], "langs": ["ka"], "ocr": "georgian"},
    "Armenian": {"regions": ["Armenia"], "langs": ["hy"], "ocr": "armenian"},
    "Bengali": {"regions": ["Bangladesh", "East India"], "langs": ["bn"], "ocr": "bengali"},
    "Tamil": {"regions": ["South India", "Sri Lanka"], "langs": ["ta"], "ocr": "tamil"},
    "Telugu": {"regions": ["South India"], "langs": ["te"], "ocr": "telugu"},
    "Han": {
        "regions": ["Chinese mainland (Simplified)", "Taiwan, China / Hong Kong, China / Macao, China (Traditional)"],
        "langs": ["zh-Hans", "zh-Hant"],
        "ocr": "chinese",
        "note": "split Simplified/Traditional: if Traditional forms dominate → Taiwan, China / Hong Kong, China / Macao, China; Simplified → Chinese mainland (use the CN lane).",
    },
}

# Latin diacritic → likely language/region (weak but useful when no other script)
DIACRITIC_LANG = {
    "áéíóúñ¿¡": "es", "ãõçâêô": "pt", "åäö": "sv", "äöüß": "de",
    "àâçéèêëîïôùûüÿ": "fr", "èéìíîòóùú": "it", "ąćęłńóśźż": "pl",
    "şğİıçöü": "tr", "ăâîșț": "ro", "čćđšž": "hr/sr(lat)",
    "øæå": "da/no", "őű": "hu", "ảãẹẽọố": "vi",
}


def _latin_diacritic_hint(text: str) -> list[str]:
    found = Counter()
    for d, lang in DIACRITIC_LANG.items():
        for c in d:
            if c in text:
                found[lang] += 1
    return [l for l, _ in found.most_common(3)]


# --------------------------------------------------------------------- text io
def _load_text(args) -> str:
    if args.text:
        return args.text
    if args.ocr:
        p = Path(args.ocr)
        data = json.loads(p.read_text(encoding="utf-8"))
        # intake ocr.json shape varies; gather any string fields
        parts = []

        def _walk(o):
            if isinstance(o, str):
                parts.append(o)
            elif isinstance(o, dict):
                for v in o.values():
                    _walk(v)
            elif isinstance(o, list):
                for v in o:
                    _walk(v)

        _walk(data)
        return " ".join(parts)
    if args.file:
        return Path(args.file).read_text(encoding="utf-8", errors="ignore")
    return ""


def route(text: str) -> dict:
    counts: Counter = Counter()
    for ch in text:
        if not ch.isalpha():
            continue
        s = _script_of(ch)
        if s:
            counts[s] += 1
    total = sum(counts.values())
    scripts = {s: round(c / total, 3) if total else 0 for s, c in counts.most_common()}
    dominant = counts.most_common(1)[0][0] if counts else None

    candidate_regions: list[str] = []
    recommended: list[str] = []
    routing_hint = ""
    if dominant and dominant in SCRIPT_REGIONS:
        info = SCRIPT_REGIONS[dominant]
        candidate_regions = info["regions"]
        recommended = info["langs"]
        routing_hint = (
            f"Dominant script = {dominant}. Re-run OCR with --langs "
            f"{','.join(info['langs'])} and focus search on: {', '.join(info['regions'])}."
        )
        if info.get("note"):
            routing_hint += " " + info["note"]
    else:
        # Latin-only: diacritic heuristic
        di = _latin_diacritic_hint(text)
        if di:
            candidate_regions = [f"Europe/Latin-America (likely {di[0]})"]
            recommended = di
            routing_hint = (
                f"Only Latin with diacritics → likely {', '.join(di)}. "
                "Weak signal (Latin is near-global); confirm with architecture/plates."
            )
        else:
            candidate_regions = ["undetermined (Latin, no diacritics — near-global)"]
            routing_hint = "Latin without diacritics: near-global, no regional cut. Use other clues."

    return {
        "scripts": scripts,
        "dominant": dominant,
        "candidate_regions": candidate_regions,
        "recommended_ocr_langs": recommended,
        "routing_hint": routing_hint,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocr", help="intake/ocr.json produced by intake_global.sh")
    ap.add_argument("--file", help="plain text file")
    ap.add_argument("--text", help="inline text")
    args = ap.parse_args()
    text = _load_text(args)
    if not text.strip():
        print(json.dumps({"error": "no text supplied"}, ensure_ascii=False))
        return
    print(json.dumps(route(text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
