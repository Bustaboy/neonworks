"""
Database Parameter Editor

Modal dialog for selecting database objects (actors, items, skills, weapons, armor, enemies, etc.).
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame


class DatabaseParamEditor:
    """
    Picker for database objects.

    Supports:
    - Actors
    - Items
    - Skills
    - Weapons
    - Armor
    - Enemies
    - Classes
    - States
    - Animations
    """

    DATABASE_TYPES = [
        "actor",
        "item",
        "skill",
        "weapon",
        "armor",
        "enemy",
        "class",
        "state",
        "animation",
    ]

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Picker mode (database type)
        self.db_type = "actor"

        # Selection state
        self.selected_id = 1

        # Database data (can be loaded from game data files)
        self.database: Dict[str, Dict[int, Dict[str, Any]]] = {
            "actor": {},
            "item": {},
            "skill": {},
            "weapon": {},
            "armor": {},
            "enemy": {},
            "class": {},
            "state": {},
            "animation": {},
        }

        # UI state
        self.scroll_offset = 0
        self.items_per_page = 12

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

    def open(self, db_type: str = "actor", initial_id: int = 1) -> None:
        """
        Open the database picker.

        Args:
            db_type: Type of database object to select
            initial_id: Initially selected ID
        """
        self.visible = True
        self.result = None
        self.db_type = db_type if db_type in self.DATABASE_TYPES else "actor"
        self.selected_id = initial_id
        self.scroll_offset = max(0, initial_id - 5)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if editor is still open, False if closed
        """
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                self.result = None
                return False
            elif event.key == pygame.K_UP:
                self.selected_id = max(1, self.selected_id - 1)
                if self.selected_id < self.scroll_offset + 1:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                max_id = self._get_max_id()
                self.selected_id = min(max_id, self.selected_id + 1)
                if self.selected_id > self.scroll_offset + self.items_per_page:
                    self.scroll_offset = min(max_id - self.items_per_page, self.scroll_offset + 1)
            elif event.key == pygame.K_RETURN:
                # Confirm selection
                self._confirm_selection()
                return False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.y < 0:  # Scroll down
                max_id = self._get_max_id()
                self.scroll_offset = min(max_id - self.items_per_page, self.scroll_offset + 1)

        return True

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render the database picker.

        Returns:
            Result data if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(800, screen_width - 100)
        dialog_height = min(700, screen_height - 100)
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog background
        pygame.draw.rect(
            self.screen,
            (30, 30, 45),
            (dialog_x, dialog_y, dialog_width, dialog_height),
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            (80, 80, 100),
            (dialog_x, dialog_y, dialog_width, dialog_height),
            2,
            border_radius=8,
        )

        # Title bar
        title_height = 50
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (dialog_x, dialog_y, dialog_width, title_height),
            border_radius=8,
        )
        title_text = f"Select {self.db_type.title()}"
        title_surface = self.title_font.render(title_text, True, (255, 200, 0))
        self.screen.blit(title_surface, (dialog_x + 20, dialog_y + 12))

        # Type selector tabs
        tab_y = dialog_y + title_height + 10
        self._render_type_tabs(dialog_x + 10, tab_y, dialog_width - 20)

        # List area
        list_y = tab_y + 50
        list_height = dialog_height - title_height - 170

        # Left panel: Object list
        list_width = 350
        self._render_list(dialog_x + 10, list_y, list_width, list_height)

        # Right panel: Object details
        details_x = dialog_x + list_width + 20
        details_width = dialog_width - list_width - 30
        self._render_details(details_x, list_y, details_width, list_height)

        # Bottom buttons
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 60,
        )

        return None

    def _render_type_tabs(self, x: int, y: int, width: int):
        """Render database type selector tabs."""
        tab_width = 90
        tab_height = 35
        tab_spacing = 5
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, db_type in enumerate(self.DATABASE_TYPES):
            if i * (tab_width + tab_spacing) > width - tab_width:
                break

            tab_x = x + i * (tab_width + tab_spacing)
            is_selected = db_type == self.db_type
            is_hover = (
                tab_x <= mouse_pos[0] <= tab_x + tab_width and y <= mouse_pos[1] <= y + tab_height
            )

            # Tab background
            if is_selected:
                tab_color = (60, 100, 160)
            elif is_hover:
                tab_color = (50, 70, 110)
            else:
                tab_color = (40, 50, 80)

            pygame.draw.rect(
                self.screen,
                tab_color,
                (tab_x, y, tab_width, tab_height),
                border_radius=6,
            )

            # Tab text
            tab_text = self.small_font.render(db_type.title(), True, (255, 255, 255))
            text_rect = tab_text.get_rect(center=(tab_x + tab_width // 2, y + tab_height // 2))
            self.screen.blit(tab_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked and not is_selected:
                self.db_type = db_type
                self.selected_id = 1
                self.scroll_offset = 0

    def _render_list(self, x: int, y: int, width: int, height: int):
        """Render the scrollable list of database objects."""
        # List background
        pygame.draw.rect(
            self.screen,
            (25, 25, 38),
            (x, y, width, height),
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            (60, 60, 80),
            (x, y, width, height),
            2,
            border_radius=6,
        )

        # Render items
        item_height = 50
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        db_objects = self.database.get(self.db_type, {})
        max_id = self._get_max_id()

        for i in range(self.items_per_page):
            item_id = self.scroll_offset + i + 1
            if item_id > max_id:
                break

            item_y = y + 5 + i * (item_height + 3)

            is_selected = item_id == self.selected_id
            is_hover = (
                x + 5 <= mouse_pos[0] <= x + width - 5
                and item_y <= mouse_pos[1] <= item_y + item_height
            )

            # Item background
            if is_selected:
                item_color = (70, 100, 160)
            elif is_hover:
                item_color = (50, 50, 75)
            else:
                item_color = (35, 35, 50)

            pygame.draw.rect(
                self.screen,
                item_color,
                (x + 5, item_y, width - 10, item_height),
                border_radius=4,
            )

            # Get object data
            obj_data = db_objects.get(item_id, {})
            obj_name = obj_data.get("name", f"(Unnamed {self.db_type.title()})")

            # Item ID
            id_text = self.font.render(f"#{item_id:03d}", True, (255, 200, 0))
            self.screen.blit(id_text, (x + 15, item_y + 8))

            # Item name
            name_text = self.font.render(obj_name, True, (220, 220, 240))
            # Truncate if too long
            max_name_width = width - 100
            if name_text.get_width() > max_name_width:
                obj_name = obj_name[:25] + "..."
                name_text = self.font.render(obj_name, True, (220, 220, 240))
            self.screen.blit(name_text, (x + 15, item_y + 28))

            # Handle click
            if is_hover and mouse_clicked:
                self.selected_id = item_id

        # Scroll indicators
        if self.scroll_offset > 0:
            arrow_text = self.font.render("▲", True, (200, 200, 200))
            self.screen.blit(arrow_text, (x + width - 30, y + 5))

        if self.scroll_offset + self.items_per_page < max_id:
            arrow_text = self.font.render("▼", True, (200, 200, 200))
            self.screen.blit(arrow_text, (x + width - 30, y + height - 25))

    def _render_details(self, x: int, y: int, width: int, height: int):
        """Render details panel for selected object."""
        # Details background
        pygame.draw.rect(
            self.screen,
            (25, 25, 38),
            (x, y, width, height),
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            (60, 60, 80),
            (x, y, width, height),
            2,
            border_radius=6,
        )

        # Panel title
        title_text = self.font.render("Details", True, (200, 200, 255))
        self.screen.blit(title_text, (x + 10, y + 10))

        # Get selected object data
        db_objects = self.database.get(self.db_type, {})
        obj_data = db_objects.get(self.selected_id, {})

        if not obj_data:
            # No data - show placeholder
            placeholder = self.small_font.render("No data available", True, (150, 150, 150))
            self.screen.blit(placeholder, (x + 15, y + 50))
            return

        # Render object-specific details
        detail_y = y + 45

        # Name
        name = obj_data.get("name", "Unknown")
        name_label = self.font.render("Name:", True, (180, 180, 200))
        self.screen.blit(name_label, (x + 15, detail_y))
        name_value = self.font.render(name, True, (255, 255, 255))
        self.screen.blit(name_value, (x + 100, detail_y))
        detail_y += 35

        # Type-specific details
        if self.db_type == "actor":
            self._render_actor_details(x + 15, detail_y, obj_data)
        elif self.db_type == "item":
            self._render_item_details(x + 15, detail_y, obj_data)
        elif self.db_type == "skill":
            self._render_skill_details(x + 15, detail_y, obj_data)
        elif self.db_type == "weapon":
            self._render_weapon_details(x + 15, detail_y, obj_data)
        elif self.db_type == "armor":
            self._render_armor_details(x + 15, detail_y, obj_data)

    def _render_actor_details(self, x: int, y: int, data: Dict[str, Any]):
        """Render actor-specific details."""
        details = [
            ("Class", data.get("class", "N/A")),
            ("Level", data.get("level", 1)),
            ("Max HP", data.get("max_hp", 100)),
            ("Max MP", data.get("max_mp", 100)),
        ]
        self._render_detail_list(x, y, details)

    def _render_item_details(self, x: int, y: int, data: Dict[str, Any]):
        """Render item-specific details."""
        details = [
            ("Type", data.get("item_type", "Normal")),
            ("Price", data.get("price", 0)),
            ("Description", data.get("description", "")),
        ]
        self._render_detail_list(x, y, details)

    def _render_skill_details(self, x: int, y: int, data: Dict[str, Any]):
        """Render skill-specific details."""
        details = [
            ("Type", data.get("skill_type", "Magic")),
            ("MP Cost", data.get("mp_cost", 0)),
            ("Scope", data.get("scope", "Single")),
            ("Description", data.get("description", "")),
        ]
        self._render_detail_list(x, y, details)

    def _render_weapon_details(self, x: int, y: int, data: Dict[str, Any]):
        """Render weapon-specific details."""
        details = [
            ("Attack", data.get("attack", 0)),
            ("Price", data.get("price", 0)),
            ("Description", data.get("description", "")),
        ]
        self._render_detail_list(x, y, details)

    def _render_armor_details(self, x: int, y: int, data: Dict[str, Any]):
        """Render armor-specific details."""
        details = [
            ("Defense", data.get("defense", 0)),
            ("Price", data.get("price", 0)),
            ("Description", data.get("description", "")),
        ]
        self._render_detail_list(x, y, details)

    def _render_detail_list(self, x: int, y: int, details: List[Tuple[str, Any]]):
        """Render a list of detail key-value pairs."""
        for i, (label, value) in enumerate(details):
            detail_y = y + i * 30
            label_text = self.small_font.render(f"{label}:", True, (180, 180, 200))
            self.screen.blit(label_text, (x, detail_y))

            value_str = str(value)
            if len(value_str) > 30:
                value_str = value_str[:27] + "..."
            value_text = self.small_font.render(value_str, True, (255, 255, 255))
            self.screen.blit(value_text, (x + 100, detail_y))

    def _render_bottom_buttons(self, x: int, y: int):
        """Render OK and Cancel buttons."""
        button_width = 100
        button_height = 40
        button_spacing = 10

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # OK button
        ok_hover = x <= mouse_pos[0] <= x + button_width and y <= mouse_pos[1] <= y + button_height
        ok_color = (0, 150, 0) if ok_hover else (0, 120, 0)

        pygame.draw.rect(
            self.screen,
            ok_color,
            (x, y, button_width, button_height),
            border_radius=6,
        )

        ok_text = self.font.render("OK", True, (255, 255, 255))
        ok_rect = ok_text.get_rect(center=(x + button_width // 2, y + button_height // 2))
        self.screen.blit(ok_text, ok_rect)

        if ok_hover and mouse_clicked:
            self._confirm_selection()

        # Cancel button
        cancel_x = x + button_width + button_spacing
        cancel_hover = (
            cancel_x <= mouse_pos[0] <= cancel_x + button_width
            and y <= mouse_pos[1] <= y + button_height
        )
        cancel_color = (150, 50, 50) if cancel_hover else (120, 30, 30)

        pygame.draw.rect(
            self.screen,
            cancel_color,
            (cancel_x, y, button_width, button_height),
            border_radius=6,
        )

        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        cancel_rect = cancel_text.get_rect(
            center=(cancel_x + button_width // 2, y + button_height // 2)
        )
        self.screen.blit(cancel_text, cancel_rect)

        if cancel_hover and mouse_clicked:
            self.visible = False
            self.result = None

    def _confirm_selection(self):
        """Confirm the current selection and close the dialog."""
        self.visible = False
        self.result = {
            "id": self.selected_id,
            "type": self.db_type,
        }

        # Include object data if available
        db_objects = self.database.get(self.db_type, {})
        if self.selected_id in db_objects:
            self.result["data"] = db_objects[self.selected_id]

    def _get_max_id(self) -> int:
        """Get the maximum ID for the current database type."""
        db_objects = self.database.get(self.db_type, {})
        if db_objects:
            return max(db_objects.keys())
        return 100  # Default max

    def load_database(self, db_type: str, data: Dict[int, Dict[str, Any]]):
        """
        Load database objects.

        Args:
            db_type: Type of database ("actor", "item", etc.)
            data: Dictionary mapping ID to object data
        """
        if db_type in self.DATABASE_TYPES:
            self.database[db_type] = data

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
