"""
Effect Editor

Visual effect builder for damage, healing, and status effects.
Supports creating and editing Effect objects used in skills and items.
"""

from typing import List, Optional

import pygame

from neonworks.engine.data.database_schema import Effect, EffectTiming, EffectType


class EffectEditor:
    """
    Visual editor for creating and modifying effects.

    Supports all effect types:
    - HP/MP Damage and Recovery
    - State application/removal
    - Buffs and Debuffs
    - Special effects

    Features:
    - Type selector with visual icons
    - Value sliders with numeric input
    - Timing configuration
    - Success rate adjustment
    - Live preview of effect
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Current effect being edited
        self.effect: Optional[Effect] = None

        # UI state
        self.active_input_field: Optional[str] = None
        self.input_text = ""

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

        # Effect type categories for easier selection
        self.effect_categories = {
            "Damage/Heal": [
                EffectType.DAMAGE_HP,
                EffectType.DAMAGE_MP,
                EffectType.RECOVER_HP,
                EffectType.RECOVER_MP,
            ],
            "States": [
                EffectType.ADD_STATE,
                EffectType.REMOVE_STATE,
            ],
            "Buffs": [
                EffectType.ADD_BUFF,
                EffectType.ADD_DEBUFF,
                EffectType.REMOVE_BUFF,
                EffectType.REMOVE_DEBUFF,
            ],
            "Special": [
                EffectType.GROW,
                EffectType.LEARN_SKILL,
                EffectType.COMMON_EVENT,
                EffectType.SPECIAL,
            ],
        }

    def open(self, initial_effect: Optional[Effect] = None) -> None:
        """
        Open the effect editor.

        Args:
            initial_effect: Effect to edit, or None to create new
        """
        self.visible = True
        self.result = None
        self.active_input_field = None
        self.input_text = ""

        if initial_effect:
            self.effect = Effect(
                effect_type=initial_effect.effect_type,
                value1=initial_effect.value1,
                value2=initial_effect.value2,
                timing=initial_effect.timing,
                target_param=initial_effect.target_param,
                rate=initial_effect.rate,
            )
        else:
            self.effect = Effect()

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
            elif event.key == pygame.K_RETURN and self.active_input_field:
                self._apply_input()
                return True
            elif event.key == pygame.K_BACKSPACE and self.active_input_field:
                self.input_text = self.input_text[:-1]
                return True
            elif event.unicode and event.unicode.isprintable() and self.active_input_field:
                # Only allow numbers, dots, and minus for numeric fields
                if event.unicode in "0123456789.-":
                    self.input_text += event.unicode
                return True

        return True

    def render(self) -> Optional[Effect]:
        """
        Render the effect editor.

        Returns:
            Effect if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(900, screen_width - 100)
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

        # Effect type selector
        selector_y = dialog_y + 70
        self._render_type_selector(dialog_x + 20, selector_y, dialog_width - 40)

        # Effect parameters
        params_y = selector_y + 180
        self._render_parameters(dialog_x + 20, params_y, dialog_width - 40)

        # Preview
        preview_y = params_y + 280
        self._render_preview(dialog_x + 20, preview_y, dialog_width - 40)

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

        title_text = self.title_font.render("Effect Editor", True, (100, 200, 255))
        self.screen.blit(title_text, (x + 20, y + 12))

        # Help text
        help_text = self.small_font.render(
            "Create and configure skill/item effects",
            True,
            (150, 150, 150)
        )
        self.screen.blit(help_text, (x + width - 280, y + 18))

    def _render_type_selector(self, x: int, y: int, width: int):
        """Render effect type selector with categories."""
        # Section title
        title = self.font.render("Effect Type", True, (200, 200, 255))
        self.screen.blit(title, (x, y))

        current_y = y + 30
        button_width = 180
        button_height = 32
        button_spacing = 8
        buttons_per_row = (width - 100) // (button_width + button_spacing)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for category, effect_types in self.effect_categories.items():
            # Category label
            cat_label = self.small_font.render(category, True, (180, 180, 200))
            self.screen.blit(cat_label, (x, current_y))
            current_y += 22

            # Effect type buttons
            for i, eff_type in enumerate(effect_types):
                col = i % buttons_per_row
                row = i // buttons_per_row

                btn_x = x + col * (button_width + button_spacing)
                btn_y = current_y + row * (button_height + button_spacing)

                is_selected = self.effect.effect_type == eff_type
                is_hover = (
                    btn_x <= mouse_pos[0] <= btn_x + button_width
                    and btn_y <= mouse_pos[1] <= btn_y + button_height
                )

                # Button background
                if is_selected:
                    btn_color = (60, 120, 200)
                elif is_hover:
                    btn_color = (50, 70, 110)
                else:
                    btn_color = (40, 50, 80)

                pygame.draw.rect(
                    self.screen,
                    btn_color,
                    (btn_x, btn_y, button_width, button_height),
                    border_radius=4,
                )

                # Button text
                type_name = eff_type.value.replace("_", " ").title()
                btn_text = self.small_font.render(type_name, True, (255, 255, 255))
                text_rect = btn_text.get_rect(
                    center=(btn_x + button_width // 2, btn_y + button_height // 2)
                )
                self.screen.blit(btn_text, text_rect)

                # Handle click
                if is_hover and mouse_clicked:
                    self.effect.effect_type = eff_type

            # Calculate rows needed for this category
            rows_needed = (len(effect_types) + buttons_per_row - 1) // buttons_per_row
            current_y += rows_needed * (button_height + button_spacing) + 10

    def _render_parameters(self, x: int, y: int, width: int):
        """Render effect parameters (values, timing, rate)."""
        # Section title
        title = self.font.render("Parameters", True, (200, 200, 255))
        self.screen.blit(title, (x, y))

        current_y = y + 30

        # Value1 (base value or percentage)
        current_y = self._render_number_field(
            x, current_y, width // 2 - 10,
            "value1", "Base Value", self.effect.value1,
            help_text="Base damage/heal or percentage"
        )

        # Value2 (variance or additional value)
        current_y = self._render_number_field(
            x, current_y, width // 2 - 10,
            "value2", "Variance/Extra", self.effect.value2,
            help_text="Variance or additional modifier"
        )

        # Target param (for buffs, states, etc.)
        current_y = self._render_number_field(
            x, current_y, width // 2 - 10,
            "target_param", "Target Param ID", self.effect.target_param,
            help_text="State/stat ID for buffs/debuffs"
        )

        # Success rate slider
        current_y = self._render_rate_slider(x, current_y, width)

        # Timing selector
        current_y = self._render_timing_selector(x, current_y, width)

    def _render_number_field(
        self, x: int, y: int, width: int,
        field_name: str, label: str, value: float,
        help_text: str = ""
    ) -> int:
        """Render a number input field."""
        # Label
        label_surf = self.small_font.render(label, True, (180, 180, 200))
        self.screen.blit(label_surf, (x, y))

        if help_text:
            help_surf = self.small_font.render(f"({help_text})", True, (120, 120, 140))
            self.screen.blit(help_surf, (x + 150, y))

        # Input box
        input_y = y + 20
        input_height = 30
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        is_active = self.active_input_field == field_name
        box_color = (70, 80, 120) if is_active else (50, 50, 70)

        pygame.draw.rect(
            self.screen,
            box_color,
            (x, input_y, width, input_height),
            border_radius=3,
        )

        # Display value
        display_value = self.input_text if is_active else str(value)
        value_surf = self.font.render(display_value, True, (255, 255, 255))
        self.screen.blit(value_surf, (x + 8, input_y + 5))

        # Handle click
        if (
            x <= mouse_pos[0] <= x + width
            and input_y <= mouse_pos[1] <= input_y + input_height
            and mouse_clicked
        ):
            self.active_input_field = field_name
            self.input_text = str(value)

        return input_y + input_height + 15

    def _render_rate_slider(self, x: int, y: int, width: int) -> int:
        """Render success rate slider."""
        # Label
        label = self.small_font.render(
            f"Success Rate: {int(self.effect.rate * 100)}%",
            True,
            (180, 180, 200)
        )
        self.screen.blit(label, (x, y))

        # Slider
        slider_y = y + 25
        slider_width = width - 20
        slider_height = 20

        # Background
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (x, slider_y, slider_width, slider_height),
            border_radius=10,
        )

        # Fill (represents current rate)
        fill_width = int(slider_width * self.effect.rate)
        pygame.draw.rect(
            self.screen,
            (0, 180, 100),
            (x, slider_y, fill_width, slider_height),
            border_radius=10,
        )

        # Handle
        handle_x = x + fill_width
        handle_radius = 12
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (handle_x, slider_y + slider_height // 2),
            handle_radius,
        )

        # Handle mouse interaction
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if (
                x <= mouse_pos[0] <= x + slider_width
                and slider_y - 10 <= mouse_pos[1] <= slider_y + slider_height + 10
            ):
                # Update rate based on mouse position
                self.effect.rate = max(0.0, min(1.0, (mouse_pos[0] - x) / slider_width))

        return slider_y + slider_height + 20

    def _render_timing_selector(self, x: int, y: int, width: int) -> int:
        """Render timing selector buttons."""
        # Label
        label = self.small_font.render("Timing", True, (180, 180, 200))
        self.screen.blit(label, (x, y))

        button_y = y + 22
        button_width = 120
        button_height = 28
        button_spacing = 8

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        timings = [
            EffectTiming.IMMEDIATE,
            EffectTiming.TURN_START,
            EffectTiming.TURN_END,
            EffectTiming.ON_HIT,
        ]

        for i, timing in enumerate(timings):
            btn_x = x + i * (button_width + button_spacing)

            is_selected = self.effect.timing == timing
            is_hover = (
                btn_x <= mouse_pos[0] <= btn_x + button_width
                and button_y <= mouse_pos[1] <= button_y + button_height
            )

            # Button background
            if is_selected:
                btn_color = (80, 100, 180)
            elif is_hover:
                btn_color = (50, 70, 110)
            else:
                btn_color = (40, 50, 80)

            pygame.draw.rect(
                self.screen,
                btn_color,
                (btn_x, button_y, button_width, button_height),
                border_radius=4,
            )

            # Button text
            timing_name = timing.value.replace("_", " ").title()
            btn_text = self.small_font.render(timing_name, True, (255, 255, 255))
            text_rect = btn_text.get_rect(
                center=(btn_x + button_width // 2, button_y + button_height // 2)
            )
            self.screen.blit(btn_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked:
                self.effect.timing = timing

        return button_y + button_height + 20

    def _render_preview(self, x: int, y: int, width: int):
        """Render effect preview/description."""
        # Section title
        title = self.font.render("Preview", True, (200, 200, 255))
        self.screen.blit(title, (x, y))

        # Background box
        preview_y = y + 30
        preview_height = 80
        pygame.draw.rect(
            self.screen,
            (25, 25, 40),
            (x, preview_y, width, preview_height),
            border_radius=6,
        )

        # Generate preview text
        preview_text = self._generate_preview_text()

        # Render preview lines
        line_y = preview_y + 10
        for line in preview_text:
            line_surf = self.small_font.render(line, True, (220, 220, 240))
            self.screen.blit(line_surf, (x + 10, line_y))
            line_y += 22

    def _generate_preview_text(self) -> List[str]:
        """Generate human-readable preview of the effect."""
        effect_type = self.effect.effect_type.value.replace("_", " ").title()
        timing = self.effect.timing.value.replace("_", " ")
        rate = int(self.effect.rate * 100)

        lines = [
            f"Type: {effect_type}",
            f"Values: {self.effect.value1} / {self.effect.value2}",
            f"Success: {rate}% | Timing: {timing}",
        ]

        return lines

    def _render_bottom_buttons(self, x: int, y: int):
        """Render OK and Cancel buttons."""
        button_width = 100
        button_height = 40
        button_spacing = 10

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # OK button
        ok_hover = (
            x <= mouse_pos[0] <= x + button_width
            and y <= mouse_pos[1] <= y + button_height
        )
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
            self.result = self.effect

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

    def _apply_input(self):
        """Apply the current input to the active field."""
        if not self.active_input_field or not self.input_text:
            self.active_input_field = None
            return

        try:
            if self.active_input_field == "value1":
                self.effect.value1 = float(self.input_text)
            elif self.active_input_field == "value2":
                self.effect.value2 = float(self.input_text)
            elif self.active_input_field == "target_param":
                self.effect.target_param = int(float(self.input_text))
        except ValueError:
            pass  # Invalid input, ignore

        self.active_input_field = None
        self.input_text = ""

    def get_result(self) -> Optional[Effect]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
