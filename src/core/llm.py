"""
LLM Client & Real-Time Streaming Engine.

Dispatches requests and streams response tokens from OpenAI-compatible endpoints
(LM Studio, Ollama, Groq, OpenAI), Google Gemini SSE endpoints, Azure OpenAI, and Anthropic Claude.
"""

from __future__ import annotations

import json
from typing import Any, Generator
import httpx


def stream_llm(
    system_prompt: str,
    user_prompt: str,
    provider: str,
    p_cfg: dict[str, Any],
    temp: float = 0.7,
    chat_history: list[dict[str, str]] | None = None
) -> Generator[str, None, None]:
    """
    Real-time streaming LLM generator.

    Yields:
        str: Incremental text tokens as they stream from the provider.
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_prompt})

    # 1. Google Gemini Streaming API
    if provider == "Google Gemini":
        api_key = p_cfg.get("api_key", "").strip()
        model = p_cfg.get("model", "gemini-2.5-flash").strip()
        if not api_key:
            raise ValueError("Google Gemini API Key is missing. Enter it in the sidebar.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"

        contents: list[dict[str, Any]] = []
        for m in messages:
            if m["role"] == "system":
                continue
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": temp}
        }

        with httpx.Client(timeout=180.0) as client:
            with client.stream("POST", url, json=payload) as resp:
                if resp.status_code != 200:
                    err_msg = resp.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"Gemini API Error ({resp.status_code}): {err_msg}")
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            data = json.loads(data_str)
                            text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                            if text:
                                yield text
                        except Exception:
                            pass
        return

    # 2. Azure OpenAI Service Streaming
    elif provider == "Azure OpenAI":
        endpoint = p_cfg.get("endpoint", "").strip().rstrip("/")
        api_key = p_cfg.get("api_key", "").strip()
        deployment = p_cfg.get("deployment", "gpt-4o").strip()
        api_ver = p_cfg.get("api_version", "2024-02-15-preview").strip()
        if not endpoint or not api_key:
            raise ValueError("Azure Endpoint and API Key are required.")

        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_ver}"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        payload = {"messages": messages, "temperature": temp, "stream": True}

        with httpx.Client(timeout=180.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as resp:
                if resp.status_code != 200:
                    err_msg = resp.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"Azure Error ({resp.status_code}): {err_msg}")
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            text = delta.get("content", "")
                            if text:
                                yield text
                        except Exception:
                            pass
        return

    # 3. Anthropic Claude Messages API Streaming
    elif provider == "Anthropic Claude":
        api_key = p_cfg.get("api_key", "").strip()
        model = p_cfg.get("model", "claude-3-5-sonnet-20241022").strip()
        if not api_key:
            raise ValueError("Anthropic API key is required.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        claude_messages = [m for m in messages if m["role"] != "system"]
        payload = {
            "model": model,
            "system": system_prompt,
            "messages": claude_messages,
            "max_tokens": 4096,
            "temperature": temp,
            "stream": True
        }

        with httpx.Client(timeout=180.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as resp:
                if resp.status_code != 200:
                    err_msg = resp.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"Anthropic Error ({resp.status_code}): {err_msg}")
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            event = json.loads(data_str)
                            ev_type = event.get("type")
                            if ev_type == "content_block_delta":
                                delta_text = event.get("delta", {}).get("text", "")
                                if delta_text:
                                    yield delta_text
                        except Exception:
                            pass
        return

    # 4. Universal OpenAI-Compatible Streaming (LM Studio, Ollama, Groq, OpenAI, Custom)
    else:
        base_url = p_cfg.get("base_url", "http://127.0.0.1:1234/v1").strip().rstrip("/")
        if not base_url.endswith("/v1") and "1234" in base_url:
            base_url = f"{base_url}/v1"
        url = f"{base_url}/chat/completions"

        api_key = p_cfg.get("api_key", "").strip() or "local"
        model = p_cfg.get("model", "local-model").strip()

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "temperature": temp, "stream": True}

        with httpx.Client(timeout=360.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as resp:
                if resp.status_code != 200:
                    err_msg = resp.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"Endpoint Error ({resp.status_code}) at {url}: {err_msg}")
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            text = delta.get("content", "")
                            if text:
                                yield text
                        except Exception:
                            pass


def call_llm(
    system_prompt: str,
    user_prompt: str,
    provider: str,
    p_cfg: dict[str, Any],
    temp: float = 0.7,
    chat_history: list[dict[str, str]] | None = None
) -> str:
    """Synchronous invocation wrapper that aggregates tokens from stream_llm."""
    chunks: list[str] = []
    for chunk in stream_llm(system_prompt, user_prompt, provider, p_cfg, temp, chat_history):
        chunks.append(chunk)
    return "".join(chunks)
