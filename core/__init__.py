"""Core engine systems"""

# Lazy imports to avoid loading heavy dependencies during test collection
# Import these explicitly when needed: from core.scene import Scene, etc.

__all__ = [
    "Scene",
    "SceneManager",
    "SceneState",
    "SceneTransition",
    "TransitionType",
]


def __getattr__(name):
    """Lazy load scene module only when accessed"""
    if name in __all__:
        from .scene import (
            Scene,
            SceneManager,
            SceneState,
            SceneTransition,
            TransitionType,
        )

        globals().update(
            {
                "Scene": Scene,
                "SceneManager": SceneManager,
                "SceneState": SceneState,
                "SceneTransition": SceneTransition,
                "TransitionType": TransitionType,
            }
        )
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
