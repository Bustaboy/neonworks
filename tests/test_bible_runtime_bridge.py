from __future__ import annotations

from pathlib import Path
from typing import Dict

from neonworks.bible.runtime_bridge import BibleRuntimeBridge, load_runtime_bridge
from neonworks.bible.schema import Character, Graph, Location, Quest
from neonworks.bible.storage import save_bible


def _build_sample_graph() -> Graph:
    """Create a tiny in-memory Bible graph for testing."""
    graph = Graph()

    # Create sample nodes
    quest = Quest(
        id="quest_rescue_1",
        props={
            "name": "Rescue the Villager",
            "description": "Find and rescue the missing villager.",
            "difficulty": "normal",
        },
    )
    character = Character(
        id="char_hero",
        props={
            "name": "Aria",
            "role": "hero",
        },
    )
    location = Location(
        id="loc_forest",
        props={
            "name": "Whispering Forest",
            "region": "north",
        },
    )

    # Add nodes to graph
    graph.add_node(quest)
    graph.add_node(character)
    graph.add_node(location)

    return graph


def test_runtime_bridge_loads_and_queries_nodes(tmp_path):
    """Bridge should load a saved Bible and expose basic query helpers."""
    bible_path: Path = tmp_path / "bible.json"

    # Build and persist a tiny graph
    graph = _build_sample_graph()
    save_bible(graph, bible_path)

    # Load via the runtime bridge
    bridge = BibleRuntimeBridge(bible_path)

    # Quest lookup
    quest = bridge.get_quest("quest_rescue_1")
    assert isinstance(quest, Quest)
    assert quest.props["name"] == "Rescue the Villager"

    # Character lookup
    character = bridge.get_character("char_hero")
    assert isinstance(character, Character)
    assert character.props["role"] == "hero"

    # Location lookup
    location = bridge.get_location("loc_forest")
    assert isinstance(location, Location)
    assert location.props["region"] == "north"

    # List helpers
    quests = bridge.list_quests()
    characters = bridge.list_characters()
    locations = bridge.list_locations()

    assert {q.id for q in quests} == {"quest_rescue_1"}
    assert {c.id for c in characters} == {"char_hero"}
    assert {l.id for l in locations} == {"loc_forest"}


def test_load_runtime_bridge_convenience_function(tmp_path):
    """load_runtime_bridge should construct a bridge pointing at the given path."""
    bible_path: Path = tmp_path / "bible.json"
    save_bible(_build_sample_graph(), bible_path)

    bridge = load_runtime_bridge(bible_path)

    quest = bridge.get_quest("quest_rescue_1")
    assert quest is not None
    assert quest.props["difficulty"] == "normal"


def test_runtime_bridge_handles_missing_file(tmp_path):
    """When the Bible file does not exist, the bridge should expose an empty graph."""
    missing_path: Path = tmp_path / "does_not_exist.json"

    bridge = BibleRuntimeBridge(missing_path)

    assert bridge.list_quests() == []
    assert bridge.list_characters() == []
    assert bridge.list_locations() == []
    assert bridge.get_quest("nonexistent") is None
    assert bridge.get_character("nonexistent") is None
    assert bridge.get_location("nonexistent") is None

