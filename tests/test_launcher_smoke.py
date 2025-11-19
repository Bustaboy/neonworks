import pytest

pygame = pytest.importorskip("pygame")


def test_launcher_can_be_constructed():
    """
    Smoke test: ensure NeonWorksLauncher can be constructed without errors.

    This does not enter the main loop; it only verifies that initialization
    (including pygame setup and project manager wiring) succeeds.
    """
    from neonworks.launcher import NeonWorksLauncher

    pygame.init()
    try:
        # Create a small window to ensure the video subsystem is initialized.
        pygame.display.set_mode((800, 600))

        launcher = NeonWorksLauncher()
        assert launcher is not None
    finally:
        pygame.display.quit()
        pygame.quit()

