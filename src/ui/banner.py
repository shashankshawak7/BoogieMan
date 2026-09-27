"""
Header Banner UI Component for The BoogieMan.

Renders the top sticky header banner displaying:
- The BoogieMan crest, title, and tagline
- Real-time AI engine connection status badge (LIVE / OFFLINE)
- Active model identifier pill
"""

from __future__ import annotations

import streamlit as st


def render_banner(active_provider: str, model_name: str, is_live: bool, status_desc: str) -> None:
    """
    Render the sticky header banner containing system branding and live connectivity badges.

    Args:
        active_provider: Name of the currently selected AI provider.
        model_name: Active model ID or deployment name.
        is_live: Boolean indicating whether the provider is currently reachable.
        status_desc: Brief description of connection status or error message.
    """
    if is_live:
        status_dot = '<span class="status-dot dot-live"></span>'
        badge_html = (
            f'<div class="banner-status-row">'
            f'<span class="banner-engine-badge live">{status_dot}{active_provider}</span>'
            f'<span class="banner-model-badge">⚡ {model_name}</span>'
            f'</div>'
        )
    else:
        status_dot = '<span class="status-dot dot-off"></span>'
        badge_html = (
            f'<div class="banner-status-row">'
            f'<span class="banner-engine-badge off">{status_dot}{active_provider}</span>'
            f'<span class="banner-model-badge">⚠️ {status_desc}</span>'
            f'</div>'
        )

    banner_html = (
        '<div class="boogieman-banner">'
        '<div class="banner-top-row">'
        '<span class="boogieman-crest">👹 ARCHITECTURAL TRIBUNAL</span>'
        '<span class="boogieman-author">BY SHASHANK SHAWAK</span>'
        '</div>'
        '<div class="banner-main-row">'
        '<h1 class="boogieman-title">THE BOOGIEMAN</h1>'
        f'{badge_html}'
        '</div>'
        '<p class="boogieman-tagline">Ruthlessly dismantling bloated architectures, premature abstractions, and buzzword traps.</p>'
        '</div>'
    )
    st.html(banner_html)
