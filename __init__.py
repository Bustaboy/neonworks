"""
Neon Works Game Engine

A comprehensive 2D turn-based strategy game engine with base building and survival elements.
Originally developed for Neon Collapse.
"""

__version__ = "0.1.0"
__author__ = "Neon Works Team"

from neonworks.core.ecs import Entity, Component, System, World
from neonworks.core.game_loop import GameEngine
from neonworks.core.events import EventManager, Event
from neonworks.core.state import StateManager, GameState

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
