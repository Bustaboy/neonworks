"""
Database Manager UI - NeonWorks

Visual interface for browsing and editing game database and the World Bible graph.

Hotkey: F6 or Ctrl+D
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type

import pygame

from ..bible.bible_manager import BibleManager
from ..bible.schema import (
    Asset,
    Character,
    Faction,
    GameplayRule,
    Item,
    Location,
    Mechanic,
    Quest,
    StyleGuide,
)
from ..bible.storage import load_bible, save_bible
from ..rendering.ui import UI


class DatabaseManagerUI:
    """Visual database manager for game data and world bible graph."""

    CATEGORIES = ["Characters", "Items", "Skills", "Quests", "Dialogues", "World Bible"]

    # (Label, node_type, dataclass)
    BIBLE_NODE_TYPES: List[Tuple[str, str, Type]] = [
        ("Characters", "character", Character),
        ("Locations", "location", Location),
        ("Quests", "quest", Quest),
        ("Items", "item", Item),
        ("Mechanics", "mechanic", Mechanic),
        ("Factions", "faction", Faction),
        ("Assets", "asset", Asset),
        ("Style Guides", "style_guide", StyleGuide),
        ("Gameplay Rules", "gameplay_rule", GameplayRule),
    ]

    BIBLE_REL_LABELS: List[str] = [
        "related_to",
        "located_in",
        "member_of",
        "gives_quest",
        "uses_mechanic",
    ]

    def __init__(self, world, renderer, project_path: Optional[str] = None):
        self.world = world
        self.renderer = renderer
        self.visible = False
        self.screen: Optional[pygame.Surface] = None
        self.ui: Optional[UI] = None

        self.project_path = project_path or ""

        # Legacy JSON-style database (still used for other categories)
        self.database: Dict[str, List[Dict]] = {}
        self.current_category = "Characters"
        self.selected_entity: Optional[Dict] = None

        # World Bible graph
        self.bible_manager = BibleManager()
        self.bible_loaded = False
        self.bible_selected_type: str = "character"
        self.bible_selected_from_id: Optional[str] = None
        self.bible_selected_to_id: Optional[str] = None
        self.bible_rel_index: int = 0

    # --------------------------------------------------------------------- UI -

    def toggle(self) -> None:
        self.visible = not self.visible

    def new_entity(self) -> None:
        """Legacy JSON entity creation for non-Bible categories."""
        category = self.current_category
        if category not in self.database:
            self.database[category] = []

        new_entity = {
            "id": f"new_{category.lower()}_{len(self.database[category])}",
            "name": f"New {category[:-1]}",
        }
        self.database[category].append(new_entity)
        self.selected_entity = new_entity

    def delete_entity(self) -> None:
        """Legacy JSON deletion for non-Bible categories."""
        if self.selected_entity and self.current_category in self.database:
            if self.selected_entity in self.database[self.current_category]:
                self.database[self.current_category].remove(self.selected_entity)
                self.selected_entity = None

    def update(self, dt: float) -> None:
        """Reserved for future animations; currently no-op."""
        return

    def render(self, screen: pygame.Surface) -> None:
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
            if self.ui.button(cat, tab_x + i * 140, py + 55, 130, 30, color=color):
                self.current_category = cat

        if self.current_category == "World Bible":
            if not self.bible_loaded:
                self._load_world_bible()
            self._render_world_bible_view(px, py, pw, ph)
            return

        # Generic legacy view for JSON categories
        entities = self.database.get(self.current_category, [])
        self.ui.text(f"{self.current_category} ({len(entities)}):", px + 20, py + 100, size=16)

        y = py + 130
        for entity in entities[:20]:  # Show first 20
            color = (100, 255, 100) if entity == self.selected_entity else (200, 200, 200)
            name = entity.get("name", entity.get("id", "Unknown"))
            self.ui.text(f"- {name}", px + 30, y, size=14, color=color)
            y += 25

        # Buttons
        by = py + ph - 45
        if self.ui.button("New (N)", px + 20, by, 100, 30):
            self.new_entity()
        if self.ui.button("Delete (D)", px + 130, by, 100, 30):
            self.delete_entity()

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.visible:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_n and self.current_category != "World Bible":
                self.new_entity()
            elif event.key == pygame.K_d and self.current_category != "World Bible":
                self.delete_entity()

    # -------------------------------------------------------- World Bible IO -

    def _load_world_bible(self) -> None:
        """Load bible.json from the project (if present) into BibleManager."""
        self.bible_loaded = True
        if not self.project_path:
            return
        path = Path(self.project_path) / "bible.json"
        if not path.exists():
            return
        try:
            graph = load_bible(path)
            # Use in-memory graph in BibleManager
            self.bible_manager._graph = graph  # type: ignore[attr-defined]
        except Exception:
            # Non-fatal; UI will just show empty graph
            return

    def _save_world_bible(self) -> None:
        """Persist the current Bible graph back to bible.json."""
        if not self.project_path:
            return
        path = Path(self.project_path) / "bible.json"
        try:
            save_bible(self.bible_manager._graph, path)  # type: ignore[attr-defined]
        except Exception:
            return

    # ------------------------------------------------- World Bible UI / Graph -

    def _render_world_bible_view(self, px: int, py: int, pw: int, ph: int) -> None:
        """Render a tree/graph-style view of the World Bible."""
        assert self.ui is not None

        # Left: node-type list
        type_x = px + 20
        type_y = py + 100
        for label, node_type, _ in self.BIBLE_NODE_TYPES:
            color = (100, 200, 255) if node_type == self.bible_selected_type else (90, 90, 120)
            if self.ui.button(label, type_x, type_y, 160, 26, color=color):
                self.bible_selected_type = node_type
                self.bible_selected_from_id = None
                self.bible_selected_to_id = None
            type_y += 30

        # Center: nodes of selected type
        list_x = type_x + 180
        list_y = py + 100
        nodes = self.bible_manager.query_nodes_by_type(self.bible_selected_type)
        self.ui.text(
            f"{self.bible_selected_type.title()} Nodes ({len(nodes)}):",
            list_x,
            list_y,
            size=16,
        )
        list_y += 30

        max_rows = 14
        for node in nodes[:max_rows]:
            label = node.props.get("name", node.id)
            is_from = node.id == self.bible_selected_from_id
            is_to = node.id == self.bible_selected_to_id
            base_color = (200, 200, 200)
            if is_from:
                base_color = (120, 240, 120)
            elif is_to:
                base_color = (240, 200, 120)

            if self.ui.button(label, list_x, list_y, 260, 24, color=base_color):
                self.bible_selected_from_id = node.id

            # Small button to set as "to" node
            if self.ui.button("→", list_x + 270, list_y, 30, 24, color=(80, 80, 120)):
                self.bible_selected_to_id = node.id

            list_y += 26

        # New node button
        if self.ui.button("New Node", list_x, py + ph - 80, 120, 30):
            self._create_bible_node()

        # Right: details and relationships for selected "from" node
        detail_x = list_x + 320
        detail_y = py + 100
        self._render_bible_node_details(detail_x, detail_y)

    def _create_bible_node(self) -> None:
        """Create a new node of the currently selected bible type."""
        for _, node_type, cls in self.BIBLE_NODE_TYPES:
            if node_type == self.bible_selected_type:
                existing = self.bible_manager.query_nodes_by_type(node_type)
                new_id = f"{node_type}_{len(existing) + 1}"
                new_node = cls(id=new_id, props={"name": f"New {node_type}"})  # type: ignore[call-arg]
                self.bible_manager.add_node(new_node)
                self._save_world_bible()
                self.bible_selected_from_id = new_id
                break

    def _render_bible_node_details(self, x: int, y: int) -> None:
        """Render details and relationships for the selected bible node."""
        assert self.ui is not None

        if not self.bible_selected_from_id:
            self.ui.text("Select a node to view details.", x, y, size=16)
            return

        from_node = self.bible_manager.get_node(self.bible_selected_from_id)
        if from_node is None:
            self.ui.text("Selected node not found.", x, y, size=16, color=(255, 120, 120))
            return

        # Basic node info
        self.ui.text(f"ID: {from_node.id}", x, y, size=16)
        y += 24
        self.ui.text(f"Type: {from_node.type}", x, y, size=16)
        y += 24
        self.ui.text(f"Name: {from_node.props.get('name', '-')}", x, y, size=16)
        y += 40

        # Outgoing relationships
        self.ui.text("Outgoing Relationships:", x, y, size=16)
        y += 26

        # Use in-memory graph for edge visualization
        graph = self.bible_manager._graph  # type: ignore[attr-defined]
        for edge in getattr(graph, "edges", []):
            if edge.from_id == from_node.id:
                self.ui.text(
                    f"{edge.rel} → {edge.to_id}",
                    x + 10,
                    y,
                    size=14,
                    color=(200, 220, 255),
                )
                y += 20

        y += 20
        # Relationship creator
        rel_label = self.BIBLE_REL_LABELS[self.bible_rel_index]
        if self.ui.button(f"Relation: {rel_label}", x, y, 200, 26, color=(80, 80, 120)):
            self.bible_rel_index = (self.bible_rel_index + 1) % len(self.BIBLE_REL_LABELS)
        y += 36

        # Show current from/to selections
        self.ui.text(f"From: {self.bible_selected_from_id or '-'}", x, y, size=14)
        y += 20
        self.ui.text(f"To:   {self.bible_selected_to_id or '-'}", x, y, size=14)
        y += 30

        # Add relationship button
        if (
            self.bible_selected_from_id
            and self.bible_selected_to_id
            and self.bible_selected_from_id != self.bible_selected_to_id
        ):
            if self.ui.button("Add Relationship", x, y, 180, 30, color=(70, 130, 220)):
                rel = self.BIBLE_REL_LABELS[self.bible_rel_index]
                self.bible_manager.add_edge(
                    self.bible_selected_from_id, rel, self.bible_selected_to_id
                )
                self._save_world_bible()
