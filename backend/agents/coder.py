from __future__ import annotations

import re
from backend.sandbox.executor import arithmetic


class CoderToolAgent:
    """
    Restricted Coder/Tool Agent.

    Converts computation requests into a safe tool plan and
    executes only through the restricted arithmetic sandbox.

    No eval()
    No exec()
    No shell commands
    No file access
    No network access
    """

    TOOL_NAME = "restricted_arithmetic_sandbox"

    def _extract_expression(self, task: str) -> str | None:
        text = task.strip()

        # Normalize mathematical symbols
        text = (
            text.replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("–", "-")
            .replace("—", "-")
        )

        # Remove common instruction prefixes.
        prefixes = [
            r"use\s+the\s+calculator",
            r"use\s+a\s+calculator",
            r"use\s+calculator",
            r"use\s+the\s+tool",
            r"run\s+the\s+tool",
            r"calculate",
            r"compute",
            r"evaluate",
            r"solve",
        ]

        prefix_pattern = (
            r"^\s*(?:"
            + "|".join(prefixes)
            + r")\s*:?\s*"
        )

        text = re.sub(
            prefix_pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

        # If the remaining text is a complete arithmetic expression,
        # return it directly.
        if re.fullmatch(r"[\d\s+\-*/%.()]+", text):
            return text.strip()

        # Otherwise look for a balanced parenthesized arithmetic
        # expression inside the sentence.
        parenthesized = re.findall(
            r"\([^()]*\)"
            r"(?:\s*[+\-*/%]\s*"
            r"(?:\d+(?:\.\d+)?|\([^()]*\)))*",
            text,
        )

        if parenthesized:
            candidate = max(parenthesized, key=len)

            # Include arithmetic immediately surrounding the
            # parenthesized expression when present.
            candidate = candidate.strip()

            return candidate

        # Fallback for simple expressions inside a sentence.
        matches = re.findall(
            r"\d+(?:\.\d+)?"
            r"(?:\s*[+\-*/%]\s*"
            r"\d+(?:\.\d+)?)+",
            text,
        )

        if matches:
            return max(matches, key=len).strip()

        return None

    def create_tool_plan(self, task: str) -> dict:
        expression = self._extract_expression(task)

        if expression is None:
            return {
                "approved": False,
                "tool": self.TOOL_NAME,
                "operation": "arithmetic",
                "expression": "",
                "reason": (
                    "Could not isolate a complete safe "
                    "arithmetic expression."
                ),
            }

        return {
            "approved": True,
            "tool": self.TOOL_NAME,
            "operation": "arithmetic",
            "expression": expression,
            "reason": "Safe arithmetic expression extracted.",
        }

    def execute(self, task: str) -> dict:
        plan = self.create_tool_plan(task)

        if not plan["approved"]:
            return {
                **plan,
                "success": False,
                "result": None,
                "error": plan["reason"],
            }

        try:
            result = arithmetic(plan["expression"])

            return {
                **plan,
                "success": True,
                "result": result,
                "error": "",
            }

        except Exception as exc:
            return {
                **plan,
                "success": False,
                "result": None,
                "error": str(exc),
            }


coder_tool = CoderToolAgent()


def run_tool(task: str) -> dict:
    return coder_tool.execute(task)