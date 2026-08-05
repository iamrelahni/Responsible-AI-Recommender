from toolkits import FAMILY_NAMES
from info_gain import build_categorical_dataset
from tree import build_tree, Leaf, Node
from toolkits import GROUPS

def predict(node, record):
    """Walk the tree using this toolkit's own bucketed values (Low/Medium/High)
    until we hit a Leaf, then return its probability distribution."""
    while isinstance(node, Node):
        value = record[node.attribute]
        if value not in node.branches:
            # This toolkit's value wasn't seen at this branch during training.
            # Be honest about it rather than guessing silently.
            return None
        node = node.branches[value]
    return node.probabilities  # now a Leaf

if __name__ == "__main__":
    data = build_categorical_dataset()
    tree = build_tree(data, list(GROUPS))

    print("Testing the tree against the SAME 32 toolkits it was built from.")
    print("(This checks the code works and shows training fit -- it does NOT")
    print(" prove the tree will generalise to a new, unseen toolkit #33.)\n")

    correct = 0
    print(f"{'ID':4} {'True family':26} {'Predicted (top)':26} {'Confidence':10} Match?")
    for d in data:
        probs = predict(tree, d)
        true_family = FAMILY_NAMES[d["family"]]
        if probs is None:
            print(f"{d['id']:4} {true_family:26} {'NO MATCHING BRANCH':26}")
            continue
        top_family_id = max(probs, key=probs.get)
        top_family_name = FAMILY_NAMES[top_family_id]
        confidence = probs[top_family_id]
        is_match = (top_family_id == d["family"])
        correct += is_match
        mark = "YES" if is_match else "no"
        print(f"{d['id']:4} {true_family:26} {top_family_name:26} {confidence:>8.0%}  {mark}")

    print()
    print(f"Training accuracy: {correct}/{len(data)} = {correct/len(data):.0%}")
