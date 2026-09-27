"""
PDF Report Generator for The BoogieMan.

Compiles Markdown text into clean, multi-page, formatted A4 PDF reports using FPDF2.
Includes Unicode sanitization, header/footer branding, and client-side base64 download encoding.
"""

from __future__ import annotations

import base64
from typing import Any
from fpdf import FPDF


class BoogieManPDF(FPDF):
    """Custom FPDF layout with branded headers, page numbering footers, and margins."""

    def __init__(self, is_executive: bool = False, *args: Any, **kwargs: Any) -> None:
        super().__init__(orientation="P", unit="mm", format="A4", *args, **kwargs)
        self.is_executive = is_executive
        self.set_margins(15, 18, 15)

    def header(self) -> None:
        self.set_font("Helvetica", "B", 9)
        if self.is_executive:
            self.set_text_color(30, 58, 102)
            self.cell(0, 6, "EXECUTIVE ARCHITECTURAL ADVISORY MEMO | C-SUITE CONFIDENTIAL", border=False, align="L")
        else:
            self.set_text_color(185, 28, 28)
            self.cell(0, 6, "THE BOOGIEMAN -- OFFICIAL ARCHITECTURAL AUTOPSY REPORT", border=False, align="L")
        self.ln(7)
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.3)
        self.line(15, 16, 195, 16)
        self.ln(3)

    def footer(self) -> None:
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}} -- The BoogieMan Architectural Tribunal", align="C")


def sanitize_for_pdf(text: str) -> str:
    """Sanitize Unicode symbols, emojis, and typography characters into latin-1 safe representations."""
    replacements: dict[str, str] = {
        "—": " - ", "–": " - ", "−": " - ",
        "“": '"', "”": '"', "„": '"',
        "‘": "'", "’": "'", "‚": "'",
        "•": "* ", "▪": "* ", "▫": "* ",
        "…": "...", "→": "->", "←": "<-", "⇒": "=>", "⇔": "<=>",
        "✔": "[YES]", "✅": "[PASS]", "❌": "[FAIL]", "✖": "[X]",
        "⚠️": "[WARNING]", "⚡": "[ACTIVE]", "💡": "[IDEA]",
        "👹": "[BOOGIEMAN]", "👔": "[EXECUTIVE]", "🏛️": "[BOARD]",
        "📋": "[SPEC]", "📑": "[RFP]", "🗺️": "[ROADMAP]", "🔍": "[AUDIT]",
        "🎯": "[TARGET]", "⚙️": "[CONFIG]", "🔒": "[LOCKED]", "🟢": "[LIVE]",
        "⚪": "[OFFLINE]", "⬇️": "[EXPORT]", "💬": "[CHAT]", "💰": "[COST]",
        "≥": ">=", "≤": "<=", "≠": "!=", "≈": "~", "±": "+/-",
        "\t": "    ", "\r": ""
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_pdf_report(title: str, markdown_content: str, is_executive: bool = False) -> bytes:
    """
    Render clean, perfectly wrapped, non-clipped PDF document bytes from Markdown content.
    Handles headings, bullet lists, code blocks, and tables without cutting off text.
    """
    pdf = BoogieManPDF(is_executive=is_executive)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    epw = pdf.epw  # Effective page width (180mm with 15mm margins)

    # Document Title Block
    pdf.set_font("Helvetica", "B", 14)
    if is_executive:
        pdf.set_text_color(15, 23, 42)
    else:
        pdf.set_text_color(180, 83, 9)
    pdf.multi_cell(w=epw, h=7.5, text=sanitize_for_pdf(title))
    pdf.ln(1)

    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w=epw, h=5, text="Target: Technical Evaluation Report | Confidential", ln=True)
    pdf.ln(2)

    # Accent Divider
    if is_executive:
        pdf.set_draw_color(30, 58, 102)
    else:
        pdf.set_draw_color(217, 119, 6)
    pdf.set_line_width(0.6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    # Line by Line Markdown Parsing
    lines = markdown_content.split("\n")
    in_code_block = False

    for raw_line in lines:
        stripped = raw_line.strip()

        # Handle Code Fences
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                pdf.ln(1)
            else:
                pdf.ln(2)
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 8.5)
            pdf.set_text_color(30, 41, 59)
            pdf.set_fill_color(241, 245, 249)
            line_sanitized = sanitize_for_pdf("  " + raw_line)
            pdf.multi_cell(w=epw, h=4.2, text=line_sanitized, fill=True)
            continue

        line = sanitize_for_pdf(stripped)

        # Blank Line
        if not line:
            pdf.ln(2)
            continue

        # Level 1 Heading (# Title)
        if line.startswith("# "):
            if pdf.get_y() > 245:
                pdf.add_page()
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            heading_text = line[2:].strip().replace("**", "")
            pdf.multi_cell(w=epw, h=6.5, text=heading_text)
            pdf.ln(1)

        # Level 2 Heading (## Section)
        elif line.startswith("## "):
            if pdf.get_y() > 245:
                pdf.add_page()
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11.5)
            if is_executive:
                pdf.set_text_color(30, 58, 102)
            else:
                pdf.set_text_color(180, 83, 9)
            heading_text = line[3:].strip().replace("**", "")
            pdf.multi_cell(w=epw, h=6, text=heading_text)
            pdf.ln(1)

        # Level 3 Heading (### Sub-section)
        elif line.startswith("### "):
            if pdf.get_y() > 245:
                pdf.add_page()
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            if is_executive:
                pdf.set_text_color(51, 65, 85)
            else:
                pdf.set_text_color(146, 64, 14)
            heading_text = line[4:].strip().replace("**", "")
            pdf.multi_cell(w=epw, h=5.5, text=heading_text)
            pdf.ln(1)

        # Horizontal Rule
        elif line.startswith("---") or line.startswith("***"):
            pdf.ln(2)
            pdf.set_draw_color(226, 232, 240)
            pdf.set_line_width(0.3)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(3)

        # Table Row (| Col 1 | Col 2 |)
        elif line.startswith("|") and line.endswith("|"):
            if "---" in line:
                continue
            cells = [c.strip().replace("**", "") for c in line.split("|")[1:-1]]
            if cells:
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(30, 41, 59)
                row_str = " | ".join(cells)
                pdf.multi_cell(w=epw, h=4.5, text=f"  [>] {row_str}")

        # Bullet List Item (* or -)
        elif line.startswith("* ") or line.startswith("- "):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 41, 59)
            content = line[2:].strip().replace("**", "")
            pdf.multi_cell(w=epw, h=4.8, text=f"  *  {content}")

        # Numbered List Item (1. 2. etc.)
        elif len(line) > 2 and line[0].isdigit() and line[1:3] in [". ", ") "]:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 41, 59)
            content = line[3:].strip().replace("**", "")
            pdf.multi_cell(w=epw, h=4.8, text=f"  {line[:2]} {content}")

        # Standard Paragraph Text
        else:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 41, 59)
            clean_p = line.replace("**", "").replace("`", "")
            pdf.multi_cell(w=epw, h=4.8, text=clean_p)

    return bytes(pdf.output())


def render_base64_download_button(
    data: bytes | str,
    filename: str,
    mime_type: str,
    label: str,
    custom_class: str = "action-dl-btn"
) -> str:
    """Render a direct client-side HTML5 download anchor with base64 data URI."""
    if isinstance(data, str):
        payload_bytes = data.encode("utf-8")
    elif isinstance(data, bytes):
        payload_bytes = data
    else:
        payload_bytes = bytes(data)

    b64_str = base64.b64encode(payload_bytes).decode("ascii")
    return f'<a href="data:{mime_type};base64,{b64_str}" download="{filename}" class="{custom_class}" target="_self">{label}</a>'
