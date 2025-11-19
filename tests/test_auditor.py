from __future__ import annotations

from typing import Any, Dict, List

from neonworks.agents.auditor import Auditor, TestRunner


def test_run_test_plan_stub_returns_required_keys():
    """Default stub behavior should match the original schema and semantics."""
    auditor = Auditor()

    test_plan = {
        "name": "Sample Plan",
        "steps": [
            {"name": "Load main menu"},
            {"description": "Start new game"},
            {"description": "Play first quest"},
        ],
    }

    result = auditor.run_test_plan(test_plan)

    assert isinstance(result, dict)
    for key in ("result", "reason", "steps_taken", "bugs"):
        assert key in result

    assert result["result"] in ("pass", "fail")
    assert result["result"] == "pass"
    assert isinstance(result["reason"], str)
    assert "placeholder" in result["reason"]
    assert isinstance(result["steps_taken"], list)
    assert isinstance(result["bugs"], list)


def test_run_test_plan_stub_steps_taken_structure():
    """Stub behavior should continue to build deterministic steps_taken entries."""
    auditor = Auditor()

    test_plan = {
        "steps": [
            {"description": "Step A"},
            {"name": "Step B"},
            "Raw step C",
        ]
    }

    result = auditor.run_test_plan(test_plan)
    steps = result["steps_taken"]

    assert len(steps) == 3

    for idx, step in enumerate(steps):
        assert isinstance(step, dict)
        assert step["index"] == idx
        assert "description" in step
        assert "status" in step
        assert step["status"] == "skipped"


class FakeRunner(TestRunner):
    """Simple fake TestRunner used to exercise runner-backed behavior."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def run(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        self.calls.append(plan)
        return {
            "result": "fail",
            "reason": "One or more steps failed",
            "steps_taken": [
                {"name": "step_one", "status": "ok"},
                {"description": "step_two", "status": "failed"},
            ],
            "bugs": [{"id": "BUG-1", "title": "Sample bug"}],
        }


def test_run_test_plan_with_runner_normalizes_result():
    """When a runner is provided, Auditor should delegate and normalize its output."""
    fake_runner = FakeRunner()
    auditor = Auditor(runner=fake_runner)

    test_plan = {
        "name": "Plan With Runner",
        "steps": [{"description": "runner_step"}],
    }

    result = auditor.run_test_plan(test_plan)

    # Ensure runner was called
    assert fake_runner.calls and fake_runner.calls[0]["name"] == "Plan With Runner"

    # Normalized schema
    assert result["result"] == "fail"
    assert result["reason"] == "One or more steps failed"
    assert isinstance(result["steps_taken"], list)
    assert isinstance(result["bugs"], list)

    # Steps normalized to index/description/status
    assert len(result["steps_taken"]) == 2
    step0, step1 = result["steps_taken"]

    assert step0["index"] == 0
    assert step0["description"] in ("step_one", "step_one".capitalize())
    assert step0["status"] == "ok"

    assert step1["index"] == 1
    assert "step_two" in step1["description"]
    assert step1["status"] == "failed"
