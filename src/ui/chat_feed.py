"""
Chat Feed & Streaming Assistant Component for The BoogieMan.

Renders:
1. Message history feed with role-based avatars (User, BoogieMan, Executive Advisor).
2. Live token streaming for initial target evaluations, follow-up interrogations, and boardroom transmutations.
3. Interactive mid-stream interruption buttons (Stop Generation).
4. Automatic session persistence to disk upon stream completion.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
import streamlit as st

from core.config import ROASTS_DIR, get_persona
from core.llm import stream_llm
from core.storage import save_chat_session
from services.transmute import get_boardroom_system_prompt


def render_chat_feed(
    feed_container: Any,
    active_provider: str,
    active_provider_data: dict[str, Any],
    temperature: float = 0.7
) -> None:
    """
    Render past conversation history and handle any active streaming tasks
    (initial evaluation, follow-up questions, or boardroom transmutation).

    Args:
        feed_container: Streamlit container dedicated to the message feed.
        active_provider: Name of the active AI engine (e.g. 'LM Studio (Local)').
        active_provider_data: Provider configuration dictionary.
        temperature: Sampling temperature for generation.
    """
    with feed_container:
        # 1. Render all existing messages in session history
        for msg in st.session_state.chat_history:
            role = msg.get("role", "user")
            is_msg_exec = (
                msg.get("mode") == "executive"
                or "EXECUTIVE" in msg.get("content", "")[:70]
                or "BOARDROOM" in msg.get("content", "")[:70]
            )
            avatar = "🧑‍💻" if role == "user" else ("👔" if is_msg_exec else "👹")
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg.get("content", ""))

        # 2. Live streaming: Follow-up user interrogation
        if "streaming_followup" in st.session_state:
            q_follow = st.session_state.pop("streaming_followup")
            is_active_exec = st.session_state.get("active_mode") == "executive"

            followup_persona = get_persona()
            if is_active_exec:
                followup_persona += (
                    "\n\nMaintain the persona of an elite executive strategy consultant. "
                    "Provide data-grounded, pragmatic corporate advice."
                )
            else:
                followup_persona += (
                    "\n\n## INTERACTIVE CHAT MODE DIRECTIVE:\n"
                    "You are in active conversation with the user. "
                    "DO NOT output the 6-part review template. "
                    "Speak directly, conversationally, and bitingly as The BoogieMan. "
                    "Use your signature cynical caveman cadence, dissect the user's specific words and buzzwords "
                    "with parenthetical reality checks, drop devastating punchlines, and offer the 50-line stone tool alternative, "
                    "matching the exact wit and rhythm of Scenarios 1, 2, 3, and 4 in your prompt."
                )

            with st.chat_message("assistant", avatar="👔" if is_active_exec else "👹"):
                col_text, col_stop = st.columns([8, 1])
                with col_stop:
                    stop_follow = st.button(
                        "🛑 Stop",
                        key="btn_stop_live_follow",
                        help="Halt streaming generation immediately",
                        use_container_width=True
                    )
                with col_text:
                    if stop_follow:
                        bot_reply = "*(Response halted by user.)*"
                        st.warning(bot_reply)
                    else:
                        stream = stream_llm(
                            system_prompt=followup_persona,
                            user_prompt=q_follow,
                            provider=active_provider,
                            p_cfg=active_provider_data,
                            temp=temperature,
                            chat_history=[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.chat_history[:-1]
                            ]
                        )
                        bot_reply = st.write_stream(stream)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": bot_reply,
                "mode": "executive" if is_active_exec else "boogieman"
            })

            _persist_active_session()
            st.rerun()

        # 3. Live streaming: Boardroom Transmutation
        if "streaming_transmute" in st.session_state:
            t_prompt = st.session_state.pop("streaming_transmute")
            st.session_state.active_mode = "executive"
            system_prompt = get_boardroom_system_prompt()

            with st.chat_message("assistant", avatar="👔"):
                col_text, col_stop = st.columns([8, 1])
                with col_stop:
                    stop_transmute = st.button(
                        "🛑 Stop",
                        key="btn_stop_live_transmute",
                        help="Halt transmutation immediately",
                        use_container_width=True
                    )
                with col_text:
                    if stop_transmute:
                        bot_reply = "*(Transmutation halted by user.)*"
                        st.warning(bot_reply)
                    else:
                        stream = stream_llm(
                            system_prompt=system_prompt,
                            user_prompt=t_prompt,
                            provider=active_provider,
                            p_cfg=active_provider_data,
                            temp=0.2
                        )
                        bot_reply = st.write_stream(stream)

            st.session_state.boardroom_report = bot_reply
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"### 💼 EXECUTIVE ARCHITECTURAL MEMORANDUM (BOARDROOM TRANSMUTATION)\n\n{bot_reply}",
                "mode": "executive"
            })

            _persist_active_session()
            st.rerun()

        # 4. Live streaming: Initial contract autopsy
        if "streaming_target" in st.session_state:
            target_raw = st.session_state.pop("streaming_target")
            tone_raw = st.session_state.pop("streaming_tone", "👹 The BoogieMan (Brutally Satirical & Folkloric)")
            is_exec_mode = "Executive Advisory Audit" in tone_raw

            persona_text = get_persona()
            if is_exec_mode:
                persona_text += (
                    "\n\n## SPECIAL OVERRIDE: EXECUTIVE BRIEFING MODE\n"
                    "Deliver the verdict as a polished, diplomatic, yet ruthlessly analytical Executive Advisory Memo "
                    "for the Board of Directors and C-suite. Frame critiques through Capital Efficiency, "
                    "Technical Debt Amortization, Operational Risk, and Time-to-Market. "
                    "Retain all architectural eliminations and the 6-part review structure, but use boardroom-appropriate language."
                )
            else:
                persona_text += (
                    "\n\n## MANDATORY AUTOPSY REQUIREMENT:\n"
                    "Open with your signature biting BoogieMan Opening Roast & Buzzword Translation, dissecting the proposal "
                    "with cynical caveman wit, vivid absurd metaphors, and devastating punchlines matching the Golden Scenarios. "
                    "Then populate the 6 sections of the Mandatory Review Template, ensuring EVERY single section is saturated with "
                    "your sharp, cynical caveman-architect voice, hilarious technical comparisons, and ruthless pragmatism. "
                    "Zero dry corporate bullet points."
                )

            with st.chat_message("assistant", avatar="👔" if is_exec_mode else "👹"):
                col_text, col_stop = st.columns([8, 1])
                with col_stop:
                    stop_initial = st.button(
                        "🛑 Stop",
                        key="btn_stop_live_initial",
                        help="Halt evaluation immediately",
                        use_container_width=True
                    )
                with col_text:
                    if stop_initial:
                        full_reply = "*(Evaluation halted by user.)*"
                        st.warning(full_reply)
                    else:
                        stream = stream_llm(
                            system_prompt=persona_text,
                            user_prompt=target_raw,
                            provider=active_provider,
                            p_cfg=active_provider_data,
                            temp=temperature
                        )
                        full_reply = st.write_stream(stream)

            if is_exec_mode:
                st.session_state.boardroom_report = full_reply
            else:
                st.session_state.boogieman_report = full_reply

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_reply,
                "mode": "executive" if is_exec_mode else "boogieman"
            })

            new_id = save_chat_session({
                "title": st.session_state.get("contract_target_title", "Untitled Interrogation"),
                "active_mode": st.session_state.get("active_mode", "boogieman"),
                "boogieman_report": st.session_state.get("boogieman_report", ""),
                "boardroom_report": st.session_state.get("boardroom_report", ""),
                "messages": st.session_state.chat_history
            })
            st.session_state.current_session_id = new_id

            # Save timestamped backup record in roasts/ directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            record_path = ROASTS_DIR / f"verdict_{timestamp}.md"
            try:
                record_path.write_text(
                    f"# BoogieMan Architectural Autopsy\n\n"
                    f"**Date:** {datetime.now()}\n"
                    f"**Engine:** {active_provider}\n"
                    f"**Tone:** {tone_raw}\n\n"
                    f"## Target\n{target_raw}\n\n"
                    f"## Verdict\n{full_reply}\n",
                    encoding="utf-8"
                )
            except Exception:
                pass

            st.rerun()


def _persist_active_session() -> None:
    """Save the current active session state to disk if a session ID exists."""
    sess_id = st.session_state.get("current_session_id")
    if sess_id:
        save_chat_session({
            "id": sess_id,
            "title": st.session_state.get("contract_target_title", "Untitled Interrogation"),
            "active_mode": st.session_state.get("active_mode", "boogieman"),
            "boogieman_report": st.session_state.get("boogieman_report", ""),
            "boardroom_report": st.session_state.get("boardroom_report", ""),
            "messages": st.session_state.chat_history
        })
