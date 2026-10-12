# Global (Overseas) Lane — Potential Optimization Paths

> Status: **design notes, not yet implemented.** The overseas lane is intentionally
> *accuracy-first* — we do **not** optimize for speed here. The CN lane owns the
> "stable 3 minutes" target; the global lane owns "get it right."

## Where we are (measured, v2)

On the 4-photo blind test (Paris / Tokyo / Marrakech / Mexico City):

| Granularity | v1 (naive) | v2 (accuracy-first) |
|-------------|-----------|---------------------|
| Country     | 3 / 4     | **4 / 4**           |
| City        | 2 / 4     | **3 / 4**           |
| Spot        | 1 / 4     | **3 / 4**           |

What actually moved the needle in v2:
1. **Source-hunting** via `WebSearch`/`WebFetch` (server-side, not GFW-blocked) — recovered Paris to *Rue de Ravignan*.
2. **Yandex web-text search** (the image endpoint is captcha-blocked, but its text search still answers).
3. **Systematic vision** (`VISION_CLUES.md`) — rejected baidu's wrong "Chefchaouen" guess for the Moroccan ksar and landed on *Aït Ben Haddou*.

Honest ceiling: for **text-less foreign street views** (no signs, no plates, no recognizable landmark), the v2 ceiling is roughly city-level. Pushing to spot-level there needs either luck (a unique landmark) or a regional hint from the user.

## Dead ends (do not re-probe blindly)

- Google Lens, TinEye, Mapillary, KartaView, `cn.bing-visual`: **all dead from CN** (timeout/captcha/empty).
- `yandex` image reverse: **captcha-blocked** from CN (only its *text* search is usable).
- AMap satellite tiles overseas: placeholder (identical MD5 for Paris/NYC) — use `sat_global.py` (ESRI/Google), not AMap, abroad.

## Optimization paths (ranked by leverage-per-effort)

### 1. Multi-script text → region routing + foreign OCR hardening  ⭐ highest leverage
- **What:** Detect the writing system in the photo (Cyrillic → RU/E.Europe; Arabic → MENA; Devanagari → India; Hangul → Korea; Katakana → Japan; Latin w/ diacritics → Europe; Thai/Lao/Khmer → SE Asia) and use it to (a) pre-filter candidate regions and (b) pick the correct OCR language for `poi.py`/`fine-OCR`.
- **Why:** It is the cheapest possible "first cut." One script read can eliminate 90% of the planet before any search runs.
- **Effort:** Low–Medium. Tie into `intake_global.sh` (currently OCR-on but language-agnostic).
- **Expected gain:** fewer false regions, faster correct routing; likely lifts *city* toward 4/4 on sign-bearing photos.

### 2. Reverse-image recovery via proxy + paid search APIs
- **What:** Behind `GEO_PROXY`, reach Google Lens / Bing visual / Yandex image directly (the dead-ends above are CN-network dead, not API dead). Optionally use a paid reverse-image API (SerpApi-style: Lens, Bing, Yandex, TinEye) that returns JSON over plain HTTPS — no proxy needed.
- **Why:** A working reverse-image hit is the single strongest spot-level signal for foreign photos.
- **Effort:** Medium (proxy config) / Low (paid API key).
- **Risk:** cost; proxy reliability; some APIs still captcha.
- **Expected gain:** the missing 4th *spot* and a faster path to the right region.

### 3. Static clue libraries (cheap knowledge, big vision boost)
- **What:** Expand the clue model the way PR #10 added "simplified vs traditional Chinese script." Add reusable, verifiable clues:
  - license-plate **formats/shapes** by country (EU white oval, US rectangle, JP ひらがな, etc.),
  - **road-marking standards** (US double-yellow centerline vs EU white),
  - **power-pole / transformer** styles,
  - **vehicle side-mirror / bumper** regional tells,
  - **electrical plug / socket** shapes caught in frame.
- **Why:** These are free once written and make `VISION_CLUES.md` systematic reading far more decisive.
- **Effort:** Low (writing + a few reference links each).
- **Expected gain:** converts "I think it's Europe" into "it's X because of plate shape."

### 4. Automated region-elimination scoring
- **What:** Turn `board.py` from manual into a scored elimination matrix: driving side (left/right from dashcam position), hemisphere/sun-angle, climate vegetation, pole style, script — each clue votes for/against a region with a weight; bottom region is dropped automatically.
- **Why:** Removes the agent's inconsistent manual elimination and makes the reasoning reproducible.
- **Effort:** Medium.
- **Expected gain:** steadier city/spot accuracy, less variance run-to-run.

### 5. Hemisphere / sun-angle + climate narrowing
- **What:** From shadow direction + a sun-position calc (date/time if EXIF, else rough), infer hemisphere and latitude band; cross-check against vegetation/pavement wetness.
- **Why:** Cheap, decisive continent-level filter that also disambiguates mirror-image latitudes.
- **Effort:** Low–Medium.
- **Expected gain:** reinforces path 1 and 4; helps text-less photos.

### 6. Satellite / OSM geometry matching upgrade
- **What:** Beyond tile mosaics (`sat_global.py`), pull **OSM vector geometry** (road networks, building footprints, coastline shape) and match junction/road shapes against the photo; compare against Google static-map higher-res tiles.
- **Why:** Geometry matching survives when there are no words in frame.
- **Effort:** High.
- **Expected gain:** the realistic route to spot-level on text-less street views — but expensive, defer.

### 7. Confidence-gated user hint (soft lever)  ⭐ cheap, big
- **What:** If confidence stays below threshold after pass 1, ask the user for a *region* hint (continent/country) instead of grinding. One correct hint can flip a miss into a hit.
- **Why:** Human regional knowledge is the highest-value input we don't currently use.
- **Effort:** Low (a prompt gate in `global_accuracy.sh`).
- **Expected gain:** pushes the weak cases (text-less streets) toward city/spot without code complexity.

### 8. Benchmark harness (measurability)
- **What:** Freeze the 4 blind photos + `BLIND_TRUTH.md` as a regression set; script `global_accuracy.sh` to score country/city/spot automatically and print a delta vs the last run.
- **Why:** Without a bench we cannot *prove* an optimization helped — we'd just be guessing.
- **Effort:** Low–Medium.
- **Expected gain:** makes every other path here verifiable.

## Suggested roadmap

1. Paths **1, 3, 7, 8** first — all Low/Medium, compound quickly, and 8 makes the rest measurable.
2. Then **2** (proxy/paid reverse-image) to attack the missing spot-level.
3. **4, 5** as the "steady-state" accuracy floor.
4. **6** only if text-less street views turn out to be a common, high-value case — it's the expensive one.

## Non-goals

- **Do not** port the CN speed hacks (drop OCR, baidu-only) to the global lane. They trade away exactly the signals overseas needs.
- **Do not** chase sub-5-minute runtime abroad. Accuracy is the product there.
