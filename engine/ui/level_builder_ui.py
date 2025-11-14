"""
Level Builder UI

Visual map editor for placing tiles, events, and other map elements.
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame

from engine.core.event_data import EventManager, GameEvent


class EventSprite:
    """Visual representation of an event on the map."""

    def __init__(self, event: GameEvent):
        self.event = event
        self.x = event.x
        self.y = event.y
        self.surface: Optional[pygame.Surface] = None
        self._create_sprite()

    def _create_sprite(self):
        """Create a visual sprite for the event."""
        # For now, create a simple colored square
        # TODO: Load actual character graphics
        self.surface = pygame.Surface((32, 32))

        # Color based on event type/trigger
        page = self.event.pages[0] if self.event.pages else None
        if page:
            trigger = page.trigger.value if hasattr(page.trigger, "value") else "action_button"
            colors = {
                "action_button": (100, 150, 255),  # Blue
                "player_touch": (255, 150, 100),  # Orange
                "autorun": (255, 100, 100),  # Red
                "parallel": (100, 255, 100),  # Green
                "event_touch": (255, 255, 100),  # Yellow
            }
            color = colors.get(trigger, (200, 200, 200))
        else:
            color = (200, 200, 200)

        self.surface.fill(color)

        # Draw event name
        font = pygame.font.Font(None, 16)
        text = font.render(self.event.name[:3], True, (255, 255, 255))
        text_rect = text.get_rect(center=(16, 16))
        self.surface.blit(text, text_rect)

    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, tile_size: int):
        """
        Render the event sprite.

        Args:
            screen: Pygame surface to render to
            camera_x: Camera offset X
            camera_y: Camera offset Y
            tile_size: Size of tiles in pixels
        """
        if not self.surface:
            return

        # Calculate screen position
        screen_x = self.event.x * tile_size - camera_x
        screen_y = self.event.y * tile_size - camera_y

        # Scale sprite if needed
        if tile_size != 32:
            scaled = pygame.transform.scale(self.surface, (tile_size, tile_size))
            screen.blit(scaled, (screen_x, screen_y))
        else:
            screen.blit(self.surface, (screen_x, screen_y))

        # Draw selection highlight if selected
        # This will be handled by the LevelBuilderUI


class LevelBuilderUI:
    """
    Level/Map editor with event placement capabilities.

    Controls:
    - Left Click: Select/Place event
    - Right Click: Delete event
    - Double Click: Edit event
    - Arrow Keys: Move camera
    - E: Create new event at cursor
    - F5: Open event editor for selected event
    - Ctrl+S: Save map
    - Ctrl+O: Open map
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = True

        # Event management
        self.event_manager = EventManager()
        self.event_sprites: Dict[int, EventSprite] = {}

        # Map settings
        self.map_width = 50
        self.map_height = 50
        self.tile_size = 32

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Selection
        self.selected_event_id: Optional[int] = None
        self.hover_x: Optional[int] = None
        self.hover_y: Optional[int] = None

        # Editing mode
        self.mode = "select"  # select, place, delete

        # UI state
        self.last_click_time = 0
        self.double_click_threshold = 300  # milliseconds

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if event.type == pygame.KEYDOWN:
            # Camera movement
            if event.key == pygame.K_LEFT:
                self.camera_x -= self.tile_size
                return True
            elif event.key == pygame.K_RIGHT:
                self.camera_x += self.tile_size
                return True
            elif event.key == pygame.K_UP:
                self.camera_y -= self.tile_size
                return True
            elif event.key == pygame.K_DOWN:
                self.camera_y += self.tile_size
                return True

            # Create event
            elif event.key == pygame.K_e:
                if self.hover_x is not None and self.hover_y is not None:
                    self.create_event_at_cursor()
                return True

            # Save/Load
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save_map()
                return True
            elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.load_map()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                current_time = pygame.time.get_ticks()
                is_double_click = (
                    current_time - self.last_click_time < self.double_click_threshold
                )
                self.last_click_time = current_time

                if is_double_click:
                    self.handle_double_click(event.pos)
                else:
                    self.handle_left_click(event.pos)
                return True

            elif event.button == 3:  # Right click
                self.handle_right_click(event.pos)
                return True

        elif event.type == pygame.MOUSEMOTION:
            self.update_hover(event.pos)

        return False

    def update(self, delta_time: float):
        """Update level builder state."""
        pass

    def render(self):
        """Render the level builder."""
        # Draw grid
        self._render_grid()

        # Draw events
        self._render_events()

        # Draw hover highlight
        self._render_hover()

        # Draw selection
        self._render_selection()

        # Draw UI overlay
        self._render_ui_overlay()

    def _render_grid(self):
        """Render the map grid."""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Calculate visible grid range
        start_x = max(0, self.camera_x // self.tile_size)
        start_y = max(0, self.camera_y // self.tile_size)
        end_x = min(self.map_width, (self.camera_x + screen_width) // self.tile_size + 1)
        end_y = min(self.map_height, (self.camera_y + screen_height) // self.tile_size + 1)

        # Draw grid lines
        for x in range(start_x, end_x + 1):
            screen_x = x * self.tile_size - self.camera_x
            pygame.draw.line(
                self.screen, (50, 50, 50), (screen_x, 0), (screen_x, screen_height)
            )

        for y in range(start_y, end_y + 1):
            screen_y = y * self.tile_size - self.camera_y
            pygame.draw.line(
                self.screen, (50, 50, 50), (0, screen_y), (screen_width, screen_y)
            )

    def _render_events(self):
        """Render all event sprites."""
        for event_sprite in self.event_sprites.values():
            event_sprite.render(self.screen, self.camera_x, self.camera_y, self.tile_size)

    def _render_hover(self):
        """Render hover highlight."""
        if self.hover_x is None or self.hover_y is None:
            return

        screen_x = self.hover_x * self.tile_size - self.camera_x
        screen_y = self.hover_y * self.tile_size - self.camera_y

        # Draw highlight
        highlight = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        highlight.fill((255, 255, 100, 100))
        self.screen.blit(highlight, (screen_x, screen_y))

    def _render_selection(self):
        """Render selection highlight."""
        if self.selected_event_id is None:
            return

        event = self.event_manager.get_event(self.selected_event_id)
        if not event:
            return

        screen_x = event.x * self.tile_size - self.camera_x
        screen_y = event.y * self.tile_size - self.camera_y

        # Draw selection border
        pygame.draw.rect(
            self.screen,
            (255, 255, 0),
            (screen_x, screen_y, self.tile_size, self.tile_size),
            3,
        )

    def _render_ui_overlay(self):
        """Render UI overlay with info and controls."""
        # Background panel
        panel_height = 120
        panel = pygame.Surface((self.screen.get_width(), panel_height), pygame.SRCALPHA)
        panel.fill((30, 30, 40, 220))
        self.screen.blit(panel, (0, 0))

        # Title
        title = self.font.render("Level Builder", True, (255, 200, 0))
        self.screen.blit(title, (10, 10))

        # Info
        y = 40
        info_lines = [
            f"Camera: ({self.camera_x // self.tile_size}, {self.camera_y // self.tile_size})",
            f"Events: {len(self.event_sprites)}",
            f"Mode: {self.mode}",
        ]

        if self.hover_x is not None and self.hover_y is not None:
            info_lines.append(f"Cursor: ({self.hover_x}, {self.hover_y})")

        for line in info_lines:
            text = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (10, y))
            y += 20

        # Controls on the right
        x = self.screen.get_width() - 400
        y = 10
        controls = [
            "E - Create Event",
            "Click - Select",
            "Double Click - Edit",
            "Right Click - Delete",
            "Arrows - Move Camera",
            "Ctrl+S - Save",
        ]

        for control in controls:
            text = self.small_font.render(control, True, (180, 180, 200))
            self.screen.blit(text, (x, y))
            y += 18

    def update_hover(self, mouse_pos: Tuple[int, int]):
        """Update hover position based on mouse."""
        mouse_x, mouse_y = mouse_pos

        # Convert to grid coordinates
        grid_x = (mouse_x + self.camera_x) // self.tile_size
        grid_y = (mouse_y + self.camera_y) // self.tile_size

        if 0 <= grid_x < self.map_width and 0 <= grid_y < self.map_height:
            self.hover_x = grid_x
            self.hover_y = grid_y
        else:
            self.hover_x = None
            self.hover_y = None

    def handle_left_click(self, mouse_pos: Tuple[int, int]):
        """Handle left click (select)."""
        if self.hover_x is None or self.hover_y is None:
            return

        # Check if clicking on an event
        for event_id, event_sprite in self.event_sprites.items():
            if event_sprite.event.x == self.hover_x and event_sprite.event.y == self.hover_y:
                self.selected_event_id = event_id
                print(f"Selected event: {event_sprite.event.name}")
                return

        # Clicked on empty space
        self.selected_event_id = None

    def handle_right_click(self, mouse_pos: Tuple[int, int]):
        """Handle right click (delete)."""
        if self.hover_x is None or self.hover_y is None:
            return

        # Find event at position
        for event_id, event_sprite in list(self.event_sprites.items()):
            if event_sprite.event.x == self.hover_x and event_sprite.event.y == self.hover_y:
                self.delete_event(event_id)
                return

    def handle_double_click(self, mouse_pos: Tuple[int, int]):
        """Handle double click (edit)."""
        if self.selected_event_id is not None:
            self.edit_selected_event()

    def create_event_at_cursor(self):
        """Create a new event at cursor position."""
        if self.hover_x is None or self.hover_y is None:
            return

        event = self.event_manager.create_event(
            name="New Event", x=self.hover_x, y=self.hover_y
        )
        self.add_event_sprite(event)
        self.selected_event_id = event.id
        print(f"Created event at ({self.hover_x}, {self.hover_y})")

    def add_event_sprite(self, event: GameEvent):
        """Add an event sprite to the map."""
        sprite = EventSprite(event)
        self.event_sprites[event.id] = sprite

    def delete_event(self, event_id: int):
        """Delete an event."""
        if event_id in self.event_sprites:
            event_name = self.event_sprites[event_id].event.name
            del self.event_sprites[event_id]
            self.event_manager.delete_event(event_id)
            if self.selected_event_id == event_id:
                self.selected_event_id = None
            print(f"Deleted event: {event_name}")

    def edit_selected_event(self):
        """Open event editor for selected event."""
        if self.selected_event_id is None:
            return

        event = self.event_manager.get_event(self.selected_event_id)
        if event:
            print(f"Opening editor for: {event.name}")
            # TODO: Open event editor UI
            # This will be integrated with MasterUIManager

    def save_map(self, filepath: str = "data/maps/current_map.json"):
        """Save current map to file."""
        from pathlib import Path

        path = Path(filepath)
        self.event_manager.save_to_file(path)
        print(f"✓ Map saved to {filepath}")

    def load_map(self, filepath: str = "data/maps/current_map.json"):
        """Load map from file."""
        from pathlib import Path

        path = Path(filepath)
        if self.event_manager.load_from_file(path):
            # Recreate sprites
            self.event_sprites.clear()
            for event in self.event_manager.events.values():
                self.add_event_sprite(event)
            print(f"✓ Map loaded from {filepath}")
        else:
            print(f"✗ Failed to load map from {filepath}")

    def get_event_at_position(self, x: int, y: int) -> Optional[GameEvent]:
        """Get event at grid position."""
        for event in self.event_manager.events.values():
            if event.x == x and event.y == y:
                return event
        return None
