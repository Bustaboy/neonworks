from __future__ import annotations

from neonworks.compliance.scanner import scan_game_text


def test_scan_game_text_pass_when_no_forbidden():
    lines = [
        "Welcome to NeonWorks.",
        "This is a peaceful village.",
        "Nothing problematic happens here.",
    ]

    result = scan_game_text(lines, rating="T")

    assert isinstance(result, dict)
    assert result["status"] == "pass"
    assert result["offending_lines"] == []
    assert result["rating"] == "T"


def test_scan_game_text_blockers_when_forbidden_present():
    lines = [
        "The ancient library holds forbidden knowledge.",
        "Beware of the dark corridors.",
    ]

    result = scan_game_text(lines, rating="M")

    assert isinstance(result, dict)
    assert result["status"] == "blockers"
    assert result["rating"] == "M"
    assert len(result["offending_lines"]) == 1
    assert lines[0] in result["offending_lines"]

