#!/usr/bin/env python3
"""
NeonWorks Launcher - Standalone Project Hub

A visual launcher application for managing NeonWorks game projects.
This provides a user-friendly interface similar to Unity Hub or Godot's project manager.

Features:
- Visual project browser with thumbnails
- Create new projects with template selection
- Open/launch projects into editor
- Recent projects tracking
- Project settings management

Usage:
    python launcher.py
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from neonworks.core.project import ProjectManager, ProjectMetadata, ProjectSettings
from neonworks.rendering.ui import UI, UIStyle


class LauncherUI:
    """Main launcher user interface"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # Custom style for launcher
        style = UIStyle()
        style.primary_color = (70, 130, 220)  # Blue
        style.secondary_color = (40, 40, 55)  # Dark gray
        style.background_color = (25, 25, 35)  # Very dark
        style.hover_color = (90, 150, 240)  # Light blue
        style.active_color = (50, 110, 200)  # Darker blue
        style.font_size = 18
        style.corner_radius = 8

        self.ui = UI(screen, style)

        # State
        self.scroll_offset = 0
        self.selected_project_index = -1

        # Text input state
        self.text_input_active = False
        self.text_input_buffer = ""

    def render_header(self, x: int, y: int, width: int):
        """Render the launcher header with branding"""
        # Title
        title_font = pygame.font.Font(None, 56)
        title_text = title_font.render("NeonWorks", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(width // 2, y + 40))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle_text = subtitle_font.render(
            "2D Game Engine - Project Launcher", True, (150, 150, 170)
        )
        subtitle_rect = subtitle_text.get_rect(center=(width // 2, y + 80))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Version
        version_text = subtitle_font.render("v0.1.0", True, (100, 100, 120))
        self.screen.blit(version_text, (width - 100, y + 10))

    def render_project_card(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        project_info: Dict,
        index: int,
        selected: bool,
    ) -> bool:
        """Render a project card and return True if clicked"""
        # Determine colors
        if selected:
            bg_color = (50, 110, 200)
            border_color = (100, 200, 255)
        else:
            bg_color = (40, 40, 55)
            border_color = (80, 80, 100)

        # Check hover
        mouse_pos = pygame.mouse.get_pos()
        is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        if is_hover and not selected:
            bg_color = (50, 50, 70)
            border_color = (100, 100, 120)

        # Draw card background
        pygame.draw.rect(
            self.screen,
            bg_color,
            (x, y, width, height),
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            border_color,
            (x, y, width, height),
            2,
            border_radius=8,
        )

        # Project name
        name_font = pygame.font.Font(None, 28)
        name_text = name_font.render(project_info["name"], True, (255, 255, 255))
        self.screen.blit(name_text, (x + 20, y + 15))

        # Project info
        info_font = pygame.font.Font(None, 18)
        desc = project_info.get("description", "No description")
        desc_text = info_font.render(
            desc[:60] + "..." if len(desc) > 60 else desc, True, (200, 200, 220)
        )
        self.screen.blit(desc_text, (x + 20, y + 50))

        # Version and date
        version = project_info.get("version", "0.1.0")
        version_text = info_font.render(f"Version: {version}", True, (150, 150, 170))
        self.screen.blit(version_text, (x + 20, y + 75))

        # Modified date
        modified = project_info.get("modified_date", "Unknown")
        if modified != "Unknown":
            try:
                date_obj = datetime.fromisoformat(modified)
                modified = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        date_text = info_font.render(f"Modified: {modified}", True, (150, 150, 170))
        self.screen.blit(date_text, (x + 20, y + 100))

        # Template info
        template = project_info.get("template", "unknown")
        template_text = info_font.render(f"Template: {template}", True, (100, 150, 200))
        self.screen.blit(template_text, (x + width - 250, y + 75))

        # Check if clicked
        clicked = False
        if is_hover and pygame.mouse.get_pressed()[0]:
            clicked = True

        return clicked

    def render_button_large(
        self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]
    ) -> bool:
        """Render a large styled button"""
        mouse_pos = pygame.mouse.get_pos()
        is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        # Determine button color
        if is_hover:
            btn_color = tuple(min(c + 30, 255) for c in color)
        else:
            btn_color = color

        # Draw button
        pygame.draw.rect(self.screen, btn_color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(
            self.screen,
            tuple(min(c + 50, 255) for c in color),
            (x, y, width, height),
            2,
            border_radius=8,
        )

        # Draw text
        font = pygame.font.Font(None, 24)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

        # Check if clicked
        clicked = is_hover and pygame.mouse.get_pressed()[0]
        return clicked

    def render_text_input(
        self, x: int, y: int, width: int, height: int, text: str, label: str
    ) -> str:
        """Render a text input field with label"""
        # Label
        label_font = pygame.font.Font(None, 20)
        label_surface = label_font.render(label, True, (200, 200, 220))
        self.screen.blit(label_surface, (x, y - 25))

        # Input box
        pygame.draw.rect(
            self.screen,
            (40, 40, 55),
            (x, y, width, height),
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            (100, 100, 120),
            (x, y, width, height),
            2,
            border_radius=6,
        )

        # Text
        if text:
            text_font = pygame.font.Font(None, 22)
            text_surface = text_font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (x + 10, y + height // 2 - 10))

        # Cursor if active
        if self.text_input_active:
            cursor_x = x + 10 + (len(text) * 12)
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (cursor_x, y + 8),
                (cursor_x, y + height - 8),
                2,
            )

        return text


class NeonWorksLauncher:
    """Main launcher application"""

    # Template configurations
    TEMPLATES = {
        "basic_game": {
            "name": "Basic Game",
            "description": "Minimal template with player movement and basic rendering",
            "settings": {
                "window_title": "My Game",
                "window_width": 1280,
                "window_height": 720,
                "tile_size": 32,
                "grid_width": 40,
                "grid_height": 30,
                "initial_scene": "gameplay",
                "enable_base_building": False,
                "enable_survival": False,
                "enable_turn_based": False,
                "enable_combat": False,
            },
        },
        "turn_based_rpg": {
            "name": "Turn-Based RPG",
            "description": "Template with turn-based combat system and character progression",
            "settings": {
                "window_title": "Turn-Based RPG",
                "window_width": 1280,
                "window_height": 720,
                "tile_size": 32,
                "grid_width": 40,
                "grid_height": 30,
                "initial_scene": "menu",
                "enable_base_building": False,
                "enable_survival": False,
                "enable_turn_based": True,
                "enable_combat": True,
            },
        },
        "base_builder": {
            "name": "Base Builder",
            "description": "Template with building system and resource management",
            "settings": {
                "window_title": "Base Builder",
                "window_width": 1600,
                "window_height": 900,
                "tile_size": 32,
                "grid_width": 50,
                "grid_height": 40,
                "initial_scene": "gameplay",
                "enable_base_building": True,
                "enable_survival": True,
                "enable_turn_based": False,
                "enable_combat": False,
                "building_definitions": "config/buildings.json",
                "item_definitions": "config/items.json",
            },
        },
        "jrpg_demo": {
            "name": "JRPG Demo",
            "description": "Complete JRPG template with battle system, magic, and exploration",
            "settings": {
                "window_title": "JRPG Demo",
                "window_width": 1280,
                "window_height": 720,
                "tile_size": 32,
                "grid_width": 40,
                "grid_height": 30,
                "initial_scene": "menu",
                "enable_base_building": False,
                "enable_survival": False,
                "enable_turn_based": True,
                "enable_combat": True,
            },
        },
    }

    def __init__(self):
        pygame.init()

        # Window settings
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("NeonWorks Launcher")

        # UI
        self.launcher_ui = LauncherUI(self.screen)

        # Project management
        self.engine_root = Path(__file__).parent
        self.projects_root = self.engine_root.parent / "projects"
        self.projects_root.mkdir(exist_ok=True)
        self.project_manager = ProjectManager(str(self.projects_root))

        # State
        self.running = True
        self.clock = pygame.time.Clock()
        self.view = "main"  # 'main', 'new_project', 'template_select'

        # Project data
        self.projects: List[Dict] = []
        self.selected_project_index = -1

        # New project state
        self.new_project_name = ""
        self.selected_template = "basic_game"
        self.new_project_author = "Developer"
        self.new_project_description = ""

        # Recent projects
        self.recent_projects_file = self.engine_root / ".recent_projects.json"
        self.recent_projects = self._load_recent_projects()

        # Click cooldown
        self.click_cooldown = 0

        # Load projects
        self.refresh_projects()

    def _load_recent_projects(self) -> List[str]:
        """Load recent projects list"""
        if self.recent_projects_file.exists():
            try:
                with open(self.recent_projects_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_recent_projects(self):
        """Save recent projects list"""
        try:
            with open(self.recent_projects_file, "w") as f:
                json.dump(self.recent_projects[:10], f, indent=2)  # Keep only last 10
        except:
            pass

    def _add_to_recent(self, project_name: str):
        """Add project to recent list"""
        if project_name in self.recent_projects:
            self.recent_projects.remove(project_name)
        self.recent_projects.insert(0, project_name)
        self._save_recent_projects()

    def refresh_projects(self):
        """Scan and load all projects"""
        self.projects = []
        project_names = self.project_manager.list_projects()

        for project_name in project_names:
            project = self.project_manager.load_project(project_name)
            if project:
                self.projects.append(
                    {
                        "name": project.config.metadata.name,
                        "path": str(project.root_dir),
                        "version": project.config.metadata.version,
                        "description": project.config.metadata.description,
                        "author": project.config.metadata.author,
                        "created_date": project.config.metadata.created_date,
                        "modified_date": project.config.metadata.modified_date,
                        "template": getattr(project.config.metadata, "template", "unknown"),
                    }
                )

    def create_project(self, name: str, template: str, author: str, description: str) -> bool:
        """Create a new project"""
        try:
            # Validate name
            if not name or not name.replace("_", "").replace("-", "").isalnum():
                print("❌ Invalid project name")
                return False

            # Check if exists
            if (self.projects_root / name).exists():
                print(f"❌ Project '{name}' already exists")
                return False

            template_info = self.TEMPLATES.get(template)
            if not template_info:
                print(f"❌ Unknown template '{template}'")
                return False

            print(f"🎮 Creating project: {name}")

            # Create metadata
            metadata = ProjectMetadata(
                name=name,
                version="0.1.0",
                description=description or f"A {template_info['name']} project",
                author=author,
                engine_version="0.1.0",
                created_date=datetime.now().isoformat(),
                modified_date=datetime.now().isoformat(),
            )

            # Store template in metadata
            metadata.template = template  # type: ignore

            # Create settings
            settings = ProjectSettings(**template_info["settings"])
            settings.window_title = name.replace("_", " ").title()

            # Create project
            project = self.project_manager.create_project(name, metadata, settings)

            if project:
                print(f"✅ Project created: {name}")
                self.refresh_projects()
                self._add_to_recent(name)
                return True

            return False

        except Exception as e:
            print(f"❌ Error creating project: {e}")
            import traceback

            traceback.print_exc()
            return False

    def launch_project(self, project_name: str):
        """Launch a project into the editor"""
        print(f"🚀 Launching project: {project_name}")

        try:
            # Add to recent projects
            self._add_to_recent(project_name)

            # Launch the project using main.py
            main_script = self.engine_root / "main.py"

            # Run as subprocess
            subprocess.Popen(
                [sys.executable, str(main_script), project_name],
                cwd=str(self.engine_root.parent),
            )

            print(f"✅ Project launched: {project_name}")
            print("💡 The launcher will remain open. Close this window to exit.")

        except Exception as e:
            print(f"❌ Error launching project: {e}")
            import traceback

            traceback.print_exc()

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.view == "new_project" and self.launcher_ui.text_input_active:
                    # Handle text input
                    if event.key == pygame.K_BACKSPACE:
                        self.new_project_name = self.new_project_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.launcher_ui.text_input_active = False
                    elif event.key == pygame.K_ESCAPE:
                        self.launcher_ui.text_input_active = False
                        self.view = "main"
                    elif len(self.new_project_name) < 50:
                        char = event.unicode
                        if char.isalnum() or char in "_-":
                            self.new_project_name += char
                else:
                    # Keyboard shortcuts
                    if event.key == pygame.K_ESCAPE:
                        if self.view != "main":
                            self.view = "main"
                        else:
                            self.running = False
                    elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.view = "new_project"

    def update(self, dt: float):
        """Update launcher state"""
        # Update click cooldown
        if self.click_cooldown > 0:
            self.click_cooldown -= dt

    def render(self):
        """Render the launcher"""
        # Clear screen
        self.screen.fill((15, 15, 25))

        if self.view == "main":
            self.render_main_view()
        elif self.view == "new_project":
            self.render_new_project_view()
        elif self.view == "template_select":
            self.render_template_select_view()

        pygame.display.flip()

    def render_main_view(self):
        """Render the main project browser view"""
        # Header
        self.launcher_ui.render_header(0, 20, self.width)

        # Action buttons
        button_y = 140
        button_width = 200
        button_height = 50
        button_spacing = 20

        # New Project button
        if self.launcher_ui.render_button_large(
            50, button_y, button_width, button_height, "New Project", (70, 130, 220)
        ):
            if self.click_cooldown <= 0:
                self.view = "new_project"
                self.new_project_name = ""
                self.click_cooldown = 0.3

        # Open Project button (only if a project is selected)
        if self.selected_project_index >= 0:
            if self.launcher_ui.render_button_large(
                50 + button_width + button_spacing,
                button_y,
                button_width,
                button_height,
                "Open Project",
                (70, 180, 100),
            ):
                if self.click_cooldown <= 0:
                    project = self.projects[self.selected_project_index]
                    self.launch_project(project["name"])
                    self.click_cooldown = 0.3

        # Refresh button
        if self.launcher_ui.render_button_large(
            self.width - button_width - 50,
            button_y,
            button_width,
            button_height,
            "Refresh Projects",
            (100, 100, 120),
        ):
            if self.click_cooldown <= 0:
                self.refresh_projects()
                self.click_cooldown = 0.3

        # Projects section
        projects_y = button_y + button_height + 30

        # Section title
        title_font = pygame.font.Font(None, 32)
        title_text = title_font.render("Your Projects", True, (200, 200, 220))
        self.screen.blit(title_text, (50, projects_y))

        projects_y += 50

        # Project list
        if not self.projects:
            # No projects message
            no_projects_font = pygame.font.Font(None, 24)
            no_projects_text = no_projects_font.render(
                "No projects found. Create your first project to get started!",
                True,
                (150, 150, 170),
            )
            no_projects_rect = no_projects_text.get_rect(center=(self.width // 2, projects_y + 100))
            self.screen.blit(no_projects_text, no_projects_rect)
        else:
            # Render project cards
            card_height = 140
            card_spacing = 15
            card_width = self.width - 100

            for i, project in enumerate(self.projects):
                card_y = projects_y + i * (card_height + card_spacing)

                # Only render if visible
                if card_y + card_height > projects_y and card_y < self.height:
                    clicked = self.launcher_ui.render_project_card(
                        50,
                        card_y,
                        card_width,
                        card_height,
                        project,
                        i,
                        i == self.selected_project_index,
                    )

                    if clicked and self.click_cooldown <= 0:
                        if self.selected_project_index == i:
                            # Double-click to open
                            self.launch_project(project["name"])
                            self.click_cooldown = 0.5
                        else:
                            # Single-click to select
                            self.selected_project_index = i
                            self.click_cooldown = 0.2

        # Footer
        footer_font = pygame.font.Font(None, 18)
        footer_text = footer_font.render(
            "Ctrl+N: New Project  |  Esc: Exit  |  Double-click to open project",
            True,
            (100, 100, 120),
        )
        footer_rect = footer_text.get_rect(center=(self.width // 2, self.height - 20))
        self.screen.blit(footer_text, footer_rect)

    def render_new_project_view(self):
        """Render the new project creation view"""
        # Background panel
        panel_width = 800
        panel_height = 650
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2

        pygame.draw.rect(
            self.screen,
            (25, 25, 35),
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            (100, 200, 255),
            (panel_x, panel_y, panel_width, panel_height),
            3,
            border_radius=12,
        )

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Create New Project", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, panel_y + 40))
        self.screen.blit(title_text, title_rect)

        # Project name input
        input_y = panel_y + 120
        self.new_project_name = self.launcher_ui.render_text_input(
            panel_x + 50, input_y, panel_width - 100, 50, self.new_project_name, "Project Name:"
        )

        # Click to activate input
        mouse_pos = pygame.mouse.get_pos()
        input_rect = pygame.Rect(panel_x + 50, input_y, panel_width - 100, 50)
        if input_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.launcher_ui.text_input_active = True

        # Template selection
        template_y = input_y + 100
        template_font = pygame.font.Font(None, 24)
        template_label = template_font.render("Select Template:", True, (200, 200, 220))
        self.screen.blit(template_label, (panel_x + 50, template_y - 30))

        # Template buttons
        template_btn_width = (panel_width - 150) // 2
        template_btn_height = 80
        template_spacing = 20

        templates_list = list(self.TEMPLATES.keys())
        for i, template_key in enumerate(templates_list):
            row = i // 2
            col = i % 2
            btn_x = panel_x + 50 + col * (template_btn_width + template_spacing)
            btn_y = template_y + row * (template_btn_height + template_spacing)

            template_info = self.TEMPLATES[template_key]

            # Determine color
            if self.selected_template == template_key:
                color = (70, 130, 220)
            else:
                color = (50, 50, 70)

            # Render button
            mouse_in_btn = (
                btn_x <= mouse_pos[0] <= btn_x + template_btn_width
                and btn_y <= mouse_pos[1] <= btn_y + template_btn_height
            )

            if mouse_in_btn:
                color = tuple(min(c + 30, 255) for c in color)

            pygame.draw.rect(
                self.screen,
                color,
                (btn_x, btn_y, template_btn_width, template_btn_height),
                border_radius=8,
            )
            pygame.draw.rect(
                self.screen,
                (100, 100, 120),
                (btn_x, btn_y, template_btn_width, template_btn_height),
                2,
                border_radius=8,
            )

            # Template name
            name_font = pygame.font.Font(None, 22)
            name_text = name_font.render(template_info["name"], True, (255, 255, 255))
            self.screen.blit(name_text, (btn_x + 10, btn_y + 10))

            # Template description
            desc_font = pygame.font.Font(None, 16)
            desc = template_info["description"]
            desc_lines = [desc[i : i + 35] for i in range(0, len(desc), 35)]
            for j, line in enumerate(desc_lines[:2]):
                desc_text = desc_font.render(line, True, (200, 200, 220))
                self.screen.blit(desc_text, (btn_x + 10, btn_y + 35 + j * 18))

            # Check click
            if mouse_in_btn and pygame.mouse.get_pressed()[0] and self.click_cooldown <= 0:
                self.selected_template = template_key
                self.click_cooldown = 0.2

        # Action buttons
        action_y = panel_y + panel_height - 80

        # Create button
        create_enabled = len(self.new_project_name) > 0
        create_color = (70, 180, 100) if create_enabled else (60, 60, 70)

        if self.launcher_ui.render_button_large(
            panel_x + 50, action_y, 300, 50, "Create Project", create_color
        ):
            if create_enabled and self.click_cooldown <= 0:
                if self.create_project(
                    self.new_project_name,
                    self.selected_template,
                    self.new_project_author,
                    self.new_project_description,
                ):
                    self.view = "main"
                self.click_cooldown = 0.3

        # Cancel button
        if self.launcher_ui.render_button_large(
            panel_x + panel_width - 350, action_y, 300, 50, "Cancel", (120, 60, 60)
        ):
            if self.click_cooldown <= 0:
                self.view = "main"
                self.click_cooldown = 0.3

    def render_template_select_view(self):
        """Render template selection view (future expansion)"""
        pass

    def run(self):
        """Run the launcher main loop"""
        print("🚀 NeonWorks Launcher started")
        print("   Press Ctrl+N to create a new project")
        print("   Press Esc to exit")

        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        print("👋 Launcher closed")


def main():
    """Main entry point for the launcher"""
    try:
        launcher = NeonWorksLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 Launcher interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
