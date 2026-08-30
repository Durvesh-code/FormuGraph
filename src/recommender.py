"""
FormuGraph recommender core: concern -> ingredient -> product matching,
with skin-type as a soft score adjustment and allergens as a hard
exclusion filter applied before scoring.

Deterministic, explainable, no model training, no API calls.
"""

import pandas as pd


class Recommender:
    def __init__(
        self,
        products_path: str = "data/processed/products_clean.csv",
        concern_map_path: str = "data/concern_ingredient_map.csv",
        skin_type_path: str = "data/skin_type_fit.csv",
        allergens_path: str = "data/allergens.csv",
    ):
        self.products = pd.read_csv(products_path)
        self.concern_map = pd.read_csv(concern_map_path)
        self.skin_type_map = pd.read_csv(skin_type_path)
        self.allergens = pd.read_csv(allergens_path)

        # Normalize once up front so every match below is a cheap
        # lowercase substring check instead of re-normalizing per call.
        self.products["_ingredients_lower"] = (
            self.products["ingredients"].astype(str).str.lower()
        )
        self.concern_map["ingredient"] = self.concern_map["ingredient"].astype(str).str.lower()
        self.skin_type_map["ingredient"] = self.skin_type_map["ingredient"].astype(str).str.lower()
        self.allergens["ingredient_keyword"] = self.allergens["ingredient_keyword"].astype(str).str.lower()

    def _ingredients_for_concerns(self, concerns):
        subset = self.concern_map[self.concern_map["concern"].isin(concerns)]
        if subset.empty:
            raise ValueError(
                f"No known ingredients mapped to concerns: {concerns}. "
                "Check the exact concern labels in concern_ingredient_map.csv."
            )
        return subset

    def _score_concerns(self, ingredients_text, target_ingredients):
        """Sum of weights of every matched concern-ingredient, with reasons."""
        score = 0.0
        matched = []
        for _, row in target_ingredients.iterrows():
            if row["ingredient"] in ingredients_text:
                score += row["weight"]
                why = row.get("why")
                if pd.isna(why):
                    why = "no explanation on file for this ingredient yet"
                matched.append({"ingredient": row["ingredient"], "why": why})
        return score, matched

    def _score_skin_type(self, ingredients_text, skin_type):
        """
        Soft adjustment: boosts add to the score, avoids subtract from it.
        Never excludes a product outright — that's what allergens are for.
        """
        if not skin_type:
            return 0.0, [], []
        rows = self.skin_type_map[self.skin_type_map["skin_type"] == skin_type]

        delta = 0.0
        boosts, cautions = [], []
        for _, row in rows.iterrows():
            if row["ingredient"] in ingredients_text:
                entry = {"ingredient": row["ingredient"], "why": row["why"]}
                if row["effect"] == "boost":
                    delta += row["weight"]
                    boosts.append(entry)
                elif row["effect"] == "avoid":
                    delta -= row["weight"]
                    cautions.append(entry)
        return delta, boosts, cautions

    def _exclude_allergens(self, products_df, allergens):
        """
        Hard filter — drop any product containing an ingredient tied to a
        selected allergen. Runs before scoring, so excluded products never
        appear at all, regardless of how well they'd otherwise match.
        """
        if not allergens:
            return products_df
        keywords = self.allergens[self.allergens["allergen_label"].isin(allergens)][
            "ingredient_keyword"
        ].tolist()
        if not keywords:
            return products_df
        mask = products_df["_ingredients_lower"].apply(
            lambda text: not any(kw in text for kw in keywords)
        )
        return products_df[mask]

    def recommend(
        self,
        concerns,
        skin_type=None,
        allergens=None,
        top_n_per_category=3,
        min_score=0.1,
    ):
        """
        Ranked recommendations. Order of operations matters:
        1. Allergens exclude products entirely (safety first).
        2. Concern-matching produces the base score.
        3. Skin-type nudges that score up or down.
        4. Results are capped per category for diversity.
        """
        target_ingredients = self._ingredients_for_concerns(concerns)
        candidates = self._exclude_allergens(self.products, allergens)

        results = []
        for _, product in candidates.iterrows():
            base_score, matched = self._score_concerns(
                product["_ingredients_lower"], target_ingredients
            )
            skin_delta, boosts, cautions = self._score_skin_type(
                product["_ingredients_lower"], skin_type
            )
            final_score = round(base_score + skin_delta, 2)

            if final_score >= min_score:
                results.append(
                    {
                        "brand": product["brand"],
                        "name": product["name"],
                        "category": product["standard_category"],
                        "price": product["price"],
                        "rating": product["rating"],
                        "score": final_score,
                        "matched_ingredients": matched,
                        "skin_type_boosts": boosts,
                        "skin_type_cautions": cautions,
                        "ingredients_full": product["ingredients"],
                    }
                )

        columns = [
            "brand", "name", "category", "price", "rating", "score",
            "matched_ingredients", "skin_type_boosts", "skin_type_cautions",
            "ingredients_full",
        ]
        if not results:
            return pd.DataFrame(columns=columns)

        results_df = pd.DataFrame(results).sort_values("score", ascending=False)
        capped = (
            results_df.groupby("category", group_keys=False)
            .head(top_n_per_category)
            .sort_values("score", ascending=False)
            .reset_index(drop=True)
        )
        return capped

    def explain(self, row, concerns):
        """Plain-language reason for one recommendation row."""
        if not row["matched_ingredients"]:
            return f"Recommended for {' / '.join(concerns)} — no direct ingredient match."
        parts = [f"{m['ingredient']} ({m['why']})" for m in row["matched_ingredients"]]
        return f"Recommended for {' / '.join(concerns)} — " + "; ".join(parts) + "."


if __name__ == "__main__":
    rec = Recommender()

    print("-- Acne, no skin type, no allergens --")
    picks = rec.recommend(concerns=["Acne & Blemishes"], top_n_per_category=2)
    for _, r in picks.iterrows():
        print(rec.explain(r, ["Acne & Blemishes"]), "| score:", r["score"])

    print("\n-- Acne, Oily/Acne-Prone skin type --")
    picks2 = rec.recommend(
        concerns=["Acne & Blemishes"], skin_type="Oily / Acne-Prone", top_n_per_category=2
    )
    for _, r in picks2.iterrows():
        print(r["name"], "| score:", r["score"], "| boosts:", r["skin_type_boosts"], "| cautions:", r["skin_type_cautions"])

    print("\n-- Acne, excluding Essential Oils allergen --")
    picks3 = rec.recommend(
        concerns=["Acne & Blemishes"], allergens=["Essential Oils"], top_n_per_category=5
    )
    print("Products returned:", list(picks3["name"]))