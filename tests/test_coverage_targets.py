"""
Targeted coverage tests to raise critical entrypoints/modules above baseline.

These tests heavily stub I/O-heavy and graphical dependencies to execute control
flow without touching disk or graphics hardware.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

pygame = pytest.importorskip("pygame")


def test_cli_create_and_list(tmp_path, monkeypatch):
    """
    Drive NeonWorksCLI through create/list/templates paths with heavy stubs.
    """
    from neonworks import cli

    dummy_manager = MagicMock()
    dummy_manager.list_projects.return_value = ["existing_project"]
    dummy_manager.create_project.return_value = object()

    def _load_modules_stub(self):
        self.ProjectManager = MagicMock(return_value=dummy_manager)
        self.ProjectMetadata = MagicMock()
        self.ProjectSettings = MagicMock()
        self.Project = MagicMock()
        self.validate_project_config = lambda *a, **k: None
        self.ValidationError = Exception

    with patch.object(cli.NeonWorksCLI, "_load_modules", _load_modules_stub):
        cli_obj = cli.NeonWorksCLI()
        cli_obj.projects_root = tmp_path
        cli_obj.templates_root = tmp_path / "templates"
        cli_obj._copy_template_files = lambda *a, **k: None
        cli_obj._create_minimal_structure = lambda *a, **k: None

        # Successful creation path
        assert cli_obj.create_project("my_game", template="basic_game")

        # Existing project path
        (tmp_path / "existing_project").mkdir()
        assert not cli_obj.create_project("existing_project", template="basic_game")

        # Invalid template path
        assert not cli_obj.create_project("other_game", template="nonexistent_template")

        # Templates/list calls
        cli_obj.list_templates()
        cli_obj.list_projects()


def test_main_game_application_init(monkeypatch):
    """
    Stub GameApplication dependencies to cover init/system setup paths.
    """
    from neonworks import main

    dummy_settings = SimpleNamespace(
        window_width=640,
        window_height=480,
        fullscreen=False,
        tile_size=32,
        grid_width=10,
        grid_height=10,
        window_title="Demo Project",
        enable_turn_based=True,
        enable_base_building=True,
        enable_survival=True,
        initial_scene="menu",
        building_definitions=None,
    )
    dummy_project = MagicMock()
    dummy_project.config.settings = dummy_settings
    dummy_project.config.metadata.name = "Dummy"
    dummy_project.config.metadata.version = "0.0.1"

    world = MagicMock()
    state_manager = MagicMock()
    engine_stub = MagicMock()
    engine_stub.world = world
    engine_stub.state_manager = state_manager
    engine_stub.start = lambda: None

    monkeypatch.setattr(main, "load_project", lambda name: dummy_project)
    monkeypatch.setattr(main, "GameEngine", lambda *a, **k: engine_stub)
    monkeypatch.setattr(main, "Renderer", MagicMock())
    monkeypatch.setattr(main, "SaveGameManager", MagicMock())
    monkeypatch.setattr(main, "PathfindingSystem", MagicMock())
    monkeypatch.setattr(main, "TurnSystem", MagicMock())
    monkeypatch.setattr(main, "BuildingLibrary", MagicMock())
    monkeypatch.setattr(main, "BuildingSystem", MagicMock())
    monkeypatch.setattr(main, "SurvivalSystem", MagicMock())
    monkeypatch.setattr(main.sys, "exit", lambda code=0: None)

    app = main.GameApplication("demo_project")
    app.run()


def test_main_entry_run_flow(monkeypatch):
    """
    Execute main.main flow with patched GameApplication to avoid real engine run.
    """
    from neonworks import main
    import sys
    import types

    monkeypatch.setattr(main, "GameApplication", MagicMock(run=lambda: None))
    monkeypatch.setattr(main.sys, "exit", lambda code=0: None)
    monkeypatch.setattr(main, "load_project", MagicMock())
    # main imports pygame inside; stub module finder to succeed
    dummy_pygame = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "pygame", dummy_pygame)
    main.sys.argv = ["main.py", "demo_project"]
    main.main()


def test_launcher_constructor_stubbed(monkeypatch):
    """
    Cover NeonWorksLauncher __init__ by stubbing pygame and project catalog.
    """
    from neonworks import launcher

    dummy_pygame = SimpleNamespace(
        init=lambda: None,
        display=SimpleNamespace(set_mode=lambda size, flags=0: MagicMock(), set_caption=lambda title: None),
        time=SimpleNamespace(Clock=lambda: MagicMock(tick=lambda fps=0: None)),
        event=SimpleNamespace(get=lambda: []),
        QUIT=0,
    )
    monkeypatch.setattr(launcher, "pygame", dummy_pygame)
    monkeypatch.setattr(launcher, "ProjectCatalog", MagicMock(return_value=MagicMock()), raising=False)
    monkeypatch.setattr(launcher, "AssetManager", MagicMock(return_value=MagicMock()), raising=False)
    monkeypatch.setattr(launcher, "APP_CONFIG", {}, raising=False)

    launcher.NeonWorksLauncher()


def test_renderer_render_world(monkeypatch):
    """
    Cover renderer.render_world with a stub world/entity.
    """
    from neonworks.rendering.renderer import Renderer
    from neonworks.core.ecs import Sprite, GridPosition

    pygame.init()
    renderer = Renderer(200, 150, tile_size=16)
    renderer.screen = pygame.Surface((200, 150))
    monkeypatch.setattr(renderer, "_get_or_load_sprite", lambda sprite: pygame.Surface((8, 8)))

    sprite = Sprite(texture="dummy.png")
    sprite.layer = 1
    entity = MagicMock()
    entity.get_component.side_effect = lambda comp: sprite if comp is Sprite else GridPosition(grid_x=1, grid_y=1)
    world = MagicMock()
    world.get_entities_with_component.return_value = [entity]

    renderer.render_world(world)
    renderer.clear((0, 0, 0))
