"""
Configuration & Catalog Management for The BoogieMan.

Loads and persists AI provider credentials and endpoint settings from config/boogie_config.json.
Provides prompt loading from prompt/ markdown files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Compute canonical paths relative to project root
CORE_DIR = Path(__file__).resolve().parent
SRC_DIR = CORE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent

CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_DIR.mkdir(exist_ok=True)

# Prefer unhidden config file, fallback to hidden
if (CONFIG_DIR / "boogie_config.json").exists():
    CONFIG_PATH = CONFIG_DIR / "boogie_config.json"
elif (CONFIG_DIR / ".boogie_config.json").exists():
    CONFIG_PATH = CONFIG_DIR / ".boogie_config.json"
else:
    CONFIG_PATH = CONFIG_DIR / "boogie_config.json"

PROMPT_DIR = PROJECT_ROOT / "prompt"
PERSONA_PATH = PROMPT_DIR / "boogieMan.md" if (PROMPT_DIR / "boogieMan.md").exists() else PROJECT_ROOT / "boogieMan.md"
BOARDROOM_PROMPT_PATH = PROMPT_DIR / "boardroom.md"

ROASTS_DIR = PROJECT_ROOT / "roasts"
ROASTS_DIR.mkdir(exist_ok=True)

CHATS_DIR = PROJECT_ROOT / "chats"
CHATS_DIR.mkdir(exist_ok=True)

STATIC_DIR = PROJECT_ROOT / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Default provider catalog
DEFAULT_CATALOG: dict[str, dict[str, Any]] = {
    "LM Studio (Local)": {
        "base_url": "http://127.0.0.1:1234/v1",
        "model": "local-model",
        "api_key": ""
    },
    "Ollama (Local)": {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "llama3",
        "api_key": ""
    },
    "Google Gemini": {
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "model": "gemini-2.5-flash"
    },
    "Groq": {
        "api_key": os.getenv("GROQ_API_KEY", ""),
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile"
    },
    "OpenAI": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini"
    },
    "Anthropic Claude": {
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "model": "claude-3-5-sonnet-20241022"
    },
    "Azure OpenAI": {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
        "endpoint": "",
        "deployment": "gpt-4o",
        "api_version": "2024-02-15-preview"
    },
    "Custom OpenAI-Compatible": {
        "base_url": "http://127.0.0.1:8000/v1",
        "model": "default",
        "api_key": ""
    }
}


def load_config() -> dict[str, Any]:
    """Load configuration from disk, overlaying any saved values onto DEFAULT_CATALOG."""
    cfg: dict[str, Any] = {
        "active_provider": "LM Studio (Local)",
        "providers": json.loads(json.dumps(DEFAULT_CATALOG)),
        "temperature": 0.7,
    }

    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if "active_provider" in saved:
                cfg["active_provider"] = saved["active_provider"]
            if "temperature" in saved:
                cfg["temperature"] = float(saved["temperature"])
            if "providers" in saved:
                for p_name, p_vals in saved["providers"].items():
                    if p_name in cfg["providers"]:
                        cfg["providers"][p_name].update(p_vals)
        except Exception:
            pass

    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    """Save configuration dictionary as formatted JSON."""
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def get_persona() -> str:
    """Load the satirical BoogieMan persona markdown prompt."""
    if PERSONA_PATH.exists():
        return PERSONA_PATH.read_text(encoding="utf-8")
    return "You are The BoogieMan, a cynical Senior Architect who roasts bad ideas ruthlessly."


def get_boardroom_prompt() -> str:
    """Load the executive boardroom transmutation prompt from prompt/boardroom.md."""
    if BOARDROOM_PROMPT_PATH.exists():
        return BOARDROOM_PROMPT_PATH.read_text(encoding="utf-8")
    return (
        "You are an Executive Strategy Advisor converting technical audits into an authoritative "
        "6-part C-suite Strategic Architectural Critique & Recommendations Report."
    )
