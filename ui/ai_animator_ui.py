"""
AI Animator UI

Visual interface for AI-powered sprite animation generation.
Allows users to upload sprites, describe animations in natural language,
preview results, and export frames.
"""

from pathlib import Path
from typing import List, Optional

import pygame

from neonworks.editor.ai_animation_interpreter import AnimationIntent, AnimationInterpreter
from neonworks.editor.ai_animator import AIAnimator, AnimationType
from neonworks.ui.ui_system import Button, Label, Panel, TextInput


class AIAnimatorUI:
    """
    Visual editor for AI animation generation.

    Hotkey: F11 (to be added to MasterUIManager)

    Features:
    - Upload or select sprites
    - Natural language animation requests
    - Live preview with playback controls
    - Animation refinement tools
    - Export to frames or sprite sheets
    """

    def __init__(self, world, renderer):
        """Initialize AI animator UI"""
        self.world = world
        self.renderer = renderer
        self.visible = False

        # AI components
        self.animator = AIAnimator(model_type="local")
        self.interpreter = AnimationInterpreter(model_type="local")

        # State
        self.current_sprite: Optional[pygame.Surface] = None
        self.current_sprite_path: Optional[Path] = None
        self.current_animation_frames: List[pygame.Surface] = []
        self.current_intent: Optional[AnimationIntent] = None
        self.preview_frame_index = 0
        self.preview_playing = False
        self.preview_timer = 0.0
        self.preview_fps = 10.0

        # UI Layout
        self.panel_width = 900
        self.panel_height = 700
        self.panel_x = 50
        self.panel_y = 50

        # Create UI panels
        self._create_ui_panels()

    def _create_ui_panels(self):
        """Create all UI panels and widgets"""
        # Main panel
        self.main_panel = Panel(
            x=self.panel_x, y=self.panel_y, width=self.panel_width, height=self.panel_height
        )

        # Title
        self.title_label = Label(
            text="AI Animation Generator", x=self.panel_x + 20, y=self.panel_y + 20
        )

        # --- Left Column: Input ---

        # Sprite selection section
        self.sprite_label = Label(
            text="1. Select Sprite:", x=self.panel_x + 20, y=self.panel_y + 60
        )

        self.upload_sprite_btn = Button(
            text="Upload Sprite",
            x=self.panel_x + 20,
            y=self.panel_y + 90,
            width=200,
            height=30,
            on_click=self._on_upload_sprite,
        )

        self.browse_components_btn = Button(
            text="Browse Components",
            x=self.panel_x + 230,
            y=self.panel_y + 90,
            width=200,
            height=30,
            on_click=self._on_browse_components,
        )

        self.sprite_info_label = Label(
            text="No sprite selected",
            x=self.panel_x + 20,
            y=self.panel_y + 130,
            color=(150, 150, 150),
        )

        # Animation request section
        self.request_label = Label(
            text="2. Describe Animation:", x=self.panel_x + 20, y=self.panel_y + 180
        )

        self.request_input = TextInput(
            x=self.panel_x + 20,
            y=self.panel_y + 210,
            width=400,
            height=80,
            placeholder="E.g., 'Make character walk slowly like they're tired'\nor select a preset below...",
        )

        # Preset buttons
        self.preset_label = Label(
            text="Quick Presets:", x=self.panel_x + 20, y=self.panel_y + 310
        )

        preset_y = self.panel_y + 340
        preset_spacing = 35
        self.preset_buttons = []

        presets = [
            ("Idle", "idle"),
            ("Walk", "walk"),
            ("Run", "run"),
            ("Attack", "attack"),
            ("Cast Spell", "cast_spell"),
            ("Jump", "jump"),
        ]

        for i, (label, anim_type) in enumerate(presets):
            row = i // 3
            col = i % 3
            btn = Button(
                text=label,
                x=self.panel_x + 20 + col * 140,
                y=preset_y + row * preset_spacing,
                width=130,
                height=25,
                on_click=lambda at=anim_type: self._on_preset_selected(at),
            )
            self.preset_buttons.append(btn)

        # Generate button
        self.generate_btn = Button(
            text="Generate Animation",
            x=self.panel_x + 20,
            y=self.panel_y + 450,
            width=200,
            height=40,
            on_click=self._on_generate,
            color=(50, 150, 50),
        )

        self.generate_status_label = Label(
            text="", x=self.panel_x + 230, y=self.panel_y + 465, color=(100, 200, 100)
        )

        # Advanced options
        self.advanced_label = Label(
            text="Advanced Options:", x=self.panel_x + 20, y=self.panel_y + 510
        )

        self.intensity_label = Label(
            text="Intensity:", x=self.panel_x + 20, y=self.panel_y + 540
        )

        self.speed_label = Label(
            text="Speed:", x=self.panel_x + 220, y=self.panel_y + 540
        )

        # TODO: Add sliders for intensity and speed

        # --- Right Column: Preview ---

        preview_x = self.panel_x + 470
        preview_y = self.panel_y + 60

        self.preview_label = Label(text="Preview:", x=preview_x, y=preview_y)

        # Preview canvas
        self.preview_canvas_x = preview_x
        self.preview_canvas_y = preview_y + 30
        self.preview_canvas_width = 400
        self.preview_canvas_height = 300

        # Playback controls
        controls_y = self.preview_canvas_y + self.preview_canvas_height + 20

        self.play_btn = Button(
            text="Play",
            x=preview_x,
            y=controls_y,
            width=80,
            height=30,
            on_click=self._on_play,
        )

        self.pause_btn = Button(
            text="Pause",
            x=preview_x + 90,
            y=controls_y,
            width=80,
            height=30,
            on_click=self._on_pause,
        )

        self.prev_frame_btn = Button(
            text="◀",
            x=preview_x + 180,
            y=controls_y,
            width=40,
            height=30,
            on_click=self._on_prev_frame,
        )

        self.next_frame_btn = Button(
            text="▶",
            x=preview_x + 230,
            y=controls_y,
            width=40,
            height=30,
            on_click=self._on_next_frame,
        )

        self.frame_info_label = Label(
            text="Frame: 0/0", x=preview_x + 280, y=controls_y + 7, color=(150, 150, 150)
        )

        # Export section
        export_y = controls_y + 60

        self.export_label = Label(text="Export:", x=preview_x, y=export_y)

        self.export_frames_btn = Button(
            text="Export Frames",
            x=preview_x,
            y=export_y + 30,
            width=190,
            height=35,
            on_click=self._on_export_frames,
        )

        self.export_sheet_btn = Button(
            text="Export Sprite Sheet",
            x=preview_x + 200,
            y=export_y + 30,
            width=190,
            height=35,
            on_click=self._on_export_sheet,
        )

        # Refinement section
        refine_y = export_y + 90

        self.refine_label = Label(text="Refine Animation:", x=preview_x, y=refine_y)

        self.refine_input = TextInput(
            x=preview_x,
            y=refine_y + 30,
            width=390,
            height=50,
            placeholder="E.g., 'make it slower' or 'more intense'",
        )

        self.refine_btn = Button(
            text="Apply Refinement",
            x=preview_x,
            y=refine_y + 90,
            width=190,
            height=30,
            on_click=self._on_refine,
        )

        # Suggestions section
        suggest_y = refine_y + 140

        self.suggest_label = Label(text="Suggested Animations:", x=preview_x, y=suggest_y)

        self.suggestions_text = Label(
            text="Load a sprite to see suggestions",
            x=preview_x,
            y=suggest_y + 30,
            color=(150, 150, 150),
        )

        # Close button
        self.close_btn = Button(
            text="Close",
            x=self.panel_x + self.panel_width - 100,
            y=self.panel_y + 20,
            width=80,
            height=30,
            on_click=self.close,
        )

    def update(self, dt: float):
        """Update UI and preview animation"""
        if not self.visible:
            return

        # Update preview animation
        if self.preview_playing and self.current_animation_frames:
            self.preview_timer += dt

            frame_duration = 1.0 / self.preview_fps
            if self.preview_timer >= frame_duration:
                self.preview_timer = 0.0
                self.preview_frame_index = (self.preview_frame_index + 1) % len(
                    self.current_animation_frames
                )
                self._update_frame_info()

        # Update UI elements
        self.main_panel.update(dt)
        self.upload_sprite_btn.update(dt)
        self.browse_components_btn.update(dt)
        self.request_input.update(dt)

        for btn in self.preset_buttons:
            btn.update(dt)

        self.generate_btn.update(dt)
        self.play_btn.update(dt)
        self.pause_btn.update(dt)
        self.prev_frame_btn.update(dt)
        self.next_frame_btn.update(dt)
        self.export_frames_btn.update(dt)
        self.export_sheet_btn.update(dt)
        self.refine_input.update(dt)
        self.refine_btn.update(dt)
        self.close_btn.update(dt)

    def render(self, screen: pygame.Surface):
        """Render UI"""
        if not self.visible:
            return

        # Main panel
        self.main_panel.render(screen)

        # Labels
        self.title_label.render(screen)
        self.sprite_label.render(screen)
        self.sprite_info_label.render(screen)
        self.request_label.render(screen)
        self.preset_label.render(screen)
        self.generate_status_label.render(screen)
        self.advanced_label.render(screen)
        self.intensity_label.render(screen)
        self.speed_label.render(screen)
        self.preview_label.render(screen)
        self.frame_info_label.render(screen)
        self.export_label.render(screen)
        self.refine_label.render(screen)
        self.suggest_label.render(screen)
        self.suggestions_text.render(screen)

        # Buttons
        self.upload_sprite_btn.render(screen)
        self.browse_components_btn.render(screen)
        self.request_input.render(screen)

        for btn in self.preset_buttons:
            btn.render(screen)

        self.generate_btn.render(screen)
        self.play_btn.render(screen)
        self.pause_btn.render(screen)
        self.prev_frame_btn.render(screen)
        self.next_frame_btn.render(screen)
        self.export_frames_btn.render(screen)
        self.export_sheet_btn.render(screen)
        self.refine_input.render(screen)
        self.refine_btn.render(screen)
        self.close_btn.render(screen)

        # Preview canvas
        self._render_preview_canvas(screen)

        # Source sprite thumbnail
        if self.current_sprite:
            self._render_sprite_thumbnail(screen)

    def _render_preview_canvas(self, screen: pygame.Surface):
        """Render the animation preview canvas"""
        # Draw canvas border
        canvas_rect = pygame.Rect(
            self.preview_canvas_x,
            self.preview_canvas_y,
            self.preview_canvas_width,
            self.preview_canvas_height,
        )
        pygame.draw.rect(screen, (50, 50, 50), canvas_rect)
        pygame.draw.rect(screen, (100, 100, 100), canvas_rect, 2)

        # Draw checkerboard background
        self._draw_checkerboard(screen, canvas_rect)

        # Draw current frame
        if self.current_animation_frames:
            frame = self.current_animation_frames[self.preview_frame_index]

            # Center frame in canvas
            frame_x = self.preview_canvas_x + (self.preview_canvas_width - frame.get_width()) // 2
            frame_y = self.preview_canvas_y + (self.preview_canvas_height - frame.get_height()) // 2

            # Scale up if sprite is small
            scale_factor = min(
                self.preview_canvas_width / frame.get_width(),
                self.preview_canvas_height / frame.get_height(),
            )

            if scale_factor > 1:
                # Scale up using nearest neighbor for pixel art
                scaled_width = int(frame.get_width() * scale_factor * 0.8)
                scaled_height = int(frame.get_height() * scale_factor * 0.8)
                scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))

                frame_x = self.preview_canvas_x + (self.preview_canvas_width - scaled_width) // 2
                frame_y = self.preview_canvas_y + (self.preview_canvas_height - scaled_height) // 2

                screen.blit(scaled_frame, (frame_x, frame_y))
            else:
                screen.blit(frame, (frame_x, frame_y))

    def _render_sprite_thumbnail(self, screen: pygame.Surface):
        """Render source sprite thumbnail"""
        thumb_x = self.panel_x + 20
        thumb_y = self.panel_y + 155

        # Thumbnail background
        thumb_rect = pygame.Rect(thumb_x, thumb_y, 64, 64)
        pygame.draw.rect(screen, (40, 40, 40), thumb_rect)
        pygame.draw.rect(screen, (100, 100, 100), thumb_rect, 1)

        # Draw sprite (scaled to fit)
        if self.current_sprite:
            scale = min(60 / self.current_sprite.get_width(), 60 / self.current_sprite.get_height())
            thumb = pygame.transform.scale(
                self.current_sprite,
                (
                    int(self.current_sprite.get_width() * scale),
                    int(self.current_sprite.get_height() * scale),
                ),
            )
            sprite_x = thumb_x + (64 - thumb.get_width()) // 2
            sprite_y = thumb_y + (64 - thumb.get_height()) // 2
            screen.blit(thumb, (sprite_x, sprite_y))

    def _draw_checkerboard(self, screen: pygame.Surface, rect: pygame.Rect):
        """Draw checkerboard pattern for transparency"""
        tile_size = 16
        color1 = (60, 60, 60)
        color2 = (70, 70, 70)

        for y in range(rect.top, rect.bottom, tile_size):
            for x in range(rect.left, rect.right, tile_size):
                row = (y - rect.top) // tile_size
                col = (x - rect.left) // tile_size
                color = color1 if (row + col) % 2 == 0 else color2

                tile_rect = pygame.Rect(
                    x, y, min(tile_size, rect.right - x), min(tile_size, rect.bottom - y)
                )
                pygame.draw.rect(screen, color, tile_rect)

    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        if not self.visible:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return

        # Pass to UI elements
        self.upload_sprite_btn.handle_event(event)
        self.browse_components_btn.handle_event(event)
        self.request_input.handle_event(event)

        for btn in self.preset_buttons:
            btn.handle_event(event)

        self.generate_btn.handle_event(event)
        self.play_btn.handle_event(event)
        self.pause_btn.handle_event(event)
        self.prev_frame_btn.handle_event(event)
        self.next_frame_btn.handle_event(event)
        self.export_frames_btn.handle_event(event)
        self.export_sheet_btn.handle_event(event)
        self.refine_input.handle_event(event)
        self.refine_btn.handle_event(event)
        self.close_btn.handle_event(event)

    # --- Event Handlers ---

    def _on_upload_sprite(self):
        """Handle sprite upload"""
        # TODO: Implement file picker dialog
        print("[AI Animator] Upload sprite clicked")
        # For now, load a test sprite
        # self.current_sprite = pygame.image.load("assets/characters/test.png")
        # self._update_sprite_info()

    def _on_browse_components(self):
        """Browse character generator components"""
        # TODO: Open component browser
        print("[AI Animator] Browse components clicked")

    def _on_preset_selected(self, animation_type: str):
        """Handle preset selection"""
        self.request_input.set_text(animation_type)
        print(f"[AI Animator] Preset selected: {animation_type}")

    def _on_generate(self):
        """Generate animation from request"""
        if not self.current_sprite:
            self.generate_status_label.set_text("❌ Please select a sprite first")
            return

        request = self.request_input.get_text()
        if not request:
            self.generate_status_label.set_text("❌ Please describe the animation")
            return

        self.generate_status_label.set_text("🔄 Generating...")

        # Interpret request
        self.current_intent = self.interpreter.interpret_request(request)

        # Convert to config
        config = self.interpreter.intent_to_config(self.current_intent)

        # Generate animation
        self.current_animation_frames = self.animator.generate_animation(
            self.current_sprite, config, component_id=None
        )

        # Reset preview
        self.preview_frame_index = 0
        self.preview_playing = True
        self._update_frame_info()

        self.generate_status_label.set_text(f"✓ Generated {len(self.current_animation_frames)} frames")

    def _on_play(self):
        """Play animation preview"""
        self.preview_playing = True

    def _on_pause(self):
        """Pause animation preview"""
        self.preview_playing = False

    def _on_prev_frame(self):
        """Go to previous frame"""
        if self.current_animation_frames:
            self.preview_frame_index = (
                self.preview_frame_index - 1
            ) % len(self.current_animation_frames)
            self._update_frame_info()

    def _on_next_frame(self):
        """Go to next frame"""
        if self.current_animation_frames:
            self.preview_frame_index = (
                self.preview_frame_index + 1
            ) % len(self.current_animation_frames)
            self._update_frame_info()

    def _on_export_frames(self):
        """Export animation as individual frames"""
        if not self.current_animation_frames:
            return

        # TODO: Add file dialog for output directory
        output_dir = Path("output/animations/frames")
        component_id = "custom_sprite"
        animation_type = self.current_intent.animation_type if self.current_intent else "animation"

        self.animator.export_animation_frames(
            self.current_animation_frames, output_dir, component_id, animation_type
        )

        print(f"[AI Animator] Exported {len(self.current_animation_frames)} frames")

    def _on_export_sheet(self):
        """Export animation as sprite sheet"""
        if not self.current_animation_frames:
            return

        # TODO: Add file dialog for output path
        output_path = Path("output/animations/sprite_sheet.png")

        self.animator.export_sprite_sheet(
            self.current_animation_frames, output_path, layout="horizontal"
        )

        print(f"[AI Animator] Exported sprite sheet: {output_path}")

    def _on_refine(self):
        """Refine animation based on feedback"""
        if not self.current_intent:
            return

        feedback = self.refine_input.get_text()
        if not feedback:
            return

        # Refine intent
        self.current_intent = self.interpreter.refine_intent(self.current_intent, feedback)

        # Regenerate
        config = self.interpreter.intent_to_config(self.current_intent)
        self.current_animation_frames = self.animator.generate_animation(
            self.current_sprite, config, component_id=None
        )

        # Reset preview
        self.preview_frame_index = 0
        self._update_frame_info()

        print(f"[AI Animator] Refined animation based on: {feedback}")

    def _update_frame_info(self):
        """Update frame counter label"""
        if self.current_animation_frames:
            self.frame_info_label.set_text(
                f"Frame: {self.preview_frame_index + 1}/{len(self.current_animation_frames)}"
            )
        else:
            self.frame_info_label.set_text("Frame: 0/0")

    def _update_sprite_info(self):
        """Update sprite info label"""
        if self.current_sprite:
            w, h = self.current_sprite.get_size()
            filename = self.current_sprite_path.name if self.current_sprite_path else "Unknown"
            self.sprite_info_label.set_text(f"Loaded: {filename} ({w}x{h}px)")

            # Generate suggestions
            sprite_info = {"type": "character", "class": "warrior"}
            suggestions = self.interpreter.suggest_animations(sprite_info)

            suggestions_text = "\n".join([f"• {name}: {desc}" for name, desc in suggestions[:3]])
            self.suggestions_text.set_text(suggestions_text)
        else:
            self.sprite_info_label.set_text("No sprite selected")

    def toggle(self):
        """Toggle visibility"""
        self.visible = not self.visible

    def close(self):
        """Close editor"""
        self.visible = False


# Integration with MasterUIManager
"""
To integrate this UI into MasterUIManager:

1. Add to __init__:
    from neonworks.ui.ai_animator_ui import AIAnimatorUI
    self.ai_animator = AIAnimatorUI(world, renderer)

2. Add hotkey to handle_event:
    if event.key == pygame.K_F11:
        self.ai_animator.toggle()

3. Add to update:
    self.ai_animator.update(dt)

4. Add to render:
    self.ai_animator.render(screen)

5. Add to handle_event passthrough:
    self.ai_animator.handle_event(event)
"""
