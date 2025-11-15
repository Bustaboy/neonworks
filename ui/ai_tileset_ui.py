"""
AI-powered tileset UI additions for NeonWorks engine.

Provides AI-enhanced tileset management UI:
- Generate new tilesets with AI
- Auto-tag tiles with metadata
- Create tile variations
- Autotiling configuration

Author: NeonWorks Team
Version: 0.1.0
"""

from __future__ import annotations

import os
import tempfile
from typing import Callable, List, Optional, Tuple

import pygame

from neonworks.data.tileset_manager import TilesetManager
from neonworks.editor.ai_tileset_generator import AITilesetGenerator


class AITilesetPanel:
    """
    AI tileset management panel UI component.

    Adds AI-powered tools for tileset generation and management.
    """

    # UI Colors
    BG_COLOR = (40, 40, 45)
    PANEL_BG_COLOR = (50, 50, 55)
    BORDER_COLOR = (70, 70, 75)
    BUTTON_COLOR = (80, 120, 180)
    BUTTON_HOVER_COLOR = (100, 140, 200)
    TEXT_COLOR = (220, 220, 220)
    SUCCESS_COLOR = (100, 255, 100)
    WARNING_COLOR = (255, 200, 100)

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        tileset_manager: TilesetManager,
        on_tileset_generated: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the AI tileset panel.

        Args:
            x: X position
            y: Y position
            width: Width of the panel
            height: Height of the panel
            tileset_manager: TilesetManager instance
            on_tileset_generated: Callback when new tileset is generated
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tileset_manager = tileset_manager
        self.on_tileset_generated = on_tileset_generated

        # Create AI generator
        self.ai_generator = AITilesetGenerator(tileset_manager)

        # UI State
        self.visible = True
        self.status_message = ""
        self.status_time = 0

        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)

        # Buttons
        self.buttons = {}
        self._create_buttons()

        # Generation settings
        self.selected_terrains = ["grass", "dirt", "stone", "water"]
        self.tiles_per_type = 4
        self.tile_size = 32

    def _create_buttons(self):
        """Create UI buttons."""
        button_y = self.y + 40
        button_height = 35
        button_spacing = 10

        self.buttons = {
            "generate": {
                "rect": pygame.Rect(self.x + 10, button_y, self.width - 20, button_height),
                "text": "Generate Tileset",
                "action": self._generate_tileset,
            },
            "auto_tag": {
                "rect": pygame.Rect(
                    self.x + 10,
                    button_y + button_height + button_spacing,
                    self.width - 20,
                    button_height,
                ),
                "text": "Auto-Tag Active Tileset",
                "action": self._auto_tag_tileset,
            },
            "create_variations": {
                "rect": pygame.Rect(
                    self.x + 10,
                    button_y + (button_height + button_spacing) * 2,
                    self.width - 20,
                    button_height,
                ),
                "text": "Create Tile Variations",
                "action": self._create_variations,
            },
        }

    def update(self, dt: float):
        """
        Update panel state.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

        # Update status message timer
        if self.status_time > 0:
            self.status_time -= dt

    def render(self, screen: pygame.Surface):
        """
        Render the AI tileset panel.

        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return

        # Draw background panel
        pygame.draw.rect(screen, self.PANEL_BG_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.BORDER_COLOR, (self.x, self.y, self.width, self.height), 2)

        # Draw title
        title = self.font.render("AI Tileset Tools", True, self.TEXT_COLOR)
        screen.blit(title, (self.x + 10, self.y + 10))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button_id, button_data in self.buttons.items():
            rect = button_data["rect"]
            text = button_data["text"]

            # Check hover
            is_hover = rect.collidepoint(mouse_pos)
            color = self.BUTTON_HOVER_COLOR if is_hover else self.BUTTON_COLOR

            # Draw button
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 2, border_radius=5)

            # Draw text
            text_surface = self.small_font.render(text, True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

        # Draw terrain selection
        self._render_terrain_selection(screen)

        # Draw status message
        if self.status_time > 0:
            self._render_status_message(screen)

    def _render_terrain_selection(self, screen: pygame.Surface):
        """Render terrain type selection checkboxes."""
        start_y = self.y + 180
        checkbox_size = 16
        spacing = 25

        label = self.small_font.render("Terrain Types:", True, self.TEXT_COLOR)
        screen.blit(label, (self.x + 10, start_y))

        y_offset = start_y + 25
        terrains = ["grass", "dirt", "stone", "water", "sand", "lava", "wall", "floor"]

        for i, terrain in enumerate(terrains):
            if i % 2 == 0:
                x = self.x + 10
                if i > 0:
                    y_offset += spacing
            else:
                x = self.x + self.width // 2

            # Checkbox
            checkbox_rect = pygame.Rect(x, y_offset, checkbox_size, checkbox_size)
            is_selected = terrain in self.selected_terrains

            # Draw checkbox
            color = self.BUTTON_COLOR if is_selected else self.BG_COLOR
            pygame.draw.rect(screen, color, checkbox_rect)
            pygame.draw.rect(screen, self.BORDER_COLOR, checkbox_rect, 2)

            # Draw label
            label = self.small_font.render(terrain.capitalize(), True, self.TEXT_COLOR)
            screen.blit(label, (x + checkbox_size + 5, y_offset))

    def _render_status_message(self, screen: pygame.Surface):
        """Render status message at bottom of panel."""
        message_y = self.y + self.height - 30

        # Background
        message_rect = pygame.Rect(self.x + 10, message_y, self.width - 20, 25)
        pygame.draw.rect(screen, self.SUCCESS_COLOR, message_rect, border_radius=3)

        # Text
        text = self.small_font.render(self.status_message, True, (0, 0, 0))
        text_rect = text.get_rect(center=message_rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Check button clicks
            for button_id, button_data in self.buttons.items():
                if button_data["rect"].collidepoint(mouse_pos):
                    button_data["action"]()
                    return True

            # Check terrain checkboxes
            if self._handle_terrain_click(mouse_pos):
                return True

        return False

    def _handle_terrain_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle clicks on terrain checkboxes."""
        start_y = self.y + 205
        checkbox_size = 16
        spacing = 25

        terrains = ["grass", "dirt", "stone", "water", "sand", "lava", "wall", "floor"]

        y_offset = start_y
        for i, terrain in enumerate(terrains):
            if i % 2 == 0:
                x = self.x + 10
                if i > 0:
                    y_offset += spacing
            else:
                x = self.x + self.width // 2

            checkbox_rect = pygame.Rect(x, y_offset, checkbox_size, checkbox_size)

            if checkbox_rect.collidepoint(mouse_pos):
                if terrain in self.selected_terrains:
                    self.selected_terrains.remove(terrain)
                else:
                    self.selected_terrains.append(terrain)
                return True

        return False

    def _generate_tileset(self):
        """Generate a new tileset using AI."""
        if not self.selected_terrains:
            self.show_status("Select at least one terrain type!")
            return

        try:
            # Generate tileset
            tileset_surface, metadata = self.ai_generator.generate_procedural_tileset(
                terrain_types=self.selected_terrains,
                tiles_per_type=self.tiles_per_type,
                tile_size=self.tile_size,
                include_variations=True,
            )

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, dir=tempfile.gettempdir()
            )
            pygame.image.save(tileset_surface, temp_file.name)
            temp_file.close()

            # Add to tileset manager
            tileset_id = f"ai_generated_{len(self.tileset_manager.tilesets)}"
            terrain_names = "_".join(self.selected_terrains[:3])

            self.tileset_manager.add_tileset(
                tileset_id=tileset_id,
                name=f"AI Generated ({terrain_names})",
                image_path=temp_file.name,
                tile_width=self.tile_size,
                tile_height=self.tile_size,
            )

            # Load tileset
            self.tileset_manager.load_tileset(tileset_id)

            # Apply metadata
            tileset = self.tileset_manager.get_tileset(tileset_id)
            tileset.metadata = metadata

            # Set as active
            self.tileset_manager.set_active_tileset(tileset_id)

            # Notify
            if self.on_tileset_generated:
                self.on_tileset_generated(tileset_id)

            self.show_status(f"Generated tileset: {tileset_id}")

        except Exception as e:
            print(f"Error generating tileset: {e}")
            self.show_status(f"Error: {str(e)}")

    def _auto_tag_tileset(self):
        """Auto-tag the active tileset with AI."""
        active_tileset = self.tileset_manager.get_active_tileset()
        if not active_tileset:
            self.show_status("No active tileset!")
            return

        try:
            # Generate metadata
            metadata = self.ai_generator.auto_tag_tileset(
                tileset_id=active_tileset.tileset_id,
                analyze_colors=True,
                analyze_patterns=True,
            )

            # Apply metadata
            for tile_id, tile_metadata in metadata.items():
                self.tileset_manager.set_tile_metadata(
                    tileset_id=active_tileset.tileset_id,
                    tile_id=tile_id,
                    passable=tile_metadata.passable,
                    terrain_tags=tile_metadata.terrain_tags,
                    name=tile_metadata.name,
                )

            self.show_status(f"Auto-tagged {len(metadata)} tiles!")

        except Exception as e:
            print(f"Error auto-tagging tileset: {e}")
            self.show_status(f"Error: {str(e)}")

    def _create_variations(self):
        """Create variations of selected tile."""
        active_tileset = self.tileset_manager.get_active_tileset()
        if not active_tileset:
            self.show_status("No active tileset!")
            return

        # For now, just show a message
        # In a full implementation, this would let the user select a tile
        # and generate variations of it
        self.show_status("Select a tile, then click this button!")

    def show_status(self, message: str, duration: float = 3.0):
        """
        Show a status message.

        Args:
            message: Message to display
            duration: Duration in seconds
        """
        self.status_message = message
        self.status_time = duration

    def toggle_visibility(self):
        """Toggle panel visibility."""
        self.visible = not self.visible

    def show(self):
        """Show the panel."""
        self.visible = True

    def hide(self):
        """Hide the panel."""
        self.visible = False
