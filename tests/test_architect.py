from __future__ import annotations

import json
from pathlib import Path

from neonworks.agents.architect import Architect
from neonworks.agents.llm_backend import DummyBackend
from neonworks.bible.schema import Character, Graph, Location, Quest


def _build_sample_bible() -> Graph:
    graph = Graph()

    town = Location(id="town_square", props={"name": "Town Square"})
    forest = Location(id="mystic_forest", props={"name": "Mystic Forest"})
    hero = Character(id="hero", props={"name": "Hero", "role": "protagonist"})
    villager = Character(id="villager", props={"name": "Villager"})
    quest = Quest(id="q1", props={"title": "First Steps"})

    for node in [town, forest, hero, villager, quest]:
        graph.add_node(node)

    graph.add_edge("hero", "starts_in", "town_square")
    graph.add_edge("hero", "assigned_quest", "q1")
    graph.add_edge("q1", "leads_to", "mystic_forest")

    return graph


def test_generate_project_from_bible_creates_expected_files(tmp_path):
    bible = _build_sample_bible()
    backend = DummyBackend()
    architect = Architect(backend=backend)

    project_root = tmp_path / "project"
    architect.generate_project_from_bible(bible, project_root)

    project_json = project_root / "project.json"
    data_dir = project_root / "data"
    locations_json = data_dir / "locations.json"
    characters_json = data_dir / "characters.json"
    quests_json = data_dir / "quests.json"

    # All expected files are created
    assert project_json.is_file()
    assert data_dir.is_dir()
    assert locations_json.is_file()
    assert characters_json.is_file()
    assert quests_json.is_file()

    # Validate project.json shape
    with project_json.open("r", encoding="utf-8") as f:
        project_data = json.load(f)

    assert isinstance(project_data, dict)
    assert "name" in project_data
    assert "version" in project_data
    assert "bible_stats" in project_data

    stats = project_data["bible_stats"]
    assert set(stats.keys()) == {
        "locations",
        "characters",
        "quests",
        "total_nodes",
        "total_edges",
    }
    assert stats["locations"] == 2
    assert stats["characters"] == 2
    assert stats["quests"] == 1
    assert stats["total_nodes"] == len(bible.nodes)
    assert stats["total_edges"] == len(bible.edges)

    # Helper to read list payloads
    def load_list(path: Path):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        return data

    locations = load_list(locations_json)
    characters = load_list(characters_json)
    quests = load_list(quests_json)

    # Each entry should have id and props keys
    for entry in locations + characters + quests:
        assert isinstance(entry, dict)
        assert "id" in entry
        assert "props" in entry

    # Counts should match stats
    assert len(locations) == stats["locations"]
    assert len(characters) == stats["characters"]
    assert len(quests) == stats["quests"]

