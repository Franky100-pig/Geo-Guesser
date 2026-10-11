#!/usr/bin/env python3
"""Stitch AMap (Gaode) satellite tiles into a mosaic.

Why this exists: `geo-sleuth` defaults to Google / ESRI satellite tiles, which are
unreachable from mainland China without a working proxy. AMap (autonavi) tiles are
reachable directly and are a usable fallback for eyeballing road layout / parking
arrangement when you cannot get Google imagery.

WGS84 center -> GCJ-02 tiles (AMap uses GCJ-02, the China-mandated offset).

Usage:
    uv run amap_sat.py <lat> <lon> [zoom=17] [radius=2] [out=amap_sat.jpg]

    radius is the number of tiles out from the center tile in each direction
    (radius=2 -> a 5x5 mosaic). zoom 17-18 shows individual roads/buildings.

Dependencies: pillow  (run with `uv run --with pillow amap_sat.py ...`)
"""
import math
import sys
import io
import urllib.request
from PIL import Image

AMAP_HOSTS = ["webst01", "webst02", "webst03", "webst04"]


def wgs84_to_gcj02(lat: float, lon: float):
    a = 6378245.0
    ee = 0.00669342162296594323

    def out_of_china(lat, lon):
        return not (73.66 < lon < 135.05 and 3.86 < lat < 53.55)

    if out_of_china(lat, lon):
        return lat, lon
    dlat = _tf_lat(lon - 105.0, lat - 35.0)
    dlon = _tf_lon(lon - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlon = (dlon * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
    return lat + dlat, lon + dlon


def _tf_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def _tf_lon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def lonlat_to_tile(lon, lat, z):
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y


def fetch_tile(x, y, z):
    host = AMAP_HOSTS[(x + y) % 4]
    url = f"https://{host}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def main():
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    z = int(sys.argv[3]) if len(sys.argv) > 3 else 17
    r = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    out = sys.argv[5] if len(sys.argv) > 5 else "amap_sat.jpg"
    glat, glon = wgs84_to_gcj02(lat, lon)
    fx, fy = lonlat_to_tile(glon, glat, z)
    cx, cy = int(fx), int(fy)
    ox, oy = cx - r, cy - r
    mosaic = Image.new("RGB", (256 * (2 * r + 1), 256 * (2 * r + 1)))
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            try:
                t = fetch_tile(ox + dx, oy + dy, z)
                mosaic.paste(t, (256 * dx, 256 * dy))
            except Exception as e:  # noqa: BLE001
                print("tile fail", ox + dx, oy + dy, e)
    mosaic.save(out, quality=88)
    px = (fx - ox) * 256
    py = (fy - oy) * 256
    print(f"saved {out} center_px=({px:.0f},{py:.0f}) size={mosaic.size} z={z} "
          f"gcj=({glat:.6f},{glon:.6f}) wgs=({lat},{lon})")


if __name__ == "__main__":
    main()
