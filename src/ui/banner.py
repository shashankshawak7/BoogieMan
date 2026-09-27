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
        badge_html = (
            f'<span class="badge-pill badge-live">● {active_provider} LIVE</span> '
            f'<span class="badge-pill badge-tech">⚡ {model_name}</span>'
        )
    else:
        badge_html = (
            f'<span class="badge-pill badge-unreachable">○ {active_provider} OFFLINE</span> '
            f'<span class="badge-pill badge-tech">⚠️ {status_desc}</span>'
        )

    banner_html = (
        '<div class="boogieman-banner">'
        '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">'
        '<div>'
        '<div class="boogieman-crest">👹 ARCHITECTURAL TRIBUNAL &bull; TECH DEBT REAPER</div>'
        '<h1 class="boogieman-title">THE BOOGIEMAN</h1>'
        '<p class="boogieman-tagline">"Ruthlessly dismantling bloated architectures, premature abstractions, and buzzword traps."</p>'
        '</div>'
        f'<div style="display: flex; align-items: center; gap: 8px;">{badge_html}</div>'
        '</div>'
        '</div>'
    )
    st.html(banner_html)
