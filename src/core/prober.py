"""
Connection Health Prober for AI Providers.

Tests live connectivity, credentials, and model endpoints for local and cloud AI engines:
LM Studio, Ollama, Google Gemini, OpenAI, Groq, Anthropic Claude, and Azure OpenAI.
Includes in-memory time-to-live (TTL) status caching.
"""

from __future__ import annotations

import time
from typing import Any
import httpx


def check_connection_live(provider: str, p_cfg: dict[str, Any]) -> tuple[bool, str]:
    """
    Probe the selected AI provider endpoint to verify connectivity and authentication.

    Returns:
        tuple[bool, str]: (is_connected, descriptive_status_badge)
    """
    if not provider or not p_cfg:
        return False, "Not configured"

    # 1. LM Studio Local Engine Probe
    if provider == "LM Studio (Local)":
        base = p_cfg.get("base_url", "http://127.0.0.1:1234/v1").rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{base}/models")
                if res.status_code == 200:
                    models = res.json().get("data", [])
                    m_names = [m.get("id") for m in models if "id" in m]
                    m_label = f" ({m_names[0]})" if m_names else ""
                    return True, f"Live & Connected{m_label}"
                return False, f"HTTP {res.status_code}"
        except Exception:
            return False, "Server Offline (Start LM Studio on 127.0.0.1:1234)"

    # 2. Ollama Local Engine Probe
    elif provider == "Ollama (Local)":
        base = p_cfg.get("base_url", "http://127.0.0.1:11434/v1").rstrip("/")
        root_url = base.replace("/v1", "")
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{root_url}/api/tags")
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    m_names = [m.get("name") for m in models if "name" in m]
                    m_label = f" ({m_names[0]})" if m_names else ""
                    return True, f"Live & Connected{m_label}"
                return False, f"HTTP {res.status_code}"
        except Exception:
            return False, "Server Offline (Start Ollama on 127.0.0.1:11434)"

    # 3. Google Gemini Authentication Probe
    elif provider == "Google Gemini":
        key = p_cfg.get("api_key", "").strip()
        if not key:
            return False, "API Key Required"
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
                if res.status_code == 200:
                    return True, "Authenticated"
                return False, f"Auth Error ({res.status_code})"
        except Exception:
            return False, "Network Unreachable"

    # 4. Standard Cloud Providers (Key Presence Check)
    elif provider in ["OpenAI", "Groq", "Anthropic Claude", "Azure OpenAI"]:
        key = p_cfg.get("api_key", "").strip()
        if not key:
            return False, "API Key Required"
        return True, "Key Stored"

    # 5. Custom OpenAI-Compatible Endpoint
    elif provider == "Custom OpenAI-Compatible":
        base = p_cfg.get("base_url", "").strip().rstrip("/")
        if not base:
            return False, "Base URL Required"
        return True, "Endpoint Set"

    return False, "Unverified"


def get_cached_live_status(
    cache_store: dict[str, Any],
    provider_name: str,
    provider_data: dict[str, Any],
    force_refresh: bool = False,
    ttl_seconds: float = 45.0
) -> tuple[bool, str]:
    """
    Retrieve live connectivity status for an AI provider from cache,
    or probe the provider endpoint if cache expired or force_refresh is requested.

    Args:
        cache_store: Dictionary used for storing probe results (e.g. st.session_state.probe_cache).
        provider_name: Name of the AI provider in DEFAULT_CATALOG.
        provider_data: Provider configuration dictionary containing base_url/api_key.
        force_refresh: Whether to bypass cache and probe immediately.
        ttl_seconds: Time-to-live for cache entries in seconds (default 45s).

    Returns:
        tuple[bool, str]: (is_live, status_description)
    """
    cached_entry = cache_store.get(provider_name)
    now = time.time()

    if force_refresh or not cached_entry or (now - cached_entry.get("timestamp", 0) > ttl_seconds):
        is_live, desc = check_connection_live(provider_name, provider_data)
        cache_store[provider_name] = {"is_live": is_live, "desc": desc, "timestamp": now}
        return is_live, desc

    return cached_entry["is_live"], cached_entry["desc"]
