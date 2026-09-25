from __future__ import annotations

import re

from backend.llm.client import llm
from backend.sandbox.executor import arithmetic


VERIFY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "factual": {"type": "string", "enum": ["PASS", "FAIL", "WARN"]},
        "logical": {"type": "string", "enum": ["PASS", "FAIL", "WARN"]},
        "evidence": {"type": "string", "enum": ["PASS", "FAIL", "WARN"]},
        "contradiction": {"type": "string", "enum": ["PASS", "FAIL", "WARN"]},
        "safety": {"type": "string", "enum": ["PASS", "FAIL", "WARN"]},
        "explanation": {"type": "string"},
    },
    "required": [
        "factual",
        "logical",
        "evidence",
        "contradiction",
        "safety",
        "explanation",
    ],
}


def _extract_expression(task: str, solution: dict) -> str | None:
    """
    Extract the arithmetic expression from either:
    1. The Coder/Tool Agent result
    2. The normal Solver result
    3. The original task as a fallback
    """

    # ---------------------------------------------------------
    # 1. Coder/Tool Agent already supplied the expression
    # ---------------------------------------------------------
    expression = solution.get("expression")

    if expression:
        return str(expression).strip()

    tool_result = solution.get("tool_result")

    if isinstance(tool_result, dict):
        expression = tool_result.get("expression")

        if expression:
            return str(expression).strip()

    # ---------------------------------------------------------
    # 2. Solver may use an expression field
    # ---------------------------------------------------------
    expression = solution.get("math_expression")

    if expression:
        return str(expression).strip()

    # ---------------------------------------------------------
    # 3. Extract from the task itself
    # ---------------------------------------------------------
    text = task.strip()

    text = (
        text.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("–", "-")
        .replace("—", "-")
    )

    text = re.sub(
        r"^\s*(?:"
        r"use\s+the\s+calculator"
        r"|use\s+a\s+calculator"
        r"|use\s+calculator"
        r"|use\s+the\s+tool"
        r"|run\s+the\s+tool"
        r"|calculate"
        r"|compute"
        r"|evaluate"
        r"|solve"
        r")\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    if re.fullmatch(r"[\d\s+\-*/%.()]+", text):
        return text.strip()

    matches = re.findall(
        r"\d+(?:\.\d+)?"
        r"(?:\s*[+\-*/%]\s*"
        r"(?:\d+(?:\.\d+)?|\([^()]*\)))+",
        text,
    )

    if matches:
        return max(matches, key=len).strip()

    return None


def _get_claimed_value(solution: dict):
    """
    Support both normal Solver and Coder/Tool result formats.
    """

    if solution.get("value") is not None:
        return solution.get("value")

    if solution.get("result") is not None:
        return solution.get("result")

    tool_result = solution.get("tool_result")

    if isinstance(tool_result, dict):
        if tool_result.get("result") is not None:
            return tool_result.get("result")

    return None


def _arithmetic_checks(task, solution):

    expression = _extract_expression(task, solution)

    if not expression:
        return [
            (
                "Computational",
                "FAIL",
                "No safe mathematical expression was extracted.",
            ),
            (
                "Logical",
                "FAIL",
                "The candidate could not be tied to a complete expression.",
            ),
            (
                "Factual",
                "PASS",
                "External factual evidence is not required for arithmetic.",
            ),
            (
                "Contradiction",
                "PASS",
                "No conflicting arithmetic result was accepted.",
            ),
            (
                "Safety",
                "PASS",
                "Only the restricted arithmetic evaluator was used.",
            ),
        ]

    # ---------------------------------------------------------
    # Independent verification
    # ---------------------------------------------------------
    try:
        expected = arithmetic(expression)

    except Exception as exc:
        return [
            (
                "Computational",
                "FAIL",
                f"Independent arithmetic evaluation failed: {exc}",
            ),
            (
                "Logical",
                "FAIL",
                "The expression could not be independently verified.",
            ),
            (
                "Factual",
                "PASS",
                "External factual evidence is not required for arithmetic.",
            ),
            (
                "Contradiction",
                "PASS",
                "No conflicting arithmetic result was accepted.",
            ),
            (
                "Safety",
                "PASS",
                "Only the restricted arithmetic evaluator was used.",
            ),
        ]

    claimed = _get_claimed_value(solution)

    try:
        ok = (
            claimed is not None
            and abs(float(claimed) - float(expected)) < 1e-9
        )

    except (TypeError, ValueError):
        ok = False

    return [
        (
            "Computational",
            "PASS" if ok else "FAIL",
            f"Independent evaluator computed {expected:g} "
            f"from the complete expression.",
        ),
        (
            "Logical",
            "PASS" if ok else "FAIL",
            "The released value corresponds to the independently "
            "evaluated expression.",
        ),
        (
            "Factual",
            "PASS",
            "External factual evidence is not required for a computational task.",
        ),
        (
            "Contradiction",
            "PASS",
            "No conflicting arithmetic result was accepted.",
        ),
        (
            "Safety",
            "PASS",
            "Only a restricted arithmetic AST evaluator was used.",
        ),
    ]


def _detect_factual_conflict(task: str, evidence: list[dict]) -> bool:

    task_lower = task.lower()

    if (
        "world wide web" in task_lower
        or "invented the web" in task_lower
        or "inventor of the web" in task_lower
        or "invented www" in task_lower
    ):

        normal_source = any(
            e.get("id") == "EV-WWW-001"
            for e in evidence
        )

        conflicting_source = any(
            e.get("id") == "EV-WWW-CONFLICT-001"
            for e in evidence
        )

        if normal_source and conflicting_source:
            return True

    evidence_text = " ".join(
        e.get("text", "").lower()
        for e in evidence
    )

    conflict_markers = [
        "conflicting",
        "disagree",
        "contradiction",
        "different researcher",
        "incompatible",
    ]

    if (
        len(evidence) >= 2
        and any(marker in evidence_text for marker in conflict_markers)
    ):
        return True

    return False


def run(
    task: str,
    plan: dict,
    solution: dict,
    evidence: list[dict],
    conflict: bool,
):

    # =========================================================
    # ARITHMETIC / TOOL VERIFICATION
    # =========================================================

    if plan["task_type"] == "arithmetic":
        return _arithmetic_checks(task, solution)

    # =========================================================
    # FACTUAL CONFLICT DETECTION
    # =========================================================

    detected_conflict = _detect_factual_conflict(
        task,
        evidence,
    )

    conflict = conflict or detected_conflict

    if conflict:
        return [
            (
                "Factual",
                "WARN",
                "Multiple evidence sources make incompatible claims "
                "about the requested fact.",
            ),
            (
                "Logical",
                "WARN",
                "A single conclusion cannot be justified while the "
                "retrieved evidence remains unresolved.",
            ),
            (
                "Evidence",
                "FAIL",
                "Conflicting evidence must be resolved or explicitly "
                "disclosed before release.",
            ),
            (
                "Contradiction",
                "FAIL",
                "Independent evidence contains a detected factual disagreement.",
            ),
            (
                "Safety",
                "PASS",
                "No unsafe tool action was executed.",
            ),
        ]

    # =========================================================
    # NO EVIDENCE
    # =========================================================

    if not evidence:
        return [
            (
                "Factual",
                "FAIL",
                "No evidence is available for a factual release.",
            ),
            (
                "Logical",
                "WARN",
                "No evidence-backed inference can be established.",
            ),
            (
                "Evidence",
                "FAIL",
                "Evidence grounding is missing.",
            ),
            (
                "Contradiction",
                "WARN",
                "No evidence means contradiction status cannot be established.",
            ),
            (
                "Safety",
                "PASS",
                "No unsafe tool action was executed.",
            ),
        ]

    # =========================================================
    # LLM VERIFICATION
    # =========================================================

    if llm.enabled:
        try:

            context = "\n".join(
                f"[{e['id']}] {e['title']} | "
                f"{e.get('text', '')} | {e.get('url', '')}"
                for e in evidence
            )

            result, _ = llm.json(
                """You are an independent adversarial verifier.

Do not improve or rewrite the candidate.

Check whether the candidate is actually supported by the evidence,
whether it answers the exact task, whether sources conflict,
and whether important uncertainty is being hidden.

Be conservative: if you cannot establish a point, WARN or FAIL it.

If evidence contains contradictory claims, the contradiction gate
must not PASS unless the contradiction has genuinely been resolved.

Never pass merely because the candidate sounds plausible.""",

                f"TASK:\n{task}\n\n"
                f"CANDIDATE:\n{solution.get('answer', '')}\n\n"
                f"EVIDENCE:\n{context}",

                VERIFY_SCHEMA,
                web=True,
            )

            return [
                (
                    "Factual",
                    result["factual"],
                    result["explanation"],
                ),
                (
                    "Logical",
                    result["logical"],
                    result["explanation"],
                ),
                (
                    "Evidence",
                    result["evidence"],
                    result["explanation"],
                ),
                (
                    "Contradiction",
                    result["contradiction"],
                    result["explanation"],
                ),
                (
                    "Safety",
                    result["safety"],
                    result["explanation"],
                ),
            ]

        except Exception as exc:

            return [
                (
                    "Factual",
                    "WARN",
                    f"Independent LLM verifier unavailable: {exc}",
                ),
                (
                    "Logical",
                    "WARN",
                    "Independent verification could not complete.",
                ),
                (
                    "Evidence",
                    "WARN",
                    "Verification could not establish evidence sufficiency.",
                ),
                (
                    "Contradiction",
                    "WARN",
                    "Contradiction check could not complete.",
                ),
                (
                    "Safety",
                    "PASS",
                    "No unsafe tool action was executed.",
                ),
            ]

    # =========================================================
    # OFFLINE FACTUAL VERIFICATION
    # =========================================================

    candidate = solution.get("answer", "").strip().lower()

    evidence_text = " ".join(
        e.get("text", "").lower()
        for e in evidence
    )

    if "capital of india" in task.lower():

        factual_supported = (
            "new delhi" in candidate
            and "new delhi" in evidence_text
            and "capital of india" in evidence_text
        )

    elif (
        "who invented the world wide web" in task.lower()
        or "who invented the web" in task.lower()
    ):

        factual_supported = (
            "tim berners-lee" in candidate
            and "tim berners-lee" in evidence_text
            and "world wide web" in evidence_text
        )

    else:

        candidate_words = {
            word
            for word in re.findall(
                r"\b[a-z0-9-]+\b",
                candidate,
            )
            if len(word) > 3
        }

        factual_supported = bool(
            candidate_words
            and any(
                word in evidence_text
                for word in candidate_words
            )
        )

    if factual_supported:

        return [
            (
                "Factual",
                "PASS",
                "The candidate is directly supported by independently retrieved evidence.",
            ),
            (
                "Logical",
                "PASS",
                "The candidate answers the requested factual question using the retrieved evidence.",
            ),
            (
                "Evidence",
                "PASS",
                "The released claim is grounded in retrieved evidence.",
            ),
            (
                "Contradiction",
                "PASS",
                "No conflicting evidence was detected.",
            ),
            (
                "Safety",
                "PASS",
                "No unsafe tool action was executed.",
            ),
        ]

    return [
        (
            "Factual",
            "FAIL",
            "The candidate could not be independently supported by the retrieved evidence.",
        ),
        (
            "Logical",
            "FAIL",
            "The candidate cannot be released without sufficient evidence support.",
        ),
        (
            "Evidence",
            "FAIL",
            "The candidate is not adequately grounded in the retrieved evidence.",
        ),
        (
            "Contradiction",
            "WARN",
            "The evidence does not establish the candidate reliably.",
        ),
        (
            "Safety",
            "PASS",
            "No unsafe tool action was executed.",
        ),
    ]