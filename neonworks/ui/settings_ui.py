"""
NeonWorks Settings UI - Visual Settings Management
Provides complete visual interface for game settings (audio, input, graphics).
"""

import json
from typing import Any, Dict, List, Optional

import pygame

from ..audio.audio_manager import AudioManager
from ..core.hotkey_manager import Hotkey, HotkeyContext, get_hotkey_manager
from ..input.input_manager import InputManager
from ..rendering.ui import UI


class SettingsUI:
    """
    Visual settings panel for configuring audio, input, graphics, and gameplay.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        audio_manager: Optional[AudioManager] = None,
        input_manager: Optional[InputManager] = None,
    ):
        self.screen = screen
        self.ui = UI(screen)
        self.audio_manager = audio_manager
        self.input_manager = input_manager
        self.hotkey_manager = get_hotkey_manager()

        self.visible = False
        self.current_tab = "audio"  # 'audio', 'input', 'graphics', 'gameplay', 'shortcuts'

        # Settings data
        self.settings = {
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sfx_volume": 0.9,
                "mute_all": False,
            },
            "graphics": {
                "fullscreen": False,
                "vsync": True,
                "show_fps": True,
                "particle_density": 1.0,
                "screen_shake": True,
            },
            "input": {
                "mouse_sensitivity": 1.0,
                "invert_y": False,
            },
            "gameplay": {
                "difficulty": "normal",  # 'easy', 'normal', 'hard'
                "auto_save": True,
                "tutorial_enabled": True,
            },
        }

        # Key binding state
        self.waiting_for_key = None
        self.key_bindings = {
            "move_up": pygame.K_w,
            "move_down": pygame.K_s,
            "move_left": pygame.K_a,
            "move_right": pygame.K_d,
            "interact": pygame.K_e,
            "attack": pygame.K_SPACE,
            "menu": pygame.K_ESCAPE,
            "inventory": pygame.K_i,
            "build": pygame.K_b,
        }

        # Shortcuts rebinding state
        self.waiting_for_shortcut = None  # Hotkey being rebound
        self.waiting_for_modifier = False
        self.new_modifiers = set()

        # Shortcuts tab scroll
        self.shortcuts_scroll_offset = 0
        self.shortcuts_max_scroll = 0
        self.shortcuts_category_filter = None  # None = show all

        # Changes tracking
        self.has_unsaved_changes = False

    def toggle(self):
        """Toggle settings UI visibility."""
        self.visible = not self.visible

    def render(self):
        """Render the settings UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Main settings panel
        panel_width = 700
        panel_height = 550
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (20, 20, 30))

        # Title
        self.ui.title(
            "Settings",
            panel_x + panel_width // 2 - 50,
            panel_y + 10,
            size=28,
            color=(255, 200, 0),
        )

        # Close button
        if self.ui.button("X", panel_x + panel_width - 50, panel_y + 10, 35, 35, color=(150, 0, 0)):
            if self.has_unsaved_changes:
                # In a real implementation, show a confirmation dialog
                pass
            self.toggle()

        # Tab buttons
        self._render_tabs(panel_x, panel_y + 60, panel_width)

        # Tab content
        content_y = panel_y + 120
        content_height = panel_height - 180

        if self.current_tab == "audio":
            self._render_audio_settings(panel_x, content_y, panel_width, content_height)
        elif self.current_tab == "graphics":
            self._render_graphics_settings(panel_x, content_y, panel_width, content_height)
        elif self.current_tab == "input":
            self._render_input_settings(panel_x, content_y, panel_width, content_height)
        elif self.current_tab == "shortcuts":
            self._render_shortcuts_settings(panel_x, content_y, panel_width, content_height)
        elif self.current_tab == "gameplay":
            self._render_gameplay_settings(panel_x, content_y, panel_width, content_height)

        # Bottom buttons
        self._render_bottom_buttons(panel_x, panel_y + panel_height - 60, panel_width)

    def _render_tabs(self, x: int, y: int, width: int):
        """Render tab buttons."""
        tabs = ["audio", "graphics", "input", "shortcuts", "gameplay"]
        tab_width = width // len(tabs)

        for i, tab in enumerate(tabs):
            tab_x = x + i * tab_width
            is_active = tab == self.current_tab
            tab_color = (50, 100, 200) if is_active else (30, 30, 50)

            if self.ui.button(tab.capitalize(), tab_x + 5, y, tab_width - 10, 40, color=tab_color):
                self.current_tab = tab

    def _render_audio_settings(self, x: int, y: int, width: int, height: int):
        """Render audio settings."""
        self.ui.label("Audio Settings", x + 20, y, size=20, color=(200, 200, 255))

        current_y = y + 35

        # Master Volume
        self.ui.label("Master Volume:", x + 20, current_y, size=16)
        current_y += 25

        if self.ui.slider(
            x + 20, current_y, width - 40, 30, self.settings["audio"]["master_volume"]
        ):
            # Update master volume
            mouse_x = pygame.mouse.get_pos()[0]
            slider_x = mouse_x - x - 20
            self.settings["audio"]["master_volume"] = max(0, min(1, slider_x / (width - 40)))
            self.has_unsaved_changes = True

            if self.audio_manager:
                self.audio_manager.set_master_volume(self.settings["audio"]["master_volume"])

        self.ui.label(
            f"{int(self.settings['audio']['master_volume'] * 100)}%",
            x + width - 60,
            current_y + 5,
            size=16,
        )
        current_y += 50

        # Music Volume
        self.ui.label("Music Volume:", x + 20, current_y, size=16)
        current_y += 25

        if self.ui.slider(
            x + 20, current_y, width - 40, 30, self.settings["audio"]["music_volume"]
        ):
            mouse_x = pygame.mouse.get_pos()[0]
            slider_x = mouse_x - x - 20
            self.settings["audio"]["music_volume"] = max(0, min(1, slider_x / (width - 40)))
            self.has_unsaved_changes = True

            if self.audio_manager:
                self.audio_manager.set_music_volume(self.settings["audio"]["music_volume"])

        self.ui.label(
            f"{int(self.settings['audio']['music_volume'] * 100)}%",
            x + width - 60,
            current_y + 5,
            size=16,
        )
        current_y += 50

        # SFX Volume
        self.ui.label("SFX Volume:", x + 20, current_y, size=16)
        current_y += 25

        if self.ui.slider(x + 20, current_y, width - 40, 30, self.settings["audio"]["sfx_volume"]):
            mouse_x = pygame.mouse.get_pos()[0]
            slider_x = mouse_x - x - 20
            self.settings["audio"]["sfx_volume"] = max(0, min(1, slider_x / (width - 40)))
            self.has_unsaved_changes = True

        self.ui.label(
            f"{int(self.settings['audio']['sfx_volume'] * 100)}%",
            x + width - 60,
            current_y + 5,
            size=16,
        )
        current_y += 50

        # Mute All
        mute_color = (150, 0, 0) if self.settings["audio"]["mute_all"] else (0, 100, 0)
        mute_text = "Unmute All" if self.settings["audio"]["mute_all"] else "Mute All"

        if self.ui.button(mute_text, x + 20, current_y, 200, 40, color=mute_color):
            self.settings["audio"]["mute_all"] = not self.settings["audio"]["mute_all"]
            self.has_unsaved_changes = True

    def _render_graphics_settings(self, x: int, y: int, width: int, height: int):
        """Render graphics settings."""
        self.ui.label("Graphics Settings", x + 20, y, size=20, color=(200, 200, 255))

        current_y = y + 35

        # Fullscreen toggle
        fullscreen_text = (
            "Fullscreen: ON" if self.settings["graphics"]["fullscreen"] else "Fullscreen: OFF"
        )
        fullscreen_color = (0, 150, 0) if self.settings["graphics"]["fullscreen"] else (150, 0, 0)

        if self.ui.button(fullscreen_text, x + 20, current_y, 300, 40, color=fullscreen_color):
            self.settings["graphics"]["fullscreen"] = not self.settings["graphics"]["fullscreen"]
            self.has_unsaved_changes = True
            # Toggle fullscreen
            if self.settings["graphics"]["fullscreen"]:
                pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((1280, 720))

        current_y += 50

        # VSync toggle
        vsync_text = "VSync: ON" if self.settings["graphics"]["vsync"] else "VSync: OFF"
        vsync_color = (0, 150, 0) if self.settings["graphics"]["vsync"] else (150, 0, 0)

        if self.ui.button(vsync_text, x + 20, current_y, 300, 40, color=vsync_color):
            self.settings["graphics"]["vsync"] = not self.settings["graphics"]["vsync"]
            self.has_unsaved_changes = True

        current_y += 50

        # Show FPS toggle
        fps_text = "Show FPS: ON" if self.settings["graphics"]["show_fps"] else "Show FPS: OFF"
        fps_color = (0, 150, 0) if self.settings["graphics"]["show_fps"] else (150, 0, 0)

        if self.ui.button(fps_text, x + 20, current_y, 300, 40, color=fps_color):
            self.settings["graphics"]["show_fps"] = not self.settings["graphics"]["show_fps"]
            self.has_unsaved_changes = True

        current_y += 50

        # Particle Density
        self.ui.label("Particle Density:", x + 20, current_y, size=16)
        current_y += 25

        if self.ui.slider(
            x + 20,
            current_y,
            width - 40,
            30,
            self.settings["graphics"]["particle_density"],
        ):
            mouse_x = pygame.mouse.get_pos()[0]
            slider_x = mouse_x - x - 20
            self.settings["graphics"]["particle_density"] = max(0, min(1, slider_x / (width - 40)))
            self.has_unsaved_changes = True

        density_pct = int(self.settings["graphics"]["particle_density"] * 100)
        self.ui.label(f"{density_pct}%", x + width - 60, current_y + 5, size=16)
        current_y += 50

        # Screen Shake toggle
        shake_text = (
            "Screen Shake: ON" if self.settings["graphics"]["screen_shake"] else "Screen Shake: OFF"
        )
        shake_color = (0, 150, 0) if self.settings["graphics"]["screen_shake"] else (150, 0, 0)

        if self.ui.button(shake_text, x + 20, current_y, 300, 40, color=shake_color):
            self.settings["graphics"]["screen_shake"] = not self.settings["graphics"][
                "screen_shake"
            ]
            self.has_unsaved_changes = True

    def _render_input_settings(self, x: int, y: int, width: int, height: int):
        """Render input settings and key bindings."""
        self.ui.label("Input Settings", x + 20, y, size=20, color=(200, 200, 255))

        current_y = y + 35

        # Mouse Sensitivity
        self.ui.label("Mouse Sensitivity:", x + 20, current_y, size=16)
        current_y += 25

        if self.ui.slider(
            x + 20,
            current_y,
            width - 40,
            30,
            (self.settings["input"]["mouse_sensitivity"] - 0.5) / 1.5,
        ):
            mouse_x = pygame.mouse.get_pos()[0]
            slider_x = mouse_x - x - 20
            normalized = max(0, min(1, slider_x / (width - 40)))
            self.settings["input"]["mouse_sensitivity"] = 0.5 + normalized * 1.5
            self.has_unsaved_changes = True

        self.ui.label(
            f"{self.settings['input']['mouse_sensitivity']:.2f}x",
            x + width - 80,
            current_y + 5,
            size=16,
        )
        current_y += 50

        # Invert Y axis
        invert_text = (
            "Invert Y-Axis: ON" if self.settings["input"]["invert_y"] else "Invert Y-Axis: OFF"
        )
        invert_color = (0, 150, 0) if self.settings["input"]["invert_y"] else (150, 0, 0)

        if self.ui.button(invert_text, x + 20, current_y, 300, 40, color=invert_color):
            self.settings["input"]["invert_y"] = not self.settings["input"]["invert_y"]
            self.has_unsaved_changes = True

        current_y += 60

        # Key Bindings
        self.ui.label("Key Bindings:", x + 20, current_y, size=18, color=(200, 200, 255))
        current_y += 30

        for action, key in self.key_bindings.items():
            key_name = pygame.key.name(key)
            action_label = action.replace("_", " ").title()

            self.ui.label(f"{action_label}:", x + 30, current_y, size=14)

            # Key button
            is_waiting = self.waiting_for_key == action
            button_color = (255, 200, 0) if is_waiting else (50, 50, 80)
            button_text = "Press Key..." if is_waiting else key_name

            if self.ui.button(button_text, x + 250, current_y - 5, 150, 30, color=button_color):
                self.waiting_for_key = action

            current_y += 35

    def _render_shortcuts_settings(self, x: int, y: int, width: int, height: int):
        """Render keyboard shortcuts settings."""
        self.ui.label("Keyboard Shortcuts", x + 20, y, size=20, color=(200, 200, 255))

        # Category filter buttons
        filter_y = y + 30
        categories = ["All"] + self.hotkey_manager.get_categories()
        button_width = 100
        button_spacing = 5

        for i, category in enumerate(categories[:6]):  # Show first 6 categories
            button_x = x + 20 + i * (button_width + button_spacing)
            is_active = (category == "All" and self.shortcuts_category_filter is None) or (
                category == self.shortcuts_category_filter
            )
            button_color = (50, 100, 200) if is_active else (30, 30, 50)

            if self.ui.button(category, button_x, filter_y, button_width, 30, color=button_color):
                self.shortcuts_category_filter = None if category == "All" else category
                self.shortcuts_scroll_offset = 0

        # Reset to defaults button
        if self.ui.button("Reset All", x + width - 120, filter_y, 100, 30, color=(150, 100, 0)):
            self.hotkey_manager.reset_to_defaults()
            self.has_unsaved_changes = True

        # Scrollable shortcuts list
        list_y = filter_y + 40
        list_height = height - 80

        # Create clipping rect for scrolling
        clip_rect = pygame.Rect(x + 10, list_y, width - 20, list_height)
        original_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        current_y = list_y - self.shortcuts_scroll_offset

        # Get hotkeys grouped by category
        if self.shortcuts_category_filter:
            hotkeys = self.hotkey_manager.get_hotkeys_by_category(self.shortcuts_category_filter)
            categories_to_show = {self.shortcuts_category_filter: hotkeys}
        else:
            categories_to_show = {}
            for category in self.hotkey_manager.get_categories():
                hotkeys = self.hotkey_manager.get_hotkeys_by_category(category)
                if hotkeys:
                    categories_to_show[category] = hotkeys

        # Render each category
        for category, hotkeys in categories_to_show.items():
            # Category header
            if current_y >= list_y - 30 and current_y <= list_y + list_height:
                self.ui.label(category, x + 25, current_y, size=16, color=(255, 200, 100))
            current_y += 25

            # Hotkeys in category
            for hotkey in hotkeys:
                if current_y >= list_y - 40 and current_y <= list_y + list_height:
                    self._render_shortcut_row(
                        x + 35, current_y, width - 70, hotkey, list_y, list_height
                    )
                current_y += 35

            current_y += 10  # Spacing between categories

        # Calculate max scroll
        total_height = current_y - (list_y - self.shortcuts_scroll_offset)
        self.shortcuts_max_scroll = max(0, total_height - list_height)

        # Restore clip
        self.screen.set_clip(original_clip)

        # Scroll indicator
        if self.shortcuts_max_scroll > 0:
            self._render_scroll_indicator(
                x + width - 15, list_y, 10, list_height, self.shortcuts_scroll_offset
            )

        # Footer help text
        footer_y = list_y + list_height + 5
        if self.waiting_for_shortcut:
            self.ui.label(
                f"Press new key for '{self.waiting_for_shortcut.description}'... (ESC to cancel)",
                x + 20,
                footer_y,
                size=14,
                color=(255, 200, 0),
            )
        else:
            self.ui.label(
                "Click on a shortcut to rebind it | Use mouse wheel to scroll",
                x + 20,
                footer_y,
                size=12,
                color=(150, 150, 150),
            )

    def _render_shortcut_row(
        self, x: int, y: int, width: int, hotkey: Hotkey, clip_y: int, clip_height: int
    ):
        """Render a single shortcut row."""
        # Description (left side)
        self.ui.label(hotkey.description, x, y, size=14, color=(200, 200, 200))

        # Shortcut button (right side)
        button_width = 200
        button_x = x + width - button_width
        is_waiting = self.waiting_for_shortcut == hotkey
        button_color = (255, 200, 0) if is_waiting else (50, 50, 80)
        button_text = "Press Key..." if is_waiting else hotkey.get_display_name()

        if self.ui.button(button_text, button_x, y - 5, button_width, 30, color=button_color):
            self.waiting_for_shortcut = hotkey
            self.new_modifiers = set()

        # Context indicator (small badge)
        if hotkey.context != HotkeyContext.GLOBAL:
            context_text = hotkey.context.value.capitalize()
            context_x = button_x - 80
            self.ui.label(f"[{context_text}]", context_x, y, size=12, color=(150, 150, 150))

    def _render_scroll_indicator(self, x: int, y: int, width: int, height: int, scroll_offset: int):
        """Render a scroll indicator."""
        max_scroll = self.shortcuts_max_scroll
        if max_scroll <= 0:
            return

        # Background track
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height))

        # Scrollbar handle
        handle_height = max(20, height * height // (height + max_scroll))
        handle_y = y + (scroll_offset / max_scroll) * (height - handle_height)

        pygame.draw.rect(
            self.screen, (100, 100, 150), (x, int(handle_y), width, int(handle_height))
        )

    def _render_gameplay_settings(self, x: int, y: int, width: int, height: int):
        """Render gameplay settings."""
        self.ui.label("Gameplay Settings", x + 20, y, size=20, color=(200, 200, 255))

        current_y = y + 35

        # Difficulty
        self.ui.label("Difficulty:", x + 20, current_y, size=16)
        current_y += 30

        difficulties = ["easy", "normal", "hard"]
        for difficulty in difficulties:
            is_selected = self.settings["gameplay"]["difficulty"] == difficulty
            diff_color = (0, 150, 0) if is_selected else (50, 50, 80)

            if self.ui.button(
                difficulty.capitalize(), x + 30, current_y, 150, 35, color=diff_color
            ):
                self.settings["gameplay"]["difficulty"] = difficulty
                self.has_unsaved_changes = True

            current_y += 40

        current_y += 20

        # Auto-save
        auto_save_text = (
            "Auto-Save: ON" if self.settings["gameplay"]["auto_save"] else "Auto-Save: OFF"
        )
        auto_save_color = (0, 150, 0) if self.settings["gameplay"]["auto_save"] else (150, 0, 0)

        if self.ui.button(auto_save_text, x + 20, current_y, 300, 40, color=auto_save_color):
            self.settings["gameplay"]["auto_save"] = not self.settings["gameplay"]["auto_save"]
            self.has_unsaved_changes = True

        current_y += 50

        # Tutorial
        tutorial_text = (
            "Tutorial: ON" if self.settings["gameplay"]["tutorial_enabled"] else "Tutorial: OFF"
        )
        tutorial_color = (
            (0, 150, 0) if self.settings["gameplay"]["tutorial_enabled"] else (150, 0, 0)
        )

        if self.ui.button(tutorial_text, x + 20, current_y, 300, 40, color=tutorial_color):
            self.settings["gameplay"]["tutorial_enabled"] = not self.settings["gameplay"][
                "tutorial_enabled"
            ]
            self.has_unsaved_changes = True

    def _render_bottom_buttons(self, x: int, y: int, width: int):
        """Render save, apply, and cancel buttons."""
        button_width = 150
        button_spacing = 20

        # Save button
        if self.ui.button("Save & Close", x + 20, y, button_width, 40, color=(0, 150, 0)):
            self.save_settings()
            self.toggle()

        # Apply button
        if self.ui.button(
            "Apply",
            x + 20 + button_width + button_spacing,
            y,
            button_width,
            40,
            color=(0, 100, 200),
        ):
            self.apply_settings()

        # Cancel button
        if self.ui.button(
            "Cancel",
            x + 20 + (button_width + button_spacing) * 2,
            y,
            button_width,
            40,
            color=(150, 0, 0),
        ):
            self.toggle()

        # Reset to defaults
        if self.ui.button(
            "Reset to Defaults",
            x + width - button_width - 20,
            y,
            button_width,
            40,
            color=(150, 100, 0),
        ):
            self.reset_to_defaults()

    def handle_key_press(self, key: int):
        """Handle key press for key binding and shortcut rebinding."""
        # Handle legacy key bindings
        if self.waiting_for_key:
            self.key_bindings[self.waiting_for_key] = key
            self.waiting_for_key = None
            self.has_unsaved_changes = True
            return

        # Handle shortcut rebinding
        if self.waiting_for_shortcut:
            # Cancel on Escape
            if key == pygame.K_ESCAPE:
                self.waiting_for_shortcut = None
                self.new_modifiers = set()
                return

            # Get modifiers
            mods = pygame.key.get_mods()
            new_modifiers = set()
            if mods & pygame.KMOD_CTRL:
                new_modifiers.add("ctrl")
            if mods & pygame.KMOD_SHIFT:
                new_modifiers.add("shift")
            if mods & pygame.KMOD_ALT:
                new_modifiers.add("alt")

            # Rebind the hotkey
            self.hotkey_manager.rebind(self.waiting_for_shortcut.action, key, new_modifiers)
            self.waiting_for_shortcut = None
            self.new_modifiers = set()
            self.has_unsaved_changes = True

    def handle_mouse_wheel(self, y: int):
        """
        Handle mouse wheel scrolling.

        Args:
            y: Scroll direction (positive = up, negative = down)
        """
        if self.current_tab == "shortcuts":
            scroll_speed = 30
            self.shortcuts_scroll_offset -= y * scroll_speed
            self.shortcuts_scroll_offset = max(
                0, min(self.shortcuts_scroll_offset, self.shortcuts_max_scroll)
            )

    def save_settings(self):
        """Save settings to file."""
        settings_data = {
            "settings": self.settings,
            "key_bindings": {k: v for k, v in self.key_bindings.items()},
        }

        try:
            with open("settings.json", "w") as f:
                json.dump(settings_data, f, indent=2)

            # Save hotkey configuration separately
            self.hotkey_manager.save_config()

            self.has_unsaved_changes = False
            print("Settings saved successfully")
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self):
        """Load settings from file."""
        try:
            with open("settings.json", "r") as f:
                settings_data = json.load(f)
                self.settings = settings_data.get("settings", self.settings)
                self.key_bindings = {
                    k: int(v) for k, v in settings_data.get("key_bindings", {}).items()
                }

            # Load hotkey configuration separately
            self.hotkey_manager.load_config()

            print("Settings loaded successfully")
        except FileNotFoundError:
            print("No settings file found, using defaults")
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def apply_settings(self):
        """Apply settings without saving."""
        # Apply audio settings
        if self.audio_manager:
            self.audio_manager.set_master_volume(self.settings["audio"]["master_volume"])
            self.audio_manager.set_music_volume(self.settings["audio"]["music_volume"])

        # Apply graphics settings
        # (These would be applied in the main game loop)

        print("Settings applied")

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = {
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sfx_volume": 0.9,
                "mute_all": False,
            },
            "graphics": {
                "fullscreen": False,
                "vsync": True,
                "show_fps": True,
                "particle_density": 1.0,
                "screen_shake": True,
            },
            "input": {
                "mouse_sensitivity": 1.0,
                "invert_y": False,
            },
            "gameplay": {
                "difficulty": "normal",
                "auto_save": True,
                "tutorial_enabled": True,
            },
        }

        self.key_bindings = {
            "move_up": pygame.K_w,
            "move_down": pygame.K_s,
            "move_left": pygame.K_a,
            "move_right": pygame.K_d,
            "interact": pygame.K_e,
            "attack": pygame.K_SPACE,
            "menu": pygame.K_ESCAPE,
            "inventory": pygame.K_i,
            "build": pygame.K_b,
        }

        # Reset hotkeys
        self.hotkey_manager.reset_to_defaults()

        self.has_unsaved_changes = True
        print("Settings reset to defaults")
