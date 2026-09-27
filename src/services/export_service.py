"""
Export Service Module for The BoogieMan.

Isolates report generation (PDF, Markdown, TXT) and export downloads.
Uses @st.fragment to isolate download interactions from full page reruns.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
import streamlit as st

from core.config import STATIC_DIR
from services.pdf_generator import generate_pdf_report


def build_export_payload(
    chat_history: list[dict[str, Any]],
    active_report_content: str,
    is_exec: bool,
    session_id: str | None
) -> dict[str, Any]:
    """Builds formatted transcript, names, and generates PDF / MD / TXT bytes."""
    if len(chat_history) > 2:
        qa_transcript = "\n\n---\n## Architectural Deliberations & Q&A Transcript\n\n"
        for m in chat_history[2:]:
            speaker = (
                "**PITCHER:** " if m.get("role") == "user"
                else ("**EXECUTIVE ADVISOR:** " if is_exec else "**BOOGIEMAN:** ")
            )
            qa_transcript += f"{speaker}\n{m.get('content', '')}\n\n"
        export_body = (active_report_content or "") + qa_transcript
    else:
        export_body = active_report_content or ""

    doc_title = "Executive Architectural Memorandum" if is_exec else "The BoogieMan Architectural Autopsy"
    file_prefix = "boardroom_report" if is_exec else "boogieman_autopsy"

    file_id_str = f"_{session_id}" if session_id else f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dl_pdf_name = f"{file_prefix}{file_id_str}.pdf"
    dl_md_name = f"{file_prefix}{file_id_str}.md"
    dl_txt_name = f"{file_prefix}{file_id_str}.txt"

    # PDF bytes generation with session caching
    cache_key = f"_pdf_cache_{session_id}_{is_exec}_{hash(export_body)}"
    if cache_key in st.session_state:
        pdf_bytes = st.session_state[cache_key]
    else:
        try:
            pdf_bytes = generate_pdf_report(
                title=doc_title,
                markdown_content=export_body or "No report content generated.",
                is_executive=is_exec
            )
        except Exception as e:
            pdf_bytes = f"Error generating PDF: {e}".encode("utf-8")
        st.session_state[cache_key] = pdf_bytes

    md_bytes = export_body.encode("utf-8")
    txt_bytes = export_body.encode("utf-8")

    # Persist directly into static/ directory
    try:
        (STATIC_DIR / dl_pdf_name).write_bytes(pdf_bytes)
        (STATIC_DIR / dl_md_name).write_bytes(md_bytes)
        (STATIC_DIR / dl_txt_name).write_bytes(txt_bytes)
    except Exception:
        pass

    return {
        "pdf_bytes": pdf_bytes,
        "md_bytes": md_bytes,
        "txt_bytes": txt_bytes,
        "pdf_name": dl_pdf_name,
        "md_name": dl_md_name,
        "txt_name": dl_txt_name,
    }


@st.fragment
def render_export_toolbar(
    chat_history: list[dict[str, Any]],
    active_report_content: str,
    is_exec: bool,
    session_id: str | None
) -> None:
    """
    Renders the export action toolbar.
    Isolated within @st.fragment to prevent rerun race conditions on download clicks.
    """
    payload = build_export_payload(chat_history, active_report_content, is_exec, session_id)

    with st.container():
        c_pdf, c_md, c_txt = st.columns(3)

        with c_pdf:
            st.caption("📄 Executive PDF")
            kb = max(1, len(payload["pdf_bytes"]) // 1024)
            st.download_button(
                label=f"⬇️ Download PDF ({kb} KB)",
                data=payload["pdf_bytes"],
                file_name=payload["pdf_name"],
                mime="application/pdf",
                use_container_width=True,
                key="btn_export_pdf_isolated",
                on_click="ignore",
            )

        with c_md:
            st.caption("📝 Markdown Dossier")
            st.download_button(
                label=f"⬇️ Download .MD ({len(payload['md_bytes'])} B)",
                data=payload["md_bytes"],
                file_name=payload["md_name"],
                mime="text/markdown",
                use_container_width=True,
                key="btn_export_md_isolated",
                on_click="ignore",
            )

        with c_txt:
            st.caption("📋 Raw Text Log")
            st.download_button(
                label=f"⬇️ Download .TXT ({len(payload['txt_bytes'])} B)",
                data=payload["txt_bytes"],
                file_name=payload["txt_name"],
                mime="text/plain",
                use_container_width=True,
                key="btn_export_txt_isolated",
                on_click="ignore",
            )
