"""
Database Manager UI - NeonWorks

Visual interface for browsing and editing game database.

Hotkey: F6 or Ctrl+D
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import pygame

from ..rendering.ui import UI


class DatabaseManagerUI:
    """Visual database manager for game data."""

    CATEGORIES = ["Characters", "Items", "Skills", "Quests", "Dialogues"]

    def __init__(self, world, renderer, project_path: Optional[str] = None):
        self.world = world
        self.renderer = renderer
        self.visible = False
        self.screen = None
        self.ui = None
        self.project_path = project_path or ""
        self.database = {}
        self.current_category = "Characters"
        self.selected_entity = None

    def toggle(self):
        self.visible = not self.visible

    def new_entity(self):
        category = self.current_category
        if category not in self.database:
            self.database[category] = []

        new_entity = {
            "id": f"new_{category.lower()}_{len(self.database[category])}",
            "name": f"New {category[:-1]}",
        }
        self.database[category].append(new_entity)
        self.selected_entity = new_entity

    def delete_entity(self):
        if self.selected_entity and self.current_category in self.database:
            if self.selected_entity in self.database[self.current_category]:
                self.database[self.current_category].remove(self.selected_entity)
                self.selected_entity = None

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
        self.ui.title("Database Manager (F6)", px + pw // 2 - 120, py + 10, size=24)

        if self.ui.button("X", px + pw - 50, py + 10, 35, 35, color=(150, 0, 0)):
            self.toggle()

        # Category tabs
        tab_x = px + 20
        for i, cat in enumerate(self.CATEGORIES):
            color = (100, 200, 255) if cat == self.current_category else (100, 100, 120)
            if self.ui.button(cat, tab_x + i * 120, py + 55, 110, 30, color=color):
                self.current_category = cat

        # Entity list
        entities = self.database.get(self.current_category, [])
        self.ui.text(f"{self.current_category} ({len(entities)}):", px + 20, py + 100, size=16)

        y = py + 130
        for entity in entities[:20]:  # Show first 20
            color = (100, 255, 100) if entity == self.selected_entity else (200, 200, 200)
            name = entity.get("name", entity.get("id", "Unknown"))
            self.ui.text(f"• {name}", px + 30, y, size=14, color=color)
            y += 25

        # Buttons
        by = py + ph - 45
        if self.ui.button("New (N)", px + 20, by, 100, 30):
            self.new_entity()
        if self.ui.button("Delete (D)", px + 130, by, 100, 30):
            self.delete_entity()

    def handle_event(self, event: pygame.event.Event):
        if not self.visible:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_n:
                self.new_entity()
            elif event.key == pygame.K_d:
                self.delete_entity()
