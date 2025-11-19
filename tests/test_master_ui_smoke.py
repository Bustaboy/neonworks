import pytest

pygame = pytest.importorskip("pygame")


def test_master_ui_toggle_smoke():
    """
    Smoke test: construct MasterUIManager and exercise primary toggle methods.

    This ensures that basic UI wiring and dependencies can be initialized
    without raising exceptions. It does not enter a full game loop.
    """
    from neonworks.audio.audio_manager import AudioManager
    from neonworks.core.ecs import World
    from neonworks.core.state import StateManager
    from neonworks.input.input_manager import InputManager
    from neonworks.rendering.renderer import Renderer
    from neonworks.ui.master_ui_manager import MasterUIManager

    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))

        world = World()
        state_manager = StateManager()
        audio_manager = AudioManager()
        input_manager = InputManager()

        # Renderer sets up its own window; for this smoke test we only care
        # that construction succeeds.
        renderer = Renderer(800, 600, tile_size=32)

        ui = MasterUIManager(
            screen=screen,
            world=world,
            state_manager=state_manager,
            audio_manager=audio_manager,
            input_manager=input_manager,
            renderer=renderer,
        )

        # Exercise primary toggle methods; any exception would fail the test.
        ui.toggle_game_hud()
        ui.toggle_building_ui()
        ui.toggle_level_builder()
        ui.toggle_event_editor()
        ui.toggle_database_editor()
        ui.toggle_character_generator()
        ui.toggle_asset_browser()
        ui.toggle_project_manager()
        ui.toggle_autotile_editor()
        ui.toggle_navmesh_editor()
        ui.toggle_ai_animator()
        ui.toggle_ai_assistant()
        ui.toggle_map_manager()

        # Basic sanity checks that key UI components exist.
        assert hasattr(ui, "game_hud")
        assert hasattr(ui, "building_ui")
        assert hasattr(ui, "level_builder")
        assert hasattr(ui, "event_editor")
        assert hasattr(ui, "database_editor")
        assert hasattr(ui, "character_generator")
        assert hasattr(ui, "asset_browser")
        assert hasattr(ui, "project_manager")
        assert hasattr(ui, "autotile_editor")
        assert hasattr(ui, "navmesh_editor")
        assert hasattr(ui, "ai_animator")
        assert hasattr(ui, "ai_assistant")
        assert hasattr(ui, "map_manager")
    finally:
        pygame.display.quit()
        pygame.quit()

