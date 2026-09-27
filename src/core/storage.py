"""
Session Storage Service for The BoogieMan.

Manages loading, persisting, previewing, and deleting chat interrogation sessions
stored as JSON files in the project's chats/ directory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.config import CHATS_DIR


def list_chat_sessions() -> list[dict[str, Any]]:
    """Return all saved chat sessions ordered by most recently updated."""
    sessions: list[dict[str, Any]] = []

    for session_file in CHATS_DIR.glob("*.json"):
        try:
            raw_text = session_file.read_text(encoding="utf-8")
            data = json.loads(raw_text)
            messages = data.get("messages", [])

            # Extract a brief preview from user's first prompt
            pitch_preview = messages[0].get("content", "").strip() if messages else ""
            if len(pitch_preview) > 150:
                pitch_preview = pitch_preview[:150] + "..."

            # Extract a brief preview from assistant's initial response
            verdict_preview = ""
            if len(messages) > 1:
                v_raw = messages[1].get("content", "").strip()
                v_clean = " ".join([line.strip("#* ") for line in v_raw.splitlines() if line.strip()])
                verdict_preview = (v_clean[:140] + "...") if len(v_clean) > 140 else v_clean

            desc_parts: list[str] = []
            if pitch_preview:
                desc_parts.append(f"Pitch: {pitch_preview}")
            if verdict_preview:
                desc_parts.append(f"Verdict: {verdict_preview}")

            combined_desc = "\n\n".join(desc_parts) if desc_parts else data.get("title", "Interrogation Session")

            sessions.append({
                "id": data.get("id", session_file.stem),
                "title": data.get("title", "Untitled Interrogation"),
                "preview": combined_desc,
                "updated_at": data.get("updated_at", ""),
                "message_count": len(messages),
            })
        except Exception:
            continue

    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


def save_chat_session(session_data: dict[str, Any]) -> str:
    """Save or update a chat session JSON file on disk."""
    session_id = session_data.get("id")
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_data["id"] = session_id

    session_data["updated_at"] = datetime.now().isoformat()
    out_file = CHATS_DIR / f"{session_id}.json"
    out_file.write_text(json.dumps(session_data, indent=2), encoding="utf-8")
    return session_id


def load_chat_session(session_id: str) -> dict[str, Any]:
    """Load a chat session dictionary by session ID."""
    session_file = CHATS_DIR / f"{session_id}.json"
    if session_file.exists():
        try:
            return json.loads(session_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def delete_chat_session(session_id: str) -> bool:
    """Delete a chat session file from disk."""
    session_file = CHATS_DIR / f"{session_id}.json"
    if session_file.exists():
        try:
            session_file.unlink()
            return True
        except Exception:
            return False
    return False
