# Solved / logged cases — `first → refined → final`

**Honesty note:** entries tagged **(rapid-only)** are first answers from the
10-second glance and have **not** been tool-verified yet. They are logged so the
chain can be filled in later, not claimed as answers. When a case is run through
the refine pipeline, fill the `Refined` / `Final` lines and move the reusable
lesson into `archetypes.md` or `bias-traps.md`.

---

### 2026-10-13 tuxun global #2 — post-Soviet street under a bridge
- **First (rapid):** Russia / Volga-basin city (medium). Why: curved-arm lamps
  + blue/white signs + graffiti abutment + cracked asphalt.
- **Refined:** — (pending tool run)
- **Final:** — (pending)
- **Lesson:** the post-Soviet lamp archetype is a fast, high-signal
  discriminator; do NOT conflate it with China (different lamp form, no Han
  script).

### 2026-10-13 tuxun global #3 — dike road across water
- **First (rapid):** Netherlands / Markermeer dike (medium). Why: straight dike,
  reedy shallows on both sides, very big sky, lattice pylon.
- **Refined:** — (pending tool run)
- **Final:** — (pending)
- **Lesson:** water-on-both-sides causeway → Dutch dike country; split from
  DK/DE by reeds + signage language.

### 2026-10-13 tuxun global #4 — olive–limestone coast road
- **First (rapid):** Greece / Ionian coast (medium). Why: olive groves +
  limestone + white guardrail + green municipal bin + sea + distant landmass.
- **Refined:** — (pending tool run)
- **Final:** — (pending)
- **Lesson:** olive + limestone + green-bin cluster → Greece first; Croatia /
  Turkey / Italy as runners-up.

---

### 2026-10-14 blind round 1 — t06 Peru street sign (TOOL-CONFIRMED)
- **Source:** `tests/rapid_20261014/t06.jpg`, truth = Peru, Lima (Plaza San Martín).
- **First (rapid):** Mexico / Chile (low). Why: Spanish sign + red-earth +
  cordillera silhouette → guessed a "plausible Spanish-speaking neighbour".
- **Refined:** — (n/a; this was a blind-test miss, not a live case)
- **Final:** Peru (ground truth).
- **Lesson (high value):** this is the single biggest accuracy leak — when no
  strong cue is present, I name a *plausible neighbour* instead of declining.
  Spanish + red soil + mountains is NOT uniquely Peru. Discriminators that were
  missed: the specific sign typography, coastal-desert vs high-altiplano context,
  and absence of the markers that would pin Mexico (pine sierras) or Chile (arid
  sparseness). **Fix:** a lone cue caps at `low`; if I can't name ≥2 cross-
  confirming cues, the answer should be a *region* or a `decline`, never a
  confident single-country guess. See `RAPID_ACCURACY.md` lever #2.
