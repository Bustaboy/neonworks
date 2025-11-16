"""
Database Editor UI - Visual Database Management Interface

Provides a comprehensive three-panel interface for managing all game database entries
including actors, items, skills, enemies, weapons, armors, states, classes, and animations.

Features:
- Category selection tabs (left panel)
- Entry list with search/filter (middle panel)
- Detail editor with field-specific inputs (right panel)
- CRUD operations (Create, Read, Update, Delete, Duplicate)
- Graphics preview for icons and sprites
- Auto-save functionality
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame

from neonworks.engine.data.database_manager import (
    CATEGORY_TYPES,
    DatabaseEntry,
    DatabaseManager,
)
from neonworks.engine.data.database_schema import (
    Actor,
    Animation,
    Armor,
    ArmorType,
    Class,
    DamageType,
    Effect,
    EffectType,
    ElementType,
    Enemy,
    EquipType,
    Item,
    ItemType,
    Skill,
    SkillType,
    State,
    StateRestriction,
    Weapon,
    WeaponType,
)


class DatabaseEditorUI:
    """
    Visual editor for game database with three-panel layout:
    - Left: Category tabs
    - Middle: Entry list with search
    - Right: Detail editor
    """

    # Category display names and order
    CATEGORIES = [
        ("actors", "Actors"),
        ("classes", "Classes"),
        ("skills", "Skills"),
        ("items", "Items"),
        ("weapons", "Weapons"),
        ("armors", "Armors"),
        ("enemies", "Enemies"),
        ("states", "States"),
        ("animations", "Animations"),
    ]

    def __init__(self, screen: pygame.Surface, database_path: Optional[Path] = None):
        self.screen = screen
        self.visible = False

        # Database manager
        self.db = DatabaseManager()
        self.database_path = database_path or Path("data/database.json")

        # Load database if it exists
        if self.database_path.exists():
            try:
                self.db.load_from_file(self.database_path)
            except Exception as e:
                print(f"⚠ Failed to load database: {e}")

        # UI State
        self.current_category = "actors"  # Currently selected category
        self.current_entry: Optional[DatabaseEntry] = None  # Currently selected entry
        self.search_query = ""  # Search/filter text
        self.entry_list_scroll = 0  # Scroll position for entry list
        self.detail_scroll = 0  # Scroll position for detail panel

        # Input state
        self.active_input_field: Optional[str] = None  # Currently editing field
        self.input_text = ""  # Text being entered
        self.input_cursor_pos = 0  # Cursor position in input

        # Unsaved changes tracking
        self.has_unsaved_changes = False

    # =========================================================================
    # Main Render Methods
    # =========================================================================

    def render(self):
        """Render the database editor UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Main panel (full screen with padding)
        panel_width = screen_width - 40
        panel_height = screen_height - 40
        panel_x = 20
        panel_y = 20

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Main background panel
        pygame.draw.rect(
            self.screen,
            (20, 20, 30),
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            (80, 80, 100),
            (panel_x, panel_y, panel_width, panel_height),
            2,
            border_radius=8,
        )

        # Title bar
        title_height = 50
        self._render_title_bar(panel_x, panel_y, panel_width, title_height)

        # Content area (three panels)
        content_y = panel_y + title_height + 10
        content_height = panel_height - title_height - 20

        # Calculate panel widths
        category_panel_width = 180
        entry_list_width = 300
        detail_panel_width = panel_width - category_panel_width - entry_list_width - 40

        # Render three panels
        self._render_category_panel(panel_x + 10, content_y, category_panel_width, content_height)
        self._render_entry_list_panel(
            panel_x + category_panel_width + 20,
            content_y,
            entry_list_width,
            content_height,
        )
        self._render_detail_panel(
            panel_x + category_panel_width + entry_list_width + 30,
            content_y,
            detail_panel_width,
            content_height,
        )

    def _render_title_bar(self, x: int, y: int, width: int, height: int):
        """Render the title bar with close button."""
        # Title bar background
        pygame.draw.rect(self.screen, (40, 40, 60), (x, y, width, height), border_radius=8)

        # Title text
        font = pygame.font.Font(None, 32)
        title_text = "Database Editor"
        if self.has_unsaved_changes:
            title_text += " *"
        title_surface = font.render(title_text, True, (100, 200, 255))
        self.screen.blit(title_surface, (x + 20, y + 12))

        # Entry count
        count = self.db.get_count(self.current_category)
        count_font = pygame.font.Font(None, 20)
        count_surface = count_font.render(f"{count} entries", True, (180, 180, 200))
        self.screen.blit(count_surface, (x + 250, y + 18))

        # Save button
        save_btn_x = x + width - 180
        save_btn_y = y + 10
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        save_hover = (
            save_btn_x <= mouse_pos[0] <= save_btn_x + 70
            and save_btn_y <= mouse_pos[1] <= save_btn_y + 30
        )
        save_color = (0, 180, 0) if save_hover else (0, 120, 0)

        if self.has_unsaved_changes:
            pygame.draw.rect(
                self.screen,
                save_color,
                (save_btn_x, save_btn_y, 70, 30),
                border_radius=4,
            )
            btn_font = pygame.font.Font(None, 20)
            btn_text = btn_font.render("Save", True, (255, 255, 255))
            self.screen.blit(btn_text, (save_btn_x + 18, save_btn_y + 7))

            if save_hover and mouse_pressed:
                self._save_database()

        # Close button
        close_btn_x = x + width - 95
        close_btn_y = y + 10
        close_hover = (
            close_btn_x <= mouse_pos[0] <= close_btn_x + 80
            and close_btn_y <= mouse_pos[1] <= close_btn_y + 30
        )
        close_color = (200, 50, 50) if close_hover else (150, 0, 0)

        pygame.draw.rect(
            self.screen,
            close_color,
            (close_btn_x, close_btn_y, 80, 30),
            border_radius=4,
        )
        close_font = pygame.font.Font(None, 20)
        close_text = close_font.render("Close", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn_x + 18, close_btn_y + 7))

        if close_hover and mouse_pressed:
            self.toggle()

    def _render_category_panel(self, x: int, y: int, width: int, height: int):
        """Render the category selection panel (left panel)."""
        # Panel background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=6)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 2, border_radius=6)

        # Panel title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("Categories", True, (200, 200, 255))
        self.screen.blit(title_surface, (x + 10, y + 10))

        # Category tabs
        current_y = y + 40
        tab_height = 40
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for category_id, category_name in self.CATEGORIES:
            is_selected = self.current_category == category_id
            is_hovered = (
                x + 10 <= mouse_pos[0] <= x + width - 10
                and current_y <= mouse_pos[1] <= current_y + tab_height
            )

            # Tab background
            if is_selected:
                tab_color = (60, 80, 140)
            elif is_hovered:
                tab_color = (50, 50, 80)
            else:
                tab_color = (40, 40, 60)

            pygame.draw.rect(
                self.screen,
                tab_color,
                (x + 10, current_y, width - 20, tab_height),
                border_radius=4,
            )

            # Category name
            cat_font = pygame.font.Font(None, 18)
            cat_text = cat_font.render(category_name, True, (255, 255, 255))
            self.screen.blit(cat_text, (x + 20, current_y + 12))

            # Entry count
            count = self.db.get_count(category_id)
            count_surface = cat_font.render(f"({count})", True, (180, 180, 200))
            self.screen.blit(count_surface, (x + width - 50, current_y + 12))

            # Click to select
            if is_hovered and mouse_pressed:
                if self.current_category != category_id:
                    self.current_category = category_id
                    self.current_entry = None
                    self.search_query = ""
                    self.entry_list_scroll = 0

            current_y += tab_height + 5

    def _render_entry_list_panel(self, x: int, y: int, width: int, height: int):
        """Render the entry list panel with search (middle panel)."""
        # Panel background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=6)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 2, border_radius=6)

        # Panel title
        font = pygame.font.Font(None, 20)
        category_display = dict(self.CATEGORIES).get(self.current_category, self.current_category)
        title_surface = font.render(category_display, True, (200, 200, 255))
        self.screen.blit(title_surface, (x + 10, y + 10))

        # Search bar
        search_y = y + 40
        self._render_search_bar(x + 10, search_y, width - 20)

        # New entry button
        new_btn_y = search_y + 40
        self._render_new_entry_button(x + 10, new_btn_y, width - 20)

        # Entry list
        list_y = new_btn_y + 45
        list_height = height - (list_y - y) - 10
        self._render_entry_list(x + 10, list_y, width - 20, list_height)

    def _render_search_bar(self, x: int, y: int, width: int):
        """Render the search/filter input bar."""
        bar_height = 30
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Search bar background
        is_active = self.active_input_field == "search"
        bar_color = (60, 60, 100) if is_active else (40, 40, 60)
        pygame.draw.rect(self.screen, bar_color, (x, y, width, bar_height), border_radius=4)

        # Search icon/text
        font = pygame.font.Font(None, 18)
        if self.search_query:
            text_surface = font.render(self.search_query, True, (255, 255, 255))
        else:
            text_surface = font.render("Search...", True, (120, 120, 140))
        self.screen.blit(text_surface, (x + 10, y + 8))

        # Click to activate search
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + bar_height and mouse_pressed:
            self.active_input_field = "search"
            self.input_text = self.search_query

    def _render_new_entry_button(self, x: int, y: int, width: int):
        """Render the 'New Entry' button."""
        btn_height = 35
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        is_hovered = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + btn_height
        btn_color = (0, 170, 0) if is_hovered else (0, 120, 0)

        pygame.draw.rect(self.screen, btn_color, (x, y, width, btn_height), border_radius=4)

        font = pygame.font.Font(None, 20)
        btn_text = font.render("+ New Entry", True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=(x + width // 2, y + btn_height // 2))
        self.screen.blit(btn_text, text_rect)

        if is_hovered and mouse_pressed:
            self._create_new_entry()

    def _render_entry_list(self, x: int, y: int, width: int, height: int):
        """Render the scrollable list of entries."""
        # Get filtered entries
        entries = self._get_filtered_entries()

        if not entries:
            # Show empty message
            font = pygame.font.Font(None, 18)
            msg = font.render("No entries found", True, (150, 150, 150))
            self.screen.blit(msg, (x + width // 2 - 70, y + height // 2))
            return

        # Render entries
        item_height = 60
        current_y = y
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        visible_entries = entries[self.entry_list_scroll :]

        for i, entry in enumerate(visible_entries):
            if current_y + item_height > y + height:
                break

            actual_index = i + self.entry_list_scroll
            is_selected = self.current_entry == entry
            is_hovered = (
                x <= mouse_pos[0] <= x + width
                and current_y <= mouse_pos[1] <= current_y + item_height
            )

            # Entry background
            if is_selected:
                item_color = (80, 80, 140)
            elif is_hovered:
                item_color = (55, 55, 85)
            else:
                item_color = (45, 45, 65)

            pygame.draw.rect(
                self.screen,
                item_color,
                (x, current_y, width, item_height),
                border_radius=4,
            )

            # Entry ID
            id_font = pygame.font.Font(None, 18)
            id_text = id_font.render(f"#{entry.id:04d}", True, (255, 200, 0))
            self.screen.blit(id_text, (x + 10, current_y + 8))

            # Entry name
            name_font = pygame.font.Font(None, 20)
            entry_name = entry.name if entry.name else f"Unnamed {self.current_category}"
            # Truncate if too long
            if len(entry_name) > 20:
                entry_name = entry_name[:17] + "..."
            name_text = name_font.render(entry_name, True, (255, 255, 255))
            self.screen.blit(name_text, (x + 10, current_y + 28))

            # Icon preview (if available)
            if hasattr(entry, "icon_index") and entry.icon_index > 0:
                icon_font = pygame.font.Font(None, 16)
                icon_text = icon_font.render(f"Icon: {entry.icon_index}", True, (180, 180, 200))
                self.screen.blit(icon_text, (x + width - 80, current_y + 8))

            # Click to select
            if is_hovered and mouse_pressed:
                self.current_entry = entry
                self.detail_scroll = 0

            current_y += item_height + 3

        # Scroll indicators
        if self.entry_list_scroll > 0:
            arrow_font = pygame.font.Font(None, 24)
            up_arrow = arrow_font.render("▲", True, (200, 200, 200))
            self.screen.blit(up_arrow, (x + width - 20, y - 5))

        if len(entries) > len(visible_entries) + self.entry_list_scroll:
            arrow_font = pygame.font.Font(None, 24)
            down_arrow = arrow_font.render("▼", True, (200, 200, 200))
            self.screen.blit(down_arrow, (x + width - 20, y + height - 20))

    def _render_detail_panel(self, x: int, y: int, width: int, height: int):
        """Render the detail editor panel (right panel)."""
        # Panel background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=6)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 2, border_radius=6)

        if not self.current_entry:
            # Show placeholder
            font = pygame.font.Font(None, 20)
            msg = font.render("Select an entry to edit", True, (150, 150, 150))
            self.screen.blit(msg, (x + width // 2 - 100, y + height // 2))
            return

        # Panel title
        font = pygame.font.Font(None, 20)
        title_text = f"Edit {self.current_entry.name[:20]}"
        title_surface = font.render(title_text, True, (200, 200, 255))
        self.screen.blit(title_surface, (x + 10, y + 10))

        # Action buttons (Delete, Duplicate)
        self._render_action_buttons(x, y + 40, width)

        # Detail fields
        fields_y = y + 90
        fields_height = height - 100
        self._render_detail_fields(x + 10, fields_y, width - 20, fields_height)

    def _render_action_buttons(self, x: int, y: int, width: int):
        """Render action buttons (Delete, Duplicate)."""
        btn_width = (width - 30) // 2
        btn_height = 35
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Duplicate button
        dup_x = x + 10
        dup_hover = (
            dup_x <= mouse_pos[0] <= dup_x + btn_width and y <= mouse_pos[1] <= y + btn_height
        )
        dup_color = (0, 120, 180) if dup_hover else (0, 80, 140)

        pygame.draw.rect(self.screen, dup_color, (dup_x, y, btn_width, btn_height), border_radius=4)
        font = pygame.font.Font(None, 18)
        dup_text = font.render("Duplicate", True, (255, 255, 255))
        self.screen.blit(dup_text, (dup_x + btn_width // 2 - 35, y + 10))

        if dup_hover and mouse_pressed:
            self._duplicate_entry()

        # Delete button
        del_x = dup_x + btn_width + 10
        del_hover = (
            del_x <= mouse_pos[0] <= del_x + btn_width and y <= mouse_pos[1] <= y + btn_height
        )
        del_color = (200, 50, 50) if del_hover else (150, 0, 0)

        pygame.draw.rect(self.screen, del_color, (del_x, y, btn_width, btn_height), border_radius=4)
        del_text = font.render("Delete", True, (255, 255, 255))
        self.screen.blit(del_text, (del_x + btn_width // 2 - 25, y + 10))

        if del_hover and mouse_pressed:
            self._delete_entry()

    def _render_detail_fields(self, x: int, y: int, width: int, height: int):
        """Render editable fields for the current entry."""
        if not self.current_entry:
            return

        current_y = y
        field_height = 30
        label_font = pygame.font.Font(None, 16)
        value_font = pygame.font.Font(None, 18)

        # Common fields for all entries
        common_fields = [
            ("id", "ID", "int", True),  # Read-only
            ("name", "Name", "str", False),
            ("icon_index", "Icon Index", "int", False),
            ("description", "Description", "str", False),
            ("note", "Note", "str", False),
        ]

        # Render common fields
        for field_name, label, field_type, readonly in common_fields:
            if current_y + field_height > y + height:
                break

            value = getattr(self.current_entry, field_name, "")
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type, readonly
            )
            current_y += 5

        # Render category-specific fields
        current_y += 10
        current_y = self._render_category_specific_fields(
            x, current_y, width, height - (current_y - y)
        )

    def _render_field(
        self,
        x: int,
        y: int,
        width: int,
        field_name: str,
        label: str,
        value: Any,
        field_type: str = "str",
        readonly: bool = False,
    ) -> int:
        """Render a single editable field. Returns new Y position."""
        field_height = 30
        label_font = pygame.font.Font(None, 16)
        value_font = pygame.font.Font(None, 18)

        # Label
        label_surface = label_font.render(label, True, (180, 180, 200))
        self.screen.blit(label_surface, (x, y))

        # Value box
        value_y = y + 18
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        is_active = self.active_input_field == field_name
        box_color = (80, 80, 120) if is_active else (50, 50, 70) if not readonly else (40, 40, 50)

        pygame.draw.rect(
            self.screen,
            box_color,
            (x, value_y, width, field_height),
            border_radius=3,
        )

        # Value text
        display_value = str(value) if value is not None else ""
        value_surface = value_font.render(display_value, True, (255, 255, 255))
        self.screen.blit(value_surface, (x + 8, value_y + 6))

        # Click to edit (if not readonly)
        if not readonly:
            if (
                x <= mouse_pos[0] <= x + width
                and value_y <= mouse_pos[1] <= value_y + field_height
                and mouse_pressed
            ):
                self.active_input_field = field_name
                self.input_text = display_value

        return value_y + field_height

    def _render_category_specific_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render fields specific to the current category."""
        current_y = y
        entry = self.current_entry

        # Add category-specific fields based on entry type
        if isinstance(entry, Item):
            current_y = self._render_item_fields(x, current_y, width, height)
        elif isinstance(entry, Skill):
            current_y = self._render_skill_fields(x, current_y, width, height)
        elif isinstance(entry, Weapon):
            current_y = self._render_weapon_fields(x, current_y, width, height)
        elif isinstance(entry, Armor):
            current_y = self._render_armor_fields(x, current_y, width, height)
        elif isinstance(entry, Enemy):
            current_y = self._render_enemy_fields(x, current_y, width, height)
        elif isinstance(entry, State):
            current_y = self._render_state_fields(x, current_y, width, height)
        elif isinstance(entry, Actor):
            current_y = self._render_actor_fields(x, current_y, width, height)
        elif isinstance(entry, Class):
            current_y = self._render_class_fields(x, current_y, width, height)
        elif isinstance(entry, Animation):
            current_y = self._render_animation_fields(x, current_y, width, height)

        return current_y

    def _render_item_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Item-specific fields."""
        current_y = y
        item = self.current_entry

        fields = [
            ("price", "Price", item.price, "int"),
            ("consumable", "Consumable", item.consumable, "bool"),
            ("occasion", "Occasion", item.occasion, "int"),
            ("scope", "Scope", item.scope, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_skill_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Skill-specific fields."""
        current_y = y
        skill = self.current_entry

        fields = [
            ("mp_cost", "MP Cost", skill.mp_cost, "int"),
            ("tp_cost", "TP Cost", skill.tp_cost, "int"),
            ("occasion", "Occasion", skill.occasion, "int"),
            ("scope", "Scope", skill.scope, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_weapon_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Weapon-specific fields."""
        current_y = y
        weapon = self.current_entry

        fields = [
            ("price", "Price", weapon.price, "int"),
            ("animation_id", "Animation ID", weapon.animation_id, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_armor_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Armor-specific fields."""
        current_y = y
        armor = self.current_entry

        fields = [
            ("price", "Price", armor.price, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_enemy_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Enemy-specific fields."""
        current_y = y
        enemy = self.current_entry

        fields = [
            ("battler_name", "Battler Name", enemy.battler_name, "str"),
            ("exp", "EXP", enemy.exp, "int"),
            ("gold", "Gold", enemy.gold, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_state_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render State-specific fields."""
        current_y = y
        state = self.current_entry

        fields = [
            ("priority", "Priority", state.priority, "int"),
            ("min_turns", "Min Turns", state.min_turns, "int"),
            ("max_turns", "Max Turns", state.max_turns, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_actor_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Actor-specific fields."""
        current_y = y
        actor = self.current_entry

        fields = [
            ("nickname", "Nickname", actor.nickname, "str"),
            ("class_id", "Class ID", actor.class_id, "int"),
            ("initial_level", "Initial Level", actor.initial_level, "int"),
            ("max_level", "Max Level", actor.max_level, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    def _render_class_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Class-specific fields."""
        current_y = y
        # Classes have complex fields that would need more UI work
        font = pygame.font.Font(None, 16)
        msg = font.render("Advanced class editing coming soon", True, (150, 150, 150))
        self.screen.blit(msg, (x, current_y))
        return current_y + 20

    def _render_animation_fields(self, x: int, y: int, width: int, height: int) -> int:
        """Render Animation-specific fields."""
        current_y = y
        animation = self.current_entry

        fields = [
            ("animation1_name", "Animation 1", animation.animation1_name, "str"),
            ("animation2_name", "Animation 2", animation.animation2_name, "str"),
            ("position", "Position", animation.position, "int"),
            ("frame_max", "Frame Count", animation.frame_max, "int"),
        ]

        for field_name, label, value, field_type in fields:
            if current_y + 50 > y + height:
                break
            current_y = self._render_field(
                x, current_y, width, field_name, label, value, field_type
            )
            current_y += 5

        return current_y

    # =========================================================================
    # Event Handling
    # =========================================================================

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was consumed."""
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            # Handle text input
            if self.active_input_field:
                if event.key == pygame.K_RETURN:
                    self._apply_input()
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.active_input_field = None
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    return True
                else:
                    # Add character to input
                    if event.unicode and event.unicode.isprintable():
                        self.input_text += event.unicode
                        return True

        elif event.type == pygame.MOUSEWHEEL:
            # Handle scrolling
            mouse_pos = pygame.mouse.get_pos()
            # Determine which panel to scroll based on mouse position
            # This is simplified - you'd want proper bounds checking
            if event.y > 0:  # Scroll up
                if self.entry_list_scroll > 0:
                    self.entry_list_scroll -= 1
            else:  # Scroll down
                self.entry_list_scroll += 1
            return True

        return False

    def update(self, delta_time: float):
        """Update UI state."""
        if not self.visible:
            return
        # Nothing to update continuously for now

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_filtered_entries(self) -> List[DatabaseEntry]:
        """Get entries filtered by search query."""
        entries = self.db.read_all(self.current_category)

        if not self.search_query:
            return entries

        # Filter by search query
        filtered = []
        query_lower = self.search_query.lower()
        for entry in entries:
            if query_lower in entry.name.lower():
                filtered.append(entry)
            elif query_lower in str(entry.id):
                filtered.append(entry)
            elif hasattr(entry, "description") and query_lower in entry.description.lower():
                filtered.append(entry)

        return filtered

    def _create_new_entry(self):
        """Create a new entry in the current category."""
        try:
            # Get the entry type for this category
            entry_type = CATEGORY_TYPES[self.current_category]

            # Create a new entry with default values
            new_entry = entry_type(
                id=0,  # Will be auto-assigned
                name=f"New {self.current_category.capitalize()}",
                icon_index=0,
                description="",
                note="",
            )

            # Create in database
            created_entry = self.db.create(self.current_category, new_entry, auto_id=True)

            # Select the new entry
            self.current_entry = created_entry
            self.has_unsaved_changes = True

            print(f"✓ Created new {self.current_category} entry #{created_entry.id}")

        except Exception as e:
            print(f"✗ Failed to create entry: {e}")

    def _duplicate_entry(self):
        """Duplicate the current entry."""
        if not self.current_entry:
            return

        try:
            duplicated = self.db.duplicate(self.current_category, self.current_entry.id)
            self.current_entry = duplicated
            self.has_unsaved_changes = True
            print(f"✓ Duplicated entry #{duplicated.id}")
        except Exception as e:
            print(f"✗ Failed to duplicate entry: {e}")

    def _delete_entry(self):
        """Delete the current entry."""
        if not self.current_entry:
            return

        try:
            entry_id = self.current_entry.id
            self.db.delete(self.current_category, entry_id)
            self.current_entry = None
            self.has_unsaved_changes = True
            print(f"✓ Deleted entry #{entry_id}")
        except Exception as e:
            print(f"✗ Failed to delete entry: {e}")

    def _apply_input(self):
        """Apply the current input to the active field."""
        if not self.active_input_field or not self.current_entry:
            return

        field_name = self.active_input_field
        value = self.input_text

        try:
            # Get the current field value to determine type
            current_value = getattr(self.current_entry, field_name)

            # Convert input to appropriate type
            # Check bool before int (bool is subclass of int in Python)
            if isinstance(current_value, bool):
                value = value.lower() in ("true", "1", "yes")
            elif isinstance(current_value, int):
                value = int(value) if value else 0
            elif isinstance(current_value, float):
                value = float(value) if value else 0.0

            # Update the entry
            setattr(self.current_entry, field_name, value)

            # Update in database
            self.db.update(self.current_category, self.current_entry)
            self.has_unsaved_changes = True

            print(f"✓ Updated {field_name} = {value}")

        except Exception as e:
            print(f"✗ Failed to update {field_name}: {e}")

        finally:
            self.active_input_field = None
            self.input_text = ""

    def _save_database(self):
        """Save the database to file."""
        try:
            self.db.save_to_file(self.database_path)
            self.has_unsaved_changes = False
            print(f"✓ Database saved to {self.database_path}")
        except Exception as e:
            print(f"✗ Failed to save database: {e}")

    # =========================================================================
    # Public API
    # =========================================================================

    def toggle(self):
        """Toggle the database editor visibility."""
        self.visible = not self.visible
        if self.visible:
            # Reset state when opening
            self.entry_list_scroll = 0
            self.detail_scroll = 0
            self.active_input_field = None

    def get_current_entry(self) -> Optional[DatabaseEntry]:
        """Get the currently selected entry."""
        return self.current_entry

    def load_database(self, filepath: Path):
        """Load database from file."""
        try:
            self.db.load_from_file(filepath)
            self.database_path = filepath
            self.has_unsaved_changes = False
            print(f"✓ Database loaded from {filepath}")
        except Exception as e:
            print(f"✗ Failed to load database: {e}")
