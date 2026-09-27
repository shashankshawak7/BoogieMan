"""
Technical Document & Code Diff Extractor.

Extracts text content from uploaded files (PDF, DOCX, XLSX, TXT)
and captures uncommitted git diffs or remote GitHub/GitLab pull requests.
"""

from __future__ import annotations

import base64
import subprocess
from typing import Any
import httpx


def get_git_diff(target_dir: str = ".") -> str:
    """Execute git diff in the specified directory, checking working tree and staged index."""
    try:
        res = subprocess.run(["git", "diff", "HEAD"], cwd=target_dir, capture_output=True, text=True, check=True)
        diff = res.stdout.strip()
        if not diff:
            res = subprocess.run(["git", "diff", "--staged"], cwd=target_dir, capture_output=True, text=True, check=True)
            diff = res.stdout.strip()
        return diff
    except Exception as e:
        return f"Error executing git diff: {e}"


def fetch_remote_diff(url_or_link: str, token: str = "", username: str = "") -> tuple[int, str]:
    """
    Fetch raw diff text from a GitHub or GitLab pull request / branch comparison URL.

    Returns:
        tuple[int, str]: (http_status_code, diff_content_or_error_message)
    """
    target_url = url_or_link.strip()
    if not target_url:
        return 400, "Error: Empty URL provided."

    headers = {
        "User-Agent": "BoogieMan-Architect/1.0",
        "Accept": "application/vnd.github.v3.diff"
    }

    if token.strip():
        if username.strip():
            auth_str = base64.b64encode(f"{username.strip()}:{token.strip()}".encode()).decode()
            headers["Authorization"] = f"Basic {auth_str}"
        else:
            headers["Authorization"] = f"Bearer {token.strip()}"
            headers["PRIVATE-TOKEN"] = token.strip()

    # Append .diff if targeting a pull request or merge request directly
    if ("github.com" in target_url or "gitlab.com" in target_url) and not target_url.endswith((".diff", ".patch")):
        target_url = target_url.rstrip("/") + ".diff"

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.get(target_url, headers=headers)
            if resp.status_code in [401, 404]:
                return resp.status_code, "Authentication required. Repository is private or credentials missing."
            if resp.status_code != 200:
                return resp.status_code, f"Error fetching diff ({resp.status_code}): {resp.text}"
            diff_text = resp.text.strip()
            if not diff_text:
                return 204, "Diff is empty. No changes detected."
            return 200, diff_text
    except Exception as e:
        return 500, f"Network error fetching diff: {e}"


def extract_text_from_upload(up_file: Any) -> str:
    """Extract human-readable text from uploaded PDF, Word (.docx), Excel (.xlsx), or raw text files."""
    if up_file is None:
        return ""

    filename = up_file.name.lower()

    # 1. Portable Document Format (PDF)
    if filename.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(up_file)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            return f"### DOCUMENT (PDF): {up_file.name} ({len(pages_text)} pages)\n\n" + "\n\n".join(pages_text)
        except Exception as e:
            return f"Error parsing PDF '{up_file.name}': {e}"

    # 2. Microsoft Word Document (.docx)
    elif filename.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(up_file)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            tables_text: list[str] = []
            for t in doc.tables:
                for row in t.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    tables_text.append(" | ".join(row_cells))
            full_text = "\n\n".join(paragraphs)
            if tables_text:
                full_text += "\n\n### TABLES IN DOCUMENT:\n" + "\n".join(tables_text)
            return f"### DOCUMENT (Word .docx): {up_file.name}\n\n{full_text}"
        except Exception as e:
            return f"Error parsing Word file '{up_file.name}': {e}"

    # 3. Microsoft Excel Workbook (.xlsx, .xls)
    elif filename.endswith((".xlsx", ".xls")):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(up_file, data_only=True)
            sheets_text: list[str] = []
            for sheetname in wb.sheetnames:
                sheet = wb[sheetname]
                rows_text: list[str] = []
                for row in sheet.iter_rows(values_only=True):
                    row_vals = [str(v).strip() if v is not None else "" for v in row]
                    if any(row_vals):
                        rows_text.append(" | ".join(row_vals))
                if rows_text:
                    sheets_text.append(f"#### Sheet: {sheetname}\n" + "\n".join(rows_text[:300]))
            return f"### SPREADSHEET (Excel): {up_file.name}\n\n" + "\n\n".join(sheets_text)
        except Exception as e:
            return f"Error parsing Excel file '{up_file.name}': {e}"

    # 4. Plaintext / Markdown / Code fallback
    else:
        try:
            content = up_file.read().decode("utf-8", errors="replace")
            return f"### DOCUMENT: {up_file.name}\n\n{content}"
        except Exception as e:
            return f"Error reading file '{up_file.name}': {e}"
