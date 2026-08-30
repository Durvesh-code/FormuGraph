"""
FormuGraph — Next-Gen Clinical Skincare Intelligence & Conflict Engine.
Ultra-premium luxury biotech UI with glassmorphism, cyber-emerald accents,
multi-tab exploration, AM/PM routine scheduler, and GPT-5.6 AI Concierge.
"""

import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from src.recommender import Recommender
from src.conflict_checker import ConflictChecker
from src import explain

# Load environment variables from .env
load_dotenv()

st.set_page_config(
    page_title="FormuGraph — Clinical Skincare Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# LUXURY BIOTECH STYLING (CSS)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

/* Global Reset & Base */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #E2E8F0;
}

/* Prevent Page Dimming / Gray-out on Script Execution */
.stApp[data-test-script-state="running"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section.main {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}

/* Browser-style Top Loading Bar (NProgress / Chrome Style) */
@keyframes browserLoader {
    0% {
        left: 0%;
        width: 0%;
        opacity: 1;
    }
    40% {
        left: 0%;
        width: 55%;
        opacity: 1;
    }
    80% {
        left: 40%;
        width: 60%;
        opacity: 1;
    }
    100% {
        left: 100%;
        width: 0%;
        opacity: 0;
    }
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    height: 3.5px;
    width: 0%;
    background: linear-gradient(90deg, #00F29D 0%, #00D4FF 50%, #9D4EDD 100%);
    box-shadow: 0 0 14px rgba(0, 242, 157, 0.9), 0 0 8px rgba(0, 212, 255, 0.7);
    z-index: 99999999;
    pointer-events: none;
    opacity: 0;
}

.stApp[data-test-script-state="running"]::before {
    opacity: 1;
    animation: browserLoader 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

/* Hide Default Streamlit Running Spinner */
[data-testid="stStatusWidget"] {
    visibility: hidden !important;
}

/* Background Atmosphere */
.stApp {
    background: radial-gradient(circle at 15% 15%, rgba(0, 242, 157, 0.04) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(0, 212, 255, 0.03) 0%, transparent 45%),
                #080C10;
}

/* Hero Branding */
.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FFFFFF 20%, #00F29D 70%, #00D4FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
    line-height: 1.1;
}

.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: rgba(0, 242, 157, 0.1);
    color: #00F29D;
    border: 1px solid rgba(0, 242, 157, 0.3);
    border-radius: 9999px;
    padding: 3px 12px;
    margin-bottom: 8px;
}

/* Ingredient Chips */
.ingredient-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    font-weight: 600;
    background: rgba(0, 242, 157, 0.1);
    color: #00F29D;
    border: 1px solid rgba(0, 242, 157, 0.3);
    border-radius: 6px;
    padding: 3px 10px;
    display: inline-block;
    margin-right: 8px;
}

.chip-row {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 6px 0;
}

/* Badges */
.match-badge-strong {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    background: rgba(0, 242, 157, 0.15);
    color: #00F29D;
    border: 1px solid rgba(0, 242, 157, 0.4);
    border-radius: 6px;
    padding: 4px 10px;
    display: inline-block;
}

.match-badge-good {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    background: rgba(0, 212, 255, 0.15);
    color: #00D4FF;
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-radius: 6px;
    padding: 4px 10px;
    display: inline-block;
}

.match-badge-partial {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    background: rgba(148, 163, 184, 0.12);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 6px;
    padding: 4px 10px;
    display: inline-block;
}

.step-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 600;
    color: #A78BFA;
    background: rgba(167, 139, 250, 0.12);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 6px;
    padding: 3px 10px;
    display: inline-block;
}

.conflict-alert-box {
    background: rgba(255, 118, 68, 0.1);
    color: #FF8F6B;
    border-left: 3px solid #FF7644;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.85rem;
    margin-top: 10px;
}

.safe-shield-box {
    background: rgba(0, 242, 157, 0.08);
    color: #00F29D;
    border: 1px solid rgba(0, 242, 157, 0.25);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 10px;
}

.ai-summary-box {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(167, 139, 250, 0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.25);
    border-radius: 12px;
    padding: 16px 18px;
    font-size: 0.88rem;
    line-height: 1.6;
    color: #E2E8F0;
    margin-top: 8px;
}

.ai-summary-loading {
    background: rgba(15, 23, 42, 0.4);
    border: 1px dashed rgba(0, 212, 255, 0.3);
    border-radius: 12px;
    padding: 24px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    min-height: 140px;
    text-align: center;
    margin-top: 8px;
}

.loading-spinner-cyber {
    width: 28px;
    height: 28px;
    border: 3px solid rgba(0, 242, 157, 0.15);
    border-top-color: #00F29D;
    border-right-color: #00D4FF;
    border-radius: 50%;
    animation: spinCyber 0.85s linear infinite;
}

@keyframes spinCyber {
    to { transform: rotate(360deg); }
}

/* Sidebar Clean Single Labels & Spacing */
section[data-testid="stSidebar"] {
    background-color: #0B0F15 !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
}

/* Clean vertical rhythm */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    gap: 0.75rem !important;
}

section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size: 0.93rem !important;
    font-weight: 700 !important;
    color: #F8FAFC !important;
    margin-bottom: 6px !important;
    letter-spacing: -0.01em !important;
}

section[data-testid="stSidebar"] h3 {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    margin: 4px 0 2px 0 !important;
    padding: 0 !important;
    color: #F8FAFC !important;
    letter-spacing: -0.01em;
}

section[data-testid="stSidebar"] hr {
    margin: 10px 0 !important;
    padding: 0 !important;
    border: none !important;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Smooth & Compact Dropdowns (Select & Multiselect) */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    border-radius: 8px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: rgba(15, 23, 42, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    min-height: 38px !important;
    font-size: 0.86rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    border-color: rgba(0, 242, 157, 0.4) !important;
    background-color: rgba(15, 23, 42, 0.85) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
    border-color: #00F29D !important;
    box-shadow: 0 0 0 1px #00F29D, 0 0 10px rgba(0, 242, 157, 0.2) !important;
}

/* Compact Multiselect Selected Tag Pills */
section[data-testid="stSidebar"] span[data-baseweb="tag"] {
    background-color: rgba(0, 242, 157, 0.12) !important;
    border: 1px solid rgba(0, 242, 157, 0.3) !important;
    border-radius: 6px !important;
    height: 25px !important;
    font-size: 0.78rem !important;
    color: #00F29D !important;
}

section[data-testid="stSidebar"] span[data-baseweb="tag"] span {
    color: #00F29D !important;
}

/* Slider Compact Spacing */
section[data-testid="stSidebar"] div[data-testid="stSlider"] {
    padding-top: 2px !important;
    margin-top: -4px !important;
}

/* Streamlit Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(15, 23, 42, 0.4);
    padding: 6px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94A3B8;
    font-weight: 600;
    padding: 8px 16px;
    border: none;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(0, 242, 157, 0.12) !important;
    color: #00F29D !important;
    border: 1px solid rgba(0, 242, 157, 0.25) !important;
}

/* Button Styling */
div.stButton > button {
    width: 100%;
}
div.stButton > button:first-child {
    width: 100%;
    background: linear-gradient(135deg, #00F29D 0%, #00C2CB 100%);
    color: #080C10;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    box-shadow: 0 4px 20px rgba(0, 242, 157, 0.25);
}

div.stButton > button:first-child:hover {
    box-shadow: 0 6px 28px rgba(0, 242, 157, 0.4);
    color: #040608;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ENGINE INITIALIZATION (CACHED)
# -----------------------------------------------------------------------------
@st.cache_resource
def load_engine():
    return Recommender(), ConflictChecker()


rec, checker = load_engine()


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_match_badge_html(score, max_score):
    if max_score <= 0:
        return '<span class="match-badge-partial">● PARTIAL MATCH</span>'
    ratio = score / max_score
    pct = int(min(100, (score / max(1.0, max_score)) * 100))
    if ratio >= 0.8:
        return f'<span class="match-badge-strong">⚡ STRONG MATCH ({pct}%)</span>'
    if ratio >= 0.5:
        return f'<span class="match-badge-good">✓ GOOD MATCH ({pct}%)</span>'
    return f'<span class="match-badge-partial">● PARTIAL MATCH ({pct}%)</span>'


def render_chips_html(matched_ingredients):
    if not matched_ingredients:
        return '<div style="color: #64748B; font-size: 0.85rem;">No direct active compounds registered.</div>'
    items = []
    for m in matched_ingredients:
        ing_name = str(m.get("ingredient", "")).upper()
        why_text = m.get("why", "Target active compound")
        items.append(
            f'<div class="chip-row">'
            f'<span class="ingredient-chip">{ing_name}</span>'
            f'<span style="font-size: 0.84rem; color: #CBD5E1;">{why_text}</span>'
            f'</div>'
        )
    return "".join(items)


# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="brand-badge">⚡ CLINICAL BIOTECH INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-title">FormuGraph</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color: #94A3B8; font-size: 1.02rem; margin-top: 4px;">'
        'Explainable, conflict-aware skincare recommendations engineered on verified biochemical rules.'
        '</p>',
        unsafe_allow_html=True,
    )

with col_h2:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 15px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00F29D; background: rgba(0,242,157,0.08); padding: 5px 12px; border-radius: 20px; border: 1px solid rgba(0,242,157,0.2);">
                ● SYSTEM OPERATIONAL
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    available_concerns = sorted(rec.concern_map["concern"].unique())
    selected_concerns = st.multiselect(
        "🎯 Skin Concerns",
        available_concerns,
        placeholder="Select skin concerns…",
    )

    skin_types = ["Not sure / skip"] + sorted(rec.skin_type_map["skin_type"].unique())
    skin_type_choice = st.selectbox(
        "💧 Skin Profile",
        skin_types,
        index=0,
    )
    skin_type = None if skin_type_choice == "Not sure / skip" else skin_type_choice

    allergen_options = sorted(rec.allergens["allergen_label"].unique())
    selected_allergens = st.multiselect(
        "🛡️ Allergens & Sensitivities",
        allergen_options,
        placeholder="Select sensitivities to exclude…",
    )

    product_labels = rec.products["name"] + " — " + rec.products["brand"]
    product_lookup = dict(zip(product_labels, rec.products["ingredients"]))
    existing_selection = st.multiselect(
        "🧴 Your Current Routine",
        sorted(product_labels),
        placeholder="Search routine to scan conflicts…",
    )
    existing_ingredients_texts = [product_lookup[p] for p in existing_selection]

    st.markdown("---")
    st.markdown("### ⚙️ Catalog Filters")
    categories = sorted(rec.products["standard_category"].unique())
    category_filter = st.multiselect("Category", categories, placeholder="All categories")
    max_price = float(rec.products["price"].max())
    price_cap = st.slider("Max price ($)", 0.0, max_price, max_price, step=5.0)

    st.markdown("---")
    run = st.button("✨ Formulate Regimen")


# -----------------------------------------------------------------------------
# MAIN APP BODY
# -----------------------------------------------------------------------------
if run or ("last_results" in st.session_state and selected_concerns):
    if not selected_concerns:
        st.warning("⚠️ Please select at least one skin concern in the sidebar first.")
    else:
        results = rec.recommend(
            selected_concerns,
            skin_type=skin_type,
            allergens=selected_allergens,
            top_n_per_category=3,
        )

        if category_filter:
            results = results[results["category"].isin(category_filter)]
        results = results[results["price"] <= price_cap]

        if results.empty:
            st.info("ℹ️ No formulations match your exact filters. Try widening your price cap or category filter.")
        else:
            results = results.sort_values("score", ascending=False).reset_index(drop=True)
            st.session_state.last_results = results
            max_score = float(results["score"].max())
            top_row = results.iloc[0]

            top_conflicts = (
                checker.check(top_row["ingredients_full"], existing_ingredients_texts)
                if existing_ingredients_texts
                else []
            )

            schedule_info = explain.generate_routine_schedule(top_row["category"])

            # 4 Tabs Layout
            tab1, tab2, tab3, tab4 = st.tabs([
                "🏆 Curated Regimen",
                "🧪 Formulation Chemistry",
                "🛡️ Safety & Routine Timeline",
                "💬 AI Clinical Concierge",
            ])

            # -----------------------------------------------------------------
            # TAB 1: CURATED REGIMEN
            # -----------------------------------------------------------------
            with tab1:
                # Top Pick Hero Container
                with st.container(border=True):
                    col_left, col_right = st.columns([1.15, 0.85], gap="large")

                    with col_left:
                        st.markdown(
                            '<span style="font-family: \'JetBrains Mono\', monospace; font-size: 0.72rem; color: #080C10; background: #00F29D; font-weight: 700; padding: 3px 10px; border-radius: 4px;">★ TOP CLINICAL PICK</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"## {top_row['brand']} — {top_row['name']}")
                        
                        rating_str = f"★ {top_row['rating']}" if top_row['rating'] > 0 else "Unrated"
                        st.markdown(
                            f"<div style='display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 0.88rem; color: #94A3B8; margin-top: -8px;'>"
                            f"<span style='color: #00D4FF; font-weight: 600;'>{top_row['category']}</span> • "
                            f"<span style='color: #F8FAFC; font-weight: 600;'>${top_row['price']:.2f}</span> • "
                            f"<span>{rating_str}</span> • "
                            f"<span class='step-pill'>⏱ {schedule_info['timing']} ({schedule_info['step']})</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(
                            "<div style='font-size: 0.78rem; font-family: \"JetBrains Mono\", monospace; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;'>"
                            "Key Matched Active Compounds:</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(render_chips_html(top_row['matched_ingredients']), unsafe_allow_html=True)

                        # Skin-type notes
                        if top_row.get("skin_type_boosts"):
                            for b in top_row["skin_type_boosts"]:
                                st.markdown(
                                    f"<div style='font-size: 0.83rem; color: #00F29D; margin-top: 6px;'>✓ Synergy for {skin_type}: <strong>{b['ingredient'].upper()}</strong> — {b['why']}</div>",
                                    unsafe_allow_html=True,
                                )
                        if top_row.get("skin_type_cautions"):
                            for c in top_row["skin_type_cautions"]:
                                st.markdown(
                                    f"<div style='font-size: 0.83rem; color: #FFB800; margin-top: 6px;'>⚠ Caution for {skin_type}: <strong>{c['ingredient'].upper()}</strong> — {c['why']}</div>",
                                    unsafe_allow_html=True,
                                )

                        # Routine safety alert
                        if existing_ingredients_texts:
                            if top_conflicts:
                                st.markdown(
                                    f"<div class='conflict-alert-box'>⚠️ <strong>Contraindication Warning:</strong> {checker.summarize(top_conflicts)}</div>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    "<div class='safe-shield-box'>🛡️ <strong>No Known Conflicts:</strong> No documented ingredient conflicts detected with your selected routine products.</div>",
                                    unsafe_allow_html=True,
                                )

                    with col_right:
                        # Match Badge at top right
                        st.markdown(
                            f"<div style='text-align: right; margin-bottom: 10px;'>"
                            f"{get_match_badge_html(top_row['score'], max_score)}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                        # AI Grounded Summary with loading placeholder
                        summary_placeholder = st.empty()
                        summary_placeholder.markdown(
                            """
                            <div class="ai-summary-loading">
                                <div class="loading-spinner-cyber"></div>
                                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #00D4FF;">
                                    ⚡ Synthesizing clinical formulation report…
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        ai_exp = explain.explain_recommendation(top_row, selected_concerns, skin_type, top_conflicts)
                        if ai_exp:
                            summary_placeholder.markdown(
                                f"<div class='ai-summary-box'>"
                                f"<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.72rem; color: #00D4FF; letter-spacing: 0.05em; margin-bottom: 8px; font-weight: 700;'>"
                                f"🤖 CLINICAL SUMMARY</div>"
                                f"<div style='font-size: 0.88rem; line-height: 1.55; color: #E2E8F0;'>{ai_exp}</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            summary_placeholder.markdown(
                                f"<div class='ai-summary-box'>"
                                f"<div style='font-family: \"JetBrains Mono\", monospace; font-size: 0.72rem; color: #00D4FF; letter-spacing: 0.05em; margin-bottom: 8px; font-weight: 700;'>"
                                f"🤖 CLINICAL SUMMARY</div>"
                                f"<div style='font-size: 0.85rem; color: #94A3B8;'>"
                                f"Target active compounds match your selected skin concerns ({', '.join(selected_concerns)})."
                                f"</div></div>",
                                unsafe_allow_html=True,
                            )

                # Alternative recommendations
                rest = results.iloc[1:]
                if not rest.empty:
                    st.markdown("### 🔬 Ranked Alternative Formulations")
                    col_a, col_b = st.columns(2)
                    for idx, (_, alt) in enumerate(rest.iterrows()):
                        col = col_a if idx % 2 == 0 else col_b
                        alt_schedule = explain.generate_routine_schedule(alt["category"])
                        rating_alt = f"★ {alt['rating']}" if alt['rating'] > 0 else "Unrated"
                        with col:
                            with st.container(border=True):
                                col_t, col_m = st.columns([3, 1])
                                with col_t:
                                    st.markdown(f"#### {alt['brand']} — {alt['name']}")
                                    st.caption(f"{alt['category']} • ${alt['price']:.2f} • {rating_alt}")
                                with col_m:
                                    st.markdown(get_match_badge_html(alt['score'], max_score), unsafe_allow_html=True)

                                st.markdown(render_chips_html(alt['matched_ingredients'][:2]), unsafe_allow_html=True)
                                st.markdown(
                                    f"<div style='font-size: 0.78rem; color: #A78BFA; font-family: \"JetBrains Mono\", monospace; margin-top: 8px;'>"
                                    f"⏱ {alt_schedule['timing']} ({alt_schedule['step']})</div>",
                                    unsafe_allow_html=True,
                                )

            # -----------------------------------------------------------------
            # TAB 2: FORMULATION CHEMISTRY
            # -----------------------------------------------------------------
            with tab2:
                st.markdown(f"### 🧪 Active Compound Matrix for **{top_row['name']}**")
                if top_row["matched_ingredients"]:
                    compounds_df = pd.DataFrame(top_row["matched_ingredients"])
                    compounds_df.columns = ["Active Ingredient", "Clinical Action / Target Mechanism"]
                    compounds_df["Active Ingredient"] = compounds_df["Active Ingredient"].str.upper()
                    st.dataframe(compounds_df, hide_index=True)
                else:
                    st.info("No primary targeted actives registered for this product.")

                st.markdown("#### 📜 Full Formulation INCI Ingredient List")
                with st.container(border=True):
                    st.code(top_row["ingredients_full"], language="text")

            # -----------------------------------------------------------------
            # TAB 3: SAFETY & ROUTINE TIMELINE
            # -----------------------------------------------------------------
            with tab3:
                st.markdown("### 🛡️ Routine Safety & Conflict Audit")
                if not existing_ingredients_texts:
                    st.info("💡 Tip: Select products you already use in the sidebar under **'Your Current Routine'** to run live chemical conflict scanning.")
                else:
                    if top_conflicts:
                        st.markdown("#### ⚠️ Identified Contraindications")
                        for conf in top_conflicts:
                            st.error(
                                f"**{conf['severity']} Risk:** `{conf['ingredient_a']}` + `{conf['ingredient_b']}` ({conf['conflict_type']})\n\n"
                                f"**Biochemical Reason:** {conf['reason']}\n\n"
                                f"**Clinical Fix:** {conf['solution']}"
                            )
                    else:
                        st.success("✅ **No Documented Conflicts Detected:** Based on our curated rule set, no contraindications were found between this product and your listed routine.")

                st.markdown("---")
                st.markdown("### 📅 Regimen Application Timeline")
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown("#### ☀️ Morning (AM) Sequence")
                        st.markdown(
                            """
                            1. **Cleanse:** Gentle pH-balanced cleanser
                            2. **Tone / Prep:** Hydrating toner or antioxidant mist
                            3. **Treat:** Vitamin C / Hydrating Serums
                            4. **Moisturize:** Lightweight barrier emulsion
                            5. **Protect:** Broad-spectrum SPF 30-50+ (Essential)
                            """
                        )
                with c2:
                    with st.container(border=True):
                        st.markdown("#### 🌙 Evening (PM) Sequence")
                        st.markdown(
                            """
                            1. **Double Cleanse:** Oil/balm followed by water cleanser
                            2. **Exfoliate / Active:** Targeted retinoids or AHA/BHA (alternate nights)
                            3. **Treat:** Peptide & Barrier serums
                            4. **Seal:** Ceramide lipid cream or sleep mask
                            """
                        )

            # -----------------------------------------------------------------
            # TAB 4: CLINICAL CONCIERGE
            # -----------------------------------------------------------------
            with tab4:
                st.markdown(f"### 💬 Consult Concierge about **{top_row['name']}**")
                st.caption("Grounded formulation guidance based on verified dermatology references.")

                product_key = f"{top_row['brand']}::{top_row['name']}"
                if st.session_state.get("chat_product_key") != product_key:
                    st.session_state.chat_product_key = product_key
                    st.session_state.chat_history = []

                # Quick Suggested Prompts
                col_p1, col_p2, col_p3 = st.columns(3)
                if col_p1.button("❓ How do I layer this?"):
                    st.session_state.preset_prompt = f"How should I layer {top_row['name']} in my routine?"
                if col_p2.button("⏱ When will I see results?"):
                    st.session_state.preset_prompt = f"How long does it typically take to see results with {top_row['name']}?"
                if col_p3.button("⚠️ Any purging risk?"):
                    st.session_state.preset_prompt = f"Is there any risk of skin purging with {top_row['name']}?"

                # Render Chat History
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                # Handle User Input
                user_question = st.chat_input("Ask a clinical or application question about this formulation…")
                if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
                    user_question = st.session_state.preset_prompt
                    del st.session_state["preset_prompt"]

                if user_question:
                    st.session_state.chat_history.append({"role": "user", "content": user_question})
                    with st.chat_message("user"):
                        st.write(user_question)

                    with st.spinner("Analyzing formulation chemistry…"):
                        ai_answer = explain.answer_followup(
                            top_row,
                            selected_concerns,
                            skin_type,
                            top_conflicts,
                            st.session_state.chat_history[:-1],
                            user_question,
                        )

                    if ai_answer:
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_answer})
                        with st.chat_message("assistant"):
                            st.write(ai_answer)
                    else:
                        st.warning("⚠️ Clinical concierge consultation unavailable. Please check your configuration.")

else:
    # -------------------------------------------------------------------------
    # WELCOME / EMPTY STATE HERO
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            """
            <div style="text-align: center; padding: 32px 16px;">
                <div style="font-size: 2.8rem; margin-bottom: 8px;">🧬</div>
                <h2 style="font-size: 1.8rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                    Welcome to FormuGraph Intelligence Studio
                </h2>
                <p style="color: #94A3B8; max-width: 620px; margin: 0 auto 20px auto; font-size: 0.95rem; line-height: 1.6;">
                    Select your skin concerns, skin type, and any existing routine products in the sidebar on the left, then click 
                    <strong style="color: #00F29D;">✨ Formulate Regimen</strong> to generate your precision regimen.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Quick Goal Presets
    st.markdown("### ⚡ Clinical Target Profiles")
    st.caption("Explore verified active ingredient strategies:")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("#### 🎯 Acne & Blemish Defense")
            st.caption("Salicylic Acid, Niacinamide & Zinc PCA to clear pore linings and balance sebum.")
    with c2:
        with st.container(border=True):
            st.markdown("#### ✨ Glass Skin & Brightening")
            st.caption("Vitamin C, Tranexamic Acid & Alpha Arbutin to safely fade hyperpigmentation.")
    with c3:
        with st.container(border=True):
            st.markdown("#### 💧 Deep Barrier Repair")
            st.caption("Ceramides, Hyaluronic Acid & Squalane for deep intercellular lipid restoration.")
                        
st.divider()
st.caption(
    "FormuGraph 3.0 — Deterministic ingredient matching and conflict screening based on curated dermatology reference tables "
    "(concern_ingredient_map.csv, conflict_rules.csv, skin_type_fit.csv). Formulations vary by brand; patch test active products before full use."
)