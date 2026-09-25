from __future__ import annotations

import re
from backend.llm.client import llm


SOLVE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "answer": {"type": "string"},
        "claim": {"type": "string"},
        "uncertainty": {"type": "string"},
    },
    "required": ["answer", "claim", "uncertainty"],
}


def _extract_expression(task: str) -> str | None:
    cleaned = task.strip().rstrip("?!. ")

    # Convert Unicode math operators to ASCII operators
    cleaned = (
        cleaned
        .replace("×", "*")
        .replace("−", "-")
        .replace("–", "-")
        .replace("—", "-")
        .replace("÷", "/")
    )

    # Remove common natural-language prefixes
    cleaned = re.sub(
        r"^\s*(calculate|compute|evaluate|solve)\s*:?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # If the remaining input is a complete arithmetic expression
    if re.fullmatch(r"[\d\s+\-*/%.()]+", cleaned):
        return cleaned

    # Look for an arithmetic expression beginning with parentheses
    start = cleaned.find("(")

    if start != -1:
        candidate = cleaned[start:]

        if re.fullmatch(r"[\d\s+\-*/%.()]+", candidate):
            return candidate

    # Simple arithmetic expression fallback
    matches = re.findall(
        r"\d+(?:\.\d+)?(?:\s*[+\-*/%]\s*\d+(?:\.\d+)?)+",
        cleaned,
    )

    if matches:
        return max(matches, key=len)

    return None


def _offline_factual_answer(task: str, evidence: list[dict]):
    """
    Produce a candidate only when local evidence directly supports it.
    """

    q = task.lower().strip()

    for e in evidence:
        text = e.get("text", "")

        if "capital of india" in q and "capital of india" in text.lower():
            return {
                "answer": "New Delhi is the capital of India.",
                "value": None,
                "claim": "The capital of India is New Delhi.",
                "uncertainty": "",
            }

        if (
            "who invented the world wide web" in q
            or "who invented the web" in q
            or "invented www" in q
        ):
            if "world wide web was invented by" in text.lower():
                return {
                    "answer": text,
                    "value": None,
                    "claim": text,
                    "uncertainty": "",
                }

    return {
        "answer": "No directly supported offline answer was found.",
        "value": None,
        "claim": "",
        "uncertainty": (
            "The available evidence does not contain "
            "a supported answer for this question."
        ),
    }


def solve(task: str, plan: dict, evidence: list[dict]):

    # --------------------------------
    # ARITHMETIC
    # --------------------------------
    if plan["task_type"] == "arithmetic":

        from backend.sandbox.executor import arithmetic

        expression = _extract_expression(task)

        if expression is None:
            return {
                "answer": (
                    "The mathematical expression "
                    "could not be extracted safely."
                ),
                "value": None,
                "expression": "",
                "claim": "",
                "uncertainty": (
                    "Unable to isolate a complete "
                    "arithmetic expression."
                ),
            }

        try:
            value = arithmetic(expression)

            return {
                "answer": f"{expression} = {value:g}",
                "value": value,
                "expression": expression,
                "claim": (
                    f"The value of {expression} is {value:g}."
                ),
                "uncertainty": "",
            }

        except Exception as exc:
            return {
                "answer": (
                    "The arithmetic expression "
                    "could not be evaluated safely."
                ),
                "value": None,
                "expression": expression,
                "claim": "",
                "uncertainty": str(exc),
            }

    # --------------------------------
    # OFFLINE FACTUAL DEMO
    # --------------------------------
    if not llm.enabled:
        return _offline_factual_answer(task, evidence)

    # --------------------------------
    # LLM FACTUAL / REASONING
    # --------------------------------

    context = "\n".join(
        f"[{e['id']}] {e['title']} | "
        f"{e.get('text', '')} | {e.get('url', '')}"
        for e in evidence
    )

    try:
        result, _ = llm.json(
            """You are the solver agent.

Answer only from the supplied task and evidence.
Do not invent facts.

If evidence is insufficient or conflicting, say so.

The verifier, not you, decides whether the answer is releasable.""",
            f"TASK:\n{task}\n\nEVIDENCE:\n{context}",
            SOLVE_SCHEMA,
        )

        return {
            **result,
            "value": None,
        }

    except Exception as exc:
        return {
            "answer": (
                "The solver failed to produce "
                "a trustworthy candidate."
            ),
            "value": None,
            "claim": "",
            "uncertainty": str(exc),
        }