"""
Stub-heavy MasterUIManager coverage: patch child UIs to no-ops and exercise toggles.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pygame = pytest.importorskip("pygame")


def test_master_ui_manager_toggle_and_render(monkeypatch):
    from neonworks.ui import master_ui_manager

    # Patch all child UI classes to lightweight stubs
    stub_ui = lambda *a, **k: MagicMock(
        toggle=lambda: None, render=lambda *args, **kwargs: None, update=lambda *a, **k: None
    )
    for attr in [
        "GameHUD",
        "BuildingUI",
        "CombatUI",
        "NavmeshEditorUI",
        "LevelBuilderUI",
        "EventEditorUI",
        "DatabaseManagerUI",
        "CharacterGeneratorUI",
        "SettingsUI",
        "ProjectManagerUI",
        "DebugConsoleUI",
        "QuestEditorUI",
        "AssetBrowserUI",
        "AutotileEditorUI",
        "AIAnimatorUI",
        "AIAssistantPanel",
        "AIAssetInspector",
        "AIAssetEditor",
        "ShortcutsOverlayUI",
        "MapManagerUI",
        "WorkspaceToolbar",
    ]:
        monkeypatch.setattr(master_ui_manager, attr, stub_ui)

    # Stub workspace manager getter
    monkeypatch.setattr(master_ui_manager, "get_workspace_manager", lambda: MagicMock())

    pygame.init()
    screen = pygame.Surface((200, 150))
    world = MagicMock()
    state_manager = MagicMock()
    audio_manager = MagicMock()
    input_manager = MagicMock()
    renderer = MagicMock()

    ui = master_ui_manager.MasterUIManager(
        screen=screen,
        world=world,
        state_manager=state_manager,
        audio_manager=audio_manager,
        input_manager=input_manager,
        renderer=renderer,
    )

    # Toggle a subset of panels
    ui.toggle_game_hud()
    ui.toggle_building_ui()
    ui.toggle_level_builder()
    ui.toggle_database_editor()
    ui.toggle_project_manager()

    # Render/update smoke
    ui.render()
    ui.update(0.016, mouse_pos=(0, 0), camera_offset=(0, 0))
