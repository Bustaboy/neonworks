"""
Stat Editor

Stat distribution editor with interactive sliders and point allocation.
Used for character stats, equipment bonuses, and enemy parameters.
"""

from typing import Dict, List, Optional

import pygame


class StatEditor:
    """
    Interactive stat distribution editor with sliders.

    Features:
    - Visual sliders for each stat
    - Optional point pool system (total points to distribute)
    - Min/max constraints per stat
    - Preset distribution templates
    - Real-time total calculation

    Supported stat types:
    - RPG Stats: HP, MP, ATK, DEF, MAT, MDF, AGI, LUK
    - Custom stats (configurable)
    """

    # Default stat labels and ranges
    DEFAULT_STATS = {
        "HP": (1, 9999, 100),  # (min, max, default)
        "MP": (0, 9999, 0),
        "ATK": (1, 999, 10),
        "DEF": (1, 999, 10),
        "MAT": (1, 999, 10),
        "MDF": (1, 999, 10),
        "AGI": (1, 999, 10),
        "LUK": (1, 999, 10),
    }

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Current stat values
        self.stats: Dict[str, int] = {}

        # Stat configuration (min, max, default for each stat)
        self.stat_config: Dict[str, tuple] = {}

        # Point pool mode
        self.use_point_pool = False
        self.max_points = 100
        self.points_spent = 0

        # UI state
        self.active_slider: Optional[str] = None
        self.dragging = False

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 28)

        # Preset templates
        self.presets = {
            "Balanced": {
                "HP": 100,
                "MP": 50,
                "ATK": 15,
                "DEF": 15,
                "MAT": 15,
                "MDF": 15,
                "AGI": 15,
                "LUK": 10,
            },
            "Warrior": {
                "HP": 150,
                "MP": 20,
                "ATK": 25,
                "DEF": 20,
                "MAT": 5,
                "MDF": 10,
                "AGI": 12,
                "LUK": 8,
            },
            "Mage": {
                "HP": 80,
                "MP": 100,
                "ATK": 5,
                "DEF": 8,
                "MAT": 30,
                "MDF": 25,
                "AGI": 10,
                "LUK": 12,
            },
            "Tank": {
                "HP": 200,
                "MP": 30,
                "ATK": 12,
                "DEF": 30,
                "MAT": 5,
                "MDF": 20,
                "AGI": 8,
                "LUK": 5,
            },
            "Rogue": {
                "HP": 90,
                "MP": 40,
                "ATK": 20,
                "DEF": 10,
                "MAT": 8,
                "MDF": 8,
                "AGI": 30,
                "LUK": 25,
            },
        }

    def open(
        self,
        initial_stats: Optional[Dict[str, int]] = None,
        stat_config: Optional[Dict[str, tuple]] = None,
        use_point_pool: bool = False,
        max_points: int = 100,
    ) -> None:
        """
        Open the stat editor.

        Args:
            initial_stats: Initial stat values
            stat_config: Stat configuration {name: (min, max, default)}
            use_point_pool: Enable point pool mode
            max_points: Maximum total points to distribute
        """
        self.visible = True
        self.result = None
        self.active_slider = None
        self.dragging = False

        # Load config or use defaults
        self.stat_config = stat_config or self.DEFAULT_STATS.copy()

        # Initialize stats
        if initial_stats:
            self.stats = initial_stats.copy()
        else:
            # Use default values from config
            self.stats = {name: config[2] for name, config in self.stat_config.items()}

        # Point pool settings
        self.use_point_pool = use_point_pool
        self.max_points = max_points
        self._calculate_points_spent()

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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                self.active_slider = None

        return True

    def render(self) -> Optional[Dict[str, int]]:
        """
        Render the stat editor.

        Returns:
            Stat dictionary if dialog was closed with OK, None otherwise
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
        self._render_title_bar(dialog_x, dialog_y, dialog_width)

        # Point pool display (if enabled)
        pool_y = dialog_y + 70
        if self.use_point_pool:
            self._render_point_pool(dialog_x + 20, pool_y, dialog_width - 40)
            pool_y += 60

        # Stat sliders
        sliders_y = pool_y + (0 if not self.use_point_pool else 0)
        self._render_stat_sliders(dialog_x + 20, sliders_y, dialog_width - 40)

        # Preset buttons
        presets_y = sliders_y + (len(self.stat_config) * 50) + 20
        self._render_presets(dialog_x + 20, presets_y, dialog_width - 40)

        # Bottom buttons
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 60,
        )

        return None

    def _render_title_bar(self, x: int, y: int, width: int):
        """Render the title bar."""
        title_height = 50
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (x, y, width, title_height),
            border_radius=8,
        )

        title_text = self.title_font.render("Stat Distribution", True, (100, 200, 255))
        self.screen.blit(title_text, (x + 20, y + 12))

        # Help text
        help_text = self.small_font.render(
            "Adjust sliders to set stat values", True, (150, 150, 150)
        )
        self.screen.blit(help_text, (x + width - 250, y + 18))

    def _render_point_pool(self, x: int, y: int, width: int):
        """Render point pool display."""
        # Background
        pygame.draw.rect(
            self.screen,
            (25, 35, 50),
            (x, y, width, 50),
            border_radius=6,
        )

        # Points remaining
        points_remaining = self.max_points - self.points_spent
        color = (100, 255, 100) if points_remaining >= 0 else (255, 100, 100)

        label = self.large_font.render(
            f"Points: {self.points_spent} / {self.max_points}", True, color
        )
        self.screen.blit(label, (x + 20, y + 12))

        # Progress bar
        bar_x = x + width - 320
        bar_width = 300
        bar_height = 25
        bar_y = y + 12

        # Background bar
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=12,
        )

        # Fill bar
        fill_ratio = min(1.0, self.points_spent / self.max_points if self.max_points > 0 else 0)
        fill_width = int(bar_width * fill_ratio)
        fill_color = (0, 180, 100) if points_remaining >= 0 else (200, 50, 50)

        pygame.draw.rect(
            self.screen,
            fill_color,
            (bar_x, bar_y, fill_width, bar_height),
            border_radius=12,
        )

    def _render_stat_sliders(self, x: int, y: int, width: int):
        """Render stat sliders."""
        current_y = y
        slider_height = 45

        mouse_pos = pygame.mouse.get_pos()

        for stat_name, (min_val, max_val, default) in self.stat_config.items():
            current_value = self.stats.get(stat_name, default)

            # Stat label
            label_text = self.font.render(stat_name, True, (200, 200, 255))
            self.screen.blit(label_text, (x, current_y + 5))

            # Current value display
            value_text = self.large_font.render(str(current_value), True, (255, 255, 255))
            value_rect = value_text.get_rect()
            value_x = x + 80
            self.screen.blit(value_text, (value_x, current_y))

            # Slider
            slider_x = x + 140
            slider_width = width - 150
            slider_y = current_y + 10
            slider_bar_height = 24

            # Render slider
            self._render_slider(
                slider_x,
                slider_y,
                slider_width,
                slider_bar_height,
                stat_name,
                current_value,
                min_val,
                max_val,
                mouse_pos,
            )

            current_y += slider_height

    def _render_slider(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        stat_name: str,
        value: int,
        min_val: int,
        max_val: int,
        mouse_pos: tuple,
    ):
        """Render a single slider."""
        # Background track
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (x, y, width, height),
            border_radius=12,
        )

        # Value fill
        value_ratio = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
        fill_width = int(width * value_ratio)

        pygame.draw.rect(
            self.screen,
            (60, 120, 200),
            (x, y, fill_width, height),
            border_radius=12,
        )

        # Handle
        handle_x = x + fill_width
        handle_radius = 14
        handle_y = y + height // 2

        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (handle_x, handle_y),
            handle_radius,
        )

        # Handle interaction
        if self.dragging or (
            x <= mouse_pos[0] <= x + width and y - 10 <= mouse_pos[1] <= y + height + 10
        ):
            # Update value based on mouse position if dragging
            if self.dragging and pygame.mouse.get_pressed()[0]:
                self.active_slider = stat_name
                new_ratio = max(0.0, min(1.0, (mouse_pos[0] - x) / width))
                new_value = int(min_val + (max_val - min_val) * new_ratio)

                # Check point pool constraints
                if self.use_point_pool:
                    old_value = self.stats.get(stat_name, 0)
                    delta = new_value - old_value
                    new_total = self.points_spent + delta

                    if new_total <= self.max_points:
                        self.stats[stat_name] = new_value
                        self._calculate_points_spent()
                else:
                    self.stats[stat_name] = new_value

    def _render_presets(self, x: int, y: int, width: int):
        """Render preset template buttons."""
        # Section title
        title = self.font.render("Presets", True, (200, 200, 255))
        self.screen.blit(title, (x, y))

        button_y = y + 30
        button_width = 110
        button_height = 32
        button_spacing = 10

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, (preset_name, preset_stats) in enumerate(self.presets.items()):
            btn_x = x + i * (button_width + button_spacing)

            is_hover = (
                btn_x <= mouse_pos[0] <= btn_x + button_width
                and button_y <= mouse_pos[1] <= button_y + button_height
            )

            btn_color = (60, 100, 160) if is_hover else (40, 60, 100)

            pygame.draw.rect(
                self.screen,
                btn_color,
                (btn_x, button_y, button_width, button_height),
                border_radius=4,
            )

            # Button text
            btn_text = self.small_font.render(preset_name, True, (255, 255, 255))
            text_rect = btn_text.get_rect(
                center=(btn_x + button_width // 2, button_y + button_height // 2)
            )
            self.screen.blit(btn_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked:
                self._apply_preset(preset_stats)

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
            self.visible = False
            self.result = self.stats.copy()

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

    def _apply_preset(self, preset_stats: Dict[str, int]):
        """Apply a preset stat distribution."""
        for stat_name, value in preset_stats.items():
            if stat_name in self.stats:
                # Clamp to min/max
                min_val, max_val, _ = self.stat_config.get(stat_name, (0, 9999, 0))
                self.stats[stat_name] = max(min_val, min(max_val, value))

        self._calculate_points_spent()

    def _calculate_points_spent(self):
        """Calculate total points spent."""
        self.points_spent = sum(self.stats.values())

    def get_result(self) -> Optional[Dict[str, int]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
