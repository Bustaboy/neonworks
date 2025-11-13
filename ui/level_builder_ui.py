"""
NeonWorks Level Builder UI - Visual Level Editing
Provides complete visual interface for creating and editing game levels.
"""

from typing import Optional, Dict, List, Tuple
import pygame
from ..core.ecs import World, Transform, GridPosition, Sprite
from ..rendering.tilemap import Tilemap, Tile
from ..rendering.ui import UI


class LevelBuilderUI:
    """
    Visual level builder for creating tilemaps and placing entities.
    """

    def __init__(self, screen: pygame.Surface, world: World):
        self.screen = screen
        self.world = world
        self.ui = UI(screen)

        self.visible = False

        # Editor state
        self.current_tool = "tile"  # 'tile', 'entity', 'erase', 'select'
        self.current_layer = 0
        self.selected_tile = None
        self.selected_entity_type = None
        self.brush_size = 1

        # Tile palette
        self.tile_palette = {
            "grass": {"color": (100, 200, 50), "walkable": True, "name": "Grass"},
            "dirt": {"color": (139, 90, 43), "walkable": True, "name": "Dirt"},
            "stone": {"color": (128, 128, 128), "walkable": True, "name": "Stone"},
            "water": {"color": (100, 150, 255), "walkable": False, "name": "Water"},
            "sand": {"color": (255, 220, 150), "walkable": True, "name": "Sand"},
            "lava": {"color": (255, 100, 0), "walkable": False, "name": "Lava"},
            "wall": {"color": (80, 80, 80), "walkable": False, "name": "Wall"},
            "floor": {"color": (200, 200, 200), "walkable": True, "name": "Floor"},
            "void": {"color": (20, 20, 30), "walkable": False, "name": "Void"},
        }

        # Entity templates
        self.entity_templates = {
            "player": {
                "name": "Player",
                "color": (0, 150, 255),
                "components": [
                    "Transform",
                    "Sprite",
                    "Health",
                    "Survival",
                    "TurnActor",
                ],
                "tags": ["player"],
            },
            "enemy": {
                "name": "Enemy",
                "color": (255, 0, 0),
                "components": ["Transform", "Sprite", "Health", "TurnActor"],
                "tags": ["enemy"],
            },
            "chest": {
                "name": "Chest",
                "color": (255, 200, 0),
                "components": ["Transform", "Sprite", "ResourceStorage"],
                "tags": ["interactable"],
            },
            "tree": {
                "name": "Tree",
                "color": (0, 150, 0),
                "components": ["Transform", "Sprite", "GridPosition"],
                "tags": ["obstacle"],
            },
            "rock": {
                "name": "Rock",
                "color": (128, 128, 128),
                "components": ["Transform", "Sprite", "GridPosition"],
                "tags": ["obstacle"],
            },
        }

        # Tilemap
        self.tilemap: Optional[Tilemap] = None
        self.tile_size = 32
        self.grid_width = 50
        self.grid_height = 50

        # UI state
        self.palette_scroll = 0
        self.show_grid = True
        self.show_layer_preview = True

    def initialize_tilemap(self):
        """Initialize a blank tilemap."""
        if self.tilemap is None:
            self.tilemap = Tilemap(
                width=self.grid_width,
                height=self.grid_height,
                tile_size=self.tile_size,
                layers=3,
            )

    def toggle(self):
        """Toggle level builder visibility."""
        self.visible = not self.visible
        if self.visible:
            self.initialize_tilemap()

    def render(self, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the level builder UI."""
        if not self.visible:
            return

        # Render tilemap
        if self.tilemap and self.show_layer_preview:
            self._render_tilemap_preview(camera_offset)

        # Render grid
        if self.show_grid:
            self._draw_grid(camera_offset)

        # Render UI panels
        self._render_tool_panel()
        self._render_palette_panel()
        self._render_layer_panel()

    def _render_tilemap_preview(self, camera_offset: Tuple[int, int]):
        """Render the tilemap for editing."""
        if not self.tilemap:
            return

        for layer_idx in range(self.tilemap.layers):
            # Dim non-current layers
            alpha = 255 if layer_idx == self.current_layer else 100

            for y in range(self.tilemap.height):
                for x in range(self.tilemap.width):
                    tile = self.tilemap.get_tile(x, y, layer_idx)
                    if tile and tile.tile_type in self.tile_palette:
                        tile_data = self.tile_palette[tile.tile_type]

                        screen_x = x * self.tile_size + camera_offset[0]
                        screen_y = y * self.tile_size + camera_offset[1]

                        # Draw tile
                        tile_surface = pygame.Surface(
                            (self.tile_size, self.tile_size), pygame.SRCALPHA
                        )
                        color = (*tile_data["color"], alpha)
                        tile_surface.fill(color)
                        self.screen.blit(tile_surface, (screen_x, screen_y))

    def _draw_grid(self, camera_offset: Tuple[int, int]):
        """Draw the grid lines."""
        grid_color = (100, 100, 100)

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

    def _render_tool_panel(self):
        """Render the tool selection panel."""
        panel_width = 80
        panel_height = 300
        panel_x = 10
        panel_y = 100

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (0, 0, 0, 200))
        self.ui.title("Tools", panel_x + 15, panel_y + 5, size=16)

        button_width = 60
        button_height = 50
        button_x = panel_x + 10
        current_y = panel_y + 35

        # Tile tool
        tile_color = (0, 150, 0) if self.current_tool == "tile" else (0, 80, 0)
        if self.ui.button(
            "Tile", button_x, current_y, button_width, button_height, color=tile_color
        ):
            self.current_tool = "tile"
        current_y += button_height + 5

        # Entity tool
        entity_color = (150, 0, 150) if self.current_tool == "entity" else (80, 0, 80)
        if self.ui.button(
            "Entity",
            button_x,
            current_y,
            button_width,
            button_height,
            color=entity_color,
        ):
            self.current_tool = "entity"
        current_y += button_height + 5

        # Erase tool
        erase_color = (150, 0, 0) if self.current_tool == "erase" else (80, 0, 0)
        if self.ui.button(
            "Erase", button_x, current_y, button_width, button_height, color=erase_color
        ):
            self.current_tool = "erase"
        current_y += button_height + 5

        # Select tool
        select_color = (150, 150, 0) if self.current_tool == "select" else (80, 80, 0)
        if self.ui.button(
            "Select",
            button_x,
            current_y,
            button_width,
            button_height,
            color=select_color,
        ):
            self.current_tool = "select"

    def _render_palette_panel(self):
        """Render the tile/entity palette panel."""
        screen_width = self.screen.get_width()
        panel_width = 250
        panel_height = 600
        panel_x = screen_width - panel_width - 10
        panel_y = 10

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (0, 0, 0, 200))

        # Close button
        if self.ui.button("X", panel_x + panel_width - 35, panel_y + 5, 25, 25):
            self.toggle()

        if self.current_tool == "tile":
            self._render_tile_palette(panel_x, panel_y, panel_width, panel_height)
        elif self.current_tool == "entity":
            self._render_entity_palette(panel_x, panel_y, panel_width, panel_height)
        else:
            self.ui.title("No Palette", panel_x + 60, panel_y + 40, size=18)

    def _render_tile_palette(self, x: int, y: int, width: int, height: int):
        """Render the tile selection palette."""
        self.ui.title("Tile Palette", x + 60, y + 5, size=18)

        item_y = y + 40
        item_height = 50
        item_width = width - 20

        for tile_id, tile_data in self.tile_palette.items():
            # Highlight selected tile
            bg_color = (80, 80, 120) if tile_id == self.selected_tile else (40, 40, 60)

            self.ui.panel(x + 10, item_y, item_width, item_height, bg_color)

            # Color swatch
            pygame.draw.rect(
                self.screen, tile_data["color"], (x + 15, item_y + 5, 30, 30)
            )

            # Name
            self.ui.label(tile_data["name"], x + 50, item_y + 10, size=16)

            # Walkable indicator
            walkable_text = "Walkable" if tile_data["walkable"] else "Blocked"
            walkable_color = (0, 255, 0) if tile_data["walkable"] else (255, 100, 100)
            self.ui.label(
                walkable_text, x + 50, item_y + 28, size=12, color=walkable_color
            )

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                x + 10 <= mouse_pos[0] <= x + 10 + item_width
                and item_y <= mouse_pos[1] <= item_y + item_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.selected_tile = tile_id

            item_y += item_height + 5

    def _render_entity_palette(self, x: int, y: int, width: int, height: int):
        """Render the entity template palette."""
        self.ui.title("Entity Palette", x + 50, y + 5, size=18)

        item_y = y + 40
        item_height = 60
        item_width = width - 20

        for entity_id, entity_data in self.entity_templates.items():
            # Highlight selected entity
            bg_color = (
                (120, 80, 120)
                if entity_id == self.selected_entity_type
                else (60, 40, 60)
            )

            self.ui.panel(x + 10, item_y, item_width, item_height, bg_color)

            # Color swatch
            pygame.draw.rect(
                self.screen, entity_data["color"], (x + 15, item_y + 5, 30, 30)
            )

            # Name
            self.ui.label(entity_data["name"], x + 50, item_y + 5, size=16)

            # Components
            comp_text = ", ".join(entity_data["components"][:2])
            if len(entity_data["components"]) > 2:
                comp_text += "..."
            self.ui.label(
                comp_text, x + 50, item_y + 25, size=10, color=(200, 200, 200)
            )

            # Tags
            tag_text = f"Tags: {', '.join(entity_data['tags'])}"
            self.ui.label(tag_text, x + 50, item_y + 40, size=10, color=(150, 150, 150))

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                x + 10 <= mouse_pos[0] <= x + 10 + item_width
                and item_y <= mouse_pos[1] <= item_y + item_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.selected_entity_type = entity_id

            item_y += item_height + 5

    def _render_layer_panel(self):
        """Render the layer control panel."""
        panel_width = 180
        panel_height = 200
        panel_x = 100
        panel_y = self.screen.get_height() - panel_height - 10

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (0, 0, 0, 200))
        self.ui.title("Layers", panel_x + 50, panel_y + 5, size=18)

        current_y = panel_y + 35

        # Layer buttons
        for layer in range(3):
            layer_color = (0, 100, 200) if layer == self.current_layer else (0, 50, 100)
            layer_name = ["Ground", "Objects", "Overlay"][layer]

            if self.ui.button(
                f"Layer {layer}: {layer_name}",
                panel_x + 10,
                current_y,
                panel_width - 20,
                35,
                color=layer_color,
            ):
                self.current_layer = layer

            current_y += 40

        # Toggle options
        current_y += 10

        grid_text = "Hide Grid" if self.show_grid else "Show Grid"
        if self.ui.button(grid_text, panel_x + 10, current_y, panel_width - 20, 25):
            self.show_grid = not self.show_grid

    def paint_tile(self, grid_x: int, grid_y: int):
        """Paint a tile at the given grid position."""
        if not self.tilemap or self.current_tool != "tile" or not self.selected_tile:
            return

        # Check bounds
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return

        # Create tile
        tile_data = self.tile_palette[self.selected_tile]
        tile = Tile(tile_type=self.selected_tile, walkable=tile_data["walkable"])

        self.tilemap.set_tile(grid_x, grid_y, self.current_layer, tile)

    def place_entity(self, grid_x: int, grid_y: int):
        """Place an entity at the given grid position."""
        if self.current_tool != "entity" or not self.selected_entity_type:
            return

        # Check bounds
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return

        template = self.entity_templates[self.selected_entity_type]

        # Create entity
        entity_id = self.world.create_entity()

        # Add transform
        self.world.add_component(
            entity_id, Transform(x=grid_x * self.tile_size, y=grid_y * self.tile_size)
        )

        # Add grid position
        self.world.add_component(entity_id, GridPosition(grid_x, grid_y))

        # Add sprite
        self.world.add_component(
            entity_id,
            Sprite(
                asset_id=f"entity_{self.selected_entity_type}", color=template["color"]
            ),
        )

        # Add other components based on template
        from ..core.ecs import Health, Survival, TurnActor, ResourceStorage

        if "Health" in template["components"]:
            self.world.add_component(entity_id, Health(current=100, maximum=100))

        if "Survival" in template["components"]:
            self.world.add_component(entity_id, Survival())

        if "TurnActor" in template["components"]:
            self.world.add_component(entity_id, TurnActor(initiative=10))

        if "ResourceStorage" in template["components"]:
            self.world.add_component(entity_id, ResourceStorage(capacity=50))

        # Add tags
        for tag in template["tags"]:
            self.world.tag_entity(entity_id, tag)

        print(f"Placed {template['name']} at ({grid_x}, {grid_y})")

    def erase_tile(self, grid_x: int, grid_y: int):
        """Erase a tile or entity at the given position."""
        if self.current_tool != "erase":
            return

        # Erase tile from tilemap
        if self.tilemap:
            self.tilemap.set_tile(grid_x, grid_y, self.current_layer, None)

        # Erase entities at this position
        to_remove = []
        for entity_id in self.world.entities:
            grid_pos = self.world.get_component(entity_id, GridPosition)
            if grid_pos and grid_pos.grid_x == grid_x and grid_pos.grid_y == grid_y:
                to_remove.append(entity_id)

        for entity_id in to_remove:
            self.world.remove_entity(entity_id)

    def handle_click(self, grid_x: int, grid_y: int):
        """Handle a click on the grid."""
        if not self.visible:
            return False

        if self.current_tool == "tile":
            self.paint_tile(grid_x, grid_y)
            return True
        elif self.current_tool == "entity":
            self.place_entity(grid_x, grid_y)
            return True
        elif self.current_tool == "erase":
            self.erase_tile(grid_x, grid_y)
            return True

        return False

    def save_level(self, filename: str):
        """Save the level to a file."""
        # TODO: Implement level saving
        print(f"Saving level to {filename}")

    def load_level(self, filename: str):
        """Load a level from a file."""
        # TODO: Implement level loading
        print(f"Loading level from {filename}")
