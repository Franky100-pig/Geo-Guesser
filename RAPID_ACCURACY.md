# Raising rapid-triage accuracy

Rapid triage is the no-tool 10-second first answer (see `references/rapid-triage.md`
and `FIRST_ANSWER.md`). This doc is about **making that first answer more often
right** — measured, not vibes. It is the companion to `API_STRATEGY.md` (which is
about the *tool* tier after the first answer).

Two premises:

1. Rapid is a **country-cluster** guess, not a coordinate. Scoring it as
   exact-country is too harsh; scoring region-contained is fair. `tools/score_rapid.py`
   does exactly this.
2. Accuracy improves only through a **feedback loop**: blind test → log the miss →
   grow `experience/archetypes.md` and `experience/bias-traps.md` → promote frequent
   patterns into the skill's `rapid-triage.md`. The blind-test harness
   (`tools/build_rapid_testset.py`) is what makes the loop real.

## What the blind tests already showed (round 1, n=11)

- **Country accuracy: 8/11 (73%) of answered**, 2 correctly declined as no-signal.
- **Strong:** high-confidence single-archetype reads (NL dike, RU post-Soviet
  bridge, GR olive-coast) were all correct.
- **Weak:** a low-signal photo (Peru rural red-earth road) was confabulated as
  "Mexico / Chile" — i.e. I named a *plausible neighbour* when no strong cue was
  present. This is the single biggest accuracy leak.
- **Bias:** Baidu reverse on foreign photos returns Chinese look-alike noise
  (v3 Manila case). The rapid answer must declare "CN or not" **before** any
  reverse search, so the noise can't anchor us.

## Ten levers, ranked by expected payoff

### 1. Calibrate confidence against the scorer, not gut feel
Track hit-rate **per confidence bucket** (high / medium / low / decline). The
Peru case tells us single-cue reads are currently *over*-confident. Rule of thumb
to adopt: a country earns **high** only if ≥2 independent cues agree; a lone cue
(one plant, one roof type) caps at **medium**. Re-run the scorer after each round
and watch the high-bucket rate climb toward ~90%.

### 2. Multi-cue voting, never single-cue anchoring
Protocol already mandates "3 reasons". Enforce it as a gate:
- 1 cue  → max confidence **low**
- 2 cues → **medium**
- 3+ cues, cross-confirming → **high**
This alone would have demoted Peru from a confident guess to a low/decline and
saved the miss.

### 3. Grow the archetype library from real misses
Every wrong or declined case becomes a new entry or a **negative clue**:
- Add "Andean altiplano red-earth rural road" as its own archetype, with
  discriminators vs Mexico sierras (greener, pine) and Chile (arid, sparse).
- Add "this red soil + cordillera is NOT automatically Mexico" as a bias trap.
The `experience/` folder is the scratchpad; promote anything that recurs ≥2× into
`rapid-triage.md`.

### 4. Explicit "NOT-X" discriminators (country vs country)
Rapid errors are almost always **confusing look-alikes**, not random. So the
highest-value content is the *contrast*, not the description:
- Greece vs Croatia: municipal bin colour (green Δήμος vs grey/metal) + guardrail
  post style.
- Russia vs Kazakhstan: aridity + soil colour (KZ drier, yellower).
- NL vs Denmark: reed beds + electricity-pylon type (lattice steel vs wooden).
Write these as paired tables in `archetypes.md`.

### 5. Cheap pre-filters folded into T0
Two free, fast checks belong *before* the scene read, so the hemisphere/side is
right by construction:
- **Driving side** (LHT/RHT) from the first road frame — already scripted
  (`driving_side.py`); a 2-second read.
- **Sun / hemisphere hint** (`sun_hint.py` + Open-Meteo/sunrise-sunset) to sanity
  check "is this really the southern hemisphere?"
These prune half the candidate space instantly.

### 6. Latent China-lookalike guard (step 0.1)
Because Baidu noise on foreign photos is real, the first line of every answer is
**"CN or not?"**. Only after declaring non-CN do we trust any later Baidu hit.
Already in `bias-traps.md`; make it the literal first field of the answer schema.

### 7. Bridge rapid → T1 with a 1-second Commons confirm
Even at T0, a single Commons geosearch around the rapid's candidate (see
`API_STRATEGY.md` recipe 1) can confirm/deny before we commit. This is the
cheapest accuracy boost that doesn't require an image matcher: if Commons has a
geotagged photo *of the same object* near the candidate, the read is validated.

### 8. Confidence-vs-accuracy tracking is the key metric
The scorer's per-bucket output IS the dashboard. Targets to watch over rounds:
- high bucket: ≥ 90% hit
- medium bucket: ≥ 60%
- low bucket: ≥ 30% (better than chance, still useful as a hint)
- declines: should be **rare and correct** (don't decline just to inflate rate)

### 9. Prompt discipline — always structured output
Every answer must be: `cluster | conf | 3 cues | top alternatives | what would
overturn`. Writing the "overturn" condition forces you to name the single fact
that would kill the guess — which is exactly what catches confabulation.

### 10. Ensemble, don't solo
When two archetypes both weakly fire, output **both** as alternatives with
weights, never collapse to one. The scorer counts a hit if either the primary or
a listed alternative contains the truth region — so honest hedging is rewarded,
confabulation is punished.

## The loop, concretely

```bash
# 1) build a blind set (truth sealed, filenames neutral)
python3 tools/build_rapid_testset.py --out tests/rapid3_XXXX --n 10 --seed <s> \
    --avoid tests/rapid_20261014 --avoid tests/rapid2_20261014

# 2) LOOK at the photos, write answers.json (cluster/conf/cues/alt/overturn)
#    — do NOT reveal yet

# 3) reveal + score
python3 tools/build_rapid_testset.py --reveal tests/rapid3_XXXX
python3 tools/score_rapid.py tests/rapid3_XXXX

# 4) for every miss/decline-wrong: add to experience/cases.md (honest rapid-only),
#    then promote recurring patterns into experience/archetypes.md + skill
```

Run a round whenever you've accumulated ~5 new identifications. The library grows
from reps, not from theory — which is exactly why `experience/` exists.
