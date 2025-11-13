"""
Entity Component System (ECS)

A flexible ECS implementation for managing game entities, components, and systems.
"""

from typing import Dict, List, Type, Optional, Set, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid


class Component:
    """Base class for all components"""
    pass


@dataclass
class Transform(Component):
    """Position, rotation, and scale"""
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0


@dataclass
class GridPosition(Component):
    """Grid-based position for tile-based games"""
    grid_x: int = 0
    grid_y: int = 0
    layer: int = 0  # For multi-layer maps


@dataclass
class Sprite(Component):
    """Visual representation"""
    texture: str = ""
    width: int = 32
    height: int = 32
    color: tuple = (255, 255, 255, 255)
    visible: bool = True


@dataclass
class Health(Component):
    """Health component for survival and combat"""
    current: float = 100.0
    maximum: float = 100.0
    regeneration: float = 0.0


@dataclass
class Survival(Component):
    """Survival needs"""
    hunger: float = 100.0  # 0 = starving, 100 = full
    thirst: float = 100.0  # 0 = dehydrated, 100 = hydrated
    energy: float = 100.0  # 0 = exhausted, 100 = well-rested

    hunger_rate: float = 1.0  # Points per turn
    thirst_rate: float = 1.5  # Points per turn
    energy_rate: float = 0.5  # Points per turn


@dataclass
class Building(Component):
    """Base building component"""
    building_type: str = ""
    construction_progress: float = 0.0  # 0.0 to 1.0
    is_constructed: bool = False
    level: int = 1
    max_level: int = 3


@dataclass
class ResourceStorage(Component):
    """Resource storage for buildings and characters"""
    resources: Dict[str, float] = field(default_factory=dict)
    capacity: Dict[str, float] = field(default_factory=dict)

    def add_resource(self, resource_type: str, amount: float) -> float:
        """Add resource, return amount that didn't fit"""
        current = self.resources.get(resource_type, 0.0)
        capacity = self.capacity.get(resource_type, float('inf'))

        new_amount = min(current + amount, capacity)
        self.resources[resource_type] = new_amount

        return amount - (new_amount - current)

    def remove_resource(self, resource_type: str, amount: float) -> float:
        """Remove resource, return amount actually removed"""
        current = self.resources.get(resource_type, 0.0)
        removed = min(current, amount)
        self.resources[resource_type] = current - removed
        return removed


@dataclass
class Navmesh(Component):
    """Navmesh data for pathfinding"""
    walkable_cells: Set[tuple] = field(default_factory=set)  # Set of (x, y) tuples
    cost_multipliers: Dict[tuple, float] = field(default_factory=dict)  # Movement costs

    def is_walkable(self, x: int, y: int) -> bool:
        return (x, y) in self.walkable_cells

    def get_cost(self, x: int, y: int) -> float:
        return self.cost_multipliers.get((x, y), 1.0)


@dataclass
class TurnActor(Component):
    """Entity that can act in turn-based system"""
    action_points: int = 2
    max_action_points: int = 2
    initiative: int = 10
    has_acted: bool = False


@dataclass
class Collider(Component):
    """Collision box for physics and collision detection"""
    width: float = 32.0
    height: float = 32.0
    offset_x: float = 0.0  # Offset from transform position
    offset_y: float = 0.0
    is_trigger: bool = False  # If true, detects collisions but doesn't block movement
    layer: int = 0  # Collision layer (0-31)
    mask: int = 0xFFFFFFFF  # Which layers this collider can collide with


@dataclass
class RigidBody(Component):
    """Physics body for movement and collision response"""
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    mass: float = 1.0
    friction: float = 0.1
    is_static: bool = False  # Static bodies don't move
    gravity_scale: float = 0.0  # For top-down games, usually 0


class Entity:
    """Represents a game entity with a unique ID and components"""

    def __init__(self, entity_id: Optional[str] = None):
        self.id = entity_id or str(uuid.uuid4())
        self._components: Dict[Type[Component], Component] = {}
        self.tags: Set[str] = set()
        self.active: bool = True
        self._world: Optional['World'] = None  # Reference to the world this entity belongs to

    def add_component(self, component: Component) -> 'Entity':
        """Add a component to this entity"""
        component_type = type(component)
        self._components[component_type] = component

        # Update world's component index if entity is in a world
        if self._world is not None:
            if component_type not in self._world._component_to_entities:
                self._world._component_to_entities[component_type] = set()
            self._world._component_to_entities[component_type].add(self.id)

        return self

    def remove_component(self, component_type: Type[Component]) -> 'Entity':
        """Remove a component from this entity"""
        if component_type in self._components:
            del self._components[component_type]

            # Update world's component index if entity is in a world
            if self._world is not None and component_type in self._world._component_to_entities:
                self._world._component_to_entities[component_type].discard(self.id)

        return self

    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        """Get a component of the specified type"""
        return self._components.get(component_type)

    def has_component(self, component_type: Type[Component]) -> bool:
        """Check if entity has a component of the specified type"""
        return component_type in self._components

    def has_components(self, *component_types: Type[Component]) -> bool:
        """Check if entity has all specified components"""
        return all(ct in self._components for ct in component_types)

    def add_tag(self, tag: str) -> 'Entity':
        """Add a tag to this entity"""
        self.tags.add(tag)
        return self

    def remove_tag(self, tag: str) -> 'Entity':
        """Remove a tag from this entity"""
        self.tags.discard(tag)
        return self

    def has_tag(self, tag: str) -> bool:
        """Check if entity has a tag"""
        return tag in self.tags


class System(ABC):
    """Base class for all systems that process entities"""

    def __init__(self):
        self.enabled = True
        self.priority = 0  # Lower numbers run first

    @abstractmethod
    def update(self, world: 'World', delta_time: float):
        """Update this system"""
        pass

    def on_entity_added(self, entity: Entity):
        """Called when an entity is added to the world"""
        pass

    def on_entity_removed(self, entity: Entity):
        """Called when an entity is removed from the world"""
        pass


class World:
    """Manages all entities and systems"""

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._systems: List[System] = []
        self._tags_to_entities: Dict[str, Set[str]] = {}

        # Component indexing for fast queries
        self._component_to_entities: Dict[Type[Component], Set[str]] = {}

    def create_entity(self, entity_id: Optional[str] = None) -> Entity:
        """Create a new entity"""
        entity = Entity(entity_id)
        self.add_entity(entity)
        return entity

    def add_entity(self, entity: Entity) -> 'World':
        """Add an existing entity to the world"""
        self._entities[entity.id] = entity

        # Set the entity's world reference
        entity._world = self

        # Index tags
        for tag in entity.tags:
            if tag not in self._tags_to_entities:
                self._tags_to_entities[tag] = set()
            self._tags_to_entities[tag].add(entity.id)

        # Index components
        for component_type in entity._components.keys():
            if component_type not in self._component_to_entities:
                self._component_to_entities[component_type] = set()
            self._component_to_entities[component_type].add(entity.id)

        # Notify systems
        for system in self._systems:
            system.on_entity_added(entity)

        return self

    def remove_entity(self, entity_id: str) -> 'World':
        """Remove an entity from the world"""
        if entity_id not in self._entities:
            return self

        entity = self._entities[entity_id]

        # Notify systems
        for system in self._systems:
            system.on_entity_removed(entity)

        # Remove from tag index
        for tag in entity.tags:
            if tag in self._tags_to_entities:
                self._tags_to_entities[tag].discard(entity_id)

        # Remove from component index
        for component_type in entity._components.keys():
            if component_type in self._component_to_entities:
                self._component_to_entities[component_type].discard(entity_id)

        # Clear the entity's world reference
        entity._world = None

        del self._entities[entity_id]
        return self

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID"""
        return self._entities.get(entity_id)

    def get_entities(self) -> List[Entity]:
        """Get all entities"""
        return list(self._entities.values())

    def get_entities_with_component(self, component_type: Type[Component]) -> List[Entity]:
        """Get all entities that have a specific component"""
        entity_ids = self._component_to_entities.get(component_type, set())
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]

    def get_entities_with_components(self, *component_types: Type[Component]) -> List[Entity]:
        """Get all entities that have all specified components"""
        if not component_types:
            return []

        # Start with entities that have the first component
        result_ids = self._component_to_entities.get(component_types[0], set()).copy()

        # Intersect with entities that have other components
        for component_type in component_types[1:]:
            result_ids &= self._component_to_entities.get(component_type, set())

        return [self._entities[eid] for eid in result_ids if eid in self._entities]

    def get_entities_with_tag(self, tag: str) -> List[Entity]:
        """Get all entities with a specific tag"""
        entity_ids = self._tags_to_entities.get(tag, set())
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]

    def add_system(self, system: System) -> 'World':
        """Add a system to the world"""
        self._systems.append(system)
        self._systems.sort(key=lambda s: s.priority)
        return self

    def remove_system(self, system: System) -> 'World':
        """Remove a system from the world"""
        if system in self._systems:
            self._systems.remove(system)
        return self

    def update(self, delta_time: float):
        """Update all systems"""
        for system in self._systems:
            if system.enabled:
                system.update(self, delta_time)

    def clear(self):
        """Remove all entities and systems"""
        self._entities.clear()
        self._systems.clear()
        self._tags_to_entities.clear()
        self._component_to_entities.clear()
