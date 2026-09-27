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

from core.config import DEFAULT_CATALOG, ROASTS_DIR, save_config
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
                    st.session_state["engine_feedback"] = ("success", f"Locked: {selected_provider}")
                    st.toast(f"Engine locked: {selected_provider}", icon="💾")
                    st.rerun()

            with col_test:
                if st.button("🔌 Test Ping", use_container_width=True, key="cfg_test_btn"):
                    with st.spinner("Probing..."):
                        is_ok, msg = check_connection_live(selected_provider, p_data)
                        st.session_state["engine_feedback"] = ("success" if is_ok else "error", msg)
                        if is_ok:
                            st.toast(f"Live & Connected: {msg}", icon="🟢")
                        else:
                            st.toast(f"Connection error: {msg}", icon="🔴")

            # Clean full-width status pill below both buttons (never misaligns button row)
            if "engine_feedback" in st.session_state:
                fb_type, fb_msg = st.session_state["engine_feedback"]
                bg_color = "rgba(34, 197, 94, 0.12)" if fb_type == "success" else "rgba(239, 68, 68, 0.12)"
                border_color = "rgba(34, 197, 94, 0.35)" if fb_type == "success" else "rgba(239, 68, 68, 0.35)"
                text_color = "#4ade80" if fb_type == "success" else "#f87171"
                icon = "●" if fb_type == "success" else "○"
                st.markdown(
                    f'<div style="margin-top: 8px; margin-bottom: 4px; padding: 6px 10px; border-radius: 6px; font-size: 0.76rem; background: {bg_color}; border: 1px solid {border_color}; color: {text_color}; text-align: center; font-weight: 500;">{icon} {fb_msg}</div>',
                    unsafe_allow_html=True
                )

            st.write("")
            cfg["temperature"] = st.slider(
                "Cynicism Temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(cfg.get("temperature", 0.7)),
                step=0.05,
                key="cfg_temp_slider"
            )

        # 4. Executed Records & Past Transcripts Section (Uncollapsed & Unmissable)
        st.divider()
        st.markdown('<div class="sidebar-chat-header">📁 Executed Records & Transcripts</div>', unsafe_allow_html=True)

        # Quick download for active chat session
        active_chat = st.session_state.get("chat_history", [])
        if active_chat:
            transcript_text = f"# Interrogation Transcript: {st.session_state.get('contract_target_title', 'Session')}\n\n"
            for m in active_chat:
                speaker = "Pitcher" if m.get("role") == "user" else ("Executive Advisor" if m.get("mode") == "executive" else "BoogieMan")
                transcript_text += f"### {speaker}:\n{m.get('content', '')}\n\n---\n\n"
            st.download_button(
                label="⬇️ Download Active Transcript (.md)",
                data=transcript_text.encode("utf-8"),
                file_name=f"active_transcript_{st.session_state.get('current_session_id', 'live')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="sidebar_dl_active_transcript"
            )

        roast_files = sorted(ROASTS_DIR.glob("*.md"), reverse=True)
        if roast_files:
            st.caption("Saved Historical Transcripts:")
            sel_file = st.selectbox("Select Past Record", [f.name for f in roast_files], key="cfg_sel_record")
            if sel_file:
                record_bytes = (ROASTS_DIR / sel_file).read_bytes()
                st.download_button(
                    label="⬇️ Download Saved Record (.md)",
                    data=record_bytes,
                    file_name=sel_file,
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"cfg_dl_rec_{sel_file}"
                )
        else:
            st.caption("No historical records yet.")

        # Footer Attribution
        st.markdown(
            """
            <div style="margin-top: 28px; padding: 12px 14px; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; background: rgba(15, 23, 42, 0.6); text-align: center; font-size: 0.74rem; color: #94a3b8;">
                <div style="color: #f1f5f9; font-weight: 600;">Shashank Shawak</div>
                <div style="color: #38bdf8; font-size: 0.72rem; margin-bottom: 4px;">Consultant Architect</div>
                <a href="https://www.linkedin.com/in/shashankshawak/" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">LinkedIn</a> &bull; 
                <a href="mailto:shashankshawak7@gmail.com" style="color: #cbd5e1; text-decoration: none;">shashankshawak7@gmail.com</a>
            </div>
            """,
            unsafe_allow_html=True
        )

