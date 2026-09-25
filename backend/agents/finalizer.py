def finalize(task, plan, solution, checks, critique, revision):
    if plan.get("needs_clarification"):
        return {"decision": "CLARIFY", "answer": "I need clarification before giving a reliable answer.", "confidence": 0.0, "clarification": plan.get("clarification")}
    if not critique["ok"]:
        return {"decision": "HOLD", "answer": "I will not release an answer because the verification gates did not establish sufficient reliability.", "confidence": 0.0, "clarification": critique["reason"]}
    # Confidence is a gate-derived estimate, never a model's self-reported probability.
    confidence = 0.99 if plan.get("task_type") == "arithmetic" else 0.90
    return {"decision": "ACCEPT", "answer": solution["answer"], "confidence": confidence, "clarification": None}
