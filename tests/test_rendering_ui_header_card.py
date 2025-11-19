"""
Coverage for rendering/ui.py header and project card rendering.
"""

import pytest

pygame = pytest.importorskip("pygame")


def test_launcher_ui_header_and_card():
    from neonworks.rendering.ui import UI, UIStyle

    pygame.init()
    screen = pygame.Surface((400, 300))
    ui = UI(screen, UIStyle())

    # Begin/end frame hit default paths
    ui.begin_frame()
    ui.label(10, 10, "Test")
    ui.button(10, 40, 120, 32, "Click", id_="btn1")
    ui.end_frame()
