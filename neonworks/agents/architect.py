from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from neonworks.bible.schema import Graph

from .llm_backend import LLMBackend


@dataclass
class Architect:
    """
    Generates a concrete project skeleton from a Bible graph.

    For now this uses simple deterministic transforms from the in-memory
    Graph into JSON files on disk. The LLM backend is injected so that
    future versions can delegate narrative or content synthesis without
    changing the public API.
    """

    backend: LLMBackend

    def generate_project_from_bible(self, bible: Graph, project_root: Path) -> None:
        """
        Generate a minimal project structure from the given Bible graph.

        Creates:
          - project.json
          - data/locations.json
          - data/characters.json
          - data/quests.json

        The contents are deterministic summaries of the Bible; the backend
        is reserved for future, richer generation.
        """
        root = Path(project_root)
        data_dir = root / "data"

        root.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Helper to write JSON deterministically.
        def write_json(path: Path, payload: Any) -> None:
            with path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

        # Collect nodes by type.
        locations = sorted(
            bible.find_nodes_by_type("location"), key=lambda n: n.id
        )
        characters = sorted(
            bible.find_nodes_by_type("character"), key=lambda n: n.id
        )
        quests = sorted(
            bible.find_nodes_by_type("quest"), key=lambda n: n.id
        )

        # project.json: high-level summary.
        project_meta: Dict[str, Any] = {
            "name": "Generated Project",
            "version": 1,
            "bible_stats": {
                "locations": len(locations),
                "characters": len(characters),
                "quests": len(quests),
                "total_nodes": len(bible.nodes),
                "total_edges": len(bible.edges),
            },
        }
        write_json(root / "project.json", project_meta)

        # locations.json
        locations_payload: List[Dict[str, Any]] = [
            {
                "id": node.id,
                "props": dict(node.props),
            }
            for node in locations
        ]
        write_json(data_dir / "locations.json", locations_payload)

        # characters.json
        characters_payload: List[Dict[str, Any]] = [
            {
                "id": node.id,
                "props": dict(node.props),
            }
            for node in characters
        ]
        write_json(data_dir / "characters.json", characters_payload)

        # quests.json
        quests_payload: List[Dict[str, Any]] = [
            {
                "id": node.id,
                "props": dict(node.props),
            }
            for node in quests
        ]
        write_json(data_dir / "quests.json", quests_payload)

