"""
Database Manager UI

Visual interface for browsing and editing game database including
characters, items, skills, quests, and game variables.

Hotkey: Ctrl+D
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

import pygame

from neonworks.ui.ui_system import (
    Panel,
    Button,
    Label,
    TextInput,
    Dropdown,
    ScrollPanel,
)


class DatabaseManagerUI:
    """
    Visual database manager for game data.

    Features:
    - Browse characters, items, skills, quests
    - Edit entity properties
    - Add/remove entities
    - Search and filter
    - Save changes back to JSON files
    - Import/export functionality
    """

    # Database categories
    CATEGORIES = [
        "Characters",
        "Items",
        "Skills",
        "Quests",
        "Dialogues",
        "Game Variables",
    ]

    def __init__(self, world, renderer, project_path: Optional[str] = None):
        """Initialize database manager UI."""
        self.world = world
        self.renderer = renderer
        self.visible = False
        self.project_path = project_path or ""

        # State
        self.current_category = "Characters"
        self.database = {}
        self.selected_entity = None
        self.search_query = ""

        # File paths
        self.file_paths = {
            "Characters": "config/characters.json",
            "Items": "config/items.json",
            "Skills": "config/skills.json",
            "Quests": "config/quests.json",
            "Dialogues": "config/dialogues.json",
            "Game Variables": "data/database.json",
        }

        # UI elements
        self._create_ui()

        # Load initial data
        if self.project_path:
            self.load_all_data()

    def _create_ui(self):
        """Create UI elements."""
        screen_width = 1280
        screen_height = 720

        # Main panel
        self.main_panel = Panel(
            x=50,
            y=50,
            width=screen_width - 100,
            height=screen_height - 100,
            color=(40, 40, 50),
        )

        # Title
        self.title_label = Label(
            text="Database Manager (Ctrl+D)",
            x=70,
            y=70,
            font_size=24,
            color=(255, 255, 255),
        )

        # Category dropdown
        self.category_label = Label(text="Category:", x=70, y=120, font_size=14)
        self.category_dropdown = Dropdown(
            x=160, y=115, width=200, height=30, options=self.CATEGORIES
        )

        # Search box
        self.search_label = Label(text="Search:", x=380, y=120, font_size=14)
        self.search_input = TextInput(x=450, y=115, width=300, height=30)

        # Refresh button
        self.refresh_button = Button(
            text="Refresh", x=770, y=115, width=100, height=30, on_click=self.load_all_data
        )

        # Entity list panel (left side)
        self.entity_list_panel = ScrollPanel(
            x=70, y=160, width=300, height=450, color=(50, 50, 60)
        )

        self.entity_count_label = Label(
            text="Entities: 0", x=80, y=170, font_size=12, color=(200, 200, 200)
        )

        # Entity details panel (right side)
        self.details_panel = ScrollPanel(
            x=400, y=160, width=750, height=450, color=(50, 50, 60)
        )

        self.details_label = Label(
            text="Entity Details:", x=410, y=170, font_size=16, color=(200, 200, 200)
        )

        # Bottom buttons
        self.new_button = Button(
            text="New Entity", x=70, y=630, width=120, height=35, on_click=self.new_entity
        )

        self.duplicate_button = Button(
            text="Duplicate",
            x=200,
            y=630,
            width=120,
            height=35,
            on_click=self.duplicate_entity,
        )

        self.delete_button = Button(
            text="Delete", x=330, y=630, width=120, height=35, on_click=self.delete_entity
        )

        self.save_button = Button(
            text="Save All", x=950, y=630, width=120, height=35, on_click=self.save_all_data
        )

        self.close_button = Button(
            text="Close", x=1080, y=630, width=70, height=35, on_click=self.close
        )

    def set_project_path(self, path: str):
        """Set the project path and load data."""
        self.project_path = path
        self.load_all_data()

    def load_all_data(self):
        """Load all database files."""
        if not self.project_path:
            return

        self.database = {}
        project_root = Path(self.project_path)

        for category, file_path in self.file_paths.items():
            full_path = project_root / file_path

            if not full_path.exists():
                self.database[category] = []
                continue

            try:
                with open(full_path, "r") as f:
                    data = json.load(f)

                # Extract array data based on category
                if category == "Game Variables":
                    self.database[category] = data
                else:
                    # Most files have structure: {"category_name": [items]}
                    key = category.lower()
                    if key in data:
                        self.database[category] = data[key]
                    else:
                        # Try singular form
                        singular_key = key.rstrip("s")
                        if singular_key in data:
                            self.database[category] = data[singular_key]
                        else:
                            self.database[category] = []

            except Exception as e:
                print(f"Error loading {category}: {e}")
                self.database[category] = []

    def save_all_data(self):
        """Save all database changes back to files."""
        if not self.project_path:
            print("No project loaded")
            return

        project_root = Path(self.project_path)

        for category, file_path in self.file_paths.items():
            full_path = project_root / file_path

            try:
                # Prepare data structure
                if category == "Game Variables":
                    data = self.database.get(category, {})
                else:
                    key = category.lower()
                    data = {key: self.database.get(category, [])}

                # Save to file
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "w") as f:
                    json.dump(data, f, indent=2)

                print(f"Saved {category} to {file_path}")

            except Exception as e:
                print(f"Error saving {category}: {e}")

        print("All database changes saved successfully!")

    def get_filtered_entities(self) -> List[Any]:
        """Get filtered list of entities based on search."""
        entities = self.database.get(self.current_category, [])

        if not self.search_query:
            return entities

        # Filter based on search query
        query_lower = self.search_query.lower()
        filtered = []

        for entity in entities:
            # Search in ID and name fields
            if isinstance(entity, dict):
                entity_id = str(entity.get("id", "")).lower()
                entity_name = str(entity.get("name", "")).lower()

                if query_lower in entity_id or query_lower in entity_name:
                    filtered.append(entity)

        return filtered

    def new_entity(self):
        """Create a new entity in current category."""
        category = self.current_category

        # Default templates for each category
        templates = {
            "Characters": {
                "id": f"new_character_{len(self.database.get(category, []))}",
                "name": "New Character",
                "level": 1,
                "stats": {
                    "hp": 100,
                    "max_hp": 100,
                    "mp": 50,
                    "max_mp": 50,
                    "attack": 10,
                    "defense": 10,
                },
            },
            "Items": {
                "id": f"new_item_{len(self.database.get(category, []))}",
                "name": "New Item",
                "description": "A new item",
                "type": "consumable",
                "price": 0,
            },
            "Skills": {
                "id": f"new_skill_{len(self.database.get(category, []))}",
                "name": "New Skill",
                "description": "A new skill",
                "type": "physical",
                "mp_cost": 0,
                "power": 100,
            },
            "Quests": {
                "id": f"new_quest_{len(self.database.get(category, []))}",
                "name": "New Quest",
                "description": "A new quest",
                "type": "side",
                "objectives": [],
                "rewards": {},
            },
            "Dialogues": {
                "id": f"new_dialogue_{len(self.database.get(category, []))}",
                "title": "New Dialogue",
                "nodes": [],
            },
        }

        template = templates.get(category, {"id": "new_entity", "name": "New Entity"})

        if category not in self.database:
            self.database[category] = []

        self.database[category].append(template)
        self.selected_entity = template

    def duplicate_entity(self):
        """Duplicate the selected entity."""
        if not self.selected_entity:
            return

        import copy

        duplicate = copy.deepcopy(self.selected_entity)

        # Update ID
        if "id" in duplicate:
            duplicate["id"] = f"{duplicate['id']}_copy"

        if self.current_category in self.database:
            self.database[self.current_category].append(duplicate)
            self.selected_entity = duplicate

    def delete_entity(self):
        """Delete the selected entity."""
        if not self.selected_entity:
            return

        if self.current_category in self.database:
            entities = self.database[self.current_category]
            if self.selected_entity in entities:
                entities.remove(self.selected_entity)
                self.selected_entity = None

    def update(self, dt: float):
        """Update database manager."""
        if not self.visible:
            return

        # Update UI elements
        self.main_panel.update(dt)
        self.category_dropdown.update(dt)
        self.search_input.update(dt)
        self.refresh_button.update(dt)
        self.entity_list_panel.update(dt)
        self.details_panel.update(dt)

        # Update buttons
        self.new_button.update(dt)
        self.duplicate_button.update(dt)
        self.delete_button.update(dt)
        self.save_button.update(dt)
        self.close_button.update(dt)

        # Update current category from dropdown
        self.current_category = self.category_dropdown.selected

        # Update search query
        self.search_query = self.search_input.text

    def render(self, screen: pygame.Surface):
        """Render database manager UI."""
        if not self.visible:
            return

        # Render main panel
        self.main_panel.render(screen)
        self.title_label.render(screen)

        # Render controls
        self.category_label.render(screen)
        self.category_dropdown.render(screen)
        self.search_label.render(screen)
        self.search_input.render(screen)
        self.refresh_button.render(screen)

        # Render entity list
        self.entity_list_panel.render(screen)

        entities = self.get_filtered_entities()
        count_text = f"Entities: {len(entities)}"
        count_label = Label(text=count_text, x=80, y=170, font_size=12, color=(200, 200, 200))
        count_label.render(screen)

        y_offset = 200
        for entity in entities:
            if isinstance(entity, dict):
                entity_id = entity.get("id", "unknown")
                entity_name = entity.get("name", entity.get("title", ""))

                display_text = f"• {entity_id}"
                if entity_name and entity_name != entity_id:
                    display_text += f" ({entity_name})"

                color = (
                    (100, 200, 100) if entity == self.selected_entity else (200, 200, 200)
                )

                label = Label(text=display_text, x=80, y=y_offset, font_size=12, color=color)
                label.render(screen)
                y_offset += 25

        # Render details panel
        self.details_panel.render(screen)

        if self.selected_entity:
            self.details_label.render(screen)

            # Render entity as formatted JSON
            y_offset = 210
            entity_json = json.dumps(self.selected_entity, indent=2)
            lines = entity_json.split("\n")

            for line in lines[:25]:  # Show first 25 lines
                if len(line) > 80:
                    line = line[:77] + "..."

                line_label = Label(
                    text=line, x=410, y=y_offset, font_size=10, color=(220, 220, 220)
                )
                line_label.render(screen)
                y_offset += 18

            # Show "..." if there are more lines
            if len(lines) > 25:
                more_label = Label(
                    text=f"... ({len(lines) - 25} more lines)",
                    x=410,
                    y=y_offset,
                    font_size=10,
                    color=(150, 150, 150),
                )
                more_label.render(screen)

        # Render buttons
        self.new_button.render(screen)
        self.duplicate_button.render(screen)
        self.delete_button.render(screen)
        self.save_button.render(screen)
        self.close_button.render(screen)

    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if not self.visible:
            return

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return

            # Ctrl+D to toggle
            if event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.toggle()
                return

        # Handle UI events
        self.category_dropdown.handle_event(event)
        self.search_input.handle_event(event)
        self.refresh_button.handle_event(event)
        self.new_button.handle_event(event)
        self.duplicate_button.handle_event(event)
        self.delete_button.handle_event(event)
        self.save_button.handle_event(event)
        self.close_button.handle_event(event)

        # Entity list click detection
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check entity list clicks
            if 80 <= mouse_x <= 350 and 200 <= mouse_y <= 600:
                entities = self.get_filtered_entities()
                index = (mouse_y - 200) // 25
                if 0 <= index < len(entities):
                    self.selected_entity = entities[index]

    def toggle(self):
        """Toggle database manager visibility."""
        self.visible = not self.visible

    def close(self):
        """Close database manager."""
        self.visible = False


def get_database_manager(world, renderer, project_path: Optional[str] = None):
    """Get or create database manager instance."""
    if not hasattr(get_database_manager, "_instance"):
        get_database_manager._instance = DatabaseManagerUI(world, renderer, project_path)
    return get_database_manager._instance
