from lifecycle_scores import LIFECYCLE_SCORES

# Maps each Q1 answer to the criterion representing "now", and the criterion
# representing the logical "next" stage after it.
STAGE_ORDER = ["exploring", "building", "deployed"]  # "multiple_systems" treated same as deployed
STAGE_TO_CRITERION = {
    "exploring": "C1",
    "building": "C3",     # C2+C3 both count as "building"; C3 (model) as the representative
    "deployed": "C4",
    "multiple_systems": "C4",
}
NEXT_STAGE = {
    "exploring": "building",
    "building": "deployed",
    "deployed": None,          # nothing after deployed in this simple model
    "multiple_systems": None,
}

STRONG_THRESHOLD = 2  # a toolkit "belongs" to a stage if it scores the max (2) on that criterion

def sequencing_tags(toolkit_id, q1_answer):
    """Returns a list of tags: any of 'now', 'next' (can be both, or neither)."""
    scores = LIFECYCLE_SCORES.get(toolkit_id, {})
    tags = []

    now_crit = STAGE_TO_CRITERION[q1_answer]
    if scores.get(now_crit, 0) >= STRONG_THRESHOLD:
        tags.append("now")

    next_stage = NEXT_STAGE[q1_answer]
    if next_stage:
        next_crit = STAGE_TO_CRITERION[next_stage]
        if scores.get(next_crit, 0) >= STRONG_THRESHOLD:
            tags.append("next")

    return tags


if __name__ == "__main__":
    # sanity check against toolkits we already understand well
    print("T01 (Microsoft Responsible Innovation) if SME is 'exploring':", sequencing_tags("T01", "exploring"))
    print("T01 (Microsoft Responsible Innovation) if SME is 'deployed'):", sequencing_tags("T01", "deployed"))
    print("T21 (NIST RMF) if SME is 'exploring':", sequencing_tags("T21", "exploring"))
    print("T21 (NIST RMF) if SME is 'deployed':", sequencing_tags("T21", "deployed"))
