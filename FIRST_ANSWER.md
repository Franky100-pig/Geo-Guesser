# First-Answer Protocol — both lanes (CN fast + global accuracy)

**Rule:** the moment a photo is in hand, look at it for ~10 seconds and
**declare a first answer before anything else runs** — before prep finishes,
before any search, before reading any engine output.

## Why

- **Anchoring defense.** Baidu/Yandex labels and contact sheets pull hard.
  Writing down an independent first guess means the engine result has to
  *earn* its way past your own read, not the other way round.
  (v3 q1: first read said "Vietnam" from the nón lá hat; the engine said
  "fish market"; the pin title said Inle Lake, Myanmar. Only the written
  first guess made the correction visible and trackable.)
- **Cheap discriminators only.** A first answer may use script, driving side,
  vegetation, plates, architecture — anything visible in 10 seconds. No
  searches, no crops.
- **Measurable.** Track first-answer accuracy separately from final accuracy;
  the gap tells you where the evidence pipeline actually adds value.

## Format (say it exactly like this)

```
First answer: <country> / <city-or-region>  (confidence: low|medium|high)
Why: <one line, the single strongest visible clue>
```

Example:
```
First answer: Vietnam / Mekong Delta  (confidence: low)
Why: conical nón lá hat + freshwater fish stall → SE Asia
```

## Rapid heuristic menu (the actual techniques)

A first answer is an *impression → cluster*, not a country. Glance in this order
(exclusion power high → low) and pick the matching scene archetype:

| Glance at… | If you see… | Rough cluster (first → runners-up) |
|---|---|---|
| Road across water on both sides | straight dike, reedy shallows, big sky, lattice pylon | **Netherlands** → Denmark / Germany / Poland / Lithuania |
| Under a bridge / city edge | curved-arm lamps, blue/white signs, graffiti abutment, cracked asphalt | **Russia** → Kazakhstan / Belarus / Ukraine / Serbia |
| Coastal hillside road | olive groves, limestone, white W-guardrail, green bin, sea + distant land | **Greece** → Croatia / Turkey / Italy |
| Roofs over an area | red terracotta vs gray pitched | Italian- vs German-speaking Europe |
| Tropical lane | laterite/red dirt, conical hat, banana | Vietnam / Thailand / Myanmar / Indonesia |
| Dry, adobe, Arabic script | flat roofs, desert | MENA / N.Africa |
| Uniform poles + vending machines | many pole transformers, blue/white road studs | Japan |
| French grid | arched crossarms | France + DOM-TOM |

Each row narrows to a **cluster**; the refine pipeline (Step 1+) confirms which
member. Full scan order, worked reads, and bias traps (Baidu China-lookalike
noise, game-screenshot watermarks, mirroring) are in the geo-sleuth skill:
`~/.workbuddy/skills/geo-sleuth/references/rapid-triage.md`. **Read it before
launching intake.**

## The refinement loop

Every later piece of evidence gets classified before it changes the answer:

| Verdict | Action |
|---|---|
| **confirms** | note it, keep the answer, raise confidence |
| **refines** | narrow inside the same answer (city → district → spot); the first answer stays visible in the log |
| **overturns** | replace the answer, and **record what overturned it** — that line is the reusable lesson |

Never silently swap an answer. The visible chain
`first → refined → final` is the product; a bare final answer is not.

## Where it lives

- In conversation: the first answer is the **first message** sent back to the
  user; refinements follow as separate messages (`refined:` …).
- In a run directory: write it to `FIRST_ANSWER.md` (or
  `board.py clue add` with `level=guess`) at T+0, then edit it as evidence
  lands.
- **Accumulated project experience:** `experience/` — real solved cases and
  scene-archetype lessons, growing as we identify more. Seed a case's reusable
  lesson there after a run.

## Wiring

- `gg_fast.sh` (CN lane): `T+5s  first answer from the glance` — the NEXT
  block starts with it.
- `global_accuracy.sh` (overseas): SOP step order is now
  **first answer → routing eliminators → deep read**.
- `GLOBAL_ACCURACY_SOP.md` Step 0 (now "Rapid triage"); `VISION_CLUES.md`
  first-pass table is the menu for what a 10-second glance may use.
- The concrete rapid techniques (archetype cheat-sheet + bias traps) now live in
  the geo-sleuth skill: `references/rapid-triage.md` — this file is the
  protocol wrapper around it.
