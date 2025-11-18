from __future__ import annotations

from typing import Dict, List


def scan_game_text(game_text: List[str], rating: str) -> Dict[str, object]:
    """
    Scan game text lines for simple compliance issues.

    If any line contains the word "forbidden" (case-insensitive), the
    scan returns status="blockers" and includes the offending lines.
    Otherwise, the scan returns status="pass".

    The `rating` parameter is reserved for future use (e.g., ESRB/PEGI
    specific policies).
    """
    offending: List[str] = []
    needle = "forbidden"

    for line in game_text:
        if needle in line.lower():
            offending.append(line)

    if offending:
        return {
            "status": "blockers",
            "offending_lines": offending,
            "rating": rating,
        }

    return {
        "status": "pass",
        "offending_lines": [],
        "rating": rating,
    }

