import math
from collections import Counter
from toolkits import TOOLKITS, FAMILY_NAMES

def entropy(labels):
    """labels: a list of family IDs, e.g. [0,1,1,2,0,...]
    Returns entropy in bits. 0 = perfectly pure (all one class). 
    log2(3) ~= 1.58 = maximum possible for 3 classes (perfectly even split)."""
    n = len(labels)
    if n == 0:
        return 0.0
    counts = Counter(labels)
    h = 0.0
    for family_id, count in counts.items():
        p = count / n              # proportion of this family in the group
        h -= p * math.log2(p)      # subtract p * log2(p), per the formula
    return h

if __name__ == "__main__":
    all_labels = [t[8] for t in TOOLKITS]
    print("Family counts:", Counter(all_labels))
    print("Entropy of the WHOLE dataset (32 toolkits):", round(entropy(all_labels), 4), "bits")

    # sanity checks so you can see the formula behaving as expected
    print()
    print("Sanity check 1 - a PURE group (all same family), entropy should be 0:")
    print("  entropy([1,1,1,1]) =", entropy([1,1,1,1]))

    print()
    print("Sanity check 2 - a perfectly EVEN 3-way split, entropy should be near max (~1.585):")
    print("  entropy([0,1,2,0,1,2]) =", round(entropy([0,1,2,0,1,2]), 4))
