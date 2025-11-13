"""
Neon Works Game Engine

A comprehensive 2D turn-based strategy game engine with base building and survival elements.
Originally developed for Neon Collapse.
"""

__version__ = "0.1.0"
__author__ = "Neon Works Team"

from neonworks.core.ecs import Component, Entity, System, World
from neonworks.core.events import Event, EventManager
from neonworks.core.game_loop import GameEngine
from neonworks.core.state import GameState, StateManager

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
