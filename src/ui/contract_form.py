"""
Initial Contract Submission Form & Zero-UI Setup Component.

Renders:
1. Target contract intake tabs (Idea pitch, Enterprise RFP, Product Roadmap, BA Spec, Source File, Git Diff).
2. Primary trigger: "SUMMON THE BOOGIEMAN" button.
3. Zero-UI configuration expander for Cursor (.cursorrules) and GitHub Copilot (copilot-instructions.md).
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st

from core.config import PROJECT_ROOT, get_persona
from core.extractors import extract_text_from_upload, fetch_remote_diff, get_git_diff


def render_contract_form(is_live: bool, active_p: str, status_desc: str) -> None:
    """Render the primary intake form when no active chat messages exist."""
    st.markdown("### 🎯 Submit Target Contract")
    st.caption("Present your architecture, code, RFP, or roadmap. The BoogieMan will ruthlessly evaluate its right to exist.")

    col_type, col_tone = st.columns([2, 1])
    with col_type:
        target_mode = st.selectbox(
            "Select Target Contract",
            [
                "💡 Architecture / Startup / Buzzword Soup",
                "📑 Enterprise RFP (Request for Proposal)",
                "🗺️ Product & Tech Roadmap",
                "📋 Business Analyst (BA) Requirements Spec",
                "📄 Architecture & Source Code File",
                "🔍 Git Diff (Local, PR, or Branch Link)"
            ],
            key="init_target_mode"
        )
    with col_tone:
        tone_mode = st.selectbox(
            "Delivery Tone",
            [
                "👹 The BoogieMan (Brutally Satirical & Folkloric)",
                "👔 Executive Advisory Audit (Boardroom-Ready & Professional)"
            ],
            key="init_tone_mode"
        )

    target_content = ""

    # 1. Architecture Pitch
    if target_mode == "💡 Architecture / Startup / Buzzword Soup":
        target_content = st.text_area(
            "Pitch Description:",
            placeholder="e.g. I want to build a distributed microservice architecture with 12 AI agents communicating over Kafka to summarize pull requests...",
            height=140,
            key="init_pitch_txt"
        )

    # 2. Enterprise RFP
    elif target_mode == "📑 Enterprise RFP (Request for Proposal)":
        col_up, col_paste = st.columns([1, 1])
        with col_up:
            rfp_f = st.file_uploader("Upload RFP File (PDF, DOCX, XLSX, TXT, MD)", type=["pdf", "docx", "xlsx", "txt", "md", "json"], key="init_rfp_file")
            if rfp_f:
                target_content = f"### TARGET CONTRACT: ENTERPRISE RFP\n\n{extract_text_from_upload(rfp_f)}"
                st.caption(f"Loaded {rfp_f.name}")
        with col_paste:
            rfp_t = st.text_area("Or Paste RFP Scope:", height=130, key="init_rfp_txt")
            if rfp_t and not target_content:
                target_content = f"### TARGET CONTRACT: ENTERPRISE RFP\n\n{rfp_t}"

    # 3. Product Roadmap
    elif target_mode == "🗺️ Product & Tech Roadmap":
        col_up, col_paste = st.columns([1, 1])
        with col_up:
            rd_f = st.file_uploader("Upload Roadmap Document (XLSX, DOCX, PDF, CSV, MD)", type=["xlsx", "xls", "docx", "pdf", "csv", "md", "txt"], key="init_rd_file")
            if rd_f:
                target_content = f"### TARGET CONTRACT: PRODUCT & TECH ROADMAP\n\n{extract_text_from_upload(rd_f)}"
                st.caption(f"Loaded {rd_f.name}")
        with col_paste:
            rd_t = st.text_area("Or Paste Roadmap:", height=130, key="init_rd_txt")
            if rd_t and not target_content:
                target_content = f"### TARGET CONTRACT: PRODUCT & TECH ROADMAP\n\n{rd_t}"

    # 4. BA Requirements Spec
    elif target_mode == "📋 Business Analyst (BA) Requirements Spec":
        col_up, col_paste = st.columns([1, 1])
        with col_up:
            ba_f = st.file_uploader("Upload BA Spec / PRD (DOCX, PDF, XLSX, TXT, MD)", type=["docx", "pdf", "xlsx", "txt", "md"], key="init_ba_file")
            if ba_f:
                target_content = f"### TARGET CONTRACT: BA SPECIFICATION\n\n{extract_text_from_upload(ba_f)}"
                st.caption(f"Loaded {ba_f.name}")
        with col_paste:
            ba_t = st.text_area("Or Paste User Stories:", height=130, key="init_ba_txt")
            if ba_t and not target_content:
                target_content = f"### TARGET CONTRACT: BA SPECIFICATION\n\n{ba_t}"

    # 5. Architecture & Source Code File
    elif target_mode == "📄 Architecture & Source Code File":
        up_file = st.file_uploader("Upload Code File", type=["py", "ts", "js", "go", "rs", "java", "sql", "yaml", "json", "md", "txt", "pdf", "docx"], key="init_code_file")
        if up_file:
            target_content = extract_text_from_upload(up_file)
            st.code(target_content[:800] + ("\n... (truncated for preview)" if len(target_content) > 800 else ""), language="python")

    # 6. Git Diff (Local or Remote PR)
    elif target_mode == "🔍 Git Diff (Local, PR, or Branch Link)":
        git_sub = st.radio("Diff Source:", ["Local Workspace Diff", "Remote PR / Branch Link"], horizontal=True, key="init_git_sub")
        if git_sub == "Local Workspace Diff":
            col_l1, col_l2 = st.columns([1, 3])
            with col_l1:
                if st.button("Capture Local Diff", key="init_btn_local_diff"):
                    diff = get_git_diff()
                    if diff.startswith("Git diff failed") or diff.startswith("Error"):
                        st.error(diff)
                    elif not diff.strip():
                        st.info("Working directory is clean. No uncommitted diffs found.")
                        st.session_state["active_diff"] = ""
                    else:
                        st.session_state["active_diff"] = diff
                        st.success(f"Captured {len(diff)} chars.")
        else:
            pr_url = st.text_input("Pull Request Link / Branch Compare URL:", placeholder="https://github.com/org/repo/pull/123", key="init_pr_url")
            needs_auth = st.session_state.get("git_needs_auth", False)
            git_user, git_token = "", ""
            if needs_auth:
                st.warning("🔒 Private repository credentials required:")
                col_u, col_t = st.columns([1, 2])
                with col_u:
                    git_user = st.text_input("Git Username", key="init_auth_user")
                with col_t:
                    git_token = st.text_input("Personal Access Token (PAT)", type="password", key="init_auth_token")

            if st.button("Fetch Remote Diff", key="init_btn_remote_diff"):
                if pr_url.strip():
                    with st.spinner("Fetching diff..."):
                        code, remote_diff = fetch_remote_diff(pr_url, token=git_token, username=git_user)
                        if code in [401, 404]:
                            st.session_state["git_needs_auth"] = True
                            st.error("Private repo. Enter credentials.")
                        elif code != 200:
                            st.error(remote_diff)
                        else:
                            st.session_state["git_needs_auth"] = False
                            st.session_state["active_diff"] = remote_diff
                            st.success(f"Captured {len(remote_diff)} chars!")

        if "active_diff" in st.session_state and st.session_state["active_diff"]:
            target_content = f"### GIT DIFF:\n```diff\n{st.session_state['active_diff']}\n```"
            st.code(st.session_state["active_diff"][:1000] + ("\n... (truncated)" if len(st.session_state["active_diff"]) > 1000 else ""), language="diff")

    st.write("")
    col_exec_l, col_exec_c, col_exec_r = st.columns([1, 2, 1])
    with col_exec_c:
        execute_btn = st.button("👹 SUMMON THE BOOGIEMAN", type="primary", use_container_width=True)

    if execute_btn:
        if not is_live:
            st.error(f"Cannot strike: {active_p} is offline ({status_desc}). Verify connection in sidebar.")
        elif not target_content.strip():
            st.error("Cannot interrogate void. Please provide an idea, document, or git diff.")
        else:
            is_exec_mode = "Executive Advisory Audit" in tone_mode
            clean_title = f"{target_mode.split(' ')[1]} - {target_content[:28].strip()}..."
            user_msg = f"**[{target_mode.split(' ')[1]}]** {target_content}"
            st.session_state.contract_target_title = clean_title
            st.session_state.active_mode = "executive" if is_exec_mode else "boogieman"
            st.session_state.chat_history = [{"role": "user", "content": user_msg}]
            st.session_state["streaming_target"] = target_content
            st.session_state["streaming_tone"] = tone_mode
            st.rerun()

    # Zero-UI Integration Expander
    with st.expander("⚡ Zero-UI Setup (Cursor & GitHub Copilot Integration)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🎯 Cursor Setup (`.cursorrules`)")
            if st.button("Install .cursorrules in project", key="btn_cursor_initial", use_container_width=True):
                try:
                    (PROJECT_ROOT / ".cursorrules").write_text(get_persona(), encoding="utf-8")
                    st.success("✅ Created `.cursorrules` in project root!")
                except Exception as e:
                    st.error(f"Failed: {e}")
            st.code("cp prompt/boogieMan.md /path/to/repo/.cursorrules", language="bash")
        with col2:
            st.markdown("#### 🐙 GitHub Copilot Setup (`copilot-instructions.md`)")
            if st.button("Install .github/copilot-instructions.md", key="btn_copilot_initial", use_container_width=True):
                try:
                    gh_dir = PROJECT_ROOT / ".github"
                    gh_dir.mkdir(exist_ok=True)
                    (gh_dir / "copilot-instructions.md").write_text(get_persona(), encoding="utf-8")
                    st.success("✅ Created `.github/copilot-instructions.md`!")
                except Exception as e:
                    st.error(f"Failed: {e}")
            st.code("mkdir -p .github && cp prompt/boogieMan.md .github/copilot-instructions.md", language="bash")
