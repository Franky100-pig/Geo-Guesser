# Bias traps (failure modes + defense)

Documented ways a first answer (or the engine) goes wrong, and how the rapid
anchor defends against them. Add a new entry whenever a run is misled.

---

### Baidu China-lookalike noise on foreign photos
- **Failure:** Baidu returns a *visual description* / generic Chinese label for
  ordinary foreign photos — e.g. a Manila street tagged as Chinese tenements, or
  a Dezhou (China) photo tagged "威海文登".
- **Defense:** the written rapid first answer is the anchor. Only a reverse-search
  **near-duplicate** (same object/scene) or **readable text** may overturn it —
  never a generic tag alone.
- **Cases:** v3 q3 Manila; Dezhou — text on the image (ICBC, 德州市人民医院,
  幸福德州) proved 山东德州 over baidu's wrong label.

### Game / app screenshot frames
- **Failure:** GeoGuessr / 图寻(tuxun) frames carry watermarks (Google, minimap,
  HUD) that get reverse-searched as scenery.
- **Defense:** identify the app first; crop out the UI; reverse-search only the
  panorama.

### Mirroring
- **Failure:** reversed text or a wrong-side driver's seat → both script and
  driving-side reads come out wrong.
- **Defense:** check for mirroring before reading anything; flip back first.

### Same-archetype confusion
- **Failure:** dike ≠ sea dike; post-Soviet ≠ China; olive coast ≠ generic
  "Europe".
- **Defense:** name the *sub-type*, not just the continent.
