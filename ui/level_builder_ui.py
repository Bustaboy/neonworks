"""
NeonWorks Level Builder UI - Visual Level Editing
Provides complete visual interface for creating and editing game levels.
"""

import json
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple

import pygame

from ..core.ecs import GridPosition, Sprite, Transform, World
from ..core.event_commands import (
    CommandType,
    EventCommand,
    EventPage,
    GameEvent,
    TriggerType,
)
from ..rendering.tilemap import Tile, Tilemap
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
        self.current_tool = "tile"  # 'tile', 'entity', 'event', 'erase', 'select'
        self.current_layer = 0
        self.selected_tile = None
        self.selected_entity_type = None
        self.selected_event_template = None
        self.brush_size = 1

        # Event data
        self.events: List[GameEvent] = []
        self.event_editor = None  # Will be set by master UI manager

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

        # Event templates
        self.event_templates = {
            "npc": {
                "name": "NPC",
                "color": (100, 150, 255),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "👤",
            },
            "door": {
                "name": "Door",
                "color": (139, 69, 19),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "🚪",
            },
            "chest": {
                "name": "Chest",
                "color": (255, 215, 0),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "📦",
            },
            "sign": {
                "name": "Sign",
                "color": (160, 82, 45),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "📋",
            },
            "trigger": {
                "name": "Trigger",
                "color": (255, 100, 200),
                "trigger": TriggerType.PLAYER_TOUCH,
                "icon": "⚡",
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

        # Render events
        self._render_events(camera_offset)

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

    def _render_events(self, camera_offset: Tuple[int, int]):
        """Render events on the map."""
        for event in self.events:
            screen_x = event.x * self.tile_size + camera_offset[0]
            screen_y = event.y * self.tile_size + camera_offset[1]

            # Get event color from metadata or use default
            event_color = getattr(event, "color", (100, 150, 255))
            event_icon = getattr(event, "icon", "⭐")

            # Draw event background
            event_surface = pygame.Surface(
                (self.tile_size, self.tile_size), pygame.SRCALPHA
            )
            pygame.draw.rect(
                event_surface,
                (*event_color, 180),
                (0, 0, self.tile_size, self.tile_size),
                border_radius=4,
            )
            self.screen.blit(event_surface, (screen_x, screen_y))

            # Draw event icon
            font = pygame.font.Font(None, 24)
            icon_text = font.render(event_icon, True, (255, 255, 255))
            icon_rect = icon_text.get_rect(
                center=(screen_x + self.tile_size // 2, screen_y + self.tile_size // 2)
            )
            self.screen.blit(icon_text, icon_rect)

            # Draw event ID
            id_font = pygame.font.Font(None, 14)
            id_text = id_font.render(f"#{event.id}", True, (255, 255, 255))
            self.screen.blit(id_text, (screen_x + 2, screen_y + 2))

    def _render_tool_panel(self):
        """Render the tool selection panel."""
        panel_width = 80
        panel_height = 350
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

        # Event tool
        event_color = (0, 150, 150) if self.current_tool == "event" else (0, 80, 80)
        if self.ui.button(
            "Event", button_x, current_y, button_width, button_height, color=event_color
        ):
            self.current_tool = "event"
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
        elif self.current_tool == "event":
            self._render_event_palette(panel_x, panel_y, panel_width, panel_height)
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

    def _render_event_palette(self, x: int, y: int, width: int, height: int):
        """Render the event template palette."""
        self.ui.title("Event Palette", x + 50, y + 5, size=18)

        item_y = y + 40
        item_height = 70
        item_width = width - 20

        for event_id, event_data in self.event_templates.items():
            # Highlight selected event
            bg_color = (
                (120, 120, 160)
                if event_id == self.selected_event_template
                else (60, 60, 80)
            )

            self.ui.panel(x + 10, item_y, item_width, item_height, bg_color)

            # Color swatch
            pygame.draw.rect(
                self.screen, event_data["color"], (x + 15, item_y + 5, 30, 30)
            )

            # Icon
            icon_font = pygame.font.Font(None, 36)
            icon_text = icon_font.render(event_data["icon"], True, (255, 255, 255))
            self.screen.blit(icon_text, (x + 15, item_y + 38))

            # Name
            self.ui.label(event_data["name"], x + 50, item_y + 5, size=16)

            # Trigger type
            trigger_text = event_data["trigger"].name.replace("_", " ").title()
            self.ui.label(
                f"Trigger: {trigger_text[:15]}",
                x + 50,
                item_y + 25,
                size=10,
                color=(200, 200, 200),
            )

            # Edit button
            edit_btn_x = x + 10 + item_width - 50
            edit_btn_y = item_y + 40
            mouse_pos = pygame.mouse.get_pos()
            edit_hover = (
                edit_btn_x <= mouse_pos[0] <= edit_btn_x + 45
                and edit_btn_y <= mouse_pos[1] <= edit_btn_y + 22
            )
            edit_color = (100, 100, 200) if edit_hover else (60, 60, 120)

            pygame.draw.rect(
                self.screen,
                edit_color,
                (edit_btn_x, edit_btn_y, 45, 22),
                border_radius=3,
            )
            edit_font = pygame.font.Font(None, 14)
            edit_text = edit_font.render("Edit", True, (255, 255, 255))
            self.screen.blit(edit_text, (edit_btn_x + 10, edit_btn_y + 4))

            # Click to select
            if (
                x + 10 <= mouse_pos[0] <= x + 10 + item_width - 60
                and item_y <= mouse_pos[1] <= item_y + item_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.selected_event_template = event_id

            # Click edit button to open event editor
            if edit_hover and pygame.mouse.get_pressed()[0]:
                if self.event_editor:
                    self.event_editor.toggle()

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
        from ..core.ecs import Health, ResourceStorage, Survival, TurnActor

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

    def place_event(self, grid_x: int, grid_y: int):
        """Place an event at the given grid position."""
        if self.current_tool != "event" or not self.selected_event_template:
            return

        # Check bounds
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return

        # Check if event already exists at this position
        for existing_event in self.events:
            if existing_event.x == grid_x and existing_event.y == grid_y:
                print(f"Event already exists at ({grid_x}, {grid_y})")
                return

        template = self.event_templates[self.selected_event_template]

        # Generate new event ID
        new_id = max([e.id for e in self.events], default=0) + 1

        # Create event with default page
        new_event = GameEvent(
            id=new_id,
            name=f"{template['name']} {new_id:03d}",
            x=grid_x,
            y=grid_y,
            pages=[],
        )

        # Add metadata for rendering
        new_event.color = template["color"]
        new_event.icon = template["icon"]
        new_event.template_type = self.selected_event_template

        # Add a default page
        default_page = EventPage(
            trigger=template["trigger"],
            commands=[],
        )
        new_event.pages.append(default_page)

        self.events.append(new_event)
        print(f"Placed {template['name']} at ({grid_x}, {grid_y}) with ID #{new_id}")

        # Sync events to event editor if available
        if self.event_editor:
            self.event_editor.load_events_from_scene(self.events)

    def erase_tile(self, grid_x: int, grid_y: int):
        """Erase a tile, entity, or event at the given position."""
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

        # Erase events at this position
        events_to_remove = []
        for event in self.events:
            if event.x == grid_x and event.y == grid_y:
                events_to_remove.append(event)

        for event in events_to_remove:
            self.events.remove(event)
            print(f"Erased event #{event.id} at ({grid_x}, {grid_y})")

        # Sync events to event editor if available
        if self.event_editor and events_to_remove:
            self.event_editor.load_events_from_scene(self.events)

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
        elif self.current_tool == "event":
            self.place_event(grid_x, grid_y)
            return True
        elif self.current_tool == "erase":
            self.erase_tile(grid_x, grid_y)
            return True

        return False

    def save_level(self, filename: str):
        """Save the level to a JSON file."""
        level_data = {
            "version": "1.0",
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "tile_size": self.tile_size,
            "tilemap": self._serialize_tilemap(),
            "events": self._serialize_events(),
        }

        try:
            with open(filename, "w") as f:
                json.dump(level_data, f, indent=2)
            print(f"Level saved successfully to {filename}")
            print(f"  - Saved {len(self.events)} events")
        except Exception as e:
            print(f"Error saving level: {e}")

    def load_level(self, filename: str):
        """Load a level from a JSON file."""
        try:
            with open(filename, "r") as f:
                level_data = json.load(f)

            # Load basic properties
            self.grid_width = level_data.get("grid_width", 50)
            self.grid_height = level_data.get("grid_height", 50)
            self.tile_size = level_data.get("tile_size", 32)

            # Load tilemap
            self._deserialize_tilemap(level_data.get("tilemap", {}))

            # Load events
            self.events = self._deserialize_events(level_data.get("events", []))

            # Sync events to event editor
            if self.event_editor:
                self.event_editor.load_events_from_scene(self.events)

            print(f"Level loaded successfully from {filename}")
            print(f"  - Loaded {len(self.events)} events")
        except FileNotFoundError:
            print(f"Error: Level file not found: {filename}")
        except Exception as e:
            print(f"Error loading level: {e}")

    def _serialize_tilemap(self) -> Dict:
        """Serialize the tilemap to a dictionary."""
        if not self.tilemap:
            return {}

        tilemap_data = {
            "width": self.tilemap.width,
            "height": self.tilemap.height,
            "layers": self.tilemap.layers,
            "tiles": [],
        }

        # Serialize tiles
        for layer in range(self.tilemap.layers):
            for y in range(self.tilemap.height):
                for x in range(self.tilemap.width):
                    tile = self.tilemap.get_tile(x, y, layer)
                    if tile:
                        tilemap_data["tiles"].append(
                            {
                                "x": x,
                                "y": y,
                                "layer": layer,
                                "tile_type": tile.tile_type,
                                "walkable": tile.walkable,
                            }
                        )

        return tilemap_data

    def _deserialize_tilemap(self, tilemap_data: Dict):
        """Deserialize tilemap from dictionary."""
        if not tilemap_data:
            self.initialize_tilemap()
            return

        self.tilemap = Tilemap(
            width=tilemap_data.get("width", self.grid_width),
            height=tilemap_data.get("height", self.grid_height),
            tile_size=self.tile_size,
            layers=tilemap_data.get("layers", 3),
        )

        # Deserialize tiles
        for tile_data in tilemap_data.get("tiles", []):
            tile = Tile(
                tile_type=tile_data["tile_type"], walkable=tile_data["walkable"]
            )
            self.tilemap.set_tile(
                tile_data["x"], tile_data["y"], tile_data["layer"], tile
            )

    def _serialize_events(self) -> List[Dict]:
        """Serialize events to a list of dictionaries."""
        events_data = []

        for event in self.events:
            event_dict = {
                "id": event.id,
                "name": event.name,
                "x": event.x,
                "y": event.y,
                "pages": [],
            }

            # Add metadata for rendering
            if hasattr(event, "color"):
                event_dict["color"] = event.color
            if hasattr(event, "icon"):
                event_dict["icon"] = event.icon
            if hasattr(event, "template_type"):
                event_dict["template_type"] = event.template_type

            # Serialize pages
            for page in event.pages:
                page_dict = {
                    "trigger": page.trigger.name,
                    "commands": [],
                }

                # Add conditions
                if page.condition_switch1_valid:
                    page_dict["condition_switch1_valid"] = True
                    page_dict["condition_switch1_id"] = page.condition_switch1_id
                if page.condition_switch2_valid:
                    page_dict["condition_switch2_valid"] = True
                    page_dict["condition_switch2_id"] = page.condition_switch2_id
                if page.condition_variable_valid:
                    page_dict["condition_variable_valid"] = True
                    page_dict["condition_variable_id"] = page.condition_variable_id
                    page_dict["condition_variable_value"] = (
                        page.condition_variable_value
                    )
                if page.condition_self_switch_valid:
                    page_dict["condition_self_switch_valid"] = True
                    page_dict["condition_self_switch_ch"] = (
                        page.condition_self_switch_ch
                    )

                # Serialize commands
                for command in page.commands:
                    command_dict = {
                        "command_type": command.command_type.name,
                        "parameters": command.parameters,
                        "indent": command.indent,
                    }
                    page_dict["commands"].append(command_dict)

                event_dict["pages"].append(page_dict)

            events_data.append(event_dict)

        return events_data

    def _deserialize_events(self, events_data: List[Dict]) -> List[GameEvent]:
        """Deserialize events from a list of dictionaries."""
        events = []

        for event_dict in events_data:
            event = GameEvent(
                id=event_dict["id"],
                name=event_dict["name"],
                x=event_dict["x"],
                y=event_dict["y"],
                pages=[],
            )

            # Restore metadata for rendering
            if "color" in event_dict:
                event.color = tuple(event_dict["color"])
            if "icon" in event_dict:
                event.icon = event_dict["icon"]
            if "template_type" in event_dict:
                event.template_type = event_dict["template_type"]

            # Deserialize pages
            for page_dict in event_dict["pages"]:
                page = EventPage(
                    trigger=TriggerType[page_dict["trigger"]],
                    commands=[],
                )

                # Restore conditions
                page.condition_switch1_valid = page_dict.get(
                    "condition_switch1_valid", False
                )
                page.condition_switch1_id = page_dict.get("condition_switch1_id", 1)
                page.condition_switch2_valid = page_dict.get(
                    "condition_switch2_valid", False
                )
                page.condition_switch2_id = page_dict.get("condition_switch2_id", 1)
                page.condition_variable_valid = page_dict.get(
                    "condition_variable_valid", False
                )
                page.condition_variable_id = page_dict.get("condition_variable_id", 1)
                page.condition_variable_value = page_dict.get(
                    "condition_variable_value", 0
                )
                page.condition_self_switch_valid = page_dict.get(
                    "condition_self_switch_valid", False
                )
                page.condition_self_switch_ch = page_dict.get(
                    "condition_self_switch_ch", "A"
                )

                # Deserialize commands
                for command_dict in page_dict["commands"]:
                    command = EventCommand(
                        command_type=CommandType[command_dict["command_type"]],
                        parameters=command_dict.get("parameters", {}),
                        indent=command_dict.get("indent", 0),
                    )
                    page.commands.append(command)

                event.pages.append(page)

            events.append(event)

        return events
