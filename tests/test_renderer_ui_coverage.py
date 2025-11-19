"""
Coverage-focused smoke tests for rendering and UI scaffolding.

These tests are minimal and avoid real display usage by relying on pygame's
dummy surface creation and short-lived objects.
"""

import pytest

pygame = pytest.importorskip("pygame")


def test_renderer_basic_draws(monkeypatch):
    """
    Instantiate Renderer and exercise simple draw calls to cover hot paths.
    """
    from neonworks.rendering.renderer import Renderer

    pygame.init()
    screen = pygame.Surface((320, 240))
    renderer = Renderer(320, 240, tile_size=16)
    renderer.screen = screen  # avoid creating a real display

    renderer.clear((0, 0, 0))
    # draw_rect helper isn't present; exercise clear and a direct blit
    sprite = pygame.Surface((8, 8))
    renderer.screen.blit(sprite, (5, 5))
    renderer.clear((10, 10, 10))


def test_ui_system_widgets_smoke():
    """
    Exercise core UI widgets rendering into an offscreen surface.
    """
    from neonworks.ui import ui_system

    pygame.init()
    surface = pygame.Surface((200, 150))
    button = ui_system.UIButton(text="Click")
    label = ui_system.UILabel(text="Hello")
    text_input = ui_system.UITextInput(text="abc")

    # Basic render/update calls
    button.render(surface)
    label.render(surface)
    text_input.render(surface)

    button.update(0.016)
    label.update(0.016)
    text_input.update(0.016)
