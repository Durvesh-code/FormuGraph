"""
FormuGraph conflict checker: cross-references a candidate recommendation
against a user's existing routine using known ingredient-conflict rules.

Fully rule-based — every flag traces back to an explicit row in
conflict_rules.csv. No model, no guessing, no hallucination risk.
"""

import pandas as pd

_SEVERITY_ORDER = {"High": 3, "Medium": 2, "Low": 1}


class ConflictChecker:
    def __init__(self, conflict_rules_path: str = "data/conflict_rules.csv"):
        self.rules = pd.read_csv(conflict_rules_path)
        self.rules["ingredient_a"] = self.rules["ingredient_a"].str.lower()
        self.rules["ingredient_b"] = self.rules["ingredient_b"].str.lower()

    def check(self, candidate_ingredients_text, existing_ingredients_texts):
        """
        Compare a candidate product's ingredients against every product
        already in the user's routine.

        Checks both directions (A in candidate + B in existing, and vice
        versa) since each pair is listed only once in the rules table.

        Returns a list of conflict dicts — empty list means no conflicts.
        """
        candidate_text = str(candidate_ingredients_text).lower()
        conflicts = []

        for existing_text in existing_ingredients_texts:
            existing_text = str(existing_text).lower()

            for _, rule in self.rules.iterrows():
                a, b = rule["ingredient_a"], rule["ingredient_b"]

                a_in_candidate = a in candidate_text
                b_in_candidate = b in candidate_text
                a_in_existing = a in existing_text
                b_in_existing = b in existing_text

                hit = (a_in_candidate and b_in_existing) or (b_in_candidate and a_in_existing)

                if hit:
                    conflicts.append(
                        {
                            "ingredient_a": a,
                            "ingredient_b": b,
                            "severity": rule["severity"],
                            "conflict_type": rule["conflict_type"],
                            "reason": rule["reason"],
                            "solution": rule["solution"],
                        }
                    )

        return conflicts

    def summarize(self, conflicts):
        """One-line summary for display in the UI."""
        if not conflicts:
            return "No known conflicts with your existing routine."
        highest = max(conflicts, key=lambda c: _SEVERITY_ORDER.get(c["severity"], 0))
        return f"{highest['severity']} risk: {highest['reason']} — {highest['solution']}"


if __name__ == "__main__":
    checker = ConflictChecker()
    candidate = "Retinol, Squalane, Simmondsia Chinensis Oil"
    existing = ["Water, Glycolic Acid, Aloe Vera Extract"]

    result = checker.check(candidate, existing)
    print(f"{len(result)} conflict(s) found:\n")
    for c in result:
        print(c)
    print()
    print(checker.summarize(result))