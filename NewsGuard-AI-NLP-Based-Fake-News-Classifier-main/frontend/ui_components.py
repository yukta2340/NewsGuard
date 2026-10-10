# frontend/ui_components.py
"""
UI Components and Asset Injector for NewsGuard.
Renders clean, direct output (REAL or FAKE) with evidence sources.
Completely removes any possibility of raw code/indented blocks showing up.
"""

import os
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(CURRENT_DIR, 'styles.css')
JS_PATH = os.path.join(CURRENT_DIR, 'app_script.js')


def inject_assets():
    """Injects custom CSS and JavaScript into the Streamlit session."""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    if os.path.exists(JS_PATH):
        with open(JS_PATH, 'r', encoding='utf-8') as f:
            js_content = f.read()
        st.markdown(f"<script>{js_content}</script>", unsafe_allow_html=True)


def render_header():
    """Renders the top application header."""
    html_header = (
        '<div class="app-header">'
        '<div>'
        '<h1 class="brand-title">'
        '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="m9 12 2 2 4-4"/>'
        '</svg>'
        'NewsGuard'
        '</h1>'
        '<p class="brand-desc">Instant Fake News Detection with Journalistic Evidence</p>'
        '</div>'
        '<div>'
        '<div class="system-status">'
        '<div class="status-dot"></div>'
        'Active'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html_header, unsafe_allow_html=True)


def render_verdict_card(hybrid: dict):
    """
    Renders direct, bold REAL or FAKE banner without any code or markdown bugs.
    """
    status = hybrid.get('status', 'REAL')
    score = hybrid.get('score_percent', 90)
    detail = hybrid.get('detail', '')

    if status == 'REAL':
        badge_text = "VERIFIED AUTHENTIC"
        theme_class = "verdict-banner-emerald"
        pill_class = "pill-emerald"
        main_title = "✅ REAL NEWS"
        accent_color = "#10b981"
        bar_gradient = "linear-gradient(90deg, #059669, #10b981)"
    elif status == 'FAKE':
        badge_text = "MISINFORMATION DETECTED"
        theme_class = "verdict-banner-rose"
        pill_class = "pill-rose"
        main_title = "🚨 FAKE NEWS"
        accent_color = "#f43f5e"
        bar_gradient = "linear-gradient(90deg, #be123c, #f43f5e)"
    else:
        badge_text = "UNVERIFIED"
        theme_class = "verdict-banner-amber"
        pill_class = "pill-amber"
        main_title = "⚠️ UNVERIFIED CLAIM"
        accent_color = "#f59e0b"
        bar_gradient = "linear-gradient(90deg, #b45309, #f59e0b)"

    # Clean single-line HTML string to avoid any Markdown indentation bugs
    card_html = (
        f'<div class="verdict-banner {theme_class}" style="margin: 18px 0; padding: 24px 28px; border-radius: 14px;">'
        f'<span class="verdict-pill {pill_class}">{badge_text}</span>'
        f'<h1 style="font-size: 2.2rem; font-weight: 800; margin: 4px 0 10px 0; color: #ffffff; letter-spacing: -0.02em;">{main_title}</h1>'
        f'<p style="font-size: 1.05rem; color: #cbd5e1; margin: 0 0 16px 0; line-height: 1.5;">{detail}</p>'
        f'<div style="background: rgba(15, 23, 42, 0.6); padding: 14px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">'
        f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">'
        f'<span>Credibility Rating</span><span style="color: {accent_color}; font-weight: 700;">{score}%</span>'
        f'</div>'
        f'<div style="width: 100%; height: 8px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">'
        f'<div style="width: {score}%; height: 100%; background: {bar_gradient}; border-radius: 9999px;"></div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_evidence_list(articles: list, summary_text: str):
    """Renders news evidence cards with direct links and publishers."""
    st.markdown(f"<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 14px; font-weight: 500;'>{summary_text}</p>", unsafe_allow_html=True)

    if not articles:
        no_evidence_html = (
            '<div class="glass-card" style="border: 1px dashed rgba(255,255,255,0.12); text-align: center; color: #94a3b8; padding: 24px; border-radius: 12px;">'
            '🔍 No corroborating articles found across accredited news agencies.'
            '</div>'
        )
        st.markdown(no_evidence_html, unsafe_allow_html=True)
        return

    for art in articles:
        date_str = art.get('pub_date', '')[:16] if art.get('pub_date') else 'Recent'
        source_name = art.get('source', 'News Source')
        title_text = art.get('title', '')
        link_url = art.get('link', '#')

        item_html = (
            f'<div class="glass-card" style="padding: 16px 20px; margin-bottom: 12px; border-radius: 12px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
            f'<span class="feed-source-badge">📰 {source_name}</span>'
            f'<span class="feed-timestamp">🕒 {date_str}</span>'
            f'</div>'
            f'<div style="font-weight: 600; font-size: 1.05rem; margin: 6px 0 8px 0;">'
            f'<a href="{link_url}" target="_blank" style="color: #60A5FA; text-decoration: none;">'
            f'{title_text} &rarr;'
            f'</a>'
            f'</div>'
            f'</div>'
        )
        st.markdown(item_html, unsafe_allow_html=True)
