"""
FormuGraph evaluation harness.

Produces real, repeatable precision/recall/coverage/latency numbers
against small hand-labeled ground-truth sets -- not numbers eyeballed
once and typed into the README. Run this and paste its actual output
into your documentation's Evaluation Methodology section.

Run from the repo root: python tests/evaluate.py

IMPORTANT: the ground-truth lists below only cover the concerns and
ingredients visible in earlier testing (Acne & Blemishes, Redness &
Sensitivity). Expand them to match every row in your real
concern_ingredient_map.csv and conflict_rules.csv before citing these
numbers in your documentation -- an evaluation is only honest if it
actually covers what you built.
"""

import sys
import time

sys.path.insert(0, "src")
# pyrefly: ignore [missing-import]
from recommender import Recommender
# pyrefly: ignore [missing-import]
from conflict_checker import ConflictChecker

# ---------------------------------------------------------------------
# Ground truth: (concern, ingredient, should_be_mapped)
# Sourced from the same dermatology knowledge used to build the map --
# this catches obvious mapping errors (wrong ingredient under wrong
# concern), not deep clinical validation.
# ---------------------------------------------------------------------
CONCERN_INGREDIENT_TRUTH = [
    ("Acne & Blemishes", "salicylic acid", True),
    ("Acne & Blemishes", "benzoyl peroxide", True),
    ("Acne & Blemishes", "zinc", True),
    ("Acne & Blemishes", "hyaluronic acid", False),   # hydrator, not an acne active
    ("Acne & Blemishes", "centella asiatica", False),  # belongs under Redness, not Acne
    ("Redness & Sensitivity", "centella asiatica", True),
    ("Redness & Sensitivity", "panthenol", True),
    ("Redness & Sensitivity", "salicylic acid", False),  # acne active, not a redness soother
]

# ---------------------------------------------------------------------
# Known ingredient conflicts (should be flagged) and known-safe pairs
# (should NOT be flagged) -- both from well-documented dermatology
# guidance, not invented.
# ---------------------------------------------------------------------
KNOWN_CONFLICTS = [
    ("Retinol, Squalane", "Water, Glycolic Acid, Aloe Vera Extract"),
    ("Water, Salicylic Acid, Panthenol", "Squalane, Retinol, Simmondsia Chinensis Oil"),
]

KNOWN_SAFE = [
    ("Water, Ceramide NP, Hyaluronic Acid, Glycerin", "Water, Niacinamide, Zinc PCA, Salicylic Acid"),
    ("Water, Centella Asiatica Extract, Madecassoside, Panthenol", "Water, Ceramide NP, Hyaluronic Acid, Glycerin"),
]


def evaluate_concern_mapping(rec):
    tp = fp = fn = tn = 0
    for concern, ingredient, should_map in CONCERN_INGREDIENT_TRUTH:
        subset = rec.concern_map[rec.concern_map["concern"] == concern]
        is_mapped = ingredient.lower() in subset["ingredient"].values
        if should_map and is_mapped:
            tp += 1
        elif should_map and not is_mapped:
            fn += 1
        elif not should_map and is_mapped:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    return {"precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def evaluate_conflict_detection(checker):
    tp = fp = fn = tn = 0
    for candidate, existing in KNOWN_CONFLICTS:
        detected = len(checker.check(candidate, [existing])) > 0
        tp += detected
        fn += not detected
    for candidate, existing in KNOWN_SAFE:
        detected = len(checker.check(candidate, [existing])) > 0
        fp += detected
        tn += not detected
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    return {"precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn, "tn": tn}


def evaluate_coverage(rec):
    """% of the product catalog reachable through at least one concern match."""
    all_ingredients = set(rec.concern_map["ingredient"].unique())
    reachable = rec.products["_ingredients_lower"].apply(
        lambda text: any(ing in text for ing in all_ingredients)
    )
    return reachable.mean()


def evaluate_latency(rec, n_runs=20):
    concerns = list(rec.concern_map["concern"].unique())
    times = []
    for i in range(n_runs):
        start = time.perf_counter()
        rec.recommend([concerns[i % len(concerns)]])
        times.append((time.perf_counter() - start) * 1000)
    return sum(times) / len(times)


if __name__ == "__main__":
    rec = Recommender()
    checker = ConflictChecker()

    print("=== Concern -> Ingredient Mapping ===")
    m = evaluate_concern_mapping(rec)
    print(f"Precision: {m['precision']:.2f}  Recall: {m['recall']:.2f}  "
          f"(TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']})")

    print("\n=== Conflict Detection ===")
    c = evaluate_conflict_detection(checker)
    print(f"Precision: {c['precision']:.2f}  Recall: {c['recall']:.2f}  "
          f"(TP={c['tp']} FP={c['fp']} FN={c['fn']} TN={c['tn']})")

    print("\n=== Catalog Coverage ===")
    cov = evaluate_coverage(rec)
    print(f"{cov*100:.1f}% of catalog reachable through at least one concern match")

    print("\n=== Latency ===")
    lat = evaluate_latency(rec)
    print(f"Average recommend() call: {lat:.2f} ms")