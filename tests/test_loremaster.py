from __future__ import annotations

from neonworks.agents.llm_backend import DummyBackend
from neonworks.agents.loremaster import Loremaster
from neonworks.bible.schema import Graph, Quest


def _build_bible_with_quest() -> Graph:
    graph = Graph()
    quest = Quest(id="q1", props={"title": "First Steps"})
    graph.add_node(quest)
    return graph


def test_generate_dialog_tree_basic_structure():
    bible = _build_bible_with_quest()
    backend = DummyBackend()
    loremaster = Loremaster(backend=backend)

    tree = loremaster.generate_dialog_tree("q1", bible)

    assert isinstance(tree, dict)
    assert tree["quest_id"] == "q1"
    assert tree["title"] == "First Steps"

    nodes = tree["nodes"]
    assert isinstance(nodes, list)
    assert len(nodes) >= 5

    # Collect nodes by id for easier assertions
    nodes_by_id = {n["id"]: n for n in nodes}

    for node_id in ["start", "accept", "decline", "accepted", "declined"]:
        assert node_id in nodes_by_id
        node = nodes_by_id[node_id]
        assert isinstance(node, dict)
        assert "speaker" in node
        assert "text" in node
        assert "next" in node
        assert isinstance(node["next"], list)

    start = nodes_by_id["start"]
    assert "First Steps" in start["text"]
    assert set(start["next"]) == {"accept", "decline"}


def test_generate_dialog_tree_missing_quest_falls_back_to_id():
    bible = Graph()  # No quests added
    backend = DummyBackend()
    loremaster = Loremaster(backend=backend)

    tree = loremaster.generate_dialog_tree("unknown_quest", bible)

    assert tree["quest_id"] == "unknown_quest"
    assert tree["title"] == "unknown_quest"
    assert isinstance(tree["nodes"], list)

