from __future__ import annotations

import re
from backend.llm.client import llm, LLMUnavailable

PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "task_type": {
            "type": "string",
            "enum": [
                "arithmetic",
                "factual",
                "reasoning",
                "safety",
                "ambiguous",
                "unsupported",
            ],
        },
        "needs_clarification": {"type": "boolean"},
        "clarification": {"type": "string"},
        "search_needed": {"type": "boolean"},
        "risk_level": {
            "type": "string",
            "enum": ["low", "medium", "high"],
        },
    },
    "required": [
        "task_type",
        "needs_clarification",
        "clarification",
        "search_needed",
        "risk_level",
    ],
}


def _looks_like_arithmetic(t: str) -> bool:
    """
    Detect mathematical tasks without requiring the entire question
    to consist only of mathematical symbols.

    Examples:
        15 + 27
        What is 15 + 27?
        Calculate 10 * 5
        Find the value of (3 * 4) + 10
        A product costs 1000 and has a 10% discount.
    """

    lower = t.lower()

    # Direct mathematical expression.
    if re.fullmatch(r"[\d\s+\-*/%.()]+", t):
        return True

    # Strong mathematical instruction words.
    math_words = [
        "calculate",
        "compute",
        "evaluate",
        "solve",
        "find the value",
        "what is the value",
        "how much",
        "how many",
        "average speed",
        "percentage",
        "percent",
        "discount",
        "profit",
        "loss",
        "total",
        "remaining",
        "distance",
        "speed",
        "rate",
    ]

    has_math_word = any(word in lower for word in math_words)

    # Mathematical operators or numeric quantities.
    has_number = bool(re.search(r"\d", t))
    has_operator = bool(re.search(r"[+\-*/%]", t))

    # Natural-language arithmetic problem.
    if has_math_word and has_number:
        return True

    # Questions such as "What is 15 + 27?"
    if has_number and has_operator:
        return True

    return False


def plan(task: str) -> dict:
    t = task.strip()

    if not t:
        return {
            "task_type": "ambiguous",
            "needs_clarification": True,
            "clarification": "Please provide a task or question.",
            "search_needed": False,
            "risk_level": "low",
        }

    # Detect computational tasks before sending them into
    # the general factual/reasoning pipeline.
    if _looks_like_arithmetic(t):
        return {
            "task_type": "arithmetic",
            "needs_clarification": False,
            "clarification": "",
            "search_needed": False,
            "risk_level": "low",
        }

    if llm.enabled:
        try:
            result, _ = llm.json(
                """You are the planning agent in a verification-first system.
Do not solve the user's task.

Classify the task accurately.

Use:
- arithmetic for calculations and mathematical word problems
- factual for claims requiring factual evidence
- reasoning for logical/deductive questions
- safety for safety-sensitive requests
- ambiguous when required information or references are genuinely missing
- unsupported only when the system cannot reliably classify the request

If a required referent, quantity, scope, date, jurisdiction, or objective
is genuinely missing, set needs_clarification=true.

Do not invent missing details.

Current/factual claims normally require web evidence.
High-risk requests require conservative handling.

Return only the requested JSON.""",
                task,
                PLAN_SCHEMA,
            )
            return result

        except Exception:
            pass

    # Safe offline fallback.
    vague = [
        "it",
        "this",
        "that",
        "they",
        "them",
        "above",
        "previous",
        "earlier",
    ]

    if any(
        re.search(rf"\b{re.escape(x)}\b", t, re.I)
        for x in vague
    ):
        return {
            "task_type": "ambiguous",
            "needs_clarification": True,
            "clarification": (
                "The request contains a reference whose meaning "
                "is not available from the task alone."
            ),
            "search_needed": False,
            "risk_level": "low",
        }

    return {
        "task_type": "unsupported",
        "needs_clarification": False,
        "clarification": "",
        "search_needed": True,
        "risk_level": "medium",
    }