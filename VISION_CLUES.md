# VISION_CLUES.md — what to look at, in what order

Fast checklist for the agent's own eyes while reading a photo (the global
lane has no Google Lens, so systematic reading IS the engine). Deep, sourced
versions of many of these live in the geo-sleuth skill's
`references/clues/global.md` and region packs — this file is the quick pass.

## First pass — whole frame, ~10 seconds

| Clue | What it tells you |
|---|---|
| Script / writing system on any sign | language family: latin, cyrillic, arabic, devanagari, han, kana, hangul, thai… |
| Driving side (steering wheel / driver position) | ~75 countries drive on the left; splits e.g. UK/JP/IN/AU vs mainland |
| License plate format + color | EU blue strip, US/CA plain white, JP white+green, CN blue… |
| Road center line color | yellow → US/Canada (most of the world is white) |
| Sun / shadow direction | hemisphere + rough latitude + time of day |
| Vegetation | palms → tropical/arid; conifers → temperate/cold; dense broadleaf → humid subtropical |
| Skyline / terrain | mountains, coast, plain, density of high-rises |

## Signage & text — the money clues

- **Street plaques** differ per country: France blue-white enamel, Germany
  white-black, UK blue with street name, US green/white. A readable plaque is
  the single strongest text clue.
- **Business signs**: language + phone number format → feed numbers to
  `phone_lookup.py` (offline, global).
- Currency symbols, units (km/h vs mph), date formats, price magnitudes.
- Religious buildings: church spire vs minaret vs pagoda roof vs Hindu
  temple gopuram vs monastery.

## Architecture

- **Roofs**: zinc grey (Paris), terracotta tile (Mediterranean / LatAm),
  thatch, flat concrete, dark tile (JP/KR).
- **Walls**: stone rubble, adobe / rammed earth (MENA ksar), timber framing
  (DE/FR half-timber), painted concrete, brick.
- **Windows**: shutters, iron Haussmann balconies (Paris) vs Spanish
  balconies, security bars (LatAm), exterior AC units (SEA/US south).
- Scale: 2–3 story village vs mid-rise district vs tower skyline.

## Street furniture

- **Lamps**: ornate black French, US cobra-head on wood pole, UK cast iron.
- **Hydrants**: above-ground painted barrel → US/Canada/JP/KR; pillar or
  underground → Europe/AU/LatAm.
- **Bus stops**: shelter style, route-number format, double-decker buses.
- **Crossings**: zebra stripes vs signal-only (much of the US has no
  markings at ordinary intersections).
- **Utility poles**: concrete vs wood vs lattice; density of overhead wires
  (dense → SEA / South Asia / older towns).
- **Guardrails**: w-beam vs cable vs concrete barrier, and their color.

## Region quick notes

- **France**: blue enamel plaques, zinc roofs, cobbled lanes + stone walls
  in Montmartre, Haussmann iron balconies downtown.
- **US / Canada**: yellow center lines, STOP signs, barrel hydrants,
  green highway signage, exit numbers.
- **Latin America**: terracotta roofs, Spanish, window bars, vivid walls,
  yellow-and-white road signs.
- **MENA / North Africa**: earthen ksar, minarets, Arabic script, satellite
  dishes, donkeys in villages.
- **Southeast / South Asia**: scooter density, dense overhead wiring,
  Thai / Devanagari / Tamil scripts, monsoon vegetation.

## Turning a clue into a query

1. Combine **2–3 distinctive clues** (never one) + "street photo" / "街景".
2. The moment you have a **proper noun**, switch to it: search the name,
   not the description.
3. Verify every hypothesis with `poi.py` + satellite (`sat_global.py` with
   `GEO_PROXY`, or `amap_sat.py` in China) before reporting.
