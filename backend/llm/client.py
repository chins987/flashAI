"""Optional LLM gateway.

The application remains runnable without an API key. When OPENAI_API_KEY is set,
agent roles use the OpenAI Responses API. Structured JSON is validated locally
before it is trusted by the orchestration layer.
"""
from __future__ import annotations

import json
import os
from typing import Any

try:
    from openai import OpenAI
except Exception:  # optional dependency / offline mode
    OpenAI = None


class LLMUnavailable(RuntimeError):
    pass


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("VERITASMESH_MODEL", "gpt-5.6-luna").strip()
        self.enabled = bool(self.api_key and OpenAI)
        self.client = OpenAI(api_key=self.api_key) if self.enabled else None

    def text(self, instructions: str, prompt: str, *, web: bool = False) -> tuple[str, list[dict[str, Any]]]:
        if not self.enabled or self.client is None:
            raise LLMUnavailable("OPENAI_API_KEY is not configured.")
        tools = [{"type": "web_search"}] if web else None
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": 3000,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["include"] = ["web_search_call.action.sources"]
        response = self.client.responses.create(**kwargs)
        sources: list[dict[str, Any]] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) != "web_search_call":
                continue
            action = getattr(item, "action", None)
            for src in getattr(action, "sources", []) or []:
                url = getattr(src, "url", None)
                if url:
                    sources.append({"url": url})
        return response.output_text, sources

    def json(self, instructions: str, prompt: str, schema: dict[str, Any], *, web: bool = False) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        if not self.enabled or self.client is None:
            raise LLMUnavailable("OPENAI_API_KEY is not configured.")
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": 4000,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "veritasmesh_agent_output",
                    "schema": schema,
                    "strict": True,
                }
            },
        }
        if web:
            kwargs["tools"] = [{"type": "web_search"}]
            kwargs["include"] = ["web_search_call.action.sources"]
        response = self.client.responses.create(**kwargs)
        raw = response.output_text
        data = json.loads(raw)
        sources: list[dict[str, Any]] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) != "web_search_call":
                continue
            action = getattr(item, "action", None)
            for src in getattr(action, "sources", []) or []:
                url = getattr(src, "url", None)
                if url:
                    sources.append({"url": url})
        return data, sources


llm = LLMClient()
