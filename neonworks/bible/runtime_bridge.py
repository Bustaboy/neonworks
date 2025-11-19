from __future__ import annotations

"""
Runtime bridge between the World Bible graph and the game engine.

This module provides a minimal, read-only integration point so that
runtime systems can pull high-level narrative data (quests, characters,
locations) from the Bible graph instead of hard-coded JSON files.

It deliberately focuses on a small vertical slice:
- Load a Graph from disk using `load_bible`.
- Provide helper methods for fetching quest / character / location nodes.

More advanced integrations (e.g. driving full quest systems from the
Bible) can be layered on top of this bridge.
"""

from pathlib import Path
from typing import List, Optional, Union

from .schema import Character, Graph, Location, Quest
from .storage import PathLike, load_bible


class BibleRuntimeBridge:
    """
    Lightweight helper for accessing World Bible content at runtime.

    The bridge owns a loaded `Graph` instance and exposes convenience
    methods for querying quests, characters, and locations. Systems can
    choose to depend on this bridge instead of (or in addition to)
    static JSON configuration.
    """

    def __init__(self, bible_path: PathLike):
        """
        Initialize the bridge and load a Bible graph from disk.

        Args:
            bible_path: Path to a Bible JSON file created via `save_bible`.
        """
        self._path: Path = Path(bible_path)
        self._graph: Graph = load_bible(self._path)

    @property
    def graph(self) -> Graph:
        """Return the underlying Graph instance."""
        return self._graph

    @property
    def path(self) -> Path:
        """Return the path to the Bible file."""
        return self._path

    def reload(self) -> None:
        """
        Reload the Bible graph from disk.

        Useful if external tools regenerate the Bible while the engine
        is running (e.g. hot-reload in editor mode).
        """
        self._graph = load_bible(self._path)

    # ------------------------------------------------------------------
    # Quest helpers
    # ------------------------------------------------------------------

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """
        Get a quest node by ID.

        Args:
            quest_id: ID of the quest node.

        Returns:
            Quest instance if found and of the correct type, otherwise None.
        """
        node = self._graph.get_node(quest_id)
        if isinstance(node, Quest):
            return node
        return None

    def list_quests(self) -> List[Quest]:
        """
        List all quest nodes in the Bible.

        Returns:
            List of Quest instances (may be empty).
        """
        nodes = self._graph.find_nodes_by_type("quest")
        return [n for n in nodes if isinstance(n, Quest)]

    # ------------------------------------------------------------------
    # Character helpers
    # ------------------------------------------------------------------

    def get_character(self, character_id: str) -> Optional[Character]:
        """
        Get a character node by ID.

        Args:
            character_id: ID of the character node.

        Returns:
            Character instance if found and of the correct type, otherwise None.
        """
        node = self._graph.get_node(character_id)
        if isinstance(node, Character):
            return node
        return None

    def list_characters(self) -> List[Character]:
        """
        List all character nodes in the Bible.

        Returns:
            List of Character instances (may be empty).
        """
        nodes = self._graph.find_nodes_by_type("character")
        return [n for n in nodes if isinstance(n, Character)]

    # ------------------------------------------------------------------
    # Location helpers
    # ------------------------------------------------------------------

    def get_location(self, location_id: str) -> Optional[Location]:
        """
        Get a location node by ID.

        Args:
            location_id: ID of the location node.

        Returns:
            Location instance if found and of the correct type, otherwise None.
        """
        node = self._graph.get_node(location_id)
        if isinstance(node, Location):
            return node
        return None

    def list_locations(self) -> List[Location]:
        """
        List all location nodes in the Bible.

        Returns:
            List of Location instances (may be empty).
        """
        nodes = self._graph.find_nodes_by_type("location")
        return [n for n in nodes if isinstance(n, Location)]


def load_runtime_bridge(bible_path: PathLike) -> BibleRuntimeBridge:
    """
    Convenience function to construct a BibleRuntimeBridge.

    This mirrors the typical pattern used in systems where an engine-wide
    bridge is created once and passed into subsystems.
    """
    return BibleRuntimeBridge(bible_path)

