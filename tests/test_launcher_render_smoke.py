"""
Launcher coverage: instantiate and tick render/update helpers with heavy stubs.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pygame = pytest.importorskip("pygame")


def test_launcher_ui_render(monkeypatch):
    from neonworks import launcher

    # Stub pygame subsystems
    dummy_display = SimpleNamespace(
        set_mode=lambda size, flags=0: pygame.Surface(size),
        set_caption=lambda title: None,
        flip=lambda: None,
    )
    dummy_time = SimpleNamespace(Clock=lambda: MagicMock(tick=lambda fps=0: None))
    dummy_font = SimpleNamespace(Font=lambda *a, **k: MagicMock(render=lambda *a, **k: pygame.Surface((10, 10))))
    dummy_draw = SimpleNamespace(
        rect=lambda *a, **k: None, circle=lambda *a, **k: None, line=lambda *a, **k: None
    )
    monkeypatch.setattr(
        launcher,
        "pygame",
        SimpleNamespace(
            init=lambda: None,
            display=dummy_display,
            time=dummy_time,
            event=SimpleNamespace(get=lambda: []),
            font=dummy_font,
            mouse=SimpleNamespace(get_pos=lambda: (0, 0)),
            draw=dummy_draw,
            QUIT=0,
        ),
    )
    monkeypatch.setattr(launcher, "ProjectCatalog", MagicMock(return_value=MagicMock()), raising=False)
    monkeypatch.setattr(launcher, "AssetManager", MagicMock(return_value=MagicMock()), raising=False)
    monkeypatch.setattr(launcher, "APP_CONFIG", {}, raising=False)

    app = launcher.NeonWorksLauncher()
    # Exercise render methods
    app.render()
    app.update(0.016)
