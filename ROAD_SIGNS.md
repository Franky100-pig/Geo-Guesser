# ROAD_SIGNS.md — road-sign & road-marking systems (global lane)

A **deep-pass clue library** for overseas photos, companion to
`VISION_CLUES.md` (the 10-second quick pass). Signs and markings are the
cheapest hard evidence when there is no readable text: unlike architecture or
vegetation, they are *standards*, so one shape can eliminate a whole continent.

This is the project-local counterpart of the geo-sleuth skill's
`references/clues/global.md`. Rules copied from there:

- An entry points to a **cluster**, never a single country, unless it is an
  exclusion-type clue.
- **Strength**: `strong` = single clue reaches that level (needs 3+ independent
  sources); `medium` = needs one more clue; `weak` = can only exclude or boost.
- **Never let one sign decide alone.** Combine with script, driving side or
  plates before excluding a candidate.
- Entries marked `unverified` are general geo-guessing knowledge that has **not**
  been confirmed on a solved case in this project. Treat them as search hints,
  not evidence. Promote to verified in `experience/archetypes.md` after a run.

Sources are named, not linked: `1968 Vienna Convention on Road Signs and
Signals` (UNECE), `Manual on Uniform Traffic Control Devices` (MUTCD, FHWA),
`GB 5768` (mainland China), Japan's `道路標識、区画線及び道路標示に関する命令`,
and the Wikipedia `Road signs in <country>` / `Comparison of European road
signs` series. Verify locally before citing any of these in a report.

---

## 1. Warning-sign shape — the highest-yield single split

### Red-bordered upright triangle (Vienna / European system)
- **Look for**: equilateral triangle, apex **up**, **red border**, white or
  yellow fill, black pictogram.
- **Points to**: continental Europe (Vienna Convention signatories) → much of
  the Middle East / North Africa, parts of sub-Saharan Africa and South America
  that inherited European standards.
- **Strength**: medium (large cluster; needs a second clue).
- **Counterexamples**: Ireland uses yellow diamonds (see §1a); Sweden, Finland,
  Iceland, Greece, Poland, Croatia, Serbia, Bosnia and North Macedonia use
  **amber/yellow-filled** red triangles for snow contrast — yellow fill alone
  does NOT mean MUTCD; mainland China uses a yellow triangle with a **black**
  border, and Taiwan (China) uses **white** with a red frame; road-work signs
  are amber/orange even in white-fill countries.
- **Sources**: Vienna Convention on Road Signs and Signals, Annex 8;
  Wikipedia "Comparison of European road signs", "警告标志" (warning-sign
  survey). Cross-checked 2026-11-12; `unverified` on a project case.

### Yellow diamond (MUTCD system)
- **Look for**: yellow diamond with black symbol/text, apex up; usually paired
  with white rectangular regulatory signs and octagonal STOP.
- **Points to**: United States / Canada → Australia, New Zealand, Japan
  (each with local variants). **Ireland** also uses yellow diamonds but is a
  hybrid system, not MUTCD — see §1a before treating a diamond as American.
- **Strength**: medium.
- **Counterexamples**: Japan's warning diamonds are yellow but its STOP is a
  red **inverted triangle** (止まれ) and its direction signs are blue/green —
  so a Japanese street is not "American"; several Latin American countries
  also use MUTCD-style diamonds; Australia uses red-bordered triangles for some
  regulatory warnings; **Ireland** uses yellow diamonds despite being in
  Europe (see §1a).
- **Sources**: MUTCD (FHWA); Wikipedia "Road signs in Japan",
  "Road signs in Australia". Cross-checked 2026-11-12; `unverified` on a
  project case.

> **Reading tip**: read the *border colour and apex direction* first, then the
> fill. Border red + apex up = Vienna family; solid yellow diamond = MUTCD
> family (or Ireland / Japan); yellow triangle with a black border = mainland
> China; white triangle with a red frame = Taiwan (China).

### 1a. Ireland — the exception worth memorising (splits UK vs IE)

UK and Ireland are the classic look-alike pair: **both left-hand traffic, both
English, both red-circle speed signs**. Road signs break the tie cheaply:

| | United Kingdom | Ireland |
|---|---|---|
| Warning sign | red-bordered **triangle** | **yellow diamond** (only EU country to use it) |
| Speed / distance | **mph / miles** | **km/h / km** |
| Place names | English only | **bilingual English + Gaeilge** (`Geill slí` / YIELD, `Stad` / STOP) |
| Motorway direction sign | blue | blue (same) |
| National-road direction sign | green (primary routes) | green (same) |
| Local / tourist | white / brown | white / brown (same) |
| Road-work warning | amber triangle | **orange diamond** |

- **Look for**: a yellow diamond, or a bilingual place name, or a speed-limit
  number like `100` that would be impossible in mph.
- **Points to**: Ireland (strong when yellow diamond + bilingual text agree).
- **Strength**: strong-to-country with two of those three; medium with one.
- **Counterexamples**: Gaeltacht areas may show Irish only (looks like a
  non-English sign, not a UK sign); Northern Ireland (part of the UK) uses UK
  red triangles and mph; imported/temporary signs; British road-work signs can
  also be amber.
- **Sources**: Transport Infrastructure Ireland Traffic Signs Manual; RSA
  *Rules of the Road*; Wikipedia "Road signs in Ireland". Cross-checked
  2026-11-12; `unverified` on a project case.

## 2. STOP / yield — the words are worth more than the shape

- **Look for**: red octagon, or a red-bordered inverted triangle; read the word
  on it if any.
- **Points to** (word → cluster):
  | Word | Cluster |
  |---|---|
  | `STOP` (English) | UK / IE / US / CA / AU / NZ + most of the world |
  | `ARRÊT` (sometimes with STOP) | Québec, Canada — French-language area |
  | `ALTO` / `PARE` | Spanish-speaking Americas |
  | `DUR` | Turkey |
  | `停` (octagon) | mainland China |
  | `止まれ` (red inverted triangle) | Japan |
- **Strength**: medium for the language cluster, strong for Japanese 止まれ
  (its shape + word combination is nearly unique).
- **Counterexamples**: octagonal STOP is near-universal, so the *shape alone*
  is worthless; multilingual regions put two words on one sign; tourist areas
  add English. A yield sign is an **empty** inverted triangle in the Vienna
  system but says `YIELD` in the US — that difference is a separator.
- **Sources**: Vienna Convention Annex 8 §2; MUTCD §2B; national manuals.
  `unverified` on a project case.

## 3. Direction-sign background colour

- **Look for**: the big overhead / roadside direction board, not the small
  warning sign. Note background colour + text colour.
- **Points to**:
  | Background | Cluster |
  |---|---|
  | Blue with white text | **motorways in the UK / Ireland / Germany / Netherlands**; general-road direction boards in much of continental Europe, Japan and mainland China |
  | Green with white text | US / Canada / Australia / NZ motorways; Japan and mainland China expressways; UK primary routes; Ireland national roads; **Germany: links to another Autobahn** |
  | **Yellow with black text** | **Germany, non-motorway (Bundesstraße)** — unusually distinctive |
  | White with dark text | local destinations (Germany, UK, Ireland, France) |
  | Brown with white text | tourist / scenic sites (international convention) |
- **Strength**: medium; yellow-black German Bundesstraße boards are
  strong-to-country.
- **Counterexamples**: **colour encodes road class, not country** — Germany
  alone uses blue (Autobahn), yellow (Bundesstraße), green (to an Autobahn),
  white (local) and brown (tourist), so one blue board does not exclude
  Germany; UK uses blue for motorways but green for primary A-roads; Italy,
  Switzerland and the Netherlands have their own motorway palettes; colour
  fades or white-balances in photos; a small blue plaque may be a street name
  (§6), not a direction sign.
- **Sources**: German StVO Anlage 1–3 (Zeichen 432 etc.), Wikivoyage "Driving
  in Germany"; TII Traffic Signs Manual (Ireland); national manuals.
  Cross-checked 2026-11-12; `unverified` on a project case.

## 4. Speed-limit sign + the number on it

- **Look for**: white disc with a **red ring** and black digits (Vienna system),
  vs a white **rectangle** reading `SPEED LIMIT 55` / `MAXIMUM 100` (MUTCD).
- **Points to**: red-ring disc → Europe + most of the world; white rectangle →
  US / Canada. The **number** then splits mph from km/h: 25/35/55/65/70 →
  mph countries (US, UK); 30/50/80/100/120/130 → km/h countries (nearly
  everywhere else).
- **Strength**: medium (shape + unit together is strong).
- **Counterexamples**: the UK uses mph **with** the red-ring disc — do not read
  "red ring" as "km/h"; Canada uses km/h with rectangular signs; Japan uses a
  red-ring disc with km/h; variable/advisory limits and school zones break the
  number ranges.
- **Sources**: Vienna Convention Annex 8 §3; MUTCD §2B; Wikipedia
  "Speed limit", "Road signs in the United Kingdom". `unverified`.

## 5. Centre-line and edge markings

- **Look for**: the line separating opposing traffic; count colours, not lanes.
- **Points to**: **yellow** centre line (single or double) → North America and
  mainland China; **white** → Europe and most of the world. Some East-Asian
  jurisdictions also use yellow — confirm locally rather than assuming.
- **Strength**: weak-to-medium (exclusion-type, but with a big East-Asian
  exception).
- **Counterexamples**: mainland China uses yellow dashed centre lines on
  two-way roads — this is why `VISION_CLUES.md`'s older "yellow → US/Canada"
  shorthand is **too narrow**; Japan uses white; some US markings are white
  in older footage; temporary works paint over everything. Always pair with
  script (Han characters instantly separate the East-Asian yellow-line cases).
- **Sources**: MUTCD Part 3; GB 5768.3; national marking manuals. `unverified`.

### Zebra / pedestrian crossings
- **Look for**: broad parallel white stripes (Vienna / Japan / China) vs two
  thin parallel lines bounding an unmarked crossing (much of the US); a
  **flashing amber globe on a black-and-white striped pole** (Belisha beacon)
  is a UK-specific marker (also copied in a few other countries).
- **Strength**: weak alone, medium with the road-sign family.
- **Counterexamples**: both styles coexist in many countries; repainted or
  faded crossings mislead. `unverified`.

## 6. Street-name plaques (the strongest text clue when readable)

- **Look for**: a small plate on a building corner; note colour + whether it
  carries a district/arrondissement number or a block range.
- **Points to**: blue enamel with white lettering → France (often with
  arrondissement); white/dark or blue with black text → Germany / Netherlands;
  green or blue with white text plus **block numbers** → US; blue with white
  text + 町/丁目/番地 → Japan; dark blue with white text + 路/街 → mainland
  China; UK varies by borough (often blue/green with white text).
- **Strength**: strong when the wording is readable (language + format).
- **Counterexamples**: tourist districts add translated plaques; private
  plaques mimic municipal ones; a blue direction board (§3) can be mistaken
  for a street plaque at low resolution.
- **Sources**: municipal signage conventions; Wikipedia "Street name plate".
  `unverified` on a project case.

## 7. Route shields / motorway numbering

- **Look for**: the small shield beside a route number.
- **Points to**: blue-and-red **Interstate shield** → US; white US-route shield
  → US; red rectangle with `E<number>` → trans-European E-road network; blue
  or green rectangle with `A`/`N`/`D` prefix → national motorways in Europe;
  green `E` / expressway shields → Japan expressways.
- **Strength**: medium (US shields strong-to-country).
- **Counterexamples**: state/province shields in the US and Canada mimic the
  Interstate shape; many countries reuse `A1`; E-road numbers appear alongside
  national numbers on the same gantry.
- **Sources**: MUTCD §2D; UNECE E-road network; Wikipedia "International
  E-road network". `unverified`.

## 8. Delineator posts and kerb painting

- **Look for**: roadside reflector posts and painted kerbs.
- **Points to**: black-and-white (or white with black patch) delineator posts →
  continental Europe, Japan, Russia; black-and-white or red-and-white painted
  kerbs → France / Japan / mainland China; yellow-and-black → parts of Latin
  America; mostly **unpainted** kerbs with reflector tabs on guardrails → US /
  Canada.
- **Strength**: weak (confirmation / tie-breaker only).
- **Counterexamples**: contractors vary within one country; snow regions use
  taller orange/black markers; private driveways copy municipal paint.
- **Sources**: national delineator standards; Wikipedia "Delineator (traffic)".
  `unverified`.

---

## Reading order for the global lane

1. **Warning-sign border + apex** (§1) → split the sign *family* first.
2. **STOP word / yield shape** (§2) → language cluster.
3. **Direction-board colour** (§3) → motorway vs ordinary road, then country.
4. **Speed-limit shape + number** (§4) → confirm the family and the unit.
5. **Centre line + street plaque + route shield** (§5–7) → tighten.
6. Only then use **driving side** (`driving_side.py --side left|right`) and
   **script** (`script_route.py`) as independent eliminators, and feed any
   readable name to `phone_lookup.py` / `poi.py`.

**Do not exclude on one clue.** A yellow centre line inside China, a yellow
diamond in Japan and a red-ring speed disc in the UK are all real cases where
a single "standard" read sends you to the wrong continent. The
confirms / refines / overturns chain in `FIRST_ANSWER.md` stays visible.

**Bias trap (from v3):** Baidu reverse search on a foreign street returns
Chinese near-misses with generic tags. Sign *standards* are exactly the hard
discriminators that resist that anchor — prefer them over the engine vote when
the contact sheet shows "same style, different scene". See
`VISION_CLUES.md` → "China-lookalike anchor".
