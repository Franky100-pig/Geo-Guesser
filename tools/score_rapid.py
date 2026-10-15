#!/usr/bin/env python3
"""Score a rapid-triage blind pass against sealed ground truth.

Reads:
  - <dir>/truth.json          (sealed by build_rapid_testset.py --reveal)
  - <dir>/answers.json        (your structured rapid first answers)

answers.json shape (one entry per photo filename):
  {
    "t01": {
      "cluster": "Netherlands",   # country or country-cluster you named
      "conf": "high",             # high | medium | low | decline
      "cues": ["cue1", "cue2"],   # the 3 (or fewer) reasons
      "alt": ["Denmark", "Germany"],
      "overturn": "if pylons are wooden rather than lattice -> not NL"
    },
    ...
  }

Scoring model (rapid is a *cluster* guess, not a coordinate):
  - conf == "decline"  -> neutral (not scored as right or wrong)
  - otherwise: normalize the named cluster vs the truth country.
      exact  : answer == truth                       -> HIT
      region  : answer is a broader region containing truth -> PARTIAL (counts as hit)
      miss    : otherwise                              -> MISS
A small REGION_MAP lets "Balkans", "post-Soviet", "Scandinavia", etc. count
when the truth country sits inside them.

Outputs aggregate accuracy, accuracy-by-confidence-bucket, and a
confusion-style list of misses (what I said vs what it was) — the raw material
for growing experience/archetypes.md and pruning over-confident single cues.
"""
import argparse
import json
import os

# Broad region labels -> member countries, so a correct *cluster* read scores
# even when I name the region instead of the exact country.
REGION_MAP = {
    "post-soviet": {"russia", "ukraine", "belarus", "kazakhstan", "uzbekistan",
                    "georgia", "armenia", "azerbaijan", "moldova", "kyrgyzstan",
                    "turkmenistan", "tajikistan", "latvia", "lithuania", "estonia"},
    "balkans": {"greece", "albania", "croatia", "serbia", "bosnia", "montenegro",
                "north macedonia", "slovenia", "bulgaria", "romania", "kosovo"},
    "scandinavia": {"sweden", "norway", "denmark", "finland", "iceland"},
    "iberia": {"spain", "portugal", "andorra"},
    "british isles": {"united kingdom", "ireland"},
    "central europe": {"germany", "poland", "czechia", "austria", "hungary",
                       "slovakia", "slovenia", "switzerland"},
    "maghreb": {"morocco", "algeria", "tunisia", "libya"},
    "southeast asia": {"vietnam", "thailand", "malaysia", "indonesia", "philippines",
                       "cambodia", "laos", "myanmar", "singapore", "brunei"},
    "east asia": {"japan", "south korea", "china", "taiwan", "north korea", "mongolia"},
    "andes": {"peru", "bolivia", "ecuador", "colombia", "chile", "venezuela",
              "argentina"},
    "subsaharan africa": {"nigeria", "kenya", "ghana", "tanzania", "ethiopia",
                          "south africa", "uganda", "senegal", "cameroon", "zimbabwe"},
    "middle east": {"turkey", "egypt", "iran", "iraq", "saudi arabia", "jordan",
                    "lebanon", "syria", "israel", "palestine", "uae", "qatar",
                    "oman", "yemen", "kuwait"},
    "caribbean": {"cuba", "jamaica", "haiti", "dominican republic", "puerto rico",
                  "trinidad and tobago", "bahamas"},
    "oceania": {"australia", "new zealand", "fiji", "papua new guinea"},
}

CONF_ORDER = ["high", "medium", "low", "decline"]


def norm(s):
    return (s or "").strip().lower()


def classify(answer, truth_country):
    a = norm(answer)
    t = norm(truth_country)
    if a == t:
        return "exact"
    for region, members in REGION_MAP.items():
        if a == region and t in members:
            return "region"
    return "miss"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", help="test directory containing truth.json + answers.json")
    args = ap.parse_args()
    d = args.dir
    with open(os.path.join(d, "truth.json")) as f:
        truth = json.load(f)
    ans_path = os.path.join(d, "answers.json")
    if not os.path.exists(ans_path):
        print(f"! no answers.json in {d} — run the blind pass first")
        return
    with open(ans_path) as f:
        answers = json.load(f)

    hits = 0
    answered = 0
    declines = 0
    by_conf = {c: {"n": 0, "hit": 0} for c in CONF_ORDER}
    misses = []

    for fname, t in truth.items():
        a = answers.get(fname)
        if not a:
            print(f"! {fname}: missing answer")
            continue
        conf = norm(a.get("conf")) or "low"
        by_conf.setdefault(conf, {"n": 0, "hit": 0})
        if conf == "decline":
            declines += 1
            by_conf[conf]["n"] += 1
            continue
        answered += 1
        by_conf[conf]["n"] += 1
        verdict = classify(a.get("cluster", ""), t.get("seed_country", ""))
        if verdict in ("exact", "region"):
            hits += 1
            by_conf[conf]["hit"] += 1
        else:
            misses.append((fname, a.get("cluster"), t.get("seed_country"), conf))

    total = len(truth)
    print(f"=== rapid blind score: {d} ===")
    print(f"total photos      : {total}")
    print(f"answered          : {answered}")
    print(f"declined (neutral): {declines}")
    acc_answered = hits / answered if answered else 0
    acc_total = hits / total if total else 0
    print(f"country hits      : {hits}/{answered}  "
          f"= {acc_answered*100:.0f}% of answered")
    print(f"of all photos     : {hits}/{total}  = {acc_total*100:.0f}%")
    print()
    print("by confidence bucket:")
    for c in CONF_ORDER:
        b = by_conf[c]
        if b["n"] == 0:
            continue
        rate = b["hit"] / b["n"] if c != "decline" else float("nan")
        tag = "neutral" if c == "decline" else f"{rate*100:.0f}%"
        print(f"  {c:<8} n={b['n']:<3} hit={b['hit']:<3} {tag}")
    print()
    if misses:
        print(f"misses ({len(misses)}) — said -> truth (conf):")
        for fn, said, truth_c, conf in misses:
            print(f"  {fn}: {said}  ->  {truth_c}  ({conf})")
    else:
        print("no misses among answered photos 🎯")


if __name__ == "__main__":
    main()
