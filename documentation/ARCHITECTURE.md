\# FlashAI Architecture

\## Overview

FlashAI is a multi-agent AI reasoning and verification system. It processes a user task through multiple specialized agents instead of relying on a single AI response.

The system follows a verification-first workflow:

User Task → Planner → Researcher → Solver/Coder → Verifier → Critic → Finalizer

If verification fails, the system can perform self-correction and retry the reasoning process.





\## System Architecture

```text

&#x20;                   ┌─────────────────┐

&#x20;                   │    User Task    │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │     Planner     │

&#x20;                   │ Task Analysis   │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │    Researcher   │

&#x20;                   │ Evidence / Data │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                 ┌──────────────────────┐

&#x20;                 │ Solver / Coder Tool  │

&#x20;                 │ Reasoning / Compute  │

&#x20;                 └──────────┬───────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │     Verifier    │

&#x20;                   │  Independent    │

&#x20;                   │   Verification  │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │      Critic     │

&#x20;                   │  Release Gate   │

&#x20;                   └───────┬─┬───────┘

&#x20;                           │ │

&#x20;                   PASS ───┘ │ └── FAIL / WARN

&#x20;                           │ │

&#x20;                           ▼ ▼

&#x20;                    ┌───────────┐

&#x20;                    │ Finalizer │

&#x20;                    └─────┬─────┘

&#x20;                          │

&#x20;                          ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │  Final Decision │

&#x20;                   │ ACCEPT / HOLD / │

&#x20;                   │    CLARIFY     │

&#x20;                   └─────────────────┘



&#x20;                   FAIL / WARN

&#x20;                        │

&#x20;                        ▼

&#x20;                 ┌─────────────────┐

&#x20;                 │ Self-Correction │

&#x20;                 │   Retry Loop    │

&#x20;                 └────────┬────────┘

&#x20;                          │

&#x20;                          └──────→ Planner

