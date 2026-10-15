#!/usr/bin/env python3
"""Build a blind rapid-triage test set from Wikimedia Commons geosearch.

Why: rapid triage (the no-tool 10-second first answer) needs measuring. This
fetches geotagged public photos whose true location is known, seals that truth
in `truth.json`, and prints ONLY neutral filenames (t01.jpg ...) so the rapid
first-answer pass stays genuinely blind.

Integrity rules (important):
- Filenames are neutral and the seed order is shuffled, so the filename gives
  away nothing about the country.
- This script never prints coordinates or country names.
- Reveal only with:  python3 tools/build_rapid_testset.py --reveal <dir>

Commons API works from mainland-China egress WITHOUT a proxy (probed 2026-10-14).

Usage:
    python3 tools/build_rapid_testset.py --out tests/rapid_20261014 --n 12
    python3 tools/build_rapid_testset.py --reveal tests/rapid_20261014
"""
import argparse
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request

# Commons geosearch returns plenty of non-geolocatable subjects (macro shots,
# artwork, logos, museum interiors, scanned archives). Filter them out so the
# rapid test set is actually about *scenes*.
BLOCK = re.compile(
    r"(logo|coat of arms|\bmap\b|portrait|painting|drawing|illustration|"
    r"diagram|chart|poster|cover|\bscan\b|archive|BAnQ|mimeograph|sketch|"
    r"engraving|\bstatue\b|\bwax\b|specimen|larva|caterpillar|insect|"
    r"\bflower\b|\bbird\b|butterfly|spider|fungus|mushroom|seal of|banknote|"
    r"\bstamp\b|manuscript|herbarium|\bbook\b|manhole)", re.I)
PREFER = re.compile(
    r"(street|road|avenue|square|plaza|city|town|village|building|station|"
    r"bridge|view|panorama|pano|skyline|market|park|garden|house|church|"
    r"temple|mosque|harbour|harbor|\bport\b|beach|downtown|alley|lane)",
    re.I)

UA = "geo-sleuth-rapid-testset/1.0 (educational geolocation testing)"
API = "https://commons.wikimedia.org/w/api.php"

# Diverse seed points. Only used to pick photos; never printed to stdout.
SEEDS = [
    ("Netherlands", 52.30, 5.20),
    ("Russia", 56.33, 44.00),
    ("Greece", 39.62, 19.92),
    ("Japan", 35.01, 135.77),
    ("Peru", -12.05, -77.04),
    ("Kenya", -1.29, 36.82),
    ("India", 28.61, 77.21),
    ("Brazil", -23.55, -46.63),
    ("Vietnam", 10.82, 106.63),
    ("Morocco", 31.63, -8.01),
    ("Australia", -33.87, 151.21),
    ("Canada", 45.50, -73.57),
    ("Italy", 43.77, 11.26),
    ("United States", 40.71, -74.01),
    ("Germany", 52.52, 13.40),
    ("Thailand", 13.76, 100.50),
    ("Egypt", 30.05, 31.24),
    ("Norway", 59.91, 10.75),
    ("Argentina", -34.60, -58.38),
    ("South Korea", 37.57, 126.98),
    ("Turkey", 41.01, 28.98),
    ("Nigeria", 6.52, 3.38),
]


def _no_proxy_opener():
    """Bypass the env proxy (helps when the transparent proxy flaps SSL)."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def preflight(timeout=8):
    """Quick liveness check for the Commons API.

    Wikimedia is occasionally unreachable from CN egress (proxy hang, not a
    fast EOF). Without this, build() would retry every seed for minutes and
    produce nothing. Bail early with a clear message instead.
    """
    url = API + "?" + urllib.parse.urlencode(
        {"action": "query", "meta": "siteinfo", "format": "json"})
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                json.load(r)
            return True
        except Exception:
            time.sleep(1)
    return False


def api_get(params, timeout=12, retries=4):
    """GET with 429 + transient-network backoff.

    Commons geosearch is reached through a transparent proxy that occasionally
    drops SSL connections (UNEXPECTED_EOF). We alternate proxy / no-proxy and
    retry with jittered exponential backoff so a single flaky stretch can't
    kill a whole build.
    """
    params = dict(params)
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    delay = 2.0
    for attempt in range(retries + 1):
        opener = _no_proxy_opener() if attempt % 2 == 1 else None
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            if opener:
                with opener.open(req, timeout=timeout) as r:
                    return json.load(r)
            else:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(delay)
                delay = min(delay * 2, 20)
                continue
            if attempt < retries:
                time.sleep(delay + random.random())
                delay = min(delay * 1.8, 20)
                continue
            raise
        except Exception:
            if attempt < retries:
                time.sleep(delay + random.random())
                delay = min(delay * 1.8, 20)
                continue
            raise


def geosearch(lat, lon, radius=10000, limit=50):
    d = api_get({
        "action": "query", "list": "geosearch",
        "gscoord": f"{lat}|{lon}", "gsradius": radius,
        "gslimit": limit, "gsnamespace": 6,
    })
    return d.get("query", {}).get("geosearch", [])


def image_info(titles, width=1400):
    if not titles:
        return {}
    d = api_get({
        "action": "query", "titles": "|".join(titles),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": width,
    })
    out = {}
    for p in d.get("query", {}).get("pages", {}).values():
        ii = p.get("imageinfo")
        if ii:
            out[p["title"]] = ii[0]
    return out


def download(url, path, retries=5):
    delay = 2.0
    last = None
    for attempt in range(retries + 1):
        opener = _no_proxy_opener() if attempt % 2 == 1 else None
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with (opener.open(req, timeout=45) if opener
                  else urllib.request.urlopen(req, timeout=45)) as r:
                data = r.read()
            with open(path, "wb") as f:
                f.write(data)
            return len(data)
        except Exception as e:
            last = e
            if attempt < retries:
                time.sleep(delay + random.random())
                delay = min(delay * 1.8, 20)
                continue
            raise last


def load_avoid(dirs):
    """Titles already used in prior runs — keep rounds independent."""
    used = set()
    for d in dirs or []:
        p = os.path.join(d, "truth.json")
        if os.path.exists(p):
            with open(p) as f:
                for v in json.load(f).values():
                    if v.get("title"):
                        used.add(v["title"])
    return used


def build(out_dir, n, seed=None, avoid_dirs=None):
    os.makedirs(out_dir, exist_ok=True)
    if not preflight():
        print("! Commons API unreachable — abort. Check network/proxy, retry later.")
        return
    rng = random.Random(seed)
    avoid = load_avoid(avoid_dirs)
    seeds = SEEDS[:]
    rng.shuffle(seeds)          # filename order must not mirror the seed list

    truth = {}
    saved = []
    for name, lat, lon in seeds:
        if len(saved) >= n:
            break
        time.sleep(2.0)          # be polite to the Commons API
        try:
            hits = geosearch(lat, lon)
        except Exception as e:
            print(f"! geosearch failed for seed {len(saved)}: {e}")
            continue
        if not hits:
            continue
        titles = [h["title"] for h in hits[:20]]
        try:
            info = image_info(titles)
        except Exception as e:
            print(f"! imageinfo failed for seed {len(saved)}: {e}")
            continue
        cand = []
        for h in hits:
            title = h.get("title", "")
            if BLOCK.search(title) or title in avoid:
                continue
            ii = info.get(h["title"])
            if not ii:
                continue
            if not str(ii.get("mime", "")).startswith("image/jpeg"):
                continue
            if (ii.get("width") or 0) < 700:
                continue
            url = ii.get("thumburl") or ii.get("url")
            if not url:
                continue
            score = 1 if PREFER.search(title) else 0
            cand.append((score, h, url))
        if not cand:
            continue
        cand.sort(key=lambda c: -c[0])
        hit, url = cand[0][1], cand[0][2]
        idx = len(saved) + 1
        fname = f"t{idx:02d}.jpg"
        path = os.path.join(out_dir, fname)
        try:
            size = download(url, path)
        except Exception as e:
            print(f"! download failed for {fname}: {e}")
            continue
        truth[fname] = {
            "seed_country": name,
            "lat": hit.get("lat"),
            "lon": hit.get("lon"),
            "title": hit.get("title"),
            "dist_m": hit.get("dist"),
            "bytes": size,
        }
        saved.append(fname)

    with open(os.path.join(out_dir, "truth.json"), "w") as f:
        json.dump(truth, f, ensure_ascii=False, indent=2)

    # Print ONLY neutral filenames — no country, no coordinates.
    print(f"saved {len(saved)} photos to {out_dir}/", flush=True)
    for f in saved:
        print("  " + f, flush=True)
    print(f"truth sealed in {out_dir}/truth.json "
          f"(reveal with --reveal {out_dir})", flush=True)


def reveal(out_dir):
    with open(os.path.join(out_dir, "truth.json")) as f:
        truth = json.load(f)
    for k in sorted(truth):
        t = truth[k]
        print(f"{k}  {t['seed_country']:<12} "
              f"({t['lat']}, {t['lon']})  {t['title']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="output directory")
    ap.add_argument("--n", type=int, default=12, help="how many photos")
    ap.add_argument("--seed", type=int, default=None, help="rng seed (shuffle)")
    ap.add_argument("--reveal", help="reveal truth.json in this directory")
    ap.add_argument("--avoid", nargs="*", default=[],
                    help="prior test dirs whose titles to exclude (keep rounds independent)")
    args = ap.parse_args()
    if args.reveal:
        reveal(args.reveal)
    else:
        build(args.out, args.n, args.seed, args.avoid)
