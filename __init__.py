"""
Neon Works Game Engine

A comprehensive 2D turn-based strategy game engine with base building and survival elements.
Originally developed for Neon Collapse.
"""

__version__ = "0.1.0"
__author__ = "Neon Works Team"


def __getattr__(name):
    """Lazy load modules to avoid pygame dependency during test collection"""
    if name == "Entity":
        from neonworks.core.ecs import Entity

        return Entity
    elif name == "Component":
        from neonworks.core.ecs import Component

        return Component
    elif name == "System":
        from neonworks.core.ecs import System

        return System
    elif name == "World":
        from neonworks.core.ecs import World

        return World
    elif name == "GameEngine":
        from neonworks.core.game_loop import GameEngine

        return GameEngine
    elif name == "EventManager":
        from neonworks.core.events import EventManager

        return EventManager
    elif name == "Event":
        from neonworks.core.events import Event

        return Event
    elif name == "StateManager":
        from neonworks.core.state import StateManager

        return StateManager
    elif name == "GameState":
        from neonworks.core.state import GameState

        return GameState
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Entity",
    "Component",
    "System",
    "World",
    "GameEngine",
    "EventManager",
    "Event",
    "StateManager",
    "GameState",
]
