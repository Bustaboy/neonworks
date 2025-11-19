from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class TestRunner(Protocol):
    """
    Protocol for pluggable test runners used by the Auditor.

    A runner is responsible for executing a test plan and returning a
    raw result dictionary. The Auditor normalizes this into a stable
    output schema.
    """

    def run(self, plan: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - interface only
        """Execute a test plan and return a raw result dictionary."""
        ...


@dataclass
class Auditor:
    """
    Evaluates automated test plans against the game.

    For now this behaves as a stub implementation by default that
    simply echoes back high-level information from the provided plan.
    When constructed with a `runner`, it delegates execution to that
    runner and normalizes the result into a stable schema. Future
    versions will integrate with vision-based playtesting and
    in-engine probes.
    """

    runner: TestRunner | None = None

    def run_test_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a test plan and return a structured result.

        Behavior:
        - If a runner is configured, delegate to runner.run(plan) and
          normalize the returned dict into the standard schema.
        - If no runner is configured, fall back to the deterministic
          stub behavior (no real execution).

        Returns a dict with keys:
          - result: "pass" or "fail" (stub always "pass")
          - reason: human-readable explanation
          - steps_taken: list of step summaries
          - bugs: list of discovered issues (stub empty)

        TODO: Connect to automated, vision-based playtesting harness that
        can drive the game, record video, and detect anomalies.
        TODO: Integrate with in-engine instrumentation (logs, metrics,
        assertions) to surface subtle logic bugs.
        """
        # Runner-backed execution path
        if self.runner is not None:
            raw = self.runner.run(plan)

            result_value = raw.get("result", "pass")
            reason_value = raw.get("reason", "")
            bugs_value = raw.get("bugs", [])

            steps_taken: List[Dict[str, Any]] = []
            raw_steps = raw.get("steps_taken") or raw.get("steps") or plan.get("steps")

            if isinstance(raw_steps, list):
                for index, step in enumerate(raw_steps):
                    if isinstance(step, dict):
                        description = (
                            step.get("description")
                            or step.get("name")
                            or f"step_{index}"
                        )
                        status = step.get("status", "unknown")
                    else:
                        description = str(step)
                        status = "unknown"

                    steps_taken.append(
                        {
                            "index": index,
                            "description": description,
                            "status": status,
                        }
                    )

            return {
                "result": result_value,
                "reason": reason_value,
                "steps_taken": steps_taken,
                "bugs": bugs_value,
            }

        # Stub-only behavior (original implementation)
        steps: List[Dict[str, Any]] = []

        raw_steps = plan.get("steps") if isinstance(plan, dict) else None
        if isinstance(raw_steps, list):
            for index, step in enumerate(raw_steps):
                if isinstance(step, dict):
                    description = step.get("description") or step.get("name") or f"step_{index}"
                else:
                    description = str(step)

                steps.append(
                    {
                        "index": index,
                        "description": description,
                        "status": "skipped",  # No real execution yet
                    }
                )

        result: Dict[str, Any] = {
            "result": "pass",
            "reason": "Auditor stub did not execute tests; this is a placeholder result.",
            "steps_taken": steps,
            "bugs": [],
        }

        return result
