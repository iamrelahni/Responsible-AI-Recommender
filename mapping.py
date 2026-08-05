from tree import build_tree, Leaf, Node
from test_tree import predict
from info_gain import build_categorical_dataset
from toolkits import GROUPS, FAMILY_NAMES

# ---- Q1: lifecycle stage -> C ----
# Monotonic: more lifecycle progress -> higher expected need for lifecycle breadth.
Q1_TO_C = {
    "exploring": "Low",
    "building": "Medium",
    "deployed": "High",
    "multiple_systems": "High",
}

# ---- Q2: current governance practice -> AG ----
Q2_TO_AG = {
    "ad_hoc": "Low",
    "informal": "Low",
    "written_inconsistent": "Medium",
    "formal_audited": "High",
}

# ---- Q4 (resourcing) and Q5 (expertise): combined, INVERTED, -> E ----
# Low capacity (little budget/expertise) means the SME NEEDS a highly usable
# toolkit, so target E is set HIGH for them, not low. High-capacity teams can
# tolerate a less polished/heavier toolkit, so target E is set LOW.
Q4_INDEX = {"just_my_time": 0, "small_budget": 1, "dedicated_team_limited_budget": 2, "team_and_budget": 3}
Q5_INDEX = {"none": 0, "technical_only": 1, "compliance_only": 1, "both": 3}

def capacity_to_E(q4_answer, q5_answer):
    r = Q4_INDEX[q4_answer]
    x = Q5_INDEX[q5_answer]
    capacity = (r + x) / 2   # 0 (lowest) to 3 (highest)
    if capacity <= 1:
        return "High"     # low capacity -> need HIGH usability
    elif capacity <= 2:
        return "Medium"
    else:
        return "Low"       # high capacity -> can tolerate LOW usability toolkits


def answers_to_profile(q1, q2, q4, q5):
    """Turns SME answers into a target profile the tree can classify.
    Only AG, C, E are set with real signal, since that's all the current
    tree actually queries. B, D, SI are set to 'Medium' as neutral
    placeholders in case a future retrained tree ever asks about them."""
    profile = {
        "C": Q1_TO_C[q1],
        "AG": Q2_TO_AG[q2],
        "E": capacity_to_E(q4, q5),
        "B": "Medium", "D": "Medium", "SI": "Medium",  # not used by current tree
    }
    return profile


if __name__ == "__main__":
    data = build_categorical_dataset()
    tree = build_tree(data, list(GROUPS))

    scenarios = [
        ("Low-maturity startup, exploring, no resources, no expertise",
         dict(q1="exploring", q2="ad_hoc", q4="just_my_time", q5="none")),
        ("Mature team, deployed, formal governance, full resources/expertise",
         dict(q1="deployed", q2="formal_audited", q4="team_and_budget", q5="both")),
        ("Mid-size, building, informal governance, small team, technical only",
         dict(q1="building", q2="informal", q4="dedicated_team_limited_budget", q5="technical_only")),
    ]

    for label, answers in scenarios:
        profile = answers_to_profile(**answers)
        result = predict(tree, profile)
        print(f"--- {label} ---")
        print(f"  Target profile: {profile}")
        if result is None:
            print("  -> No matching branch (this combination wasn't seen in training)")
        else:
            for fam_id, p in sorted(result.items(), key=lambda x: -x[1]):
                if p > 0:
                    print(f"  -> {FAMILY_NAMES[fam_id]}: {p:.0%}")
        print()


# ---- Q6: scope -> adjusts family probabilities as a prior nudge ----
# "one specific system" favours technical/audit tools; "general approach"
# favours governance and lifecycle/procurement tools. Applied as a multiplier
# on the tree's output, then renormalised so probabilities still sum to 1.
Q6_MULTIPLIERS = {
    "specific_system": {0: 1.5, 1: 0.85, 2: 0.85},
    "general_approach": {0: 0.7, 1: 1.3, 2: 1.2},
}

def apply_scope_filter(family_probs, q6_answer):
    mults = Q6_MULTIPLIERS[q6_answer]
    adjusted = {fam: p * mults.get(fam, 1.0) for fam, p in family_probs.items()}
    total = sum(adjusted.values())
    if total == 0:
        return family_probs  # safety fallback, shouldn't happen
    return {fam: p / total for fam, p in adjusted.items()}
