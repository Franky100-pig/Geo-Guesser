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

## What's inside

| File | What it does |
|---|---|
| `amap_sat.py` | Stitch **AMap (Gaode)** satellite tiles into a mosaic. AMap is reachable from CN and replaces the blocked Google/ESRI source. Handles WGS84→GCJ-02. |
| `evidence_sheet.py` | Compose an evidence image (grid of crops + captions + conclusion) from a JSON spec — reusable across cases. |
| `fast_intake.sh` | Run `intake.py` **Baidu-only, no OCR, in the background** (~60s instead of ~190s). |
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

## License

MIT — same as geo-sleuth. This repo only adds China-specific helpers and does
not modify the upstream skill.
