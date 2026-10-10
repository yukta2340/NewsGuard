# app.py
"""
NewsGuard - Autonomous News Credibility & Verification Application.
Orchestrates backend ML/evidence engines with the frontend UI design system.
Linked with NDTV Latest (https://www.ndtv.com/latest) and accredited press wires.
Fully optimized for Streamlit Cloud deployment and local execution.
"""

import sys
import os
import streamlit as st

# Ensure repository root is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import isolated backend services
from backend.ml_engine import MLEngine
from backend.evidence_engine import (
    fetch_live_press_feed,
    fetch_ndtv_latest_feed,
    search_journalistic_evidence,
    compute_hybrid_credibility
)

# Import isolated frontend presentation components
from frontend.ui_components import (
    inject_assets,
    render_header,
    render_verdict_card,
    render_evidence_list
)

# --- 1. Streamlit App Configuration ---
st.set_page_config(
    page_title="NewsGuard - News Credibility Verification Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Inject Frontend Stylesheet & JavaScript ---
inject_assets()

# --- 3. Initialize Backend Services ---
@st.cache_resource
def get_ml_engine():
    return MLEngine()

ml_engine = get_ml_engine()

# Cached live feeds
@st.cache_data(ttl=120)
def get_cached_press_feed(category: str):
    return fetch_live_press_feed(category=category, max_items=15)


# --- 4. Render Application Header ---
render_header()


# --- 5. Application Tabs ---
tab_verify, tab_feed = st.tabs([
    "🔍 Verify News",
    "📰 Live News Feed (NDTV & National)"
])


# =========================================================================
# TAB 1: VERIFY NEWS (DIRECT REAL / FAKE OUTPUT WITH EVIDENCE)
# =========================================================================
with tab_verify:
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 16px;'>Enter any news headline, article, or claim below to check whether it is <b>REAL</b> or <b>FAKE</b> with journalistic evidence.</p>", unsafe_allow_html=True)

    if 'news_verifier_input' not in st.session_state:
        st.session_state['news_verifier_input'] = ""

    col_input, col_examples = st.columns([3, 1])

    with col_input:
        news_input = st.text_area(
            "News content to analyze:",
            placeholder="Paste news headline or claim here (politics, general, sports, world, science)...",
            height=150,
            key="news_verifier_input",
            label_visibility="collapsed"
        )

    with col_examples:
        st.markdown("<div style='font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; color: #64748b; font-weight: 700; margin-bottom: 8px;'>Try Examples</div>", unsafe_allow_html=True)
        if st.button("🌐 NDTV General / World News", use_container_width=True):
            st.session_state['news_verifier_input'] = "Over 8 Lakh Left Without Power In 3 States As Hurricane Makes Landfall In US"
            st.rerun()

        if st.button("🏛️ National Policy News", use_container_width=True):
            st.session_state['news_verifier_input'] = "Prime Minister announces new solar energy project in Gujarat to boost green power infrastructure."
            st.rerun()

        if st.button("🚨 Fabricated Hoax", use_container_width=True):
            st.session_state['news_verifier_input'] = "BREAKING: Scientists invent pills that permanently eliminate sleep, government mandates usage nationwide!"
            st.rerun()

        if st.session_state.get('news_verifier_input') and st.button("🧹 Clear Input", use_container_width=True):
            st.session_state['news_verifier_input'] = ""
            st.rerun()

    col_action, col_toggle = st.columns([1, 2])
    with col_action:
        analyze_clicked = st.button("Verify News", type="primary", use_container_width=True)
    with col_toggle:
        live_corroboration = st.checkbox("Check live news databases & NDTV for proof", value=True)

    if analyze_clicked:
        claim_text = st.session_state.get('news_verifier_input', '').strip()

        if not claim_text:
            st.warning("Please enter a headline or article text to evaluate.")
        else:
            with st.spinner("Checking claim authenticity against NDTV and journalistic databases..."):
                # 1. Backend ML Analysis
                ml_result = ml_engine.analyze_style(claim_text)

                # 2. Backend Live Evidence Search (NDTV + Wires)
                evidence_result = {
                    'evidence_found': False,
                    'confidence': 'NONE',
                    'search_query': '',
                    'articles': [],
                    'summary': 'Live news verification was skipped.'
                }
                if live_corroboration:
                    evidence_result = search_journalistic_evidence(claim_text, max_results=5)

                # 3. Backend Credibility Synthesis
                hybrid_result = compute_hybrid_credibility(ml_result['prediction'], evidence_result)

                # 4. Display Clear Output: REAL or FAKE
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                render_verdict_card(hybrid_result)

                # 5. Display Evidence Directly Below
                st.markdown("### 📰 Journalistic Evidence & Sources")
                render_evidence_list(evidence_result['articles'], evidence_result['summary'])


# =========================================================================
# TAB 2: LIVE NEWS FEED (NDTV LATEST & ACCREDITED WIRES)
# =========================================================================
with tab_feed:
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 14px;'>Live feed of latest news across all categories: national, world, sports, science, and governance.</p>", unsafe_allow_html=True)

    col_cat, col_refresh = st.columns([3, 1])
    with col_cat:
        feed_category = st.radio(
            "Feed Selection",
            options=[
                "🌐 NDTV Latest (National, World, Sports & General)",
                "🏛️ Politics & Governance",
                "⚡ Top National Headlines"
            ],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col_refresh:
        if st.button("🔄 Refresh Feed", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if "NDTV" in feed_category:
        cat_key = "ndtv"
    elif "Politics" in feed_category:
        cat_key = "politics"
    else:
        cat_key = "top"

    feed_data = get_cached_press_feed(cat_key)

    if not feed_data:
        st.markdown("""
        <div class="glass-card" style="text-align: center; color: #64748b; padding: 28px;">
            Unable to reach news services. Check network connection.
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, item in enumerate(feed_data):
            c_card, c_btn = st.columns([4, 1])
            with c_card:
                pub_date = item.get('pub_date', '')[:22] if item.get('pub_date') else 'Recent'
                st.markdown(f"""
                <div class="feed-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="feed-source-badge">{item['source']}</span>
                        <span class="feed-timestamp">{pub_date}</span>
                    </div>
                    <div class="feed-article-title">{item['title']}</div>
                    <div>
                        <a href="{item['link']}" target="_blank" class="feed-link">
                            Read Original Article &rarr;
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_btn:
                if st.button("🔍 Check Story", key=f"feed_verify_{idx}", use_container_width=True):
                    st.session_state['news_verifier_input'] = item['title']
                    st.rerun()


# --- Standalone Execution Fallback ---
if __name__ == "__main__":
    import subprocess
    cmd = [sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)]
    subprocess.run(cmd)
