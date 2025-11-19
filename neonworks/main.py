"""
Main Application Entry Point

Load and run game projects with the engine.

Usage:
    python -m neonworks.main <project_name>
    python -m neonworks.main neon_collapse
"""

import sys
from pathlib import Path

from neonworks.core.ecs import World
from neonworks.core.game_loop import EngineConfig, GameEngine
from neonworks.core.project import Project, load_project
from neonworks.core.state import GameplayState, MenuState
from neonworks.data.serialization import SaveGameManager
from neonworks.rendering.renderer import Renderer
from neonworks.systems.base_building import BuildingLibrary, BuildingSystem
from neonworks.systems.pathfinding import PathfindingSystem
from neonworks.systems.survival import SurvivalSystem
from neonworks.systems.turn_system import TurnSystem


class GameApplication:
    """Main game application"""

    def __init__(self, project_name: str, mode: str = "run"):
        print(f"🎮 Starting Neon Works Engine...")
        print(f"   Loading project: {project_name}")
        self.mode = mode

        # Load project
        try:
            self.project = load_project(project_name)
            if not self.project:
                self._handle_project_not_found(project_name)
                sys.exit(1)
        except FileNotFoundError as e:
            self._handle_project_not_found(project_name)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading project: {e}")
            print(f"\nIf this is a configuration error, check your project.json file.")
            print(f"See docs/project_configuration.md for help.")
            sys.exit(1)

        # Create engine config from project settings
        self.engine_config = self._create_engine_config()

        # Initialize engine
        self.engine = GameEngine(
            target_fps=self.engine_config.target_fps,
            fixed_timestep=self.engine_config.fixed_timestep,
        )

        # Initialize renderer
        self.renderer = Renderer(
            self.engine_config.window_width,
            self.engine_config.window_height,
            self.engine_config.tile_size,
        )
        self.renderer.set_title(self.project.config.settings.window_title)

        # Optional editor UI manager (only used in editor mode)
        self.ui_manager = None
        if self.mode == "edit":
            try:
                from neonworks.ui.master_ui_manager import MasterUIManager

                self.ui_manager = MasterUIManager(
                    self.renderer.screen,
                    self.engine.world,
                    self.engine.state_manager,
                    self.engine.audio_manager,
                    self.engine.input_manager,
                    self.renderer,
                )
                self.engine.attach_ui_manager(
                    self.ui_manager,
                    lambda: (self.renderer.camera.x, self.renderer.camera.y),
                )
                self.ui_manager.set_mode("editor")
                self.ui_manager.toggle_level_builder()
            except Exception as ui_error:
                print(f"❌ Failed to initialize editor UI: {ui_error}")

        # Initialize save system
        self.save_manager = SaveGameManager(self.project)

        # Setup game systems
        self._setup_systems()

        # Setup game states
        self._setup_states()

        print("✅ Engine initialized successfully")
        print(
            f"   Project: {self.project.config.metadata.name} v{self.project.config.metadata.version}"
        )
        print(
            f"   Resolution: {self.engine_config.window_width}x{self.engine_config.window_height}"
        )
        print(f"   Systems: {len(self.engine.world._systems)} active")

    def _create_engine_config(self) -> EngineConfig:
        """Create engine config from project settings"""
        config = EngineConfig()

        settings = self.project.config.settings

        config.window_width = settings.window_width
        config.window_height = settings.window_height
        config.fullscreen = settings.fullscreen
        config.tile_size = settings.tile_size
        config.grid_width = settings.grid_width
        config.grid_height = settings.grid_height

        return config

    def _setup_systems(self):
        """Setup game systems based on project configuration"""
        world = self.engine.world
        settings = self.project.config.settings

        # Always add pathfinding
        pathfinding = PathfindingSystem()
        world.add_system(pathfinding)
        print("   ✓ Pathfinding system")

        # Add turn-based system if enabled
        if settings.enable_turn_based:
            turn_system = TurnSystem()
            world.add_system(turn_system)
            print("   ✓ Turn-based system")

        # Add base building system if enabled
        if settings.enable_base_building:
            building_library = BuildingLibrary()

            # Load building definitions from project if available
            if settings.building_definitions:
                building_config_path = self.project.get_config_path(
                    settings.building_definitions.replace("config/", "").replace(".json", "")
                )
                # TODO: Load building definitions from file
                print(f"   Building definitions: {building_config_path}")

            building_system = BuildingSystem(building_library)
            world.add_system(building_system)
            print("   ✓ Base building system")

        # Add survival system if enabled
        if settings.enable_survival:
            survival_system = SurvivalSystem()
            world.add_system(survival_system)
            print("   ✓ Survival system")

    def _setup_states(self):
        """Setup game states"""
        state_manager = self.engine.state_manager

        # Menu state
        menu_state = MenuState()
        state_manager.register_state(menu_state)

        # Gameplay state
        gameplay_state = GameplayState(self.engine.world)
        state_manager.register_state(gameplay_state)

        # Start with the initial scene from project settings
        from neonworks.core.state import StateTransition

        initial_scene = self.project.config.settings.initial_scene
        state_manager.change_state(initial_scene, StateTransition.PUSH)

    def run(self):
        """Run the game"""
        print("\n🚀 Starting game loop...")
        print("   Press Ctrl+C to quit\n")

        if self.ui_manager:
            self.ui_manager.show_notification(
                "Editor mode active: F4 Level Builder, F5 Event Editor, F6 Database, F8 Quest"
            )

        try:
            self.engine.start()
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            self.shutdown()

    def shutdown(self):
        """Shutdown the game"""
        print("   Cleaning up...")
        print("✅ Game closed successfully")

    def _handle_project_not_found(self, project_name: str):
        """Handle project not found error with helpful message."""
        print(f"❌ Project '{project_name}' not found!")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check that the project directory exists:")
        print(f"      projects/{project_name}/")
        print(f"   2. Verify project.json exists in the project directory")
        print(f"   3. Make sure you're running from the engine root directory")
        print(f"\n📚 Quick Start:")
        print(f"   • See QUICKSTART.md for installation and setup")
        print(f"   • Try the example: cd engine/examples/simple_rpg && python main.py")
        print(f"   • Read docs/getting_started.md for a complete tutorial")
        print(f"\n📁 Available projects:")

        from neonworks.core.project import get_project_manager

        pm = get_project_manager()
        projects = pm.list_projects()

        if projects:
            for project in projects:
                print(f"   • {project}")
        else:
            print(f"   (No projects found in projects/ directory)")
            print(f"   Create your first project by following docs/getting_started.md")


def print_usage():
    """Print usage information"""
    print(
        """
NeonWorks Game Engine

Usage:
    python -m neonworks.main <project_name> [--editor | --run]

Examples:
    python -m neonworks.main neon_collapse --run
    python -m neonworks.main my_game --editor  # opens editor tools

Available Projects:
    """
    )

def main():
    """Main entry point"""
    # Check for required dependencies
    try:
        import pygame
    except ImportError:
        print("❌ Error: pygame is not installed!")
        print("\n💡 To fix this:")
        print("   pip install pygame")
        print("   or")
        print("   pip install -e .  (installs all dependencies)")
        print("\nSee QUICKSTART.md for complete installation instructions.")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        print_usage()
        sys.exit(1)

    mode = "run"
    project_name = None

    for arg in args:
        if arg in ["--help", "-h", "help"]:
            print_usage()
            sys.exit(0)
        if arg in ["--version", "-v"]:
            print("Neon Works v0.1.0")
            sys.exit(0)
        if arg in ["--editor", "--edit", "-e"]:
            mode = "edit"
            continue
        if arg in ["--run"]:
            mode = "run"
            continue
        if project_name is None:
            project_name = arg

    if project_name is None:
        print_usage()
        sys.exit(1)

    # Create and run application
    try:
        app = GameApplication(project_name, mode=mode)
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print(f"\n💡 If you need help:")
        print(f"   • Check the error message above")
        print(f"   • See docs/ for documentation")
        print(f"   • Report bugs on GitHub")
        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
