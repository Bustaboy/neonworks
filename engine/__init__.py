"""
Neon Works Game Engine

A comprehensive 2D turn-based strategy game engine with base building and survival elements.
Originally developed for Neon Collapse.
"""

__version__ = "0.1.0"
__author__ = "Neon Works Team"

from engine.core.ecs import Entity, Component, System, World
from engine.core.game_loop import GameEngine
from engine.core.events import EventManager, Event
from engine.core.state import StateManager, GameState

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
