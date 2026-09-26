import os
import sys
from pathlib import Path
from datetime import datetime

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import streamlit as st

# Import core backend engine
from engine import (
    DEFAULT_CATALOG,
    load_config,
    save_config,
    get_persona,
    check_connection_live,
    get_git_diff,
    fetch_remote_diff,
    extract_text_from_upload,
    call_llm,
    generate_pdf_report
)

APP_DIR = Path(__file__).parent.resolve()
STYLES_PATH = APP_DIR / "styles.css"
ROASTS_DIR = APP_DIR / "roasts"
ROASTS_DIR.mkdir(exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="The BoogieMan — Tech Debt Reaper",
    page_icon="👹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load external CSS stylesheet
if STYLES_PATH.exists():
    css_content = STYLES_PATH.read_text(encoding="utf-8")
    st.html(f"<style>\n{css_content}\n</style>")


# ================= PRESENTATION & HTML TEMPLATES =================
def render_hero_banner(active_provider: str, model_id: str, is_live: bool, status_desc: str) -> None:
    """Renders the top branding header and live engine status badge."""
    if is_live:
        badge_html = f'<span class="badge-pill badge-live">● {active_provider} LIVE</span> <span class="badge-pill badge-tech">⚡ {model_id}</span>'
    else:
        badge_html = f'<span class="badge-pill badge-unreachable">○ {active_provider} OFFLINE</span> <span class="badge-pill badge-tech">⚠️ {status_desc}</span>'

    banner_html = (
        '<div class="boogieman-banner">'
        '<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">'
        '<div>'
        '<div class="boogieman-crest">👹 THE BOOGIEMAN &bull; ARCHITECTURAL TRIBUNAL</div>'
        '<h1 class="boogieman-title">THE BOOGIEMAN</h1>'
        '<p class="boogieman-tagline">"The Mythic Reaper of Tech Debt. An ancient phantom lurking in the shadows of over-engineering. Dismantling bloated architectures, premature abstractions, and enterprise buzzwords."</p>'
        '</div>'
        f'<div style="margin-top: 6px;">{badge_html}</div>'
        '</div>'
        '</div>'
    )
    st.html(banner_html)


def render_dossier_header(title: str, subtitle: str = "STATUS: IRREVOCABLE") -> None:
    """Renders the header bar for an architectural evaluation or report."""
    html = (
        f'<div class="dossier-box">'
        f'<div class="dossier-header-bar">'
        f'<span class="dossier-title">{title}</span>'
        f'<span style="font-size: 0.75rem; color: #94a3b8; letter-spacing: 1px; font-weight: 600;">{subtitle}</span>'
        f'</div>'
        f'</div>'
    )
    st.html(html)


# ================= CACHED CONNECTION PROBER =================
def get_cached_live_status(provider_name: str, provider_data: dict, force_refresh: bool = False):
    """
    Caches connection probes to prevent slow UI reruns when switching tabs or dropdowns.
    Probes at most once every 45 seconds unless explicitly refreshed.
    """
    if "probe_cache" not in st.session_state:
        st.session_state["probe_cache"] = {}

    cache = st.session_state["probe_cache"]
    cached_entry = cache.get(provider_name)
    now = datetime.now().timestamp()

    if force_refresh or not cached_entry or (now - cached_entry.get("timestamp", 0) > 45):
        is_live, desc = check_connection_live(provider_name, provider_data)
        cache[provider_name] = {"is_live": is_live, "desc": desc, "timestamp": now}
        st.session_state["probe_cache"] = cache
        return is_live, desc

    return cached_entry["is_live"], cached_entry["desc"]


# Initialize session configuration
if "config" not in st.session_state:
    st.session_state.config = load_config()

cfg = st.session_state.config


# ================= SIDEBAR: ENGINE ARSENAL =================
with st.sidebar:
    st.html('<div style="text-align:center;padding:8px 0 12px 0;border-bottom:1px solid rgba(245,158,11,0.25);margin-bottom:14px;"><span style="font-family:Cinzel,serif;font-size:1.1rem;font-weight:800;letter-spacing:1.5px;color:#fbbf24;">⚙️ CONFIGURATION</span></div>')
    st.markdown("### 👹 BoogieMan Arsenal")
    st.caption("Zero-leak configuration. Each engine maintains its own parameters.")

    provider_options = list(DEFAULT_CATALOG.keys())
    saved_active = cfg.get("active_provider", "LM Studio (Local)")
    initial_idx = provider_options.index(saved_active) if saved_active in provider_options else 0

    selected_provider = st.selectbox("Active AI Engine", provider_options, index=initial_idx)
    p_data = cfg["providers"].get(selected_provider, DEFAULT_CATALOG[selected_provider])

    # Dynamic isolated inputs per provider
    if selected_provider in ["LM Studio (Local)", "Ollama (Local)", "Custom OpenAI-Compatible"]:
        p_base = st.text_input(
            "Local Server Base URL",
            value=p_data.get("base_url") or DEFAULT_CATALOG[selected_provider]["base_url"],
            help="Default uses 127.0.0.1 to avoid Windows IPv6 resolution latency"
        )
        p_data["base_url"] = p_base

        p_key = st.text_input(
            "API Key (Optional for local servers)",
            value=p_data.get("api_key", ""),
            type="password"
        )
        p_data["api_key"] = p_key

        p_mod = st.text_input("Local Model ID", value=p_data.get("model", "local-model"))
        p_data["model"] = p_mod

    elif selected_provider == "Azure OpenAI":
        p_end = st.text_input("Azure Endpoint URL", value=p_data.get("endpoint", ""))
        p_data["endpoint"] = p_end

        p_key = st.text_input("Azure API Key", value=p_data.get("api_key", ""), type="password")
        p_data["api_key"] = p_key

        p_dep = st.text_input("Deployment Name", value=p_data.get("deployment", "gpt-4o"))
        p_data["deployment"] = p_dep

        p_ver = st.text_input("API Version", value=p_data.get("api_version", "2024-02-15-preview"))
        p_data["api_version"] = p_ver

    elif selected_provider == "Google Gemini":
        p_key = st.text_input("Google AI Studio API Key", value=p_data.get("api_key", ""), type="password")
        p_data["api_key"] = p_key

        p_mod = st.text_input("Gemini Model", value=p_data.get("model", "gemini-2.5-flash"))
        p_data["model"] = p_mod

    elif selected_provider in ["OpenAI", "Groq", "Anthropic Claude"]:
        p_key = st.text_input(f"{selected_provider} API Key", value=p_data.get("api_key", ""), type="password")
        p_data["api_key"] = p_key

        p_mod = st.text_input("Model ID", value=p_data.get("model", DEFAULT_CATALOG[selected_provider]["model"]))
        p_data["model"] = p_mod

    # Responsive Action Controls
    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Lock Engine", use_container_width=True):
            cfg["active_provider"] = selected_provider
            cfg["providers"][selected_provider] = p_data
            save_config(cfg)
            st.session_state["active_provider"] = selected_provider
            # Probe immediately on lock
            is_alive, msg = get_cached_live_status(selected_provider, p_data, force_refresh=True)
            st.session_state["sidebar_feedback"] = ("success", f"🔒 Locked {selected_provider} as active engine!")

    with col_test:
        if st.button("🔄 Check Live", use_container_width=True):
            is_alive, msg = get_cached_live_status(selected_provider, p_data, force_refresh=True)
            if is_alive:
                st.session_state["sidebar_feedback"] = ("success", f"🟢 Live & Ready: {msg}")
            else:
                st.session_state["sidebar_feedback"] = ("warning", f"⚪ Unreachable: {msg}")

    # Display clear, persistent response banner in sidebar
    if "sidebar_feedback" in st.session_state:
        status_type, feedback_msg = st.session_state["sidebar_feedback"]
        if status_type == "success":
            st.success(feedback_msg)
        else:
            st.warning(feedback_msg)

    cfg["temperature"] = st.slider(
        "Cynicism Temperature",
        0.0, 1.0, float(cfg.get("temperature", 0.7)), 0.05
    )

    st.divider()
    st.markdown("### 📁 Executed Records")
    roast_files = sorted(ROASTS_DIR.glob("*.md"), reverse=True)
    if roast_files:
        sel_file = st.selectbox("Inspect Past Record", [f.name for f in roast_files])
        if sel_file:
            st.download_button(
                label="⬇️ Download Record (.md)",
                data=(ROASTS_DIR / sel_file).read_text(encoding="utf-8"),
                file_name=sel_file,
                mime="text/markdown",
                use_container_width=True
            )
    else:
        st.caption("No autopsies recorded yet.")


# ================= ACTIVE PROVIDER LIVE STATUS & HERO =================
active_p = cfg.get("active_provider") or selected_provider
active_p_data = p_data if active_p == selected_provider else cfg["providers"].get(active_p, p_data)

# Fast cached probe (0ms delay on tab/dropdown switches)
is_live, status_desc = get_cached_live_status(active_p, active_p_data)
model_name = active_p_data.get("model") or active_p_data.get("deployment") or "default"

render_hero_banner(
    active_provider=active_p,
    model_id=model_name,
    is_live=is_live,
    status_desc=status_desc
)


# ================= MAIN APPLICATION TABS =================
tab_slaughter, tab_export = st.tabs([
    "🎯 Contract Execution (Submit Target)",
    "⚡ BoogieMan Integration (Cursor & Copilot)"
])

with tab_slaughter:
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
            ]
        )
    with col_tone:
        tone_mode = st.selectbox(
            "Delivery Tone",
            [
                "👹 The BoogieMan (Brutally Satirical & Folkloric)",
                "👔 Executive Advisory Audit (Boardroom-Ready & Professional)"
            ]
        )

    target_content = ""

    # 1. Idea Pitch
    if target_mode == "💡 Architecture / Startup / Buzzword Soup":
        st.markdown("**Pitch your architecture or feature idea:** Evaluates necessity, over-engineering, and future maintenance horror.")
        target_content = st.text_area(
            "Pitch Description:",
            placeholder="e.g. I want to build a distributed microservice architecture with 12 AI agents communicating over Kafka to summarize pull requests...",
            height=160
        )

    # 2. Enterprise RFP
    elif target_mode == "📑 Enterprise RFP (Request for Proposal)":
        st.markdown("**Interrogate an RFP:** Upload PDF, Word (.docx), Excel (.xlsx), or text. Exposes vendor lock-in, unmeasurable SLAs, compliance theatre, and budget traps.")
        col_up, col_paste = st.columns([1, 1])
        with col_up:
            rfp_f = st.file_uploader("Upload RFP File (PDF, DOCX, XLSX, TXT, MD)", type=["pdf", "docx", "xlsx", "txt", "md", "json"], key="rfp_file")
            if rfp_f:
                target_content = (
                    "### TARGET CONTRACT: ENTERPRISE RFP (REQUEST FOR PROPOSAL)\n"
                    "[MANDATE: Interrogate vendor traps, unmeasurable SLAs, compliance theatre, scope ambiguity, and budget traps.]\n\n"
                    + extract_text_from_upload(rfp_f)
                )
                st.caption(f"Loaded {rfp_f.name}")
        with col_paste:
            rfp_t = st.text_area("Or Paste RFP Scope / Requirements:", height=150, key="rfp_txt")
            if rfp_t and not target_content:
                target_content = (
                    "### TARGET CONTRACT: ENTERPRISE RFP (REQUEST FOR PROPOSAL)\n"
                    "[MANDATE: Interrogate vendor traps, unmeasurable SLAs, compliance theatre, scope ambiguity, and budget traps.]\n\n"
                    + rfp_t
                )

    # 3. Product & Tech Roadmap
    elif target_mode == "🗺️ Product & Tech Roadmap":
        st.markdown("**Interrogate a Roadmap:** Upload Excel (.xlsx), Word (.docx), PDF, or CSV. Exposes feature-factory syndrome, zero tech-debt payoff, and speculative delivery milestones.")
        col_up, col_paste = st.columns([1, 1])
        with col_up:
            rd_f = st.file_uploader("Upload Roadmap Document (XLSX, DOCX, PDF, CSV, MD)", type=["xlsx", "xls", "docx", "pdf", "csv", "md", "txt"], key="rd_file")
            if rd_f:
                target_content = (
                    "### TARGET CONTRACT: PRODUCT & TECH ROADMAP\n"
                    "[MANDATE: Expose feature-factory traps, lack of tech-debt amortization, unrealistic milestones, and speculative building.]\n\n"
                    + extract_text_from_upload(rd_f)
                )
                st.caption(f"Loaded {rd_f.name}")
        with col_paste:
            rd_t = st.text_area("Or Paste Roadmap Milestones:", height=150, key="rd_txt")
            if rd_t and not target_content:
                target_content = (
                    "### TARGET CONTRACT: PRODUCT & TECH ROADMAP\n"
                    "[MANDATE: Expose feature-factory traps, lack of tech-debt amortization, unrealistic milestones, and speculative building.]\n\n"
                    + rd_t
                )

    # 4. Business Analyst (BA) Requirements Spec
    elif target_mode == "📋 Business Analyst (BA) Requirements Spec":
        st.markdown("**Interrogate a BA Spec:** Upload Word (.docx), PDF, Excel (.xlsx), or text. Strips circular logic, vanity metrics, edge-case delusions, and buzzword requirements.")
        col_up, col_paste = st.columns([1, 1])
        with col_up:
            ba_f = st.file_uploader("Upload BA Spec / PRD (DOCX, PDF, XLSX, TXT, MD)", type=["docx", "pdf", "xlsx", "txt", "md"], key="ba_file")
            if ba_f:
                target_content = (
                    "### TARGET CONTRACT: BUSINESS ANALYST REQUIREMENTS SPECIFICATION (PRD)\n"
                    "[MANDATE: Challenge business justification, expose circular user stories, strip vanity metrics, and reduce over-specified logic.]\n\n"
                    + extract_text_from_upload(ba_f)
                )
                st.caption(f"Loaded {ba_f.name}")
        with col_paste:
            ba_t = st.text_area("Or Paste User Stories / Acceptance Criteria:", height=150, key="ba_txt")
            if ba_t and not target_content:
                target_content = (
                    "### TARGET CONTRACT: BUSINESS ANALYST REQUIREMENTS SPECIFICATION (PRD)\n"
                    "[MANDATE: Challenge business justification, expose circular user stories, strip vanity metrics, and reduce over-specified logic.]\n\n"
                    + ba_t
                )

    # 5. Architecture & Source Code File
    elif target_mode == "📄 Architecture & Source Code File":
        st.markdown("**Upload a file:** Upload Python, TypeScript, Java, Go, Rust, SQL, YAML, or any document.")
        up_file = st.file_uploader("Upload file", type=["py", "ts", "js", "go", "rs", "java", "sql", "yaml", "json", "md", "txt", "pdf", "docx"], key="code_file")
        if up_file:
            target_content = extract_text_from_upload(up_file)
            st.code(target_content[:800] + ("\n... (truncated for preview)" if len(target_content) > 800 else ""), language="python")

    # 6. Git Diff (Local or Remote PR)
    elif target_mode == "🔍 Git Diff (Local, PR, or Branch Link)":
        st.markdown("**Review code changes:** Audit local repository diffs or inspect remote Pull Requests / Branch links.")

        git_sub = st.radio("Diff Source:", ["Local Workspace Diff", "Remote PR / Branch Link (GitHub / GitLab)"], horizontal=True)

        if git_sub == "Local Workspace Diff":
            col_l1, col_l2 = st.columns([1, 3])
            with col_l1:
                if st.button("Capture Local Diff"):
                    diff = get_git_diff()
                    if diff.startswith("Git diff failed") or diff.startswith("Error"):
                        st.error(diff)
                    elif not diff.strip():
                        st.info("Working directory is clean. No uncommitted diffs found.")
                        st.session_state["active_diff"] = ""
                    else:
                        st.session_state["active_diff"] = diff
                        st.success(f"Captured {len(diff)} characters of local diff.")

        else:
            pr_url = st.text_input("Enter Pull Request Link or Branch Compare URL:", placeholder="e.g. https://github.com/torvalds/linux/pull/123")
            needs_auth = st.session_state.get("git_needs_auth", False)
            git_user = ""
            git_token = ""

            if needs_auth:
                st.warning("🔒 This repository or PR is private. Please provide your Git credentials:")
                col_u, col_t = st.columns([1, 2])
                with col_u:
                    git_user = st.text_input("Git Username", key="auth_git_user")
                with col_t:
                    git_token = st.text_input("Personal Access Token (PAT)", type="password", key="auth_git_token")

            if st.button("Fetch Remote PR / Branch Diff"):
                if not pr_url.strip():
                    st.error("Please enter a valid PR or Branch comparison link.")
                else:
                    with st.spinner("Fetching diff from remote Git provider..."):
                        code, remote_diff = fetch_remote_diff(pr_url, token=git_token, username=git_user)
                        if code in [401, 404]:
                            st.session_state["git_needs_auth"] = True
                            st.error(f"Access Denied ({code}): Repository is private. Enter credentials above and retry.")
                        elif code != 200:
                            st.error(remote_diff)
                        else:
                            st.session_state["git_needs_auth"] = False
                            st.session_state["active_diff"] = remote_diff
                            st.success(f"Successfully captured diff ({len(remote_diff)} characters)!")

        if "active_diff" in st.session_state and st.session_state["active_diff"]:
            diff_content = st.session_state["active_diff"]
            target_content = f"### GIT DIFF:\n```diff\n{diff_content}\n```"
            st.markdown("#### Captured Diff Preview:")
            st.code(diff_content[:1500] + ("\n... (truncated for preview)" if len(diff_content) > 1500 else ""), language="diff")

    st.write("")
    # Centered, compact, professional execute button
    col_exec_l, col_exec_c, col_exec_r = st.columns([1, 2, 1])
    with col_exec_c:
        execute_btn = st.button("👹 SUMMON THE BOOGIEMAN", type="primary", use_container_width=True)

    if execute_btn:
        if not is_live:
            st.error(f"Cannot strike: {active_p} is offline or unreachable ({status_desc}). Verify connection in sidebar.")
        elif not target_content.strip():
            st.error("Cannot interrogate void. Please provide an idea, document, or git diff.")
        else:
            with st.spinner(f"The BoogieMan is dissecting the architecture via {active_p}..."):
                try:
                    persona_text = get_persona()
                    persona_text += (
                        "\n\n## MANDATORY AUTOPSY REQUIREMENT:\n"
                        "Provide a deeply thorough, exhaustive, and uncompromising architectural evaluation. "
                        "Do NOT provide brief or superficial bullet points. Scrutinize every nuance. "
                        "Fill out all 6 sections of the Mandatory Review Template with rigorous engineering depth, "
                        "concrete risk calculations, maintenance forecasts, and explicit technical trade-offs."
                    )

                    is_exec_mode = "Executive Advisory Audit" in tone_mode
                    if is_exec_mode:
                        persona_text += (
                            "\n\n## SPECIAL OVERRIDE: EXECUTIVE BRIEFING MODE\n"
                            "Deliver the verdict as a polished, diplomatic, yet ruthlessly analytical Executive Advisory Memo for the Board of Directors and C-suite. "
                            "Frame critiques through Capital Efficiency, Technical Debt Amortization, Operational Risk, and Time-to-Market. "
                            "Retain all architectural eliminations and the 6-part review structure, but use boardroom-appropriate corporate language."
                        )

                    roast_result = call_llm(
                        system_prompt=persona_text,
                        user_prompt=target_content,
                        provider=active_p,
                        p_cfg=active_p_data,
                        temp=float(cfg.get("temperature", 0.7))
                    )

                    st.session_state["last_verdict"] = roast_result
                    st.session_state["last_target"] = target_content
                    st.session_state["is_executive"] = is_exec_mode
                    st.session_state["chat_history"] = [
                        {"role": "assistant", "content": roast_result}
                    ]

                    # Save record to disk
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_path = ROASTS_DIR / f"verdict_{timestamp}.md"
                    out_path.write_text(
                        f"# BoogieMan Architectural Autopsy\n\n**Date:** {datetime.now()}\n**Engine:** {active_p}\n**Tone:** {tone_mode}\n\n## Input Target\n{target_content}\n\n## Verdict\n{roast_result}\n",
                        encoding="utf-8"
                    )

                except Exception as ex:
                    st.error(f"Execution Aborted: {ex}")

    # ================= VERDICT DOSSIER & EXPORTS =================
    if "last_verdict" in st.session_state and st.session_state["last_verdict"]:
        verdict_text = st.session_state["last_verdict"]
        is_exec = st.session_state.get("is_executive", False)

        st.markdown("---")
        dossier_title = "💼 EXECUTIVE ARCHITECTURAL ADVISORY MEMO" if is_exec else "👹 THE BOOGIEMAN: OFFICIAL ARCHITECTURAL AUTOPSY"
        render_dossier_header(dossier_title)

        # Primary Action & Export Toolbar
        st.markdown("##### 📥 Export & Transmutation Toolbar")
        col_pdf, col_md, col_trans = st.columns([1, 1, 2])

        with col_pdf:
            try:
                pdf_bytes = generate_pdf_report(
                    title="Executive Strategy Memo" if is_exec else "The BoogieMan Architectural Autopsy",
                    markdown_content=verdict_text,
                    is_executive=is_exec
                )
                st.download_button(
                    label="⬇️ Export as PDF Report",
                    data=pdf_bytes,
                    file_name=f"boogieman_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.caption(f"PDF generation error: {e}")

        with col_md:
            st.download_button(
                label="⬇️ Export as Markdown (.md)",
                data=verdict_text,
                file_name=f"boogieman_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_trans:
            if not is_exec:
                if st.button("👔 Transmute to Formal Boardroom Report", use_container_width=True):
                    with st.spinner("Transmuting into formal C-suite advisory memo..."):
                        try:
                            transmute_prompt = (
                                "You are a Principal Executive Strategy Consultant at an elite management advisory firm. "
                                "Take the following technical autopsy report and transmute it into an impeccably polished, diplomatic, "
                                "and data-grounded C-Suite Executive Memorandum. "
                                "Highlight Capital Allocation, Risk Exposure, Total Cost of Ownership (TCO), and Engineering Throughput. "
                                "Preserve the strict 6-part structure and all technical elimination recommendations, but replace satirical wording with surgical corporate prose.\n\n"
                                f"ORIGINAL AUTOPSY:\n{verdict_text}"
                            )
                            exec_memo = call_llm(
                                system_prompt="You are an elite corporate architect translating technical truth into boardroom value.",
                                user_prompt=transmute_prompt,
                                provider=active_p,
                                p_cfg=active_p_data,
                                temp=0.3
                            )
                            st.session_state["last_verdict"] = exec_memo
                            st.session_state["is_executive"] = True
                            st.session_state["chat_history"].append({"role": "assistant", "content": exec_memo})
                            st.success("Transmuted into Boardroom Executive Report!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Transmutation failed: {e}")
            else:
                if st.button("👹 Revert to Unfiltered BoogieMan Roast", use_container_width=True):
                    st.session_state["is_executive"] = False
                    st.rerun()

        # Display the formatted evaluation
        st.markdown(verdict_text)

        # ================= MULTI-TURN INTERROGATION CHAT =================
        st.markdown("---")
        st.markdown("### 💬 Interrogate the BoogieMan Further")
        st.caption("Ask follow-up questions, probe specific trade-offs, request simpler architectures, or challenge the verdict.")

        chat_hist = st.session_state.get("chat_history", [])

        # Display conversation messages (skip the initial verdict since it is already rendered in the dossier above)
        if len(chat_hist) > 1:
            for msg in chat_hist[1:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_query = st.chat_input("Ask how to simplify this, probe trade-offs, or demand alternative designs...")
        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("The BoogieMan is formulating response..."):
                    try:
                        followup_persona = get_persona()
                        if st.session_state.get("is_executive", False):
                            followup_persona += "\n\nMaintain the persona of a senior executive strategy consultant. Provide data-grounded, pragmatic corporate advice."
                        else:
                            followup_persona += "\n\nMaintain the sharp, cynical, satirical senior architect persona. Be ruthless, pragmatic, and concise."

                        bot_reply = call_llm(
                            system_prompt=followup_persona,
                            user_prompt=user_query,
                            provider=active_p,
                            p_cfg=active_p_data,
                            temp=float(cfg.get("temperature", 0.7)),
                            chat_history=chat_hist
                        )
                        st.markdown(bot_reply)

                        st.session_state["chat_history"].append({"role": "user", "content": user_query})
                        st.session_state["chat_history"].append({"role": "assistant", "content": bot_reply})
                    except Exception as e:
                        st.error(f"Conversation error: {e}")

        # Full Discussion Synthesis & Export Option
        if len(chat_hist) >= 3:
            st.markdown("#### 📄 Synthesize Full Discussion")
            st.caption("Consolidate the initial autopsy and all follow-up questions into a unified, formal executive report.")

            col_syn, col_exp_all = st.columns([1, 1])
            with col_syn:
                if st.button("👔 Transmute Full Discussion to Executive Report", use_container_width=True):
                    with st.spinner("Synthesizing full discussion into unified formal report..."):
                        try:
                            # Combine transcript
                            transcript_text = "\n\n".join([f"**{m['role'].upper()}:** {m['content']}" for m in chat_hist])
                            synthesis_prompt = (
                                "You are a Principal Enterprise Architect and Executive Strategy Advisor. "
                                "Synthesize the entire following technical discussion (including original evaluation and all follow-up Q&A) "
                                "into a single, highly structured, comprehensive, and polished Executive Architecture Report. "
                                "Use objective, professional, and non-satirical corporate language. "
                                "Include:\n"
                                "1. Executive Summary & Core Strategic Verdict\n"
                                "2. Component Elimination & Simplification Plan\n"
                                "3. Answers to Key Technical Inquiries Raised in Discussion\n"
                                "4. Total Cost of Ownership (TCO) & Maintenance Risk Assessment\n"
                                "5. Recommended Pragmatic Action Roadmap\n\n"
                                f"DISCUSSION TRANSCRIPT:\n{transcript_text}"
                            )
                            synth_report = call_llm(
                                system_prompt="You are an elite corporate advisor synthesizing technical debates into boardroom clarity.",
                                user_prompt=synthesis_prompt,
                                provider=active_p,
                                p_cfg=active_p_data,
                                temp=0.3
                            )
                            st.session_state["synthesized_report"] = synth_report
                            st.success("Unified Executive Report Generated!")
                        except Exception as e:
                            st.error(f"Synthesis failed: {e}")

            if "synthesized_report" in st.session_state:
                st.markdown("---")
                render_dossier_header("💼 SYNTHESIZED EXECUTIVE ADVISORY REPORT (FULL DISCUSSION)")
                st.markdown(st.session_state["synthesized_report"])
                
                try:
                    synth_pdf = generate_pdf_report(
                        title="Comprehensive Executive Advisory Report",
                        markdown_content=st.session_state["synthesized_report"],
                        is_executive=True
                    )
                    st.download_button(
                        label="⬇️ Download Synthesized Report as PDF",
                        data=synth_pdf,
                        file_name=f"boogieman_synthesized_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as ex:
                    st.caption(f"PDF build error: {ex}")


# ================= TAB: ZERO-UI INTEGRATIONS =================
with tab_export:
    st.markdown("### ⚡ The BoogieMan Everywhere: Zero-UI Setup")
    st.caption("Install the BoogieMan persona directly into your developer environment. No browser needed.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Cursor Setup (`.cursorrules`)")
        st.markdown("Inject the BoogieMan standards into Cursor's native background agent.")
        if st.button("Install .cursorrules in project_AI", use_container_width=True):
            try:
                (APP_DIR / ".cursorrules").write_text(get_persona(), encoding="utf-8")
                st.success("✅ Created `.cursorrules` in project_AI!")
            except Exception as e:
                st.error(f"Failed to create: {e}")

        st.code("""# Install in any repository:
cp project_AI/boogieMan.md /path/to/repo/.cursorrules""", language="bash")

    with col2:
        st.markdown("#### 🐙 GitHub Copilot Setup (`copilot-instructions.md`)")
        st.markdown("Enforce ruthless architectural reviews across all Copilot PR audits.")
        if st.button("Install .github/copilot-instructions.md", use_container_width=True):
            try:
                gh_dir = APP_DIR / ".github"
                gh_dir.mkdir(exist_ok=True)
                (gh_dir / "copilot-instructions.md").write_text(get_persona(), encoding="utf-8")
                st.success("✅ Created `.github/copilot-instructions.md` in project_AI!")
            except Exception as e:
                st.error(f"Failed to create: {e}")

        st.code("""# Install in any repository:
mkdir -p /path/to/repo/.github
cp project_AI/boogieMan.md /path/to/repo/.github/copilot-instructions.md""", language="bash")
