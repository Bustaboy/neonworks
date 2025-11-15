"""
Shared pytest fixtures for NeonWorks test suite.

This module provides common fixtures used across all test files,
including world instances, entities, mock objects, and test data.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, Mock

import pygame
import pytest

from neonworks.core.ecs import (
    Building,
    Collider,
    Entity,
    GridPosition,
    Health,
    Navmesh,
    ResourceStorage,
    RigidBody,
    Sprite,
    Survival,
    Transform,
    TurnActor,
    World,
)
from neonworks.core.events import EventManager, get_event_manager
from neonworks.gameplay.combat import Team, TeamComponent
from neonworks.gameplay.jrpg_combat import JRPGStats, MagicPoints, PartyMember
from neonworks.gameplay.movement import Movement


# Initialize Pygame for tests that need it
@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize Pygame once for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def world():
    """
    Create a fresh World instance for testing.

    Returns:
        World: Empty world instance
    """
    return World()


@pytest.fixture
def event_manager():
    """
    Create a fresh EventManager instance for testing.

    Returns:
        EventManager: Event manager instance
    """
    return EventManager()


@pytest.fixture
def player_entity(world):
    """
    Create a basic player entity with common components.

    Args:
        world: World fixture

    Returns:
        Entity: Player entity with Transform, Health, GridPosition, and tags
    """
    entity = world.create_entity("Player")
    entity.add_component(Transform(x=0, y=0))
    entity.add_component(Health(current=100, maximum=100))
    entity.add_component(GridPosition(grid_x=5, grid_y=5))
    entity.add_tag("player")
    return entity


@pytest.fixture
def enemy_entity(world):
    """
    Create a basic enemy entity with common components.

    Args:
        world: World fixture

    Returns:
        Entity: Enemy entity with Transform, Health, GridPosition, and tags
    """
    entity = world.create_entity("Enemy")
    entity.add_component(Transform(x=10, y=10))
    entity.add_component(Health(current=50, maximum=50))
    entity.add_component(GridPosition(grid_x=8, grid_y=8))
    entity.add_tag("enemy")
    return entity


@pytest.fixture
def jrpg_player(world):
    """
    Create a JRPG-style player character with full stats.

    Args:
        world: World fixture

    Returns:
        Entity: JRPG player with JRPGStats, MagicPoints, and PartyMember
    """
    entity = world.create_entity("Hero")
    entity.add_component(Transform(x=0, y=0))
    entity.add_component(
        JRPGStats(
            hp=100,
            max_hp=100,
            attack=20,
            defense=10,
            magic_attack=15,
            magic_defense=12,
            speed=18,
            level=5,
        )
    )
    entity.add_component(MagicPoints(mp=50, max_mp=50))
    entity.add_component(PartyMember(name="Hero", character_class="Warrior"))
    entity.add_tag("player")
    entity.add_tag("party_member")
    return entity


@pytest.fixture
def jrpg_enemy(world):
    """
    Create a JRPG-style enemy with full stats.

    Args:
        world: World fixture

    Returns:
        Entity: JRPG enemy with JRPGStats and MagicPoints
    """
    entity = world.create_entity("Goblin")
    entity.add_component(Transform(x=10, y=10))
    entity.add_component(
        JRPGStats(
            hp=30,
            max_hp=30,
            attack=10,
            defense=5,
            magic_attack=5,
            magic_defense=5,
            speed=12,
            level=2,
        )
    )
    entity.add_component(MagicPoints(mp=10, max_mp=10))
    entity.add_tag("enemy")
    return entity


@pytest.fixture
def building_entity(world):
    """
    Create a building entity with placement data.

    Args:
        world: World fixture

    Returns:
        Entity: Building entity with Building and GridPosition components
    """
    entity = world.create_entity("House")
    entity.add_component(GridPosition(grid_x=10, grid_y=10))
    entity.add_component(Building(building_type="house", level=1))
    entity.add_component(ResourceStorage(resources={"wood": 0, "stone": 0}))
    entity.add_tag("building")
    return entity


@pytest.fixture
def turn_actor(world):
    """
    Create an entity with turn-based combat components.

    Args:
        world: World fixture

    Returns:
        Entity: Turn actor with TurnActor component
    """
    entity = world.create_entity("TurnActor")
    entity.add_component(Transform(x=5, y=5))
    entity.add_component(GridPosition(grid_x=5, grid_y=5))
    entity.add_component(TurnActor(action_points=10, max_action_points=10, initiative=15))
    entity.add_component(Health(current=50, maximum=50))
    entity.add_tag("combatant")
    return entity


@pytest.fixture
def physics_entity(world):
    """
    Create an entity with physics components.

    Args:
        world: World fixture

    Returns:
        Entity: Entity with Collider and RigidBody components
    """
    entity = world.create_entity("PhysicsObject")
    entity.add_component(Transform(x=0, y=0))
    entity.add_component(Collider(width=32, height=32))
    entity.add_component(RigidBody(velocity_x=0, velocity_y=0, mass=1.0))
    return entity


@pytest.fixture
def survival_entity(world):
    """
    Create an entity with survival stats.

    Args:
        world: World fixture

    Returns:
        Entity: Entity with Survival component
    """
    entity = world.create_entity("Survivor")
    entity.add_component(Transform(x=0, y=0))
    entity.add_component(Survival(hunger=100, thirst=100, energy=100))
    entity.add_component(Health(current=100, maximum=100))
    entity.add_tag("survivor")
    return entity


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test files.

    Yields:
        Path: Temporary directory path

    Cleanup:
        Removes temporary directory after test
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_project_dir(temp_dir):
    """
    Create a temporary project directory structure.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Project root directory
    """
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()

    # Create standard project structure
    (project_dir / "assets").mkdir()
    (project_dir / "assets" / "sprites").mkdir()
    (project_dir / "assets" / "tilesets").mkdir()
    (project_dir / "assets" / "audio").mkdir()
    (project_dir / "config").mkdir()
    (project_dir / "maps").mkdir()
    (project_dir / "saves").mkdir()

    # Create minimal project.json
    project_json = project_dir / "project.json"
    project_json.write_text(
        """{
        "metadata": {
            "name": "Test Project",
            "version": "1.0.0",
            "description": "Test project for unit tests",
            "author": "Test Suite"
        },
        "settings": {
            "window_title": "Test Game",
            "window_width": 800,
            "window_height": 600,
            "tile_size": 32
        }
    }"""
    )

    return project_dir


@pytest.fixture
def mock_renderer():
    """
    Create a mock renderer for UI tests.

    Returns:
        Mock: Mock renderer with common methods
    """
    renderer = Mock()
    renderer.screen = pygame.Surface((800, 600))
    renderer.camera = Mock()
    renderer.camera.x = 0
    renderer.camera.y = 0
    renderer.camera.zoom = 1.0
    renderer.draw_rect = Mock()
    renderer.draw_text = Mock()
    renderer.draw_sprite = Mock()
    return renderer


@pytest.fixture
def mock_surface():
    """
    Create a mock Pygame surface for rendering tests.

    Returns:
        pygame.Surface: 800x600 test surface
    """
    return pygame.Surface((800, 600))


@pytest.fixture
def sample_entities(world):
    """
    Create a collection of diverse entities for testing.

    Args:
        world: World fixture

    Returns:
        Dict[str, Entity]: Dictionary of named entities
    """
    entities = {}

    # Player
    player = world.create_entity("Player")
    player.add_component(Transform(x=0, y=0))
    player.add_component(GridPosition(grid_x=0, grid_y=0))
    player.add_component(Health(current=100, maximum=100))
    player.add_component(Movement(speed=5.0, direction=(0, 0)))
    player.add_tag("player")
    entities["player"] = player

    # Enemies
    for i in range(3):
        enemy = world.create_entity(f"Enemy_{i}")
        enemy.add_component(Transform(x=i * 10, y=i * 10))
        enemy.add_component(GridPosition(grid_x=i * 2, grid_y=i * 2))
        enemy.add_component(Health(current=50, maximum=50))
        enemy.add_tag("enemy")
        entities[f"enemy_{i}"] = enemy

    # Buildings
    for i in range(2):
        building = world.create_entity(f"Building_{i}")
        building.add_component(GridPosition(grid_x=i * 5, grid_y=i * 5))
        building.add_component(
            Building(building_type="house", level=1)
        )
        building.add_tag("building")
        entities[f"building_{i}"] = building

    # NPCs
    for i in range(2):
        npc = world.create_entity(f"NPC_{i}")
        npc.add_component(Transform(x=i * 8, y=i * 8))
        npc.add_component(GridPosition(grid_x=i * 3, grid_y=i * 3))
        npc.add_tag("npc")
        entities[f"npc_{i}"] = npc

    return entities


@pytest.fixture
def performance_test_marker():
    """
    Marker for performance tests.

    Use this to skip performance tests in regular test runs.
    Run with: pytest -v -m performance
    """
    return pytest.mark.performance


@pytest.fixture
def stress_test_marker():
    """
    Marker for stress tests.

    Use this to skip stress tests in regular test runs.
    Run with: pytest -v -m stress
    """
    return pytest.mark.stress


@pytest.fixture
def integration_test_marker():
    """
    Marker for integration tests.

    Use this to skip integration tests in regular test runs.
    Run with: pytest -v -m integration
    """
    return pytest.mark.integration


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "performance: mark test as performance benchmark")
    config.addinivalue_line("markers", "stress: mark test as stress test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
