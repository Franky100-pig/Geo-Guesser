# Accessible data APIs + search-path strategy

Probed **2026-10-14 from mainland-China egress**. The old SOP said "Yandex dead,
ESRI needs proxy, no automated path for foreign street photos" — that is now
outdated. Several useful APIs are reachable, some **without any proxy**.

Re-run the probe any time with a small `curl --max-time 6` matrix (direct and
`-x http://127.0.0.1:7890`) before trusting this table.

## Reachability

| API / service | Direct | Via proxy `127.0.0.1:7890` | Notes |
|---|---|---|---|
| **Wikimedia Commons API** | ✅ 200, ~1.0s | ✅ | geosearch, file search, imageinfo — free, no key, fast |
| **Open-Meteo** (forecast + geocoding) | ✅ ~1.0–1.2s | ❌ | climate / phenology cross-check, no key. **Do NOT proxy it** |
| **ESRI World Imagery tiles** | ✅ ~0.8s | ✅ | satellite tiles **without** a proxy (previously needed `GEO_PROXY`) |
| ipinfo.io | ✅ ~1.3s | ✅ | IP → location for web-sourced photos |
| sunrise-sunset.org | ✅ ~2.6s | ✅ | sun times → sanity-check `sun.py` |
| Baidu images | ✅ ~0.25s | ✅ | CN reverse search (still the only working image engine) |
| Yandex (web) | ✅ ~6s (slow) | ✅ ~4.6s | web search reachable; the *reverse* endpoint captcha'd in v3 |
| Nominatim (geocode/reverse) | ❌ | ✅ ~2.5s | needs proxy; send a real `User-Agent`, ≤1 req/s |
| Overpass (OSM features) | ❌ | ✅ ~3.7s | needs proxy; filter queries, cap bbox |
| Openverse | ❌ | ✅ ~4.4s | CC image search; `page_size` capped at 20 for anonymous |
| Wikipedia API (geosearch) | ❌ | ✅ ~1.3s | needs proxy |
| OSM raster tiles | ❌ | ✅ ~4.7s | needs proxy |
| OSM API 0.6 | ❌ | ✅ ~6s (slow) | needs proxy, avoid if Overpass works |
| Google (www) | ❌ | ✅ ~1.3s | host reachable via proxy; **Lens still needs upload + auth** |
| Flickr API | ❌ | ✅ ~1.6s | host reachable; needs an API key for real queries |
| Mapillary graph | ❌ | 500 | needs a token |
| KartaView | 405 | 405 | reachable but the endpoint rejects this method |
| Photon (komoot) | ❌ | ❌ | dead |

## How this reshapes the search path

The old path was: photo → baidu reverse (only lever) → text search → give up on
ordinary foreign photos. The new path adds a **cheap data-API tier between the
rapid answer and the expensive scans**.

| Tier | Cost | What it does |
|---|---|---|
| **T0 — rapid triage** | 0 | no-tool scene-archetype read → country cluster (`references/rapid-triage.md` + `experience/archetypes.md`) |
| **T1 — direct APIs (seconds, no proxy)** | ~1–3s | Commons geosearch/search, Open-Meteo climate+geocode, sunrise-sunset, ipinfo |
| **T2 — proxy APIs (seconds)** | ~3–5s | Nominatim geocode, Overpass feature enumeration, Openverse/Flickr text-image search, Wikipedia geosearch |
| **T3 — imagery** | ~1–5s | ESRI World Imagery (**direct**), OSM tiles (proxy) |
| **T4 — heavy** | minutes | baidu intake, `sat_scan.py` CLIP grid, `match.py` street-view, pose/terrain |

Rule: **exhaust T1–T3 before paying for T4.** Most "no automated path" cases
were failures of imagination, not of access.

## Concrete recipes (new)

### 1. Commons as a poor-man's reverse image search
Google Lens is still unavailable, but Commons is a **geotagged corpus with
ground truth**:
- Search by scene words in the local language:
  `action=query&list=search&srsearch=<words>&srnamespace=6` → titles + then
  `prop=imageinfo` for the thumbnail.
- **Geosearch** around a candidate point:
  `list=geosearch&gscoord=lat|lon&gsradius=10000&gsnamespace=6` → files *with
  coordinates* near there. If a candidate location is right, Commons often
  already has a photo of the same object with a title that names it.
- Gotcha: bursts get **429**. Sleep ~2s between calls and back off
  exponentially (already implemented in `tools/build_rapid_testset.py`).

### 2. Overpass archetype queries (turn the rapid read into candidates)
The rapid read names an *archetype*; Overpass can enumerate that archetype
inside the candidate country — no image matching needed:
- "dike / causeway across water" → `way[embankment=yes]`, `man_made=causeway`,
  or roads whose bbox intersects `natural=water` on both sides.
- "bridge with concrete abutment" → `way[bridge=yes]` + `man_made` filters.
- "olive grove on limestone coast" → `landuse=orchard` / `natural=scrub` within
  a coastal bbox.
Then confirm each candidate with ESRI imagery (T3) instead of blind scanning.

### 3. Open-Meteo phenology / climate plausibility
A rapid read that depends on vegetation ("olive", "taiga", "tropical") can be
checked against climate normals for a candidate point:
`geocoding-api.open-meteo.com/v1/search?name=…` → coords, then
`api.open-meteo.com/v1/forecast?latitude=…&longitude=…` for temperature. Cheap
falsifier for "this can't be X, X is too cold/hot/dry".

### 4. Nominatim + ESRI for the confirm loop
Nominatim (proxy) turns a name into a bbox; ESRI (direct) gives the imagery to
confirm. This pair replaces most of the "needs `GEO_PROXY`" satellite work.

## Still blocked (don't burn time)

- **Google Lens** — no upload path from CN.
- **Mapillary / KartaView street-level imagery** — need token / wrong endpoint.
- **Yandex *reverse* image** — captcha (the web endpoint is fine, use it for text).
- **Photon** — unreachable both ways; use Nominatim.

## Blind-test harness

`tools/build_rapid_testset.py` fetches geotagged Commons photos, seals the
ground truth in `truth.json`, and prints only neutral filenames so the rapid
pass stays blind:

```bash
python3 tools/build_rapid_testset.py --out tests/rapid_20261014 --n 12
# … look at the photos, write first answers …
python3 tools/build_rapid_testset.py --reveal tests/rapid_20261014
```

This is what makes rapid accuracy measurable instead of anecdotal.
