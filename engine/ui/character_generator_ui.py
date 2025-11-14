"""
Character Generator UI - Visual Character Creator

Provides a complete visual interface for creating custom character sprites with:
- Layer-based component selection
- Real-time preview with animation
- Color tinting/customization
- Preset save/load
- Export to sprite sheets
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import re
import shutil
import datetime

import pygame

from neonworks.engine.tools.character_generator import (
    CharacterGenerator,
    CharacterPreset,
    ComponentLayer,
    LayerType,
    ColorTint,
    Direction,
)
from neonworks.engine.tools.character_bio_generator import (
    CharacterBioGenerator,
    CharacterImportance,
    generate_character_bio,
)


class CharacterGeneratorUI:
    """
    Visual character generator with real-time preview.

    Layout:
    - Left Panel (200px): Component category tabs
    - Center Panel (600px): Component thumbnail grid
    - Right Panel (400px): Live preview + animation controls
    - Bottom (full width): Color pickers, export, save/load, random
    - Layer List (right side): Drag-to-reorder layer stack
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False

        # Character generator instance
        self.generator = CharacterGenerator(default_size=64)

        # Load component library
        self._load_components()

        # Current character preset
        self.current_preset = CharacterPreset(name="New Character")

        # UI State
        self.selected_category = LayerType.BODY
        self.selected_component_id: Optional[str] = None
        self.selected_layer_index: Optional[int] = None

        # Scrolling
        self.component_scroll = 0
        self.layer_scroll = 0

        # Animation state
        self.preview_frame = 0
        self.preview_direction = Direction.DOWN
        self.animation_speed = 0.15  # seconds per frame
        self.animation_timer = 0.0
        self.animate_preview = True

        # Color picker state
        self.show_color_picker = False
        self.editing_color_layer: Optional[LayerType] = None
        self.color_sliders = {'r': 255, 'g': 255, 'b': 255, 'a': 255}

        # AI description input state
        self.ai_description = ""
        self.ai_input_active = False
        self.ai_cursor_visible = True
        self.ai_cursor_timer = 0.0

        # Drag and drop state
        self.dragging_layer_index: Optional[int] = None
        self.drag_offset_y = 0

        # Preview rendering
        self.preview_surface: Optional[pygame.Surface] = None
        self._regenerate_preview()

        # Export history tracking
        self.export_history: List[Dict] = []
        self.last_export_path: Optional[Path] = None
        self._load_export_history()

        # Batch export state
        self.batch_export_presets: List[str] = []
        self.show_batch_export = False

        # UI component references (set by master UI manager)
        self.database_editor = None
        self.asset_browser = None
        self.level_builder = None

        # Bio generation state
        self.bio_generator = CharacterBioGenerator()
        self.character_importance = CharacterImportance.NPC
        self.generated_bio: Optional[Dict[str, str]] = None
        self.manual_bio_override = False
        self.use_bio_templates = False  # False = AI generation (default)
        self.show_bio_editor = False
        self.bio_text_input = ""
        self.bio_input_active = False

        # Bio regeneration confirmation
        self.show_regen_confirmation = False
        self.pending_importance_change = None

        # Unsaved changes tracking
        self.has_unsaved_changes = False
        self.last_saved_state = None  # Snapshot of character when last saved

        # Confirmation dialogs for destructive operations
        self.show_load_preset_confirmation = False
        self.pending_preset_load = None
        self.show_randomize_confirmation = False
        self.show_clear_confirmation = False
        self.show_component_replace_confirmation = False
        self.pending_component_add = None

        # Fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 16)

    def _load_components(self):
        """Load component library from assets."""
        # Try to load from standard location
        component_path = Path("assets/character_components")
        if component_path.exists():
            try:
                self.generator.load_component_library(component_path)
                print(f"✓ Loaded character components from {component_path}")
            except Exception as e:
                print(f"⚠ Failed to load components: {e}")
        else:
            print(f"ℹ Component library not found at {component_path}")
            print("  You can generate sample components or add your own.")

    def toggle(self):
        """Toggle character generator visibility."""
        self.visible = not self.visible
        if self.visible:
            self._regenerate_preview()

    def update(self, delta_time: float):
        """Update animation and state."""
        if not self.visible:
            return

        # Update animation
        if self.animate_preview:
            self.animation_timer += delta_time
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                # Cycle through frames (assuming 4 frames)
                self.preview_frame = (self.preview_frame + 1) % 4
                self._regenerate_preview()

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
                    # Generate character from description
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

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_layer_index is not None:
                self._handle_drop(mouse_pos)
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_layer_index is not None:
                return True  # Consume event while dragging

        return False

    def render(self):
        """Render the character generator UI."""
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
        title_surface = self.title_font.render("Character Generator", True, (100, 200, 255))
        title_x = panel_x + (panel_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, panel_y + 15))

        # Close button
        close_x = panel_x + panel_width - 50
        close_y = panel_y + 10
        self._render_button("×", close_x, close_y, 35, 35, (150, 0, 0))

        # AI Description Input (below title)
        self._render_ai_input(panel_x + 10, panel_y + 50, panel_width - 20)

        # Content area (below AI input)
        content_y = panel_y + 110  # Adjusted for AI input field
        content_height = panel_height - 210  # Leave room for AI input and bottom controls

        # Layout sections
        left_panel_x = panel_x + 10
        left_panel_width = 200

        center_panel_x = left_panel_x + left_panel_width + 10
        center_panel_width = 700

        right_panel_x = center_panel_x + center_panel_width + 10
        right_panel_width = 460

        # Render main sections
        self._render_category_tabs(left_panel_x, content_y, left_panel_width, content_height)
        self._render_component_grid(center_panel_x, content_y, center_panel_width, content_height)
        self._render_preview_panel(right_panel_x, content_y, right_panel_width, content_height)

        # Bottom controls
        bottom_y = panel_y + panel_height - 90
        self._render_bottom_controls(panel_x, bottom_y, panel_width, 80)

        # Color picker overlay (if active)
        if self.show_color_picker:
            self._render_color_picker(screen_width // 2 - 200, screen_height // 2 - 250, 400, 500)

        # Confirmation dialogs (rendered on top of everything)
        if self.show_load_preset_confirmation:
            self._render_confirmation_dialog(
                "Load Preset Warning",
                [
                    "You have unsaved changes.",
                    f"Loading '{self.pending_preset_load.name if self.pending_preset_load else 'preset'}' will replace your current character.",
                    "",
                    "Do you want to proceed?"
                ],
                "Load Anyway",
                "Cancel",
                "_btn_confirm_load_yes",
                "_btn_confirm_load_no",
            )

        if self.show_randomize_confirmation:
            self._render_confirmation_dialog(
                "Randomize Warning",
                [
                    "You have unsaved changes.",
                    "Randomizing will replace your current character.",
                    "",
                    "Do you want to proceed?"
                ],
                "Randomize",
                "Cancel",
                "_btn_confirm_randomize_yes",
                "_btn_confirm_randomize_no",
            )

        if self.show_clear_confirmation:
            self._render_confirmation_dialog(
                "Clear All Warning",
                [
                    "This will remove all layers and data.",
                    "This action cannot be undone.",
                    "",
                    "Do you want to proceed?"
                ],
                "Clear All",
                "Cancel",
                "_btn_confirm_clear_yes",
                "_btn_confirm_clear_no",
            )

        if self.show_component_replace_confirmation and self.pending_component_add:
            self._render_confirmation_dialog(
                "Replace Component?",
                [
                    f"Layer {self.pending_component_add['layer_type'].name} already has:",
                    f"'{self.pending_component_add['existing_id']}'",
                    "",
                    f"Replace with '{self.pending_component_add['component_id']}'?"
                ],
                "Replace",
                "Cancel",
                "_btn_confirm_replace_yes",
                "_btn_confirm_replace_no",
            )

    def _render_category_tabs(self, x: int, y: int, width: int, height: int):
        """Render left panel with component category tabs."""
        # Panel background
        pygame.draw.rect(self.screen, (25, 25, 40), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Title
        label = self.font.render("Categories", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Category buttons
        button_y = y + 45
        button_height = 35
        button_spacing = 3

        categories = [
            LayerType.BODY,
            LayerType.HAIR_BACK,
            LayerType.HAIR_FRONT,
            LayerType.EYES,
            LayerType.FACIAL_HAIR,
            LayerType.TORSO,
            LayerType.LEGS,
            LayerType.FEET,
            LayerType.HANDS,
            LayerType.HEAD,
            LayerType.NECK,
            LayerType.CAPE,
            LayerType.WEAPON,
            LayerType.WEAPON_BACK,
            LayerType.ACCESSORY,
            LayerType.BELT,
            LayerType.EFFECT,
        ]

        mouse_pos = pygame.mouse.get_pos()

        for category in categories:
            if button_y + button_height > y + height - 10:
                break  # Out of space

            is_selected = category == self.selected_category
            color = (50, 100, 200) if is_selected else (40, 40, 60)

            # Check hover
            is_hovered = (x + 5 <= mouse_pos[0] <= x + width - 5 and
                         button_y <= mouse_pos[1] <= button_y + button_height)
            if is_hovered and not is_selected:
                color = (60, 60, 90)

            # Button
            pygame.draw.rect(self.screen, color, (x + 5, button_y, width - 10, button_height), border_radius=3)

            # Label
            category_name = category.name.replace('_', ' ').title()
            label = self.small_font.render(category_name, True, (255, 255, 255))
            self.screen.blit(label, (x + 15, button_y + 10))

            # Store button rect for click detection
            setattr(self, f'_cat_btn_{category.name}', pygame.Rect(x + 5, button_y, width - 10, button_height))

            button_y += button_height + button_spacing

    def _render_component_grid(self, x: int, y: int, width: int, height: int):
        """Render center panel with component thumbnail grid."""
        # Panel background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Title
        category_name = self.selected_category.name.replace('_', ' ').title()
        label = self.font.render(f"Components: {category_name}", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Get available components for this category
        components = self.generator.list_components(self.selected_category)

        if not components:
            # No components message
            no_comp_label = self.font.render("No components available", True, (150, 150, 150))
            label_x = x + (width - no_comp_label.get_width()) // 2
            label_y = y + height // 2
            self.screen.blit(no_comp_label, (label_x, label_y))
            return

        # Grid layout
        grid_start_y = y + 50
        grid_height = height - 60
        thumbnail_size = 96
        padding = 12
        columns = (width - 20) // (thumbnail_size + padding)

        current_x = x + 10
        current_y = grid_start_y - self.component_scroll
        col = 0
        row = 0

        mouse_pos = pygame.mouse.get_pos()

        for comp_id, comp_sprite in components.items():
            # Skip if scrolled out of view
            if current_y + thumbnail_size < grid_start_y:
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
                    current_x = x + 10
                    current_y = grid_start_y + row * (thumbnail_size + padding) - self.component_scroll
                else:
                    current_x += thumbnail_size + padding
                continue

            if current_y > y + height:
                break  # Out of view

            # Check if selected
            is_selected = comp_id == self.selected_component_id

            # Check hover
            is_hovered = (current_x <= mouse_pos[0] <= current_x + thumbnail_size and
                         current_y <= mouse_pos[1] <= current_y + thumbnail_size and
                         grid_start_y <= mouse_pos[1] <= y + height)

            # Thumbnail background
            bg_color = (80, 120, 200) if is_selected else (70, 100, 150) if is_hovered else (50, 50, 70)
            pygame.draw.rect(self.screen, bg_color,
                           (current_x, current_y, thumbnail_size, thumbnail_size),
                           border_radius=4)

            # Render component preview
            try:
                # Get a frame from the component sprite
                frame_surface = comp_sprite.get_frame(0, Direction.DOWN)
                # Scale to fit thumbnail (with some padding)
                scale_size = thumbnail_size - 16
                scaled = pygame.transform.scale(frame_surface, (scale_size, scale_size))

                # Center in thumbnail
                thumb_x = current_x + (thumbnail_size - scale_size) // 2
                thumb_y = current_y + (thumbnail_size - scale_size) // 2
                self.screen.blit(scaled, (thumb_x, thumb_y))
            except Exception as e:
                # If rendering fails, show placeholder
                pygame.draw.rect(self.screen, (100, 100, 120),
                               (current_x + 8, current_y + 8, thumbnail_size - 16, thumbnail_size - 16))

            # Component ID label (truncated)
            comp_name = comp_id[:10] + "..." if len(comp_id) > 10 else comp_id
            name_label = self.small_font.render(comp_name, True, (220, 220, 220))
            name_x = current_x + (thumbnail_size - name_label.get_width()) // 2
            name_y = current_y + thumbnail_size + 3

            # Only render if in bounds
            if name_y < y + height:
                self.screen.blit(name_label, (name_x, name_y))

            # Store rect for click detection
            setattr(self, f'_comp_btn_{comp_id}',
                   pygame.Rect(current_x, current_y, thumbnail_size, thumbnail_size))

            # Next position
            col += 1
            if col >= columns:
                col = 0
                row += 1
                current_x = x + 10
                current_y = grid_start_y + row * (thumbnail_size + padding) - self.component_scroll
            else:
                current_x += thumbnail_size + padding

    def _render_preview_panel(self, x: int, y: int, width: int, height: int):
        """Render right panel with live preview and layer list."""
        # Panel background
        pygame.draw.rect(self.screen, (25, 25, 40), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Preview section (top half)
        preview_height = height // 2

        # Title
        label = self.font.render("Preview", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Preview area (checkerboard background)
        preview_area_y = y + 45
        preview_area_height = preview_height - 90
        self._render_checkerboard(x + 10, preview_area_y, width - 20, preview_area_height)

        # Render character preview
        if self.preview_surface:
            # Center the preview
            preview_x = x + (width - self.preview_surface.get_width()) // 2
            preview_y = preview_area_y + (preview_area_height - self.preview_surface.get_height()) // 2
            self.screen.blit(self.preview_surface, (preview_x, preview_y))

        # Animation controls
        controls_y = preview_area_y + preview_area_height + 10

        # Direction selector
        dir_label = self.small_font.render("Direction:", True, (200, 200, 200))
        self.screen.blit(dir_label, (x + 10, controls_y))

        directions = [
            (Direction.UP, "↑"),
            (Direction.LEFT, "←"),
            (Direction.DOWN, "↓"),
            (Direction.RIGHT, "→"),
        ]

        dir_btn_x = x + 100
        for direction, symbol in directions:
            is_selected = direction == self.preview_direction
            color = (70, 140, 220) if is_selected else (50, 50, 70)

            self._render_button(symbol, dir_btn_x, controls_y - 5, 35, 30, color,
                              id_=f"dir_{direction.name}")
            dir_btn_x += 40

        # Animate toggle
        anim_y = controls_y + 35
        anim_color = (0, 150, 0) if self.animate_preview else (70, 70, 70)
        self._render_button("Animate" if self.animate_preview else "Static",
                          x + 10, anim_y, 120, 30, anim_color, id_="toggle_anim")

        # Character Importance selector
        importance_y = anim_y + 40
        importance_label = self.small_font.render("Importance:", True, (200, 200, 200))
        self.screen.blit(importance_label, (x + 10, importance_y))

        importance_btn_y = importance_y + 20
        importance_options = [
            (CharacterImportance.NPC, "NPC", (100, 100, 120)),
            (CharacterImportance.SUPPORTING, "Support", (120, 140, 100)),
            (CharacterImportance.MAIN, "Main", (180, 120, 100)),
        ]

        importance_btn_x = x + 10
        for importance, label, base_color in importance_options:
            is_selected = importance == self.character_importance
            color = tuple(min(c + 40, 255) for c in base_color) if is_selected else base_color

            self._render_button(label, importance_btn_x, importance_btn_y, 70, 25, color,
                              id_=f"importance_{importance.value}")
            importance_btn_x += 75

        # Bio generation toggle
        bio_toggle_y = importance_btn_y + 35
        bio_mode_label = self.small_font.render(
            "Bio: AI" if not self.use_bio_templates else "Bio: Template",
            True,
            (150, 200, 150) if not self.use_bio_templates else (200, 150, 150)
        )
        self.screen.blit(bio_mode_label, (x + 10, bio_toggle_y))

        # Manual bio edit button
        if self.generated_bio:
            edit_bio_color = (100, 150, 200) if not self.manual_bio_override else (200, 150, 100)
            self._render_button("Edit Bio", x + 130, bio_toggle_y - 3, 80, 25, edit_bio_color, id_="edit_bio")

        # Regenerate Bio button (manual trigger)
        regen_bio_y = bio_toggle_y + 30
        if self.current_preset.layers:
            regen_color = (120, 180, 120)
            self._render_button("Regenerate Bio", x + 10, regen_bio_y, 200, 25, regen_color, id_="regen_bio")

        # Confirmation dialog for bio regeneration
        if self.show_regen_confirmation:
            self._render_bio_regen_confirmation()

        # Layer list (bottom half)
        layers_y = y + preview_height + 10
        layers_height = height - preview_height - 20

        self._render_layer_list(x + 10, layers_y, width - 20, layers_height)

    def _render_layer_list(self, x: int, y: int, width: int, height: int):
        """Render layer list with drag-to-reorder."""
        # Background
        pygame.draw.rect(self.screen, (35, 35, 50), (x, y, width, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height), 1, border_radius=4)

        # Title
        label = self.font.render("Layers", True, (200, 200, 200))
        self.screen.blit(label, (x + 10, y + 10))

        # Layer items
        item_y = y + 40
        item_height = 40
        item_spacing = 3

        mouse_pos = pygame.mouse.get_pos()

        for i, layer in enumerate(self.current_preset.layers):
            if item_y + item_height > y + height - 10:
                break  # Out of space

            # Dragging offset
            if self.dragging_layer_index == i:
                item_y_adjusted = mouse_pos[1] - self.drag_offset_y
            else:
                item_y_adjusted = item_y

            # Background
            is_hovered = (x + 5 <= mouse_pos[0] <= x + width - 5 and
                         item_y_adjusted <= mouse_pos[1] <= item_y_adjusted + item_height)

            color = (60, 100, 140) if is_hovered else (45, 45, 65)
            if self.dragging_layer_index == i:
                color = (80, 120, 160)

            pygame.draw.rect(self.screen, color,
                           (x + 5, item_y_adjusted, width - 10, item_height),
                           border_radius=3)

            # Layer type label
            layer_name = layer.layer_type.name.replace('_', ' ').title()
            layer_label = self.small_font.render(layer_name, True, (255, 255, 255))
            self.screen.blit(layer_label, (x + 15, item_y_adjusted + 5))

            # Component ID (truncated)
            comp_id_short = layer.component_id[:15] + "..." if len(layer.component_id) > 15 else layer.component_id
            comp_label = self.small_font.render(comp_id_short, True, (180, 180, 180))
            self.screen.blit(comp_label, (x + 15, item_y_adjusted + 22))

            # Color indicator (if tinted)
            if layer.tint:
                color_rect_x = x + width - 50
                pygame.draw.rect(self.screen,
                               (layer.tint.r, layer.tint.g, layer.tint.b),
                               (color_rect_x, item_y_adjusted + 10, 20, 20))
                pygame.draw.rect(self.screen, (200, 200, 200),
                               (color_rect_x, item_y_adjusted + 10, 20, 20), 1)

            # Delete button
            delete_x = x + width - 25
            if self._render_button("×", delete_x, item_y_adjusted + 10, 20, 20, (150, 0, 0),
                                  id_=f"delete_layer_{i}", return_hovered=True):
                pass  # Will be handled in click

            # Store rect for click/drag detection
            setattr(self, f'_layer_item_{i}',
                   pygame.Rect(x + 5, item_y, width - 10, item_height))

            if self.dragging_layer_index != i:
                item_y += item_height + item_spacing

    def _render_bottom_controls(self, x: int, y: int, width: int, height: int):
        """Render bottom control buttons."""
        # Background
        pygame.draw.rect(self.screen, (30, 30, 45), (x + 10, y, width - 20, height), border_radius=4)
        pygame.draw.rect(self.screen, (60, 60, 80), (x + 10, y, width - 20, height), 1, border_radius=4)

        button_width = 140
        button_height = 40
        button_y = y + (height - button_height) // 2
        button_spacing = 15

        buttons = [
            ("Add to Character", (0, 120, 200), "add_component"),
            ("Color Tint", (120, 80, 200), "color_tint"),
            ("Randomize", (200, 120, 0), "randomize"),
            ("Clear All", (150, 0, 0), "clear_all"),
            ("Save Preset", (0, 150, 0), "save_preset"),
            ("Load Preset", (0, 100, 150), "load_preset"),
            ("Export PNG", (200, 100, 200), "export"),
            ("Create Actor", (100, 200, 100), "create_actor"),
            ("Batch Export", (150, 100, 0), "batch_export"),
        ]

        button_x = x + 20
        for label, color, btn_id in buttons:
            self._render_button(label, button_x, button_y, button_width, button_height, color, id_=btn_id)
            button_x += button_width + button_spacing

    def _render_button(self, text: str, x: int, y: int, width: int, height: int,
                      color: Tuple[int, int, int], id_: str = "", return_hovered: bool = False) -> bool:
        """Render a button and return True if hovered (for click detection)."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = (x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height)

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
            setattr(self, f'_btn_{id_}', pygame.Rect(x, y, width, height))

        return is_hovered if return_hovered else False

    def _render_checkerboard(self, x: int, y: int, width: int, height: int, square_size: int = 16):
        """Render a checkerboard pattern (for transparency preview)."""
        color1 = (100, 100, 100)
        color2 = (130, 130, 130)

        for row in range(0, height, square_size):
            for col in range(0, width, square_size):
                color = color1 if (row // square_size + col // square_size) % 2 == 0 else color2
                rect_width = min(square_size, width - col)
                rect_height = min(square_size, height - row)
                pygame.draw.rect(self.screen, color, (x + col, y + row, rect_width, rect_height))

    def _render_ai_input(self, x: int, y: int, width: int):
        """Render AI description input field."""
        input_height = 45
        button_width = 180

        # Input field background
        input_bg_color = (60, 100, 140) if self.ai_input_active else (40, 40, 60)
        pygame.draw.rect(self.screen, input_bg_color,
                        (x, y, width - button_width - 10, input_height),
                        border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 120),
                        (x, y, width - button_width - 10, input_height), 2, border_radius=4)

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
                pygame.draw.rect(self.screen, (255, 255, 255),
                               (cursor_x, text_y, 2, 20))
        else:
            # Placeholder text
            placeholder = "🤖 Describe your character... (e.g., 'A brave knight with brown hair and blue armor')"
            placeholder_color = (120, 120, 140) if not self.ai_input_active else (150, 150, 170)
            text_surface = self.small_font.render(placeholder, True, placeholder_color)
            self.screen.blit(text_surface, (text_x, text_y + 5))

            # Cursor at start
            if self.ai_input_active and self.ai_cursor_visible:
                pygame.draw.rect(self.screen, (255, 255, 255),
                               (text_x, text_y, 2, 20))

        # Generate button
        button_x = x + width - button_width
        button_color = (0, 150, 200) if self.ai_description.strip() else (60, 60, 80)
        self._render_button("Generate from AI ✨", button_x, y, button_width, input_height,
                          button_color, id_="generate_ai")

        # Store input field rect for click detection
        setattr(self, '_ai_input_rect', pygame.Rect(x, y, width - button_width - 10, input_height))

    def _render_color_picker(self, x: int, y: int, width: int, height: int):
        """Render color picker overlay."""
        # Background
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, width, height), border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, width, height), 2, border_radius=8)

        # Title
        title = self.font.render("Color Tint", True, (200, 200, 200))
        self.screen.blit(title, (x + 20, y + 20))

        # Close button
        if self._render_button("×", x + width - 50, y + 15, 35, 35, (150, 0, 0), id_="close_picker"):
            pass

        # Color sliders
        slider_y = y + 70
        slider_height = 30
        slider_spacing = 50

        for channel in ['r', 'g', 'b', 'a']:
            label_color = {
                'r': (255, 100, 100),
                'g': (100, 255, 100),
                'b': (100, 100, 255),
                'a': (200, 200, 200),
            }[channel]

            label = self.font.render(channel.upper(), True, label_color)
            self.screen.blit(label, (x + 20, slider_y))

            # Slider track
            track_x = x + 60
            track_width = width - 100
            pygame.draw.rect(self.screen, (50, 50, 70),
                           (track_x, slider_y, track_width, slider_height),
                           border_radius=3)

            # Slider fill
            fill_width = int((self.color_sliders[channel] / 255) * track_width)
            fill_color = label_color
            pygame.draw.rect(self.screen, fill_color,
                           (track_x, slider_y, fill_width, slider_height),
                           border_radius=3)

            # Value label
            value_label = self.font.render(str(self.color_sliders[channel]), True, (255, 255, 255))
            self.screen.blit(value_label, (x + width - 70, slider_y + 5))

            # Store rect for interaction
            setattr(self, f'_slider_{channel}',
                   pygame.Rect(track_x, slider_y, track_width, slider_height))

            slider_y += slider_spacing

        # Color preview
        preview_y = slider_y + 20
        preview_size = 100
        preview_x = x + (width - preview_size) // 2

        self._render_checkerboard(preview_x, preview_y, preview_size, preview_size, 10)

        preview_color = (
            self.color_sliders['r'],
            self.color_sliders['g'],
            self.color_sliders['b'],
            self.color_sliders['a'],
        )
        preview_surface = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
        preview_surface.fill(preview_color)
        self.screen.blit(preview_surface, (preview_x, preview_y))

        # Apply button
        apply_y = preview_y + preview_size + 30
        self._render_button("Apply", x + width // 2 - 60, apply_y, 120, 40,
                          (0, 150, 0), id_="apply_color")

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click events."""
        # AI input field click
        if hasattr(self, '_ai_input_rect'):
            rect = getattr(self, '_ai_input_rect')
            if rect.collidepoint(mouse_pos):
                self.ai_input_active = True
                return True

        # Generate from AI button
        if hasattr(self, '_btn_generate_ai'):
            rect = getattr(self, '_btn_generate_ai')
            if rect.collidepoint(mouse_pos) and self.ai_description.strip():
                self._generate_from_ai_description()
                return True

        # Close button
        if hasattr(self, '_btn_') and self._check_button_click('_btn_', mouse_pos):
            close_rect = getattr(self, '_btn_', None)
            if close_rect and close_rect.collidepoint(mouse_pos):
                self.visible = False
                return True

        # Category buttons
        for category in LayerType:
            btn_attr = f'_cat_btn_{category.name}'
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    self.selected_category = category
                    self.component_scroll = 0
                    return True

        # Component thumbnails
        components = self.generator.list_components(self.selected_category)
        for comp_id in components.keys():
            btn_attr = f'_comp_btn_{comp_id}'
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    self.selected_component_id = comp_id
                    return True

        # Direction buttons
        for direction in [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]:
            btn_attr = f'_btn_dir_{direction.name}'
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    self.preview_direction = direction
                    self.preview_frame = 0
                    self._regenerate_preview()
                    return True

        # Animation toggle
        if hasattr(self, '_btn_toggle_anim'):
            rect = getattr(self, '_btn_toggle_anim')
            if rect.collidepoint(mouse_pos):
                self.animate_preview = not self.animate_preview
                return True

        # Character importance selector
        for importance in CharacterImportance:
            btn_attr = f'_btn_importance_{importance.value}'
            if hasattr(self, btn_attr):
                rect = getattr(self, btn_attr)
                if rect.collidepoint(mouse_pos):
                    # Check if bio exists and would be overwritten
                    if self.generated_bio and importance != self.character_importance:
                        # Show confirmation dialog
                        self.show_regen_confirmation = True
                        self.pending_importance_change = importance
                        print(f"⚠ Importance change: {self.character_importance.value} → {importance.value}")
                        print("  This will require bio regeneration. Confirm in UI to proceed.")
                    else:
                        # No bio exists yet, safe to change
                        self.character_importance = importance
                        print(f"✓ Importance set to: {importance.value.upper()}")
                    return True

        # Edit bio button
        if hasattr(self, '_btn_edit_bio'):
            rect = getattr(self, '_btn_edit_bio')
            if rect.collidepoint(mouse_pos):
                self._open_bio_editor()
                return True

        # Regenerate bio button
        if hasattr(self, '_btn_regen_bio'):
            rect = getattr(self, '_btn_regen_bio')
            if rect.collidepoint(mouse_pos):
                self._generate_bio()
                print("✓ Bio regenerated")
                return True

        # Bio regeneration confirmation dialog
        if self.show_regen_confirmation:
            if hasattr(self, '_btn_confirm_regen_yes'):
                rect = getattr(self, '_btn_confirm_regen_yes')
                if rect.collidepoint(mouse_pos):
                    # User confirmed - apply importance change and regenerate
                    self.character_importance = self.pending_importance_change
                    self._generate_bio()
                    self.show_regen_confirmation = False
                    self.pending_importance_change = None
                    print(f"✓ Importance changed to {self.character_importance.value.upper()} and bio regenerated")
                    return True

            if hasattr(self, '_btn_confirm_regen_no'):
                rect = getattr(self, '_btn_confirm_regen_no')
                if rect.collidepoint(mouse_pos):
                    # User cancelled - keep current importance and bio
                    self.show_regen_confirmation = False
                    self.pending_importance_change = None
                    print("✓ Importance change cancelled - bio preserved")
                    return True

        # Load Preset confirmation
        if self.show_load_preset_confirmation:
            if hasattr(self, '_btn_confirm_load_yes'):
                rect = getattr(self, '_btn_confirm_load_yes')
                if rect.collidepoint(mouse_pos):
                    self._do_load_preset(self.pending_preset_load)
                    return True

            if hasattr(self, '_btn_confirm_load_no'):
                rect = getattr(self, '_btn_confirm_load_no')
                if rect.collidepoint(mouse_pos):
                    self.show_load_preset_confirmation = False
                    self.pending_preset_load = None
                    print("✓ Load cancelled - current character preserved")
                    return True

        # Randomize confirmation
        if self.show_randomize_confirmation:
            if hasattr(self, '_btn_confirm_randomize_yes'):
                rect = getattr(self, '_btn_confirm_randomize_yes')
                if rect.collidepoint(mouse_pos):
                    self._do_randomize()
                    self.show_randomize_confirmation = False
                    return True

            if hasattr(self, '_btn_confirm_randomize_no'):
                rect = getattr(self, '_btn_confirm_randomize_no')
                if rect.collidepoint(mouse_pos):
                    self.show_randomize_confirmation = False
                    print("✓ Randomize cancelled - current character preserved")
                    return True

        # Clear All confirmation
        if self.show_clear_confirmation:
            if hasattr(self, '_btn_confirm_clear_yes'):
                rect = getattr(self, '_btn_confirm_clear_yes')
                if rect.collidepoint(mouse_pos):
                    self._do_clear_all()
                    return True

            if hasattr(self, '_btn_confirm_clear_no'):
                rect = getattr(self, '_btn_confirm_clear_no')
                if rect.collidepoint(mouse_pos):
                    self.show_clear_confirmation = False
                    print("✓ Clear cancelled - current character preserved")
                    return True

        # Component Replace confirmation
        if self.show_component_replace_confirmation:
            if hasattr(self, '_btn_confirm_replace_yes'):
                rect = getattr(self, '_btn_confirm_replace_yes')
                if rect.collidepoint(mouse_pos):
                    self._replace_component()
                    return True

            if hasattr(self, '_btn_confirm_replace_no'):
                rect = getattr(self, '_btn_confirm_replace_no')
                if rect.collidepoint(mouse_pos):
                    self.show_component_replace_confirmation = False
                    self.pending_component_add = None
                    print("✓ Component replacement cancelled")
                    return True

        # Bottom control buttons
        if hasattr(self, '_btn_add_component'):
            if getattr(self, '_btn_add_component').collidepoint(mouse_pos):
                self._add_component_to_character()
                return True

        if hasattr(self, '_btn_color_tint'):
            if getattr(self, '_btn_color_tint').collidepoint(mouse_pos):
                self.show_color_picker = True
                return True

        if hasattr(self, '_btn_randomize'):
            if getattr(self, '_btn_randomize').collidepoint(mouse_pos):
                self._randomize_character()
                return True

        if hasattr(self, '_btn_clear_all'):
            if getattr(self, '_btn_clear_all').collidepoint(mouse_pos):
                self._clear_all()
                return True

        if hasattr(self, '_btn_save_preset'):
            if getattr(self, '_btn_save_preset').collidepoint(mouse_pos):
                self._save_preset()
                return True

        if hasattr(self, '_btn_load_preset'):
            if getattr(self, '_btn_load_preset').collidepoint(mouse_pos):
                self._load_preset()
                return True

        if hasattr(self, '_btn_export'):
            if getattr(self, '_btn_export').collidepoint(mouse_pos):
                self._export_character()
                return True

        if hasattr(self, '_btn_create_actor'):
            if getattr(self, '_btn_create_actor').collidepoint(mouse_pos):
                self._create_actor_from_character()
                return True

        if hasattr(self, '_btn_batch_export'):
            if getattr(self, '_btn_batch_export').collidepoint(mouse_pos):
                self._batch_export_characters()
                return True

        # Color picker buttons
        if self.show_color_picker:
            if hasattr(self, '_btn_close_picker'):
                if getattr(self, '_btn_close_picker').collidepoint(mouse_pos):
                    self.show_color_picker = False
                    return True

            if hasattr(self, '_btn_apply_color'):
                if getattr(self, '_btn_apply_color').collidepoint(mouse_pos):
                    self._apply_color_tint()
                    return True

            # Check slider clicks
            for channel in ['r', 'g', 'b', 'a']:
                slider_attr = f'_slider_{channel}'
                if hasattr(self, slider_attr):
                    rect = getattr(self, slider_attr)
                    if rect.collidepoint(mouse_pos):
                        # Calculate value from click position
                        normalized = (mouse_pos[0] - rect.x) / rect.width
                        normalized = max(0.0, min(1.0, normalized))
                        self.color_sliders[channel] = int(normalized * 255)
                        return True

        # Layer item clicks (for dragging)
        for i in range(len(self.current_preset.layers)):
            layer_attr = f'_layer_item_{i}'
            delete_attr = f'_btn_delete_layer_{i}'

            # Check delete button first
            if hasattr(self, delete_attr):
                rect = getattr(self, delete_attr)
                if rect.collidepoint(mouse_pos):
                    self.current_preset.layers.pop(i)
                    self._mark_unsaved_changes()
                    self._regenerate_preview()
                    return True

            # Check layer item for dragging
            if hasattr(self, layer_attr):
                rect = getattr(self, layer_attr)
                if rect.collidepoint(mouse_pos):
                    self.dragging_layer_index = i
                    self.drag_offset_y = mouse_pos[1] - rect.y
                    return True

        return False

    def _handle_scroll(self, direction: int, mouse_pos: Tuple[int, int]):
        """Handle scroll wheel."""
        # Component grid scrolling would be detected here based on mouse position
        # Simplified: always scroll component grid
        self.component_scroll += direction * 30
        self.component_scroll = max(0, self.component_scroll)

    def _handle_drop(self, mouse_pos: Tuple[int, int]):
        """Handle layer drag and drop."""
        if self.dragging_layer_index is None:
            return

        # Find which layer position we're over
        drop_index = None
        for i in range(len(self.current_preset.layers)):
            layer_attr = f'_layer_item_{i}'
            if hasattr(self, layer_attr):
                rect = getattr(self, layer_attr)
                if rect.collidepoint(mouse_pos):
                    drop_index = i
                    break

        # Reorder layers
        if drop_index is not None and drop_index != self.dragging_layer_index:
            layer = self.current_preset.layers.pop(self.dragging_layer_index)
            self.current_preset.layers.insert(drop_index, layer)
            self._regenerate_preview()

        self.dragging_layer_index = None

    def _add_component_to_character(self):
        """Add selected component to character."""
        if not self.selected_component_id:
            print("⚠ No component selected")
            return

        # Check if layer already has a component (replacement warning)
        existing_layer = next(
            (l for l in self.current_preset.layers if l.layer_type == self.selected_category),
            None
        )

        if existing_layer:
            # Show confirmation for component replacement
            self.show_component_replace_confirmation = True
            self.pending_component_add = {
                "component_id": self.selected_component_id,
                "layer_type": self.selected_category,
                "existing_id": existing_layer.component_id,
            }
            print(f"⚠ Layer {self.selected_category.name} already has {existing_layer.component_id}")
            print("  Confirm replacement in UI")
            return

        # No existing component, safe to add
        self._do_add_component()

    def _do_add_component(self):
        """Actually add the component (after confirmation if needed)."""
        if not self.selected_component_id:
            return

        # Create layer
        layer = ComponentLayer(
            layer_type=self.selected_category,
            component_id=self.selected_component_id,
            enabled=True,
        )

        self.current_preset.add_layer(layer)
        self._regenerate_preview()
        self._mark_unsaved_changes()
        print(f"✓ Added {self.selected_component_id} to character")

    def _replace_component(self):
        """Replace existing component with pending one."""
        if not self.pending_component_add:
            return

        # Remove existing layer
        self.current_preset.layers = [
            l for l in self.current_preset.layers
            if l.layer_type != self.pending_component_add["layer_type"]
        ]

        # Add new layer
        layer = ComponentLayer(
            layer_type=self.pending_component_add["layer_type"],
            component_id=self.pending_component_add["component_id"],
            enabled=True,
        )

        self.current_preset.add_layer(layer)
        self._regenerate_preview()
        self._mark_unsaved_changes()
        print(f"✓ Replaced {self.pending_component_add['existing_id']} with {self.pending_component_add['component_id']}")

        # Clean up
        self.pending_component_add = None
        self.show_component_replace_confirmation = False

    def _randomize_character(self):
        """Generate a random character (with confirmation if needed)."""
        # Check for unsaved changes
        if self._has_content():
            self.show_randomize_confirmation = True
            print("⚠ Character has content - confirm randomization in UI")
            return

        # No content, safe to randomize
        self._do_randomize()

    def _do_randomize(self):
        """Actually randomize the character."""
        try:
            self.current_preset = self.generator.randomize_character()
            self._regenerate_preview()
            self.has_unsaved_changes = False  # Fresh start
            self.generated_bio = None  # Clear bio
            print("✓ Generated random character")
        except Exception as e:
            print(f"⚠ Failed to randomize: {e}")

    def _generate_from_ai_description(self):
        """Generate character from AI description."""
        if not self.ai_description.strip():
            return

        try:
            print(f"🤖 Generating character from: '{self.ai_description}'")

            # Use the character generator's AI-friendly method
            self.current_preset = self.generator.generate_from_description(
                self.ai_description,
                name=self._extract_name_from_description() or "AI Generated Character"
            )

            self._regenerate_preview()
            print("✓ AI character generation complete!")

            # Clear the input after successful generation
            self.ai_description = ""
            self.ai_input_active = False

        except Exception as e:
            print(f"⚠ Failed to generate from AI: {e}")
            print(f"   Description was: '{self.ai_description}'")

    def _extract_name_from_description(self) -> Optional[str]:
        """Try to extract a name from the description."""
        # Simple pattern matching for names
        # Example: "Create a knight named Arthur" -> "Arthur"
        patterns = [
            r'named\s+(\w+)',
            r'called\s+(\w+)',
            r'name\s+(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.ai_description, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()

        return None

    def _apply_color_tint(self):
        """Apply color tint to selected layer."""
        if not self.current_preset.layers:
            print("⚠ No layers to tint")
            return

        # Apply to last layer (could be enhanced to select specific layer)
        layer = self.current_preset.layers[-1]
        layer.tint = ColorTint(
            r=self.color_sliders['r'],
            g=self.color_sliders['g'],
            b=self.color_sliders['b'],
            a=self.color_sliders['a'],
        )

        self._regenerate_preview()
        self.show_color_picker = False
        print(f"✓ Applied color tint to {layer.layer_type.name}")

    def _save_preset(self):
        """Save current preset to file."""
        try:
            preset_dir = Path("presets/characters")
            preset_dir.mkdir(parents=True, exist_ok=True)

            preset_path = preset_dir / f"{self.current_preset.name}.json"
            self.generator.save_preset(self.current_preset, str(preset_path))

            # Mark as saved
            self.has_unsaved_changes = False
            self.last_saved_state = len(self.current_preset.layers)  # Simple snapshot

            print(f"✓ Saved preset to {preset_path}")
        except Exception as e:
            print(f"⚠ Failed to save preset: {e}")

    def _load_preset(self):
        """Load preset from file (with confirmation if needed)."""
        # Check for unsaved changes
        if self._has_content():
            # Store the preset path for after confirmation
            try:
                preset_dir = Path("presets/characters")
                if not preset_dir.exists():
                    print("⚠ No presets directory found")
                    return

                presets = list(preset_dir.glob("*.json"))
                if not presets:
                    print("⚠ No presets found")
                    return

                # For now, load first preset (can be enhanced with file picker)
                self.pending_preset_load = presets[0]
                self.show_load_preset_confirmation = True
                print(f"⚠ Loading {presets[0].name} will replace current character")
                print("  Confirm in UI")
                return
            except Exception as e:
                print(f"⚠ Failed to check presets: {e}")
                return

        # No content, safe to load
        self._do_load_preset()

    def _do_load_preset(self, preset_path: Optional[Path] = None):
        """Actually load the preset."""
        try:
            if preset_path is None:
                preset_dir = Path("presets/characters")
                if not preset_dir.exists():
                    print("⚠ No presets directory found")
                    return

                presets = list(preset_dir.glob("*.json"))
                if not presets:
                    print("⚠ No presets found")
                    return

                preset_path = presets[0]

            # Load preset
            self.current_preset = self.generator.load_preset(str(preset_path))
            self._regenerate_preview()

            # Mark as saved and clear bio
            self.has_unsaved_changes = False
            self.last_saved_state = len(self.current_preset.layers)
            self.generated_bio = None

            # Clean up confirmation state
            self.pending_preset_load = None
            self.show_load_preset_confirmation = False

            print(f"✓ Loaded preset from {preset_path}")
        except Exception as e:
            print(f"⚠ Failed to load preset: {e}")

    def _export_character(self):
        """Export character to PNG sprite sheet and copy to assets."""
        try:
            output_dir = Path("exports/characters")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename with timestamp if needed
            base_name = self.current_preset.name.replace(" ", "_")
            output_path = output_dir / f"{base_name}.png"

            # If file exists, add timestamp
            if output_path.exists():
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"{base_name}_{timestamp}.png"

            # Render sprite sheet (4 frames, 4 directions)
            sprite_sheet = self.generator.render_sprite_sheet(
                self.current_preset,
                num_frames=4,
                num_directions=4,
            )

            # Save to exports directory
            pygame.image.save(sprite_sheet, str(output_path))
            print(f"✓ Exported character to {output_path}")

            # Copy to assets/sprites directory for asset browser
            assets_dir = Path("assets/sprites")
            assets_dir.mkdir(parents=True, exist_ok=True)

            assets_path = assets_dir / output_path.name
            shutil.copy2(output_path, assets_path)
            print(f"✓ Copied to assets: {assets_path}")

            # Add to export history
            self._add_to_export_history(output_path, assets_path)

            # Store last export path
            self.last_export_path = output_path

            # Refresh asset browser if available
            if self.asset_browser:
                self.asset_browser.refresh_assets()

        except Exception as e:
            print(f"⚠ Failed to export: {e}")

    def _regenerate_preview(self):
        """Regenerate the preview surface."""
        try:
            if not self.current_preset.layers:
                # Empty character - create blank surface
                self.preview_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
                self.preview_surface.fill((0, 0, 0, 0))
                return

            # Compose layers
            preview_size = 256  # Large preview
            self.preview_surface = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
            self.preview_surface.fill((0, 0, 0, 0))

            for layer in self.current_preset.layers:
                if not layer.enabled:
                    continue

                # Get component
                comp_id = layer.component_id
                comp_sprite = self.generator.component_library.get(comp_id)

                if not comp_sprite:
                    continue

                # Get frame
                frame = comp_sprite.get_frame(self.preview_frame, self.preview_direction)

                # Apply tint if needed
                if layer.tint:
                    # Create tinted version
                    tinted = frame.copy()
                    # Simple multiply blend (could be enhanced)
                    tint_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                    tint_surface.fill((layer.tint.r, layer.tint.g, layer.tint.b, layer.tint.a))
                    tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    frame = tinted

                # Scale up for preview
                scaled = pygame.transform.scale(frame, (preview_size, preview_size))

                # Composite
                self.preview_surface.blit(scaled, (0, 0))

        except Exception as e:
            print(f"⚠ Preview generation failed: {e}")
            self.preview_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.preview_surface.fill((100, 0, 0, 128))  # Red error indicator

    def _check_button_click(self, prefix: str, mouse_pos: Tuple[int, int]) -> bool:
        """Helper to check if any button with prefix was clicked."""
        for attr_name in dir(self):
            if attr_name.startswith(prefix):
                rect = getattr(self, attr_name)
                if isinstance(rect, pygame.Rect) and rect.collidepoint(mouse_pos):
                    return True
        return False

    def _load_export_history(self):
        """Load export history from file."""
        history_file = Path("exports/characters/export_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.export_history = json.load(f)
                print(f"✓ Loaded {len(self.export_history)} export history entries")
            except Exception as e:
                print(f"⚠ Failed to load export history: {e}")
                self.export_history = []
        else:
            self.export_history = []

    def _add_to_export_history(self, export_path: Path, assets_path: Path):
        """Add an export to the history and save to file."""
        history_entry = {
            "character_name": self.current_preset.name,
            "export_path": str(export_path),
            "assets_path": str(assets_path),
            "timestamp": datetime.datetime.now().isoformat(),
            "preset_file": f"presets/characters/{self.current_preset.name}.json",
            "layers_count": len(self.current_preset.layers),
            "importance": self.character_importance.value if self.character_importance else "npc",
            "has_bio": self.generated_bio is not None,
        }

        # Add bio if generated
        if self.generated_bio:
            history_entry["bio"] = self.generated_bio.copy()

        self.export_history.append(history_entry)

        # Save history to file
        history_file = Path("exports/characters/export_history.json")
        history_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(history_file, 'w') as f:
                json.dump(self.export_history, f, indent=2)
            print(f"✓ Export history updated ({len(self.export_history)} entries)")
        except Exception as e:
            print(f"⚠ Failed to save export history: {e}")

    def _create_actor_from_character(self):
        """Create an actor in the database from the current character."""
        if not self.current_preset.layers:
            print("⚠ Cannot create actor from empty character")
            return

        # First, export the character if not already exported
        if not self.last_export_path or not self.last_export_path.exists():
            print("ℹ Exporting character first...")
            self._export_character()

        # Generate bio if not already generated
        if not self.generated_bio:
            print("ℹ Generating bio...")
            self._generate_bio()

        # Prepare bio text
        if self.generated_bio:
            description = self.generated_bio['description']
            note = self.generated_bio['note']
        else:
            description = f"Generated character: {self.current_preset.name}"
            note = f"Created from character generator on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Open database editor if available
        if self.database_editor:
            try:
                from neonworks.engine.data.database_schema import Actor

                # Create a new actor with generated bio
                new_actor = Actor(
                    id=0,  # Will be auto-assigned
                    name=self.current_preset.name,
                    nickname="",
                    class_id=1,
                    initial_level=1,
                    max_level=99,
                    character_name=self.last_export_path.stem if self.last_export_path else self.current_preset.name,
                    face_name="",
                    face_index=0,
                    icon_index=1,
                    description=description,
                    note=note,
                )

                # Add to database
                created_actor = self.database_editor.db.create("actors", new_actor, auto_id=True)

                # Select the new actor in the database editor
                self.database_editor.current_category = "actors"
                self.database_editor.current_entry = created_actor
                self.database_editor.has_unsaved_changes = True

                # Open the database editor
                if not self.database_editor.visible:
                    self.database_editor.toggle()

                print(f"✓ Created actor '{self.current_preset.name}' (ID: {created_actor.id}) in database")
                print(f"  Character sprite: {self.last_export_path.name if self.last_export_path else 'N/A'}")

            except Exception as e:
                print(f"⚠ Failed to create actor: {e}")
        else:
            print("⚠ Database editor not available")
            print("  Please connect the database editor to the character generator")

    def _batch_export_characters(self):
        """Batch export all presets from the presets directory."""
        preset_dir = Path("presets/characters")

        if not preset_dir.exists():
            print("⚠ No presets directory found")
            return

        presets = list(preset_dir.glob("*.json"))

        if not presets:
            print("⚠ No presets found to export")
            return

        print(f"🔄 Starting batch export of {len(presets)} presets...")

        exported_count = 0
        failed_count = 0

        for preset_path in presets:
            try:
                # Load preset
                preset = self.generator.load_preset(str(preset_path))

                # Temporarily set as current preset
                original_preset = self.current_preset
                original_bio = self.generated_bio
                self.current_preset = preset

                # Generate bio for this character (use NPC level for batch export)
                self.character_importance = CharacterImportance.NPC
                self._generate_bio()

                # Export (sprite + bio in history)
                self._export_character()

                # Restore original preset and bio
                self.current_preset = original_preset
                self.generated_bio = original_bio

                exported_count += 1

            except Exception as e:
                print(f"⚠ Failed to export {preset_path.name}: {e}")
                failed_count += 1

        print(f"✓ Batch export complete: {exported_count} succeeded, {failed_count} failed")

    def set_ui_references(self, database_editor=None, asset_browser=None, level_builder=None):
        """Set references to other UI components for integration."""
        self.database_editor = database_editor
        self.asset_browser = asset_browser
        self.level_builder = level_builder
        print("✓ Character generator UI references set")

    def _generate_bio(self):
        """Generate character bio using AI or templates."""
        if not self.current_preset.layers:
            print("⚠ Cannot generate bio for empty character")
            return

        # Detect character type from preset name or layers
        character_type = self._detect_character_type()

        # Convert layers to dict format
        layers_data = []
        for layer in self.current_preset.layers:
            layers_data.append({
                "layer_type": layer.layer_type.name,
                "component_id": layer.component_id,
                "tint": layer.tint.to_dict() if layer.tint else None,
            })

        try:
            self.generated_bio = generate_character_bio(
                character_name=self.current_preset.name,
                character_type=character_type,
                layers=layers_data,
                importance=self.character_importance.value,
                use_ai=not self.use_bio_templates,
            )

            print(f"✓ Generated {self.character_importance.value.upper()} bio for {self.current_preset.name}")
            if self.character_importance == CharacterImportance.NPC:
                print(f"  Short: {len(self.generated_bio['description'])} chars")
            else:
                print(f"  Description: {len(self.generated_bio['description'])} chars")
                print(f"  Full Bio: {len(self.generated_bio['note'])} chars")

        except Exception as e:
            print(f"⚠ Failed to generate bio: {e}")
            self.generated_bio = None

    def _detect_character_type(self) -> str:
        """Detect character type from preset name or appearance."""
        name_lower = self.current_preset.name.lower()

        # Check preset name for keywords
        type_keywords = {
            "warrior": ["warrior", "fighter", "soldier"],
            "mage": ["mage", "wizard", "sorcerer", "witch"],
            "thief": ["thief", "rogue", "assassin", "ninja"],
            "cleric": ["cleric", "priest", "healer"],
            "archer": ["archer", "ranger", "hunter"],
            "knight": ["knight", "paladin", "crusader"],
            "monk": ["monk", "martial artist"],
            "bard": ["bard", "musician"],
        }

        for char_type, keywords in type_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return char_type

        # Default to generic based on equipment
        has_armor = any("armor" in layer.component_id.lower() for layer in self.current_preset.layers)
        has_robe = any("robe" in layer.component_id.lower() for layer in self.current_preset.layers)

        if has_robe:
            return "mage"
        elif has_armor:
            return "warrior"
        else:
            return "warrior"  # Default

    def _open_bio_editor(self):
        """Open bio editor for manual editing."""
        if not self.generated_bio:
            self._generate_bio()

        if self.generated_bio:
            self.bio_text_input = self.generated_bio['description']
            self.show_bio_editor = True
            self.manual_bio_override = True
            print("✓ Bio editor opened - Press Enter to save, ESC to cancel")

    def _apply_manual_bio(self, bio_text: str):
        """Apply manually edited bio."""
        if self.generated_bio:
            self.generated_bio['description'] = bio_text
            # Keep the same note or update it
            if not self.generated_bio['note'].startswith("Manual"):
                self.generated_bio['note'] = f"Manual Override:\n\n{bio_text}"
            print("✓ Manual bio applied")
        else:
            # Create new bio entry
            self.generated_bio = {
                "description": bio_text,
                "note": f"Manual Bio:\n\n{bio_text}",
            }
            print("✓ Manual bio created")

    def _render_bio_regen_confirmation(self):
        """Render confirmation dialog for bio regeneration."""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        dialog_width = 500
        dialog_height = 220
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        # Background
        pygame.draw.rect(self.screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 120), (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=8)

        # Title
        title_text = self.title_font.render("Bio Regeneration Required", True, (255, 200, 100))
        title_rect = title_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 30))
        self.screen.blit(title_text, title_rect)

        # Message
        message_lines = [
            f"Changing importance from {self.character_importance.value.upper()} to {self.pending_importance_change.value.upper()}",
            "will require regenerating the bio to match the new role.",
            "",
            "This will overwrite your current bio.",
            "Do you want to proceed?"
        ]

        message_y = dialog_y + 65
        for line in message_lines:
            text = self.small_font.render(line, True, (220, 220, 220))
            text_rect = text.get_rect(center=(dialog_x + dialog_width // 2, message_y))
            self.screen.blit(text, text_rect)
            message_y += 22

        # Buttons
        button_y = dialog_y + dialog_height - 50
        button_width = 120
        button_height = 35
        button_spacing = 20

        # Yes button
        yes_x = dialog_x + (dialog_width // 2) - button_width - (button_spacing // 2)
        yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 180, 100), yes_rect, border_radius=5)
        pygame.draw.rect(self.screen, (150, 220, 150), yes_rect, 2, border_radius=5)
        yes_text = self.font.render("Yes, Regenerate", True, (255, 255, 255))
        yes_text_rect = yes_text.get_rect(center=yes_rect.center)
        self.screen.blit(yes_text, yes_text_rect)
        self._btn_confirm_regen_yes = yes_rect

        # No button
        no_x = dialog_x + (dialog_width // 2) + (button_spacing // 2)
        no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (180, 100, 100), no_rect, border_radius=5)
        pygame.draw.rect(self.screen, (220, 150, 150), no_rect, 2, border_radius=5)
        no_text = self.font.render("No, Keep Bio", True, (255, 255, 255))
        no_text_rect = no_text.get_rect(center=no_rect.center)
        self.screen.blit(no_text, no_text_rect)
        self._btn_confirm_regen_no = no_rect

    # === Data Loss Prevention Methods ===

    def _has_content(self) -> bool:
        """Check if character has any content that would be lost."""
        return len(self.current_preset.layers) > 0 or self.generated_bio is not None

    def _mark_unsaved_changes(self):
        """Mark that the character has unsaved changes."""
        self.has_unsaved_changes = True

    def _clear_all(self):
        """Clear all character data (with confirmation)."""
        if self._has_content():
            self.show_clear_confirmation = True
            print("⚠ Character has content - confirm clear in UI")
            return

        # No content, safe to clear
        self._do_clear_all()

    def _do_clear_all(self):
        """Actually clear the character."""
        self.current_preset = CharacterPreset(name="New Character")
        self.generated_bio = None
        self.has_unsaved_changes = False
        self.last_saved_state = None
        self._regenerate_preview()
        self.show_clear_confirmation = False
        print("✓ Character cleared")

    # === Confirmation Dialog Renderers ===

    def _render_confirmation_dialog(
        self,
        title: str,
        messages: List[str],
        yes_text: str = "Yes",
        no_text: str = "No",
        yes_attr: str = "_btn_confirm_yes",
        no_attr: str = "_btn_confirm_no",
    ):
        """Render a generic confirmation dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        dialog_width = 500
        dialog_height = 200 + (len(messages) * 20)
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        # Background
        pygame.draw.rect(self.screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 120), (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=8)

        # Title
        title_text = self.title_font.render(title, True, (255, 200, 100))
        title_rect = title_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 30))
        self.screen.blit(title_text, title_rect)

        # Messages
        message_y = dialog_y + 65
        for message in messages:
            text = self.small_font.render(message, True, (220, 220, 220))
            text_rect = text.get_rect(center=(dialog_x + dialog_width // 2, message_y))
            self.screen.blit(text, text_rect)
            message_y += 22

        # Buttons
        button_y = dialog_y + dialog_height - 50
        button_width = 120
        button_height = 35
        button_spacing = 20

        # Yes button
        yes_x = dialog_x + (dialog_width // 2) - button_width - (button_spacing // 2)
        yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (180, 100, 100), yes_rect, border_radius=5)
        pygame.draw.rect(self.screen, (220, 150, 150), yes_rect, 2, border_radius=5)
        yes_btn_text = self.font.render(yes_text, True, (255, 255, 255))
        yes_text_rect = yes_btn_text.get_rect(center=yes_rect.center)
        self.screen.blit(yes_btn_text, yes_text_rect)
        setattr(self, yes_attr, yes_rect)

        # No button
        no_x = dialog_x + (dialog_width // 2) + (button_spacing // 2)
        no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 180, 100), no_rect, border_radius=5)
        pygame.draw.rect(self.screen, (150, 220, 150), no_rect, 2, border_radius=5)
        no_btn_text = self.font.render(no_text, True, (255, 255, 255))
        no_text_rect = no_btn_text.get_rect(center=no_rect.center)
        self.screen.blit(no_btn_text, no_text_rect)
        setattr(self, no_attr, no_rect)
