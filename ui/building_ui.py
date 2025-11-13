"""
NeonWorks Building UI - Visual Building Placement and Management
Provides complete visual interface for base building system.
"""

from typing import Optional, Dict, List, Tuple
import pygame
from ..core.ecs import World, Transform, GridPosition, Sprite
from ..systems.base_building import Building, ResourceStorage, BuildingSystem
from ..rendering.ui import UI


class BuildingUI:
    """
    Visual UI for building placement, upgrading, and management.
    """

    def __init__(self, screen: pygame.Surface, world: World):
        self.screen = screen
        self.world = world
        self.ui = UI(screen)

        # UI State
        self.visible = False
        self.selected_building_type = None
        self.placement_mode = False
        self.preview_position = None
        self.building_catalog_scroll = 0

        # Building definitions (can be loaded from config)
        self.building_definitions = {
            "house": {
                "name": "House",
                "cost": {"wood": 50, "stone": 30},
                "production": {},
                "consumption": {},
                "description": "Basic shelter for survivors",
                "color": (139, 90, 43),
                "size": (2, 2),
            },
            "farm": {
                "name": "Farm",
                "cost": {"wood": 30, "water": 20},
                "production": {"food": 5},
                "consumption": {"water": 2},
                "description": "Produces food over time",
                "color": (100, 200, 50),
                "size": (3, 3),
            },
            "well": {
                "name": "Well",
                "cost": {"stone": 40, "metal": 10},
                "production": {"water": 3},
                "consumption": {},
                "description": "Provides clean water",
                "color": (100, 150, 255),
                "size": (1, 1),
            },
            "solar_panel": {
                "name": "Solar Panel",
                "cost": {"metal": 100, "energy": 20},
                "production": {"energy": 10},
                "consumption": {},
                "description": "Generates energy from sunlight",
                "color": (255, 255, 0),
                "size": (2, 1),
            },
            "storage": {
                "name": "Storage",
                "cost": {"wood": 40, "metal": 20},
                "production": {},
                "consumption": {},
                "description": "Stores resources (capacity +100)",
                "color": (128, 128, 128),
                "size": (2, 2),
            },
            "workshop": {
                "name": "Workshop",
                "cost": {"wood": 60, "metal": 80, "stone": 40},
                "production": {"metal": 2},
                "consumption": {"energy": 5},
                "description": "Processes raw materials",
                "color": (192, 192, 192),
                "size": (3, 2),
            },
            "wall": {
                "name": "Wall",
                "cost": {"stone": 20},
                "production": {},
                "consumption": {},
                "description": "Defensive barrier",
                "color": (100, 100, 100),
                "size": (1, 1),
            },
            "turret": {
                "name": "Turret",
                "cost": {"metal": 150, "energy": 50},
                "production": {},
                "consumption": {"energy": 3},
                "description": "Automated defense",
                "color": (255, 0, 0),
                "size": (1, 1),
            },
        }

        # Grid settings (should match project settings)
        self.tile_size = 32
        self.grid_width = 50
        self.grid_height = 50

    def toggle(self):
        """Toggle building UI visibility."""
        self.visible = not self.visible
        if not self.visible:
            self.cancel_placement()

    def render(self, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the building UI and placement preview."""
        if not self.visible:
            return

        # Render building catalog panel
        self._render_building_catalog()

        # Render placement preview if in placement mode
        if self.placement_mode and self.preview_position:
            self._render_placement_preview(camera_offset)

    def _render_building_catalog(self):
        """Render the building catalog panel."""
        screen_width = self.screen.get_width()
        panel_width = 320
        panel_height = self.screen.get_height()
        panel_x = screen_width - panel_width

        # Main panel
        self.ui.panel(panel_x, 0, panel_width, panel_height, (0, 0, 0, 200))
        self.ui.title(
            "Building Catalog", panel_x + 70, 10, size=22, color=(255, 200, 0)
        )

        # Close button
        if self.ui.button("X", panel_x + panel_width - 40, 10, 30, 30):
            self.toggle()

        # Resource display
        resources_y = 50
        self.ui.label(
            "Available Resources:",
            panel_x + 10,
            resources_y,
            size=16,
            color=(200, 200, 255),
        )
        resources_y += 25

        total_resources = self._get_total_resources()
        for resource, amount in sorted(total_resources.items()):
            self.ui.label(
                f"{resource.capitalize()}: {amount:.0f}",
                panel_x + 15,
                resources_y,
                size=14,
            )
            resources_y += 20

        # Building list
        building_y = resources_y + 20
        self.ui.label(
            "Buildings:", panel_x + 10, building_y, size=18, color=(255, 255, 100)
        )
        building_y += 30

        for building_type, definition in self.building_definitions.items():
            # Building button
            button_height = 100
            button_color = (
                (40, 40, 60)
                if building_type != self.selected_building_type
                else (60, 60, 100)
            )

            self.ui.panel(
                panel_x + 10, building_y, panel_width - 20, button_height, button_color
            )

            # Building name and color swatch
            pygame.draw.rect(
                self.screen, definition["color"], (panel_x + 15, building_y + 5, 20, 20)
            )
            self.ui.label(
                definition["name"],
                panel_x + 40,
                building_y + 5,
                size=18,
                color=(255, 255, 255),
            )

            # Description
            self.ui.label(
                definition["description"],
                panel_x + 15,
                building_y + 30,
                size=12,
                color=(200, 200, 200),
            )

            # Cost
            cost_text = "Cost: " + ", ".join(
                [f"{k}: {v}" for k, v in definition["cost"].items()]
            )
            can_afford = self._can_afford_building(building_type)
            cost_color = (0, 255, 0) if can_afford else (255, 100, 100)
            self.ui.label(
                cost_text, panel_x + 15, building_y + 50, size=12, color=cost_color
            )

            # Production/Consumption
            if definition["production"]:
                prod_text = "Prod: " + ", ".join(
                    [f"{k}: +{v}" for k, v in definition["production"].items()]
                )
                self.ui.label(
                    prod_text,
                    panel_x + 15,
                    building_y + 65,
                    size=11,
                    color=(100, 255, 100),
                )

            if definition["consumption"]:
                cons_text = "Uses: " + ", ".join(
                    [f"{k}: -{v}" for k, v in definition["consumption"].items()]
                )
                self.ui.label(
                    cons_text,
                    panel_x + 15,
                    building_y + 80,
                    size=11,
                    color=(255, 200, 100),
                )

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                panel_x + 10 <= mouse_pos[0] <= panel_x + panel_width - 10
                and building_y <= mouse_pos[1] <= building_y + button_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.select_building(building_type)

            building_y += button_height + 10

        # Place button (if building selected)
        if self.selected_building_type:
            place_y = panel_height - 100
            if self.ui.button(
                "Place Building", panel_x + 10, place_y, panel_width - 20, 40
            ):
                self.start_placement()

            if self.ui.button(
                "Cancel", panel_x + 10, place_y + 50, panel_width - 20, 35
            ):
                self.cancel_placement()

    def _render_placement_preview(self, camera_offset: Tuple[int, int]):
        """Render the building placement preview on the grid."""
        if not self.selected_building_type or not self.preview_position:
            return

        definition = self.building_definitions[self.selected_building_type]
        grid_x, grid_y = self.preview_position
        size_w, size_h = definition["size"]

        # Calculate screen position
        screen_x = grid_x * self.tile_size + camera_offset[0]
        screen_y = grid_y * self.tile_size + camera_offset[1]

        # Check if placement is valid
        is_valid = self._is_valid_placement(grid_x, grid_y, size_w, size_h)

        # Draw preview
        preview_color = (*definition["color"], 128) if is_valid else (255, 0, 0, 128)
        preview_surface = pygame.Surface(
            (size_w * self.tile_size, size_h * self.tile_size), pygame.SRCALPHA
        )
        preview_surface.fill(preview_color)
        self.screen.blit(preview_surface, (screen_x, screen_y))

        # Draw border
        border_color = (0, 255, 0) if is_valid else (255, 0, 0)
        pygame.draw.rect(
            self.screen,
            border_color,
            (screen_x, screen_y, size_w * self.tile_size, size_h * self.tile_size),
            3,
        )

        # Draw building name
        font = pygame.font.Font(None, 24)
        text = font.render(definition["name"], True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(screen_x + size_w * self.tile_size // 2, screen_y - 15)
        )
        self.screen.blit(text, text_rect)

    def select_building(self, building_type: str):
        """Select a building type."""
        self.selected_building_type = building_type
        self.placement_mode = False
        self.preview_position = None

    def start_placement(self):
        """Enter placement mode."""
        if not self.selected_building_type:
            return

        if not self._can_afford_building(self.selected_building_type):
            print(f"Cannot afford {self.selected_building_type}")
            return

        self.placement_mode = True

    def cancel_placement(self):
        """Cancel placement mode."""
        self.placement_mode = False
        self.preview_position = None
        self.selected_building_type = None

    def update_preview_position(self, grid_x: int, grid_y: int):
        """Update the preview position based on mouse cursor."""
        if self.placement_mode:
            self.preview_position = (grid_x, grid_y)

    def place_building(self, grid_x: int, grid_y: int) -> bool:
        """
        Attempt to place the selected building at the given position.
        Returns True if successful.
        """
        if not self.placement_mode or not self.selected_building_type:
            return False

        definition = self.building_definitions[self.selected_building_type]
        size_w, size_h = definition["size"]

        # Check if valid placement
        if not self._is_valid_placement(grid_x, grid_y, size_w, size_h):
            return False

        # Check if can afford
        if not self._can_afford_building(self.selected_building_type):
            return False

        # Deduct resources
        self._deduct_building_cost(self.selected_building_type)

        # Create building entity
        entity_id = self.world.create_entity()

        # Add components
        self.world.add_component(
            entity_id, Transform(x=grid_x * self.tile_size, y=grid_y * self.tile_size)
        )

        self.world.add_component(entity_id, GridPosition(grid_x, grid_y))

        # Create sprite (placeholder)
        self.world.add_component(
            entity_id,
            Sprite(
                asset_id=f"building_{self.selected_building_type}",
                color=definition["color"],
            ),
        )

        # Add building component
        building = Building(
            building_type=self.selected_building_type,
            construction_time=5.0,  # 5 seconds build time
        )
        building.production_rates = definition["production"].copy()
        building.consumption_rates = definition["consumption"].copy()
        self.world.add_component(entity_id, building)

        # Add resource storage if it's a storage building
        if self.selected_building_type == "storage":
            self.world.add_component(entity_id, ResourceStorage(capacity=100))

        # Tag it
        self.world.tag_entity(entity_id, "building")

        # Cancel placement (single-place mode)
        self.cancel_placement()

        return True

    def _get_total_resources(self) -> Dict[str, float]:
        """Get total available resources."""
        total = {}
        for entity_id in self.world.entities:
            storage = self.world.get_component(entity_id, ResourceStorage)
            if storage:
                for resource, amount in storage.resources.items():
                    total[resource] = total.get(resource, 0) + amount
        return total

    def _can_afford_building(self, building_type: str) -> bool:
        """Check if player can afford the building."""
        definition = self.building_definitions[building_type]
        total_resources = self._get_total_resources()

        for resource, cost in definition["cost"].items():
            if total_resources.get(resource, 0) < cost:
                return False
        return True

    def _deduct_building_cost(self, building_type: str):
        """Deduct building cost from resources."""
        definition = self.building_definitions[building_type]
        cost = definition["cost"].copy()

        # Deduct from storage entities
        for entity_id in self.world.entities:
            storage = self.world.get_component(entity_id, ResourceStorage)
            if storage:
                for resource in list(cost.keys()):
                    if resource in storage.resources and cost[resource] > 0:
                        deduct_amount = min(storage.resources[resource], cost[resource])
                        storage.resources[resource] -= deduct_amount
                        cost[resource] -= deduct_amount

    def _is_valid_placement(
        self, grid_x: int, grid_y: int, size_w: int, size_h: int
    ) -> bool:
        """Check if building can be placed at the given position."""
        # Check bounds
        if (
            grid_x < 0
            or grid_y < 0
            or grid_x + size_w > self.grid_width
            or grid_y + size_h > self.grid_height
        ):
            return False

        # Check for overlapping buildings
        for entity_id in self.world.get_entities_with_tag("building"):
            grid_pos = self.world.get_component(entity_id, GridPosition)
            if grid_pos:
                # Get building size (assume 1x1 if not found)
                building = self.world.get_component(entity_id, Building)
                existing_size = (1, 1)
                if building and building.building_type in self.building_definitions:
                    existing_size = self.building_definitions[building.building_type][
                        "size"
                    ]

                # Check overlap
                if (
                    grid_x < grid_pos.grid_x + existing_size[0]
                    and grid_x + size_w > grid_pos.grid_x
                    and grid_y < grid_pos.grid_y + existing_size[1]
                    and grid_y + size_h > grid_pos.grid_y
                ):
                    return False

        return True

    def handle_click(self, grid_x: int, grid_y: int) -> bool:
        """
        Handle click event for building placement.
        Returns True if click was handled.
        """
        if self.placement_mode:
            return self.place_building(grid_x, grid_y)
        return False
