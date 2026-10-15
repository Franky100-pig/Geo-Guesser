# Rapid blind-test results

Run with `tools/build_rapid_testset.py` + `tools/score_rapid.py`. Rapid is
scored as a **country-cluster** guess (exact country or region-that-contains the
truth = hit). This is the measurement loop that feeds `experience/` and the
skill's `rapid-triage.md`.

## Round 1 — `tests/rapid_20261014` (n=11) — genuine blind, tool-confirmed
- answered 9 · declined 2 · correct 8
- **8/9 = 89% of answered**, **8/11 = 73% of all photos**
- miss: t06 = Peru (Lima, Plaza San Martín street sign) read as Mexico/Chile.
  Lone Spanish-sign + red-soil + cordillera cue → confabulated a plausible
  neighbour. See `experience/cases.md` + `archetypes.md` (Andean negative-clue).
- the 2 declines were low-signal / non-scene frames — correctly abstained.
- **takeaway:** high-confidence multi-cue reads are solid; single-cue reads are
  over-confident. Directly drove `RAPID_ACCURACY.md` lever #2 (multi-cue voting).

## Round 2 — `tests/rapid2_20261014` (n=10) — truth known, NOT re-scored blind
Truth (for reference only — do not treat as a blind measurement):
Nigeria, Japan, Kenya, Turkey, Russia, India, Canada, Egypt, Morocco, Germany.
Not used as a blind round because answers weren't captured at reveal time.

## Round 3 — `tests/rapid3_20261014` — BLOCKED (Commons outage)
Could not build: Wikimedia Commons egress from CN was unreachable on 2026-10-15
(proxy + direct both timed out; other egress like Open-Meteo/example.com fine).
The build script now fails fast on this (see `preflight()`). Re-run when Commons
is back:

```bash
python3 tools/build_rapid_testset.py --out tests/rapid3_20261014 --n 10 \
    --seed 99173 --avoid tests/rapid_20261014 --avoid tests/rapid2_20261014
# then: look at the photos -> write answers.json -> reveal + score
python3 tools/build_rapid_testset.py --reveal tests/rapid3_20261014
python3 tools/score_rapid.py tests/rapid3_20261014
```
