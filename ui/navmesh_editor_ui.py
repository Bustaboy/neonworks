"""
NeonWorks Navmesh Editor UI - Visual Navmesh Editing
Provides complete visual interface for creating and editing navmeshes.
"""

from typing import List, Optional, Set, Tuple

import pygame

from ..core.ecs import GridPosition, Navmesh, World
from ..core.undo_manager import NavmeshPaintCommand, UndoManager
from ..editor.ai_navmesh import NavmeshGenerator
from ..rendering.ui import UI


class NavmeshEditorUI:
    """
    Visual editor for creating and modifying navigation meshes.
    Allows painting walkable/unwalkable tiles and automatic navmesh generation.
    """

    def __init__(self, screen: pygame.Surface, world: World):
        self.screen = screen
        self.world = world
        self.ui = UI(screen)

        self.visible = False
        self.navmesh_generator = NavmeshGenerator()

        # Editor state
        self.paint_mode = "walkable"  # 'walkable', 'unwalkable', 'erase'
        self.brush_size = 1
        self.show_navmesh = True
        self.show_grid = True

        # Navmesh data
        self.walkable_tiles: Set[Tuple[int, int]] = set()
        self.unwalkable_tiles: Set[Tuple[int, int]] = set()

        # Grid settings
        self.tile_size = 32
        self.grid_width = 50
        self.grid_height = 50

        # Painting state
        self.is_painting = False
        self.last_paint_pos = None

        # Undo/Redo manager
        self.undo_manager = UndoManager(enable_compression=True)

        # Track changes for batching
        self.current_paint_stroke: List[Tuple[int, int, bool, bool]] = []

    def toggle(self):
        """Toggle navmesh editor visibility."""
        self.visible = not self.visible

    def render(self, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the navmesh editor UI and visualization."""
        if not self.visible:
            return

        # Render navmesh visualization
        if self.show_navmesh or self.show_grid:
            self._render_navmesh_visualization(camera_offset)

        # Render editor panel
        self._render_editor_panel()

    def _render_navmesh_visualization(self, camera_offset: Tuple[int, int]):
        """Render the navmesh on the grid."""
        # Draw grid
        if self.show_grid:
            self._draw_grid(camera_offset)

        # Draw walkable tiles
        for grid_x, grid_y in self.walkable_tiles:
            screen_x = grid_x * self.tile_size + camera_offset[0]
            screen_y = grid_y * self.tile_size + camera_offset[1]

            # Create semi-transparent surface
            tile_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            tile_surface.fill((0, 255, 0, 100))  # Green for walkable
            self.screen.blit(tile_surface, (screen_x, screen_y))

        # Draw unwalkable tiles
        for grid_x, grid_y in self.unwalkable_tiles:
            screen_x = grid_x * self.tile_size + camera_offset[0]
            screen_y = grid_y * self.tile_size + camera_offset[1]

            # Create semi-transparent surface
            tile_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            tile_surface.fill((255, 0, 0, 100))  # Red for unwalkable
            self.screen.blit(tile_surface, (screen_x, screen_y))

    def _draw_grid(self, camera_offset: Tuple[int, int]):
        """Draw the grid lines."""
        grid_color = (80, 80, 80)

        # Vertical lines
        for x in range(0, self.grid_width + 1):
            screen_x = x * self.tile_size + camera_offset[0]
            pygame.draw.line(
                self.screen,
                grid_color,
                (screen_x, camera_offset[1]),
                (screen_x, self.grid_height * self.tile_size + camera_offset[1]),
            )

        # Horizontal lines
        for y in range(0, self.grid_height + 1):
            screen_y = y * self.tile_size + camera_offset[1]
            pygame.draw.line(
                self.screen,
                grid_color,
                (camera_offset[0], screen_y),
                (self.grid_width * self.tile_size + camera_offset[0], screen_y),
            )

    def _render_editor_panel(self):
        """Render the navmesh editor control panel."""
        screen_width = self.screen.get_width()
        panel_width = 280
        panel_height = 500
        panel_x = screen_width - panel_width - 10
        panel_y = 100

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (0, 0, 0, 200))
        self.ui.title("Navmesh Editor", panel_x + 60, panel_y + 5, size=20)

        # Close button
        if self.ui.button("X", panel_x + panel_width - 40, panel_y + 5, 30, 30):
            self.toggle()

        current_y = panel_y + 45

        # Paint mode selection
        self.ui.label("Paint Mode:", panel_x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        button_width = panel_width - 20
        button_height = 35

        # Walkable mode
        walkable_color = (0, 200, 0) if self.paint_mode == "walkable" else (0, 100, 0)
        if self.ui.button(
            "Paint Walkable",
            panel_x + 10,
            current_y,
            button_width,
            button_height,
            color=walkable_color,
        ):
            self.paint_mode = "walkable"
        current_y += button_height + 5

        # Unwalkable mode
        unwalkable_color = (200, 0, 0) if self.paint_mode == "unwalkable" else (100, 0, 0)
        if self.ui.button(
            "Paint Unwalkable",
            panel_x + 10,
            current_y,
            button_width,
            button_height,
            color=unwalkable_color,
        ):
            self.paint_mode = "unwalkable"
        current_y += button_height + 5

        # Erase mode
        erase_color = (150, 150, 150) if self.paint_mode == "erase" else (80, 80, 80)
        if self.ui.button(
            "Erase",
            panel_x + 10,
            current_y,
            button_width,
            button_height,
            color=erase_color,
        ):
            self.paint_mode = "erase"
        current_y += button_height + 15

        # Brush size
        self.ui.label(
            f"Brush Size: {self.brush_size}",
            panel_x + 10,
            current_y,
            size=16,
            color=(200, 200, 255),
        )
        current_y += 25

        if self.ui.button("-", panel_x + 10, current_y, 50, 30):
            self.brush_size = max(1, self.brush_size - 1)

        self.ui.label(str(self.brush_size), panel_x + 70, current_y + 5, size=18)

        if self.ui.button("+", panel_x + 110, current_y, 50, 30):
            self.brush_size = min(10, self.brush_size + 1)

        current_y += 45

        # Visualization options
        self.ui.label("Display Options:", panel_x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        # Toggle grid
        grid_text = "Hide Grid" if self.show_grid else "Show Grid"
        if self.ui.button(grid_text, panel_x + 10, current_y, button_width, 30):
            self.show_grid = not self.show_grid
        current_y += 35

        # Toggle navmesh
        navmesh_text = "Hide Navmesh" if self.show_navmesh else "Show Navmesh"
        if self.ui.button(navmesh_text, panel_x + 10, current_y, button_width, 30):
            self.show_navmesh = not self.show_navmesh
        current_y += 45

        # Actions
        self.ui.label("Actions:", panel_x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        # Auto-generate from buildings
        if self.ui.button("Auto-Generate from Map", panel_x + 10, current_y, button_width, 35):
            self.auto_generate_from_map()
        current_y += 40

        # Clear all
        if self.ui.button(
            "Clear All", panel_x + 10, current_y, button_width, 35, color=(150, 0, 0)
        ):
            self.clear_navmesh()
        current_y += 40

        # Save to entity
        if self.ui.button(
            "Save to Entity",
            panel_x + 10,
            current_y,
            button_width,
            35,
            color=(0, 150, 0),
        ):
            self.save_to_entity()
        current_y += 40

        # Load from entity
        if self.ui.button(
            "Load from Entity",
            panel_x + 10,
            current_y,
            button_width,
            35,
            color=(0, 100, 150),
        ):
            self.load_from_entity()

        # Undo/Redo buttons
        current_y += 45
        self.ui.label("Undo/Redo:", panel_x + 10, current_y, size=14, color=(200, 200, 200))
        current_y += 20

        # Undo button
        undo_enabled = self.undo_manager.can_undo()
        undo_color = (0, 180, 0) if undo_enabled else (50, 50, 50)
        if self.ui.button(
            f"Undo (Ctrl+Z)",
            panel_x + 10,
            current_y,
            button_width // 2 - 5,
            30,
            color=undo_color,
        ):
            if undo_enabled:
                self.undo_manager.undo()

        # Redo button
        redo_enabled = self.undo_manager.can_redo()
        redo_color = (0, 140, 180) if redo_enabled else (50, 50, 50)
        if self.ui.button(
            f"Redo (Ctrl+Y)",
            panel_x + button_width // 2 + 15,
            current_y,
            button_width // 2 - 5,
            30,
            color=redo_color,
        ):
            if redo_enabled:
                self.undo_manager.redo()

        # Show undo/redo descriptions
        current_y += 35
        undo_desc = self.undo_manager.get_undo_description()
        if undo_desc:
            self.ui.label(
                f"← {undo_desc[:25]}",
                panel_x + 15,
                current_y,
                size=10,
                color=(150, 255, 150),
            )
        current_y += 15

        # Statistics
        current_y += 10
        self.ui.label("Statistics:", panel_x + 10, current_y, size=14, color=(200, 200, 200))
        current_y += 20
        self.ui.label(f"Walkable: {len(self.walkable_tiles)}", panel_x + 15, current_y, size=12)
        current_y += 18
        self.ui.label(
            f"Unwalkable: {len(self.unwalkable_tiles)}",
            panel_x + 15,
            current_y,
            size=12,
        )

    def paint_tile(self, grid_x: int, grid_y: int):
        """Paint a tile with the current mode and brush size."""
        if not self.visible:
            return

        # Apply brush
        for dx in range(-self.brush_size // 2, self.brush_size // 2 + 1):
            for dy in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                tile_x = grid_x + dx
                tile_y = grid_y + dy

                # Check bounds
                if not (0 <= tile_x < self.grid_width and 0 <= tile_y < self.grid_height):
                    continue

                tile_pos = (tile_x, tile_y)

                # Get old state for undo
                old_walkable = tile_pos in self.walkable_tiles
                old_unwalkable = tile_pos in self.unwalkable_tiles

                # Determine new state
                if self.paint_mode == "walkable":
                    new_walkable = True
                elif self.paint_mode == "unwalkable":
                    new_walkable = False
                else:  # erase
                    new_walkable = None  # Neither walkable nor unwalkable

                # Only record change if state actually changes
                if self.paint_mode == "walkable":
                    if not old_walkable:
                        self.current_paint_stroke.append((tile_x, tile_y, old_walkable, True))
                        self.walkable_tiles.add(tile_pos)
                        self.unwalkable_tiles.discard(tile_pos)
                elif self.paint_mode == "unwalkable":
                    if not old_unwalkable:
                        self.current_paint_stroke.append((tile_x, tile_y, old_walkable, False))
                        self.unwalkable_tiles.add(tile_pos)
                        self.walkable_tiles.discard(tile_pos)
                elif self.paint_mode == "erase":
                    if old_walkable or old_unwalkable:
                        # Track what was there before erasing
                        self.current_paint_stroke.append((tile_x, tile_y, old_walkable, None))
                        self.walkable_tiles.discard(tile_pos)
                        self.unwalkable_tiles.discard(tile_pos)

    def start_painting(self, grid_x: int, grid_y: int):
        """Start a painting stroke."""
        self.is_painting = True
        self.last_paint_pos = (grid_x, grid_y)
        self.current_paint_stroke.clear()  # Start new stroke
        self.paint_tile(grid_x, grid_y)

    def continue_painting(self, grid_x: int, grid_y: int):
        """Continue painting while dragging."""
        if not self.is_painting:
            return

        # Interpolate between last position and current
        if self.last_paint_pos:
            self._paint_line(self.last_paint_pos[0], self.last_paint_pos[1], grid_x, grid_y)

        self.last_paint_pos = (grid_x, grid_y)

    def stop_painting(self):
        """Stop painting and record undo command."""
        if not self.is_painting:
            return

        self.is_painting = False
        self.last_paint_pos = None

        # Record undo command if any changes were made
        if self.current_paint_stroke:
            # Convert None values to proper boolean for NavmeshPaintCommand
            processed_changes = []
            for x, y, old_walkable, new_walkable in self.current_paint_stroke:
                # Convert None to False for consistency
                if new_walkable is None:
                    new_walkable = False
                processed_changes.append((x, y, old_walkable, new_walkable))

            command = NavmeshPaintCommand(
                self.walkable_tiles,
                self.unwalkable_tiles,
                processed_changes,
                f"Paint {self.paint_mode.capitalize()}",
            )
            # Don't execute since we already applied changes
            command.executed = True
            self.undo_manager.undo_stack.append(command)
            self.current_paint_stroke.clear()

    def _paint_line(self, x0: int, y0: int, x1: int, y1: int):
        """Paint a line between two points (Bresenham's algorithm)."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            self.paint_tile(x, y)

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def auto_generate_from_map(self):
        """Auto-generate navmesh based on buildings and obstacles in the world."""
        self.clear_navmesh()

        # Mark all tiles as walkable initially
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.walkable_tiles.add((x, y))

        # Mark tiles with buildings as unwalkable
        from ..systems.base_building import Building

        for entity_id in self.world.get_entities_with_tag("building"):
            grid_pos = self.world.get_component(entity_id, GridPosition)
            building = self.world.get_component(entity_id, Building)

            if grid_pos:
                # Mark building footprint as unwalkable
                size_w = 1
                size_h = 1

                # Get building size if available
                # (This would require storing building definitions somewhere accessible)

                for dx in range(size_w):
                    for dy in range(size_h):
                        tile_pos = (grid_pos.grid_x + dx, grid_pos.grid_y + dy)
                        self.unwalkable_tiles.add(tile_pos)
                        self.walkable_tiles.discard(tile_pos)

    def clear_navmesh(self):
        """Clear all navmesh data."""
        self.walkable_tiles.clear()
        self.unwalkable_tiles.clear()

    def save_to_entity(self):
        """Save navmesh data to a world entity."""
        # Find existing navmesh entity or create new one
        navmesh_entity = None
        for entity_id in self.world.get_entities_with_tag("navmesh"):
            navmesh_entity = entity_id
            break

        if navmesh_entity is None:
            navmesh_entity = self.world.create_entity()
            self.world.tag_entity(navmesh_entity, "navmesh")

        # Create navmesh component
        navmesh = Navmesh(width=self.grid_width, height=self.grid_height, tile_size=self.tile_size)

        # Set walkable data
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                is_walkable = (x, y) in self.walkable_tiles
                navmesh.set_walkable(x, y, is_walkable)

        self.world.add_component(navmesh_entity, navmesh)

        print(f"Navmesh saved to entity #{navmesh_entity}")

    def load_from_entity(self):
        """Load navmesh data from a world entity."""
        # Find navmesh entity
        navmesh_entity = None
        for entity_id in self.world.get_entities_with_tag("navmesh"):
            navmesh_entity = entity_id
            break

        if navmesh_entity is None:
            print("No navmesh entity found")
            return

        navmesh = self.world.get_component(navmesh_entity, Navmesh)
        if not navmesh:
            print("Entity has no navmesh component")
            return

        # Clear current data
        self.clear_navmesh()

        # Load walkable tiles
        for x in range(navmesh.width):
            for y in range(navmesh.height):
                if navmesh.is_walkable(x, y):
                    self.walkable_tiles.add((x, y))
                else:
                    self.unwalkable_tiles.add((x, y))

        print(f"Navmesh loaded from entity #{navmesh_entity}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        # Handle keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            # Check for Ctrl modifier
            ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
            shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT

            # Ctrl+Z: Undo
            if ctrl_pressed and event.key == pygame.K_z and not shift_pressed:
                if self.undo_manager.undo():
                    return True

            # Ctrl+Y or Ctrl+Shift+Z: Redo
            if (ctrl_pressed and event.key == pygame.K_y) or (
                ctrl_pressed and shift_pressed and event.key == pygame.K_z
            ):
                if self.undo_manager.redo():
                    return True

        return False
