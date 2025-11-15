"""
Tests for Base Building System

Tests building construction, upgrades, production, and resource management.
"""

import pytest

from neonworks.core.ecs import Building, Entity, GridPosition, ResourceStorage, World
from neonworks.core.events import EventType, get_event_manager
from neonworks.systems.base_building import (
    BuildingLibrary,
    BuildingSystem,
    BuildingTemplate,
)


class TestBuildingTemplate:
    """Test building template"""

    def test_building_template_creation(self):
        """Test creating a building template"""
        template = BuildingTemplate(
            building_type="test_building",
            name="Test Building",
            description="A test building",
            construction_cost={"metal": 100},
            construction_time=5,
            upgrade_costs={2: {"metal": 200}},
        )

        assert template.building_type == "test_building"
        assert template.name == "Test Building"
        assert template.construction_cost == {"metal": 100}
        assert template.construction_time == 5

    def test_template_defaults_initialized(self):
        """Test that template defaults are properly initialized"""
        template = BuildingTemplate(
            building_type="test",
            name="Test",
            description="Test",
            construction_cost={},
            construction_time=1,
            upgrade_costs={},
        )

        assert template.provides_storage == {}
        assert template.produces_per_turn == {}
        assert template.consumes_per_turn == {}
        assert template.requires_buildings == []

    def test_template_with_production(self):
        """Test template with resource production"""
        template = BuildingTemplate(
            building_type="generator",
            name="Generator",
            description="Produces energy",
            construction_cost={"metal": 50},
            construction_time=3,
            upgrade_costs={},
            produces_per_turn={"energy": 10},
        )

        assert template.produces_per_turn == {"energy": 10}

    def test_template_with_consumption(self):
        """Test template with resource consumption"""
        template = BuildingTemplate(
            building_type="factory",
            name="Factory",
            description="Consumes resources",
            construction_cost={"metal": 100},
            construction_time=5,
            upgrade_costs={},
            consumes_per_turn={"energy": 5, "water": 2},
        )

        assert template.consumes_per_turn == {"energy": 5, "water": 2}


class TestBuildingLibrary:
    """Test building library"""

    def test_library_creation(self):
        """Test creating building library"""
        library = BuildingLibrary()

        assert library is not None
        assert len(library.templates) > 0  # Has default buildings

    def test_register_template(self):
        """Test registering a building template"""
        library = BuildingLibrary()

        template = BuildingTemplate(
            building_type="custom",
            name="Custom",
            description="Custom building",
            construction_cost={"metal": 50},
            construction_time=2,
            upgrade_costs={},
        )

        library.register_template(template)

        assert "custom" in library.templates
        assert library.templates["custom"] == template

    def test_get_template(self):
        """Test getting a building template"""
        library = BuildingLibrary()

        warehouse = library.get_template("warehouse")

        assert warehouse is not None
        assert warehouse.name == "Warehouse"
        assert warehouse.building_type == "warehouse"

    def test_get_nonexistent_template(self):
        """Test getting template that doesn't exist"""
        library = BuildingLibrary()

        template = library.get_template("nonexistent")

        assert template is None

    def test_default_buildings_registered(self):
        """Test that default buildings are registered"""
        library = BuildingLibrary()

        assert library.get_template("warehouse") is not None
        assert library.get_template("generator") is not None
        assert library.get_template("hydroponics") is not None
        assert library.get_template("turret") is not None
        assert library.get_template("medbay") is not None
        assert library.get_template("lab") is not None


class TestBuildingSystem:
    """Test building system"""

    def test_building_system_creation(self):
        """Test creating building system"""
        library = BuildingLibrary()
        system = BuildingSystem(library)

        assert system is not None
        assert system.priority == -50
        assert system.library == library

    def test_place_building(self):
        """Test placing a new building"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Create player resources
        resources = ResourceStorage()
        resources.add_resource("metal", 100)
        resources.add_resource("energy", 50)

        # Place building
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        assert entity is not None
        assert entity.has_component(Building)
        assert entity.has_component(GridPosition)
        assert entity.has_tag("building")

        # Check resources were deducted
        assert resources.resources["metal"] == 50  # 100 - 50 cost
        assert resources.resources["energy"] == 30  # 50 - 20 cost

    def test_place_building_insufficient_resources(self):
        """Test placing building without enough resources"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Create player resources (insufficient)
        resources = ResourceStorage()
        resources.add_resource("metal", 10)  # Not enough

        # Try to place building
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        assert entity is None
        assert resources.resources["metal"] == 10  # Resources unchanged

    def test_place_nonexistent_building(self):
        """Test placing building type that doesn't exist"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        resources = ResourceStorage()
        resources.add_resource("metal", 1000)

        entity = system.place_building(world, "nonexistent", 0, 0, resources)

        assert entity is None


class TestBuildingConstruction:
    """Test building construction mechanics"""

    def test_building_construction_progress(self):
        """Test that buildings construct over time"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place building
        resources = ResourceStorage()
        resources.add_resource("metal", 100)
        resources.add_resource("energy", 50)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        building = entity.get_component(Building)
        assert building.construction_progress == 0.0
        assert building.is_constructed is False

        # Update to progress construction
        system.update(world, 60.0)  # 1 minute

        building = entity.get_component(Building)
        assert building.construction_progress > 0.0

    def test_building_completes_construction(self):
        """Test that building completes after enough time"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)
        event_manager = get_event_manager()

        events = []

        def on_complete(event):
            events.append(event)

        event_manager.subscribe(EventType.BUILDING_COMPLETED, on_complete)

        # Place building (warehouse has construction_time=3)
        resources = ResourceStorage()
        resources.add_resource("metal", 100)
        resources.add_resource("energy", 50)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        # Update for long enough to complete (3 turns * 60s = 180s)
        system.update(world, 200.0)
        event_manager.process_events()

        building = entity.get_component(Building)
        assert building.is_constructed is True
        assert building.construction_progress == 1.0
        assert len(events) > 0

        event_manager.unsubscribe(EventType.BUILDING_COMPLETED, on_complete)

    def test_storage_added_on_completion(self):
        """Test that storage capacity is added when warehouse completes"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place warehouse
        resources = ResourceStorage()
        resources.add_resource("metal", 100)
        resources.add_resource("energy", 50)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        # Complete construction
        system.update(world, 200.0)

        # Check storage was added
        storage = entity.get_component(ResourceStorage)
        assert storage is not None
        assert "metal" in storage.capacity
        assert "food" in storage.capacity
        assert "water" in storage.capacity


class TestBuildingProduction:
    """Test resource production and consumption"""

    def test_building_produces_resources(self):
        """Test that completed buildings produce resources"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place generator (produces energy)
        resources = ResourceStorage()
        resources.add_resource("metal", 200)
        resources.add_resource("components", 50)
        entity = system.place_building(world, "generator", 5, 10, resources)

        # Complete construction
        building = entity.get_component(Building)
        building.is_constructed = True
        building.construction_progress = 1.0

        # Add storage
        storage = ResourceStorage()
        entity.add_component(storage)

        # Update to trigger production
        system.update(world, 1.0)

        # Check energy was produced
        storage = entity.get_component(ResourceStorage)
        assert storage.resources.get("energy", 0) > 0

    def test_building_consumes_resources(self):
        """Test that buildings consume resources"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place hydroponics (consumes water and energy)
        resources = ResourceStorage()
        resources.add_resource("metal", 200)
        resources.add_resource("water", 100)
        resources.add_resource("energy", 100)
        entity = system.place_building(world, "hydroponics", 5, 10, resources)

        # Complete construction
        building = entity.get_component(Building)
        building.is_constructed = True
        building.construction_progress = 1.0

        # Add storage with resources
        storage = ResourceStorage()
        storage.add_resource("water", 50)
        storage.add_resource("energy", 50)
        entity.add_component(storage)

        initial_water = storage.resources["water"]
        initial_energy = storage.resources["energy"]

        # Update to trigger consumption
        system.update(world, 1.0)

        # Check resources were consumed
        storage = entity.get_component(ResourceStorage)
        assert storage.resources["water"] < initial_water
        assert storage.resources["energy"] < initial_energy

    def test_production_scales_with_level(self):
        """Test that production scales with building level"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place generator
        resources = ResourceStorage()
        resources.add_resource("metal", 200)
        resources.add_resource("components", 50)
        entity = system.place_building(world, "generator", 5, 10, resources)

        # Complete and set level
        building = entity.get_component(Building)
        building.is_constructed = True
        building.construction_progress = 1.0
        building.level = 2  # Level 2

        storage = ResourceStorage()
        entity.add_component(storage)

        # Update
        system.update(world, 1.0)

        level2_production = storage.resources.get("energy", 0)

        # Increase level
        building.level = 3
        storage.resources["energy"] = 0

        # Update again
        system.update(world, 1.0)

        level3_production = storage.resources.get("energy", 0)

        # Level 3 should produce more than level 2
        assert level3_production > level2_production


class TestBuildingUpgrade:
    """Test building upgrades"""

    def test_upgrade_building(self):
        """Test upgrading a building"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)
        event_manager = get_event_manager()

        events = []

        def on_upgrade(event):
            events.append(event)

        event_manager.subscribe(EventType.BUILDING_UPGRADED, on_upgrade)

        # Place and complete building
        resources = ResourceStorage()
        resources.add_resource("metal", 300)
        resources.add_resource("energy", 100)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        building = entity.get_component(Building)
        building.is_constructed = True
        building.construction_progress = 1.0

        # Upgrade building
        success = system.upgrade_building(entity, resources)
        event_manager.process_events()

        assert success is True
        assert building.level == 2
        assert len(events) > 0

        event_manager.unsubscribe(EventType.BUILDING_UPGRADED, on_upgrade)

    def test_upgrade_insufficient_resources(self):
        """Test upgrading without enough resources"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place and complete building
        resources = ResourceStorage()
        resources.add_resource("metal", 100)
        resources.add_resource("energy", 50)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        building = entity.get_component(Building)
        building.is_constructed = True

        # Try to upgrade (insufficient resources)
        success = system.upgrade_building(entity, resources)

        assert success is False
        assert building.level == 1  # Level unchanged

    def test_upgrade_unconstructed_building(self):
        """Test upgrading building that isn't constructed"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place building (not completed)
        resources = ResourceStorage()
        resources.add_resource("metal", 300)
        resources.add_resource("energy", 100)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        # Try to upgrade
        success = system.upgrade_building(entity, resources)

        assert success is False

    def test_upgrade_at_max_level(self):
        """Test upgrading building already at max level"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Place and complete building
        resources = ResourceStorage()
        resources.add_resource("metal", 1000)
        resources.add_resource("energy", 500)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        building = entity.get_component(Building)
        building.is_constructed = True
        building.level = 3  # Max level
        building.max_level = 3

        # Try to upgrade
        success = system.upgrade_building(entity, resources)

        assert success is False
        assert building.level == 3  # Level unchanged


class TestBuildingDemolition:
    """Test building demolition"""

    def test_demolish_building(self):
        """Test demolishing a building"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)
        event_manager = get_event_manager()

        events = []

        def on_destroy(event):
            events.append(event)

        event_manager.subscribe(EventType.BUILDING_DESTROYED, on_destroy)

        # Place building
        resources = ResourceStorage()
        resources.add_resource("metal", 100)
        resources.add_resource("energy", 50)
        entity = system.place_building(world, "warehouse", 5, 10, resources)

        entity_id = entity.id

        # Demolish
        system.demolish_building(world, entity)
        event_manager.process_events()

        # Check building is removed
        assert world.get_entity(entity_id) is None
        assert len(events) > 0

        event_manager.unsubscribe(EventType.BUILDING_DESTROYED, on_destroy)

    def test_demolish_without_building_component(self):
        """Test demolishing entity without Building component"""
        world = World()
        library = BuildingLibrary()
        system = BuildingSystem(library)

        # Create regular entity
        entity = world.create_entity("NotABuilding")

        # Should not crash
        system.demolish_building(world, entity)
