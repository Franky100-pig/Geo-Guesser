#!/usr/bin/env python3
"""Global satellite mosaic — the worldwide complement to amap_sat.py.

amap_sat.py only has imagery inside China (overseas tiles return AMap's
"no satellite imagery" placeholder). This tool covers the rest of the world:

  esri    ArcGIS World Imagery (default) — global, high resolution, WGS84
  google  Google satellite tiles — global, needs reachability or a proxy

Routing from mainland China: set GEO_PROXY (e.g. http://127.0.0.1:PORT) to
fetch through your VPN/proxy; without it, direct connections to both
providers usually time out from CN. Coordinates are plain WGS84 — no GCJ-02
conversion needed for either provider (that offset is China-only and AMap's).

Usage:
  uv run --with pillow sat_global.py <lat> <lon> [zoom=17] [radius=2] [out=sat_global.jpg] [--provider esri|google] [--dry-run]

  --dry-run prints the tile URLs it *would* fetch (useful to test routing /
  tile math offline) and exits.

Examples:
  # Eiffel Tower via ESRI through your proxy
  GEO_PROXY=http://127.0.0.1:57941 uv run --with pillow sat_global.py 48.8584 2.2945 17 1 paris.jpg

  # offline sanity check of tile math
  uv run --with pillow sat_global.py 48.8584 2.2945 17 1 --dry-run
"""
import math
import os
import sys
import io
import urllib.request
from urllib.parse import urlparse

ZOOM_RANGE = (0, 23)

PROVIDERS = {
    # {z}/{y}/{x} order for ESRI; google uses query params
    "esri": ("https://services.arcgisonline.com/ArcGIS/rest/services/"
             "World_Imagery/MapServer/tile/{z}/{y}/{x}"),
    "google": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
}


def lonlat_to_tile(lon: float, lat: float, z: int):
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y


def tile_url(provider: str, x: int, y: int, z: int) -> str:
    tpl = PROVIDERS[provider]
    return tpl.format(x=x, y=y, z=z)


def fetcher_with_proxy():
    proxy = os.environ.get("GEO_PROXY", "").strip()
    if proxy:
        handler = urllib.request.ProxyHandler({
            "http": proxy,
            "https": proxy,
        })
        return urllib.request.build_opener(handler).open
    return urllib.request.urlopen


def fetch_tile(opener, url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener(req, timeout=20) as r:
        return r.read()


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    lat, lon = float(args[0]), float(args[1])
    z = int(args[2]) if len(args) > 2 else 17
    r = int(args[3]) if len(args) > 3 else 2
    out = args[4] if len(args) > 4 else "sat_global.jpg"
    provider = "esri"
    if "--provider" in sys.argv:
        provider = sys.argv[sys.argv.index("--provider") + 1]
    if provider not in PROVIDERS:
        sys.exit(f"unknown provider {provider!r}; choose from {list(PROVIDERS)}")
    if not (ZOOM_RANGE[0] <= z <= ZOOM_RANGE[1]):
        sys.exit(f"zoom {z} outside {ZOOM_RANGE}")

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        sys.exit("lat/lon out of range")
    if lat > 85.05 or lat < -85.05:
        sys.exit("web-mercator covers latitudes only up to ±85.0511°")

    fx, fy = lonlat_to_tile(lon, lat, z)
    cx, cy = int(fx), int(fy)
    n = 2 ** z
    ox, oy = cx - r, cy - r

    urls = []
    for dy in range(2 * r + 1):
        ty = oy + dy
        if not (0 <= ty < n):
            urls.append(None)  # pole-adjacent: no tile
            continue
        for dx in range(2 * r + 1):
            tx = (ox + dx) % n  # wrap around the antimeridian
            urls.append(tile_url(provider, tx, ty, z))

    print(f"provider={provider} zoom={z} center_tile=({cx},{cy}) "
          f"mosaic={2 * r + 1}x{2 * r + 1} out={out}")

    if dry:
        for u in urls:
            print(u or "(no tile: pole-adjacent row)")
        return

    from PIL import Image
    opener = fetcher_with_proxy()
    mosaic = Image.new("RGB", (256 * (2 * r + 1), 256 * (2 * r + 1)), (24, 24, 24))
    fails = 0
    for i, u in enumerate(urls):
        if u is None:
            fails += 1
            continue
        dx, dy = i % (2 * r + 1), i // (2 * r + 1)
        try:
            raw = fetch_tile(opener, u)
            mosaic.paste(Image.open(io.BytesIO(raw)).convert("RGB"), (256 * dx, 256 * dy))
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"tile fail ({dx},{dy}): {e}", file=sys.stderr)
    mosaic.save(out, quality=88)
    px, py = (fx - ox) * 256, (fy - oy) * 256
    got = (2 * r + 1) ** 2 - fails
    print(f"saved {out} center_px=({px:.0f},{py:.0f}) tiles_ok={got}/{(2*r+1)**2}")
    if got == 0:
        sys.exit("all tiles failed — if you are behind the GFW, set GEO_PROXY "
                 "to your VPN's http proxy and retry")


if __name__ == "__main__":
    main()
