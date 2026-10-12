# Geo-Guesser

A small toolbox of **China-network workarounds** for [geo-sleuth](https://github.com/Oldcircle/geo-sleuth)
(an MIT-licensed agent skill for photo geolocation). It is *not* a fork of
geo-sleuth — it complements it when you run the skill from mainland China, where
the default Google/ESRI satellite sources and some engines are unreachable.

## Why

`geo-sleuth` assumes global network access. From a CN machine:

- Google & ESRI satellite tiles time out (no proxy) → `tiles.py` / `sat_scan.py` stall.
- Baidu reverse image search still works and is usually enough to name the place.
- Baidu street view has no coverage inside scenic areas.

These helpers restore a usable workflow without touching the upstream skill.

## Quick Start — geolocate a photo in ~3 minutes

**Answering protocol (both lanes):** every photo gets a **first answer within
~10 seconds of seeing it** — country/city + confidence + one-line why — before
any prep output is read; later evidence then confirms / refines / overturns it
with the chain kept visible. Protocol: `FIRST_ANSWER.md`.

One-command version (sets up run dir, background intake, board and signboard
crops in a single call, then prints the timed next steps):

```bash
bash gg_fast.sh photo.jpg run1
```

Assumes geo-sleuth is installed at `~/.workbuddy/skills/geo-sleuth`
(see Prerequisites) and you have a photo, e.g. `photo.jpg`:

```bash
# 1) start fast intake in the background (~60s; Baidu-only, no OCR)
bash fast_intake.sh photo.jpg intake/ &

# 2) while that runs, prep the candidate board + edge crops in parallel
export CLAUDE_SKILL_DIR="$HOME/.workbuddy/skills/geo-sleuth"
S="$CLAUDE_SKILL_DIR/scripts"; RUN=<your-run-dir>; cd "$RUN"
uv run "$S/board.py" init --photo photo.jpg
uv run "$S/board.py" country cn          # skip if unknown
uv run "$S/imgprep.py" edges photo.jpg --out-dir edges/
wait                                      # 3) intake/intake.md is ready

# 4) read the Baidu vote + the contact sheet (intake/rev/photo_baidu_similar.jpg)
#    -> for most CN photos this alone names the place at country/city/area level
```

Optional follow-ups (outside the 3-minute budget):

```bash
# verify road layout against a satellite mosaic
uv run --with pillow amap_sat.py <lat> <lon> 18 2 sat.jpg
# compose a shareable one-page evidence sheet
uv run --with pillow evidence_sheet.py my_case.json evidence.jpg
```

## Scope: China lane vs worldwide lane

| Tool | Scope | Notes |
|---|---|---|
| `gg_fast.sh` / `fast_intake.sh` | **CN lane** | baidu-only intake, no OCR; baidu is strongest for CN scenes |
| `amap_sat.py` | **CN-only imagery** | overseas AMap tiles return a "no satellite imagery" placeholder (tested) |
| `phone_lookup.py` | 🌍 **worldwide, offline** | libphonenumber geodata bundled; zero network, GFW-proof |
| `sat_global.py` | 🌍 worldwide | ESRI/Google tiles; from CN set `GEO_PROXY` to your VPN |
| `intake_global.sh` | 🌍 worldwide | all engines + OCR on; needs global reachability or `GEO_PROXY` |
| `global_accuracy.sh` | 🌍 worldwide | accuracy-first prep lane + SOP (CN/OV split), `REGION` speed profiles |
| `script_route.py` / `driving_side.py` / `sun_hint.py` | 🌍 worldwide | step-0 region eliminators (script / traffic side / hemisphere) |
| `pin_title_mine.py` | 🌍 worldwide | mines baidu rev-search source pages for place names (~30s) |
| `gg_prep_batch.sh` | 🌍 worldwide | staggered parallel preps for a batch of photos |
| `evidence_sheet.py` | 🌍 worldwide | pure local image compositing |

**Rule of thumb:** CN photo → CN lane (`gg_fast.sh` + `amap_sat.py`).
Anything else → worldwide lane (`intake_global.sh` + `sat_global.py`), with
`GEO_PROXY` exported if you run from mainland China. `phone_lookup.py` and
`evidence_sheet.py` help on both lanes.

### Worldwide lane — measured reality (2026-10-12, from CN)

Blind-tested on 4 photos (Paris street / Tokyo skyline / Morocco ksar /
Mexico City Zocalo), two lanes, same blind truth:

| | v1 (image engines only) | v2 (accuracy-first: `global_accuracy.sh` + SOP) |
|---|---|---|
| Country | 3/4 | **4/4** |
| City | 2/4 | **3/4** |
| Spot (street/square/site) | 1/4 | **3/4** |

What moved the numbers:
- **Paris** (was country-level FAIL): baidu is a dead end on ordinary foreign
  streets (4/4 variants returned the same visual-only tag). **Source hunting**
  fixed it — the photo's origin gallery captions it "Rue de Ravignan:
  Montmartre Street" → street-level hit, coordinates verified.
- **Morocco** (city was wrong): baidu said 舍夫沙万; agent vision (earthen ksar,
  not the blue city) + a ctrip source naming 阿伊特本哈杜 → correct site,
  coordinates verified.
- Tokyo / Mexico City were already right and stayed right with stronger evidence.

Measured dead ends (do not retry blindly): Google Lens, TinEye, Mapillary,
KartaView, cn.bing visual upload, Yandex image search, variant baidu rescue,
`poi.py` on foreign POIs. What works: **Yandex WEB search via WebFetch,
server-side WebSearch/WebFetch, source hunting, systematic agent vision.**
Full numbers: `CHINA_NETWORK_NOTES.md` ("Engine availability probed",
"Global lane retest").

### Overseas lane — speed (measured 2026-10-12, v3)

`global_accuracy.sh` now takes region **speed profiles** — baidu variant
reverse search pays off for SE/East Asia (Chinese travel blogs cover it) but
returned noise for every NA/EU photo so far, so the variants are cut there:

| Profile | baidu reverse on | prep time/photo | when |
|---|---|---|---|
| `full` (auto default) | photo + flip + gray + wb | ~105s | unknown photo, non-Latin script |
| `sea` | photo + flip | ~80s | SEA/East/South Asia |
| `eu` / `na` | photo only | **~61–64s** | Europe / Americas |

```bash
# one photo, forced profile
REGION=eu bash global_accuracy.sh photo.jpg run_eu

# batch: staggered parallel preps (2 photos: 72s wall total)
REGION=sea bash gg_prep_batch.sh --stagger 8 *.jpg
```

After prep, the fastest accuracy lever is usually `pin_title_mine.py .`
(mines the baidu source-page titles for place names, ~30s). Auto-routing is
deliberately conservative: text-only routing cannot split Europe from the
Americas, so set `REGION` yourself after a 5-second look at the photo.

## What's inside

| File | What it does |
|---|---|
| `gg_fast.sh` | One-command CN fast lane: run dir + background baidu intake + board + crops, prints a timed SOP. |
| `fast_intake.sh` | Run `intake.py` **Baidu-only, no OCR, in the background** (~60s instead of ~190s). |
| `amap_sat.py` | Stitch **AMap (Gaode)** satellite tiles into a mosaic. AMap is reachable from CN and replaces the blocked Google/ESRI source. Handles WGS84→GCJ-02. |
| `phone_lookup.py` | **Offline worldwide phone-number geolocation** (libphonenumber). Numbers on signs/graffiti pin country + city with zero network. |
| `sat_global.py` | Global satellite mosaic (ESRI/Google) for outside China, with `GEO_PROXY` support and `--dry-run` tile-math verification. |
| `global_accuracy.sh` | Accuracy-first worldwide lane: full intake (OCR on) + fine OCR pass + baidu reverse search on every variant. |
| `intake_global.sh` | Thin full-engine intake wrapper for non-CN photos (kept for ad-hoc use). |
| `GLOBAL_ACCURACY_SOP.md` | Agent playbook for overseas photos: engine map, text-first / source-hunt / verify order, photo-type decision table. |
| `FIRST_ANSWER.md` | Answering protocol: declare a first answer in ~10s, then refine with a visible confirms/refines/overturns chain. |
| `VISION_CLUES.md` | Systematic reading checklist (script, driving side, plates, architecture, street furniture…) for the agent's own eyes. |
| `evidence_sheet.py` | Compose an evidence image (grid of crops + captions + conclusion) from a JSON spec — reusable across cases. |
| `CHINA_NETWORK_NOTES.md` | Measured network constraints and the 3-minute workflow. |
| `examples/zhangjiajie_evidence.json` | Example `evidence_sheet.py` spec from a real Zhangjiajie run. |

## Prerequisites

- `uv` (https://docs.astral.sh/uv/)
- geo-sleuth installed: `https://github.com/Oldcircle/geo-sleuth`
  (default location assumed: `~/.workbuddy/skills/geo-sleuth`; override with
  `GEO_SLEUTH_SKILL=/path/to/geo-sleuth`).

## Usage

### Fast intake (Baidu-only, ~60s, non-blocking)

```bash
# run in background so you can prep the board in parallel
bash fast_intake.sh photo.jpg intake/ &

# meanwhile, in another shell:
export CLAUDE_SKILL_DIR="$HOME/.workbuddy/skills/geo-sleuth"
uv run "$CLAUDE_SKILL_DIR/scripts/board.py" init --photo photo.jpg
uv run "$CLAUDE_SKILL_DIR/scripts/board.py" country cn
uv run "$CLAUDE_SKILL_DIR/scripts/imgprep.py" edges photo.jpg --out-dir edges/
wait   # once intake/intake.md exists, read the Baidu vote + contact sheet
```

### AMap satellite fallback

```bash
uv run --with pillow amap_sat.py 29.3454 110.4648 18 2 amap_srsm18.jpg
# args: <lat> <lon> [zoom=17] [radius=2] [out]
# zoom 17-18 shows individual roads/buildings; radius=2 -> 5x5 mosaic
```

### Evidence sheet

```bash
uv run --with pillow evidence_sheet.py examples/zhangjiajie_evidence.json evidence.jpg
# spec JSON: title, optional base dir, rows[{images,height,caption}], footer[]
```

### Worldwide mode (accuracy first — no clock)

```bash
# 1) prep: full intake (OCR on) + fine OCR pass (3x3 tiles, 3x upscale)
#    + baidu reverse search on EVERY variant (crop/flip/gray/wb)
#    ~3-6 min; run in background
bash global_accuracy.sh paris.jpg run_paris

# 2) then follow GLOBAL_ACCURACY_SOP.md, in this order:
#    - READ everything; walk VISION_CLUES.md while looking at the photo
#    - TEXT first: phone_lookup.py for numbers (offline, instant);
#      WebSearch / Yandex-text-via-WebFetch for names (both work from CN)
#    - SOURCE hunt: any URL / filename / watermark / EXIF hint ->
#      WebFetch the source page; captions name places. This single step
#      turned the Paris blind test from country-level FAIL into a
#      street-level hit.
#    - VERIFY: poi.py + sat_global.py (needs GEO_PROXY) / amap_sat.py (CN)

# 3) offline phone-number geolocation (both lanes)
uv run --with phonenumbers phone_lookup.py 13758466320 +33142685300

# 4) global satellite mosaic (ESRI default; add proxy from CN)
GEO_PROXY=http://127.0.0.1:<port> uv run --with pillow sat_global.py 48.8584 2.2945 17 1 paris.jpg
```

Why this shape: measured from CN, no additional image engine is reachable
(google lens / yandex-reverse / tineye / mapillary all dead). Overseas
accuracy therefore comes from **text search + source hunting + systematic
agent vision**, not from more reverse-image engines.

## License

MIT — same as geo-sleuth. This repo only adds China-specific helpers and does
not modify the upstream skill.
