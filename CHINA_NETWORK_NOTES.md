# China network notes (geo-sleuth behind the GFW)

Measured on a Mac in mainland China (no working system proxy to Google). These
are the constraints that shaped the helpers in this repo.

## What is blocked / unavailable

| Source | Status from CN | Note |
|---|---|---|
| Google satellite tiles (`mt1.google.com/vt/lyrs=s`) | **timeout** | `tiles.py` default; unreachable |
| ESRI World Imagery | **timeout** | also unreachable |
| `GEO_PROXY=http://127.0.0.1:7890` | **works (2026-10-12)** | system Clash port; flickr / commons / openverse / yandex all reachable through it. The old 57941 WorkBuddy port is often down |
| Baidu reverse image search | **works (200)** | the killer feature for CN photos |
| Baidu pano (street view) | **no coverage inside scenic areas** | works in cities (e.g. Shenzhen) but returns null in Zhangjiajie park |
| Apple Vision OCR | works | but on a screenshot only reads the app UI text, not scene signs |

## What works as a fallback

- **AMap (Gaode) satellite tiles** — reachable directly. `amap_sat.py` stitches them.
  AMap uses GCJ-02, so the script converts WGS84 -> GCJ-02 first.
- **Baidu reverse image search only** — gives the location for most CN photos via
  near-duplicate travel-blog images. Use `fast_intake.sh` (Baidu-only, no OCR).

## Global lane measured (2026-10-12, 4 photos: Paris/Tokyo/Morocco/Mexico)

Measured with `intake_global.sh` on the same machine. Results:

| Component | Measured status | Detail |
|---|---|---|
| `intake.py` default engines | **baidu + yandex only** | NOT google/bing — the wrapper comment was wrong; `--engines baidu,yandex` is the actual default set |
| Yandex reverse search | **ALL captcha-blocked** | every variant of every test photo returned "upload input not found (possibly asked for verification)" |
| Google satellite tiles | **timeout** | same as CN lane |
| ESRI World Imagery (`sat_global.py` default) | **timeout without GEO_PROXY** | global sat step is unusable from CN unless a proxy works |
| Baidu reverse search (overseas photos) | **works, but scene-dependent** | see below |

Baidu's overseas capability profile (the only working engine):
- **Works**: overseas landmark / postcard scenes (Tokyo skyline -> "富士山与东京夜景" + source pages naming 日本东京; Mexico City Zocalo -> "墨西哥城历史中心广场" x3 + Wanderlog source "墨西哥城主教座堂, 墨西哥"; Morocco ksar -> "舍夫沙万"/"摩洛哥古城" + ctrip source naming 阿伊特本哈杜)
- **Fails**: ordinary foreign street views (Paris Montmartre -> tags degraded to visual descriptions "石砌老街巷", no country/city at all) — Chinese web has no near-duplicates of such scenes

Verdict: global lane is **half-usable** — 3/4 country, 2/4 city on this set, but the
engine it relies on (baidu) has no coverage of ordinary foreign streets, and the
designed second engine (yandex) is captcha-walled. The CN lane is the reliable
one from this network.

### Engine availability probed (2026-10-12, round 2 — the accuracy hunt)

"Add more reverse-image engines" was the first idea for fixing overseas
accuracy. Measured, it is dead:

| Engine | Result from this machine |
|---|---|
| Google Lens (upload, and by public URL via WebFetch) | timeout / fetch failed |
| TinEye | timeout |
| Mapillary (graph.mapillary.com) | timeout |
| KartaView (api.openstreetcam.org) | timeout |
| cn.bing.com visual-search upload | 404 (keyword search only) |
| Yandex image search by URL (`rpt=imageview`) | "service is under construction" |
| **Yandex WEB search via WebFetch** | **WORKS** — full results, no captcha; best text engine for foreign content |
| **WebSearch / WebFetch (built-in, server-side)** | **WORKS** — source hunting, gallery captions |
| `revimg.py --query --text-engines bing` | works, but cn.bing web search is weak on foreign proper nouns (returns dictionary entries for "rue") |
| Stock-site fallback (vcg.com, from baidu's similar list) | security check, no location data |

Rescue tactics measured on the Paris photo:
- **Variant reverse search does NOT rescue**: baidu on flip/gray/up/wb variants
  all returned the same visual-only tag ("石墙小巷" / "石墙街道"), no place name.
- **Source hunt DOES**: the photo's origin gallery page captions it
  "Rue de Ravignan: Montmartre Street" — a country-level FAIL becomes a
  street-level hit in one WebFetch.

Conclusion: overseas accuracy comes from **text search + source hunting +
systematic agent vision**, not from more image engines. Speed is irrelevant on
this lane — see `GLOBAL_ACCURACY_SOP.md`.

### Global lane retest (2026-10-12, accuracy-first v2, same 4 photos)

Same blind truth, new lane (`global_accuracy.sh` + SOP). Result:
**country 3/4 → 4/4, city 2/4 → 3/4, spot 1/4 → 3/4.**

| Photo | v1 | v2 | What made the difference |
|---|---|---|---|
| Paris street | country FAIL | **street-level** (rue de Ravignan, Montmartre) | source hunt: origin gallery caption named the street |
| Tokyo skyline | country+city | same, stronger | 4/4 consistent baidu votes + vision |
| Morocco ksar | country ✓, city ✗ | **site-level** (Aït Ben Haddou) | vision rejected baidu's 舍夫沙万; ctrip source named the ksar |
| Mexico Zócalo | country+city+spot | same, stronger | 5/5 votes + source page naming the cathedral |

Additional measured findings from the retest:
- fine OCR (3x3 tiles, 3x upscale): 0 useful items on all 4 photos — the source
  images are too low-resolution; don't count on OCR for small web images
- variant baidu reverse search: identical visual-only tags, no rescue
- `poi.py` on foreign POIs returns **empty** (CN-oriented sources) → verify
  overseas coordinates via WebSearch/WebFetch instead

## Practical 3-minute path (country / city / area)

1. `bash fast_intake.sh photo.jpg intake/ &`  (Baidu-only, ~60s, non-blocking)
2. Meanwhile: `board.py init`, `board.py country cn`, `imgprep.py edges`
3. Read `intake/intake.md` vote count + open `rev/*_baidu_similar.jpg`
4. Conclude. Exact-road refinement needs Google z18 imagery or street view,
   which are not available from CN without a proxy -> out of scope for 3 min.

## Gotchas

- `gh auth switch` did not persist across separate shell invocations here; if a
  push to the wrong GitHub account happens, re-run `gh auth switch --user <you>`
  in the SAME shell as the push.
- AMap tiles are GCJ-02 offset; do not compare them 1:1 against WGS84 coords
  without the conversion (handled in `amap_sat.py`).
