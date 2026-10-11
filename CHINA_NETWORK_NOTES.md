# China network notes (geo-sleuth behind the GFW)

Measured on a Mac in mainland China (no working system proxy to Google). These
are the constraints that shaped the helpers in this repo.

## What is blocked / unavailable

| Source | Status from CN | Note |
|---|---|---|
| Google satellite tiles (`mt1.google.com/vt/lyrs=s`) | **timeout** | `tiles.py` default; unreachable |
| ESRI World Imagery | **timeout** | also unreachable |
| `GEO_PROXY=http://127.0.0.1:57941` | **connection refused** | the WorkBuddy proxy port was not up at test time; if it IS up, Google/ESRI may work and you can skip AMap |
| Baidu reverse image search | **works (200)** | the killer feature for CN photos |
| Baidu pano (street view) | **no coverage inside scenic areas** | works in cities (e.g. Shenzhen) but returns null in Zhangjiajie park |
| Apple Vision OCR | works | but on a screenshot only reads the app UI text, not scene signs |

## What works as a fallback

- **AMap (Gaode) satellite tiles** — reachable directly. `amap_sat.py` stitches them.
  AMap uses GCJ-02, so the script converts WGS84 -> GCJ-02 first.
- **Baidu reverse image search only** — gives the location for most CN photos via
  near-duplicate travel-blog images. Use `fast_intake.sh` (Baidu-only, no OCR).

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
