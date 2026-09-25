def critic(plan, checks, evidence, conflict):
    if plan.get("needs_clarification"):
        return {"ok": False, "reason": plan.get("clarification") or "Clarification is required."}
    if conflict:
        return {"ok": False, "reason": "Conflicting evidence was detected; the system will not silently choose a side."}
    hard_fail = [x for x in checks if x[1] == "FAIL"]
    if hard_fail:
        return {"ok": False, "reason": "; ".join(f"{x[0]} failed: {x[2]}" for x in hard_fail)}
    if any(x[1] == "WARN" for x in checks) and plan.get("task_type") != "arithmetic":
        return {"ok": False, "reason": "Verification is incomplete; a general factual answer will not be released with unresolved warnings."}
    if not evidence and plan.get("task_type") not in {"arithmetic"}:
        return {"ok": False, "reason": "No evidence supports release."}
    return {"ok": True, "reason": "All release gates passed."}
