from collections import Counter, defaultdict
from toolkits import GROUPS, FAMILY_NAMES
from entropy import entropy
from info_gain import build_categorical_dataset, information_gain

MIN_BRANCH_SIZE = 4   # stop splitting if fewer than this many toolkits remain
MAX_DEPTH = 3          # stop splitting after this many questions deep

class Leaf:
    """A final node: no more splitting. Holds the toolkits that landed here
    and their family probabilities."""
    def __init__(self, data):
        self.data = data
        n = len(data)
        counts = Counter(d["family"] for d in data)
        # probability of each family = its share of the toolkits in this leaf
        self.probabilities = {fam: counts.get(fam, 0) / n for fam in FAMILY_NAMES}
        self.toolkit_ids = [d["id"] for d in data]

class Node:
    """A question node: splits the data by one attribute into branches."""
    def __init__(self, attribute, branches):
        self.attribute = attribute          # e.g. "AG"
        self.branches = branches            # dict: value (e.g. "High") -> child Node or Leaf

def build_tree(data, available_attributes, depth=0):
    labels = [d["family"] for d in data]

    # Stopping rule 1: pure group, nothing left to learn
    if entropy(labels) == 0.0:
        return Leaf(data)
    # Stopping rule 2: too few toolkits to trust a further split
    if len(data) < MIN_BRANCH_SIZE:
        return Leaf(data)
    # Stopping rule 3: no attributes left to test
    if not available_attributes:
        return Leaf(data)
    # Stopping rule 4: tree is already as deep as we've allowed
    if depth >= MAX_DEPTH:
        return Leaf(data)

    # Rank all remaining attributes by information gain, best first
    ranked = []
    for attr in available_attributes:
        gain, _ = information_gain(data, attr)
        ranked.append((gain, attr))
    ranked.sort(key=lambda x: -x[0])

    # Walk down the ranked list; only accept the FIRST attribute whose split
    # doesn't produce any branch smaller than MIN_BRANCH_SIZE.
    chosen_attr = None
    chosen_groups = None
    for gain, attr in ranked:
        if gain <= 0:
            continue  # this attribute tells us nothing, skip it
        groups = defaultdict(list)
        for d in data:
            groups[d[attr]].append(d)
        branch_sizes = [len(v) for v in groups.values()]
        if min(branch_sizes) >= MIN_BRANCH_SIZE:
            chosen_attr = attr
            chosen_groups = groups
            break  # good split found, stop searching

    # Stopping rule 5: no attribute could split without creating a tiny branch
    if chosen_attr is None:
        return Leaf(data)

    remaining_attrs = [a for a in available_attributes if a != chosen_attr]
    branches = {}
    for value, subset in chosen_groups.items():
        branches[value] = build_tree(subset, remaining_attrs, depth + 1)

    return Node(chosen_attr, branches)


def print_tree(node, indent=""):
    """Prints the whole tree so nothing is hidden."""
    if isinstance(node, Leaf):
        probs = ", ".join(f"{FAMILY_NAMES[f][:12]}={p:.0%}" for f, p in sorted(node.probabilities.items(), key=lambda x:-x[1]) if p > 0)
        print(f"{indent}LEAF ({len(node.data)} toolkits: {node.toolkit_ids}) -> {probs}")
    else:
        for value, child in node.branches.items():
            print(f"{indent}IF {node.attribute} = {value}:")
            print_tree(child, indent + "    ")


if __name__ == "__main__":
    data = build_categorical_dataset()
    tree = build_tree(data, list(GROUPS))
    print("The full trained tree:\n")
    print_tree(tree)
