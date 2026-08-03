"""A small, printable decision-tree learner.

Deliberately hand-rolled rather than pulled from a library, for two reasons.

* The output has to be *readable*. The question this repository asks is whether a
  solved game has a short description; a 400-node black box would not answer it
  either way, so the learner is depth-limited and prints as nested English.
* Description length is one of the measurements. A learner whose size we control
  lets us report "this many rules, this much accuracy" honestly.

Features are small non-negative integers, so splits are multiway on feature
value. That keeps the printed rule readable ("confinement < 10%") instead of a
chain of binary thresholds.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Node:
    prediction: int
    n: int
    feature: int | None = None
    children: dict = field(default_factory=dict)
    impurity: float = 0.0

    @property
    def is_leaf(self) -> bool:
        return self.feature is None

    def size(self) -> int:
        """Number of nodes -- our stand-in for description length."""
        return 1 + sum(c.size() for c in self.children.values())

    def depth(self) -> int:
        return 1 + max((c.depth() for c in self.children.values()), default=0)


def _entropy(labels) -> float:
    total = len(labels)
    if not total:
        return 0.0
    counts = Counter(labels)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c)


def _majority(labels) -> int:
    return Counter(labels).most_common(1)[0][0]


def fit(rows, labels, n_features: int, max_depth: int = 6, min_samples: int = 30,
        min_gain: float = 1e-3) -> Node:
    """Greedy multiway decision tree minimising label entropy."""
    node = Node(prediction=_majority(labels), n=len(labels), impurity=_entropy(labels))
    if max_depth <= 0 or len(labels) < min_samples or node.impurity == 0.0:
        return node

    best_feature, best_gain, best_partition = None, min_gain, None
    for feature in range(n_features):
        partition: dict = {}
        for row, label in zip(rows, labels):
            partition.setdefault(row[feature], ([], []))
            partition[row[feature]][0].append(row)
            partition[row[feature]][1].append(label)
        if len(partition) < 2:
            continue
        remainder = sum(
            (len(part_labels) / len(labels)) * _entropy(part_labels)
            for _, part_labels in partition.values()
        )
        gain = node.impurity - remainder
        if gain > best_gain:
            best_feature, best_gain, best_partition = feature, gain, partition

    if best_feature is None:
        return node

    node.feature = best_feature
    for value, (part_rows, part_labels) in sorted(best_partition.items()):
        node.children[value] = fit(
            part_rows, part_labels, n_features,
            max_depth=max_depth - 1, min_samples=min_samples, min_gain=min_gain,
        )
    return node


def predict(node: Node, row) -> int:
    return predict_traced(node, row)[0]


def predict_traced(node: Node, row) -> tuple:
    """Return ``(prediction, hit_unseen_value)``.

    The second element matters more than it looks. A rule fitted on a 4x4 board
    can never have seen "the king reaches more than 16 squares", so on 8x8 it
    falls back to an internal node's majority class. That fallback can score
    well by accident, and reporting accuracy without reporting how often it
    fired would turn an artefact into a claim about transfer.
    """
    while not node.is_leaf:
        child = node.children.get(row[node.feature])
        if child is None:
            return node.prediction, True
        node = child
    return node.prediction, False


def fallback_rate(node: Node, rows) -> float:
    """Fraction of rows whose prediction came from an unseen feature value."""
    if not rows:
        return float("nan")
    return sum(predict_traced(node, row)[1] for row in rows) / len(rows)


def accuracy(node: Node, rows, labels) -> float:
    if not labels:
        return float("nan")
    correct = sum(1 for row, label in zip(rows, labels) if predict(node, row) == label)
    return correct / len(labels)


def per_class_accuracy(node: Node, rows, labels, class_names) -> dict:
    totals: Counter = Counter()
    hits: Counter = Counter()
    for row, label in zip(rows, labels):
        totals[label] += 1
        if predict(node, row) == label:
            hits[label] += 1
    return {
        class_names.get(label, str(label)): hits[label] / totals[label]
        for label in sorted(totals)
    }


def majority_baseline(train_labels, test_labels) -> float:
    """Accuracy of always predicting the training set's most common class."""
    if not test_labels:
        return float("nan")
    guess = _majority(train_labels)
    return sum(1 for label in test_labels if label == guess) / len(test_labels)


def render(node: Node, feature_names, class_names, value_labels=None,
           indent: str = "") -> str:
    """Print the tree as nested English."""
    value_labels = value_labels or {}
    if node.is_leaf:
        return f"{indent}=> {class_names.get(node.prediction, node.prediction)} (n={node.n})\n"
    name = feature_names[node.feature]
    labels = value_labels.get(name, {})
    out = ""
    for value, child in node.children.items():
        shown = labels.get(value, value)
        out += f"{indent}if {name} = {shown}:\n"
        out += render(child, feature_names, class_names, value_labels, indent + "    ")
    return out
