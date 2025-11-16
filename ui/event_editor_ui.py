"""
Visual Event Editor UI - NeonWorks

Provides a visual interface for creating and editing game events.

Hotkey: F5 or Ctrl+E
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import pygame

from ..rendering.ui import UI


class EventEditorUI:
    """Visual event editor for creating game events."""

    def __init__(self, world, renderer):
        self.world = world
        self.renderer = renderer
        self.visible = False
        self.screen = None
        self.ui = None
        self.events = []
        self.selected_event_index = -1

    def toggle(self):
        self.visible = not self.visible

    def new_event(self):
        event_id = f"event_{len(self.events) + 1}"
        self.events.append({
            "id": event_id,
            "trigger": "on_enter",
            "condition": "",
            "actions": [{"type": "message", "text": "New event"}],
        })
        self.selected_event_index = len(self.events) - 1

    def delete_event(self):
        if 0 <= self.selected_event_index < len(self.events):
            self.events.pop(self.selected_event_index)
            self.selected_event_index = -1

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
        self.ui.title("Event Editor (F5)", px + pw // 2 - 100, py + 10, size=24)

        if self.ui.button("X", px + pw - 50, py + 10, 35, 35, color=(150, 0, 0)):
            self.toggle()

        # Events list
        self.ui.text(f"Events ({len(self.events)}):", px + 20, py + 60, size=16)
        y = py + 90
        for i, event in enumerate(self.events):
            color = (100, 255, 100) if i == self.selected_event_index else (200, 200, 200)
            text = f"{i + 1}. {event.get('id')} ({event.get('trigger')})"
            self.ui.text(text, px + 30, y, size=14, color=color)
            y += 25

        # Buttons
        by = py + ph - 45
        if self.ui.button("New (N)", px + 20, by, 100, 30):
            self.new_event()
        if self.ui.button("Delete (D)", px + 130, by, 100, 30):
            self.delete_event()

    def handle_event(self, event: pygame.event.Event):
        if not self.visible:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_n:
                self.new_event()
            elif event.key == pygame.K_d:
                self.delete_event()
            elif event.key == pygame.K_UP and self.selected_event_index > 0:
                self.selected_event_index -= 1
            elif event.key == pygame.K_DOWN and self.selected_event_index < len(self.events) - 1:
                self.selected_event_index += 1
