"""
NeonWorks Game HUD - Comprehensive Visual Interface
Provides all necessary visual feedback for gameplay systems.
"""

from typing import Dict, List, Optional, Tuple

import pygame

from ..core.ecs import Component, World
from ..rendering.ui import UI


class GameHUD:
    """
    Comprehensive visual HUD for NeonWorks games.
    Displays survival stats, resources, turn info, building info, and more.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.ui = UI(screen)
        self.visible = True
        self.show_survival = True
        self.show_resources = True
        self.show_turn_info = True
        self.show_building_info = True
        self.show_fps = True
        self.selected_entity = None

    def set_selected_entity(self, entity_id: Optional[int]):
        """Set the currently selected entity for inspection."""
        self.selected_entity = entity_id

    def render(self, world: World, fps: float = 60.0):
        """Render the complete HUD."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Top-left: FPS and performance stats
        if self.show_fps:
            self._render_performance_stats(world, fps, 10, 10)

        # Top-center: Turn information
        if self.show_turn_info:
            self._render_turn_info(world, screen_width // 2, 10)

        # Top-right: Resources
        if self.show_resources:
            self._render_resources(world, screen_width - 250, 10)

        # Left side: Selected entity info
        if self.selected_entity is not None:
            self._render_selected_entity(world, 10, 100)

        # Bottom-left: Survival stats for player
        if self.show_survival:
            self._render_survival_stats(world, 10, screen_height - 150)

        # Bottom-right: Building quick info
        if self.show_building_info:
            self._render_building_info(world, screen_width - 250, screen_height - 200)

    def _render_performance_stats(self, world: World, fps: float, x: int, y: int):
        """Render FPS and entity count."""
        entity_count = len(world.entities)

        self.ui.panel(x, y, 200, 80, (0, 0, 0, 180))
        self.ui.label(f"FPS: {fps:.1f}", x + 10, y + 10, size=20, color=(0, 255, 0))
        self.ui.label(f"Entities: {entity_count}", x + 10, y + 35, size=16)
        self.ui.label(f"Systems: {len(world.systems)}", x + 10, y + 55, size=16)

    def _render_turn_info(self, world: World, x: int, y: int):
        """Render turn-based combat information."""
        from ..systems.turn_system import TurnActor, TurnSystem

        # Find turn system
        turn_system = None
        for system in world.systems:
            if isinstance(system, TurnSystem):
                turn_system = system
                break

        if not turn_system:
            return

        width = 300
        height = 120
        panel_x = x - width // 2

        self.ui.panel(panel_x, y, width, height, (0, 0, 0, 180))
        self.ui.title("Turn Information", panel_x + width // 2 - 80, y + 10, size=20)

        # Current turn info
        current_y = y + 40
        self.ui.label(
            f"Round: {turn_system.current_round}", panel_x + 10, current_y, size=16
        )

        # Current actor
        if turn_system.current_turn_index < len(turn_system.turn_order):
            current_actor_id = turn_system.turn_order[turn_system.current_turn_index]
            actor = world.get_component(current_actor_id, TurnActor)
            if actor:
                self.ui.label(
                    f"Current Turn: Entity {current_actor_id}",
                    panel_x + 10,
                    current_y + 25,
                    size=16,
                    color=(255, 255, 0),
                )

                # Action points bar
                ap_ratio = actor.action_points / actor.max_action_points
                bar_width = width - 20
                self.ui.progress_bar(
                    panel_x + 10,
                    current_y + 50,
                    bar_width,
                    20,
                    ap_ratio,
                    f"AP: {actor.action_points}/{actor.max_action_points}",
                    bar_color=(0, 200, 255),
                )

    def _render_resources(self, world: World, x: int, y: int):
        """Render resource counters."""
        from ..systems.base_building import ResourceStorage

        # Aggregate all resources
        total_resources = {}
        for entity_id in world.entities:
            storage = world.get_component(entity_id, ResourceStorage)
            if storage:
                for resource, amount in storage.resources.items():
                    total_resources[resource] = (
                        total_resources.get(resource, 0) + amount
                    )

        if not total_resources:
            return

        height = 30 + len(total_resources) * 25
        self.ui.panel(x, y, 240, height, (0, 0, 0, 180))
        self.ui.title("Resources", x + 70, y + 5, size=18)

        resource_y = y + 30
        resource_colors = {
            "metal": (192, 192, 192),
            "food": (255, 200, 100),
            "water": (100, 150, 255),
            "energy": (255, 255, 0),
            "wood": (139, 90, 43),
            "stone": (128, 128, 128),
        }

        for resource, amount in sorted(total_resources.items()):
            color = resource_colors.get(resource, (255, 255, 255))
            self.ui.label(
                f"{resource.capitalize()}: {amount:.0f}",
                x + 10,
                resource_y,
                size=16,
                color=color,
            )
            resource_y += 25

    def _render_survival_stats(self, world: World, x: int, y: int):
        """Render survival stats for player entity."""
        from ..core.ecs import Health, Survival

        # Find player entity (assumes tag 'player')
        player_id = None
        for entity_id in world.get_entities_with_tag("player"):
            player_id = entity_id
            break

        if player_id is None:
            return

        health = world.get_component(player_id, Health)
        survival = world.get_component(player_id, Survival)

        if not health and not survival:
            return

        self.ui.panel(x, y, 240, 140, (0, 0, 0, 180))
        self.ui.title("Player Status", x + 60, y + 5, size=18)

        bar_y = y + 30
        bar_width = 220

        # Health bar
        if health:
            health_ratio = health.current / health.maximum
            bar_color = (255, 0, 0) if health_ratio < 0.3 else (0, 255, 0)
            self.ui.progress_bar(
                x + 10,
                bar_y,
                bar_width,
                20,
                health_ratio,
                f"Health: {health.current:.0f}/{health.maximum:.0f}",
                bar_color=bar_color,
            )
            bar_y += 30

        # Survival bars
        if survival:
            # Hunger
            hunger_ratio = survival.hunger / survival.max_hunger
            hunger_color = (255, 165, 0) if hunger_ratio < 0.3 else (255, 200, 100)
            self.ui.progress_bar(
                x + 10,
                bar_y,
                bar_width,
                20,
                hunger_ratio,
                f"Hunger: {survival.hunger:.0f}/{survival.max_hunger:.0f}",
                bar_color=hunger_color,
            )
            bar_y += 25

            # Thirst
            thirst_ratio = survival.thirst / survival.max_thirst
            thirst_color = (100, 150, 255) if thirst_ratio > 0.3 else (255, 0, 0)
            self.ui.progress_bar(
                x + 10,
                bar_y,
                bar_width,
                20,
                thirst_ratio,
                f"Thirst: {survival.thirst:.0f}/{survival.max_thirst:.0f}",
                bar_color=thirst_color,
            )
            bar_y += 25

            # Energy
            energy_ratio = survival.energy / survival.max_energy
            energy_color = (255, 255, 0) if energy_ratio > 0.3 else (255, 100, 0)
            self.ui.progress_bar(
                x + 10,
                bar_y,
                bar_width,
                20,
                energy_ratio,
                f"Energy: {survival.energy:.0f}/{survival.max_energy:.0f}",
                bar_color=energy_color,
            )

    def _render_building_info(self, world: World, x: int, y: int):
        """Render information about buildings."""
        from ..systems.base_building import Building

        buildings = []
        for entity_id in world.entities:
            building = world.get_component(entity_id, Building)
            if building:
                buildings.append((entity_id, building))

        if not buildings:
            return

        height = 30 + min(len(buildings), 5) * 25
        self.ui.panel(x, y, 240, height, (0, 0, 0, 180))
        self.ui.title(f"Buildings ({len(buildings)})", x + 60, y + 5, size=18)

        building_y = y + 30
        for i, (entity_id, building) in enumerate(buildings[:5]):
            status = "Building..." if building.under_construction else "Active"
            color = (255, 200, 0) if building.under_construction else (0, 255, 0)

            self.ui.label(
                f"{building.building_type}: {status}",
                x + 10,
                building_y,
                size=14,
                color=color,
            )
            building_y += 25

        if len(buildings) > 5:
            self.ui.label(
                f"... and {len(buildings) - 5} more",
                x + 10,
                building_y,
                size=12,
                color=(150, 150, 150),
            )

    def _render_selected_entity(self, world: World, x: int, y: int):
        """Render detailed info about selected entity."""
        if self.selected_entity not in world.entities:
            self.selected_entity = None
            return

        self.ui.panel(x, y, 280, 350, (0, 0, 0, 200))
        self.ui.title(f"Entity {self.selected_entity}", x + 70, y + 5, size=18)

        info_y = y + 35
        line_height = 20

        # List all components
        self.ui.label("Components:", x + 10, info_y, size=16, color=(200, 200, 255))
        info_y += line_height + 5

        from ..core.ecs import (Building, Health, ResourceStorage, Sprite,
                                Survival, Transform, TurnActor)

        # Transform
        transform = world.get_component(self.selected_entity, Transform)
        if transform:
            self.ui.label(
                f"Position: ({transform.x:.0f}, {transform.y:.0f})",
                x + 15,
                info_y,
                size=14,
            )
            info_y += line_height

        # Sprite
        sprite = world.get_component(self.selected_entity, Sprite)
        if sprite:
            self.ui.label(f"Sprite: {sprite.asset_id}", x + 15, info_y, size=14)
            info_y += line_height

        # Health
        health = world.get_component(self.selected_entity, Health)
        if health:
            health_pct = (health.current / health.maximum) * 100
            self.ui.label(
                f"Health: {health.current:.0f}/{health.maximum:.0f} ({health_pct:.0f}%)",
                x + 15,
                info_y,
                size=14,
            )
            info_y += line_height

        # Survival
        survival = world.get_component(self.selected_entity, Survival)
        if survival:
            self.ui.label(
                f"Hunger: {survival.hunger:.0f}/{survival.max_hunger:.0f}",
                x + 15,
                info_y,
                size=14,
            )
            info_y += line_height
            self.ui.label(
                f"Thirst: {survival.thirst:.0f}/{survival.max_thirst:.0f}",
                x + 15,
                info_y,
                size=14,
            )
            info_y += line_height
            self.ui.label(
                f"Energy: {survival.energy:.0f}/{survival.max_energy:.0f}",
                x + 15,
                info_y,
                size=14,
            )
            info_y += line_height

        # Turn Actor
        turn_actor = world.get_component(self.selected_entity, TurnActor)
        if turn_actor:
            self.ui.label(
                f"Initiative: {turn_actor.initiative}", x + 15, info_y, size=14
            )
            info_y += line_height
            self.ui.label(
                f"AP: {turn_actor.action_points}/{turn_actor.max_action_points}",
                x + 15,
                info_y,
                size=14,
            )
            info_y += line_height

        # Building
        building = world.get_component(self.selected_entity, Building)
        if building:
            self.ui.label(
                f"Building: {building.building_type}", x + 15, info_y, size=14
            )
            info_y += line_height
            if building.under_construction:
                progress = (
                    building.construction_progress / building.construction_time
                ) * 100
                self.ui.label(f"Construction: {progress:.0f}%", x + 15, info_y, size=14)
                info_y += line_height

        # Resource Storage
        storage = world.get_component(self.selected_entity, ResourceStorage)
        if storage:
            self.ui.label("Resources:", x + 15, info_y, size=14, color=(200, 255, 200))
            info_y += line_height
            for resource, amount in storage.resources.items():
                self.ui.label(f"  {resource}: {amount:.0f}", x + 20, info_y, size=12)
                info_y += line_height

        # Tags
        tags = world.get_entity_tags(self.selected_entity)
        if tags:
            self.ui.label(
                f"Tags: {', '.join(tags)}",
                x + 15,
                info_y,
                size=12,
                color=(150, 150, 150),
            )

    def toggle_visibility(self):
        """Toggle HUD visibility."""
        self.visible = not self.visible

    def toggle_section(self, section: str):
        """Toggle specific HUD section visibility."""
        if section == "fps":
            self.show_fps = not self.show_fps
        elif section == "survival":
            self.show_survival = not self.show_survival
        elif section == "resources":
            self.show_resources = not self.show_resources
        elif section == "turn":
            self.show_turn_info = not self.show_turn_info
        elif section == "building":
            self.show_building_info = not self.show_building_info
