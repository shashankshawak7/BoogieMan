"""
Action Dock UI Component for The BoogieMan.

Renders the bottom executive control panel below the conversation feed:
1. Mode switch buttons (Transmute Boardroom / Switch BoogieMan)
2. Interactive tone dropdown selector
3. Stop / New interrogation button
4. Isolated export downloads toolbar (PDF, Markdown, TXT)
"""

from __future__ import annotations

from typing import Callable
import streamlit as st

from core.storage import save_chat_session
from services.export_service import render_export_toolbar
from services.transmute import build_transmutation_prompt


def render_action_dock(on_new_interrogation: Callable[[], None]) -> None:
    """
    Render the executive command dock and report export toolbar.

    Args:
        on_new_interrogation: Callback function to reset session state for a fresh interrogation.
    """
    current_mode = st.session_state.get("active_mode", "boogieman")
    is_exec = (current_mode == "executive")

    # Determine active report content for document export
    active_report_content = st.session_state.get("boardroom_report" if is_exec else "boogieman_report", "")
    if not active_report_content:
        for m in st.session_state.get("chat_history", []):
            if m.get("role") == "assistant":
                active_report_content = m.get("content", "")
                break

    with st.container(border=True):
        col_transmute, col_tone, col_stop = st.columns([1.8, 1.3, 1.0])

        # 1. Transmute / Mode Toggle Button
        with col_transmute:
            if current_mode == "boogieman":
                if st.button("👔 Transmute Boardroom", use_container_width=True, key="dock_transmute_btn"):
                    with st.spinner("Transmuting conversation into formal C-suite advisory memo..."):
                        try:
                            st.session_state.active_mode = "executive"
                            st.session_state["streaming_transmute"] = build_transmutation_prompt(
                                st.session_state.get("chat_history", [])
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Transmutation failed: {e}")
            else:
                if st.button("👹 Switch BoogieMan", use_container_width=True, key="dock_switch_boogie_btn"):
                    st.session_state.active_mode = "boogieman"
                    _save_current_session()
                    st.rerun()

        # 2. Tone Selector Dropdown
        with col_tone:
            current_idx = 0 if current_mode == "boogieman" else 1
            tone_choice = st.selectbox(
                "Tone",
                ["👹 BoogieMan", "👔 Boardroom"],
                index=current_idx,
                label_visibility="collapsed",
                key="dock_tone_choice"
            )
            new_mode = "boogieman" if "BoogieMan" in tone_choice else "executive"
            if new_mode != current_mode:
                st.session_state.active_mode = new_mode
                if new_mode == "executive" and not st.session_state.get("boardroom_report"):
                    st.session_state["streaming_transmute"] = build_transmutation_prompt(
                        st.session_state.get("chat_history", [])
                    )
                else:
                    _save_current_session()
                st.rerun()

        # 3. Halt / New Interrogation Button
        with col_stop:
            if st.button("🛑 Stop / New", use_container_width=True, key="dock_stop_btn", help="Halt and start fresh interrogation"):
                on_new_interrogation()

        # 4. Isolated Report Export Downloads Toolbar
        render_export_toolbar(
            chat_history=st.session_state.get("chat_history", []),
            active_report_content=active_report_content,
            is_exec=is_exec,
            session_id=st.session_state.get("current_session_id")
        )


def _save_current_session() -> None:
    """Save active session state to disk if a session ID exists."""
    sess_id = st.session_state.get("current_session_id")
    if sess_id:
        save_chat_session({
            "id": sess_id,
            "title": st.session_state.get("contract_target_title", "Untitled Interrogation"),
            "active_mode": st.session_state.get("active_mode", "boogieman"),
            "boogieman_report": st.session_state.get("boogieman_report", ""),
            "boardroom_report": st.session_state.get("boardroom_report", ""),
            "messages": st.session_state.get("chat_history", [])
        })
