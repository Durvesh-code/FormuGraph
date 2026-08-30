"""
FormuGraph explain layer -- the one place an LLM is used in this project.

Strict boundary, enforced by what context the model is given:
- It NEVER decides which product to recommend -- that's already decided
  by Recommender before this file is ever called.
- It NEVER invents or softens a conflict -- conflicts come verbatim from
  ConflictChecker and are marked "do not soften" in the prompt.
- It MAY explain what a well-known ingredient does, in plain language,
  when the curated table has no entry yet -- that's low-stakes, factual,
  general knowledge, not a safety claim.

If no API key is configured, or the call fails for any reason, every
function returns None. The app must keep working correctly on the
deterministic text alone -- this layer is enhancement, not a dependency.
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You explain skincare product recommendations to someone with
no chemistry background. You are given verified facts computed by a
deterministic matching and safety-conflict engine.

Rules you must follow:
- Never contradict, soften, or omit a line marked CONFLICT WARNING.
- Never invent a conflict that isn't listed.
- Never suggest or imply a different product than the one given.
- For ingredients with no listed reason, you may add ONE short,
  well-established, general-knowledge explanation of what that
  ingredient is commonly used for. Keep it factual and plain, not
  clinical-sounding or overconfident.
- Keep answers short: 2-4 sentences, unless the user asks for more detail."""


def _get_model():
    """Returns the OpenAI model name configured in .env / secrets or fallback to default."""
    model = os.environ.get("OPENAI_MODEL") or os.environ.get("OPENAI_MODEL_NAME")
    if not model:
        try:
            model = st.secrets.get("OPENAI_MODEL") or st.secrets.get("OPENAI_MODEL_NAME")
        except Exception:
            model = None
    return model or DEFAULT_MODEL


def _get_client():
    """Returns an OpenAI API client, or None if no key is configured / package missing."""
    if OpenAI is None:
        return None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def _build_product_context(row, concerns, skin_type, conflicts):
    """
    One grounded fact-block, reused by both functions below, so the LLM
    always works from exactly the same verified facts the UI already
    showed the user -- nothing extra, nothing hidden.
    """
    lines = [f"Product: {row['brand']} — {row['name']} ({row['category']}, ${row['price']})"]
    lines.append(f"Targeted concern(s): {', '.join(concerns)}")

    lines.append("Matched ingredients (from a hand-curated dermatology reference table):")
    for m in row["matched_ingredients"]:
        lines.append(f"  - {m['ingredient']}: {m['why']}")

    if skin_type:
        for b in row.get("skin_type_boosts", []):
            lines.append(f"Skin-type note (good fit for {skin_type}): {b['ingredient']} — {b['why']}")
        for c in row.get("skin_type_cautions", []):
            lines.append(f"Skin-type caution (for {skin_type}): {c['ingredient']} — {c['why']}")

    if conflicts:
        for c in conflicts:
            lines.append(
                f"CONFLICT WARNING (verified, do not soften): {c['ingredient_a']} + "
                f"{c['ingredient_b']} — {c['severity']} risk. {c['reason']} "
                f"Fix: {c['solution']}"
            )
    else:
        lines.append("No known conflicts with the user's existing routine.")

    return "\n".join(lines)


def explain_recommendation(row, concerns, skin_type, conflicts):
    """One-time grounded explanation for why this product is the top pick."""
    client = _get_client()
    if client is None:
        return None

    context = _build_product_context(row, concerns, skin_type, conflicts)
    prompt = (
        f"{context}\n\n"
        "In 2-4 plain-language sentences, explain why this product is a strong "
        "match and flag anything the user should know before using it."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    target_model = _get_model()
    try:
        response = client.chat.completions.create(
            model=target_model,
            max_completion_tokens=250,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception:
        # If primary model hits rate limit or quota, fallback to gpt-4o-mini
        if target_model != DEFAULT_MODEL:
            try:
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    max_completion_tokens=250,
                    messages=messages,
                )
                return response.choices[0].message.content
            except Exception:
                return None
        return None


def answer_followup(row, concerns, skin_type, conflicts, chat_history, question):
    """
    Grounded Q&A about the same product. chat_history is a list of
    {"role": "user"|"assistant", "content": str} dicts from prior turns
    in this session, so the conversation can continue naturally.
    """
    client = _get_client()
    if client is None:
        return None

    context = _build_product_context(row, concerns, skin_type, conflicts)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context for this conversation:\n{context}"},
        {"role": "assistant", "content": "Understood, I'll answer using only these facts."},
    ]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": question})

    target_model = _get_model()
    try:
        response = client.chat.completions.create(
            model=target_model,
            max_completion_tokens=300,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception:
        # If primary model hits rate limit or quota, fallback to gpt-4o-mini
        if target_model != DEFAULT_MODEL:
            try:
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    max_completion_tokens=300,
                    messages=messages,
                )
                return response.choices[0].message.content
            except Exception:
                return None
        return None


def generate_routine_schedule(product_category: str) -> dict:
    """Returns dynamic AM/PM application placement and step sequence based on formulation vehicle."""
    cat = str(product_category).lower()
    if "sunscreen" in cat or "spf" in cat:
        return {
            "timing": "AM Routine Only",
            "step": "Final Step (Step 5)",
            "guideline": "Apply generously as the final step before makeup / sun exposure. Reapply every 2 hours outdoors.",
            "badge_color": "#00D4FF"
        }
    elif "cleanser" in cat or "wash" in cat or "scrub" in cat:
        return {
            "timing": "AM & PM Routine",
            "step": "First Step (Step 1)",
            "guideline": "Massage onto damp skin for 60 seconds; rinse thoroughly with lukewarm water.",
            "badge_color": "#00F29D"
        }
    elif "toner" in cat or "exfoliant" in cat or "peel" in cat:
        return {
            "timing": "PM Preferred",
            "step": "Pre-Treatment (Step 2)",
            "guideline": "Apply immediately after cleansing. For active acids, limit use to 2-3 nights per week.",
            "badge_color": "#A78BFA"
        }
    elif "serum" in cat or "oil" in cat or "treatment" in cat:
        return {
            "timing": "AM & PM Routine",
            "step": "Target Treatment (Step 3)",
            "guideline": "Apply 3-4 drops onto clean, slightly damp skin before heavier creams.",
            "badge_color": "#00F29D"
        }
    elif "eye" in cat:
        return {
            "timing": "AM & PM Routine",
            "step": "Eye Contour (Step 3.5)",
            "guideline": "Gently pat around the orbital bone using your ring finger without pulling skin.",
            "badge_color": "#F4A261"
        }
    elif "night" in cat or "mask" in cat:
        return {
            "timing": "PM Routine Only",
            "step": "Overnight Seal (Step 4)",
            "guideline": "Apply as the final evening layer to deeply lock in active hydration overnight.",
            "badge_color": "#6366F1"
        }
    else:
        return {
            "timing": "AM & PM Routine",
            "step": "Barrier Lock (Step 4)",
            "guideline": "Smooth evenly over face and neck to seal in treatment actives and support lipid barrier.",
            "badge_color": "#00F29D"
        }