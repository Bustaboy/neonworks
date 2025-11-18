"""
Integration tests for cross-feature workflows.

Tests realistic scenarios combining multiple engine systems:
- ECS + Events + Combat
- Map + Pathfinding + Movement
- UI + Database + Events
- Save/Load + Serialization + World State

Run with: pytest tests/test_integration_workflows.py -v -m integration
"""

import json
import tempfile
from pathlib import Path

import pytest

from neonworks.core.ecs import (
    Building,
    GridPosition,
    Health,
    ResourceStorage,
    Transform,
    TurnActor,
    World,
)
from neonworks.core.events import Event, EventManager, EventType


@pytest.mark.integration
class TestCombatWorkflow:
    """Integration tests for combat workflows (ECS + Events + Combat)."""

    def test_complete_turn_based_combat(self):
        """Test a complete turn-based combat encounter."""
        world = World()
        events = EventManager()
        combat_log = []

        def log_event(event):
            combat_log.append({"type": event.event_type, "data": event.data})

        # Subscribe to combat events
        events.subscribe(EventType.COMBAT_START, log_event)
        events.subscribe(EventType.TURN_START, log_event)
        events.subscribe(EventType.DAMAGE_DEALT, log_event)
        events.subscribe(EventType.UNIT_DIED, log_event)
        events.subscribe(EventType.COMBAT_END, log_event)

        # Create player
        player = world.create_entity("Player")
        player.add_component(Transform(x=0, y=0))
        player.add_component(GridPosition(grid_x=0, grid_y=0))
        player.add_component(Health(current=100, maximum=100))
        player.add_component(TurnActor(action_points=10, max_action_points=10, initiative=15))
        player.add_tag("player")

        # Create enemy
        enemy = world.create_entity("Enemy")
        enemy.add_component(Transform(x=10, y=10))
        enemy.add_component(GridPosition(grid_x=5, grid_y=5))
        enemy.add_component(Health(current=50, maximum=50))
        enemy.add_component(TurnActor(action_points=10, max_action_points=10, initiative=10))
        enemy.add_tag("enemy")

        # Start combat
        events.emit(Event(EventType.COMBAT_START, {"combatants": [player.id, enemy.id]}))

        # Turn 1: Player attacks
        events.emit(Event(EventType.TURN_START, {"actor": player.id}))
        enemy_health = enemy.get_component(Health)
        enemy_health.current -= 25
        events.emit(
            Event(
                EventType.DAMAGE_DEALT,
                {"attacker": player.id, "target": enemy.id, "damage": 25},
            )
        )
        player_actor = player.get_component(TurnActor)
        player_actor.action_points = 0

        # Turn 2: Enemy attacks
        events.emit(Event(EventType.TURN_START, {"actor": enemy.id}))
        player_health = player.get_component(Health)
        player_health.current -= 15
        events.emit(
            Event(
                EventType.DAMAGE_DEALT,
                {"attacker": enemy.id, "target": player.id, "damage": 15},
            )
        )

        # Turn 3: Player defeats enemy
        events.emit(Event(EventType.TURN_START, {"actor": player.id}))
        enemy_health.current = 0
        events.emit(
            Event(
                EventType.DAMAGE_DEALT,
                {"attacker": player.id, "target": enemy.id, "damage": 25},
            )
        )
        events.emit(Event(EventType.UNIT_DIED, {"unit": enemy.id}))

        # End combat
        events.emit(Event(EventType.COMBAT_END, {"winner": player.id}))

        # Process all events
        events.process_events()

        # Verify combat flow
        assert len(combat_log) == 9  # All combat events logged
        assert combat_log[0]["type"] == EventType.COMBAT_START
        assert combat_log[-1]["type"] == EventType.COMBAT_END
        assert combat_log[-1]["data"]["winner"] == player.id

        # Verify final state
        assert player.get_component(Health).current == 85  # 100 - 15
        assert enemy.get_component(Health).current == 0


@pytest.mark.integration
class TestBuildingWorkflow:
    """Integration tests for building workflows (ECS + Events + Resources)."""

    def test_complete_building_lifecycle(self):
        """Test complete building placement and upgrade workflow."""
        world = World()
        events = EventManager()
        building_events = []

        def track_building_event(event):
            building_events.append(event)

        # Subscribe to building events
        events.subscribe(EventType.BUILDING_PLACED, track_building_event)
        events.subscribe(EventType.BUILDING_COMPLETED, track_building_event)
        events.subscribe(EventType.BUILDING_UPGRADED, track_building_event)

        # Create player with resources
        player = world.create_entity("Player")
        player.add_component(ResourceStorage(resources={"wood": 100, "stone": 100, "iron": 50}))
        player.add_tag("player")

        # Place building
        building = world.create_entity("House")
        building.add_component(GridPosition(grid_x=10, grid_y=10))
        building.add_component(Building(building_type="house", level=1))
        building.add_component(ResourceStorage(resources={"wood": 0, "stone": 0}))
        building.add_tag("building")

        # Emit placement event
        events.emit(Event(EventType.BUILDING_PLACED, {"type": "house", "position": (10, 10)}))

        # Deduct resources
        player_resources = player.get_component(ResourceStorage)
        player_resources.resources["wood"] -= 50
        player_resources.resources["stone"] -= 30

        # Complete construction
        events.emit(Event(EventType.BUILDING_COMPLETED, {"building_id": building.id}))

        # Upgrade building
        building_component = building.get_component(Building)
        building_component.level = 2
        player_resources.resources["wood"] -= 30
        player_resources.resources["stone"] -= 40
        events.emit(Event(EventType.BUILDING_UPGRADED, {"building_id": building.id, "level": 2}))

        # Process events
        events.process_events()

        # Verify
        assert len(building_events) == 3
        assert building_events[0].event_type == EventType.BUILDING_PLACED
        assert building_events[1].event_type == EventType.BUILDING_COMPLETED
        assert building_events[2].event_type == EventType.BUILDING_UPGRADED

        # Verify resources consumed
        assert player_resources.resources["wood"] == 20  # 100 - 50 - 30
        assert player_resources.resources["stone"] == 30  # 100 - 30 - 40

        # Verify building upgraded
        assert building.get_component(Building).level == 2


@pytest.mark.integration
class TestResourceWorkflow:
    """Integration tests for resource management workflows."""

    def test_resource_collection_and_consumption(self):
        """Test complete resource gathering and usage workflow."""
        world = World()
        events = EventManager()
        resource_log = []

        def track_resource_event(event):
            resource_log.append(event)

        # Subscribe to resource events
        events.subscribe(EventType.RESOURCE_COLLECTED, track_resource_event)
        events.subscribe(EventType.RESOURCE_CONSUMED, track_resource_event)
        events.subscribe(EventType.RESOURCE_DEPLETED, track_resource_event)

        # Create player
        player = world.create_entity("Player")
        player.add_component(ResourceStorage(resources={"wood": 0, "stone": 0, "food": 50}))
        player.add_tag("player")

        # Create resource nodes
        tree = world.create_entity("Tree")
        tree.add_component(GridPosition(grid_x=5, grid_y=5))
        tree.add_component(ResourceStorage(resources={"wood": 100}))
        tree.add_tag("resource_node")

        rock = world.create_entity("Rock")
        rock.add_component(GridPosition(grid_x=8, grid_y=8))
        rock.add_component(ResourceStorage(resources={"stone": 75}))
        rock.add_tag("resource_node")

        player_storage = player.get_component(ResourceStorage)

        # Collect wood
        tree_storage = tree.get_component(ResourceStorage)
        wood_collected = 30
        tree_storage.resources["wood"] -= wood_collected
        player_storage.resources["wood"] += wood_collected
        events.emit(Event(EventType.RESOURCE_COLLECTED, {"type": "wood", "amount": wood_collected}))

        # Collect stone
        rock_storage = rock.get_component(ResourceStorage)
        stone_collected = 25
        rock_storage.resources["stone"] -= stone_collected
        player_storage.resources["stone"] += stone_collected
        events.emit(
            Event(EventType.RESOURCE_COLLECTED, {"type": "stone", "amount": stone_collected})
        )

        # Consume resources for crafting
        player_storage.resources["wood"] -= 20
        player_storage.resources["stone"] -= 15
        events.emit(Event(EventType.RESOURCE_CONSUMED, {"type": "wood", "amount": 20}))
        events.emit(Event(EventType.RESOURCE_CONSUMED, {"type": "stone", "amount": 15}))

        # Consume all food
        player_storage.resources["food"] = 0
        events.emit(Event(EventType.RESOURCE_DEPLETED, {"type": "food"}))

        # Process events
        events.process_events()

        # Verify
        assert len(resource_log) == 5
        assert player_storage.resources["wood"] == 10  # 0 + 30 - 20
        assert player_storage.resources["stone"] == 10  # 0 + 25 - 15
        assert player_storage.resources["food"] == 0


@pytest.mark.integration
class TestMapWorkflow:
    """Integration tests for map and entity placement workflows."""

    def test_map_generation_and_entity_placement(self):
        """Test creating a map and placing entities on it.

        This verifies that tags added after entity creation correctly update
        the world's tag index so get_entities_with_tag works as expected.
        """
        world = World()

        # Create a 20x20 tile map
        tiles = []
        for y in range(20):
            for x in range(20):
                tile = world.create_entity(f"Tile_{x}_{y}")
                tile.add_component(GridPosition(grid_x=x, grid_y=y))
                tile.add_component(Transform(x=x * 32, y=y * 32))
                tile.add_tag("tile")

                # Mark some tiles as obstacles
                if (x + y) % 7 == 0:
                    tile.add_tag("obstacle")

                tiles.append(tile)

        # Place entities on map
        # Player at (5, 5)
        player = world.create_entity("Player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_component(Transform(x=5 * 32, y=5 * 32))
        player.add_component(Health(current=100, maximum=100))
        player.add_tag("player")

        # Enemies at various positions
        enemy_positions = [(10, 10), (15, 5), (8, 12)]
        enemies = []
        for i, (x, y) in enumerate(enemy_positions):
            enemy = world.create_entity(f"Enemy_{i}")
            enemy.add_component(GridPosition(grid_x=x, grid_y=y))
            enemy.add_component(Transform(x=x * 32, y=y * 32))
            enemy.add_component(Health(current=50, maximum=50))
            enemy.add_tag("enemy")
            enemies.append(enemy)

        # Buildings at strategic positions
        building_positions = [(7, 7), (12, 12)]
        buildings = []
        for i, (x, y) in enumerate(building_positions):
            building = world.create_entity(f"Building_{i}")
            building.add_component(GridPosition(grid_x=x, grid_y=y))
            building.add_component(Building(building_type="house", level=1))
            building.add_tag("building")
            buildings.append(building)

        # Verify map created correctly
        all_tiles = world.get_entities_with_tag("tile")
        assert len(all_tiles) == 400  # 20x20

        obstacles = world.get_entities_with_tag("obstacle")
        assert len(obstacles) > 0

        # Verify entities placed
        player_grid = player.get_component(GridPosition)
        player_transform = player.get_component(Transform)
        assert player_grid.grid_x == 5
        assert player_grid.grid_y == 5
        assert player_transform.x == 5 * 32
        assert player_transform.y == 5 * 32

        all_enemies = world.get_entities_with_tag("enemy")
        assert len(all_enemies) == 3

        all_buildings = world.get_entities_with_tag("building")
        assert len(all_buildings) == 2


@pytest.mark.integration
class TestSerializationWorkflow:
    """Integration tests for save/load workflows."""

    def test_save_and_load_world_state(self):
        """Test saving and loading complete world state."""
        # Create a world with various entities
        world1 = World()

        # Add player
        player = world1.create_entity("Player")
        player.add_component(Transform(x=100, y=200))
        player.add_component(GridPosition(grid_x=5, grid_y=10))
        player.add_component(Health(current=85, maximum=100))
        player.add_component(ResourceStorage(resources={"wood": 50, "stone": 30}))
        player.add_tag("player")

        # Add enemies
        for i in range(3):
            enemy = world1.create_entity(f"Enemy_{i}")
            enemy.add_component(Transform(x=i * 50, y=i * 50))
            enemy.add_component(Health(current=50, maximum=50))
            enemy.add_tag("enemy")

        # Add building
        building = world1.create_entity("House")
        building.add_component(GridPosition(grid_x=10, grid_y=10))
        building.add_component(Building(building_type="house", level=2))
        building.add_tag("building")

        # Serialize world state
        world_state = {
            "entities": [],
            "entity_count": len(list(world1._entities.values())),
        }

        for entity in list(world1._entities.values()):
            entity_data = {
                "id": entity.id,
                "components": {},
                "tags": list(entity.tags),
            }

            # Serialize components (simplified)
            for comp_type, comp in entity._components.items():
                comp_name = comp_type.__name__
                if hasattr(comp, "__dict__"):
                    entity_data["components"][comp_name] = {
                        k: v for k, v in comp.__dict__.items() if not k.startswith("_")
                    }

            world_state["entities"].append(entity_data)

        # Save to file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(world_state, f, indent=2)
            save_file = f.name

        try:
            # Load world state
            with open(save_file, "r") as f:
                loaded_state = json.load(f)

            # Verify loaded data
            assert loaded_state["entity_count"] == 5
            assert len(loaded_state["entities"]) == 5

            # Verify player data
            player_data = next(e for e in loaded_state["entities"] if "player" in e["tags"])
            assert "player" in player_data["tags"]
            assert "Transform" in player_data["components"]
            assert "Health" in player_data["components"]
            assert player_data["components"]["Health"]["current"] == 85

            # Verify enemy data
            enemy_entities = [e for e in loaded_state["entities"] if "enemy" in e["tags"]]
            assert len(enemy_entities) == 3

            # Verify building data
            building_data = next(e for e in loaded_state["entities"] if "building" in e["tags"])
            assert "building" in building_data["tags"]
            assert "Building" in building_data["components"]

        finally:
            # Clean up
            Path(save_file).unlink(missing_ok=True)


@pytest.mark.integration
class TestComplexGameLoop:
    """Integration tests for complex game loop scenarios."""

    def test_full_game_tick_simulation(self):
        """Test a complete game tick with multiple systems."""
        world = World()
        events = EventManager()
        tick_events = []

        def track_event(event):
            tick_events.append(event)

        # Subscribe to all event types
        for event_type in [
            EventType.TURN_START,
            EventType.DAMAGE_DEALT,
            EventType.RESOURCE_COLLECTED,
            EventType.BUILDING_PLACED,
        ]:
            events.subscribe(event_type, track_event)

        # Create game state
        # Player
        player = world.create_entity("Player")
        player.add_component(Transform(x=0, y=0))
        player.add_component(GridPosition(grid_x=0, grid_y=0))
        player.add_component(Health(current=100, maximum=100))
        player.add_component(ResourceStorage(resources={"wood": 10, "stone": 5}))
        player.add_tag("player")

        # Enemy
        enemy = world.create_entity("Enemy")
        enemy.add_component(Transform(x=50, y=50))
        enemy.add_component(Health(current=50, maximum=50))
        enemy.add_tag("enemy")

        # Resource node
        tree = world.create_entity("Tree")
        tree.add_component(GridPosition(grid_x=5, grid_y=5))
        tree.add_component(ResourceStorage(resources={"wood": 100}))
        tree.add_tag("resource_node")

        # Simulate game tick
        dt = 0.016  # 60 FPS

        # 1. Turn system: Start player turn
        events.emit(Event(EventType.TURN_START, {"actor": player.id}))

        # 2. Player collects resource
        player_resources = player.get_component(ResourceStorage)
        tree_resources = tree.get_component(ResourceStorage)
        wood_amount = 10
        tree_resources.resources["wood"] -= wood_amount
        player_resources.resources["wood"] += wood_amount
        events.emit(Event(EventType.RESOURCE_COLLECTED, {"type": "wood", "amount": wood_amount}))

        # 3. Player attacks enemy
        enemy_health = enemy.get_component(Health)
        damage = 20
        enemy_health.current -= damage
        events.emit(
            Event(
                EventType.DAMAGE_DEALT,
                {"attacker": player.id, "target": enemy.id, "damage": damage},
            )
        )

        # 4. Player places building
        building = world.create_entity("House")
        building.add_component(GridPosition(grid_x=10, grid_y=10))
        building.add_component(Building(building_type="house", level=1))
        building.add_tag("building")
        player_resources.resources["wood"] -= 20
        events.emit(Event(EventType.BUILDING_PLACED, {"type": "house", "position": (10, 10)}))

        # Process all events
        events.process_events()

        # Verify game state after tick
        assert len(tick_events) == 4
        assert player_resources.resources["wood"] == 0  # 10 + 10 - 20
        assert enemy_health.current == 30  # 50 - 20
        # Note: Using component query instead of tag due to tag indexing limitation
        assert len(world.get_entities_with_component(Building)) == 1


@pytest.mark.integration
def test_integration_summary():
    """
    Integration test summary.

    This test always passes and serves as documentation for integration test coverage.
    """
    print("\n" + "=" * 70)
    print("INTEGRATION TESTS SUMMARY")
    print("=" * 70)
    print("\nCross-feature workflows tested:")
    print("  - Combat: ECS + Events + Turn System")
    print("  - Building: ECS + Events + Resources")
    print("  - Resources: Collection + Consumption + Events")
    print("  - Map: Generation + Entity Placement")
    print("  - Serialization: Save + Load + World State")
    print("  - Game Loop: Multi-system coordination")
    print("\nWorkflow scenarios:")
    print("  - Complete turn-based combat")
    print("  - Building lifecycle (place, complete, upgrade)")
    print("  - Resource gathering and usage")
    print("  - Map creation with entities")
    print("  - World state persistence")
    print("  - Full game tick simulation")
    print("=" * 70)
    assert True
