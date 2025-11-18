from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from neonworks.bible.schema import Graph

from .llm_backend import LLMBackend


@dataclass
class Loremaster:
    """
    Generates dialog trees and narrative content for quests.

    For now this uses a deterministic placeholder structure so tests and
    downstream systems can rely on stable output. The LLM backend is
    injected for future upgrades where dialog will be authored by a
    language model.
    """

    backend: LLMBackend

    def generate_dialog_tree(self, quest_id: str, bible: Graph) -> Dict[str, Any]:
        """
        Generate a simple, deterministic dialog tree for the given quest.

        The structure is intentionally minimal:
          {
            "quest_id": ...,
            "title": ...,
            "nodes": [
              {"id": "start", "speaker": "system", "text": "...", "next": ["accept", "decline"]},
              {"id": "accept", "speaker": "player", "text": "...", "next": ["accepted"]},
              {"id": "decline", "speaker": "player", "text": "...", "next": ["declined"]},
              {"id": "accepted", "speaker": "system", "text": "...", "next": []},
              {"id": "declined", "speaker": "system", "text": "...", "next": []},
            ]
          }

        Later this will be replaced or enriched using the backend.
        """
        quest = bible.get_node(quest_id)
        title = ""
        if quest is not None:
            # Try common title/name keys in props, fall back to id.
            props = quest.props or {}
            title = (
                props.get("title")
                or props.get("name")
                or props.get("label")
                or quest.id
            )
        else:
            title = quest_id

        nodes: List[Dict[str, Any]] = [
            {
                "id": "start",
                "speaker": "system",
                "text": f"Quest available: {title}",
                "next": ["accept", "decline"],
            },
            {
                "id": "accept",
                "speaker": "player",
                "text": "I'll take this quest.",
                "next": ["accepted"],
            },
            {
                "id": "decline",
                "speaker": "player",
                "text": "Not interested.",
                "next": ["declined"],
            },
            {
                "id": "accepted",
                "speaker": "system",
                "text": "The quest has begun.",
                "next": [],
            },
            {
                "id": "declined",
                "speaker": "system",
                "text": "Maybe another time.",
                "next": [],
            },
        ]

        return {
            "quest_id": quest_id,
            "title": title,
            "nodes": nodes,
        }

