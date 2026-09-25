# FlashAI — HackFusion 2026 | Theme 8

**FlashAI** is a verification-first multi-agent AI reasoning engine designed to reduce hallucinations and unsupported answers through **evidence grounding, independent verification, contradiction detection, self-correction, and fail-closed decisions**.

> **Core idea:** An AI-generated answer is not treated as proof until it passes independent verification.

## 🧠 Architecture

```text
User Task
   ↓
Planner
   ↓
Researcher
   ↓
Coder / Tool
   ↓
Solver
   ↓
Verifier
   ↓
Critic
   ↓
Finalizer
   ↓
ACCEPT / HOLD / CLARIFY
```

### Agents

* **Planner** — classifies the task and detects ambiguity.
* **Researcher** — retrieves evidence and identifies conflicts.
* **Coder / Tool** — performs approved computations through a restricted execution path.
* **Solver** — generates a candidate answer.
* **Verifier** — independently checks the candidate.
* **Critic** — decides whether verification requirements are satisfied.
* **Finalizer** — releases the final decision.

## ✨ Key Features

* **Independent verification** instead of trusting the generator.
* **Evidence grounding** for factual answers.
* **Contradiction detection** when sources disagree.
* **Self-correction and re-verification** after failed checks.
* **Ambiguity detection** with `CLARIFY` instead of guessing.
* **Fail-closed decisions** using `ACCEPT`, `HOLD`, or `CLARIFY`.
* **Restricted arithmetic execution** using an AST-based evaluator.
* **Audit trail** showing the reasoning and verification pipeline.
* **Evaluation suite** for testing reliability across different scenarios.

## 🔧 Major Modifications Made

Compared with the earlier prototype, the current FlashAI version includes:

1. **Renamed the project from VeritasMesh to FlashAI** for consistent project and GitHub branding.
2. **Added the Coder / Tool Agent** as a separate stage in the multi-agent pipeline.
3. **Fixed arithmetic expression handling** so complete expressions such as `(3*4)+10` are evaluated correctly.
4. **Added restricted AST-based computation** instead of unsafe `eval()`/`exec()` execution.
5. **Improved independent verification** with computational, factual, logical, contradiction, and safety checks.
6. **Added self-correction and re-verification** when verification fails.
7. **Improved the audit trail** so judges can see why an answer was accepted or blocked.
8. **Added demonstration cases** for arithmetic, factual reasoning, ambiguity, conflicts, unsupported questions, and unsafe requests.
9. **Added a regression evaluation suite** to measure verification performance.

## 🧪 Evaluation

FlashAI currently includes **7 curated evaluation cases** covering:

* Arithmetic
* Factual reasoning
* Conflicting evidence
* Ambiguous requests
* Misleading input
* Unsafe requests
* Unsupported questions

Current baseline:

```text
7/7 cases passed
Verification Accuracy: 100.0%
```

This is the result on the project's curated test suite and is **not a claim of 100% real-world AI accuracy**.

## 💻 Run Locally

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Run the evaluation:

```cmd
.venv\Scripts\python evaluation\run.py
```

## 🎬 Demo

Recommended demonstrations:

| Input                              | Expected Behavior                      |
| ---------------------------------- | -------------------------------------- |
| `(3*4)+10`                         | `ACCEPT` after independent computation |
| `What is the capital of India?`    | Evidence-grounded answer               |
| `What is the answer to this?`      | `CLARIFY`                              |
| `What is the capital of Atlantis?` | `HOLD` due to missing evidence         |
| Conflicting arithmetic claim       | Contradiction detection                |
| Unsafe request                     | Blocked / `HOLD`                       |

## 🔐 Safety

The built-in arithmetic evaluator is intentionally restricted.

It does **not** use `eval()` or `exec()` and does not provide arbitrary shell, file, or network execution.

For production-grade arbitrary code execution, a separately isolated sandbox with resource, filesystem, and network restrictions would be required.

## 🚀 Future Scope

* PDF/document evidence ingestion
* Larger evidence collections
* Vector-based retrieval
* Source credibility scoring
* Stronger adversarial verification
* Expanded evaluation benchmarks
* Production-grade isolated code execution
* Persistent audit logs and authentication

---

### HackFusion 2026

**Theme 8 — Multi-Agent AI Reasoning & Verification Engine**

**Project: FlashAI**
