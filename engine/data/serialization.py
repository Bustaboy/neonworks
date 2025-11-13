"""
Serialization System

Save and load game state, entities, and world data.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from engine.core.ecs import World, Entity, Component, GridPosition, Transform, Sprite, Health, Survival, Building, ResourceStorage, TurnActor, Navmesh, Collider, RigidBody
from engine.core.project import Project


class GameSerializer:
    """Serialize and deserialize game state"""

    @staticmethod
    def serialize_component(component: Component) -> Dict[str, Any]:
        """Serialize a component to dict"""
        component_type = type(component).__name__
        data = {
            "_type": component_type,
        }

        # Serialize known component types
        if isinstance(component, GridPosition):
            data.update({
                "grid_x": component.grid_x,
                "grid_y": component.grid_y,
                "layer": component.layer
            })
        elif isinstance(component, Transform):
            data.update({
                "x": component.x,
                "y": component.y,
                "rotation": component.rotation,
                "scale_x": component.scale_x,
                "scale_y": component.scale_y
            })
        elif isinstance(component, Sprite):
            data.update({
                "texture": component.texture,
                "width": component.width,
                "height": component.height,
                "color": component.color,
                "visible": component.visible
            })
        elif isinstance(component, Health):
            data.update({
                "current": component.current,
                "maximum": component.maximum,
                "regeneration": component.regeneration
            })
        elif isinstance(component, Survival):
            data.update({
                "hunger": component.hunger,
                "thirst": component.thirst,
                "energy": component.energy,
                "hunger_rate": component.hunger_rate,
                "thirst_rate": component.thirst_rate,
                "energy_rate": component.energy_rate
            })
        elif isinstance(component, Building):
            data.update({
                "building_type": component.building_type,
                "construction_progress": component.construction_progress,
                "is_constructed": component.is_constructed,
                "level": component.level,
                "max_level": component.max_level
            })
        elif isinstance(component, ResourceStorage):
            data.update({
                "resources": component.resources,
                "capacity": component.capacity
            })
        elif isinstance(component, TurnActor):
            data.update({
                "action_points": component.action_points,
                "max_action_points": component.max_action_points,
                "initiative": component.initiative,
                "has_acted": component.has_acted
            })
        elif isinstance(component, Navmesh):
            data.update({
                "walkable_cells": list(component.walkable_cells),
                "cost_multipliers": {f"{x},{y}": cost for (x, y), cost in component.cost_multipliers.items()}
            })
        elif isinstance(component, Collider):
            data.update({
                "width": component.width,
                "height": component.height,
                "offset_x": component.offset_x,
                "offset_y": component.offset_y,
                "is_trigger": component.is_trigger,
                "layer": component.layer,
                "mask": component.mask
            })
        elif isinstance(component, RigidBody):
            data.update({
                "velocity_x": component.velocity_x,
                "velocity_y": component.velocity_y,
                "mass": component.mass,
                "friction": component.friction,
                "is_static": component.is_static,
                "gravity_scale": component.gravity_scale
            })

        return data

    @staticmethod
    def deserialize_component(data: Dict[str, Any]) -> Optional[Component]:
        """Deserialize a component from dict"""
        component_type = data.get("_type")

        if component_type == "GridPosition":
            return GridPosition(
                grid_x=data["grid_x"],
                grid_y=data["grid_y"],
                layer=data.get("layer", 0)
            )
        elif component_type == "Transform":
            return Transform(
                x=data["x"],
                y=data["y"],
                rotation=data.get("rotation", 0.0),
                scale_x=data.get("scale_x", 1.0),
                scale_y=data.get("scale_y", 1.0)
            )
        elif component_type == "Sprite":
            return Sprite(
                texture=data.get("texture", ""),
                width=data.get("width", 32),
                height=data.get("height", 32),
                color=tuple(data.get("color", [255, 255, 255, 255])),
                visible=data.get("visible", True)
            )
        elif component_type == "Health":
            return Health(
                current=data["current"],
                maximum=data["maximum"],
                regeneration=data.get("regeneration", 0.0)
            )
        elif component_type == "Survival":
            return Survival(
                hunger=data["hunger"],
                thirst=data["thirst"],
                energy=data["energy"],
                hunger_rate=data.get("hunger_rate", 1.0),
                thirst_rate=data.get("thirst_rate", 1.5),
                energy_rate=data.get("energy_rate", 0.5)
            )
        elif component_type == "Building":
            return Building(
                building_type=data["building_type"],
                construction_progress=data["construction_progress"],
                is_constructed=data["is_constructed"],
                level=data.get("level", 1),
                max_level=data.get("max_level", 3)
            )
        elif component_type == "ResourceStorage":
            return ResourceStorage(
                resources=data.get("resources", {}),
                capacity=data.get("capacity", {})
            )
        elif component_type == "TurnActor":
            return TurnActor(
                action_points=data["action_points"],
                max_action_points=data["max_action_points"],
                initiative=data.get("initiative", 10),
                has_acted=data.get("has_acted", False)
            )
        elif component_type == "Navmesh":
            walkable_cells = set(tuple(cell) for cell in data["walkable_cells"])
            cost_multipliers = {}
            for key, cost in data["cost_multipliers"].items():
                x, y = map(int, key.split(','))
                cost_multipliers[(x, y)] = cost

            navmesh = Navmesh()
            navmesh.walkable_cells = walkable_cells
            navmesh.cost_multipliers = cost_multipliers
            return navmesh
        elif component_type == "Collider":
            return Collider(
                width=data["width"],
                height=data["height"],
                offset_x=data.get("offset_x", 0.0),
                offset_y=data.get("offset_y", 0.0),
                is_trigger=data.get("is_trigger", False),
                layer=data.get("layer", 0),
                mask=data.get("mask", 0xFFFFFFFF)
            )
        elif component_type == "RigidBody":
            return RigidBody(
                velocity_x=data.get("velocity_x", 0.0),
                velocity_y=data.get("velocity_y", 0.0),
                mass=data.get("mass", 1.0),
                friction=data.get("friction", 0.1),
                is_static=data.get("is_static", False),
                gravity_scale=data.get("gravity_scale", 0.0)
            )

        return None

    @staticmethod
    def serialize_entity(entity: Entity) -> Dict[str, Any]:
        """Serialize an entity to dict"""
        components = []

        for component in entity._components.values():
            components.append(GameSerializer.serialize_component(component))

        return {
            "id": entity.id,
            "tags": list(entity.tags),
            "active": entity.active,
            "components": components
        }

    @staticmethod
    def deserialize_entity(data: Dict[str, Any]) -> Entity:
        """Deserialize an entity from dict"""
        entity = Entity(entity_id=data["id"])
        entity.active = data.get("active", True)

        # Restore tags
        for tag in data.get("tags", []):
            entity.add_tag(tag)

        # Restore components
        for component_data in data.get("components", []):
            component = GameSerializer.deserialize_component(component_data)
            if component:
                entity.add_component(component)

        return entity

    @staticmethod
    def serialize_world(world: World) -> Dict[str, Any]:
        """Serialize world to dict"""
        entities = []

        for entity in world.get_entities():
            entities.append(GameSerializer.serialize_entity(entity))

        return {
            "entities": entities
        }

    @staticmethod
    def deserialize_world(data: Dict[str, Any]) -> World:
        """Deserialize world from dict"""
        world = World()

        for entity_data in data.get("entities", []):
            entity = GameSerializer.deserialize_entity(entity_data)
            world.add_entity(entity)

        return world


class SaveGameManager:
    """Manage save games"""

    def __init__(self, project: Project):
        self.project = project

    def save_game(self, save_name: str, world: World, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save the game state.

        Args:
            save_name: Name of the save file
            world: World to save
            metadata: Additional metadata (player name, play time, etc.)
        """
        save_path = self.project.get_save_path(save_name)

        try:
            # Serialize world
            world_data = GameSerializer.serialize_world(world)

            # Add metadata
            save_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "project": self.project.config.metadata.name,
                "metadata": metadata or {},
                "world": world_data
            }

            # Write to file
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            print(f"✅ Game saved: {save_name}")
            return True

        except Exception as e:
            print(f"❌ Error saving game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[World]:
        """
        Load a saved game.

        Args:
            save_name: Name of the save file

        Returns:
            World object or None if load failed
        """
        save_path = self.project.get_save_path(save_name)

        if not save_path.exists():
            print(f"❌ Save file not found: {save_name}")
            return None

        try:
            # Read save file
            with open(save_path, 'r') as f:
                save_data = json.load(f)

            # Check version
            if save_data.get("version") != "1.0":
                print("⚠️ Save file version mismatch")

            # Deserialize world
            world = GameSerializer.deserialize_world(save_data["world"])

            print(f"✅ Game loaded: {save_name}")
            print(f"   Timestamp: {save_data.get('timestamp')}")
            print(f"   Entities: {len(world.get_entities())}")

            return world

        except Exception as e:
            print(f"❌ Error loading game: {e}")
            return None

    def list_saves(self) -> list:
        """List all available save files"""
        return self.project.list_saves()

    def delete_save(self, save_name: str) -> bool:
        """Delete a save file"""
        save_path = self.project.get_save_path(save_name)

        if not save_path.exists():
            return False

        try:
            save_path.unlink()
            print(f"🗑️  Deleted save: {save_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting save: {e}")
            return False

    def get_save_info(self, save_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a save file"""
        save_path = self.project.get_save_path(save_name)

        if not save_path.exists():
            return None

        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)

            return {
                "name": save_name,
                "timestamp": save_data.get("timestamp"),
                "project": save_data.get("project"),
                "metadata": save_data.get("metadata", {}),
                "entity_count": len(save_data.get("world", {}).get("entities", []))
            }
        except:
            return None


class AutoSaveManager:
    """Automatic save management"""

    def __init__(self, save_manager: SaveGameManager, interval: int = 300):
        """
        Args:
            save_manager: SaveGameManager instance
            interval: Auto-save interval in seconds (default: 5 minutes)
        """
        self.save_manager = save_manager
        self.interval = interval
        self.last_save_time = 0
        self.auto_save_count = 0
        self.max_auto_saves = 3  # Keep only last 3 auto-saves

    def update(self, world: World, current_time: float):
        """Update auto-save (call every frame)"""
        if current_time - self.last_save_time >= self.interval:
            self._perform_auto_save(world)
            self.last_save_time = current_time

    def _perform_auto_save(self, world: World):
        """Perform an auto-save"""
        auto_save_name = f"autosave_{self.auto_save_count % self.max_auto_saves}"

        metadata = {
            "type": "auto_save",
            "auto_save_index": self.auto_save_count
        }

        self.save_manager.save_game(auto_save_name, world, metadata)
        self.auto_save_count += 1

        print(f"💾 Auto-saved (slot {self.auto_save_count % self.max_auto_saves})")
