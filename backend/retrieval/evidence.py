from __future__ import annotations


CORPUS = [

    # =========================================================
    # ARITHMETIC EVIDENCE
    # =========================================================

    {
        "id": "EV-ARITH-001",
        "title": "Restricted arithmetic evaluator",
        "text": (
            "Numeric expressions are evaluated with a restricted "
            "AST parser. Arbitrary Python execution is not allowed."
        ),
        "terms": [
            "calculate",
            "compute",
            "arithmetic",
            "math",
        ],
    },


    # =========================================================
    # INDIA FACTUAL DEMO
    # =========================================================

    {
        "id": "EV-INDIA-001",
        "title": "Capital of India",
        "text": "New Delhi is the capital of India.",
        "terms": [
            "capital of india",
            "capital india",
            "new delhi",
        ],
    },

    {
        "id": "EV-INDIA-002",
        "title": "India",
        "text": "India is a country in South Asia.",
        "terms": [
            "india",
            "country in south asia",
        ],
    },


    # =========================================================
    # WORLD WIDE WEB — NORMAL SOURCE
    # =========================================================

    {
        "id": "EV-WWW-001",
        "title": "World Wide Web",
        "text": (
            "The World Wide Web was invented by Tim Berners-Lee."
        ),
        "terms": [
            "world wide web",
            "invented the web",
            "inventor of the web",
            "invented www",
            "who invented the world wide web",
            "who invented the web",
        ],
    },


    # =========================================================
    # WORLD WIDE WEB — DELIBERATELY CONFLICTING SOURCE
    # =========================================================

    {
        "id": "EV-WWW-CONFLICT-001",
        "title": "Conflicting Web History Claim",
        "text": (
            "This deliberately conflicting demonstration source "
            "claims that the World Wide Web was invented by "
            "a different researcher."
        ),
        "terms": [
            "world wide web",
            "invented the web",
            "inventor of the web",
            "invented www",
            "who invented the world wide web",
            "who invented the web",
        ],
    },


    # =========================================================
    # CONFLICT POLICY
    # =========================================================

    {
        "id": "EV-POLICY-001",
        "title": "Conflict handling policy",
        "text": (
            "When sources disagree, the system exposes the "
            "disagreement and does not silently select an "
            "unsupported side."
        ),
        "terms": [
            "conflict",
            "conflicting",
            "contradiction",
            "disagree",
            "sources disagree",
        ],
    },


    # =========================================================
    # LEGACY ARITHMETIC CONFLICT DEMO
    # Kept so the old test still works.
    # =========================================================

    {
        "id": "EV-CONFLICT-001",
        "title": "Conflicting arithmetic claim",
        "text": (
            "This deliberately unreliable demonstration source "
            "claims that 2 + 2 = 5."
        ),
        "terms": [
            "2 + 2",
            "2+2",
            "two plus two",
        ],
    },

    {
        "id": "EV-ARITH-002",
        "title": "Basic arithmetic fact",
        "text": "Two plus two equals four.",
        "terms": [
            "2 + 2",
            "2+2",
            "two plus two",
        ],
    },

]


def retrieve_local(task: str):

    q = task.lower()

    results = []

    for e in CORPUS:

        if any(term in q for term in e["terms"]):

            results.append(
                {
                    **e,
                    "relevance": 0.8,
                    "supports": None,
                    "url": "",
                    "claim_supported": "",
                }
            )

    return results
