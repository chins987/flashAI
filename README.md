# FlashAI — HackFusion 2026 | Theme 8

## Multi-Agent AI Reasoning & Verification Engine

FlashAI is a **verification-first multi-agent AI reasoning system** designed to reduce hallucinations, unsupported answers, and reasoning errors.

Instead of directly trusting an AI-generated response, FlashAI separates **answer generation from verification** and uses multiple specialized agents to evaluate whether a response should be released.

> **Core Principle:** A plausible AI answer is not treated as proof until it passes independent verification.

---

## 📌 Problem Statement

Modern AI systems can generate answers that appear convincing but may be:

* Factually incorrect
* Unsupported by evidence
* Based on ambiguous input
* Logically inconsistent
* Contradicted by other information
* Incorrect in calculations
* Unsafe to execute or act upon

A major challenge is that the same AI system that generates an answer may also be responsible for judging whether that answer is correct.

FlashAI addresses this problem by introducing a **multi-agent verification pipeline** in which generation and verification are separate stages.

---

## 💡 Solution

FlashAI processes a user request through a sequence of specialized agents:

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

Each stage has a specific responsibility.

If the system cannot establish sufficient confidence in an answer, it does not simply guess. Instead, it can:

* Request clarification
* Trigger self-correction
* Re-run verification
* Detect conflicting evidence
* Hold the response

---

## 🤖 Multi-Agent Architecture

### 1. Planner

Classifies the incoming task and identifies:

* Task type
* Ambiguity
* Whether additional evidence is required
* Whether clarification is necessary

### 2. Researcher

Retrieves relevant evidence and checks for conflicting information.

The Researcher is designed to:

* Ground factual answers in evidence
* Identify conflicting sources
* Expose uncertainty
* Avoid unsupported claims

### 3. Coder / Tool Agent

Handles approved computational tasks through a restricted execution path.

For example:

```text
(3*4)+10
      ↓
Restricted arithmetic evaluator
      ↓
22
```

### 4. Solver

Generates a candidate answer using the task, plan, and available evidence.

### 5. Verifier

Independently evaluates the candidate using multiple checks:

* Computational correctness
* Factual consistency
* Logical consistency
* Evidence grounding
* Contradiction detection
* Safety and tool-use checks

### 6. Critic

Acts as the release gate.

The Critic determines whether the verification results are sufficient for the answer to be released.

### 7. Finalizer

Produces the final system decision:

```text
ACCEPT
HOLD
CLARIFY
```

---

## ✨ Key Features

* **Multi-agent reasoning pipeline**
* **Independent answer verification**
* **Evidence-based factual grounding**
* **Contradiction detection**
* **Self-correction and re-verification**
* **Ambiguity detection**
* **Fail-closed decision making**
* **Restricted arithmetic execution**
* **Safety verification**
* **Audit trail**
* **Curated evaluation suite**
* **Interactive web dashboard**

---

## 🔄 Self-Correction

When verification fails, FlashAI does not immediately release the response.

Instead:

```text
Candidate Answer
       ↓
Verification
       ↓
     FAIL
       ↓
Critic → HOLD
       ↓
Self-Correction
       ↓
Re-run Reasoning
       ↓
Re-verification
       ↓
ACCEPT / HOLD
```

This makes the verification process visible through the application's audit trail.

---

## ⚔️ Contradiction Detection

FlashAI can identify conflicting evidence instead of silently selecting an unsupported answer.

For example, if different evidence sources provide contradictory claims, the system exposes the conflict and prevents an unsupported release.

This is especially important for the hackathon's **reasoning and verification** objective.

---

## 🛡️ Restricted Tool Execution

FlashAI uses a restricted AST-based arithmetic evaluator.

The evaluator:

* Allows approved numeric operations
* Uses Python's AST parser
* Does not use `eval()`
* Does not use `exec()`
* Does not provide arbitrary shell execution
* Does not provide arbitrary file execution

The current evaluator is intentionally limited to arithmetic and should not be considered a general-purpose sandbox.

---

## 🧪 Evaluation

FlashAI includes a curated evaluation suite containing **7 test cases** covering:

| Test Case   | Purpose                     |
| ----------- | --------------------------- |
| Arithmetic  | Computational verification  |
| Factual     | Evidence-grounded reasoning |
| Conflicting | Contradiction handling      |
| Ambiguous   | Clarification handling      |
| Misleading  | Error detection             |
| Unsafe      | Safety verification         |
| Unsupported | Fail-closed behavior        |

Current baseline:

```text
7/7 cases passed
Verification Accuracy: 100.0%
```

> This result represents performance on the project's curated evaluation suite and is **not a claim of 100% real-world AI accuracy**.

Run the evaluation with:

```cmd
.venv\Scripts\python evaluation\run.py
```

---

## 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* JavaScript
* Three.js

### Backend

* Python
* FastAPI
* Uvicorn

### AI / Reasoning

* Multi-agent architecture
* Optional API-backed LLM integration
* Evidence retrieval
* Independent verification

### Security / Execution

* Python AST-based restricted evaluator
* Safety verification layer
* Fail-closed release mechanism

### Testing

* Python smoke tests
* Curated evaluation cases

### Deployment

* Docker
* Docker Compose

---

## 📁 Project Structure

```text
flashAI/
│
├── backend/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── coder.py
│   │   ├── solver.py
│   │   ├── verifier.py
│   │   ├── critic.py
│   │   └── finalizer.py
│   │
│   ├── orchestration/
│   ├── retrieval/
│   ├── sandbox/
│   ├── verification/
│   ├── audit/
│   ├── llm/
│   ├── models.py
│   └── main.py
│
├── frontend/
│   └── index.html
│
├── evaluation/
│   ├── cases/
│   └── run.py
│
├── tests_smoke.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 💻 Setup and Installation

### 1. Clone the repository

```cmd
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd flashAI
```

### 2. Create a virtual environment

```cmd
python -m venv .venv
```

### 3. Activate the environment

Windows:

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

### 5. Start the application

```cmd
python -m uvicorn backend.main:app --reload
```

### 6. Open the application

```text
http://127.0.0.1:8000
```

---

## 🔑 Environment Variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Add the required API configuration if the optional AI/web-search functionality is being used.

**Never commit `.env` or API keys to GitHub.**

---

## 🔌 API

### Health Check

```text
GET /api/health
```

Returns backend status and AI configuration information.

### Submit Task

```text
POST /api/tasks
```

Example request:

```json
{
  "task": "Calculate: (3*4)+10"
}
```

The response contains the final decision together with verification results, evidence, revision information, and the audit trail.

---

## 🗄️ Database

FlashAI currently does **not require a persistent database**.

The current implementation uses project files/local data for:

* Evaluation cases
* Evidence
* Runtime audit information

Therefore, database schema and migration files are not applicable to the current implementation.

---

## 👥 Team

### HackFusion 2026 — Theme 8

**Project:** FlashAI

**Team Name:** `BugBusters`

**Team Members:**

* `Jeevana Sai`
* `Pavan Kumar`
* `Chinmayi BV`
* `Jatish`

---

## 🏁 Conclusion

FlashAI demonstrates a verification-first approach to multi-agent AI systems.

Rather than assuming that generated answers are correct, the system attempts to establish reliability through:

```text
Generation
    ↓
Evidence
    ↓
Independent Verification
    ↓
Contradiction Detection
    ↓
Self-Correction
    ↓
Release Decision
```

The objective is not to claim perfect AI accuracy, but to build a system that **recognizes when an answer cannot be reliably established and avoids presenting uncertainty as fact**.

---

**HackFusion 2026 | Theme 8 — Multi-Agent AI Reasoning & Verification Engine**

**FlashAI**
