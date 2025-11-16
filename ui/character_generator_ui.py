"""
Character Generator UI - NeonWorks

Visual interface for creating characters with AI assistance.

Hotkey: F7 or Ctrl+G
"""

import json
from pathlib import Path
from typing import Dict, Optional

import pygame

from ..rendering.ui import UI


class CharacterGeneratorUI:
    """Visual character generator with AI assistance."""

    ARCHETYPES = ["Warrior", "Mage", "Rogue", "Cleric", "Paladin", "Custom"]
    CLASSES = ["hero", "enemy", "npc", "boss"]

    def __init__(self, world, renderer, project_path: Optional[str] = None):
        self.world = world
        self.renderer = renderer
        self.visible = False
        self.screen = None
        self.ui = None
        self.project_path = project_path or ""
        self.character = self._default_character()
        self.current_archetype = "Warrior"

    def _default_character(self) -> Dict:
        return {
            "id": "new_character",
            "name": "New Character",
            "level": 1,
            "class": "hero",
            "stats": {
                "hp": 100,
                "max_hp": 100,
                "mp": 50,
                "max_mp": 50,
                "attack": 10,
                "defense": 10,
                "speed": 10,
                "luck": 5,
            },
        }

    def toggle(self):
        self.visible = not self.visible

    def apply_archetype(self):
        archetypes = {
            "Warrior": {"hp": 120, "mp": 20, "attack": 15, "defense": 12, "speed": 8},
            "Mage": {"hp": 70, "mp": 100, "attack": 5, "defense": 6, "speed": 7},
            "Rogue": {"hp": 90, "mp": 30, "attack": 12, "defense": 8, "speed": 16},
            "Cleric": {"hp": 85, "mp": 80, "attack": 6, "defense": 10, "speed": 9},
            "Paladin": {"hp": 110, "mp": 50, "attack": 13, "defense": 14, "speed": 7},
        }

        if self.current_archetype in archetypes:
            stats = archetypes[self.current_archetype]
            self.character["stats"].update(stats)
            self.character["stats"]["max_hp"] = stats["hp"]
            self.character["stats"]["max_mp"] = stats["mp"]

    def randomize_stats(self):
        import random
        self.character["stats"]["hp"] = random.randint(60, 150)
        self.character["stats"]["max_hp"] = self.character["stats"]["hp"]
        self.character["stats"]["mp"] = random.randint(10, 100)
        self.character["stats"]["max_mp"] = self.character["stats"]["mp"]
        self.character["stats"]["attack"] = random.randint(5, 20)
        self.character["stats"]["defense"] = random.randint(5, 20)
        self.character["stats"]["speed"] = random.randint(5, 18)
        self.character["stats"]["luck"] = random.randint(3, 15)

    def clear_character(self):
        self.character = self._default_character()

    def update(self, dt: float):
        pass

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        self.screen = screen
        if self.ui is None:
            self.ui = UI(screen)

        w, h = screen.get_size()
        pw, ph = 1000, 650
        px, py = (w - pw) // 2, (h - ph) // 2

        # Overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Panel
        self.ui.panel(px, py, pw, ph, (20, 20, 30))
        self.ui.title("Character Generator (F7)", px + pw // 2 - 130, py + 10, size=24)

        if self.ui.button("X", px + pw - 50, py + 10, 35, 35, color=(150, 0, 0)):
            self.toggle()

        # Archetype buttons
        arch_x = px + 20
        for i, arch in enumerate(self.ARCHETYPES):
            color = (100, 200, 255) if arch == self.current_archetype else (100, 100, 120)
            if self.ui.button(arch, arch_x + i * 100, py + 55, 90, 30, color=color):
                self.current_archetype = arch
                self.apply_archetype()

        # Character info
        self.ui.text(f"Name: {self.character['name']}", px + 20, py + 110, size=16)
        self.ui.text(f"Class: {self.character['class']}", px + 300, py + 110, size=16)
        self.ui.text(f"Level: {self.character['level']}", px + 500, py + 110, size=16)

        # Stats
        stats = self.character["stats"]
        self.ui.text("Stats:", px + 20, py + 150, size=16, color=(100, 200, 255))

        stat_y = py + 180
        for stat, value in [
            ("HP", stats["hp"]),
            ("MP", stats["mp"]),
            ("Attack", stats["attack"]),
            ("Defense", stats["defense"]),
            ("Speed", stats["speed"]),
            ("Luck", stats["luck"]),
        ]:
            self.ui.text(f"{stat}: {value}", px + 40, stat_y, size=14)
            stat_y += 30

        # Buttons
        by = py + ph - 45
        if self.ui.button("Apply Archetype", px + 20, by, 140, 30):
            self.apply_archetype()
        if self.ui.button("Randomize", px + 170, by, 100, 30):
            self.randomize_stats()
        if self.ui.button("Clear", px + 280, by, 80, 30):
            self.clear_character()

    def handle_event(self, event: pygame.event.Event):
        if not self.visible:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()

    def set_project_path(self, path: str):
        self.project_path = path
