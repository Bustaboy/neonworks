"""
NeonWorks Settings UI - Visual Settings Management
Provides complete visual interface for game settings (audio, input, graphics).
"""

from typing import Optional, Dict, Any, List
import pygame
import json
from ..rendering.ui import UI
from ..audio.audio_manager import AudioManager
from ..input.input_manager import InputManager


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

        self.visible = False
        self.current_tab = "audio"  # 'audio', 'input', 'graphics', 'gameplay'

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
        if self.ui.button(
            "X", panel_x + panel_width - 50, panel_y + 10, 35, 35, color=(150, 0, 0)
        ):
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
            self._render_graphics_settings(
                panel_x, content_y, panel_width, content_height
            )
        elif self.current_tab == "input":
            self._render_input_settings(panel_x, content_y, panel_width, content_height)
        elif self.current_tab == "gameplay":
            self._render_gameplay_settings(
                panel_x, content_y, panel_width, content_height
            )

        # Bottom buttons
        self._render_bottom_buttons(panel_x, panel_y + panel_height - 60, panel_width)

    def _render_tabs(self, x: int, y: int, width: int):
        """Render tab buttons."""
        tabs = ["audio", "graphics", "input", "gameplay"]
        tab_width = width // len(tabs)

        for i, tab in enumerate(tabs):
            tab_x = x + i * tab_width
            is_active = tab == self.current_tab
            tab_color = (50, 100, 200) if is_active else (30, 30, 50)

            if self.ui.button(
                tab.capitalize(), tab_x + 5, y, tab_width - 10, 40, color=tab_color
            ):
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
            self.settings["audio"]["master_volume"] = max(
                0, min(1, slider_x / (width - 40))
            )
            self.has_unsaved_changes = True

            if self.audio_manager:
                self.audio_manager.set_master_volume(
                    self.settings["audio"]["master_volume"]
                )

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
            self.settings["audio"]["music_volume"] = max(
                0, min(1, slider_x / (width - 40))
            )
            self.has_unsaved_changes = True

            if self.audio_manager:
                self.audio_manager.set_music_volume(
                    self.settings["audio"]["music_volume"]
                )

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

        if self.ui.slider(
            x + 20, current_y, width - 40, 30, self.settings["audio"]["sfx_volume"]
        ):
            mouse_x = pygame.mouse.get_pos()[0]
            slider_x = mouse_x - x - 20
            self.settings["audio"]["sfx_volume"] = max(
                0, min(1, slider_x / (width - 40))
            )
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
            "Fullscreen: ON"
            if self.settings["graphics"]["fullscreen"]
            else "Fullscreen: OFF"
        )
        fullscreen_color = (
            (0, 150, 0) if self.settings["graphics"]["fullscreen"] else (150, 0, 0)
        )

        if self.ui.button(
            fullscreen_text, x + 20, current_y, 300, 40, color=fullscreen_color
        ):
            self.settings["graphics"]["fullscreen"] = not self.settings["graphics"][
                "fullscreen"
            ]
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
        fps_text = (
            "Show FPS: ON" if self.settings["graphics"]["show_fps"] else "Show FPS: OFF"
        )
        fps_color = (
            (0, 150, 0) if self.settings["graphics"]["show_fps"] else (150, 0, 0)
        )

        if self.ui.button(fps_text, x + 20, current_y, 300, 40, color=fps_color):
            self.settings["graphics"]["show_fps"] = not self.settings["graphics"][
                "show_fps"
            ]
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
            self.settings["graphics"]["particle_density"] = max(
                0, min(1, slider_x / (width - 40))
            )
            self.has_unsaved_changes = True

        density_pct = int(self.settings["graphics"]["particle_density"] * 100)
        self.ui.label(f"{density_pct}%", x + width - 60, current_y + 5, size=16)
        current_y += 50

        # Screen Shake toggle
        shake_text = (
            "Screen Shake: ON"
            if self.settings["graphics"]["screen_shake"]
            else "Screen Shake: OFF"
        )
        shake_color = (
            (0, 150, 0) if self.settings["graphics"]["screen_shake"] else (150, 0, 0)
        )

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
            "Invert Y-Axis: ON"
            if self.settings["input"]["invert_y"]
            else "Invert Y-Axis: OFF"
        )
        invert_color = (
            (0, 150, 0) if self.settings["input"]["invert_y"] else (150, 0, 0)
        )

        if self.ui.button(invert_text, x + 20, current_y, 300, 40, color=invert_color):
            self.settings["input"]["invert_y"] = not self.settings["input"]["invert_y"]
            self.has_unsaved_changes = True

        current_y += 60

        # Key Bindings
        self.ui.label(
            "Key Bindings:", x + 20, current_y, size=18, color=(200, 200, 255)
        )
        current_y += 30

        for action, key in self.key_bindings.items():
            key_name = pygame.key.name(key)
            action_label = action.replace("_", " ").title()

            self.ui.label(f"{action_label}:", x + 30, current_y, size=14)

            # Key button
            is_waiting = self.waiting_for_key == action
            button_color = (255, 200, 0) if is_waiting else (50, 50, 80)
            button_text = "Press Key..." if is_waiting else key_name

            if self.ui.button(
                button_text, x + 250, current_y - 5, 150, 30, color=button_color
            ):
                self.waiting_for_key = action

            current_y += 35

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
            "Auto-Save: ON"
            if self.settings["gameplay"]["auto_save"]
            else "Auto-Save: OFF"
        )
        auto_save_color = (
            (0, 150, 0) if self.settings["gameplay"]["auto_save"] else (150, 0, 0)
        )

        if self.ui.button(
            auto_save_text, x + 20, current_y, 300, 40, color=auto_save_color
        ):
            self.settings["gameplay"]["auto_save"] = not self.settings["gameplay"][
                "auto_save"
            ]
            self.has_unsaved_changes = True

        current_y += 50

        # Tutorial
        tutorial_text = (
            "Tutorial: ON"
            if self.settings["gameplay"]["tutorial_enabled"]
            else "Tutorial: OFF"
        )
        tutorial_color = (
            (0, 150, 0)
            if self.settings["gameplay"]["tutorial_enabled"]
            else (150, 0, 0)
        )

        if self.ui.button(
            tutorial_text, x + 20, current_y, 300, 40, color=tutorial_color
        ):
            self.settings["gameplay"]["tutorial_enabled"] = not self.settings[
                "gameplay"
            ]["tutorial_enabled"]
            self.has_unsaved_changes = True

    def _render_bottom_buttons(self, x: int, y: int, width: int):
        """Render save, apply, and cancel buttons."""
        button_width = 150
        button_spacing = 20

        # Save button
        if self.ui.button(
            "Save & Close", x + 20, y, button_width, 40, color=(0, 150, 0)
        ):
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
        """Handle key press for key binding."""
        if self.waiting_for_key:
            self.key_bindings[self.waiting_for_key] = key
            self.waiting_for_key = None
            self.has_unsaved_changes = True

    def save_settings(self):
        """Save settings to file."""
        settings_data = {
            "settings": self.settings,
            "key_bindings": {k: v for k, v in self.key_bindings.items()},
        }

        try:
            with open("settings.json", "w") as f:
                json.dump(settings_data, f, indent=2)
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
            print("Settings loaded successfully")
        except FileNotFoundError:
            print("No settings file found, using defaults")
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def apply_settings(self):
        """Apply settings without saving."""
        # Apply audio settings
        if self.audio_manager:
            self.audio_manager.set_master_volume(
                self.settings["audio"]["master_volume"]
            )
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

        self.has_unsaved_changes = True
        print("Settings reset to defaults")
