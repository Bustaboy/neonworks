"""
Autotile Editor UI for NeonWorks Engine

Visual editor for creating and configuring autotile sets.
Allows users to define autotile patterns, test neighbor matching, and manage autotile sets.
"""

import json
from typing import Dict, List, Optional, Tuple

import pygame

from neonworks.data.tileset_manager import get_tileset_manager
from neonworks.rendering.autotiles import (
    AutotileFormat,
    AutotileManager,
    AutotileSet,
    get_autotile_manager,
)
from neonworks.data.map_layers import EnhancedTileLayer
from neonworks.rendering.tilemap import Tile, Tilemap
from neonworks.rendering.ui import UI


class AutotileEditorUI:
    """
    Visual editor for creating and managing autotile sets.

    Hotkey: F11 (when integrated with MasterUIManager)

    Features:
    - Create new autotile sets
    - Configure tile matching rules
    - Test autotile behavior in real-time
    - Import/export autotile definitions
    - Preview autotile patterns
    """

    def __init__(self, screen: pygame.Surface, project_path: Optional[str] = None):
        """
        Initialize the autotile editor.

        Args:
            screen: Pygame surface to render to
            project_path: Path to current project (optional)
        """
        self.screen = screen
        self.ui = UI(screen)
        self.visible = False

        # Managers
        self.autotile_manager = get_autotile_manager()
        self.tileset_manager = get_tileset_manager(project_path)

        # Editor state
        self.current_autotile_set: Optional[AutotileSet] = None
        self.selected_tileset_id: Optional[str] = None
        self.selected_format = AutotileFormat.TILE_16
        self.test_layer: Optional[EnhancedTileLayer] = None

        # UI dimensions
        self.panel_x = 50
        self.panel_y = 50
        self.panel_width = screen.get_width() - 100
        self.panel_height = screen.get_height() - 100

        # Autotile set list
        self.autotile_sets: List[AutotileSet] = []
        self.selected_autotile_index = 0

        # Test grid for previewing autotiles
        self.test_grid_size = 8
        self.test_layer = EnhancedTileLayer(width=self.test_grid_size, height=self.test_grid_size)

        # Colors
        self.bg_color = (40, 40, 50)
        self.panel_color = (60, 60, 70)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)
        self.button_color = (80, 80, 90)
        self.button_hover_color = (100, 100, 110)

        # Scroll state
        self.scroll_offset = 0

        # Input state
        self.input_active = False
        self.input_field = None
        self.input_text = ""

        # New autotile form
        self.new_autotile_name = ""
        self.new_autotile_base_id = 0

    def toggle(self):
        """Toggle visibility of the autotile editor."""
        self.visible = not self.visible

        # Load autotile sets when opened
        if self.visible:
            self._refresh_autotile_list()

    def _refresh_autotile_list(self):
        """Refresh the list of autotile sets."""
        self.autotile_sets = list(self.autotile_manager.autotile_sets.values())

    def update(self, dt: float):
        """
        Update editor logic.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

    def render(self, screen: pygame.Surface):
        """
        Render the autotile editor UI.

        Args:
            screen: Surface to render to
        """
        if not self.visible:
            return

        # Draw background overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Draw main panel
        pygame.draw.rect(
            screen,
            self.panel_color,
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
        )
        pygame.draw.rect(
            screen,
            self.highlight_color,
            (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
            2,
        )

        # Draw title
        self._draw_text("Autotile Editor", self.panel_x + 20, self.panel_y + 20, size=32)

        # Draw close button
        close_btn_rect = pygame.Rect(
            self.panel_x + self.panel_width - 100,
            self.panel_y + 20,
            80,
            30,
        )
        self._draw_button("Close", close_btn_rect)

        # Divide panel into sections
        left_panel_width = 250
        middle_panel_width = 300
        right_panel_width = self.panel_width - left_panel_width - middle_panel_width - 60

        left_x = self.panel_x + 20
        middle_x = left_x + left_panel_width + 20
        right_x = middle_x + middle_panel_width + 20
        content_y = self.panel_y + 80

        # Left panel - Autotile set list
        self._render_autotile_list(left_x, content_y, left_panel_width)

        # Middle panel - Autotile configuration
        self._render_autotile_config(middle_x, content_y, middle_panel_width)

        # Right panel - Test grid
        self._render_test_grid(right_x, content_y, right_panel_width)

        # Bottom buttons
        self._render_bottom_buttons()

    def _render_autotile_list(self, x: int, y: int, width: int):
        """Render the list of autotile sets."""
        self._draw_text("Autotile Sets", x, y - 30, size=20)

        # Draw list background
        list_height = self.panel_height - 200
        pygame.draw.rect(
            self.screen,
            self.bg_color,
            (x, y, width, list_height),
        )
        pygame.draw.rect(
            self.screen,
            self.text_color,
            (x, y, width, list_height),
            1,
        )

        # Draw autotile sets
        item_height = 40
        visible_items = min(len(self.autotile_sets), list_height // item_height)

        for i in range(visible_items):
            index = i + self.scroll_offset
            if index >= len(self.autotile_sets):
                break

            autotile_set = self.autotile_sets[index]
            item_y = y + i * item_height

            # Highlight selected
            if index == self.selected_autotile_index:
                pygame.draw.rect(
                    self.screen,
                    self.highlight_color,
                    (x, item_y, width, item_height),
                )

            # Draw autotile set info
            self._draw_text(autotile_set.name, x + 10, item_y + 5, size=16)
            self._draw_text(
                f"{autotile_set.format.value}",
                x + 10,
                item_y + 22,
                size=12,
                color=(180, 180, 180),
            )

        # New autotile button
        new_btn_rect = pygame.Rect(x, y + list_height + 10, width, 30)
        self._draw_button("New Autotile Set", new_btn_rect)

    def _render_autotile_config(self, x: int, y: int, width: int):
        """Render autotile configuration panel."""
        self._draw_text("Configuration", x, y - 30, size=20)

        config_height = self.panel_height - 200
        pygame.draw.rect(
            self.screen,
            self.bg_color,
            (x, y, width, config_height),
        )
        pygame.draw.rect(
            self.screen,
            self.text_color,
            (x, y, width, config_height),
            1,
        )

        if self.current_autotile_set:
            # Show current autotile set config
            content_x = x + 10
            content_y = y + 10

            self._draw_text(f"Name: {self.current_autotile_set.name}", content_x, content_y)
            content_y += 25

            self._draw_text(
                f"Format: {self.current_autotile_set.format.value}", content_x, content_y
            )
            content_y += 25

            self._draw_text(
                f"Base Tile ID: {self.current_autotile_set.base_tile_id}",
                content_x,
                content_y,
            )
            content_y += 25

            self._draw_text(
                f"Tileset: {self.current_autotile_set.tileset_name}",
                content_x,
                content_y,
            )
            content_y += 25

            self._draw_text(
                f"Tile Count: {len(self.current_autotile_set.tile_ids)}",
                content_x,
                content_y,
            )
            content_y += 40

            # Format selector
            self._draw_text("Format:", content_x, content_y)
            content_y += 25

            format_16_btn = pygame.Rect(content_x, content_y, 130, 30)
            self._draw_button(
                "16-Tile",
                format_16_btn,
                active=self.current_autotile_set.format == AutotileFormat.TILE_16,
            )

            format_47_btn = pygame.Rect(content_x + 140, content_y, 130, 30)
            self._draw_button(
                "47-Tile",
                format_47_btn,
                active=self.current_autotile_set.format == AutotileFormat.TILE_47,
            )
            content_y += 50

            # Match same type checkbox
            checkbox_rect = pygame.Rect(content_x, content_y, 20, 20)
            self._draw_checkbox(checkbox_rect, self.current_autotile_set.match_same_type)
            self._draw_text("Match same type", content_x + 30, content_y + 2, size=14)

        else:
            # No autotile set selected
            self._draw_text(
                "Select or create an autotile set",
                x + width // 2 - 100,
                y + config_height // 2,
            )

    def _render_test_grid(self, x: int, y: int, width: int):
        """Render the test grid for previewing autotiles."""
        self._draw_text("Test Grid", x, y - 30, size=20)

        grid_height = self.panel_height - 200
        pygame.draw.rect(
            self.screen,
            self.bg_color,
            (x, y, width, grid_height),
        )
        pygame.draw.rect(
            self.screen,
            self.text_color,
            (x, y, width, grid_height),
            1,
        )

        if self.current_autotile_set and self.test_layer:
            # Calculate tile size to fit in panel
            grid_size = min(width, grid_height) - 20
            tile_size = grid_size // self.test_grid_size

            grid_x = x + (width - grid_size) // 2
            grid_y = y + (grid_height - grid_size) // 2

            # Draw test grid
            for ty in range(self.test_grid_size):
                for tx in range(self.test_grid_size):
                    tile = self.test_layer.get_tile(tx, ty)
                    screen_x = grid_x + tx * tile_size
                    screen_y = grid_y + ty * tile_size

                    # Draw tile
                    if tile and not tile.is_empty():
                        # Draw filled tile
                        pygame.draw.rect(
                            self.screen,
                            self.highlight_color,
                            (screen_x, screen_y, tile_size, tile_size),
                        )

                        # Draw tile ID
                        self._draw_text(
                            str(tile.tile_id),
                            screen_x + 2,
                            screen_y + 2,
                            size=10,
                            color=(0, 0, 0),
                        )
                    else:
                        # Draw empty tile
                        pygame.draw.rect(
                            self.screen,
                            (80, 80, 90),
                            (screen_x, screen_y, tile_size, tile_size),
                        )

                    # Draw grid lines
                    pygame.draw.rect(
                        self.screen,
                        (100, 100, 110),
                        (screen_x, screen_y, tile_size, tile_size),
                        1,
                    )

            # Instructions
            instructions_y = y + grid_height - 80
            self._draw_text("Click to paint", x + 10, instructions_y, size=12)
            self._draw_text("Right-click to erase", x + 10, instructions_y + 15, size=12)
            self._draw_text("Tiles auto-update!", x + 10, instructions_y + 30, size=12)

    def _render_bottom_buttons(self):
        """Render bottom action buttons."""
        button_y = self.panel_y + self.panel_height - 50
        button_width = 120
        button_spacing = 10
        button_x = self.panel_x + 20

        # Save button
        save_btn = pygame.Rect(button_x, button_y, button_width, 30)
        self._draw_button("Save", save_btn)
        button_x += button_width + button_spacing

        # Load button
        load_btn = pygame.Rect(button_x, button_y, button_width, 30)
        self._draw_button("Load", load_btn)
        button_x += button_width + button_spacing

        # Delete button
        delete_btn = pygame.Rect(button_x, button_y, button_width, 30)
        self._draw_button("Delete", delete_btn)
        button_x += button_width + button_spacing

        # Export button
        export_btn = pygame.Rect(button_x, button_y, button_width, 30)
        self._draw_button("Export", export_btn)

    def handle_event(self, event: pygame.event.Event):
        """
        Handle input events.

        Args:
            event: Pygame event
        """
        if not self.visible:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_F11:
                self.toggle()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check close button
            close_btn_rect = pygame.Rect(
                self.panel_x + self.panel_width - 100,
                self.panel_y + 20,
                80,
                30,
            )
            if close_btn_rect.collidepoint(mouse_x, mouse_y):
                self.toggle()
                return

            # Check autotile list clicks
            self._handle_list_click(mouse_x, mouse_y)

            # Check test grid clicks
            self._handle_test_grid_click(mouse_x, mouse_y, event.button)

            # Check bottom buttons
            self._handle_bottom_buttons_click(mouse_x, mouse_y)

    def _handle_list_click(self, mouse_x: int, mouse_y: int):
        """Handle clicks on the autotile set list."""
        left_x = self.panel_x + 20
        content_y = self.panel_y + 80
        left_panel_width = 250
        list_height = self.panel_height - 200
        item_height = 40

        # Check if click is in list area
        if not (
            left_x <= mouse_x <= left_x + left_panel_width
            and content_y <= mouse_y <= content_y + list_height
        ):
            return

        # Calculate clicked item
        relative_y = mouse_y - content_y
        item_index = relative_y // item_height + self.scroll_offset

        if 0 <= item_index < len(self.autotile_sets):
            self.selected_autotile_index = item_index
            self.current_autotile_set = self.autotile_sets[item_index]

            # Clear test grid
            self.test_layer.clear()

    def _handle_test_grid_click(self, mouse_x: int, mouse_y: int, button: int):
        """Handle clicks on the test grid."""
        if not self.current_autotile_set or not self.test_layer:
            return

        # Calculate grid position
        right_panel_width = self.panel_width - 250 - 300 - 60
        right_x = self.panel_x + 20 + 250 + 20 + 300 + 20
        content_y = self.panel_y + 80

        grid_height = self.panel_height - 200
        grid_size = min(right_panel_width, grid_height) - 20
        tile_size = grid_size // self.test_grid_size

        grid_x = right_x + (right_panel_width - grid_size) // 2
        grid_y = content_y + (grid_height - grid_size) // 2

        # Check if click is in grid
        if not (
            grid_x <= mouse_x <= grid_x + grid_size and grid_y <= mouse_y <= grid_y + grid_size
        ):
            return

        # Calculate tile position
        tile_x = (mouse_x - grid_x) // tile_size
        tile_y = (mouse_y - grid_y) // tile_size

        if 0 <= tile_x < self.test_grid_size and 0 <= tile_y < self.test_grid_size:
            if button == 1:  # Left click - paint
                self.autotile_manager.paint_autotile(
                    self.test_layer, tile_x, tile_y, self.current_autotile_set
                )
            elif button == 3:  # Right click - erase
                self.autotile_manager.erase_autotile(self.test_layer, tile_x, tile_y)

    def _handle_bottom_buttons_click(self, mouse_x: int, mouse_y: int):
        """Handle clicks on bottom action buttons."""
        button_y = self.panel_y + self.panel_height - 50
        button_width = 120
        button_spacing = 10
        button_x = self.panel_x + 20

        # Save button
        save_btn = pygame.Rect(button_x, button_y, button_width, 30)
        if save_btn.collidepoint(mouse_x, mouse_y):
            self._save_autotile_sets()
            return

        button_x += button_width + button_spacing

        # Load button
        load_btn = pygame.Rect(button_x, button_y, button_width, 30)
        if load_btn.collidepoint(mouse_x, mouse_y):
            self._load_autotile_sets()
            return

        button_x += button_width + button_spacing

        # Delete button
        delete_btn = pygame.Rect(button_x, button_y, button_width, 30)
        if delete_btn.collidepoint(mouse_x, mouse_y):
            self._delete_current_autotile()
            return

        button_x += button_width + button_spacing

        # Export button
        export_btn = pygame.Rect(button_x, button_y, button_width, 30)
        if export_btn.collidepoint(mouse_x, mouse_y):
            self._export_autotile_sets()
            return

    def _save_autotile_sets(self):
        """Save autotile sets to file."""
        try:
            autotile_data = []
            for autotile_set in self.autotile_sets:
                autotile_data.append(
                    {
                        "name": autotile_set.name,
                        "tileset_name": autotile_set.tileset_name,
                        "format": autotile_set.format.value,
                        "base_tile_id": autotile_set.base_tile_id,
                        "tile_ids": list(autotile_set.tile_ids),
                        "match_same_type": autotile_set.match_same_type,
                        "match_tile_ids": list(autotile_set.match_tile_ids),
                    }
                )

            with open("autotiles.json", "w") as f:
                json.dump(autotile_data, f, indent=2)

            print("Autotile sets saved successfully!")
        except Exception as e:
            print(f"Error saving autotile sets: {e}")

    def _load_autotile_sets(self):
        """Load autotile sets from file."""
        try:
            with open("autotiles.json", "r") as f:
                autotile_data = json.load(f)

            for data in autotile_data:
                autotile_set = AutotileSet(
                    name=data["name"],
                    tileset_name=data["tileset_name"],
                    format=AutotileFormat(data["format"]),
                    base_tile_id=data["base_tile_id"],
                    tile_ids=set(data.get("tile_ids", [])),
                    match_same_type=data.get("match_same_type", True),
                    match_tile_ids=set(data.get("match_tile_ids", [])),
                )
                self.autotile_manager.register_autotile_set(autotile_set)

            self._refresh_autotile_list()
            print("Autotile sets loaded successfully!")
        except FileNotFoundError:
            print("No autotile sets file found.")
        except Exception as e:
            print(f"Error loading autotile sets: {e}")

    def _delete_current_autotile(self):
        """Delete the currently selected autotile set."""
        if self.current_autotile_set:
            # Remove from manager
            if self.current_autotile_set.name in self.autotile_manager.autotile_sets:
                del self.autotile_manager.autotile_sets[self.current_autotile_set.name]

            # Refresh list
            self._refresh_autotile_list()
            self.current_autotile_set = None
            self.selected_autotile_index = 0

            print("Autotile set deleted!")

    def _export_autotile_sets(self):
        """Export autotile sets to JSON file."""
        self._save_autotile_sets()
        print("Autotile sets exported to autotiles.json")

    # Helper rendering methods
    def _draw_text(
        self,
        text: str,
        x: int,
        y: int,
        size: int = 16,
        color: Tuple[int, int, int] = None,
    ):
        """Draw text on screen."""
        if color is None:
            color = self.text_color

        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def _draw_button(
        self,
        text: str,
        rect: pygame.Rect,
        active: bool = False,
    ):
        """Draw a button."""
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)

        # Draw button background
        button_color = self.button_hover_color if is_hover else self.button_color
        if active:
            button_color = self.highlight_color

        pygame.draw.rect(self.screen, button_color, rect)
        pygame.draw.rect(self.screen, self.text_color, rect, 1)

        # Draw button text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def _draw_checkbox(self, rect: pygame.Rect, checked: bool):
        """Draw a checkbox."""
        # Draw checkbox background
        pygame.draw.rect(self.screen, self.button_color, rect)
        pygame.draw.rect(self.screen, self.text_color, rect, 1)

        # Draw checkmark if checked
        if checked:
            pygame.draw.line(
                self.screen,
                self.highlight_color,
                (rect.left + 3, rect.centery),
                (rect.centerx, rect.bottom - 3),
                2,
            )
            pygame.draw.line(
                self.screen,
                self.highlight_color,
                (rect.centerx, rect.bottom - 3),
                (rect.right - 3, rect.top + 3),
                2,
            )
