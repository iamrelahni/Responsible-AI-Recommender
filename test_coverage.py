import itertools
from tree import build_tree, Node, Leaf
from info_gain import build_categorical_dataset
from toolkits import GROUPS, FAMILY_NAMES
from test_tree import predict

data = build_categorical_dataset()
tree = build_tree(data, list(GROUPS))

# The tree only ever queries AG, C, E (confirmed earlier). Exhaustively test
# every combination of those three -- this is the FULL space any SME's
# mapped profile could ever land in, regardless of which questions they answered.
BUCKETS = ["Low", "Medium", "High"]

print("Exhaustive test: every possible (AG, C, E) combination a mapped SME profile could produce.\n")
missing = []
tested = 0
for ag, c, e in itertools.product(BUCKETS, BUCKETS, BUCKETS):
    profile = {"AG": ag, "C": c, "E": e, "B": "Medium", "D": "Medium", "SI": "Medium"}
    result = predict(tree, profile)
    tested += 1
    if result is None:
        missing.append((ag, c, e))
    else:
        top = max(result, key=result.get)
        print(f"  AG={ag:6} C={c:6} E={e:6} -> {FAMILY_NAMES[top]} ({result[top]:.0%})")

print(f"\nTested {tested} combinations. Missing/no-match: {len(missing)}")
if missing:
    print("These combinations returned NO prediction (would break the UI ungracefully):")
    for m in missing:
        print(" ", m)
else:
    print("Every combination produced a valid prediction. No gaps.")
