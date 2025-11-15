"""
Comprehensive tests for Entity Component System (ECS).

Tests the core ECS architecture including Entity, Component, System, and World classes.
This is the heart of the NeonWorks engine.
"""

import pytest

from neonworks.core.ecs import (
    Building,
    Collider,
    Component,
    Entity,
    GridPosition,
    Health,
    Navmesh,
    ResourceStorage,
    RigidBody,
    Sprite,
    Survival,
    System,
    Transform,
    TurnActor,
    World,
)


class TestEntity:
    """Test suite for Entity class."""

    def test_create_entity(self):
        """Test creating an entity."""
        entity = Entity()

        assert entity is not None
        assert entity.id is not None
        assert len(entity._components) == 0
        assert len(entity.tags) == 0

    def test_entity_unique_ids(self):
        """Test that entities have unique IDs."""
        entity1 = Entity()
        entity2 = Entity()

        assert entity1.id != entity2.id

    def test_add_component(self):
        """Test adding a component to an entity."""
        entity = Entity()
        transform = Transform(x=10, y=20)

        entity.add_component(transform)

        assert entity.has_component(Transform)
        assert entity.get_component(Transform) is transform

    def test_add_multiple_components(self):
        """Test adding multiple different components."""
        entity = Entity()
        transform = Transform(x=10, y=20)
        health = Health(current=100, maximum=100)
        grid_pos = GridPosition(grid_x=5, grid_y=5)

        entity.add_component(transform)
        entity.add_component(health)
        entity.add_component(grid_pos)

        assert entity.has_component(Transform)
        assert entity.has_component(Health)
        assert entity.has_component(GridPosition)
        assert len(entity._components) == 3

    def test_replace_component(self):
        """Test that adding same component type replaces the old one."""
        entity = Entity()
        transform1 = Transform(x=10, y=20)
        transform2 = Transform(x=30, y=40)

        entity.add_component(transform1)
        entity.add_component(transform2)

        assert entity.get_component(Transform) is transform2
        assert entity.get_component(Transform).x == 30
        assert len(entity._components) == 1

    def test_remove_component(self):
        """Test removing a component from an entity."""
        entity = Entity()
        transform = Transform(x=10, y=20)

        entity.add_component(transform)
        assert entity.has_component(Transform)

        entity.remove_component(Transform)
        assert not entity.has_component(Transform)
        assert entity.get_component(Transform) is None

    def test_get_component_when_missing(self):
        """Test getting a component that doesn't exist returns None."""
        entity = Entity()

        result = entity.get_component(Transform)

        assert result is None

    def test_add_tag(self):
        """Test adding a tag to an entity."""
        entity = Entity()

        entity.add_tag("player")

        assert "player" in entity.tags
        assert entity.has_tag("player")

    def test_add_multiple_tags(self):
        """Test adding multiple tags to an entity."""
        entity = Entity()

        entity.add_tag("player")
        entity.add_tag("alive")
        entity.add_tag("protagonist")

        assert len(entity.tags) == 3
        assert entity.has_tag("player")
        assert entity.has_tag("alive")
        assert entity.has_tag("protagonist")

    def test_add_duplicate_tag(self):
        """Test that adding duplicate tags doesn't create duplicates."""
        entity = Entity()

        entity.add_tag("player")
        entity.add_tag("player")
        entity.add_tag("player")

        assert len(entity.tags) == 1

    def test_remove_tag(self):
        """Test removing a tag from an entity."""
        entity = Entity()
        entity.add_tag("player")

        entity.remove_tag("player")

        assert not entity.has_tag("player")
        assert "player" not in entity.tags

    def test_remove_nonexistent_tag(self):
        """Test removing a tag that doesn't exist (should not error)."""
        entity = Entity()

        # Should not raise an error
        entity.remove_tag("nonexistent")

        assert not entity.has_tag("nonexistent")


class TestTransformComponent:
    """Test suite for Transform component."""

    def test_create_transform(self):
        """Test creating a transform component."""
        transform = Transform(x=10.5, y=20.3)

        assert transform.x == 10.5
        assert transform.y == 20.3
        assert transform.rotation == 0.0
        assert transform.scale_x == 1.0
        assert transform.scale_y == 1.0

    def test_transform_with_rotation_and_scale(self):
        """Test transform with custom rotation and scale."""
        transform = Transform(x=0, y=0, rotation=45, scale_x=2.0, scale_y=2.0)

        assert transform.rotation == 45
        assert transform.scale_x == 2.0
        assert transform.scale_y == 2.0

    @pytest.mark.parametrize(
        "x,y,expected_x,expected_y",
        [
            (0, 0, 0, 0),
            (100, 200, 100, 200),
            (-50, -75, -50, -75),
            (1000.5, 2000.7, 1000.5, 2000.7),
        ],
    )
    def test_transform_positions(self, x, y, expected_x, expected_y):
        """Test transform at various positions."""
        transform = Transform(x=x, y=y)

        assert transform.x == expected_x
        assert transform.y == expected_y


class TestGridPositionComponent:
    """Test suite for GridPosition component."""

    def test_create_grid_position(self):
        """Test creating a grid position component."""
        grid_pos = GridPosition(grid_x=5, grid_y=10)

        assert grid_pos.x == 5
        assert grid_pos.y == 10

    @pytest.mark.parametrize(
        "x,y",
        [
            (0, 0),
            (10, 10),
            (100, 200),
            (-5, -10),  # Negative grid positions
        ],
    )
    def test_grid_position_values(self, x, y):
        """Test grid position with various values."""
        grid_pos = GridPosition(grid_x=x, grid_y=y)

        assert grid_pos.x == x
        assert grid_pos.y == y


class TestHealthComponent:
    """Test suite for Health component."""

    def test_create_health(self):
        """Test creating a health component."""
        health = Health(current=100, maximum=100)

        assert health.current == 100
        assert health.maximum == 100

    def test_take_damage(self):
        """Test reducing health."""
        health = Health(current=100, maximum=100)

        health.current -= 25

        assert health.current == 75
        assert health.maximum == 100

    def test_heal(self):
        """Test healing."""
        health = Health(current=50, maximum=100)

        health.current += 30

        assert health.current == 80

    def test_overheal_not_capped(self):
        """Test that healing beyond max_hp is allowed (game logic handles cap)."""
        health = Health(current=90, maximum=100)

        health.current += 50

        # Component itself doesn't enforce the cap
        assert health.current == 140

    def test_death(self):
        """Test health reaching zero."""
        health = Health(current=10, maximum=100)

        health.current = 0

        assert health.current == 0


class TestSurvivalComponent:
    """Test suite for Survival component."""

    def test_create_survival(self):
        """Test creating a survival component."""
        survival = Survival(hunger=100, thirst=100, energy=100)

        assert survival.hunger == 100
        assert survival.thirst == 100
        assert survival.energy == 100

    def test_deplete_survival_stats(self):
        """Test depleting survival stats."""
        survival = Survival(hunger=100, thirst=100, energy=100)

        survival.hunger -= 20
        survival.thirst -= 30
        survival.energy -= 40

        assert survival.hunger == 80
        assert survival.thirst == 70
        assert survival.energy == 60

    def test_restore_survival_stats(self):
        """Test restoring survival stats."""
        survival = Survival(hunger=50, thirst=60, energy=70)

        survival.hunger += 30
        survival.thirst += 25
        survival.energy += 20

        assert survival.hunger == 80
        assert survival.thirst == 85
        assert survival.energy == 90


class TestBuildingComponent:
    """Test suite for Building component."""

    def test_create_building(self):
        """Test creating a building component."""
        building = Building(building_type="house", placed_at=(10, 15), level=1)

        assert building.building_type == "house"
        assert building.level == 1

    def test_upgrade_building(self):
        """Test upgrading a building."""
        building = Building(building_type="house", placed_at=(10, 15), level=1)

        building.level += 1

        assert building.level == 2

    @pytest.mark.parametrize(
        "building_type,expected",
        [
            ("house", "house"),
            ("farm", "farm"),
            ("barracks", "barracks"),
            ("wall", "wall"),
        ],
    )
    def test_building_types(self, building_type, expected):
        """Test various building types."""
        building = Building(building_type=building_type, placed_at=(0, 0), level=1)

        assert building.building_type == expected


class TestResourceStorageComponent:
    """Test suite for ResourceStorage component."""

    def test_create_resource_storage(self):
        """Test creating a resource storage component."""
        storage = ResourceStorage(resources={"wood": 100, "stone": 50})

        assert storage.resources["wood"] == 100
        assert storage.resources["stone"] == 50

    def test_add_resources(self):
        """Test adding resources to storage."""
        storage = ResourceStorage(resources={"wood": 100})

        storage.resources["wood"] += 50

        assert storage.resources["wood"] == 150

    def test_remove_resources(self):
        """Test removing resources from storage."""
        storage = ResourceStorage(resources={"wood": 100})

        storage.resources["wood"] -= 30

        assert storage.resources["wood"] == 70

    def test_add_new_resource_type(self):
        """Test adding a new resource type."""
        storage = ResourceStorage(resources={"wood": 100})

        storage.resources["iron"] = 25

        assert "iron" in storage.resources
        assert storage.resources["iron"] == 25


class TestColliderComponent:
    """Test suite for Collider component."""

    def test_create_box_collider(self):
        """Test creating a box collider."""
        collider = Collider(width=32, height=32)

        assert collider.width == 32
        assert collider.height == 32

    def test_create_circle_collider(self):
        """Test creating a circle collider."""
        collider = Collider(radius=16)


    @pytest.mark.parametrize(
        "shape,width,height",
        [
            (16, 16),
            (32, 64),
            (64, 32),
        ],
    )
    def test_collider_sizes(self, shape, width, height):
        """Test colliders of various sizes."""
        collider = Collider(width=width, height=height)

        assert collider.width == width
        assert collider.height == height


class TestRigidBodyComponent:
    """Test suite for RigidBody component."""

    def test_create_rigidbody(self):
        """Test creating a rigidbody component."""
        rb = RigidBody(velocity_x=0, velocity_y=0, mass=1.0)

        assert rb.velocity_x == 0.0 and rb.velocity_y == 0.0
        assert rb.velocity_x
        assert rb.mass == 1.0

    def test_apply_velocity(self):
        """Test applying velocity to rigidbody."""
        rb = RigidBody(velocity_x=0, velocity_y=0, mass=1.0)

        rb.velocity_x = 5
        rb.velocity_y = 10

        assert rb.velocity_x == 0.0 and rb.velocity_y == 0.0

    def test_apply_acceleration(self):
        """Test applying acceleration to rigidbody."""
        rb = RigidBody(velocity_x=0, velocity_y=0, mass=1.0)

        rb.velocity_x = 2
        rb.velocity_y = 3

        assert rb.velocity_x

    @pytest.mark.parametrize(
        "mass",
        [0.1, 0.5, 1.0, 2.0, 10.0, 100.0],
    )
    def test_different_masses(self, mass):
        """Test rigidbodies with different masses."""
        rb = RigidBody(velocity_x=0, velocity_y=0, mass=mass)

        assert rb.mass == mass


class TestTurnActorComponent:
    """Test suite for TurnActor component."""

    def test_create_turn_actor(self):
        """Test creating a turn actor component."""
        actor = TurnActor(action_points=10, max_action_points=10, initiative=15)

        assert actor.action_points == 10
        assert actor.max_ap == 10
        assert actor.initiative == 15

    def test_spend_action_points(self):
        """Test spending action points."""
        actor = TurnActor(action_points=10, max_action_points=10, initiative=15)

        actor.action_points -= 3

        assert actor.action_points == 7

    def test_restore_action_points(self):
        """Test restoring action points."""
        actor = TurnActor(action_points=5, max_action_points=10, initiative=15)

        actor.action_points = actor.max_ap

        assert actor.action_points == 10


class TestWorld:
    """Test suite for World class."""

    def test_create_world(self):
        """Test creating a world."""
        world = World()

        assert world is not None
        assert len(world.entities) == 0
        assert len(world.systems) == 0

    def test_create_entity(self, world):
        """Test creating an entity in the world."""
        entity = world.create_entity("TestEntity")

        assert entity is not None
        assert entity.name == "TestEntity"
        assert entity in world.entities

    def test_create_multiple_entities(self, world):
        """Test creating multiple entities."""
        entity1 = world.create_entity("Entity1")
        entity2 = world.create_entity("Entity2")
        entity3 = world.create_entity("Entity3")

        assert len(world.entities) == 3
        assert entity1 in world.entities
        assert entity2 in world.entities
        assert entity3 in world.entities

    def test_remove_entity(self, world):
        """Test removing an entity from the world."""
        entity = world.create_entity("TestEntity")

        world.remove_entity(entity)

        assert entity not in world.entities
        assert len(world.entities) == 0

    def test_get_entity_by_id(self, world):
        """Test getting an entity by ID."""
        entity = world.create_entity("TestEntity")
        entity_id = entity.id

        retrieved = world.get_entity(entity_id)

        assert retrieved is entity
        assert retrieved.id == entity_id

    def test_get_nonexistent_entity(self, world):
        """Test getting an entity that doesn't exist."""
        result = world.get_entity("nonexistent_id")

        assert result is None

    def test_get_entities_with_component(self, world):
        """Test querying entities with a specific component."""
        entity1 = world.create_entity("Entity1")
        entity1.add_component(Transform(x=0, y=0))

        entity2 = world.create_entity("Entity2")
        entity2.add_component(Transform(x=10, y=10))

        entity3 = world.create_entity("Entity3")
        entity3.add_component(Health(current=100, maximum=100))

        entities_with_transform = world.get_entities_with_component(Transform)

        assert len(entities_with_transform) == 2
        assert entity1 in entities_with_transform
        assert entity2 in entities_with_transform
        assert entity3 not in entities_with_transform

    def test_get_entities_with_tag(self, world):
        """Test querying entities with a specific tag."""
        entity1 = world.create_entity("Entity1")
        entity1.add_tag("player")

        entity2 = world.create_entity("Entity2")
        entity2.add_tag("enemy")

        entity3 = world.create_entity("Entity3")
        entity3.add_tag("enemy")

        entities_with_enemy_tag = world.get_entities_with_tag("enemy")

        assert len(entities_with_enemy_tag) == 2
        assert entity1 not in entities_with_enemy_tag
        assert entity2 in entities_with_enemy_tag
        assert entity3 in entities_with_enemy_tag

    def test_get_entities_with_multiple_components(self, world):
        """Test querying entities with multiple components."""
        entity1 = world.create_entity("Entity1")
        entity1.add_component(Transform(x=0, y=0))
        entity1.add_component(Health(current=100, maximum=100))

        entity2 = world.create_entity("Entity2")
        entity2.add_component(Transform(x=10, y=10))

        entity3 = world.create_entity("Entity3")
        entity3.add_component(Health(current=50, maximum=50))

        # Entities with both Transform and Health
        entities_with_transform = world.get_entities_with_component(Transform)
        entities_with_both = [
            e for e in entities_with_transform if e.has_component(Health)
        ]

        assert len(entities_with_both) == 1
        assert entity1 in entities_with_both

    def test_add_system(self, world):
        """Test adding a system to the world."""

        class TestSystem(System):
            def update(self, dt, world):
                pass

        system = TestSystem()
        world.add_system(system)

        assert system in world.systems
        assert len(world.systems) == 1

    def test_add_multiple_systems(self, world):
        """Test adding multiple systems."""

        class System1(System):
            def update(self, dt, world):
                pass

        class System2(System):
            def update(self, dt, world):
                pass

        system1 = System1()
        system2 = System2()

        world.add_system(system1)
        world.add_system(system2)

        assert len(world.systems) == 2
        assert system1 in world.systems
        assert system2 in world.systems

    def test_remove_system(self, world):
        """Test removing a system from the world."""

        class TestSystem(System):
            def update(self, dt, world):
                pass

        system = TestSystem()
        world.add_system(system)

        world.remove_system(system)

        assert system not in world.systems
        assert len(world.systems) == 0

    def test_update_systems(self, world):
        """Test updating all systems."""
        update_count = []

        class TestSystem(System):
            def update(self, dt, world):
                update_count.append(dt)

        system = TestSystem()
        world.add_system(system)

        world.update(0.016)  # 60 FPS delta time

        assert len(update_count) == 1
        assert update_count[0] == 0.016

    def test_clear_world(self, world):
        """Test clearing all entities from the world."""
        world.create_entity("Entity1")
        world.create_entity("Entity2")
        world.create_entity("Entity3")

        world.clear()

        assert len(world.entities) == 0


class TestSystem:
    """Test suite for System base class."""

    def test_create_system(self):
        """Test creating a system."""

        class TestSystem(System):
            def update(self, dt, world):
                pass

        system = TestSystem()

        assert system is not None

    def test_system_update(self, world):
        """Test system update is called."""
        was_updated = []

        class TestSystem(System):
            def update(self, dt, world):
                was_updated.append(True)

        system = TestSystem()
        system.update(0.016, world)

        assert len(was_updated) == 1

    def test_system_processes_entities(self, world):
        """Test system processing entities."""
        processed_entities = []

        class MovementSystem(System):
            def update(self, dt, world):
                entities = world.get_entities_with_component(Transform)
                for entity in entities:
                    processed_entities.append(entity)

        entity1 = world.create_entity("Entity1")
        entity1.add_component(Transform(x=0, y=0))

        entity2 = world.create_entity("Entity2")
        entity2.add_component(Transform(x=10, y=10))

        system = MovementSystem()
        system.update(0.016, world)

        assert len(processed_entities) == 2
        assert entity1 in processed_entities
        assert entity2 in processed_entities
