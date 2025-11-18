from __future__ import annotations

from neonworks.agents.auditor import Auditor


def test_run_test_plan_returns_required_keys():
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
    assert isinstance(result["reason"], str)
    assert isinstance(result["steps_taken"], list)
    assert isinstance(result["bugs"], list)


def test_run_test_plan_steps_taken_structure():
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

