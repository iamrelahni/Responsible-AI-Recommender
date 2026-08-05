from collections import defaultdict
from toolkits import TOOLKITS, GROUPS
from entropy import entropy

def bucket(score):
    """Turn a continuous 0-2 score into Low/Medium/High, mirroring the
    original 0/1/2 ordinal scale (thirds of the 0-2 range)."""
    if score < 0.67:
        return "Low"
    elif score < 1.33:
        return "Medium"
    else:
        return "High"

def build_categorical_dataset():
    """Returns a list of dicts, one per toolkit: 
    {'B':'High','C':'Medium',...,'family':1}"""
    data = []
    for row in TOOLKITS:
        tid, name = row[0], row[1]
        scores = row[2:8]   # B,C,D,E,SI,AG in that order
        family = row[8]
        record = {group: bucket(score) for group, score in zip(GROUPS, scores)}
        record["family"] = family
        record["id"] = tid
        data.append(record)
    return data

def information_gain(data, attribute):
    """data: list of toolkit records (dicts). attribute: e.g. 'D'.
    Returns entropy(whole group) - weighted average entropy(each branch)."""
    parent_labels = [d["family"] for d in data]
    parent_entropy = entropy(parent_labels)

    # split the data into branches, one per category value (Low/Medium/High)
    branches = defaultdict(list)
    for d in data:
        branches[d[attribute]].append(d["family"])

    n = len(data)
    weighted_child_entropy = 0.0
    for value, labels in branches.items():
        weight = len(labels) / n
        weighted_child_entropy += weight * entropy(labels)

    gain = parent_entropy - weighted_child_entropy
    return gain, branches

if __name__ == "__main__":
    data = build_categorical_dataset()

    print("First 3 toolkits after bucketing, so you can see the conversion:")
    for d in data[:3]:
        print(" ", d)
    print()

    print("Information gain for EACH of the six attributes, tested independently:")
    print("(higher = this question splits the 32 toolkits into more family-pure groups)")
    print()
    results = []
    for attr in GROUPS:
        gain, branches = information_gain(data, attr)
        results.append((attr, gain, branches))

    results.sort(key=lambda x: -x[1])  # best first
    for attr, gain, branches in results:
        branch_sizes = {v: len(labels) for v, labels in branches.items()}
        print(f"  {attr:3} -> gain = {gain:.4f} bits   (branch sizes: {branch_sizes})")
