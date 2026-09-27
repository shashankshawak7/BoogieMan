"""
The BoogieMan Engine — Core Backend Subsystem Facade.

Aggregates modular backend components:
- config: Provider catalogs, configurations, and persona loading
- prober: Live connectivity & health verification
- extractors: Document and git diff parsers
- llm: Streaming and synchronous LLM inference
- storage: Chat session JSON persistence
- pdf_generator: A4 PDF report generation
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure package importability
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Re-export configuration and constants
from core.config import (
    CONFIG_DIR,
    CONFIG_PATH,
    DEFAULT_CATALOG,
    PERSONA_PATH,
    PROMPT_DIR,
    PROJECT_ROOT,
    ROASTS_DIR,
    STATIC_DIR,
    get_boardroom_prompt,
    get_persona,
    load_config,
    save_config,
)

# Re-export session storage
from core.storage import (
    CHATS_DIR,
    delete_chat_session,
    list_chat_sessions,
    load_chat_session,
    save_chat_session,
)

# Re-export connectivity prober
from core.prober import check_connection_live, get_cached_live_status

# Re-export document & diff extractors
from core.extractors import (
    extract_text_from_upload,
    fetch_remote_diff,
    get_git_diff,
)

# Re-export LLM callers
from core.llm import call_llm, stream_llm

# Re-export PDF generators & services
from services.pdf_generator import (
    BoogieManPDF,
    generate_pdf_report,
    render_base64_download_button,
    sanitize_for_pdf,
)
from services.transmute import build_transmutation_prompt, get_boardroom_system_prompt
from services.export_service import render_export_toolbar

__all__ = [
    "CONFIG_DIR",
    "CONFIG_PATH",
    "DEFAULT_CATALOG",
    "PERSONA_PATH",
    "PROMPT_DIR",
    "PROJECT_ROOT",
    "ROASTS_DIR",
    "CHATS_DIR",
    "get_boardroom_prompt",
    "get_persona",
    "load_config",
    "save_config",
    "delete_chat_session",
    "list_chat_sessions",
    "load_chat_session",
    "save_chat_session",
    "check_connection_live",
    "extract_text_from_upload",
    "fetch_remote_diff",
    "get_git_diff",
    "call_llm",
    "stream_llm",
    "BoogieManPDF",
    "generate_pdf_report",
    "render_base64_download_button",
    "sanitize_for_pdf",
]
