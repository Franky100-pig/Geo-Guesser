# Judgment experience (判断经验库)

Real, accumulated identification lessons from this project's actual runs —
the tuxun daily challenges, blind tests, and the Dezhou / Manila cases.

The geo-sleuth skill's `references/rapid-triage.md` is the **generic method**
(the no-tool 10-second first-answer technique). **This folder is the
project-specific, growing record of what actually worked**, so the next run
starts from experience instead of from zero.

## How to add an entry

- One entry per scene archetype, bias trap, or solved case.
- Keep it **transferable**: write the method, not the answer to a specific
  puzzle. Don't leak an eval puzzle's conclusion.
- Follow the format in each file's header.
- Add a one-line pointer here in the index.

## Files

| File | What it holds |
|---|---|
| `archetypes.md` | Scene → country-cluster heuristics (the rapid-read menu, extended over time) |
| `bias-traps.md` | Failure modes and how the first answer defends against them |
| `cases.md` | Concrete runs with the `first → refined → final` chain and the reusable lesson |

## Workflow tie-in

The two-stage flow is: **rapid rough answer → tool-refined search**. The rapid
read comes from `references/rapid-triage.md` (skill) + the archetype menu here;
the refine stage is `intake.py` / `observe.md` / `clues.py` / `script_route.py`
/ `driving_side.py` / `pin_title_mine.py`. Every solved case's reusable lesson
gets folded back into `archetypes.md` or `bias-traps.md`.
