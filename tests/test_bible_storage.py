from pathlib import Path

from neonworks.bible.schema import Character, Graph, Location
from neonworks.bible.storage import load_bible, save_bible


def test_save_and_load_bible_round_trip(tmp_path):
    graph = Graph()

    hero = Character(id="hero", props={"name": "Hero", "hp": 100})
    village = Location(id="village", props={"name": "Starting Village"})

    graph.add_node(hero)
    graph.add_node(village)
    graph.add_edge("hero", "located_in", "village")

    path = tmp_path / "bible.json"
    save_bible(graph, path)

    assert path.exists()

    loaded_graph = load_bible(path)

    assert isinstance(loaded_graph, Graph)
    assert loaded_graph.to_dict() == graph.to_dict()


def test_load_bible_missing_file_returns_empty_graph(tmp_path):
    path = tmp_path / "missing_bible.json"
    assert not path.exists()

    graph = load_bible(path)

    assert isinstance(graph, Graph)
    assert graph.nodes == {}
    assert graph.edges == []

