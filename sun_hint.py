#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Path 5 — hemisphere / sun-angle narrowing for the overseas lane.

Thin wrapper over geo-sleuth's sun.py (NOAA solar position). Three situations:

  A. EXIF has GPS + capture time:
     -> hemisphere + latitude band are known; compute the EXPECTED shadow
        bearing at capture time. If you also measured a shadow bearing in the
        photo, we sanity-check location vs time (a mismatch > tol flags that
        the GPS was stripped/wrong or the photo is a re-post).

  B. No GPS, but capture time + a measured shadow bearing (or shadow ratio):
     -> run sun.py `locate` over a world bbox and report the matching latitude
        bands = hemisphere + band candidates.

  C. Nothing measurable: print what to look for instead.

Usage:
  python sun_hint.py --exif intake/exif.json
  python sun_hint.py --exif intake/exif.json --shadow-bearing 320
  python sun_hint.py --time 2026-08-15T16:20 --shadow-bearing 60 --ratio 1.2
  python sun_hint.py --manual          # what to measure when nothing is known
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent  # not used; skill comes from env
DEFAULT_SKILL = Path.home() / ".workbuddy/skills/geo-sleuth"
SUN = DEFAULT_SKILL / "scripts" / "sun.py"
WORLD_BBOX = "-60,-170,78,180"

LAT_BANDS = [
    (23.44, 90, "northern temperate/polar"),
    (0, 23.44, "northern tropics"),
    (-23.44, 0, "southern tropics"),
    (-90, -23.44, "southern temperate/polar"),
]


def lat_band(lat: float) -> str:
    for lo, hi, name in LAT_BANDS:
        if lo <= lat <= hi:
            return name
    return "unknown"


def _run_sun(args: list[str]) -> dict | None:
    cmd = ["uv", "run", "-q", str(SUN), *args]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    lines = [l for l in (out.stdout or "").strip().splitlines() if l.strip()]
    for line in reversed(lines):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def _parse_dt(exif: dict) -> tuple[datetime | None, str]:
    """Return (utc datetime, tz note)."""
    dt_s = exif.get("DateTimeOriginal") or exif.get("DateTime")
    off = exif.get("OffsetTimeOriginal", "+00:00")
    if not dt_s:
        return None, "no capture time in EXIF"
    try:
        dt = datetime.strptime(dt_s.strip("\x00 "), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None, f"unparseable DateTimeOriginal {dt_s!r}"
    try:
        tz = timezone(timedelta(hours=int(off[:3]), minutes=int(off[0] + off[4:6])))
    except Exception:  # noqa: BLE001
        tz = timezone.utc
    return dt.replace(tzinfo=tz).astimezone(timezone.utc), f"local offset {off}"


def mode_exif(path: Path, shadow_bearing: float | None, tol: float) -> dict:
    exif = json.loads(path.read_text(encoding="utf-8"))
    out: dict = {"mode": "exif", "exif_file": str(path)}
    gps = exif.get("gps_wgs84")
    dt_utc, tz_note = _parse_dt(exif)
    out["capture_time_utc"] = dt_utc.isoformat() if dt_utc else None
    out["tz_note"] = tz_note

    if gps:
        lat, lon = gps
        out["hemisphere"] = "northern" if lat >= 0 else "southern"
        out["latitude_band"] = lat_band(lat)
        out["gps_wgs84"] = gps
        out["image_direction_deg"] = exif.get("image_direction_deg")

    if gps and dt_utc:
        pos = _run_sun(["pos", "--at", f"{gps[0]},{gps[1]}", "--time", dt_utc.strftime("%Y-%m-%dT%H:%M")])
        if pos:
            out["expected_at_capture"] = {
                "sun_azimuth": pos.get("sun_azimuth"),
                "sun_elevation": pos.get("sun_elevation"),
                "shadow_bearing": pos.get("shadow_bearing"),
                "shadow_len_per_1m": pos.get("shadow_len_per_1m"),
            }
            if shadow_bearing is not None:
                exp = pos.get("shadow_bearing")
                if exp is not None:
                    diff = abs((shadow_bearing - exp + 180) % 360 - 180)
                    out["observed_shadow_bearing"] = shadow_bearing
                    out["shadow_diff_deg"] = round(diff, 1)
                    out["verdict"] = (
                        "consistent — GPS/time fit the shadows"
                        if diff <= tol
                        else f"MISMATCH > {tol}° — GPS or time is wrong, or shadows were misread; do not trust the GPS blindly"
                    )
        else:
            out["error"] = "sun.py pos failed (check uv/GEO_SLEUTH_SKILL)"
    elif gps:
        out["hint"] = "GPS known but no capture time: hemisphere/band still valid; measure a shadow and re-run with --shadow-bearing only if time becomes known."
    elif dt_utc and shadow_bearing is not None:
        args = ["locate", "--time", dt_utc.strftime("%Y-%m-%dT%H:%M"), "--shadow-bearing", str(shadow_bearing), "--bbox", WORLD_BBOX]
        band = _run_sun(args)
        out["mode"] = "locate-no-gps"
        out["locate"] = band if band else "sun.py locate failed — run it manually (see docstring)"
        out["hint"] = "Bands returned = candidate latitude ranges (hemisphere + band). Cross-check with vegetation/climate."
    else:
        out["hint"] = "Need GPS, or (capture time + measured shadow bearing) — see --manual."
    return out


MANUAL = {
    "what_to_measure": [
        "shadow bearing: compass direction the shadow points (N=0, E=90, S=180, W=270)",
        "shadow ratio: object height / shadow length -> sun elevation = atan(1/ratio)",
        "which walls are lit vs shaded (works without a measurable shadow)",
    ],
    "then": [
        "sun.py locate --time <utc> --elev <deg> --shadow-bearing <deg> --bbox -60,-170,78,180",
        "or: sun.py facing --at <lat,lon> --time <utc>   (wall lighting -> camera heading)",
    ],
    "reading": [
        "shadow points SOUTH around noon in the northern hemisphere, NORTH in the southern",
        "long shadows + low sun near midday => high latitude",
        "cross-check against climate: palm/banana trees vs conifers vs tundra",
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exif", help="intake/exif.json (or exif.py output)")
    ap.add_argument("--shadow-bearing", type=float, help="shadow compass bearing measured in the photo")
    ap.add_argument("--tol", type=float, default=15.0, help="shadow bearing tolerance in degrees")
    ap.add_argument("--manual", action="store_true", help="print measurement guidance")
    args = ap.parse_args()

    if args.manual:
        print(json.dumps(MANUAL, ensure_ascii=False, indent=2))
        return
    if not args.exif:
        print(json.dumps({"error": "pass --exif <intake/exif.json> or --manual"}, ensure_ascii=False))
        return
    result = mode_exif(Path(args.exif), args.shadow_bearing, args.tol)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
