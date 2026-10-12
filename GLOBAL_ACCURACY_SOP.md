# Global Accuracy SOP — overseas photos, accuracy first (no clock)

Companion to `global_accuracy.sh` (deterministic prep) and `gg_fast.sh`
(CN lane, speed first). This file is the **agent playbook**: what to do with
the prep output, in what order, and where the accuracy actually comes from.

Measured 2026-10-12 from a mainland-China network. Do not trust memory —
re-run the probes in `CHINA_NETWORK_NOTES.md` if the environment changes.

## Engine map (measured, CN egress)

| Capability | Status from CN | Notes |
|---|---|---|
| Baidu reverse image search | **WORKS** | strong on Chinese + landmark/postcard scenes; weak on ordinary foreign streets |
| Yandex reverse image search | DEAD | captcha on every variant, all 4 test photos |
| Google Lens | DEAD | connection timeout (also by public URL via WebFetch) |
| TinEye / Mapillary / KartaView | DEAD | connection timeout |
| cn.bing.com visual search upload | DEAD | 404 (only keyword search works) |
| **Yandex WEB search via WebFetch** | **WORKS** | best text engine for foreign content |
| **WebSearch (built-in)** | **WORKS** | server-side, unblocked |
| **WebFetch (built-in)** | **WORKS** | server-side: source hunting, gallery captions |
| ESRI/Google satellite tiles | needs `GEO_PROXY` | `sat_global.py` handles the rest |
| AMap satellite tiles | CN-only imagery | `amap_sat.py` |

**Consequence:** overseas accuracy does NOT come from adding more image
engines — it comes from **text search + source hunting + agent vision**.

## The workflow (do all steps; they are cheap and independent)

### Step 0 — Cut the search space first (routing, `global_accuracy.sh` step 5)
Before deep reading, apply the three cheap eliminators (output already in
`routing.json` / `sun_hint.json`):
- **`script_route.py --ocr ocr_fine.json`** — writing system on any sign →
  candidate regions + the right OCR languages for a re-run (Cyrillic →
  RU/E.Europe, Arabic → MENA, kana → Japan, Devanagari → India…). One script
  read can eliminate 90% of the planet.
- **`sun_hint.py --exif intake/exif.json`** — hemisphere + latitude band from
  GPS/time; with a measured shadow bearing it also sanity-checks whether the
  EXIF is trustworthy. No GPS? `sun_hint.py --manual` tells you what to measure.
- **`driving_side.py --side left|right`** — once you can see which side traffic
  keeps to, this eliminates half the planet (LHT set: UK/IE/JP/IN/TH/ID/AU/NZ/KE/ZA…).
Never let a single one of these decide alone — combine two before committing.

### Step 1 — Read everything the prep produced
`photo.jpg`, `intake/edges/*` (four edges + corners), `ocr_fine.json`,
and **every** `rev_vars/*_baidu.json` vote + contact sheet. While reading,
walk `VISION_CLUES.md` deliberately — script, driving side, plates, poles,
road markings, architecture, vegetation, sun angle.

### Step 2 — Text first (highest precision per second)
Any text at all — street plaque, shop sign, poster, phone number:
- phone numbers → `phone_lookup.py` (offline, global, instant)
- names/addresses → WebSearch, then Yandex text via WebFetch
  (`https://yandex.com/search/?text=...`), then `revimg.py --query` (Bing)
- Cross-check every text hit against a second source before believing it.

### Step 3 — Source hunt (the biggest single lever for web photos)
Any hint that the photo came from the internet — watermark, app UI, filename,
EXIF, or "I downloaded it from somewhere" — turns the problem into a
**caption lookup**:
- WebSearch the distinctive phrase / site / filename
- WebFetch the gallery or article page; captions almost always name the
  street or place
- Worked example: `paris.jpg` from davidphenry.com → gallery caption
  "Rue de Ravignan: Montmartre Street" → country-level FAIL becomes
  **street-level hit** in one fetch.

#### 3a. Pin-title mining (v3-verified, cheap and high yield)
Baidu reverse search often finds near-duplicates on Chinese pinboard sites
(huaban.com, duitang.com, meipian.cn). These pins carry the ORIGINAL photo
title, which usually names the place — even when the engine tag itself is a
useless generic label (鱼市场/城市街道).
- For EVERY near-duplicate cell in `rev/*_baidu_similar.jpg`, take `similar[i].from`
  from the JSON and WebFetch it; read the pin/album title.
- Worked example (v3 q1): engine tag only「图中可能是鱼市场」→ near-dup duitang
  pin titled「缅甸莱茵湖鱼市场」→ Myanmar · Inle Lake in one fetch.

#### 3b. Watermark → photographer profile (v3-verified)
A faint watermark (corner, 2021-style, `name © year`) is a person lookup, not
a place lookup — use it indirectly:
- OCR/zoom the corner strip (`imgprep.py zoom` on the bottom band)
- WebSearch the name + platform guesses (Flickr / Wikimedia Commons). A hit on
  the person's gallery/geo area tells you where they shoot (v3 q4: "Steven R.
  Barringer" → Commons contributor of Taiwan → country confirmed without text).
- Commons is scriptable from CN via proxy:
  `commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6...`
  (XHS/Flickr pages often need login/JS — skip those, do not fight them).

#### 3c. Variant hits can name cities in their titles (v3-verified)
A variant (flip/gray/wb) reverse hit may land on an article whose TITLE names
the city even when no near-duplicate exists (v3 q2: flip-variant hit on a
xiaohongshu post titled「西班牙小岛 Palma de Mallorca」→ city confirmed).
Read the `from` list of every variant JSON, not only the guessed tag.

### Step 4 — Verify the hypothesis (never skip)
- `poi.py "<name>"` for coordinates (OSM Nominatim / so.com)
- `sat_global.py lat lon` with `GEO_PROXY` for satellite confirmation;
  `amap_sat.py` if the candidate is inside China
- Record every step on the board (`board.py clue/add/rank`)

### Step 5 — Report
`board.py report` + `evidence_sheet.py` composite. State the confidence
per level (country / city / spot) and what evidence supports each.

## Which path for which photo

| Photo type | Primary path | Backup |
|---|---|---|
| Landmark / postcard scene | baidu reverse image (usually enough) | source hunt |
| Street scene WITH readable text | text first (phone/name lookup) | source hunt |
| Street scene, text unreadable | agent vision + VISION_CLUES → descriptive WebSearch / Yandex text | variant baidu rev |
| Photo with any source hint | **source hunt** (captions name places) | everything above |
| Screenshot from a game/app | watermark identifies the source app first | then normal lane |

## Honest ceiling

Without Google Lens (blocked from CN), an **ordinary foreign street photo
with no readable text and no source hint** has no reliable automated path:
baidu will return a visual description, not a place. The realistic play is
agent vision + region knowledge to form a hypothesis, then text-search to
confirm. Say so in the report instead of guessing a city.
