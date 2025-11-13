"""
NeonWorks Combat UI - Turn-Based Combat Visualization
Provides complete visual interface for turn-based combat system.
"""

from typing import List, Optional, Tuple

import pygame

from ..core.ecs import Health, Sprite, Transform, World
from ..rendering.ui import UI
from ..systems.turn_system import TurnActor, TurnSystem


class CombatUI:
    """
    Visual UI for turn-based combat with initiative order,
    action points, and combat abilities.
    """

    def __init__(self, screen: pygame.Surface, world: World):
        self.screen = screen
        self.world = world
        self.ui = UI(screen)

        self.visible = True
        self.show_initiative_bar = True
        self.show_ability_bar = True
        self.show_combat_log = True

        # Combat log
        self.combat_log: List[Tuple[str, Tuple[int, int, int]]] = []
        self.max_log_entries = 10

        # Ability definitions (can be loaded from config)
        self.abilities = {
            "attack": {
                "name": "Attack",
                "cost": 3,
                "icon_color": (255, 0, 0),
                "description": "Basic melee attack",
            },
            "defend": {
                "name": "Defend",
                "cost": 2,
                "icon_color": (0, 100, 255),
                "description": "Increase defense this turn",
            },
            "special": {
                "name": "Special",
                "cost": 5,
                "icon_color": (255, 200, 0),
                "description": "Powerful special ability",
            },
            "heal": {
                "name": "Heal",
                "cost": 4,
                "icon_color": (0, 255, 0),
                "description": "Restore health",
            },
            "move": {
                "name": "Move",
                "cost": 1,
                "icon_color": (200, 200, 200),
                "description": "Move to adjacent tile",
            },
            "skip": {
                "name": "Skip Turn",
                "cost": 0,
                "icon_color": (150, 150, 150),
                "description": "End your turn",
            },
        }

        self.selected_ability = None

    def render(self):
        """Render all combat UI elements."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Top bar: Initiative order
        if self.show_initiative_bar:
            self._render_initiative_bar(screen_width // 2, 10)

        # Bottom center: Ability bar (for current turn actor)
        if self.show_ability_bar:
            self._render_ability_bar(screen_width // 2, screen_height - 120)

        # Bottom left: Combat log
        if self.show_combat_log:
            self._render_combat_log(10, screen_height - 250)

    def _render_initiative_bar(self, center_x: int, y: int):
        """Render the initiative order bar showing turn order."""
        turn_system = self._get_turn_system()
        if not turn_system:
            return

        # Panel
        panel_width = 600
        panel_height = 90
        panel_x = center_x - panel_width // 2

        self.ui.panel(panel_x, y, panel_width, panel_height, (0, 0, 0, 200))
        self.ui.title(
            "Initiative Order", panel_x + panel_width // 2 - 70, y + 5, size=18
        )

        # Display turn order
        slot_y = y + 35
        slot_width = 80
        slot_height = 50
        slot_spacing = 10
        start_x = panel_x + 10

        visible_count = min(6, len(turn_system.turn_order))

        for i in range(visible_count):
            idx = (turn_system.current_turn_index + i) % len(turn_system.turn_order)
            entity_id = turn_system.turn_order[idx]

            if entity_id not in self.world.entities:
                continue

            slot_x = start_x + i * (slot_width + slot_spacing)

            # Highlight current actor
            is_current = i == 0
            slot_color = (100, 150, 255) if is_current else (40, 40, 60)

            self.ui.panel(slot_x, slot_y, slot_width, slot_height, slot_color)

            # Entity info
            turn_actor = self.world.get_component(entity_id, TurnActor)
            health = self.world.get_component(entity_id, Health)

            # Entity ID
            self.ui.label(
                f"#{entity_id}", slot_x + 5, slot_y + 5, size=14, color=(255, 255, 255)
            )

            # Initiative
            if turn_actor:
                self.ui.label(
                    f"Init: {turn_actor.initiative}",
                    slot_x + 5,
                    slot_y + 22,
                    size=11,
                    color=(200, 200, 200),
                )

            # Health bar (if available)
            if health:
                health_ratio = health.current / health.maximum
                bar_width = slot_width - 10
                bar_height = 8
                bar_x = slot_x + 5
                bar_y = slot_y + slot_height - bar_height - 5

                # Background
                pygame.draw.rect(
                    self.screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height)
                )
                # Health
                pygame.draw.rect(
                    self.screen,
                    (255, 0, 0),
                    (bar_x, bar_y, int(bar_width * health_ratio), bar_height),
                )

    def _render_ability_bar(self, center_x: int, y: int):
        """Render ability bar for the current turn actor."""
        turn_system = self._get_turn_system()
        if not turn_system:
            return

        # Get current actor
        if turn_system.current_turn_index >= len(turn_system.turn_order):
            return

        current_actor_id = turn_system.turn_order[turn_system.current_turn_index]
        turn_actor = self.world.get_component(current_actor_id, TurnActor)

        if not turn_actor:
            return

        # Panel
        panel_width = 600
        panel_height = 110
        panel_x = center_x - panel_width // 2

        self.ui.panel(panel_x, y, panel_width, panel_height, (0, 0, 0, 200))

        # Current actor info
        self.ui.label(
            f"Entity #{current_actor_id} - Turn",
            panel_x + 10,
            y + 5,
            size=18,
            color=(255, 255, 100),
        )

        # Action points bar
        ap_ratio = turn_actor.action_points / turn_actor.max_action_points
        self.ui.progress_bar(
            panel_x + 10,
            y + 30,
            panel_width - 20,
            25,
            ap_ratio,
            f"Action Points: {turn_actor.action_points}/{turn_actor.max_action_points}",
            bar_color=(0, 200, 255),
        )

        # Ability buttons
        button_y = y + 65
        button_width = 85
        button_height = 35
        button_spacing = 10
        start_x = panel_x + 10

        for i, (ability_id, ability_data) in enumerate(self.abilities.items()):
            if i >= 6:  # Max 6 abilities
                break

            button_x = start_x + i * (button_width + button_spacing)

            # Check if can afford
            can_afford = turn_actor.action_points >= ability_data["cost"]
            button_color = ability_data["icon_color"] if can_afford else (80, 80, 80)

            # Highlight if selected
            if ability_id == self.selected_ability:
                pygame.draw.rect(
                    self.screen,
                    (255, 255, 0),
                    (button_x - 2, button_y - 2, button_width + 4, button_height + 4),
                )

            # Button
            if self.ui.button(
                ability_data["name"],
                button_x,
                button_y,
                button_width,
                button_height,
                color=button_color,
            ):
                if can_afford:
                    self.select_ability(ability_id)

            # Cost
            cost_text = (
                f"{ability_data['cost']} AP" if ability_data["cost"] > 0 else "Free"
            )
            self.ui.label(
                cost_text,
                button_x + 5,
                button_y + button_height - 15,
                size=10,
                color=(255, 255, 255),
            )

        # End turn button
        end_turn_x = panel_x + panel_width - 100
        if self.ui.button(
            "End Turn", end_turn_x, button_y, 90, button_height, color=(200, 50, 50)
        ):
            self.end_turn()

    def _render_combat_log(self, x: int, y: int):
        """Render combat event log."""
        panel_width = 350
        panel_height = 240

        self.ui.panel(x, y, panel_width, panel_height, (0, 0, 0, 180))
        self.ui.title("Combat Log", x + 100, y + 5, size=18)

        # Display log entries
        log_y = y + 35
        for message, color in self.combat_log[-self.max_log_entries :]:
            self.ui.label(message, x + 10, log_y, size=14, color=color)
            log_y += 20

    def select_ability(self, ability_id: str):
        """Select an ability for use."""
        self.selected_ability = ability_id
        self.add_log(f"Selected: {self.abilities[ability_id]['name']}", (255, 255, 100))

    def use_ability(self, ability_id: str, target_entity: Optional[int] = None) -> bool:
        """
        Use an ability. Returns True if successful.
        """
        turn_system = self._get_turn_system()
        if not turn_system:
            return False

        # Get current actor
        if turn_system.current_turn_index >= len(turn_system.turn_order):
            return False

        current_actor_id = turn_system.turn_order[turn_system.current_turn_index]
        turn_actor = self.world.get_component(current_actor_id, TurnActor)

        if not turn_actor:
            return False

        ability_data = self.abilities.get(ability_id)
        if not ability_data:
            return False

        # Check if can afford
        if turn_actor.action_points < ability_data["cost"]:
            self.add_log("Not enough action points!", (255, 0, 0))
            return False

        # Deduct action points
        turn_actor.action_points -= ability_data["cost"]

        # Execute ability (basic implementation)
        if ability_id == "attack" and target_entity:
            self._execute_attack(current_actor_id, target_entity)
        elif ability_id == "heal":
            self._execute_heal(current_actor_id)
        elif ability_id == "defend":
            self._execute_defend(current_actor_id)
        else:
            self.add_log(f"{ability_data['name']} used!", (200, 200, 255))

        self.selected_ability = None
        return True

    def _execute_attack(self, attacker_id: int, target_id: int):
        """Execute an attack."""
        target_health = self.world.get_component(target_id, Health)
        if target_health:
            damage = 10  # Base damage
            target_health.current -= damage
            self.add_log(
                f"Entity #{attacker_id} attacks #{target_id} for {damage} damage!",
                (255, 100, 100),
            )

            if target_health.current <= 0:
                self.add_log(f"Entity #{target_id} defeated!", (255, 0, 0))
        else:
            self.add_log("Invalid target!", (255, 0, 0))

    def _execute_heal(self, entity_id: int):
        """Execute a heal."""
        health = self.world.get_component(entity_id, Health)
        if health:
            heal_amount = 20
            health.current = min(health.current + heal_amount, health.maximum)
            self.add_log(f"Entity #{entity_id} heals for {heal_amount}!", (0, 255, 100))

    def _execute_defend(self, entity_id: int):
        """Execute a defend action."""
        # This would set a defense buff in a real implementation
        self.add_log(f"Entity #{entity_id} takes a defensive stance!", (100, 150, 255))

    def end_turn(self):
        """End the current turn."""
        turn_system = self._get_turn_system()
        if turn_system:
            turn_system.next_turn()
            self.selected_ability = None
            self.add_log("Turn ended", (200, 200, 200))

    def add_log(self, message: str, color: Tuple[int, int, int] = (255, 255, 255)):
        """Add a message to the combat log."""
        self.combat_log.append((message, color))
        if len(self.combat_log) > 50:  # Keep last 50 messages
            self.combat_log.pop(0)

    def _get_turn_system(self) -> Optional[TurnSystem]:
        """Get the turn system from world."""
        for system in self.world.systems:
            if isinstance(system, TurnSystem):
                return system
        return None

    def toggle_visibility(self):
        """Toggle combat UI visibility."""
        self.visible = not self.visible

    def handle_entity_click(self, entity_id: int):
        """Handle clicking on an entity (for targeting abilities)."""
        if self.selected_ability and self.selected_ability in ["attack", "special"]:
            self.use_ability(self.selected_ability, entity_id)
            return True
        return False
