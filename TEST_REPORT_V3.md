# v3 blind test — overseas accuracy (2026-10-12)

4 fresh web photos (Openverse/Flickr, EXIF stripped, truth sealed in a file
during the run). New tools in the loop: `script_route.py`, `sun_hint.py`,
`driving_side.py` (SOP step 0.5) + the SOP source-hunt additions.

## Score

| Photo | Truth | Country | City | Spot |
|---|---|---|---|---|
| q1 street market | Myanmar, Inle Lake fish market ("Weary Street Market Seller", Flickr) | ✅ | ✅ Inle Lake (via pin title) | ❌ |
| q2 narrow alley | Palma de Mallorca, Spain | ✅ | ✅ Palma | ❌ |
| q3 city street | Tondo, Manila, Philippines | ✅ | ✅ Manila | ✅ said "Tondo-like" (district-level) |
| q4 fishing harbor | 梧棲漁港 Wuqi Fishing Harbor, Taichung, Taiwan (China) | ✅ | ❌ | ❌ |
| **Total** | | **4/4** | **3/4** | **1/4** |

## What actually produced each hit

| Photo | Decisive lever |
|---|---|
| q1 | **Pin-title mining**: baidu near-dup on duitang titled「缅甸莱茵湖鱼市场」(engine tag was just 鱼市场) |
| q2 | Visual hypothesis (Mallorca arches/salmon walls) + flip-variant hit on xiaohongshu「西班牙小岛 Palma de Mallorca」+ TOMMIE HANSEN watermark path |
| q3 | Vision only: pedicab sidecars + tenement style → PH/Manila; district read off density/awning cues. Baidu was pure noise (CN tenement lookalikes) |
| q4 | Script route (Traditional) + 「3包100元」 pricing + watermark → Steven R. Barringer = Commons photographer of Taiwan. City/spot not reached |

## New levers found this round (now in GLOBAL_ACCURACY_SOP.md step 3)

1. **Pin-title mining** — near-dup pins on huaban/duitang/meipian carry the
   original title with the place name. Highest-value single fetch of the test.
2. **Watermark → photographer profile** — name + "Flickr/Commons" search
   pins the photographer's shooting region (country-level rescue for q4).
3. **Variant-hit title reading** — flip/gray variants can hit articles whose
   titles name the city even with no near-duplicate.
4. **Bias guard** — baidu CN-lookalike floods (90 same-style Chinese estates)
   are noise, not evidence; don't let them override regional eliminators.

## Honest ceiling

Text-less market/alley/tenement photos still cap out around city level:
q1/q2 needed luck (a titled pin existed); q4's city (Taichung) and spot
(Wuqi harbor) were unrecoverable without the source page. Spot-level on
web photos remains "source hunt or bust" — matches the v2 conclusion.

## Infra notes

- Openverse API anonymous `page_size` ≤ 20; good blind-test photo source
  (Flickr-backed, titles as truth, usually no EXIF).
- Local system proxy for this Mac is `127.0.0.1:7890` (Clash), not 57941 —
  flickr/commons/openverse/yandex all work through it with curl/WebFetch
  (server-side WebFetch works for yandex but rate-limits into captcha).
