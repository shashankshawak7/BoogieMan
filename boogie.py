#!/usr/bin/env python3
"""
The BoogieMan CLI — The Tech Debt Reaper & Satirical Senior Architect.
Zero-bloat runner that executes the BoogieMan persona against ideas, files, or git diffs.
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import httpx

# Fix Windows cp1252 console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Rich console for terminal beauty if available
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    console = Console(force_terminal=True, legacy_windows=False)
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None


BOOGIE_DIR = Path(__file__).parent.resolve()
PERSONA_PATH = BOOGIE_DIR / "boogieMan.md"
ROASTS_DIR = BOOGIE_DIR / "roasts"


def print_ui(text: str, title: str = "THE BOOGIEMAN", border_style: str = "bold yellow"):
    if HAS_RICH:
        console.print(Panel(Markdown(text), title=f"[bold white]{title}[/bold white]", border_style=border_style))
    else:
        print(f"\n=== {title} ===\n")
        print(text)
        print("\n" + "=" * (len(title) + 8) + "\n")


def load_persona() -> str:
    if not PERSONA_PATH.exists():
        sys.exit(f"Error: BoogieMan persona file not found at {PERSONA_PATH}")
    return PERSONA_PATH.read_text(encoding="utf-8")


def get_git_diff(target_dir: str = ".") -> str:
    try:
        res = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            check=True
        )
        diff = res.stdout.strip()
        if not diff:
            # Check staged
            res = subprocess.run(
                ["git", "diff", "--staged"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            diff = res.stdout.strip()
        return diff
    except subprocess.CalledProcessError as e:
        sys.exit(f"Git diff failed: {e}")
    except FileNotFoundError:
        sys.exit("Error: 'git' command not found in PATH.")


def fetch_remote_diff(url_or_link: str, token: str = "") -> str:
    target_url = url_or_link.strip()
    if not target_url:
        sys.exit("Error: Empty PR/branch URL provided.")

    headers = {
        "User-Agent": "BoogieMan-CLI/1.0",
        "Accept": "application/vnd.github.v3.diff"
    }
    tok = token.strip() or os.getenv("GITHUB_TOKEN", "")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
        headers["PRIVATE-TOKEN"] = tok

    if "github.com" in target_url or "gitlab.com" in target_url:
        if not target_url.endswith(".diff") and not target_url.endswith(".patch"):
            target_url = target_url.rstrip("/") + ".diff"

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.get(target_url, headers=headers)
            if resp.status_code in [401, 404]:
                sys.exit(f"Error ({resp.status_code}): Repository or PR not found. For private repos, use --git-token or set GITHUB_TOKEN.")
            if resp.status_code != 200:
                sys.exit(f"Error fetching diff ({resp.status_code}): {resp.text}")
            diff_text = resp.text.strip()
            if not diff_text:
                sys.exit("Diff is empty. No changes detected.")
            return diff_text
    except Exception as e:
        sys.exit(f"Network error fetching diff: {e}")



def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Zero-bloat universal caller supporting:
    - Gemini (GEMINI_API_KEY)
    - Groq (GROQ_API_KEY)
    - OpenAI / OpenRouter / DeepSeek (OPENAI_API_KEY)
    - Local Ollama (OLLAMA_BASE_URL or default http://localhost:11434/v1)
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    # 1. Gemini
    if gemini_key:
        model = os.getenv("BOOGIE_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.7}
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                sys.exit(f"Gemini API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    # 2. OpenAI-compatible endpoints (Groq, DeepSeek, OpenAI, Ollama)
    base_url = "https://api.openai.com/v1"
    api_key = openai_key
    model = "gpt-4o-mini"

    if groq_key:
        base_url = "https://api.groq.com/openai/v1"
        api_key = groq_key
        model = "llama-3.3-70b-versatile"
    elif deepseek_key:
        base_url = "https://api.deepseek.com"
        api_key = deepseek_key
        model = "deepseek-chat"
    elif not api_key:
        # Check if Ollama is running locally
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get("http://localhost:11434/api/tags")
                if res.status_code == 200:
                    base_url = ollama_url
                    api_key = "ollama"
                    model = os.getenv("BOOGIE_MODEL", "llama3")
        except Exception:
            pass

    if not api_key:
        return (
            "[!] **NO API KEY FOUND!**\n\n"
            "The BoogieMan requires an LLM engine to power the slaughter.\n\n"
            "Set one in your environment or a `.env` file in `project_AI/`:\n"
            "- `GEMINI_API_KEY=your_key` (Google AI Studio - free tier available)\n"
            "- `GROQ_API_KEY=your_key` (Groq - blazing fast & free tier)\n"
            "- `OPENAI_API_KEY=your_key` (OpenAI / OpenRouter)\n"
            "- Or start local **Ollama** (`ollama run llama3`)."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": os.getenv("BOOGIE_MODEL", model),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        if resp.status_code != 200:
            sys.exit(f"LLM API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]





def main():
    parser = argparse.ArgumentParser(
        description="The BoogieMan — The Tech Debt Reaper & Satirical Senior Architect CLI"
    )
    parser.add_argument("idea", nargs="?", help="Idea, architecture, or buzzword soup to roast")
    parser.add_argument("-f", "--file", help="Path to code, markdown, or architecture file to roast")
    parser.add_argument("--rfp", help="Path to RFP document (PDF, TXT, MD) to roast for vendor traps & SLA bloat")
    parser.add_argument("--roadmap", help="Path to Product/Tech Roadmap to roast for feature-factory syndrome")
    parser.add_argument("--ba", help="Path to BA spec / User Stories to roast for gold-plating & scope creep")
    parser.add_argument("-d", "--git-diff", action="store_true", help="Extract git diff from current repo and roast uncommitted code")
    parser.add_argument("--diff-target", default=".", help="Directory to run git diff in (default: current directory)")
    parser.add_argument("--pr", help="URL of GitHub/GitLab Pull Request or branch compare link to roast")
    parser.add_argument("--git-token", help="GitHub/GitLab Personal Access Token for private repositories")
    parser.add_argument("-o", "--output", help="Optional path to save roast markdown file")

    args = parser.parse_args()

    def read_target_file(p: str) -> str:
        fp = Path(p)
        if not fp.exists():
            sys.exit(f"Error: Target file not found: {fp}")
        suf = fp.suffix.lower()
        if suf == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(fp)
                pages = [page.extract_text() or "" for page in reader.pages]
                return f"### DOCUMENT: {fp.name} (PDF, {len(pages)} pages)\n\n" + "\n\n".join(pages)
            except Exception as e:
                sys.exit(f"Error parsing PDF: {e}")
        elif suf == ".docx":
            try:
                import docx
                doc = docx.Document(fp)
                paragraphs = [par.text for par in doc.paragraphs if par.text.strip()]
                return f"### DOCUMENT (Word .docx): {fp.name}\n\n" + "\n\n".join(paragraphs)
            except Exception as e:
                sys.exit(f"Error parsing Word file: {e}")
        elif suf in [".xlsx", ".xls"]:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(fp, data_only=True)
                sheets_text = []
                for sname in wb.sheetnames:
                    sheet = wb[sname]
                    rows_text = []
                    for row in sheet.iter_rows(values_only=True):
                        row_vals = [str(v).strip() if v is not None else "" for v in row]
                        if any(row_vals):
                            rows_text.append(" | ".join(row_vals))
                    if rows_text:
                        sheets_text.append(f"#### Sheet: {sname}\n" + "\n".join(rows_text[:300]))
                return f"### SPREADSHEET (Excel): {fp.name}\n\n" + "\n\n".join(sheets_text)
            except Exception as e:
                sys.exit(f"Error parsing Excel file: {e}")
        return fp.read_text(encoding="utf-8", errors="replace")



    # Target selection
    if args.git_diff:
        print(f"[*] Extracting git diff from: {args.diff_target}...")
        diff_text = get_git_diff(args.diff_target)
        if not diff_text:
            print("No uncommitted git changes detected! Write some terrible code first.")
            return
        user_input = f"### CODE TO ROAST (GIT DIFF):\n```diff\n{diff_text}\n```"
    elif args.pr:
        print(f"[*] Fetching remote diff from: {args.pr}...")
        diff_text = fetch_remote_diff(args.pr, args.git_token or "")
        user_input = f"### REMOTE PR / BRANCH DIFF TO ROAST ({args.pr}):\n```diff\n{diff_text}\n```"
    elif args.rfp:
        content = read_target_file(args.rfp)
        user_input = (
            "### TARGET TYPE: ENTERPRISE RFP (REQUEST FOR PROPOSAL)\n"
            "[BOOGIEMAN MANDATE: Interrogate vendor traps, unmeasurable SLAs, compliance theatre, scope ambiguity, and budget traps.]\n\n"
            + content
        )
    elif args.roadmap:
        content = read_target_file(args.roadmap)
        user_input = (
            "### TARGET TYPE: PRODUCT & TECH ROADMAP\n"
            "[BOOGIEMAN MANDATE: Expose feature-factory syndrome, missing tech-debt payoffs, speculative delivery milestones, and vanity metrics.]\n\n"
            + content
        )
    elif args.ba:
        content = read_target_file(args.ba)
        user_input = (
            "### TARGET TYPE: BUSINESS ANALYST (BA) SPECIFICATION / USER STORIES\n"
            "[BOOGIEMAN MANDATE: Dismantle gold-plating, non-functional buzzwords, bloated user stories, circular logic, and lack of verified customer value.]\n\n"
            + content
        )
    elif args.file:
        content = read_target_file(args.file)
        user_input = f"### TARGET FILE TO ROAST:\n\n{content}"
    elif args.idea:
        user_input = args.idea
    else:
        # Interactive mode
        print("\n👹 THE BOOGIEMAN IS LISTENING. Feed him your architecture, startup idea, or design proposal:")
        try:
            user_input = input("\n> ")
        except (KeyboardInterrupt, EOFError):
            print("\nFled before the slaughter. Wise choice.")
            return

    if not user_input.strip():
        print("Empty input. BoogieMan sleeps.")
        return

    persona = load_persona()
    print("\n[*] The BoogieMan is sharpening the blade...")

    roast = call_llm(persona, user_input)

    print_ui(roast, title="BOOGIEMAN VERDICT & ARCHITECTURAL ROAST", border_style="bold red")

    # Save roast
    ROASTS_DIR.mkdir(exist_ok=True)
    out_file = Path(args.output) if args.output else ROASTS_DIR / f"roast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_file.write_text(f"# BoogieMan Architectural Roast\n\n**Date:** {datetime.now()}\n\n## Input Target\n{user_input}\n\n## Roast Verdict\n{roast}\n", encoding="utf-8")
    print(f"\n[+] Roast record etched in stone: {out_file.relative_to(BOOGIE_DIR) if out_file.is_relative_to(BOOGIE_DIR) else out_file}")


if __name__ == "__main__":
    main()
