"""
Base Building System

Manage construction, upgrades, and building functionality.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from neonworks.core.ecs import (Building, Entity, GridPosition,
                                ResourceStorage, System, World)
from neonworks.core.events import (Event, EventManager, EventType,
                                   get_event_manager)


@dataclass
class BuildingTemplate:
    """Template for building types"""

    building_type: str
    name: str
    description: str

    # Construction requirements
    construction_cost: Dict[str, float]
    construction_time: float  # In turns

    # Upgrade costs
    upgrade_costs: Dict[int, Dict[str, float]]  # level -> resources

    # Functionality
    provides_storage: Dict[str, float] = None  # Resource storage
    produces_per_turn: Dict[str, float] = None  # Resource production
    consumes_per_turn: Dict[str, float] = None  # Resource consumption

    # Requirements
    requires_buildings: list = None  # Other buildings needed

    def __post_init__(self):
        if self.provides_storage is None:
            self.provides_storage = {}
        if self.produces_per_turn is None:
            self.produces_per_turn = {}
        if self.consumes_per_turn is None:
            self.consumes_per_turn = {}
        if self.requires_buildings is None:
            self.requires_buildings = []


class BuildingLibrary:
    """Library of building templates"""

    def __init__(self):
        self.templates: Dict[str, BuildingTemplate] = {}
        self._initialize_default_buildings()

    def _initialize_default_buildings(self):
        """Initialize default building types"""
        # Storage
        self.register_template(
            BuildingTemplate(
                building_type="warehouse",
                name="Warehouse",
                description="Stores resources",
                construction_cost={"metal": 50, "energy": 20},
                construction_time=3,
                upgrade_costs={
                    2: {"metal": 100, "energy": 40},
                    3: {"metal": 200, "energy": 80},
                },
                provides_storage={"metal": 500, "food": 300, "water": 200},
            )
        )

        # Production
        self.register_template(
            BuildingTemplate(
                building_type="generator",
                name="Power Generator",
                description="Generates energy",
                construction_cost={"metal": 100, "components": 20},
                construction_time=5,
                upgrade_costs={
                    2: {"metal": 200, "components": 40},
                    3: {"metal": 400, "components": 80},
                },
                produces_per_turn={"energy": 10},
            )
        )

        # Food production
        self.register_template(
            BuildingTemplate(
                building_type="hydroponics",
                name="Hydroponics Bay",
                description="Grows food",
                construction_cost={"metal": 80, "water": 50, "energy": 30},
                construction_time=4,
                upgrade_costs={
                    2: {"metal": 160, "water": 100, "energy": 60},
                    3: {"metal": 320, "water": 200, "energy": 120},
                },
                produces_per_turn={"food": 5},
                consumes_per_turn={"water": 2, "energy": 3},
            )
        )

        # Defense
        self.register_template(
            BuildingTemplate(
                building_type="turret",
                name="Defense Turret",
                description="Automated defense",
                construction_cost={"metal": 150, "components": 30, "energy": 40},
                construction_time=6,
                upgrade_costs={
                    2: {"metal": 300, "components": 60, "energy": 80},
                    3: {"metal": 600, "components": 120, "energy": 160},
                },
                consumes_per_turn={"energy": 2},
            )
        )

        # Medical
        self.register_template(
            BuildingTemplate(
                building_type="medbay",
                name="Medical Bay",
                description="Heals units",
                construction_cost={"metal": 100, "medical_supplies": 50, "energy": 30},
                construction_time=5,
                upgrade_costs={
                    2: {"metal": 200, "medical_supplies": 100, "energy": 60},
                    3: {"metal": 400, "medical_supplies": 200, "energy": 120},
                },
                consumes_per_turn={"energy": 2, "medical_supplies": 1},
            )
        )

        # Research
        self.register_template(
            BuildingTemplate(
                building_type="lab",
                name="Research Lab",
                description="Unlocks new technologies",
                construction_cost={"metal": 200, "components": 50, "energy": 50},
                construction_time=8,
                upgrade_costs={
                    2: {"metal": 400, "components": 100, "energy": 100},
                    3: {"metal": 800, "components": 200, "energy": 200},
                },
                consumes_per_turn={"energy": 5},
            )
        )

    def register_template(self, template: BuildingTemplate):
        """Register a building template"""
        self.templates[template.building_type] = template

    def get_template(self, building_type: str) -> Optional[BuildingTemplate]:
        """Get a building template"""
        return self.templates.get(building_type)


class BuildingSystem(System):
    """Manages building construction and functionality"""

    def __init__(self, building_library: BuildingLibrary):
        super().__init__()
        self.priority = -50

        self.library = building_library
        self.event_manager = get_event_manager()

        # Track buildings under construction
        self.construction_progress: Dict[str, float] = {}

    def update(self, world: World, delta_time: float):
        """Update buildings"""
        buildings = world.get_entities_with_component(Building)

        for entity in buildings:
            building = entity.get_component(Building)
            template = self.library.get_template(building.building_type)

            if not template:
                continue

            # Update construction
            if not building.is_constructed:
                self._update_construction(entity, building, template, delta_time)
            else:
                # Handle production/consumption
                self._update_production(entity, building, template)

    def _update_construction(
        self,
        entity: Entity,
        building: Building,
        template: BuildingTemplate,
        delta_time: float,
    ):
        """Update building construction"""
        # Progress construction (simplified - assumes one turn = 1.0 progress units)
        progress_per_second = 1.0 / (
            template.construction_time * 60
        )  # Assuming 60s per turn
        building.construction_progress += progress_per_second * delta_time

        if building.construction_progress >= 1.0:
            building.construction_progress = 1.0
            building.is_constructed = True

            # Emit completion event
            self.event_manager.emit(
                Event(
                    EventType.BUILDING_COMPLETED,
                    {"entity_id": entity.id, "building_type": building.building_type},
                )
            )

            # Add storage capacity if provided
            if template.provides_storage:
                storage = entity.get_component(ResourceStorage)
                if not storage:
                    storage = ResourceStorage()
                    entity.add_component(storage)

                for resource, capacity in template.provides_storage.items():
                    storage.capacity[resource] = capacity * building.level

    def _update_production(
        self, entity: Entity, building: Building, template: BuildingTemplate
    ):
        """Update resource production/consumption"""
        storage = entity.get_component(ResourceStorage)
        if not storage:
            return

        # Produce resources
        if template.produces_per_turn:
            for resource, amount in template.produces_per_turn.items():
                production = amount * building.level
                storage.add_resource(resource, production)

        # Consume resources
        if template.consumes_per_turn:
            for resource, amount in template.consumes_per_turn.items():
                consumption = amount * building.level
                storage.remove_resource(resource, consumption)

    def place_building(
        self,
        world: World,
        building_type: str,
        grid_x: int,
        grid_y: int,
        player_resources: ResourceStorage,
    ) -> Optional[Entity]:
        """Place a new building"""
        template = self.library.get_template(building_type)
        if not template:
            return None

        # Check if player has resources
        for resource, cost in template.construction_cost.items():
            if player_resources.resources.get(resource, 0) < cost:
                return None

        # Deduct resources
        for resource, cost in template.construction_cost.items():
            player_resources.remove_resource(resource, cost)

        # Create building entity
        entity = world.create_entity()
        entity.add_tag("building")

        # Add components
        entity.add_component(GridPosition(grid_x=grid_x, grid_y=grid_y, layer=0))
        entity.add_component(
            Building(
                building_type=building_type,
                construction_progress=0.0,
                is_constructed=False,
                level=1,
                max_level=3,
            )
        )

        # Emit placement event
        self.event_manager.emit(
            Event(
                EventType.BUILDING_PLACED,
                {
                    "entity_id": entity.id,
                    "building_type": building_type,
                    "grid_x": grid_x,
                    "grid_y": grid_y,
                },
            )
        )

        return entity

    def upgrade_building(
        self, entity: Entity, player_resources: ResourceStorage
    ) -> bool:
        """Upgrade a building"""
        building = entity.get_component(Building)
        if not building or not building.is_constructed:
            return False

        if building.level >= building.max_level:
            return False

        template = self.library.get_template(building.building_type)
        if not template:
            return False

        # Check upgrade cost
        next_level = building.level + 1
        upgrade_cost = template.upgrade_costs.get(next_level, {})

        for resource, cost in upgrade_cost.items():
            if player_resources.resources.get(resource, 0) < cost:
                return False

        # Deduct resources
        for resource, cost in upgrade_cost.items():
            player_resources.remove_resource(resource, cost)

        # Upgrade building
        building.level = next_level

        # Emit upgrade event
        self.event_manager.emit(
            Event(
                EventType.BUILDING_UPGRADED,
                {
                    "entity_id": entity.id,
                    "building_type": building.building_type,
                    "new_level": building.level,
                },
            )
        )

        return True

    def demolish_building(self, world: World, entity: Entity):
        """Demolish a building"""
        building = entity.get_component(Building)
        if not building:
            return

        # Emit destruction event
        self.event_manager.emit(
            Event(
                EventType.BUILDING_DESTROYED,
                {"entity_id": entity.id, "building_type": building.building_type},
            )
        )

        # Remove entity
        world.remove_entity(entity.id)
