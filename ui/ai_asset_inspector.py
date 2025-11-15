"""
AI Asset Inspector

Click-to-inspect interface for entities and tiles.
Shows detailed properties and enables natural language editing.
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..core.ecs import Entity, GridPosition, Sprite, Transform, World
from ..rendering.tilemap import Tile


class InspectedAsset:
    """
    Represents an asset being inspected by the user.
    Can be an entity or a tile.
    """

    def __init__(
        self,
        asset_type: str,  # "entity" or "tile"
        position: Tuple[int, int],
        data: Dict[str, Any],
        entity: Optional[Entity] = None,
        tile: Optional[Tile] = None,
    ):
        self.asset_type = asset_type
        self.position = position
        self.data = data
        self.entity = entity
        self.tile = tile


class AIAssetInspector:
    """
    Asset inspector with AI-powered natural language editing.

    Features:
    - Click entity/tile to inspect
    - See all properties and components
    - Edit via natural language ("make it bigger", "change color")
    - Visual highlighting of selected asset
    - Undo/redo support
    """

    def __init__(self, screen: pygame.Surface, world: World):
        """
        Initialize asset inspector.

        Args:
            screen: Pygame surface to render to
            world: ECS world reference
        """
        self.screen = screen
        self.world = world
        self.visible = False

        # Selected asset
        self.selected_asset: Optional[InspectedAsset] = None

        # UI layout
        self.panel_width = 350
        self.panel_height = 500
        self.panel_x = 0  # Will be set in render (right side)
        self.panel_y = 150  # Below workspace toolbar

        # Colors
        self.bg_color = (35, 35, 45, 240)
        self.header_color = (45, 45, 60)
        self.property_bg_color = (50, 50, 65)
        self.highlight_color = (255, 255, 100, 150)  # Yellow highlight
        self.text_color = (220, 220, 220)
        self.label_color = (150, 150, 180)
        self.value_color = (200, 220, 255)

        # Fonts
        try:
            self.header_font = pygame.font.Font(None, 24)
            self.label_font = pygame.font.Font(None, 18)
            self.value_font = pygame.font.Font(None, 16)
        except:
            self.header_font = pygame.font.SysFont("Arial", 24)
            self.label_font = pygame.font.SysFont("Arial", 18)
            self.value_font = pygame.font.SysFont("Arial", 16)

        # Scroll state
        self.scroll_offset = 0

    def toggle(self):
        """Toggle inspector visibility"""
        self.visible = not self.visible

    def select_entity(self, entity: Entity, grid_pos: Tuple[int, int]):
        """
        Select an entity for inspection.

        Args:
            entity: Entity to inspect
            grid_pos: Grid position of entity
        """
        # Build entity data
        data = {
            "id": entity.id,
            "name": entity.name,
            "tags": list(entity.tags),
            "components": {},
        }

        # Extract component data
        for comp_type, component in entity.components.items():
            comp_name = comp_type.__name__
            comp_data = {}

            if hasattr(component, "__dict__"):
                for key, value in component.__dict__.items():
                    if not key.startswith("_"):
                        comp_data[key] = value

            data["components"][comp_name] = comp_data

        self.selected_asset = InspectedAsset(
            asset_type="entity", position=grid_pos, data=data, entity=entity
        )

        self.visible = True

    def select_tile(self, tile: Tile, grid_pos: Tuple[int, int]):
        """
        Select a tile for inspection.

        Args:
            tile: Tile to inspect
            grid_pos: Grid position of tile
        """
        data = {
            "tile_id": tile.tile_id,
            "tileset_id": tile.tileset_id,
            "position": grid_pos,
        }

        self.selected_asset = InspectedAsset(
            asset_type="tile", position=grid_pos, data=data, tile=tile
        )

        self.visible = True

    def deselect(self):
        """Deselect current asset"""
        self.selected_asset = None

    def render(self, camera_offset: Tuple[int, int], tile_size: int = 32):
        """
        Render asset inspector panel.

        Args:
            camera_offset: Camera position for highlighting
            tile_size: Size of tiles in pixels
        """
        if not self.visible or not self.selected_asset:
            return

        # Highlight selected asset on map
        self._render_highlight(camera_offset, tile_size)

        # Render inspector panel
        screen_width = self.screen.get_width()
        self.panel_x = screen_width - self.panel_width - 10

        # Panel background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        self.screen.blit(panel_surface, (self.panel_x, self.panel_y))

        # Header
        self._render_header()

        # Properties
        self._render_properties()

        # Actions
        self._render_actions()

    def _render_highlight(self, camera_offset: Tuple[int, int], tile_size: int):
        """Render highlight around selected asset"""
        if not self.selected_asset:
            return

        x, y = self.selected_asset.position
        screen_x = x * tile_size - camera_offset[0]
        screen_y = y * tile_size - camera_offset[1]

        # Draw pulsing highlight
        highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        highlight_surface.fill(self.highlight_color)
        self.screen.blit(highlight_surface, (screen_x, screen_y))

        # Draw border
        border_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
        pygame.draw.rect(self.screen, (255, 255, 100), border_rect, 2)

    def _render_header(self):
        """Render panel header"""
        header_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, 40)
        pygame.draw.rect(self.screen, self.header_color, header_rect)

        # Title
        if self.selected_asset.asset_type == "entity":
            title = f"🔍 {self.selected_asset.data.get('name', 'Entity')}"
        else:
            title = f"🔍 Tile {self.selected_asset.data.get('tile_id', '?')}"

        title_text = self.header_font.render(title, True, self.text_color)
        self.screen.blit(title_text, (self.panel_x + 10, self.panel_y + 8))

        # Close button
        close_text = self.label_font.render("✕", True, self.text_color)
        self.screen.blit(close_text, (self.panel_x + self.panel_width - 30, self.panel_y + 10))

    def _render_properties(self):
        """Render asset properties"""
        y = self.panel_y + 50

        if self.selected_asset.asset_type == "entity":
            self._render_entity_properties(y)
        else:
            self._render_tile_properties(y)

    def _render_entity_properties(self, y: int):
        """Render entity properties"""
        data = self.selected_asset.data

        # Basic info
        y = self._render_property("ID", str(data["id"]), y)
        y = self._render_property("Name", data["name"], y)
        y = self._render_property("Tags", ", ".join(data["tags"]), y)
        y = self._render_property("Position", str(self.selected_asset.position), y)

        # Components
        y += 10
        components_label = self.label_font.render("Components:", True, self.label_color)
        self.screen.blit(components_label, (self.panel_x + 10, y))
        y += 25

        for comp_name, comp_data in data["components"].items():
            y = self._render_component(comp_name, comp_data, y)

            if y > self.panel_y + self.panel_height - 100:
                break  # Out of space

    def _render_tile_properties(self, y: int):
        """Render tile properties"""
        data = self.selected_asset.data

        y = self._render_property("Tile ID", str(data["tile_id"]), y)
        y = self._render_property("Tileset", data["tileset_id"], y)
        y = self._render_property("Position", str(data["position"]), y)

    def _render_property(self, label: str, value: str, y: int) -> int:
        """
        Render a property row.

        Returns:
            New y position
        """
        label_text = self.label_font.render(f"{label}:", True, self.label_color)
        self.screen.blit(label_text, (self.panel_x + 15, y))

        value_text = self.value_font.render(str(value), True, self.value_color)
        self.screen.blit(value_text, (self.panel_x + 150, y))

        return y + 25

    def _render_component(self, comp_name: str, comp_data: Dict[str, Any], y: int) -> int:
        """
        Render component data.

        Returns:
            New y position
        """
        # Component name
        comp_bg = pygame.Rect(self.panel_x + 15, y, self.panel_width - 30, 20)
        pygame.draw.rect(self.screen, self.property_bg_color, comp_bg, border_radius=3)

        comp_text = self.label_font.render(comp_name, True, (150, 200, 255))
        self.screen.blit(comp_text, (self.panel_x + 20, y + 2))

        y += 25

        # Component properties
        for key, value in comp_data.items():
            if y > self.panel_y + self.panel_height - 120:
                break

            key_text = self.value_font.render(f"  {key}:", True, self.label_color)
            self.screen.blit(key_text, (self.panel_x + 25, y))

            value_str = str(value)
            if len(value_str) > 20:
                value_str = value_str[:17] + "..."

            value_text = self.value_font.render(value_str, True, self.value_color)
            self.screen.blit(value_text, (self.panel_x + 150, y))

            y += 20

        return y + 5

    def _render_actions(self):
        """Render action buttons"""
        y = self.panel_y + self.panel_height - 80

        # AI Edit hint
        hint_text = self.value_font.render(
            "Use AI Assistant to edit:", True, (150, 150, 150)
        )
        self.screen.blit(hint_text, (self.panel_x + 10, y))

        y += 20
        examples = [
            '"make it bigger"',
            '"change color to red"',
            '"rotate 90 degrees"',
        ]

        for example in examples:
            example_text = self.value_font.render(f"• {example}", True, (180, 180, 180))
            self.screen.blit(example_text, (self.panel_x + 15, y))
            y += 18

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_click(event.pos)

        return False

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click"""
        mx, my = mouse_pos

        # Check close button
        if (
            self.panel_x + self.panel_width - 35 <= mx <= self.panel_x + self.panel_width - 5
            and self.panel_y + 5 <= my <= self.panel_y + 35
        ):
            self.visible = False
            self.selected_asset = None
            return True

        # Check if click is inside panel
        if (
            self.panel_x <= mx <= self.panel_x + self.panel_width
            and self.panel_y <= my <= self.panel_y + self.panel_height
        ):
            return True  # Consume click

        return False

    def get_selected_entity(self) -> Optional[Entity]:
        """Get currently selected entity"""
        if self.selected_asset and self.selected_asset.asset_type == "entity":
            return self.selected_asset.entity
        return None

    def get_selected_tile(self) -> Optional[Tuple[Tile, Tuple[int, int]]]:
        """Get currently selected tile and position"""
        if self.selected_asset and self.selected_asset.asset_type == "tile":
            return (self.selected_asset.tile, self.selected_asset.position)
        return None
