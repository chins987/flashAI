from __future__ import annotations

from backend.agents.planner import plan
from backend.agents.researcher import research
from backend.agents.solver import solve
from backend.agents.coder import run_tool
from backend.agents.verifier import run
from backend.agents.critic import critic
from backend.agents.finalizer import finalize
from backend.models import TaskResponse, Verification, Evidence
from backend.audit.logger import log


def _is_tool_task(task: str, task_plan: dict) -> bool:
    text = task.lower().strip()

    tool_markers = (
        "use the calculator",
        "use calculator",
        "use the tool",
        "run the tool",
        "tool:",
        "calculate using",
        "compute using",
    )

    return (
        task_plan.get("task_type") == "tool"
        or any(marker in text for marker in tool_markers)
    )


def execute(task: str):
    audit = []

    p = plan(task)

    log(
        audit,
        f"Planner: {p.get('task_type')} | "
        f"clarification={p.get('needs_clarification')} | "
        f"search={p.get('search_needed')}",
    )

    if p.get("needs_clarification"):
        f = finalize(
            task,
            p,
            {"answer": ""},
            [],
            {
                "ok": False,
                "reason": p.get("clarification"),
            },
            0,
        )

        return TaskResponse(
            **f,
            revision=0,
            verifications=[],
            evidence=[],
            audit=audit,
        )

    evidence, conflict, uncertainty = research(task, p)

    log(
        audit,
        f"Researcher: {len(evidence)} evidence item(s); "
        f"conflict={conflict}.",
    )

    if uncertainty:
        log(
            audit,
            f"Researcher note: {uncertainty}",
        )

    tool_result = None

    if _is_tool_task(task, p):
        log(
            audit,
            "Coder/Tool Agent: task routed to restricted sandbox.",
        )

        tool_result = run_tool(task)

        if tool_result.get("success"):
            log(
                audit,
                "Coder/Tool Agent: "
                f"{tool_result.get('expression')} = "
                f"{tool_result.get('result')}",
            )
        else:
            log(
                audit,
                "Coder/Tool Agent: execution blocked - "
                f"{tool_result.get('error')}",
            )

    last_checks = []

    for revision in range(3):
        if tool_result is not None:
            if tool_result.get("success"):
                sol = {
                    "answer": str(tool_result.get("result")),
                    "confidence": 0.99,
                    "method": "restricted_arithmetic_sandbox",
                    "tool_result": tool_result,
                }
            else:
                sol = {
                    "answer": "",
                    "confidence": 0.0,
                    "method": "restricted_arithmetic_sandbox",
                    "tool_result": tool_result,
                }
        else:
            sol = solve(
                task,
                p,
                evidence,
            )

        agent_name = (
            "Coder/Tool Agent"
            if tool_result is not None
            else "Solver"
        )

        log(
            audit,
            f"{agent_name}: candidate generated "
            f"(attempt {revision + 1}).",
        )

        raw = run(
            task,
            p,
            sol,
            evidence,
            conflict,
        )

        last_checks = [
            Verification(
                name=a,
                status=b,
                detail=c,
            )
            for a, b, c in raw
        ]

        critique = critic(
            p,
            raw,
            evidence,
            conflict,
        )

        log(
            audit,
            f"Critic: "
            f"{'PASS' if critique['ok'] else 'HOLD'} - "
            f"{critique['reason']}",
        )

        if critique["ok"]:
            f = finalize(
                task,
                p,
                sol,
                raw,
                critique,
                revision,
            )

            return TaskResponse(
                **f,
                revision=revision,
                verifications=last_checks,
                evidence=[
                    Evidence(
                        id=x["id"],
                        title=x["title"],
                        text=x["text"],
                        relevance=x["relevance"],
                        supports=x.get("supports"),
                        url=x.get("url", ""),
                    )
                    for x in evidence
                ],
                audit=audit,
            )

        if revision < 2:
            log(
                audit,
                "Self-correction: verification failed; "
                "re-running the reasoning and verification loop.",
            )

    return TaskResponse(
        decision="HOLD",
        answer=(
            "No answer was released because independent "
            "verification remained incomplete or failed."
        ),
        confidence=0.0,
        revision=2,
        verifications=last_checks,
        evidence=[
            Evidence(
                id=x["id"],
                title=x["title"],
                text=x["text"],
                relevance=x["relevance"],
                supports=x.get("supports"),
                url=x.get("url", ""),
            )
            for x in evidence
        ],
        audit=audit,
        clarification=(
            "Provide clearer input or stronger evidence, "
            "then re-run verification."
        ),
    )
