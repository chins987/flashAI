from __future__ import annotations
from backend.llm.client import llm, LLMUnavailable
from backend.retrieval.evidence import retrieve_local

RESEARCH_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "claims": {"type": "array", "items": {"type": "string"}},
        "evidence": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "title": {"type": "string"}, "url": {"type": "string"},
                "claim_supported": {"type": "string"}, "snippet": {"type": "string"},
                "supports": {"type": "boolean"}
            },
            "required": ["title", "url", "claim_supported", "snippet", "supports"]
        }},
        "conflict": {"type": "boolean"},
        "uncertainty": {"type": "string"}
    },
    "required": ["claims", "evidence", "conflict", "uncertainty"]
}


def research(task: str, plan: dict):
    local = retrieve_local(task)
    if llm.enabled and plan.get("search_needed"):
        try:
            result, sources = llm.json(
                """You are the evidence-research agent. Find evidence, not an answer.
Use web search when needed. Prefer primary/authoritative sources. Separate what a source says from your own interpretation.
Never treat a search snippet or unsupported assertion as proof. Report conflicting evidence explicitly.
Every evidence item must have a real source URL. If reliable evidence cannot be established, return an empty evidence list.
Do not fabricate URLs, quotations, facts, or source contents.""",
                task,
                RESEARCH_SCHEMA,
                web=True,
            )
            ev = []
            for i, e in enumerate(result.get("evidence", []), 1):
                ev.append({
                    "id": f"WEB-{i:03d}", "title": e["title"], "text": e["snippet"],
                    "relevance": 0.9, "supports": e["supports"], "url": e["url"],
                    "claim_supported": e["claim_supported"],
                })
            # Keep a source URL even if the model omitted it but the tool returned one.
            known = {x.get("url") for x in ev}
            for i, s in enumerate(sources, 1):
                if s["url"] not in known:
                    ev.append({"id": f"WEB-SRC-{i:03d}", "title": "Web source", "text": "Source returned by web search; inspect before relying on it.", "relevance": 0.5, "supports": None, "url": s["url"], "claim_supported": ""})
            return ev, bool(result.get("conflict")), result.get("uncertainty", "")
        except Exception as exc:
            return local, False, f"Live research unavailable: {exc}"
    return local, False, ""
