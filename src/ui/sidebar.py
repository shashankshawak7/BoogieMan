"""
Sidebar UI Component for The BoogieMan.

Renders:
1. Primary action: "New Interrogation" button
2. ChatGPT-style flat navigation list of previous interrogations with delete actions
3. Collapsible AI Engine Configuration expander for all local and cloud providers
"""

from __future__ import annotations

from typing import Any, Callable
import streamlit as st

from core.config import DEFAULT_CATALOG, save_config
from core.prober import check_connection_live
from core.storage import delete_chat_session, list_chat_sessions, load_chat_session


def render_sidebar(cfg: dict[str, Any], on_new_interrogation: Callable[[], None]) -> None:
    """Render the entire sidebar UI navigation and engine configuration panel."""
    with st.sidebar:
        # 1. Primary Action: New Interrogation
        if st.button("➕ New Interrogation", type="primary", use_container_width=True, key="sidebar_new_chat"):
            on_new_interrogation()

        # 2. ChatGPT-Style Past Interrogations Flat List
        st.markdown('<div class="sidebar-chat-header">Recent Interrogations</div>', unsafe_allow_html=True)
        saved_sessions = list_chat_sessions()

        if saved_sessions:
            for s in saved_sessions[:20]:
                is_active = (s["id"] == st.session_state.get("current_session_id"))
                title_display = s["title"][:30] + "..." if len(s["title"]) > 30 else s["title"]

                col_sess, col_del = st.columns([5.2, 0.8], vertical_alignment="center")

                with col_sess:
                    prefix = "⚡ " if is_active else "💬 "
                    hover_desc = s.get("preview", "") or s["title"]
                    tooltip_txt = (
                        f"🎯 {s['title']}\n"
                        f"────────────────────────\n"
                        f"{hover_desc}\n\n"
                        f"📊 {s.get('message_count', 0)} messages  |  🕒 {s.get('updated_at', '')[:16].replace('T', ' ')}"
                    )
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(f"{prefix}{title_display}", key=f"btn_sess_{s['id']}", type=btn_type, help=tooltip_txt, use_container_width=True):
                        loaded = load_chat_session(s["id"])
                        if loaded:
                            st.session_state.current_session_id = s["id"]
                            st.session_state.chat_history = loaded.get("messages", [])
                            st.session_state.boogieman_report = loaded.get("boogieman_report", "")
                            st.session_state.boardroom_report = loaded.get("boardroom_report", "")
                            st.session_state.active_mode = loaded.get("active_mode", "boogieman")
                            st.session_state.contract_target_title = loaded.get("title", "")
                            st.rerun()

                with col_del:
                    if st.button("✕", key=f"del_{s['id']}", help="Delete interrogation session"):
                        delete_chat_session(s["id"])
                        if st.session_state.get("current_session_id") == s["id"]:
                            st.session_state.current_session_id = None
                            st.session_state.chat_history = []
                            st.session_state.boogieman_report = ""
                            st.session_state.boardroom_report = ""
                        st.rerun()
        else:
            st.caption("No past interrogations.")

        st.divider()

        # 3. Collapsible Engine Configuration Expander
        with st.expander("⚙️ AI Engine Configuration", expanded=False):
            provider_options = list(DEFAULT_CATALOG.keys())
            saved_active = cfg.get("active_provider", "LM Studio (Local)")
            initial_idx = provider_options.index(saved_active) if saved_active in provider_options else 0

            selected_provider = st.selectbox("Active AI Engine", provider_options, index=initial_idx, key="cfg_engine_select")
            p_data = cfg["providers"].get(selected_provider, DEFAULT_CATALOG[selected_provider])

            if selected_provider in ["LM Studio (Local)", "Ollama (Local)", "Custom OpenAI-Compatible"]:
                p_base = st.text_input("Local Server Base URL", value=p_data.get("base_url") or DEFAULT_CATALOG[selected_provider]["base_url"], key="cfg_base_url")
                p_data["base_url"] = p_base
                p_key = st.text_input("API Key (Optional)", value=p_data.get("api_key", ""), type="password", key="cfg_local_key")
                p_data["api_key"] = p_key
                p_mod = st.text_input("Model ID", value=p_data.get("model", "local-model"), key="cfg_local_mod")
                p_data["model"] = p_mod
            elif selected_provider == "Azure OpenAI":
                p_end = st.text_input("Azure Endpoint URL", value=p_data.get("endpoint", ""), key="cfg_az_end")
                p_data["endpoint"] = p_end
                p_key = st.text_input("Azure API Key", value=p_data.get("api_key", ""), type="password", key="cfg_az_key")
                p_data["api_key"] = p_key
                p_dep = st.text_input("Deployment Name", value=p_data.get("deployment", "gpt-4o"), key="cfg_az_dep")
                p_data["deployment"] = p_dep
                p_ver = st.text_input("API Version", value=p_data.get("api_version", "2024-02-15-preview"), key="cfg_az_ver")
                p_data["api_version"] = p_ver
            elif selected_provider == "Google Gemini":
                p_key = st.text_input("Google AI Studio API Key", value=p_data.get("api_key", ""), type="password", key="cfg_gem_key")
                p_data["api_key"] = p_key
                p_mod = st.text_input("Gemini Model", value=p_data.get("model", "gemini-2.5-flash"), key="cfg_gem_mod")
                p_data["model"] = p_mod
            elif selected_provider in ["OpenAI", "Groq", "Anthropic Claude"]:
                p_key = st.text_input(f"{selected_provider} API Key", value=p_data.get("api_key", ""), type="password", key="cfg_api_key")
                p_data["api_key"] = p_key
                p_mod = st.text_input("Model ID", value=p_data.get("model", DEFAULT_CATALOG[selected_provider]["model"]), key="cfg_api_mod")
                p_data["model"] = p_mod

            col_save, col_test = st.columns([1, 1])
            with col_save:
                if st.button("💾 Lock Engine", use_container_width=True, key="cfg_lock_btn"):
                    cfg["active_provider"] = selected_provider
                    cfg["providers"][selected_provider] = p_data
                    save_config(cfg)
                    st.session_state["probe_cache"] = {}
                    st.success(f"Locked: {selected_provider}")
                    st.rerun()

            with col_test:
                if st.button("🔌 Test Ping", use_container_width=True, key="cfg_test_btn"):
                    with st.spinner("Probing..."):
                        is_ok, msg = check_connection_live(selected_provider, p_data)
                        if is_ok:
                            st.success(msg)
                        else:
                            st.error(msg)

            st.write("")
            cfg["temperature"] = st.slider(
                "Cynicism Temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(cfg.get("temperature", 0.7)),
                step=0.05,
                key="cfg_temp_slider"
            )
