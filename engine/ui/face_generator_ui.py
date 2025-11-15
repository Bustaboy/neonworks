"""
Face Generator UI - Visual Face Creator

Provides a complete visual interface for creating custom face sprites with:
- Component-based facial features (eyes, nose, mouth, etc.)
- Expression selector with real-time preview
- Color synchronization with character bodies
- Multi-expression preview panel
- Export to 96x96, 128x128, or 256x256
- Batch export all expressions
- Integration with Character Generator
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from neonworks.engine.tools.face_generator import (
    ColorTint,
    Expression,
    FaceGenerator,
    FaceLayer,
    FaceLayerType,
    FacePreset,
)


class FaceGeneratorUI:
    """
    Visual face generator with expression support.

    Layout:
    - Left Panel (200px): Component category tabs
    - Center Panel (500px): Component thumbnail grid
    - Right Panel (600px): Expression preview grid (all expressions shown)
    - Top Bar: Expression selector
    - Bottom: Color sync, export options, save/load
    """

    def __init__(self, screen: pygame.Surface, character_generator_ui=None):
        self.screen = screen
        self.visible = False
        self.character_generator_ui = character_generator_ui

        # Face generator instance
        self.generator = FaceGenerator(default_size=128)

        # Load component library
        self._load_components()

        # Current face preset
        self.current_preset = FacePreset(name="New Face")

        # UI State
        self.selected_category = FaceLayerType.BASE
        self.selected_component_id: Optional[str] = None
        self.selected_expression = Expression.NEUTRAL

        # Scrolling
        self.component_scroll = 0

        # Color picker state
        self.show_color_picker = False
        self.editing_color_layer: Optional[FaceLayerType] = None
        self.color_sliders = {"r": 255, "g": 255, "b": 255, "a": 255}

        # AI description input state
        self.ai_description = ""
        self.ai_input_active = False
        self.ai_cursor_visible = True
        self.ai_cursor_timer = 0.0

        # Export size selection
        self.export_size = 128  # Default
        self.export_sizes = [96, 128, 256]

        # Expression previews (cached)
        self.expression_previews: Dict[Expression, pygame.Surface] = {}
        self._regenerate_all_previews()

        # Fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 16)

    def _load_components(self):
        """Load face component library from assets."""
        component_path = Path("assets/face_components")
        if component_path.exists():
            try:
                self.generator.load_component_library(component_path)
                print(f"✓ Loaded face components from {component_path}")
            except Exception as e:
                print(f"⚠ Failed to load face components: {e}")
        else:
            print(f"ℹ Face component library not found at {component_path}")

    def toggle(self):
        """Toggle face generator visibility."""
        self.visible = not self.visible
        if self.visible:
            self._regenerate_all_previews()

    def update(self, delta_time: float):
        """Update UI state."""
        if not self.visible:
            return

        # Update cursor blink for text input
        if self.ai_input_active:
            self.ai_cursor_timer += delta_time
            if self.ai_cursor_timer >= 0.5:  # Blink every 0.5 seconds
                self.ai_cursor_timer = 0.0
                self.ai_cursor_visible = not self.ai_cursor_visible

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.ai_input_active:
                    self.ai_input_active = False
                    return True
                self.visible = False
                return True

            # Handle text input when AI input is active
            if self.ai_input_active:
                if event.key == pygame.K_RETURN:
                    # Generate face from description
                    if self.ai_description.strip():
                        self._generate_from_ai_description()
                    self.ai_input_active = False
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.ai_description = self.ai_description[:-1]
                    return True
                elif event.unicode and len(self.ai_description) < 200:  # Limit length
                    # Only allow printable characters
                    if event.unicode.isprintable():
                        self.ai_description += event.unicode
                        return True
                return True  # Consume all key events when input is active

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_click(mouse_pos)
            elif event.button == 4:  # Scroll up
                self._handle_scroll(-1, mouse_pos)
                return True
            elif event.button == 5:  # Scroll down
                self._handle_scroll(1, mouse_pos)
                return True

        return False

    def render(self):
        """Render the face generator UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Main panel dimensions
        panel_width = 1400
        panel_height = 900
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

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

        # Title
        title_surface = self.title_font.render("Face Generator", True, (255, 150, 100))
        title_x = panel_x + (panel_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, panel_y + 15))

        # Close button
        close_x = panel_x + panel_width - 50
        close_y = panel_y + 10
        self._render_button("×", close_x, close_y, 35, 35, (150, 0, 0), id_="close")

        # AI Description Input (below title)
        ai_input_y = panel_y + 50
        self._render_ai_input(panel_x + 10, ai_input_y, panel_width - 20)

        # Expression selector (below AI input)
        expr_bar_y = panel_y + 105
        self._render_expression_selector(panel_x + 10, expr_bar_y, panel_width - 20, 50)

        # Content area
        content_y = panel_y + 170
        content_height = panel_height - 270

        # Layout sections
        left_panel_x = panel_x + 10
        left_panel_width = 200

        center_panel_x = left_panel_x + left_panel_width + 10
        center_panel_width = 500

        right_panel_x = center_panel_x + center_panel_width + 10
        right_panel_width = 660

        # Render main sections
        self._render_category_tabs(left_panel_x, content_y, left_panel_width, content_height)
        self._render_component_grid(center_panel_x, content_y, center_panel_width, content_height)
        self._render_expression_grid(right_panel_x, content_y, right_panel_width, content_height)

        # Bottom controls
        bottom_y = panel_y + panel_height - 90
        self._render_bottom_controls(panel_x, bottom_y, panel_width, 80)

        # Color picker overlay (if active)
        if self.show_color_picker:
            self._render_color_picker(screen_width // 2 - 200, screen_height // 2 - 250, 400, 500)

    def _render_expression_selector(self, x: int, y: int, width: int, height: int):
        """Render expression selector bar."""
        # Background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Label
        label = self.font.render("Expression:", True, (200, 200, 200))
        self.screen.blit(label, (x + 15, y + 15))

        # Expression buttons
        expressions = [
            Expression.NEUTRAL,
            Expression.HAPPY,
            Expression.SAD,
            Expression.ANGRY,
            Expression.SURPRISED,
            Expression.SCARED,
            Expression.DISGUSTED,
            Expression.CONFUSED,
            Expression.WINK,
            Expression.EMBARRASSED,
        ]

        button_x = x + 140
        button_width = 110
        button_height = 30
        button_spacing = 8

        mouse_pos = pygame.mouse.get_pos()

        for expr in expressions:
            if button_x + button_width > x + width - 10:
                break  # No more space

            is_selected = expr == self.selected_expression
            color = (100, 150, 200) if is_selected else (50, 50, 70)

            # Check hover
            is_hovered = (
                button_x <= mouse_pos[0] <= button_x + button_width
                and y + 10 <= mouse_pos[1] <= y + 10 + button_height
            )
            if is_hovered and not is_selected:
                color = (70, 70, 100)

            # Button
            pygame.draw.rect(
                self.screen, color, (button_x, y + 10, button_width, button_height), border_radius=3
            )

            # Label
            expr_label = self.small_font.render(expr.value.capitalize(), True, (255, 255, 255))
            label_x = button_x + (button_width - expr_label.get_width()) // 2
            label_y = y + 10 + (button_height - expr_label.get_height()) // 2
            self.screen.blit(expr_label, (label_x, label_y))

            # Store rect
            setattr(
                self,
                f"_expr_btn_{expr.name}",
                pygame.Rect(button_x, y + 10, button_width, button_height),
            )

            button_x += button_width + button_spacing

    def _render_ai_input(self, x: int, y: int, width: int):
        """Render AI description input field."""
        input_height = 45
        button_width = 180

        # Input field background
        input_bg_color = (60, 100, 140) if self.ai_input_active else (40, 40, 60)
        pygame.draw.rect(
            self.screen,
            input_bg_color,
            (x, y, width - button_width - 10, input_height),
            border_radius=4,
        )
        pygame.draw.rect(
            self.screen,
            (100, 100, 120),
            (x, y, width - button_width - 10, input_height),
            2,
            border_radius=4,
        )

        # Placeholder or text
        text_x = x + 15
        text_y = y + (input_height - 20) // 2

        if self.ai_description:
            # Display current text
            display_text = self.ai_description
            if len(display_text) > 80:
                display_text = display_text[:80] + "..."

            text_surface = self.font.render(display_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (text_x, text_y))

            # Cursor
            if self.ai_input_active and self.ai_cursor_visible:
                cursor_x = text_x + text_surface.get_width() + 2
                pygame.draw.rect(self.screen, (255, 255, 255), (cursor_x, text_y, 2, 20))
        else:
            # Placeholder text
            placeholder = "🤖 Describe the face... (e.g., 'A happy young woman with blue eyes and rosy cheeks')"
            placeholder_color = (120, 120, 140) if not self.ai_input_active else (150, 150, 170)
            text_surface = self.small_font.render(placeholder, True, placeholder_color)
            self.screen.blit(text_surface, (text_x, text_y + 5))

            # Cursor at start
            if self.ai_input_active and self.ai_cursor_visible:
                pygame.draw.rect(self.screen, (255, 255, 255), (text_x, text_y, 2, 20))

        # Generate button
        button_x = x + width - button_width
        button_color = (0, 150, 200) if self.ai_description.strip() else (60, 60, 80)
        self._render_button(
            "Generate from AI ✨",
            button_x,
            y,
            button_width,
            input_height,
            button_color,
            id_="generate_ai",
        )

        # Store input field rect for click detection
        setattr(self, "_ai_input_rect", pygame.Rect(x, y, width - button_width - 10, input_height))

    def _render_category_tabs(self, x: int, y: int, width: int, height: int):
        """Render left panel with component category tabs."""
        # Panel background
        pygame.draw.rect(self.screen, (25, 25, 40), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Title
        label = self.font.render("Features", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Category buttons
        button_y = y + 45
        button_height = 35
        button_spacing = 3

        categories = [
            FaceLayerType.BASE,
            FaceLayerType.EYES,
            FaceLayerType.EYEBROWS,
            FaceLayerType.NOSE,
            FaceLayerType.MOUTH,
            FaceLayerType.BLUSH,
            FaceLayerType.FACIAL_HAIR,
            FaceLayerType.GLASSES,
            FaceLayerType.FACE_PAINT,
            FaceLayerType.ACCESSORY,
            FaceLayerType.EFFECT,
        ]

        mouse_pos = pygame.mouse.get_pos()

        for category in categories:
            if button_y + button_height > y + height - 10:
                break

            is_selected = category == self.selected_category
            color = (80, 120, 180) if is_selected else (40, 40, 60)

            # Check hover
            is_hovered = (
                x + 5 <= mouse_pos[0] <= x + width - 5
                and button_y <= mouse_pos[1] <= button_y + button_height
            )
            if is_hovered and not is_selected:
                color = (60, 60, 90)

            # Button
            pygame.draw.rect(
                self.screen, color, (x + 5, button_y, width - 10, button_height), border_radius=3
            )

            # Label
            category_name = category.name.replace("_", " ").title()
            label = self.small_font.render(category_name, True, (255, 255, 255))
            self.screen.blit(label, (x + 15, button_y + 10))

            # Store button rect
            setattr(
                self,
                f"_cat_btn_{category.name}",
                pygame.Rect(x + 5, button_y, width - 10, button_height),
            )

            button_y += button_height + button_spacing

    def _render_component_grid(self, x: int, y: int, width: int, height: int):
        """Render center panel with component thumbnail grid."""
        # Panel background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Title
        category_name = self.selected_category.name.replace("_", " ").title()
        label = self.font.render(f"Components: {category_name}", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Get available components
        components = self.generator.list_components(self.selected_category)

        if not components:
            no_comp_label = self.font.render("No components available", True, (150, 150, 150))
            label_x = x + (width - no_comp_label.get_width()) // 2
            label_y = y + height // 2
            self.screen.blit(no_comp_label, (label_x, label_y))
            return

        # Grid layout
        grid_start_y = y + 50
        grid_height = height - 60
        thumbnail_size = 80
        padding = 10
        columns = (width - 20) // (thumbnail_size + padding)

        current_x = x + 10
        current_y = grid_start_y - self.component_scroll
        col = 0
        row = 0

        mouse_pos = pygame.mouse.get_pos()

        for comp_id, component in components.items():
            # Skip if scrolled out of view
            if current_y + thumbnail_size < grid_start_y:
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
                    current_x = x + 10
                    current_y = (
                        grid_start_y + row * (thumbnail_size + padding) - self.component_scroll
                    )
                else:
                    current_x += thumbnail_size + padding
                continue

            if current_y > y + height:
                break

            # Check if selected
            is_selected = comp_id == self.selected_component_id

            # Check hover
            is_hovered = (
                current_x <= mouse_pos[0] <= current_x + thumbnail_size
                and current_y <= mouse_pos[1] <= current_y + thumbnail_size
                and grid_start_y <= mouse_pos[1] <= y + height
            )

            # Thumbnail background
            bg_color = (
                (120, 160, 220) if is_selected else (90, 130, 170) if is_hovered else (50, 50, 70)
            )
            pygame.draw.rect(
                self.screen,
                bg_color,
                (current_x, current_y, thumbnail_size, thumbnail_size),
                border_radius=4,
            )

            # Render component preview
            try:
                # Get neutral expression for preview
                expr_surface = component.get_expression(Expression.NEUTRAL)
                # Scale to fit thumbnail
                scale_size = thumbnail_size - 8
                scaled = pygame.transform.scale(expr_surface, (scale_size, scale_size))

                # Center in thumbnail
                thumb_x = current_x + (thumbnail_size - scale_size) // 2
                thumb_y = current_y + (thumbnail_size - scale_size) // 2
                self.screen.blit(scaled, (thumb_x, thumb_y))
            except Exception:
                # Placeholder if rendering fails
                pygame.draw.rect(
                    self.screen,
                    (100, 100, 120),
                    (current_x + 4, current_y + 4, thumbnail_size - 8, thumbnail_size - 8),
                )

            # Store rect for click detection
            setattr(
                self,
                f"_comp_btn_{comp_id}",
                pygame.Rect(current_x, current_y, thumbnail_size, thumbnail_size),
            )

            # Next position
            col += 1
            if col >= columns:
                col = 0
                row += 1
                current_x = x + 10
                current_y = grid_start_y + row * (thumbnail_size + padding) - self.component_scroll
            else:
                current_x += thumbnail_size + padding

    def _render_expression_grid(self, x: int, y: int, width: int, height: int):
        """Render right panel with all expression previews."""
        # Panel background
        pygame.draw.rect(self.screen, (25, 25, 40), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Title
        label = self.font.render("All Expressions Preview", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Grid layout for expressions
        preview_size = 120
        padding = 15
        columns = 5

        grid_start_x = x + 15
        grid_start_y = y + 45

        expressions = [
            Expression.NEUTRAL,
            Expression.HAPPY,
            Expression.SAD,
            Expression.ANGRY,
            Expression.SURPRISED,
            Expression.SCARED,
            Expression.DISGUSTED,
            Expression.CONFUSED,
            Expression.WINK,
            Expression.EMBARRASSED,
        ]

        for idx, expr in enumerate(expressions):
            row = idx // columns
            col = idx % columns

            preview_x = grid_start_x + col * (preview_size + padding)
            preview_y = grid_start_y + row * (preview_size + padding)

            # Don't render if out of bounds
            if preview_y + preview_size > y + height - 10:
                break

            # Background
            is_selected = expr == self.selected_expression
            bg_color = (60, 100, 140) if is_selected else (40, 40, 60)
            pygame.draw.rect(
                self.screen,
                bg_color,
                (preview_x, preview_y, preview_size, preview_size),
                border_radius=4,
            )

            # Render preview
            if expr in self.expression_previews:
                preview = self.expression_previews[expr]
                # Scale to fit
                scaled = pygame.transform.scale(preview, (preview_size - 10, preview_size - 10))
                self.screen.blit(scaled, (preview_x + 5, preview_y + 5))

            # Expression label
            expr_name = expr.value.capitalize()
            name_label = self.small_font.render(expr_name, True, (220, 220, 220))
            name_x = preview_x + (preview_size - name_label.get_width()) // 2
            name_y = preview_y + preview_size + 3
            if name_y < y + height:
                self.screen.blit(name_label, (name_x, name_y))

    def _render_bottom_controls(self, x: int, y: int, width: int, height: int):
        """Render bottom control buttons."""
        # Background
        pygame.draw.rect(
            self.screen, (30, 30, 45), (x + 10, y, width - 20, height), border_radius=4
        )
        pygame.draw.rect(
            self.screen, (60, 60, 80), (x + 10, y, width - 20, height), 1, border_radius=4
        )

        button_width = 140
        button_height = 35
        button_y = y + 15
        button_spacing = 12

        # Top row buttons
        top_buttons = [
            ("Add Component", (0, 120, 200), "add_component"),
            ("Color Tint", (120, 80, 200), "color_tint"),
            ("Randomize", (200, 120, 0), "randomize"),
            ("Clear All", (150, 0, 0), "clear_all"),
            ("Sync Colors", (0, 150, 150), "sync_colors"),
        ]

        button_x = x + 20
        for label, color, btn_id in top_buttons:
            self._render_button(
                label, button_x, button_y, button_width, button_height, color, id_=btn_id
            )
            button_x += button_width + button_spacing

        # Bottom row buttons
        bottom_y = button_y + button_height + 8
        bottom_buttons = [
            ("Save Preset", (0, 150, 0), "save_preset"),
            ("Load Preset", (0, 100, 150), "load_preset"),
        ]

        button_x = x + 20
        for label, color, btn_id in bottom_buttons:
            self._render_button(
                label, button_x, bottom_y, button_width, button_height, color, id_=btn_id
            )
            button_x += button_width + button_spacing

        # Export size selector
        size_label = self.small_font.render("Export Size:", True, (200, 200, 200))
        self.screen.blit(size_label, (button_x, bottom_y + 5))
        button_x += 95

        for size in self.export_sizes:
            is_selected = size == self.export_size
            color = (80, 120, 180) if is_selected else (50, 50, 70)
            size_btn_width = 60

            self._render_button(
                f"{size}x{size}",
                button_x,
                bottom_y,
                size_btn_width,
                button_height,
                color,
                id_=f"size_{size}",
            )
            button_x += size_btn_width + 5

        # Export buttons
        button_x += 15
        export_buttons = [
            ("Export Single", (180, 100, 180), "export_single"),
            ("Export All", (200, 100, 200), "export_all"),
        ]

        for label, color, btn_id in export_buttons:
            self._render_button(
                label, button_x, bottom_y, button_width, button_height, color, id_=btn_id
            )
            button_x += button_width + button_spacing

    def _render_button(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        id_: str = "",
    ) -> bool:
        """Render a button and return True if hovered."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        # Adjust color on hover
        if is_hovered:
            color = tuple(min(c + 30, 255) for c in color)

        # Button background
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, width, height), 1, border_radius=4)

        # Button text
        font = self.small_font if width < 100 else self.font
        text_surface = font.render(text, True, (255, 255, 255))
        text_x = x + (width - text_surface.get_width()) // 2
        text_y = y + (height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))

        # Store rect for click detection
        if id_:
            setattr(self, f"_btn_{id_}", pygame.Rect(x, y, width, height))

        return is_hovered

    def _render_color_picker(self, x: int, y: int, width: int, height: int):
        """Render color picker overlay."""
        # Background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, width, height), 2, border_radius=8)

        # Title
        title = self.font.render("Color Tint", True, (200, 200, 200))
        self.screen.blit(title, (x + 20, y + 20))

        # Close button
        self._render_button("×", x + width - 50, y + 15, 35, 35, (150, 0, 0), id_="close_picker")

        # Color sliders
        slider_y = y + 70
        slider_height = 30
        slider_spacing = 50

        for channel in ["r", "g", "b", "a"]:
            label_color = {
                "r": (255, 100, 100),
                "g": (100, 255, 100),
                "b": (100, 100, 255),
                "a": (200, 200, 200),
            }[channel]

            label = self.font.render(channel.upper(), True, label_color)
            self.screen.blit(label, (x + 20, slider_y))

            # Slider track
            track_x = x + 60
            track_width = width - 100
            pygame.draw.rect(
                self.screen,
                (50, 50, 70),
                (track_x, slider_y, track_width, slider_height),
                border_radius=3,
            )

            # Slider fill
            fill_width = int((self.color_sliders[channel] / 255) * track_width)
            pygame.draw.rect(
                self.screen,
                label_color,
                (track_x, slider_y, fill_width, slider_height),
                border_radius=3,
            )

            # Value label
            value_label = self.font.render(str(self.color_sliders[channel]), True, (255, 255, 255))
            self.screen.blit(value_label, (x + width - 70, slider_y + 5))

            # Store rect for interaction
            setattr(
                self,
                f"_slider_{channel}",
                pygame.Rect(track_x, slider_y, track_width, slider_height),
            )

            slider_y += slider_spacing

        # Color preview
        preview_y = slider_y + 20
        preview_size = 100
        preview_x = x + (width - preview_size) // 2

        preview_color = (
            self.color_sliders["r"],
            self.color_sliders["g"],
            self.color_sliders["b"],
            self.color_sliders["a"],
        )
        preview_surface = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
        preview_surface.fill(preview_color)
        self.screen.blit(preview_surface, (preview_x, preview_y))

        # Apply button
        apply_y = preview_y + preview_size + 30
        self._render_button(
            "Apply", x + width // 2 - 60, apply_y, 120, 40, (0, 150, 0), id_="apply_color"
        )

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click events."""
        # AI input field click
        if hasattr(self, "_ai_input_rect"):
            rect = getattr(self, "_ai_input_rect")
            if rect.collidepoint(mouse_pos):
                self.ai_input_active = True
                return True

        # Generate from AI button
        if hasattr(self, "_btn_generate_ai"):
            rect = getattr(self, "_btn_generate_ai")
            if rect.collidepoint(mouse_pos) and self.ai_description.strip():
                self._generate_from_ai_description()
                return True

        # Close button
        if hasattr(self, "_btn_close"):
            if getattr(self, "_btn_close").collidepoint(mouse_pos):
                self.visible = False
                return True

        # Expression selector
        for expr in Expression:
            btn_attr = f"_expr_btn_{expr.name}"
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    self.selected_expression = expr
                    return True

        # Category buttons
        for category in FaceLayerType:
            btn_attr = f"_cat_btn_{category.name}"
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    self.selected_category = category
                    self.component_scroll = 0
                    return True

        # Component thumbnails
        components = self.generator.list_components(self.selected_category)
        for comp_id in components.keys():
            btn_attr = f"_comp_btn_{comp_id}"
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    self.selected_component_id = comp_id
                    return True

        # Bottom control buttons
        if hasattr(self, "_btn_add_component"):
            if getattr(self, "_btn_add_component").collidepoint(mouse_pos):
                self._add_component_to_face()
                return True

        if hasattr(self, "_btn_color_tint"):
            if getattr(self, "_btn_color_tint").collidepoint(mouse_pos):
                self.show_color_picker = True
                return True

        if hasattr(self, "_btn_randomize"):
            if getattr(self, "_btn_randomize").collidepoint(mouse_pos):
                self._randomize_face()
                return True

        if hasattr(self, "_btn_clear_all"):
            if getattr(self, "_btn_clear_all").collidepoint(mouse_pos):
                self.current_preset = FacePreset(name="New Face")
                self._regenerate_all_previews()
                return True

        if hasattr(self, "_btn_sync_colors"):
            if getattr(self, "_btn_sync_colors").collidepoint(mouse_pos):
                self._sync_colors_from_character()
                return True

        if hasattr(self, "_btn_save_preset"):
            if getattr(self, "_btn_save_preset").collidepoint(mouse_pos):
                self._save_preset()
                return True

        if hasattr(self, "_btn_load_preset"):
            if getattr(self, "_btn_load_preset").collidepoint(mouse_pos):
                self._load_preset()
                return True

        # Export size buttons
        for size in self.export_sizes:
            btn_attr = f"_btn_size_{size}"
            if hasattr(self, btn_attr):
                if getattr(self, btn_attr).collidepoint(mouse_pos):
                    self.export_size = size
                    return True

        if hasattr(self, "_btn_export_single"):
            if getattr(self, "_btn_export_single").collidepoint(mouse_pos):
                self._export_single_expression()
                return True

        if hasattr(self, "_btn_export_all"):
            if getattr(self, "_btn_export_all").collidepoint(mouse_pos):
                self._export_all_expressions()
                return True

        # Color picker buttons
        if self.show_color_picker:
            if hasattr(self, "_btn_close_picker"):
                if getattr(self, "_btn_close_picker").collidepoint(mouse_pos):
                    self.show_color_picker = False
                    return True

            if hasattr(self, "_btn_apply_color"):
                if getattr(self, "_btn_apply_color").collidepoint(mouse_pos):
                    self._apply_color_tint()
                    return True

            # Check slider clicks
            for channel in ["r", "g", "b", "a"]:
                slider_attr = f"_slider_{channel}"
                if hasattr(self, slider_attr):
                    rect = getattr(self, slider_attr)
                    if rect.collidepoint(mouse_pos):
                        normalized = (mouse_pos[0] - rect.x) / rect.width
                        normalized = max(0.0, min(1.0, normalized))
                        self.color_sliders[channel] = int(normalized * 255)
                        return True

        return False

    def _handle_scroll(self, direction: int, mouse_pos: Tuple[int, int]):
        """Handle scroll wheel."""
        self.component_scroll += direction * 30
        self.component_scroll = max(0, self.component_scroll)

    def _add_component_to_face(self):
        """Add selected component to face."""
        if not self.selected_component_id:
            print("⚠ No component selected")
            return

        layer = FaceLayer(
            layer_type=self.selected_category,
            component_id=self.selected_component_id,
            enabled=True,
        )

        self.current_preset.add_layer(layer)
        self._regenerate_all_previews()
        print(f"✓ Added {self.selected_component_id} to face")

    def _randomize_face(self):
        """Generate a random face."""
        try:
            self.current_preset = self.generator.randomize_face()
            self._regenerate_all_previews()
            print("✓ Generated random face")
        except Exception as e:
            print(f"⚠ Failed to randomize: {e}")

    def _generate_from_ai_description(self):
        """Generate face from AI description."""
        if not self.ai_description.strip():
            return

        try:
            print(f"🤖 Generating face from: '{self.ai_description}'")

            # Use the face generator's AI-friendly method
            self.current_preset = self.generator.generate_from_description(
                self.ai_description, name="AI Generated Face"
            )

            # Auto-set expression if detected
            if "detected_expression" in self.current_preset.metadata:
                detected_expr_name = self.current_preset.metadata["detected_expression"]
                try:
                    self.selected_expression = Expression(detected_expr_name)
                    print(f"✓ Auto-selected expression: {detected_expr_name}")
                except ValueError:
                    pass  # Keep current expression if invalid

            self._regenerate_all_previews()
            print("✓ AI face generation complete!")

            # Clear the input after successful generation
            self.ai_description = ""
            self.ai_input_active = False

        except Exception as e:
            print(f"⚠ Failed to generate from AI: {e}")
            print(f"   Description was: '{self.ai_description}'")

    def _apply_color_tint(self):
        """Apply color tint to selected layer."""
        if not self.current_preset.layers:
            print("⚠ No layers to tint")
            return

        layer = self.current_preset.layers[-1]
        layer.tint = ColorTint(
            r=self.color_sliders["r"],
            g=self.color_sliders["g"],
            b=self.color_sliders["b"],
            a=self.color_sliders["a"],
        )

        self._regenerate_all_previews()
        self.show_color_picker = False
        print(f"✓ Applied color tint to {layer.layer_type.name}")

    def _sync_colors_from_character(self):
        """Sync colors from character generator if available."""
        if not self.character_generator_ui:
            print("⚠ Character generator not available")
            return

        try:
            # Extract colors from character preset
            char_preset = self.character_generator_ui.current_preset
            character_colors = {}

            # Map character layers to face colors
            for layer in char_preset.layers:
                if layer.layer_type.name == "BODY" and layer.tint:
                    character_colors["skin"] = layer.tint
                elif layer.layer_type.name in ["HAIR_FRONT", "HAIR_BACK"] and layer.tint:
                    character_colors["hair"] = layer.tint

            # Sync to face
            self.generator.sync_colors_from_character(self.current_preset, character_colors)
            self._regenerate_all_previews()
            print("✓ Synced colors from character")
        except Exception as e:
            print(f"⚠ Failed to sync colors: {e}")

    def _save_preset(self):
        """Save current preset to file."""
        try:
            preset_dir = Path("presets/faces")
            preset_dir.mkdir(parents=True, exist_ok=True)

            preset_path = preset_dir / f"{self.current_preset.name}.json"
            self.generator.save_preset(self.current_preset, str(preset_path))
            print(f"✓ Saved preset to {preset_path}")
        except Exception as e:
            print(f"⚠ Failed to save preset: {e}")

    def _load_preset(self):
        """Load preset from file."""
        try:
            preset_dir = Path("presets/faces")
            if not preset_dir.exists():
                print("⚠ No presets directory found")
                return

            presets = list(preset_dir.glob("*.json"))
            if not presets:
                print("⚠ No presets found")
                return

            preset_path = presets[0]
            self.current_preset = self.generator.load_preset(str(preset_path))
            self._regenerate_all_previews()
            print(f"✓ Loaded preset from {preset_path}")
        except Exception as e:
            print(f"⚠ Failed to load preset: {e}")

    def _export_single_expression(self):
        """Export current expression."""
        try:
            output_dir = Path("exports/faces")
            output_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{self.current_preset.name}_{self.selected_expression.value}.png"
            output_path = output_dir / filename

            self.generator.render_face(
                self.current_preset, output_path, self.selected_expression, self.export_size
            )
            print(f"✓ Exported {self.selected_expression.value} to {output_path}")
        except Exception as e:
            print(f"⚠ Failed to export: {e}")

    def _export_all_expressions(self):
        """Batch export all expressions."""
        try:
            output_dir = Path("exports/faces") / self.current_preset.name
            output_dir.mkdir(parents=True, exist_ok=True)

            self.generator.batch_export_expressions(
                self.current_preset, output_dir, output_size=self.export_size
            )
            print(f"✓ Exported all expressions to {output_dir}")
        except Exception as e:
            print(f"⚠ Failed to batch export: {e}")

    def _regenerate_all_previews(self):
        """Regenerate all expression previews."""
        try:
            self.expression_previews = self.generator.render_all_expressions(
                self.current_preset, output_size=128
            )
        except Exception as e:
            print(f"⚠ Preview generation failed: {e}")
            # Create empty previews
            self.expression_previews = {
                expr: pygame.Surface((128, 128), pygame.SRCALPHA) for expr in Expression
            }
