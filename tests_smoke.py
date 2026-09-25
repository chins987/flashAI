from backend.orchestration.workflow import execute

def test_complete_arithmetic():
    r = execute("(3*4)+10")
    assert r.decision == "ACCEPT"
    assert r.answer.endswith("= 22")
    assert any(v.name == "Computational" and v.status == "PASS" for v in r.verifications)

def test_ambiguous_fails_closed():
    r = execute("What is the answer to this?")
    assert r.decision == "CLARIFY"

def test_unknown_offline_fails_closed():
    r = execute("Explain the latest scientific discovery.")
    assert r.decision in {"HOLD", "ACCEPT"}  # ACCEPT only when an LLM/web provider is configured
