from __future__ import annotations

from typing import Any, Dict, List, Tuple

from neonworks.bible.bible_manager import BibleManager
from neonworks.bible.schema import Character, Location


class _FakeSession:
    def __init__(self, driver: "_FakeDriver") -> None:
        self._driver = driver

    def __enter__(self) -> "_FakeSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query: str, **params: Any) -> List[Dict[str, Any]]:
        self._driver.queries.append((query, params))

        # Minimal branching based on query shape to simulate results.
        if "MATCH (n:BibleNode {id: $id})" in query and "LIMIT 1" in query:
            # get_node
            return [
                {
                    "id": params["id"],
                    "type": "character",
                    "props": {"name": "Hero"},
                }
            ]

        if "MATCH (n:BibleNode {type: $type})" in query:
            # query_nodes_by_type
            return [
                {
                    "id": "hero",
                    "type": params["type"],
                    "props": {"name": "Hero"},
                }
            ]

        if "MATCH (a:BibleNode {id: $id})-[:BIBLE_RELATION]->(b:BibleNode)" in query or (
            "MATCH (a:BibleNode {id: $id})-[r:BIBLE_RELATION {rel: $rel}]->(b:BibleNode)"
            in query
        ):
            # query_neighbors
            return [
                {
                    "id": "villager",
                    "type": "character",
                    "props": {"name": "Villager"},
                }
            ]

        # add_node / add_edge return no records
        return []


class _FakeDriver:
    def __init__(self) -> None:
        self.queries: List[Tuple[str, Dict[str, Any]]] = []

    def verify_connectivity(self) -> None:
        # No-op for testing.
        return None

    def session(self) -> _FakeSession:
        return _FakeSession(self)


class _FakeGraphDatabase:
    @staticmethod
    def driver(uri: str, auth: Any) -> _FakeDriver:
        return _FakeDriver()


def test_bible_manager_uses_neo4j_driver_for_operations(monkeypatch):
    # Patch the GraphDatabase symbol inside the bible_manager module.
    monkeypatch.setattr(
        "neonworks.bible.bible_manager.GraphDatabase", _FakeGraphDatabase
    )

    manager = BibleManager()
    manager.connect("bolt://localhost:7687", "neo4j", "password")

    # After connect, a driver should be present.
    assert isinstance(manager._driver, _FakeDriver)
    driver: _FakeDriver = manager._driver  # type: ignore[assignment]

    # add_node / add_edge should produce Cypher queries.
    hero = Character(id="hero", props={"name": "Hero"})
    villager = Character(id="villager", props={"name": "Villager"})
    manager.add_node(hero)
    manager.add_node(villager)
    manager.add_edge("hero", "knows", "villager")

    recorded_queries = " ".join(q for q, _ in driver.queries)
    assert "MERGE (n:BibleNode" in recorded_queries
    assert "MATCH (a:BibleNode {id: $from_id})" in recorded_queries

    # get_node should return a reconstructed Node instance.
    fetched = manager.get_node("hero")
    assert fetched is not None
    assert fetched.id == "hero"
    assert fetched.type == "character"
    assert fetched.props["name"] == "Hero"

    # query_nodes_by_type should return a list with at least one node.
    characters = manager.query_nodes_by_type("character")
    assert characters
    assert characters[0].type == "character"

    # query_neighbors should return at least one neighbor node.
    neighbors = manager.query_neighbors("hero")
    assert neighbors
    assert neighbors[0].id == "villager"
    assert neighbors[0].type == "character"


def test_bible_manager_falls_back_to_in_memory_graph(monkeypatch):
    # Force GraphDatabase to be unavailable.
    monkeypatch.setattr("neonworks.bible.bible_manager.GraphDatabase", None)

    manager = BibleManager()
    manager.connect("bolt://localhost:7687", "neo4j", "password")

    # No driver should be configured; operations use the in-memory Graph.
    assert manager._driver is None

    hero = Character(id="hero", props={"name": "Hero"})
    town = Location(id="town", props={"name": "Starter Town"})

    manager.add_node(hero)
    manager.add_node(town)
    manager.add_edge("hero", "located_in", "town")

    fetched_hero = manager.get_node("hero")
    assert fetched_hero is hero

    characters = manager.query_nodes_by_type("character")
    assert len(characters) == 1
    assert characters[0] is hero

    neighbors = manager.query_neighbors("hero", rel_type="located_in")
    assert len(neighbors) == 1
    assert neighbors[0] is town

