from toolkits import TOOLKITS, GROUPS, FAMILY_NAMES
from subcriteria import SUBCRITERIA
from mapping import answers_to_profile, apply_scope_filter
from sequencing import sequencing_tags
from tree import build_tree
from test_tree import predict
from info_gain import build_categorical_dataset

# Q3: primary concern -> which score to prioritise for ranking.
# 4 options point at a specific D sub-criterion; 2 point at a whole group.
Q3_TARGET = {
    "fairness": ("sub", "fair"),
    "explainability": ("sub", "explain"),
    "privacy": ("sub", "priv"),
    "security": ("sub", "sec"),
    "compliance": ("group", "AG"),
    "trust": ("group", "SI"),
}

# lookup: toolkit ID -> full record (name, group scores, family)
TOOLKIT_BY_ID = {t[0]: t for t in TOOLKITS}
GROUP_INDEX = {g: i + 2 for i, g in enumerate(GROUPS)}  # position in the TOOLKITS tuple


def fit_score(toolkit_id, q3_answer):
    """Score 0-1: how well this toolkit matches the SME's stated priority (Q3).
    Deliberately does NOT blend in the toolkit's overall six-group average.
    Blending would penalise specialist toolkits (e.g. AI Fairness 360, which
    scores a perfect 2/2 on fairness but has a low overall average because it
    ignores privacy/security/explainability by design) for their low breadth --
    which is exactly the aggregation bias this dissertation argues against.
    Overall average is returned separately, for display/context only."""
    kind, key = Q3_TARGET[q3_answer]

    if kind == "sub":
        targeted_raw = SUBCRITERIA[toolkit_id][key]   # 0, 1, or 2
    else:  # "group"
        targeted_raw = TOOLKIT_BY_ID[toolkit_id][GROUP_INDEX[key]]  # continuous 0-2

    return targeted_raw / 2.0


def overall_average(toolkit_id):
    """For display only -- not used in ranking."""
    record = TOOLKIT_BY_ID[toolkit_id]
    return sum(record[GROUP_INDEX[g]] for g in GROUPS) / len(GROUPS) / 2.0


import json
with open("evidence_dump.json") as f:
    EVIDENCE = json.load(f)

Q3_CRITERION_LABEL = {
    "fairness": "fair", "explainability": "explain", "privacy": "priv",
    "security": "sec", "compliance": "AG", "trust": "SI",
}


FALLBACK_TOOLKIT_ID = "T21"  # NIST AI RMF: highest overall score (1.84), four perfect
# group scores, framework-agnostic. Chosen specifically because both known gap
# patterns (AG=High+C=Low, AG=Medium+E=Low) only affect organisations that already
# have some governance maturity -- exactly where NIST's comprehensiveness fits,
# and its one real weakness (assumes organisational maturity) doesn't apply here.


def recommend(tree, q1, q2, q3, q4, q5, q6):
    """Full pipeline: answers -> profile -> family probabilities (adjusted by
    Q6 scope) -> TIERED shortlist of toolkits.
    If no tree leaf matches this exact profile (a genuine data gap, not an
    error), falls back to a single, clearly-labelled universal recommendation
    rather than showing nothing."""
    profile = answers_to_profile(q1, q2, q4, q5)
    family_probs = predict(tree, profile)

    if family_probs is None:
        fallback = next(t for t in TOOLKITS if t[0] == FALLBACK_TOOLKIT_ID)
        return [[{
            "id": fallback[0], "name": fallback[1], "family": FAMILY_NAMES[fallback[8]],
            "family_p": None, "fit": None, "overall": overall_average(fallback[0]),
            "evidence": EVIDENCE[fallback[0]][Q3_CRITERION_LABEL[q3]],
            "sequencing": sequencing_tags(fallback[0], q1),
            "is_fallback": True,
        }]]

    family_probs = apply_scope_filter(family_probs, q6)

    candidates = []
    for family_id, family_p in family_probs.items():
        if family_p <= 0:
            continue
        for t in TOOLKITS:
            if t[8] == family_id:
                fit = fit_score(t[0], q3)
                overall = overall_average(t[0])
                candidates.append({
                    "id": t[0], "name": t[1], "family": FAMILY_NAMES[family_id],
                    "family_p": family_p, "fit": fit, "overall": overall,
                    "evidence": EVIDENCE[t[0]][Q3_CRITERION_LABEL[q3]],
                    "sequencing": sequencing_tags(t[0], q1),
                    "is_fallback": False,
                })

    # Group into tiers: same family AND same targeted fit = a genuine tie.
    # Order tiers by (family_p, fit) descending. Order WITHIN a tier by
    # overall_average descending -- shown as supplementary info, not used
    # to break the tie itself (every toolkit in a tier is presented, none dropped).
    candidates.sort(key=lambda c: (-c["family_p"], -c["fit"], -c["overall"]))

    tiers = []
    current_key, current_tier = None, []
    for c in candidates:
        key = (c["family_p"], c["fit"])
        if key != current_key:
            if current_tier:
                tiers.append(current_tier)
            current_tier = [c]
            current_key = key
        else:
            current_tier.append(c)
    if current_tier:
        tiers.append(current_tier)

    return tiers


def print_shortlist(tiers, max_tiers=2):
    for tier_num, tier in enumerate(tiers[:max_tiers], 1):
        rep = tier[0]
        families_in_tier = sorted(set(c["family"] for c in tier))
        print(f"  Tier {tier_num}: targeted fit = {rep['fit']:.1f}/1.0, "
              f"family match {rep['family_p']:.0%} -- {len(tier)} toolkit(s) tied "
              f"(spans: {', '.join(families_in_tier)}):")
        for c in tier:
            seq = ", ".join(c["sequencing"]) if c["sequencing"] else "not stage-matched"
            print(f"    - {c['id']} {c['name'][:38]:40} [{c['family']}]  (overall breadth {c['overall']:.2f}/1.0)  [{seq}]")
            print(f"        why: {c['evidence']}")


if __name__ == "__main__":
    data = build_categorical_dataset()
    tree = build_tree(data, list(GROUPS))

    scenarios = [
        ("Low-maturity, exploring, fairness concern, no resources/expertise, specific system",
         dict(q1="exploring", q2="ad_hoc", q3="fairness", q4="just_my_time", q5="none", q6="specific_system")),
        ("Mature, deployed, compliance concern, full resources/expertise, general approach",
         dict(q1="deployed", q2="formal_audited", q3="compliance", q4="team_and_budget", q5="both", q6="general_approach")),
    ]

    for label, answers in scenarios:
        print(f"--- {label} ---")
        tiers = recommend(tree, **answers)
        print_shortlist(tiers)
        print()
