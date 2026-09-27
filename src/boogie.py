#!/usr/bin/env python3
"""
The BoogieMan CLI — The Tech Debt Reaper & Satirical Senior Architect.

Zero-bloat command-line interface that evaluates architecture ideas, source code files,
enterprise RFPs, product roadmaps, or git diffs against the satirical BoogieMan persona.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import sys

# Windows UTF-8 safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Optional rich console formatting
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    console = Console(force_terminal=True, legacy_windows=False)
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

# Ensure src/ and project root are in sys.path
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import ROASTS_DIR, get_persona, load_config
from core.extractors import extract_text_from_upload, fetch_remote_diff, get_git_diff
from core.llm import call_llm


def print_ui(text: str, title: str = "THE BOOGIEMAN", border_style: str = "bold yellow") -> None:
    """Print formatted markdown panel in terminal using Rich, or fallback to plain text."""
    if HAS_RICH and console is not None:
        console.print(Panel(Markdown(text), title=f"[bold white]{title}[/bold white]", border_style=border_style))
    else:
        print(f"\n=== {title} ===\n")
        print(text)
        print("\n" + "=" * (len(title) + 8) + "\n")


def read_local_file(path_str: str) -> str:
    """Read and parse local file content based on file extension."""
    fp = Path(path_str)
    if not fp.exists():
        sys.exit(f"Error: Target file not found: {fp}")

    suffix = fp.suffix.lower()
    if suffix in [".pdf", ".docx", ".xlsx", ".xls"]:
        class MockUpload:
            def __init__(self, p: Path):
                self.name = p.name
                self._p = p
            def read(self):
                return self._p.read_bytes()
        return extract_text_from_upload(MockUpload(fp))

    return fp.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    """Main CLI entrypoint for The BoogieMan."""
    parser = argparse.ArgumentParser(
        description="The BoogieMan — The Tech Debt Reaper & Satirical Senior Architect CLI"
    )
    parser.add_argument("idea", nargs="?", help="Idea, architecture, or buzzword soup to roast")
    parser.add_argument("-f", "--file", help="Path to code, markdown, or architecture file to roast")
    parser.add_argument("--rfp", help="Path to RFP document (PDF, TXT, MD) to roast for vendor traps & SLA bloat")
    parser.add_argument("--roadmap", help="Path to Product/Tech Roadmap to roast for feature-factory syndrome")
    parser.add_argument("--ba", help="Path to BA spec / User Stories to roast for scope creep")
    parser.add_argument("-d", "--git-diff", action="store_true", help="Extract git diff from current repo")
    parser.add_argument("--diff-target", default=".", help="Directory to run git diff in (default: current directory)")
    parser.add_argument("--pr", help="URL of GitHub/GitLab Pull Request or branch compare link")
    parser.add_argument("--git-token", help="Personal Access Token for private repositories")
    parser.add_argument("-o", "--output", help="Optional path to save roast markdown file")

    args = parser.parse_args()

    # Determine evaluation target
    if args.git_diff:
        print(f"[*] Extracting git diff from: {args.diff_target}...")
        diff_text = get_git_diff(args.diff_target)
        if not diff_text or diff_text.startswith("Error"):
            print(f"No git changes detected or error: {diff_text}")
            return
        user_input = f"### CODE TO ROAST (GIT DIFF):\n```diff\n{diff_text}\n```"
    elif args.pr:
        print(f"[*] Fetching remote diff from: {args.pr}...")
        code, diff_text = fetch_remote_diff(args.pr, args.git_token or "")
        if code != 200:
            sys.exit(f"Error fetching diff ({code}): {diff_text}")
        user_input = f"### REMOTE PR / BRANCH DIFF TO ROAST ({args.pr}):\n```diff\n{diff_text}\n```"
    elif args.rfp:
        content = read_local_file(args.rfp)
        user_input = (
            "### TARGET TYPE: ENTERPRISE RFP (REQUEST FOR PROPOSAL)\n"
            "[BOOGIEMAN MANDATE: Interrogate vendor traps, unmeasurable SLAs, compliance theatre, scope ambiguity, and budget traps.]\n\n"
            + content
        )
    elif args.roadmap:
        content = read_local_file(args.roadmap)
        user_input = (
            "### TARGET TYPE: PRODUCT & TECH ROADMAP\n"
            "[BOOGIEMAN MANDATE: Expose feature-factory syndrome, missing tech-debt payoffs, speculative delivery milestones, and vanity metrics.]\n\n"
            + content
        )
    elif args.ba:
        content = read_local_file(args.ba)
        user_input = (
            "### TARGET TYPE: BUSINESS ANALYST (BA) SPECIFICATION / USER STORIES\n"
            "[BOOGIEMAN MANDATE: Dismantle gold-plating, non-functional buzzwords, bloated user stories, circular logic, and lack of verified customer value.]\n\n"
            + content
        )
    elif args.file:
        content = read_local_file(args.file)
        user_input = f"### TARGET FILE TO ROAST:\n\n{content}"
    elif args.idea:
        user_input = args.idea
    else:
        print("\n👹 THE BOOGIEMAN IS LISTENING. Feed him your architecture, startup idea, or design proposal:")
        try:
            user_input = input("\n> ")
        except (KeyboardInterrupt, EOFError):
            print("\nFled before the slaughter. Wise choice.")
            return

    if not user_input.strip():
        print("Empty input. BoogieMan sleeps.")
        return

    # Load engine configuration
    cfg = load_config()
    active_p = cfg.get("active_provider", "LM Studio (Local)")
    p_data = cfg.get("providers", {}).get(active_p, {})
    persona = get_persona()

    print(f"\n[*] The BoogieMan is sharpening the blade using [{active_p}]...")

    try:
        roast = call_llm(
            system_prompt=persona,
            user_prompt=user_input,
            provider=active_p,
            p_cfg=p_data,
            temp=float(cfg.get("temperature", 0.7))
        )
    except Exception as e:
        sys.exit(f"\n[!] Inference failed: {e}")

    print_ui(roast, title="BOOGIEMAN VERDICT & ARCHITECTURAL ROAST", border_style="bold red")

    # Persist markdown record
    ROASTS_DIR.mkdir(exist_ok=True)
    out_file = Path(args.output) if args.output else ROASTS_DIR / f"roast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_file.write_text(
        f"# BoogieMan Architectural Roast\n\n"
        f"**Date:** {datetime.now()}\n"
        f"**Engine:** {active_p}\n\n"
        f"## Input Target\n{user_input}\n\n"
        f"## Roast Verdict\n{roast}\n",
        encoding="utf-8"
    )
    print(f"\n[+] Roast record etched in stone: {out_file.name}")


if __name__ == "__main__":
    main()
