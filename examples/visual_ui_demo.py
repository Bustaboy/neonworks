"""
NeonWorks Visual UI Demo
Complete demonstration of all visual UI systems in the NeonWorks engine.

This example shows how to use:
- Game HUD with stats and resources
- Building placement UI
- Turn-based combat UI
- Navmesh editor
- Level builder
- Settings panel
- Project manager
- Debug console
- Quest editor
- Asset browser

Press F1-F10 to toggle different UI systems (see on-screen help).
"""

import sys
from pathlib import Path

import pygame

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neonworks.audio.audio_manager import AudioManager
from neonworks.core.ecs import (GridPosition, Health, Sprite, Survival,
                                Transform, World)
from neonworks.core.game_loop import GameLoop
from neonworks.input.input_manager import InputManager
from neonworks.systems.base_building import (Building, BuildingSystem,
                                             ResourceStorage)
from neonworks.systems.survival_system import SurvivalSystem
from neonworks.systems.turn_system import TurnActor, TurnSystem
from neonworks.ui.master_ui_manager import MasterUIManager


class VisualUIDemo:
    """
    Complete visual UI demonstration.
    """

    def __init__(self):
        pygame.init()

        # Create window
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("NeonWorks Visual UI Demo")

        # Create clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60

        # Create world
        self.world = World()

        # Add systems
        self.turn_system = TurnSystem()
        self.survival_system = SurvivalSystem()
        self.building_system = BuildingSystem()

        self.world.add_system(self.turn_system)
        self.world.add_system(self.survival_system)
        self.world.add_system(self.building_system)

        # Create managers
        self.audio_manager = AudioManager()
        self.input_manager = InputManager()

        # Create master UI manager
        self.ui_manager = MasterUIManager(
            self.screen,
            self.world,
            audio_manager=self.audio_manager,
            input_manager=self.input_manager,
        )

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Initialize demo
        self._setup_demo_scene()

        # Show welcome message
        self.show_welcome_message()

    def _setup_demo_scene(self):
        """Set up the demo scene with entities."""
        # Create player entity
        player_id = self.world.create_entity()
        self.world.add_component(player_id, Transform(x=400, y=300))
        self.world.add_component(
            player_id, Sprite(asset_id="player", color=(0, 150, 255))
        )
        self.world.add_component(player_id, Health(current=80, maximum=100))
        self.world.add_component(
            player_id,
            Survival(
                hunger=75,
                max_hunger=100,
                thirst=60,
                max_thirst=100,
                energy=50,
                max_energy=100,
            ),
        )
        self.world.add_component(
            player_id, TurnActor(initiative=15, max_action_points=10)
        )
        self.world.add_component(player_id, GridPosition(12, 9))
        self.world.tag_entity(player_id, "player")

        # Add player to turn order
        self.turn_system.add_actor(player_id)

        # Create some enemy entities
        for i in range(3):
            enemy_id = self.world.create_entity()
            self.world.add_component(enemy_id, Transform(x=600 + i * 100, y=400))
            self.world.add_component(
                enemy_id, Sprite(asset_id="enemy", color=(255, 0, 0))
            )
            self.world.add_component(enemy_id, Health(current=50, maximum=50))
            self.world.add_component(
                enemy_id, TurnActor(initiative=10 - i, max_action_points=8)
            )
            self.world.add_component(enemy_id, GridPosition(18 + i * 3, 12))
            self.world.tag_entity(enemy_id, "enemy")
            self.turn_system.add_actor(enemy_id)

        # Create resource storage entity
        storage_id = self.world.create_entity()
        self.world.add_component(storage_id, Transform(x=200, y=200))
        self.world.add_component(
            storage_id, Sprite(asset_id="storage", color=(150, 150, 150))
        )
        self.world.add_component(storage_id, GridPosition(6, 6))

        storage = ResourceStorage(capacity=500)
        storage.resources = {
            "metal": 150,
            "food": 200,
            "water": 180,
            "energy": 100,
            "wood": 120,
        }
        self.world.add_component(storage_id, storage)
        self.world.tag_entity(storage_id, "storage")

        # Create a building entity
        building_id = self.world.create_entity()
        self.world.add_component(building_id, Transform(x=500, y=500))
        self.world.add_component(
            building_id, Sprite(asset_id="farm", color=(100, 200, 50))
        )
        self.world.add_component(building_id, GridPosition(15, 15))

        building = Building(building_type="farm", construction_time=10.0)
        building.under_construction = False
        building.production_rates = {"food": 5}
        building.consumption_rates = {"water": 2}
        self.world.add_component(building_id, building)
        self.world.tag_entity(building_id, "building")

        # Set player as selected entity
        self.ui_manager.set_selected_entity(player_id)

        # Set to game mode
        self.ui_manager.set_mode("game")

    def show_welcome_message(self):
        """Show welcome message in debug console."""
        self.ui_manager.debug_console.add_log("=" * 50, (0, 255, 255))
        self.ui_manager.debug_console.add_log(
            "Welcome to NeonWorks Visual UI Demo!", (255, 255, 0)
        )
        self.ui_manager.debug_console.add_log("=" * 50, (0, 255, 255))
        self.ui_manager.debug_console.add_log("", (255, 255, 255))
        self.ui_manager.debug_console.add_log(
            "Press F1-F10 to toggle UI systems:", (200, 200, 255)
        )
        self.ui_manager.debug_console.add_log(
            "  F1 - Debug Console (you are here!)", (150, 150, 150)
        )
        self.ui_manager.debug_console.add_log("  F2 - Settings", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F3 - Building UI", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F4 - Level Builder", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F5 - Navmesh Editor", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F6 - Quest Editor", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F7 - Asset Browser", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F8 - Project Manager", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F9 - Combat UI", (150, 150, 150))
        self.ui_manager.debug_console.add_log("  F10 - Toggle HUD", (150, 150, 150))
        self.ui_manager.debug_console.add_log("", (255, 255, 255))
        self.ui_manager.debug_console.add_log(
            "Type 'help' for console commands", (200, 200, 200)
        )

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Let UI manager handle events first
            if self.ui_manager.handle_event(event):
                continue

            # Handle other events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Next turn
                    self.turn_system.next_turn()
                    self.ui_manager.show_notification(
                        "Turn advanced", color=(255, 255, 100)
                    )

    def update(self, dt: float):
        """Update game logic."""
        # Update world systems
        self.world.update(dt)

        # Update UI
        mouse_pos = pygame.mouse.get_pos()
        camera_offset = (self.camera_x, self.camera_y)
        self.ui_manager.update(dt, mouse_pos, camera_offset)

    def render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill((20, 20, 30))

        # Draw grid
        self._draw_grid()

        # Draw entities
        self._draw_entities()

        # Render all UI
        camera_offset = (self.camera_x, self.camera_y)
        actual_fps = self.clock.get_fps()
        self.ui_manager.render(actual_fps, camera_offset)

        # Draw instructions if no UI is open
        if not any(
            [
                self.ui_manager.debug_console.visible,
                self.ui_manager.settings_ui.visible,
                self.ui_manager.building_ui.visible,
                self.ui_manager.level_builder.visible,
                self.ui_manager.navmesh_editor.visible,
                self.ui_manager.quest_editor.visible,
                self.ui_manager.asset_browser.visible,
                self.ui_manager.project_manager.visible,
            ]
        ):
            self._draw_instructions()

        # Update display
        pygame.display.flip()

    def _draw_grid(self):
        """Draw background grid."""
        grid_color = (40, 40, 50)
        tile_size = 32

        # Vertical lines
        for x in range(0, self.screen_width, tile_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen_height))

        # Horizontal lines
        for y in range(0, self.screen_height, tile_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.screen_width, y))

    def _draw_entities(self):
        """Draw all entities."""
        for entity_id in self.world.entities:
            transform = self.world.get_component(entity_id, Transform)
            sprite = self.world.get_component(entity_id, Sprite)

            if transform and sprite:
                # Draw entity
                entity_rect = pygame.Rect(
                    transform.x + self.camera_x, transform.y + self.camera_y, 32, 32
                )
                pygame.draw.rect(self.screen, sprite.color, entity_rect)

                # Draw entity ID if debug console has it enabled
                if self.ui_manager.debug_console.show_entity_ids:
                    font = pygame.font.Font(None, 16)
                    id_text = font.render(str(entity_id), True, (255, 255, 255))
                    self.screen.blit(id_text, (entity_rect.x + 8, entity_rect.y + 8))

    def _draw_instructions(self):
        """Draw on-screen instructions."""
        instructions = [
            "NeonWorks Visual UI Demo",
            "",
            "Press F1-F10 to open UI panels",
            "Press SPACE to advance turn",
            "Press ESC to quit",
        ]

        font = pygame.font.Font(None, 24)
        y = self.screen_height - 150

        for line in instructions:
            text = font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.screen_width // 2, y))
            self.screen.blit(text, text_rect)
            y += 25

    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.fps) / 1000.0

            # Handle events
            self.handle_events()

            # Update
            self.update(dt)

            # Render
            self.render()

        pygame.quit()


if __name__ == "__main__":
    demo = VisualUIDemo()
    demo.run()
