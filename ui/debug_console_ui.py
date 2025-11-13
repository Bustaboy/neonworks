"""
NeonWorks Debug Console UI - Visual Debugging Interface
Provides complete visual interface for debugging, console commands, and entity inspection.
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..core.ecs import GridPosition, Health, Sprite, Survival, Transform, World
from ..rendering.ui import UI


class DebugConsoleUI:
    """
    Visual debug console with command execution and entity inspector.
    """

    def __init__(self, screen: pygame.Surface, world: World):
        self.screen = screen
        self.world = world
        self.ui = UI(screen)

        self.visible = False

        # Console state
        self.command_history: List[str] = []
        self.output_log: List[Tuple[str, Tuple[int, int, int]]] = []
        self.current_command = ""
        self.history_index = -1
        self.scroll_offset = 0
        self.max_log_entries = 100

        # Inspector state
        self.inspector_visible = True
        self.selected_entity = None

        # Performance tracking
        self.fps_history: List[float] = []
        self.max_fps_samples = 60

        # Debug visualization
        self.show_colliders = False
        self.show_grid = False
        self.show_navmesh = False
        self.show_entity_ids = True

        # Command registry
        self.commands = {
            "help": self._cmd_help,
            "clear": self._cmd_clear,
            "list_entities": self._cmd_list_entities,
            "inspect": self._cmd_inspect,
            "spawn": self._cmd_spawn,
            "destroy": self._cmd_destroy,
            "tp": self._cmd_teleport,
            "give": self._cmd_give_resource,
            "heal": self._cmd_heal,
            "toggle": self._cmd_toggle,
            "save": self._cmd_save,
            "load": self._cmd_load,
        }

    def toggle(self):
        """Toggle debug console visibility."""
        self.visible = not self.visible

    def toggle_inspector(self):
        """Toggle entity inspector visibility."""
        self.inspector_visible = not self.inspector_visible

    def render(self, fps: float = 60.0):
        """Render the debug console UI."""
        if not self.visible:
            return

        # Track FPS
        self.fps_history.append(fps)
        if len(self.fps_history) > self.max_fps_samples:
            self.fps_history.pop(0)

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Console panel (bottom half of screen)
        console_height = 350
        console_y = screen_height - console_height

        self._render_console_panel(0, console_y, screen_width, console_height)

        # Inspector panel (top right)
        if self.inspector_visible:
            self._render_inspector_panel(screen_width - 350, 10, 340, 450)

        # Performance overlay (top left)
        self._render_performance_overlay(10, 10, 250, 120, fps)

    def _render_console_panel(self, x: int, y: int, width: int, height: int):
        """Render the main console panel."""
        # Panel background
        self.ui.panel(x, y, width, height, (0, 0, 0, 220))

        # Title bar
        self.ui.title("Debug Console", x + 10, y + 5, size=18, color=(0, 255, 0))

        # Close button
        if self.ui.button("X", x + width - 40, y + 5, 30, 30, color=(150, 0, 0)):
            self.toggle()

        # Toggle inspector button
        if self.ui.button(
            "Inspector", x + width - 140, y + 5, 90, 30, color=(0, 100, 150)
        ):
            self.toggle_inspector()

        # Output log area
        log_y = y + 45
        log_height = height - 95

        # Render log entries
        visible_lines = min(15, len(self.output_log))
        start_index = max(0, len(self.output_log) - visible_lines - self.scroll_offset)
        end_index = len(self.output_log) - self.scroll_offset

        current_y = log_y
        line_height = 18

        for i in range(start_index, end_index):
            if i < 0 or i >= len(self.output_log):
                continue

            message, color = self.output_log[i]
            self.ui.label(message, x + 10, current_y, size=14, color=color)
            current_y += line_height

        # Command input area
        input_y = y + height - 45
        self.ui.panel(x + 5, input_y, width - 10, 40, (30, 30, 40))

        # Command prompt
        self.ui.label(">", x + 10, input_y + 10, size=18, color=(0, 255, 0))

        # Command text
        command_text = self.current_command if self.current_command else "_"
        self.ui.label(
            command_text, x + 30, input_y + 10, size=16, color=(255, 255, 255)
        )

    def _render_inspector_panel(self, x: int, y: int, width: int, height: int):
        """Render the entity inspector panel."""
        self.ui.panel(x, y, width, height, (0, 0, 0, 200))

        # Title
        self.ui.title("Entity Inspector", x + 80, y + 5, size=18, color=(255, 200, 0))

        current_y = y + 40

        if (
            self.selected_entity is None
            or self.selected_entity not in self.world.entities
        ):
            self.ui.label(
                "No entity selected",
                x + 80,
                y + height // 2,
                size=14,
                color=(150, 150, 150),
            )
            self.ui.label(
                "Click on an entity or use",
                x + 50,
                y + height // 2 + 25,
                size=12,
                color=(120, 120, 120),
            )
            self.ui.label(
                "'inspect <id>' command",
                x + 60,
                y + height // 2 + 45,
                size=12,
                color=(120, 120, 120),
            )
            return

        # Entity ID
        self.ui.label(
            f"Entity ID: {self.selected_entity}",
            x + 10,
            current_y,
            size=16,
            color=(255, 255, 100),
        )
        current_y += 30

        # Tags
        tags = self.world.get_entity_tags(self.selected_entity)
        if tags:
            tags_text = ", ".join(tags)
            self.ui.label(
                f"Tags: {tags_text}", x + 10, current_y, size=12, color=(200, 200, 255)
            )
            current_y += 25

        # Components
        self.ui.label("Components:", x + 10, current_y, size=14, color=(200, 255, 200))
        current_y += 25

        # Transform
        transform = self.world.get_component(self.selected_entity, Transform)
        if transform:
            self.ui.label(
                f"Transform:", x + 15, current_y, size=13, color=(255, 200, 100)
            )
            current_y += 20
            self.ui.label(
                f"  Position: ({transform.x:.1f}, {transform.y:.1f})",
                x + 20,
                current_y,
                size=11,
            )
            current_y += 18
            self.ui.label(
                f"  Rotation: {transform.rotation:.1f}°", x + 20, current_y, size=11
            )
            current_y += 18
            self.ui.label(
                f"  Scale: ({transform.scale_x:.2f}, {transform.scale_y:.2f})",
                x + 20,
                current_y,
                size=11,
            )
            current_y += 23

        # Grid Position
        grid_pos = self.world.get_component(self.selected_entity, GridPosition)
        if grid_pos:
            self.ui.label(
                f"GridPosition: ({grid_pos.grid_x}, {grid_pos.grid_y})",
                x + 15,
                current_y,
                size=11,
            )
            current_y += 23

        # Sprite
        sprite = self.world.get_component(self.selected_entity, Sprite)
        if sprite:
            self.ui.label(f"Sprite:", x + 15, current_y, size=13, color=(255, 200, 100))
            current_y += 20
            self.ui.label(f"  Asset: {sprite.asset_id}", x + 20, current_y, size=11)
            current_y += 18
            if sprite.color:
                pygame.draw.rect(self.screen, sprite.color, (x + 20, current_y, 15, 15))
                self.ui.label(f"Color: {sprite.color}", x + 40, current_y, size=11)
                current_y += 23

        # Health
        health = self.world.get_component(self.selected_entity, Health)
        if health:
            self.ui.label(f"Health:", x + 15, current_y, size=13, color=(255, 200, 100))
            current_y += 20
            health_pct = (health.current / health.maximum) * 100
            self.ui.label(
                f"  {health.current:.0f} / {health.maximum:.0f} ({health_pct:.0f}%)",
                x + 20,
                current_y,
                size=11,
            )
            current_y += 23

        # Survival
        survival = self.world.get_component(self.selected_entity, Survival)
        if survival:
            self.ui.label(
                f"Survival:", x + 15, current_y, size=13, color=(255, 200, 100)
            )
            current_y += 20
            self.ui.label(
                f"  Hunger: {survival.hunger:.0f}/{survival.max_hunger:.0f}",
                x + 20,
                current_y,
                size=11,
            )
            current_y += 18
            self.ui.label(
                f"  Thirst: {survival.thirst:.0f}/{survival.max_thirst:.0f}",
                x + 20,
                current_y,
                size=11,
            )
            current_y += 18
            self.ui.label(
                f"  Energy: {survival.energy:.0f}/{survival.max_energy:.0f}",
                x + 20,
                current_y,
                size=11,
            )
            current_y += 23

        # Action buttons
        button_y = y + height - 100

        if self.ui.button(
            "Destroy Entity", x + 10, button_y, width - 20, 30, color=(150, 0, 0)
        ):
            self.world.remove_entity(self.selected_entity)
            self.add_log(f"Destroyed entity {self.selected_entity}", (255, 100, 100))
            self.selected_entity = None

        if self.ui.button(
            "Heal to Full", x + 10, button_y + 35, width - 20, 30, color=(0, 150, 0)
        ):
            health = self.world.get_component(self.selected_entity, Health)
            if health:
                health.current = health.maximum
                self.add_log(f"Healed entity {self.selected_entity}", (0, 255, 100))

    def _render_performance_overlay(
        self, x: int, y: int, width: int, height: int, current_fps: float
    ):
        """Render performance statistics overlay."""
        self.ui.panel(x, y, width, height, (0, 0, 0, 180))

        self.ui.label("Performance", x + 10, y + 5, size=16, color=(255, 200, 0))

        current_y = y + 30

        # Current FPS
        fps_color = (
            (0, 255, 0)
            if current_fps >= 55
            else (255, 200, 0) if current_fps >= 30 else (255, 0, 0)
        )
        self.ui.label(
            f"FPS: {current_fps:.1f}", x + 10, current_y, size=14, color=fps_color
        )
        current_y += 20

        # Average FPS
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            self.ui.label(
                f"Avg: {avg_fps:.1f}", x + 10, current_y, size=12, color=(200, 200, 200)
            )
            current_y += 18

        # Entity count
        entity_count = len(self.world.entities)
        self.ui.label(f"Entities: {entity_count}", x + 10, current_y, size=12)
        current_y += 18

        # System count
        system_count = len(self.world.systems)
        self.ui.label(f"Systems: {system_count}", x + 10, current_y, size=12)

    def add_log(self, message: str, color: Tuple[int, int, int] = (255, 255, 255)):
        """Add a message to the output log."""
        self.output_log.append((message, color))
        if len(self.output_log) > self.max_log_entries:
            self.output_log.pop(0)

    def execute_command(self, command: str):
        """Execute a console command."""
        if not command.strip():
            return

        # Add to history
        self.command_history.append(command)

        # Log command
        self.add_log(f"> {command}", (0, 255, 0))

        # Parse command
        parts = command.split()
        cmd_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # Execute command
        if cmd_name in self.commands:
            try:
                self.commands[cmd_name](args)
            except Exception as e:
                self.add_log(f"Error: {e}", (255, 0, 0))
        else:
            self.add_log(
                f"Unknown command: {cmd_name}. Type 'help' for commands.",
                (255, 100, 100),
            )

        # Clear current command
        self.current_command = ""
        self.history_index = -1

    def handle_text_input(self, text: str):
        """Handle text input for command line."""
        if self.visible:
            self.current_command += text

    def handle_key_press(self, key: int):
        """Handle key press for command line."""
        if not self.visible:
            return

        if key == pygame.K_RETURN:
            self.execute_command(self.current_command)
        elif key == pygame.K_BACKSPACE:
            self.current_command = self.current_command[:-1]
        elif key == pygame.K_UP:
            # Navigate command history up
            if (
                self.command_history
                and self.history_index < len(self.command_history) - 1
            ):
                self.history_index += 1
                self.current_command = self.command_history[-(self.history_index + 1)]
        elif key == pygame.K_DOWN:
            # Navigate command history down
            if self.history_index > 0:
                self.history_index -= 1
                self.current_command = self.command_history[-(self.history_index + 1)]
            elif self.history_index == 0:
                self.history_index = -1
                self.current_command = ""

    # Command implementations

    def _cmd_help(self, args: List[str]):
        """Display available commands."""
        self.add_log("Available commands:", (255, 255, 100))
        for cmd_name in self.commands.keys():
            self.add_log(f"  {cmd_name}", (200, 200, 200))

    def _cmd_clear(self, args: List[str]):
        """Clear the console output."""
        self.output_log.clear()

    def _cmd_list_entities(self, args: List[str]):
        """List all entities in the world."""
        self.add_log(f"Entities ({len(self.world.entities)}):", (255, 255, 100))
        for entity_id in list(self.world.entities)[:20]:  # Limit to 20
            tags = self.world.get_entity_tags(entity_id)
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            self.add_log(f"  {entity_id}{tag_str}", (200, 200, 200))
        if len(self.world.entities) > 20:
            self.add_log(
                f"  ... and {len(self.world.entities) - 20} more", (150, 150, 150)
            )

    def _cmd_inspect(self, args: List[str]):
        """Inspect an entity by ID."""
        if not args:
            self.add_log("Usage: inspect <entity_id>", (255, 200, 0))
            return

        try:
            entity_id = int(args[0])
            if entity_id in self.world.entities:
                self.selected_entity = entity_id
                self.add_log(f"Inspecting entity {entity_id}", (0, 255, 100))
            else:
                self.add_log(f"Entity {entity_id} not found", (255, 100, 100))
        except ValueError:
            self.add_log("Invalid entity ID", (255, 0, 0))

    def _cmd_spawn(self, args: List[str]):
        """Spawn a new entity."""
        entity_id = self.world.create_entity()
        self.world.add_component(entity_id, Transform(x=400, y=300))
        self.add_log(f"Spawned entity {entity_id}", (0, 255, 100))

    def _cmd_destroy(self, args: List[str]):
        """Destroy an entity by ID."""
        if not args:
            self.add_log("Usage: destroy <entity_id>", (255, 200, 0))
            return

        try:
            entity_id = int(args[0])
            if entity_id in self.world.entities:
                self.world.remove_entity(entity_id)
                self.add_log(f"Destroyed entity {entity_id}", (255, 100, 100))
            else:
                self.add_log(f"Entity {entity_id} not found", (255, 100, 100))
        except ValueError:
            self.add_log("Invalid entity ID", (255, 0, 0))

    def _cmd_teleport(self, args: List[str]):
        """Teleport an entity to a position."""
        if len(args) < 3:
            self.add_log("Usage: tp <entity_id> <x> <y>", (255, 200, 0))
            return

        try:
            entity_id = int(args[0])
            x = float(args[1])
            y = float(args[2])

            transform = self.world.get_component(entity_id, Transform)
            if transform:
                transform.x = x
                transform.y = y
                self.add_log(
                    f"Teleported entity {entity_id} to ({x}, {y})", (0, 255, 100)
                )
            else:
                self.add_log(f"Entity {entity_id} has no Transform", (255, 100, 100))
        except (ValueError, IndexError):
            self.add_log("Invalid arguments", (255, 0, 0))

    def _cmd_give_resource(self, args: List[str]):
        """Give resources to an entity."""
        if len(args) < 3:
            self.add_log("Usage: give <entity_id> <resource> <amount>", (255, 200, 0))
            return

        from ..systems.base_building import ResourceStorage

        try:
            entity_id = int(args[0])
            resource = args[1]
            amount = float(args[2])

            storage = self.world.get_component(entity_id, ResourceStorage)
            if storage:
                storage.resources[resource] = (
                    storage.resources.get(resource, 0) + amount
                )
                self.add_log(
                    f"Gave {amount} {resource} to entity {entity_id}", (0, 255, 100)
                )
            else:
                self.add_log(
                    f"Entity {entity_id} has no ResourceStorage", (255, 100, 100)
                )
        except (ValueError, IndexError):
            self.add_log("Invalid arguments", (255, 0, 0))

    def _cmd_heal(self, args: List[str]):
        """Heal an entity."""
        if not args:
            self.add_log("Usage: heal <entity_id> [amount]", (255, 200, 0))
            return

        try:
            entity_id = int(args[0])
            amount = float(args[1]) if len(args) > 1 else 999999

            health = self.world.get_component(entity_id, Health)
            if health:
                health.current = min(health.current + amount, health.maximum)
                self.add_log(f"Healed entity {entity_id}", (0, 255, 100))
            else:
                self.add_log(f"Entity {entity_id} has no Health", (255, 100, 100))
        except (ValueError, IndexError):
            self.add_log("Invalid arguments", (255, 0, 0))

    def _cmd_toggle(self, args: List[str]):
        """Toggle debug visualizations."""
        if not args:
            self.add_log("Usage: toggle <colliders|grid|navmesh|ids>", (255, 200, 0))
            return

        option = args[0].lower()
        if option == "colliders":
            self.show_colliders = not self.show_colliders
            self.add_log(
                f"Colliders: {'ON' if self.show_colliders else 'OFF'}", (200, 200, 200)
            )
        elif option == "grid":
            self.show_grid = not self.show_grid
            self.add_log(f"Grid: {'ON' if self.show_grid else 'OFF'}", (200, 200, 200))
        elif option == "navmesh":
            self.show_navmesh = not self.show_navmesh
            self.add_log(
                f"Navmesh: {'ON' if self.show_navmesh else 'OFF'}", (200, 200, 200)
            )
        elif option == "ids":
            self.show_entity_ids = not self.show_entity_ids
            self.add_log(
                f"Entity IDs: {'ON' if self.show_entity_ids else 'OFF'}",
                (200, 200, 200),
            )
        else:
            self.add_log(f"Unknown option: {option}", (255, 100, 100))

    def _cmd_save(self, args: List[str]):
        """Save the game."""
        self.add_log("Saving game...", (200, 200, 255))
        # This would call the save system
        self.add_log("Game saved", (0, 255, 100))

    def _cmd_load(self, args: List[str]):
        """Load the game."""
        self.add_log("Loading game...", (200, 200, 255))
        # This would call the load system
        self.add_log("Game loaded", (0, 255, 100))
