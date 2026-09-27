"""
Boardroom Transmutation Service.

Loads the official Boardroom Transmutation template from prompt/boardroom.md
and hydrates it with the target under evaluation and discussion findings.
Eliminates duplicated in-code prompt definitions.
"""

from __future__ import annotations

from typing import Any
from core.config import get_boardroom_prompt


def get_boardroom_system_prompt() -> str:
    """Return the raw system persona and operational directives from prompt/boardroom.md."""
    raw = get_boardroom_prompt()
    # If the file contains target/findings template markers, extract the directive header
    if "---" in raw:
        return raw.split("---")[0].strip()
    return raw.strip()


def build_transmutation_prompt(history: list[dict[str, Any]]) -> str:
    """
    Extract the evaluation target and critique findings from the chat history
    and hydrate them directly into prompt/boardroom.md template.

    Args:
        history: List of chat message dictionaries with 'role' and 'content'.

    Returns:
        The hydrated prompt string loaded directly from prompt/boardroom.md.
    """
    target = ""
    findings: list[str] = []

    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user" and not target:
            target = content
        elif role == "assistant":
            findings.append(content)

    findings_text = "\n\n---\n\n".join(findings) if findings else "(No prior assistant findings recorded.)"
    raw_template = get_boardroom_prompt()

    # Hydrate placeholders directly into prompt/boardroom.md
    if "{target}" in raw_template and "{findings}" in raw_template:
        return raw_template.replace("{target}", target or "(No target provided)").replace("{findings}", findings_text)

    # Clean fallback if template markers are absent
    return (
        f"{raw_template}\n\n---\n\n"
        f"## TARGET SYSTEM UNDER EVALUATION:\n{target}\n\n"
        f"## TECHNICAL CRITIQUE FINDINGS:\n{findings_text}"
    )
