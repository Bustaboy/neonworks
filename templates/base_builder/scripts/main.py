#!/usr/bin/env python3
"""
Base Builder Template - Main Script

A template demonstrating:
- Building placement and construction
- Resource management
- Grid-based building system
- Survival mechanics
- Production and consumption

Controls:
- Arrow keys: Move camera
- Number keys (1-3): Select building type
- Mouse click: Place building
- ESC: Quit game
"""

import pygame
import sys
from pathlib import Path
from enum import Enum

# Add engine to Python path
engine_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(engine_path))

from engine.core.ecs import World, Entity, Component, System
from engine.systems.base_building import BuildingComponent, BuildingLibrary, Building


# Components
class Position(Component):
    """Grid position component"""

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y


class Resources(Component):
    """Resource storage component"""

    def __init__(self):
        self.wood = 100
        self.stone = 50
        self.food = 50
        self.population = 5
        self.max_population = 5


class Producer(Component):
    """Resource producer component"""

    def __init__(self, resource_type: str, production_rate: float):
        self.resource_type = resource_type
        self.production_rate = production_rate
        self.accumulated = 0.0


class Consumer(Component):
    """Resource consumer component"""

    def __init__(self, resource_type: str, consumption_rate: float):
        self.resource_type = resource_type
        self.consumption_rate = consumption_rate
        self.accumulated = 0.0


class Renderable(Component):
    """Rendering information"""

    def __init__(self, color: tuple, size: int = 32):
        self.color = color
        self.size = size


class BuildingInfo(Component):
    """Building metadata"""

    def __init__(self, building_type: str, name: str):
        self.building_type = building_type
        self.name = name


# Systems
class ProductionSystem(System):
    """Handle resource production and consumption"""

    def __init__(self, resource_storage: Entity):
        super().__init__()
        self.resource_storage = resource_storage

    def update(self, world: World, delta_time: float):
        """Update resource production"""
        resources = self.resource_storage.get_component(Resources)

        # Process producers
        for entity in world.get_entities_with_component(Producer):
            producer = entity.get_component(Producer)

            producer.accumulated += producer.production_rate * delta_time

            # Produce resources when accumulated >= 1
            if producer.accumulated >= 1.0:
                amount = int(producer.accumulated)
                producer.accumulated -= amount

                # Add to storage
                if producer.resource_type == "wood":
                    resources.wood += amount
                elif producer.resource_type == "stone":
                    resources.stone += amount
                elif producer.resource_type == "food":
                    resources.food += amount

        # Process consumers
        for entity in world.get_entities_with_component(Consumer):
            consumer = entity.get_component(Consumer)

            consumer.accumulated += consumer.consumption_rate * delta_time

            # Consume resources when accumulated >= 1
            if consumer.accumulated >= 1.0:
                amount = int(consumer.accumulated)
                consumer.accumulated -= amount

                # Remove from storage
                if consumer.resource_type == "food":
                    resources.food -= amount
                    resources.food = max(0, resources.food)


class RenderSystem(System):
    """Render buildings and UI"""

    def __init__(
        self,
        screen: pygame.Surface,
        camera_x: int = 0,
        camera_y: int = 0,
        tile_size: int = 32,
    ):
        super().__init__()
        self.screen = screen
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.tile_size = tile_size
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)

    def update(self, world: World, delta_time: float):
        """Render game"""
        self.screen.fill((40, 60, 40))  # Dark green background

        # Draw grid
        self._draw_grid()

        # Draw buildings
        for entity in world.get_entities_with_component(Position):
            position = entity.get_component(Position)
            renderable = entity.get_component(Renderable)
            building_info = entity.get_component(BuildingInfo)

            if renderable:
                screen_x = position.x * self.tile_size - self.camera_x
                screen_y = position.y * self.tile_size - self.camera_y

                pygame.draw.rect(
                    self.screen,
                    renderable.color,
                    (screen_x, screen_y, renderable.size, renderable.size),
                )

                # Draw building name
                if building_info:
                    text = self.font.render(
                        building_info.name[:8], True, (255, 255, 255)
                    )
                    self.screen.blit(text, (screen_x + 2, screen_y + 2))

    def _draw_grid(self):
        """Draw grid lines"""
        grid_color = (60, 80, 60)
        width = self.screen.get_width()
        height = self.screen.get_height()

        # Vertical lines
        for x in range(-self.camera_x % self.tile_size, width, self.tile_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, height))

        # Horizontal lines
        for y in range(-self.camera_y % self.tile_size, height, self.tile_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (width, y))

    def render_ui(self, resource_entity: Entity, selected_building: str = None):
        """Render UI overlay"""
        resources = resource_entity.get_component(Resources)

        # Resource display
        ui_y = 10
        self.screen.blit(
            self.large_font.render("Resources", True, (255, 255, 255)), (10, ui_y)
        )

        ui_y += 40
        resource_info = [
            f"Wood: {resources.wood}",
            f"Stone: {resources.stone}",
            f"Food: {resources.food}",
            f"Population: {resources.population}/{resources.max_population}",
        ]

        for info in resource_info:
            text = self.font.render(info, True, (255, 255, 200))
            self.screen.blit(text, (10, ui_y))
            ui_y += 30

        # Building selection
        ui_y += 20
        self.screen.blit(
            self.large_font.render("Buildings (Press Number)", True, (255, 255, 255)),
            (10, ui_y),
        )

        ui_y += 40
        building_list = [
            "1: Lumber Mill (Wood: 20, Stone: 10)",
            "2: Quarry (Wood: 15, Stone: 15)",
            "3: Farm (Wood: 25, Stone: 5)",
        ]

        for i, building in enumerate(building_list):
            color = (
                (100, 255, 100) if selected_building == str(i + 1) else (200, 200, 200)
            )
            text = self.font.render(building, True, color)
            self.screen.blit(text, (10, ui_y))
            ui_y += 30

        # Instructions
        ui_y = self.screen.get_height() - 100
        instructions = [
            "Arrow Keys: Move camera",
            "Number Keys: Select building",
            "Mouse Click: Place building",
            "ESC: Quit",
        ]

        for instruction in instructions:
            text = self.font.render(instruction, True, (150, 150, 150))
            self.screen.blit(text, (10, ui_y))
            ui_y += 25


# Game Logic
class BaseBuilderGame:
    """Main game controller"""

    def __init__(self):
        pygame.init()

        self.WINDOW_WIDTH = 1600
        self.WINDOW_HEIGHT = 900
        self.TILE_SIZE = 64
        self.FPS = 60

        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Base Builder - NeonWorks Template")

        self.clock = pygame.time.Clock()
        self.world = World()

        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 300

        # Resource storage entity
        self.resource_entity = self.world.create_entity()
        self.resource_entity.add_component(Resources())

        # Systems
        self.production_system = ProductionSystem(self.resource_entity)
        self.render_system = RenderSystem(
            self.screen, self.camera_x, self.camera_y, self.TILE_SIZE
        )

        self.world.add_system(self.production_system)
        self.world.add_system(self.render_system)

        # Building library
        self.setup_building_library()

        # Game state
        self.selected_building = None
        self.grid = {}  # Track occupied grid cells

        # Create initial buildings
        self.create_starting_base()

    def setup_building_library(self):
        """Setup available building types"""
        # Building definitions are hard-coded for this template
        # In a real game, these would be loaded from config files
        pass

    def create_starting_base(self):
        """Create starting buildings"""
        # Start with a basic house
        self.create_building("house", 5, 5, "House", (150, 100, 50))

    def create_building(
        self, building_type: str, grid_x: int, grid_y: int, name: str, color: tuple
    ) -> Entity:
        """Create a building entity"""
        building = self.world.create_entity()
        building.add_component(Position(grid_x, grid_y))
        building.add_component(Renderable(color, self.TILE_SIZE))
        building.add_component(BuildingInfo(building_type, name))

        # Add production/consumption based on type
        if building_type == "lumber_mill":
            building.add_component(Producer("wood", 2.0))  # 2 wood per second
        elif building_type == "quarry":
            building.add_component(Producer("stone", 1.5))  # 1.5 stone per second
        elif building_type == "farm":
            building.add_component(Producer("food", 3.0))  # 3 food per second

        # All buildings consume food
        building.add_component(Consumer("food", 0.5))  # 0.5 food per second

        # Mark grid as occupied
        self.grid[(grid_x, grid_y)] = building

        return building

    def try_place_building(self, building_type: str, grid_x: int, grid_y: int) -> bool:
        """Try to place a building at grid position"""
        # Check if cell is occupied
        if (grid_x, grid_y) in self.grid:
            return False

        resources = self.resource_entity.get_component(Resources)

        # Building costs and definitions
        buildings = {
            "1": {
                "type": "lumber_mill",
                "name": "Lumber Mill",
                "color": (139, 69, 19),
                "wood": 20,
                "stone": 10,
            },
            "2": {
                "type": "quarry",
                "name": "Quarry",
                "color": (128, 128, 128),
                "wood": 15,
                "stone": 15,
            },
            "3": {
                "type": "farm",
                "name": "Farm",
                "color": (50, 200, 50),
                "wood": 25,
                "stone": 5,
            },
        }

        if building_type not in buildings:
            return False

        building_def = buildings[building_type]

        # Check resources
        if (
            resources.wood < building_def["wood"]
            or resources.stone < building_def["stone"]
        ):
            print(
                f"Not enough resources! Need {building_def['wood']} wood and {building_def['stone']} stone"
            )
            return False

        # Deduct resources
        resources.wood -= building_def["wood"]
        resources.stone -= building_def["stone"]

        # Create building
        self.create_building(
            building_def["type"],
            grid_x,
            grid_y,
            building_def["name"],
            building_def["color"],
        )

        print(f"Built {building_def['name']} at ({grid_x}, {grid_y})")
        return True

    def screen_to_grid(self, screen_x: int, screen_y: int) -> tuple:
        """Convert screen coordinates to grid coordinates"""
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        grid_x = world_x // self.TILE_SIZE
        grid_y = world_y // self.TILE_SIZE
        return (grid_x, grid_y)

    def run(self):
        """Main game loop"""
        print("Starting Base Builder...")
        print("Build production buildings to gather resources!")
        running = True

        while running:
            delta_time = self.clock.tick(self.FPS) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        self.selected_building = chr(event.key)
                        print(f"Selected building type: {self.selected_building}")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.selected_building:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                        self.try_place_building(self.selected_building, grid_x, grid_y)

            # Handle camera movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.camera_x -= self.camera_speed * delta_time
            if keys[pygame.K_RIGHT]:
                self.camera_x += self.camera_speed * delta_time
            if keys[pygame.K_UP]:
                self.camera_y -= self.camera_speed * delta_time
            if keys[pygame.K_DOWN]:
                self.camera_y += self.camera_speed * delta_time

            # Clamp camera
            self.camera_x = max(0, self.camera_x)
            self.camera_y = max(0, self.camera_y)

            # Update camera in render system
            self.render_system.camera_x = int(self.camera_x)
            self.render_system.camera_y = int(self.camera_y)

            # Update game logic
            self.world.update(delta_time)

            # Render UI
            self.render_system.render_ui(self.resource_entity, self.selected_building)

            # Display
            pygame.display.flip()

        pygame.quit()
        print("Thanks for playing!")


def main():
    """Main entry point"""
    game = BaseBuilderGame()
    game.run()


if __name__ == "__main__":
    main()
