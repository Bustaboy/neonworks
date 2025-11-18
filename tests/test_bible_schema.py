import json

from neonworks.bible.schema import (
    Asset,
    Character,
    Faction,
    GameplayRule,
    Graph,
    Item,
    Location,
    Mechanic,
    Quest,
    StyleGuide,
)


def test_node_creation_and_storage():
    graph = Graph()

    hero = Character(id="hero", props={"name": "Hero", "level": 5})
    village = Location(id="village", props={"name": "Starting Village"})
    rule = GameplayRule(id="no_pvp", props={"description": "No PvP in safe zones"})

    graph.add_node(hero)
    graph.add_node(village)
    graph.add_node(rule)

    retrieved_hero = graph.get_node("hero")
    retrieved_village = graph.get_node("village")
    retrieved_rule = graph.get_node("no_pvp")

    assert retrieved_hero is hero
    assert retrieved_village is village
    assert retrieved_rule is rule

    assert isinstance(retrieved_hero, Character)
    assert retrieved_hero.type == "character"
    assert retrieved_hero.props["name"] == "Hero"
    assert retrieved_hero.props["level"] == 5

    assert isinstance(retrieved_village, Location)
    assert retrieved_village.type == "location"
    assert retrieved_village.props["name"] == "Starting Village"

    assert isinstance(retrieved_rule, GameplayRule)
    assert retrieved_rule.type == "gameplay_rule"
    assert "description" in retrieved_rule.props

    characters = graph.find_nodes_by_type("character")
    locations = graph.find_nodes_by_type("location")
    gameplay_rules = graph.find_nodes_by_type("gameplay_rule")

    assert [n.id for n in characters] == ["hero"]
    assert [n.id for n in locations] == ["village"]
    assert [n.id for n in gameplay_rules] == ["no_pvp"]


def test_add_edge_and_query_neighbors():
    graph = Graph()

    hero = Character(id="hero", props={"name": "Hero"})
    villager = Character(id="villager", props={"name": "Villager"})
    village = Location(id="village", props={"name": "Village"})

    graph.add_node(hero)
    graph.add_node(villager)
    graph.add_node(village)

    graph.add_edge("hero", "knows", "villager")
    graph.add_edge("hero", "located_in", "village")
    graph.add_edge("villager", "located_in", "village")

    neighbors_any = graph.query_neighbors("hero")
    neighbor_ids_any = {n.id for n in neighbors_any}
    assert neighbor_ids_any == {"villager", "village"}

    neighbors_knows = graph.query_neighbors("hero", rel="knows")
    neighbor_ids_knows = {n.id for n in neighbors_knows}
    assert neighbor_ids_knows == {"villager"}

    neighbors_located_in_hero = graph.query_neighbors("hero", rel="located_in")
    neighbor_ids_located_in_hero = {n.id for n in neighbors_located_in_hero}
    assert neighbor_ids_located_in_hero == {"village"}

    neighbors_located_in_villager = graph.query_neighbors("villager", rel="located_in")
    neighbor_ids_located_in_villager = {n.id for n in neighbors_located_in_villager}
    assert neighbor_ids_located_in_villager == {"village"}

    assert graph.query_neighbors("hero", rel="enemy_of") == []


def test_graph_json_round_trip():
    graph = Graph()

    hero = Character(id="hero", props={"name": "Hero", "hp": 100})
    village = Location(id="village", props={"name": "Village"})
    quest = Quest(id="quest1", props={"title": "Find the Relic"})
    relic = Item(id="relic", props={"rarity": "legendary"})
    faction = Faction(id="guild", props={"name": "Adventurer's Guild"})
    mechanic = Mechanic(id="turn_based", props={"description": "Turn-based combat"})
    asset = Asset(id="sprite_hero", props={"path": "assets/hero.png"})
    style = StyleGuide(id="pixel_art", props={"palette": "neon"})
    rule = GameplayRule(id="no_griefing", props={"description": "No griefing other players"})

    for node in [hero, village, quest, relic, faction, mechanic, asset, style, rule]:
        graph.add_node(node)

    graph.add_edge("hero", "located_in", "village")
    graph.add_edge("hero", "on_quest", "quest1")
    graph.add_edge("quest1", "requires_item", "relic")
    graph.add_edge("hero", "member_of", "guild")
    graph.add_edge("hero", "uses_mechanic", "turn_based")
    graph.add_edge("hero", "uses_asset", "sprite_hero")
    graph.add_edge("hero", "follows_style", "pixel_art")
    graph.add_edge("hero", "governed_by", "no_griefing")

    data = graph.to_dict()

    json_str = json.dumps(data)
    assert isinstance(json_str, str)

    loaded_data = json.loads(json_str)
    graph_rt = Graph.from_dict(loaded_data)

    assert set(graph_rt.nodes.keys()) == set(graph.nodes.keys())

    hero_rt = graph_rt.get_node("hero")
    assert isinstance(hero_rt, Character)
    assert hero_rt.type == "character"
    assert hero_rt.props["name"] == "Hero"
    assert hero_rt.props["hp"] == 100

    quest_rt = graph_rt.get_node("quest1")
    assert isinstance(quest_rt, Quest)
    assert quest_rt.props["title"] == "Find the Relic"

    neighbors_located_in = graph_rt.query_neighbors("hero", rel="located_in")
    assert {n.id for n in neighbors_located_in} == {"village"}

    neighbors_requires = graph_rt.query_neighbors("quest1", rel="requires_item")
    assert {n.id for n in neighbors_requires} == {"relic"}

    neighbors_member_of = graph_rt.query_neighbors("hero", rel="member_of")
    assert {n.id for n in neighbors_member_of} == {"guild"}

    style_rt = graph_rt.get_node("pixel_art")
    rule_rt = graph_rt.get_node("no_griefing")

    assert isinstance(style_rt, StyleGuide)
    assert style_rt.type == "style_guide"
    assert style_rt.props["palette"] == "neon"

    assert isinstance(rule_rt, GameplayRule)
    assert rule_rt.type == "gameplay_rule"
    assert "description" in rule_rt.props

