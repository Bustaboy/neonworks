# Tutorial 3: Creating UI

Learn to create professional game UI with menus, buttons, and HUD elements in NeonWorks.

## What You'll Learn

- Creating UI entities and components
- Button systems with hover and click
- Menu screens (main menu, pause menu, game over)
- HUD elements (health bars, score display)
- UI layout and positioning
- Screen transitions

## Prerequisites

- Completed [Tutorial 2: Adding Combat](tutorial_02_adding_combat.md)
- OR basic NeonWorks project

## Overview

We'll add a complete UI system to our game:
- Main menu with "Start" and "Quit" buttons
- Pause menu (press ESC)
- Game over screen
- Improved HUD

## Step 1: UI Components

Create or update `scripts/ui_components.py`:

```python
"""UI components."""

from neonworks.core.ecs import Component
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class UIElement(Component):
    """Base UI element."""
    visible: bool = True
    layer: int = 0  # Higher layers render on top

@dataclass
class Button(Component):
    """Clickable button."""
    x: int = 0
    y: int = 0
    width: int = 200
    height: int = 50
    text: str = "Button"
    color: tuple = (70, 70, 90)
    hover_color: tuple = (100, 100, 120)
    text_color: tuple = (255, 255, 255)
    is_hovered: bool = False
    on_click: Optional[Callable] = None

@dataclass
class Text(Component):
    """Text display."""
    x: int = 0
    y: int = 0
    text: str = ""
    color: tuple = (255, 255, 255)
    font_size: int = 36
    centered: bool = False

@dataclass
class Panel(Component):
    """UI panel/background."""
    x: int = 0
    y: int = 0
    width: int = 400
    height: int = 300
    color: tuple = (40, 40, 60, 200)  # Semi-transparent
    border_color: tuple = (255, 255, 255)
    border_width: int = 2

@dataclass
class GameState(Component):
    """Global game state."""
    current_screen: str = "main_menu"  # main_menu, playing, paused, game_over
    score: int = 0
    high_score: int = 0
```

## Step 2: UI Systems

Create `scripts/ui_systems.py`:

```python
"""UI systems."""

from neonworks.core.ecs import System, World
from ui_components import Button, Text, Panel, UIElement, GameState
import pygame

class ButtonSystem(System):
    """Handles button interactions."""

    def __init__(self):
        super().__init__()
        self.priority = 5

    def update(self, world: World, delta_time: float):
        """Update buttons."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for entity in world.get_entities_with_component(Button):
            button = entity.get_component(Button)
            ui_element = entity.get_component(UIElement)

            if not ui_element or not ui_element.visible:
                continue

            # Check hover
            button.is_hovered = (
                button.x <= mouse_pos[0] <= button.x + button.width and
                button.y <= mouse_pos[1] <= button.y + button.height
            )

            # Check click
            if button.is_hovered and mouse_clicked and button.on_click:
                button.on_click()
                # Small delay to prevent multiple triggers
                pygame.time.wait(100)

class UIRenderSystem(System):
    """Renders UI elements."""

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.priority = 150
        self.fonts = {}

    def get_font(self, size: int) -> pygame.font.Font:
        """Get or create font of specified size."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]

    def update(self, world: World, delta_time: float):
        """Render UI elements by layer."""
        # Collect visible UI elements
        elements = []
        for entity in world.get_entities_with_component(UIElement):
            ui_element = entity.get_component(UIElement)
            if ui_element.visible:
                elements.append((entity, ui_element.layer))

        # Sort by layer
        elements.sort(key=lambda x: x[1])

        # Render each element
        for entity, layer in elements:
            if entity.has_component(Panel):
                self._render_panel(entity)
            elif entity.has_component(Button):
                self._render_button(entity)
            elif entity.has_component(Text):
                self._render_text(entity)

    def _render_panel(self, entity):
        """Render panel."""
        panel = entity.get_component(Panel)

        # Create surface with alpha
        surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        surface.fill(panel.color)

        # Draw to screen
        self.screen.blit(surface, (panel.x, panel.y))

        # Draw border
        if panel.border_width > 0:
            rect = pygame.Rect(panel.x, panel.y, panel.width, panel.height)
            pygame.draw.rect(self.screen, panel.border_color, rect, panel.border_width)

    def _render_button(self, entity):
        """Render button."""
        button = entity.get_component(Button)

        # Choose color based on hover
        color = button.hover_color if button.is_hovered else button.color

        # Draw button background
        rect = pygame.Rect(button.x, button.y, button.width, button.height)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

        # Draw text
        font = self.get_font(32)
        text_surface = font.render(button.text, True, button.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def _render_text(self, entity):
        """Render text."""
        text = entity.get_component(Text)
        font = self.get_font(text.font_size)
        text_surface = font.render(text.text, True, text.color)

        if text.centered:
            text_rect = text_surface.get_rect(center=(text.x, text.y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (text.x, text.y))

class ScreenManager(System):
    """Manages screen state."""

    def __init__(self, world: World):
        super().__init__()
        self.world = world
        self.priority = 1
        self.game_state = None

    def update(self, world: World, delta_time: float):
        """Update based on current screen."""
        # Get game state
        if not self.game_state:
            state_entities = world.get_entities_with_component(GameState)
            if state_entities:
                self.game_state = state_entities[0].get_component(GameState)

        # Handle input based on screen
        if self.game_state:
            if self.game_state.current_screen == "playing":
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    self.show_pause_menu()
                    pygame.time.wait(200)

    def show_main_menu(self):
        """Show main menu screen."""
        if self.game_state:
            self.game_state.current_screen = "main_menu"
            self._clear_screen()
            self._create_main_menu()

    def show_pause_menu(self):
        """Show pause menu."""
        if self.game_state:
            self.game_state.current_screen = "paused"
            self._create_pause_menu()

    def show_game_over(self):
        """Show game over screen."""
        if self.game_state:
            self.game_state.current_screen = "game_over"
            self._create_game_over_screen()

    def start_game(self):
        """Start playing."""
        if self.game_state:
            self.game_state.current_screen = "playing"
            self._clear_ui()

    def _clear_screen(self):
        """Clear all entities."""
        for entity in self.world.get_entities():
            if not entity.has_component(GameState):
                self.world.remove_entity(entity.id)

    def _clear_ui(self):
        """Clear only UI entities."""
        for entity in self.world.get_entities_with_component(UIElement):
            self.world.remove_entity(entity.id)

    def _create_main_menu(self):
        """Create main menu UI."""
        # Title
        title = self.world.create_entity()
        title.add_component(UIElement(layer=1))
        title.add_component(Text(
            x=400, y=150,
            text="Coin Collector",
            font_size=72,
            color=(255, 215, 0),
            centered=True
        ))

        # Start button
        start_btn = self.world.create_entity()
        start_btn.add_component(UIElement(layer=1))
        start_btn.add_component(Button(
            x=300, y=300,
            width=200, height=60,
            text="Start Game",
            on_click=lambda: [self.start_game(), self._create_game()]
        ))

        # Quit button
        quit_btn = self.world.create_entity()
        quit_btn.add_component(UIElement(layer=1))
        quit_btn.add_component(Button(
            x=300, y=380,
            width=200, height=60,
            text="Quit",
            on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))
        ))

    def _create_pause_menu(self):
        """Create pause menu UI."""
        # Semi-transparent background
        overlay = self.world.create_entity()
        overlay.add_component(UIElement(layer=10))
        overlay.add_component(Panel(
            x=250, y=150,
            width=300, height=300,
            color=(20, 20, 40, 220)
        ))

        # Paused text
        title = self.world.create_entity()
        title.add_component(UIElement(layer=11))
        title.add_component(Text(
            x=400, y=200,
            text="PAUSED",
            font_size=64,
            centered=True
        ))

        # Resume button
        resume_btn = self.world.create_entity()
        resume_btn.add_component(UIElement(layer=11))
        resume_btn.add_component(Button(
            x=300, y=280,
            width=200, height=50,
            text="Resume",
            on_click=lambda: [
                setattr(self.game_state, 'current_screen', 'playing'),
                self._clear_ui()
            ]
        ))

        # Main menu button
        menu_btn = self.world.create_entity()
        menu_btn.add_component(UIElement(layer=11))
        menu_btn.add_component(Button(
            x=300, y=350,
            width=200, height=50,
            text="Main Menu",
            on_click=self.show_main_menu
        ))

    def _create_game_over_screen(self):
        """Create game over screen."""
        # Clear game entities
        self._clear_screen()

        # Panel
        panel = self.world.create_entity()
        panel.add_component(UIElement(layer=10))
        panel.add_component(Panel(
            x=200, y=150,
            width=400, height=300,
            color=(40, 20, 20, 230)
        ))

        # Game over text
        title = self.world.create_entity()
        title.add_component(UIElement(layer=11))
        title.add_component(Text(
            x=400, y=200,
            text="GAME OVER",
            font_size=64,
            color=(255, 0, 0),
            centered=True
        ))

        # Score
        score_text = self.world.create_entity()
        score_text.add_component(UIElement(layer=11))
        score_text.add_component(Text(
            x=400, y=270,
            text=f"Score: {self.game_state.score}",
            font_size=36,
            centered=True
        ))

        # Retry button
        retry_btn = self.world.create_entity()
        retry_btn.add_component(UIElement(layer=11))
        retry_btn.add_component(Button(
            x=300, y=330,
            width=200, height=50,
            text="Retry",
            on_click=lambda: [self.start_game(), self._create_game()]
        ))

    def _create_game(self):
        """Create game entities."""
        # Import and call game setup from your game.py
        from game import setup_game
        setup_game(self.world, pygame.display.get_surface())
```

## Step 3: Update Main Loop

Update `main.py` to use the screen manager:

```python
#!/usr/bin/env python3
"""Main entry point with UI."""

import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from neonworks.core.ecs import World
from ui_components import GameState
from ui_systems import ButtonSystem, UIRenderSystem, ScreenManager

def main():
    """Main game loop."""
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Coin Collector")

    world = World()

    # Create game state entity
    state_entity = world.create_entity("game_state")
    state_entity.add_component(GameState(current_screen="main_menu"))

    # Add UI systems
    button_system = ButtonSystem()
    ui_render_system = UIRenderSystem(screen)
    screen_manager = ScreenManager(world)

    world.add_system(screen_manager)
    world.add_system(button_system)
    world.add_system(ui_render_system)

    # Show main menu
    screen_manager.show_main_menu()

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill((20, 20, 40))

        # Update world
        delta_time = clock.tick(60) / 1000.0
        world.update(delta_time)

        # Display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
```

## Step 4: Run and Test

```bash
python main.py
```

You should see:
1. Main menu with Start and Quit buttons
2. Press Start to play
3. Press ESC to pause
4. Game over screen when player dies

## Key Concepts

### UI Entity Architecture

UI elements are entities with components:
- `UIElement`: Base visibility and layering
- `Button`: Interactive buttons
- `Text`: Text display
- `Panel`: Background panels

### Screen Management

The `ScreenManager` handles transitions:
- `main_menu`: Initial screen
- `playing`: Active gameplay
- `paused`: Pause overlay
- `game_over`: End screen

### Rendering Layers

UI elements render by layer (higher = on top):
- Layer 0: Game entities
- Layer 1-9: HUD
- Layer 10+: Menus and overlays

## Challenges

### Easy
1. Change button colors and styles
2. Add more buttons (Settings, Credits)
3. Add a subtitle to the main menu

### Medium
1. **Settings menu**: Volume controls, difficulty
2. **Animations**: Fade in/out transitions
3. **Victory screen**: Win condition and special UI
4. **Health bar UI**: Visual health display in HUD

### Hard
1. **Inventory UI**: Grid-based item display
2. **Dialogue boxes**: NPC conversation UI
3. **Minimap**: Show game area overview
4. **Skill tree**: Upgrade system UI

## Next Steps

Continue to [Tutorial 4: Save/Load System](tutorial_04_save_load_system.md) to learn about persisting game state.

## Summary

✅ UI elements are entities with components
✅ Button system handles interactions
✅ Screen manager controls game flow
✅ Layers control render order
✅ Events can trigger UI changes

Great work! Your game now has professional UI! 🎮✨
