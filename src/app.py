"""
The BoogieMan — Main Streamlit Application Orchestrator.

High-level application coordinator that connects:
- System configuration and session state initialization
- Custom CSS stylesheet injection
- ChatGPT-style sidebar navigation and provider settings (ui_sidebar)
- Branded header banner with real-time status indicators (ui_banner)
- Initial target contract submission form (ui_contract_form)
- Interactive conversation feed with live streaming assistant (ui_chat_feed)
- Executive command dock and report export toolbar (ui_action_dock)
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# Windows UTF-8 console encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure src/ and project root are in sys.path
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Backend core & services
from core.config import DEFAULT_CATALOG, load_config
from core.prober import get_cached_live_status
from services.transmute import build_transmutation_prompt

# UI components
from ui.action_dock import render_action_dock
from ui.banner import render_banner
from ui.chat_feed import render_chat_feed
from ui.contract_form import render_contract_form
from ui.sidebar import render_sidebar

# -----------------------------------------------------------------------------
# Page Configuration & Stylesheet Injection
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="The BoogieMan — Tech Debt Reaper",
    page_icon="👹",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_file = PROJECT_ROOT / "css" / "style.css"
if not css_file.exists():
    css_file = PROJECT_ROOT / "css" / "styles.css"

if css_file.exists():
    st.html(f"<style>\n{css_file.read_text(encoding='utf-8')}\n</style>")

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "config" not in st.session_state:
    st.session_state.config = load_config()
if "probe_cache" not in st.session_state:
    st.session_state.probe_cache = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_mode" not in st.session_state:
    st.session_state.active_mode = "boogieman"
if "boogieman_report" not in st.session_state:
    st.session_state.boogieman_report = ""
if "boardroom_report" not in st.session_state:
    st.session_state.boardroom_report = ""
if "contract_target_title" not in st.session_state:
    st.session_state.contract_target_title = ""

cfg = st.session_state.config


def start_new_interrogation() -> None:
    """Reset session state to start a clean interrogation session."""
    st.session_state.current_session_id = None
    st.session_state.chat_history = []
    st.session_state.boogieman_report = ""
    st.session_state.boardroom_report = ""
    st.session_state.active_mode = "boogieman"
    st.session_state.contract_target_title = ""
    st.session_state.pop("pending_submission", None)
    st.session_state.pop("streaming_target", None)
    st.session_state.pop("streaming_tone", None)
    st.session_state.pop("streaming_followup", None)
    st.session_state.pop("streaming_transmute", None)
    for k in ["init_pitch_txt", "init_rfp_txt", "init_rd_txt", "init_ba_txt", "active_diff", "init_pr_url"]:
        st.session_state.pop(k, None)
    st.rerun()


# -----------------------------------------------------------------------------
# 1. Sidebar Navigation & Provider Settings
# -----------------------------------------------------------------------------
render_sidebar(cfg=cfg, on_new_interrogation=start_new_interrogation)

# -----------------------------------------------------------------------------
# 2. Provider Connectivity & Top Banner
# -----------------------------------------------------------------------------
active_p = cfg.get("active_provider", "LM Studio (Local)")
active_p_data = cfg.get("providers", {}).get(active_p, DEFAULT_CATALOG.get(active_p, {}))
is_live, status_desc = get_cached_live_status(
    cache_store=st.session_state.probe_cache,
    provider_name=active_p,
    provider_data=active_p_data
)
model_name = active_p_data.get("model") or active_p_data.get("deployment") or "default"

render_banner(
    active_provider=active_p,
    model_name=model_name,
    is_live=is_live,
    status_desc=status_desc
)

# -----------------------------------------------------------------------------
# 3. Main Workspace: Contract Intake or Active Chat Feed
# -----------------------------------------------------------------------------
form_slot = st.empty()

if not st.session_state.chat_history:
    # State A: Intake form for new contracts
    with form_slot.container():
        render_contract_form(
            is_live=is_live,
            active_p=active_p,
            status_desc=status_desc
        )
else:
    # State B: Active interrogation session
    form_slot.empty()

    # Active session sub-bar
    col_title, col_new = st.columns([4, 1.2])
    with col_title:
        st.caption(f"🎯 **Interrogation:** {st.session_state.get('contract_target_title', 'Architecture Review')}")
    with col_new:
        if st.button("➕ New Chat", use_container_width=True, key="top_active_new_chat"):
            start_new_interrogation()

    # Dedicated message feed container
    feed_container = st.container()
    render_chat_feed(
        feed_container=feed_container,
        active_provider=active_p,
        active_provider_data=active_p_data,
        temperature=float(cfg.get("temperature", 0.7))
    )

    # Executive action dock & export toolbar
    render_action_dock(on_new_interrogation=start_new_interrogation)

    # User follow-up input
    user_query = st.chat_input("Ask how to simplify this, probe trade-offs, or demand alternative designs...")
    if user_query:
        query_lower = user_query.lower().strip()
        transmute_keywords = [
            "transmute", "boardroom", "executive report", "c-suite",
            "formal report", "convert to boardroom", "transmute to boardroom",
            "executive summary", "recommendation report", "convert roast", "convert to professional"
        ]
        is_transmute_cmd = any(k in query_lower for k in transmute_keywords)

        st.session_state.chat_history.append({"role": "user", "content": user_query})
        if is_transmute_cmd:
            st.session_state.active_mode = "executive"
            st.session_state["streaming_transmute"] = build_transmutation_prompt(st.session_state.chat_history)
        else:
            st.session_state["streaming_followup"] = user_query
        st.rerun()
