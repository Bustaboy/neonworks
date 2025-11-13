"""
NeonWorks Project Manager UI - Visual Project and Scene Management
Provides complete visual interface for managing projects, scenes, and saves.
"""
from typing import Optional, List, Dict, Tuple
import pygame
import os
import json
from pathlib import Path
from ..rendering.ui import UI
from ..core.project import Project
from ..core.state import StateManager


class ProjectManagerUI:
    """
    Visual project manager for creating, loading, and managing NeonWorks projects.
    """

    def __init__(self, screen: pygame.Surface, state_manager: Optional[StateManager] = None):
        self.screen = screen
        self.ui = UI(screen)
        self.state_manager = state_manager

        self.visible = False
        self.current_view = 'projects'  # 'projects', 'scenes', 'saves'

        # Data
        self.projects: List[Dict] = []
        self.scenes: List[str] = []
        self.save_files: List[Dict] = []

        # UI state
        self.selected_project = None
        self.selected_scene = None
        self.selected_save = None
        self.scroll_offset = 0

        # New project state
        self.creating_new_project = False
        self.new_project_name = ""
        self.new_project_template = "blank"

        # Paths
        self.projects_dir = Path("projects")
        self.saves_dir = Path("saves")

    def toggle(self):
        """Toggle project manager visibility."""
        self.visible = not self.visible
        if self.visible:
            self.refresh_data()

    def refresh_data(self):
        """Refresh project, scene, and save data."""
        self._scan_projects()
        if self.selected_project:
            self._scan_scenes(self.selected_project)
            self._scan_saves(self.selected_project)

    def render(self):
        """Render the project manager UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Main panel
        panel_width = 900
        panel_height = 650
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (15, 15, 25))

        # Title
        self.ui.title("Project Manager", panel_x + panel_width // 2 - 100, panel_y + 10, size=28, color=(100, 200, 255))

        # Close button
        if self.ui.button("X", panel_x + panel_width - 50, panel_y + 10, 35, 35, color=(150, 0, 0)):
            self.toggle()

        # View tabs
        self._render_view_tabs(panel_x, panel_y + 60, panel_width)

        # Content area
        content_y = panel_y + 110
        content_height = panel_height - 170

        if self.current_view == 'projects':
            self._render_projects_view(panel_x, content_y, panel_width, content_height)
        elif self.current_view == 'scenes':
            self._render_scenes_view(panel_x, content_y, panel_width, content_height)
        elif self.current_view == 'saves':
            self._render_saves_view(panel_x, content_y, panel_width, content_height)

        # Bottom action bar
        self._render_action_bar(panel_x, panel_y + panel_height - 60, panel_width)

    def _render_view_tabs(self, x: int, y: int, width: int):
        """Render view selection tabs."""
        tabs = ['projects', 'scenes', 'saves']
        tab_width = width // 3

        for i, tab in enumerate(tabs):
            tab_x = x + i * tab_width
            is_active = tab == self.current_view
            tab_color = (50, 100, 200) if is_active else (25, 25, 40)

            if self.ui.button(tab.capitalize(), tab_x + 5, y, tab_width - 10, 40, color=tab_color):
                self.current_view = tab
                if tab == 'scenes' or tab == 'saves':
                    if not self.selected_project:
                        # Need to select a project first
                        self.current_view = 'projects'

    def _render_projects_view(self, x: int, y: int, width: int, height: int):
        """Render the projects list view."""
        # Header
        self.ui.label("Your Projects", x + 20, y + 10, size=20, color=(200, 200, 255))

        # New project button
        if self.ui.button("+ New Project", x + width - 180, y + 5, 160, 35, color=(0, 150, 0)):
            self.creating_new_project = True

        list_y = y + 50
        list_height = height - 60

        if self.creating_new_project:
            self._render_new_project_dialog(x, y, width, height)
            return

        # Projects list
        item_height = 80
        item_spacing = 10
        current_y = list_y

        if not self.projects:
            self.ui.label("No projects found. Create a new project to get started!",
                         x + width // 2 - 200, y + height // 2, size=16, color=(150, 150, 150))
            return

        for project_data in self.projects:
            if current_y + item_height > y + height:
                break

            project_name = project_data['name']
            is_selected = self.selected_project == project_name

            # Project item
            item_color = (60, 60, 100) if is_selected else (35, 35, 50)
            self.ui.panel(x + 20, current_y, width - 40, item_height, item_color)

            # Project icon (colored square)
            icon_color = project_data.get('color', (100, 150, 255))
            pygame.draw.rect(self.screen, icon_color, (x + 30, current_y + 10, 50, 50))

            # Project name
            self.ui.label(project_name, x + 90, current_y + 10, size=20, color=(255, 255, 255))

            # Project info
            project_path = project_data.get('path', 'Unknown')
            self.ui.label(f"Path: {project_path}", x + 90, current_y + 35, size=12, color=(180, 180, 180))

            last_modified = project_data.get('last_modified', 'Unknown')
            self.ui.label(f"Modified: {last_modified}", x + 90, current_y + 50, size=12, color=(150, 150, 150))

            # Action buttons
            button_x = x + width - 350

            if self.ui.button("Open", button_x, current_y + 20, 80, 35, color=(0, 120, 0)):
                self.open_project(project_name)

            if self.ui.button("Scenes", button_x + 90, current_y + 20, 80, 35, color=(0, 80, 150)):
                self.selected_project = project_name
                self.current_view = 'scenes'

            if self.ui.button("Delete", button_x + 180, current_y + 20, 80, 35, color=(150, 0, 0)):
                self.delete_project(project_name)

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (x + 20 <= mouse_pos[0] <= x + width - 20 and
                current_y <= mouse_pos[1] <= current_y + item_height):
                if pygame.mouse.get_pressed()[0]:
                    self.selected_project = project_name

            current_y += item_height + item_spacing

    def _render_new_project_dialog(self, x: int, y: int, width: int, height: int):
        """Render the new project creation dialog."""
        dialog_width = 600
        dialog_height = 400
        dialog_x = x + (width - dialog_width) // 2
        dialog_y = y + (height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (25, 25, 40))

        # Title
        self.ui.title("Create New Project", dialog_x + dialog_width // 2 - 120, dialog_y + 20, size=22)

        current_y = dialog_y + 70

        # Project name
        self.ui.label("Project Name:", dialog_x + 30, current_y, size=16)
        current_y += 30

        # Simple text input visualization (in real implementation, would handle keyboard input)
        self.ui.panel(dialog_x + 30, current_y, dialog_width - 60, 40, (50, 50, 70))
        self.ui.label(self.new_project_name if self.new_project_name else "Enter project name...",
                     dialog_x + 40, current_y + 10, size=16, color=(255, 255, 255) if self.new_project_name else (120, 120, 120))

        current_y += 60

        # Template selection
        self.ui.label("Template:", dialog_x + 30, current_y, size=16)
        current_y += 30

        templates = {
            'blank': 'Blank Project',
            'platformer': 'Platformer',
            'rpg': 'RPG',
            'survival': 'Survival Game',
        }

        for template_id, template_name in templates.items():
            is_selected = self.new_project_template == template_id
            template_color = (0, 100, 150) if is_selected else (50, 50, 70)

            if self.ui.button(template_name, dialog_x + 30, current_y, 250, 35, color=template_color):
                self.new_project_template = template_id

            current_y += 40

        # Create and Cancel buttons
        button_y = dialog_y + dialog_height - 70

        if self.ui.button("Create Project", dialog_x + 30, button_y, 200, 40, color=(0, 150, 0)):
            self.create_project(self.new_project_name, self.new_project_template)
            self.creating_new_project = False
            self.new_project_name = ""

        if self.ui.button("Cancel", dialog_x + dialog_width - 230, button_y, 200, 40, color=(150, 0, 0)):
            self.creating_new_project = False
            self.new_project_name = ""

    def _render_scenes_view(self, x: int, y: int, width: int, height: int):
        """Render the scenes list view."""
        if not self.selected_project:
            self.ui.label("Please select a project first", x + width // 2 - 100, y + height // 2, size=16)
            return

        # Header
        self.ui.label(f"Scenes - {self.selected_project}", x + 20, y + 10, size=20, color=(200, 200, 255))

        # New scene button
        if self.ui.button("+ New Scene", x + width - 180, y + 5, 160, 35, color=(0, 150, 0)):
            self.create_scene()

        list_y = y + 50
        item_height = 60
        item_spacing = 10
        current_y = list_y

        if not self.scenes:
            self.ui.label("No scenes found. Create a new scene!", x + width // 2 - 120, y + height // 2, size=16, color=(150, 150, 150))
            return

        for scene_name in self.scenes:
            if current_y + item_height > y + height:
                break

            is_selected = self.selected_scene == scene_name

            # Scene item
            item_color = (60, 100, 60) if is_selected else (35, 50, 35)
            self.ui.panel(x + 20, current_y, width - 40, item_height, item_color)

            # Scene name
            self.ui.label(scene_name, x + 30, current_y + 20, size=18, color=(255, 255, 255))

            # Load button
            if self.ui.button("Load", x + width - 250, current_y + 12, 100, 35, color=(0, 100, 150)):
                self.load_scene(scene_name)

            # Delete button
            if self.ui.button("Delete", x + width - 140, current_y + 12, 100, 35, color=(150, 0, 0)):
                self.delete_scene(scene_name)

            current_y += item_height + item_spacing

    def _render_saves_view(self, x: int, y: int, width: int, height: int):
        """Render the save files list view."""
        if not self.selected_project:
            self.ui.label("Please select a project first", x + width // 2 - 100, y + height // 2, size=16)
            return

        # Header
        self.ui.label(f"Save Files - {self.selected_project}", x + 20, y + 10, size=20, color=(200, 200, 255))

        list_y = y + 50
        item_height = 70
        item_spacing = 10
        current_y = list_y

        if not self.save_files:
            self.ui.label("No save files found.", x + width // 2 - 80, y + height // 2, size=16, color=(150, 150, 150))
            return

        for save_data in self.save_files:
            if current_y + item_height > y + height:
                break

            save_name = save_data['name']
            is_selected = self.selected_save == save_name

            # Save item
            item_color = (60, 60, 100) if is_selected else (35, 35, 50)
            self.ui.panel(x + 20, current_y, width - 40, item_height, item_color)

            # Save name
            self.ui.label(save_name, x + 30, current_y + 10, size=18, color=(255, 255, 255))

            # Save info
            timestamp = save_data.get('timestamp', 'Unknown')
            self.ui.label(f"Saved: {timestamp}", x + 30, current_y + 35, size=12, color=(180, 180, 180))

            # Action buttons
            if self.ui.button("Load", x + width - 250, current_y + 17, 100, 35, color=(0, 120, 0)):
                self.load_save(save_name)

            if self.ui.button("Delete", x + width - 140, current_y + 17, 100, 35, color=(150, 0, 0)):
                self.delete_save(save_name)

            current_y += item_height + item_spacing

    def _render_action_bar(self, x: int, y: int, width: int):
        """Render the bottom action bar."""
        if self.ui.button("Refresh", x + 20, y, 120, 40, color=(0, 100, 150)):
            self.refresh_data()

        if self.ui.button("Close", x + width - 140, y, 120, 40, color=(100, 100, 100)):
            self.toggle()

    def _scan_projects(self):
        """Scan for available projects."""
        self.projects = []

        if not self.projects_dir.exists():
            self.projects_dir.mkdir(parents=True)
            return

        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project_json = project_dir / "project.json"
                if project_json.exists():
                    try:
                        with open(project_json, 'r') as f:
                            project_data = json.load(f)
                            self.projects.append({
                                'name': project_data.get('name', project_dir.name),
                                'path': str(project_dir),
                                'color': tuple(project_data.get('color', [100, 150, 255])),
                                'last_modified': project_dir.stat().st_mtime,
                            })
                    except Exception as e:
                        print(f"Failed to load project {project_dir}: {e}")

    def _scan_scenes(self, project_name: str):
        """Scan for scenes in a project."""
        self.scenes = []
        project_dir = self.projects_dir / project_name / "scenes"

        if not project_dir.exists():
            return

        for scene_file in project_dir.glob("*.json"):
            self.scenes.append(scene_file.stem)

    def _scan_saves(self, project_name: str):
        """Scan for save files in a project."""
        self.save_files = []
        saves_dir = self.saves_dir / project_name

        if not saves_dir.exists():
            return

        for save_file in saves_dir.glob("*.json"):
            try:
                with open(save_file, 'r') as f:
                    save_data = json.load(f)
                    self.save_files.append({
                        'name': save_file.stem,
                        'timestamp': save_data.get('timestamp', 'Unknown'),
                        'path': str(save_file),
                    })
            except Exception as e:
                print(f"Failed to load save file {save_file}: {e}")

    def create_project(self, name: str, template: str):
        """Create a new project."""
        if not name:
            print("Project name cannot be empty")
            return

        project_dir = self.projects_dir / name
        if project_dir.exists():
            print(f"Project {name} already exists")
            return

        # Create project directory structure
        project_dir.mkdir(parents=True)
        (project_dir / "scenes").mkdir()
        (project_dir / "assets").mkdir()
        (project_dir / "scripts").mkdir()

        # Create project.json
        project_data = {
            'name': name,
            'template': template,
            'version': '1.0.0',
            'engine_version': '1.0.0',
        }

        with open(project_dir / "project.json", 'w') as f:
            json.dump(project_data, f, indent=2)

        print(f"Created project: {name}")
        self.refresh_data()

    def open_project(self, project_name: str):
        """Open a project."""
        print(f"Opening project: {project_name}")
        # This would load the project and switch to the game/editor view
        self.selected_project = project_name

    def delete_project(self, project_name: str):
        """Delete a project."""
        # In a real implementation, would show a confirmation dialog
        print(f"Deleting project: {project_name}")
        self.refresh_data()

    def create_scene(self):
        """Create a new scene."""
        if not self.selected_project:
            return

        scene_name = f"scene_{len(self.scenes) + 1}"
        print(f"Creating scene: {scene_name}")
        self.refresh_data()

    def load_scene(self, scene_name: str):
        """Load a scene."""
        print(f"Loading scene: {scene_name}")
        # This would use the state manager to load the scene
        if self.state_manager:
            # self.state_manager.change_state(new_scene_state)
            pass

    def delete_scene(self, scene_name: str):
        """Delete a scene."""
        print(f"Deleting scene: {scene_name}")
        self.refresh_data()

    def load_save(self, save_name: str):
        """Load a save file."""
        print(f"Loading save: {save_name}")

    def delete_save(self, save_name: str):
        """Delete a save file."""
        print(f"Deleting save: {save_name}")
        self.refresh_data()
