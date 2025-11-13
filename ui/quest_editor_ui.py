"""
NeonWorks Quest/Dialogue Editor UI - Visual Quest and Dialogue Creation
Provides complete visual interface for creating quests and dialogue trees.
"""

from typing import Optional, List, Dict, Any, Tuple
import pygame
import json
from ..rendering.ui import UI


class QuestEditorUI:
    """
    Visual editor for creating and managing quests and dialogue trees.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.ui = UI(screen)

        self.visible = False
        self.current_mode = "quest"  # 'quest' or 'dialogue'

        # Quest data
        self.quests: List[Dict] = []
        self.current_quest: Optional[Dict] = None
        self.editing_quest = False

        # Dialogue data
        self.dialogues: List[Dict] = []
        self.current_dialogue: Optional[Dict] = None
        self.editing_dialogue = False
        self.selected_node = None

        # UI state
        self.scroll_offset = 0

    def toggle(self):
        """Toggle quest editor visibility."""
        self.visible = not self.visible

    def render(self):
        """Render the quest editor UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Main panel
        panel_width = 1000
        panel_height = 700
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (20, 20, 30))

        # Title
        title = "Quest Editor" if self.current_mode == "quest" else "Dialogue Editor"
        self.ui.title(
            title,
            panel_x + panel_width // 2 - 80,
            panel_y + 10,
            size=24,
            color=(255, 200, 0),
        )

        # Close button
        if self.ui.button(
            "X", panel_x + panel_width - 50, panel_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.toggle()

        # Mode toggle
        self._render_mode_toggle(panel_x, panel_y + 60, panel_width)

        # Content area
        content_y = panel_y + 110
        content_height = panel_height - 120

        if self.current_mode == "quest":
            self._render_quest_editor(panel_x, content_y, panel_width, content_height)
        else:
            self._render_dialogue_editor(
                panel_x, content_y, panel_width, content_height
            )

    def _render_mode_toggle(self, x: int, y: int, width: int):
        """Render mode toggle buttons."""
        button_width = width // 2 - 10

        quest_color = (0, 150, 0) if self.current_mode == "quest" else (50, 50, 70)
        if self.ui.button(
            "Quest Editor", x + 5, y, button_width, 40, color=quest_color
        ):
            self.current_mode = "quest"

        dialogue_color = (
            (0, 100, 200) if self.current_mode == "dialogue" else (50, 50, 70)
        )
        if self.ui.button(
            "Dialogue Editor",
            x + button_width + 15,
            y,
            button_width,
            40,
            color=dialogue_color,
        ):
            self.current_mode = "dialogue"

    def _render_quest_editor(self, x: int, y: int, width: int, height: int):
        """Render the quest editor interface."""
        # Split into list and editor
        list_width = 300
        editor_x = x + list_width + 20

        # Quest list
        self._render_quest_list(x + 10, y, list_width, height)

        # Quest editor
        if self.current_quest:
            self._render_quest_details(editor_x, y, width - list_width - 40, height)
        else:
            self.ui.label(
                "Select a quest or create a new one",
                editor_x + 150,
                y + height // 2,
                size=16,
                color=(150, 150, 150),
            )

    def _render_quest_list(self, x: int, y: int, width: int, height: int):
        """Render the list of quests."""
        self.ui.panel(x, y, width, height, (30, 30, 45))
        self.ui.label("Quests", x + 10, y + 10, size=18, color=(200, 200, 255))

        # New quest button
        if self.ui.button(
            "+ New Quest", x + 10, y + 40, width - 20, 35, color=(0, 120, 0)
        ):
            self.create_new_quest()

        # Quest list
        list_y = y + 85
        item_height = 60

        for i, quest in enumerate(self.quests):
            if list_y + item_height > y + height - 10:
                break

            is_selected = self.current_quest == quest

            # Quest item
            item_color = (60, 60, 100) if is_selected else (40, 40, 60)
            self.ui.panel(x + 10, list_y, width - 20, item_height, item_color)

            # Quest name
            quest_name = quest.get("name", "Untitled Quest")
            self.ui.label(
                quest_name, x + 15, list_y + 10, size=16, color=(255, 255, 255)
            )

            # Quest status
            status = quest.get("status", "draft")
            status_colors = {
                "draft": (150, 150, 150),
                "active": (0, 255, 0),
                "complete": (255, 200, 0),
            }
            status_color = status_colors.get(status, (150, 150, 150))
            self.ui.label(
                status.capitalize(), x + 15, list_y + 32, size=12, color=status_color
            )

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                x + 10 <= mouse_pos[0] <= x + width - 10
                and list_y <= mouse_pos[1] <= list_y + item_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.current_quest = quest

            list_y += item_height + 5

    def _render_quest_details(self, x: int, y: int, width: int, height: int):
        """Render quest details editor."""
        self.ui.panel(x, y, width, height, (30, 30, 45))

        current_y = y + 10

        # Quest name
        quest_name = self.current_quest.get("name", "Untitled Quest")
        self.ui.label("Quest Name:", x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        self.ui.panel(x + 10, current_y, width - 20, 35, (50, 50, 70))
        self.ui.label(quest_name, x + 15, current_y + 8, size=16)
        current_y += 45

        # Quest description
        self.ui.label("Description:", x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        description = self.current_quest.get("description", "No description")
        self.ui.panel(x + 10, current_y, width - 20, 80, (50, 50, 70))
        self.ui.label(description, x + 15, current_y + 10, size=14)
        current_y += 90

        # Objectives
        self.ui.label("Objectives:", x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        objectives = self.current_quest.get("objectives", [])
        for i, objective in enumerate(objectives[:5]):
            objective_text = objective.get("text", "")
            complete = objective.get("complete", False)
            color = (0, 255, 0) if complete else (255, 255, 255)

            checkbox_text = "[X]" if complete else "[ ]"
            self.ui.label(
                f"{checkbox_text} {objective_text}",
                x + 15,
                current_y,
                size=14,
                color=color,
            )
            current_y += 22

        current_y += 10

        if self.ui.button(
            "+ Add Objective", x + 10, current_y, 200, 30, color=(0, 100, 150)
        ):
            if "objectives" not in self.current_quest:
                self.current_quest["objectives"] = []
            self.current_quest["objectives"].append(
                {
                    "text": f'Objective {len(self.current_quest["objectives"]) + 1}',
                    "complete": False,
                }
            )

        current_y += 40

        # Rewards
        self.ui.label("Rewards:", x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        rewards = self.current_quest.get("rewards", {})
        for reward_type, amount in rewards.items():
            self.ui.label(
                f"{reward_type.capitalize()}: {amount}",
                x + 15,
                current_y,
                size=14,
                color=(255, 200, 100),
            )
            current_y += 22

        current_y += 10

        # Action buttons
        button_y = y + height - 50

        if self.ui.button("Save Quest", x + 10, button_y, 150, 35, color=(0, 150, 0)):
            self.save_quest(self.current_quest)

        if self.ui.button(
            "Delete Quest", x + 170, button_y, 150, 35, color=(150, 0, 0)
        ):
            self.delete_quest(self.current_quest)

    def _render_dialogue_editor(self, x: int, y: int, width: int, height: int):
        """Render the dialogue editor interface."""
        # Split into list and node editor
        list_width = 300
        editor_x = x + list_width + 20

        # Dialogue list
        self._render_dialogue_list(x + 10, y, list_width, height)

        # Dialogue tree editor
        if self.current_dialogue:
            self._render_dialogue_tree(editor_x, y, width - list_width - 40, height)
        else:
            self.ui.label(
                "Select a dialogue or create a new one",
                editor_x + 150,
                y + height // 2,
                size=16,
                color=(150, 150, 150),
            )

    def _render_dialogue_list(self, x: int, y: int, width: int, height: int):
        """Render the list of dialogue trees."""
        self.ui.panel(x, y, width, height, (30, 30, 45))
        self.ui.label("Dialogues", x + 10, y + 10, size=18, color=(200, 200, 255))

        # New dialogue button
        if self.ui.button(
            "+ New Dialogue", x + 10, y + 40, width - 20, 35, color=(0, 120, 0)
        ):
            self.create_new_dialogue()

        # Dialogue list
        list_y = y + 85
        item_height = 60

        for i, dialogue in enumerate(self.dialogues):
            if list_y + item_height > y + height - 10:
                break

            is_selected = self.current_dialogue == dialogue

            # Dialogue item
            item_color = (60, 100, 60) if is_selected else (40, 60, 40)
            self.ui.panel(x + 10, list_y, width - 20, item_height, item_color)

            # Dialogue name
            dialogue_name = dialogue.get("name", "Untitled Dialogue")
            self.ui.label(
                dialogue_name, x + 15, list_y + 10, size=16, color=(255, 255, 255)
            )

            # Node count
            node_count = len(dialogue.get("nodes", []))
            self.ui.label(
                f"{node_count} nodes",
                x + 15,
                list_y + 32,
                size=12,
                color=(200, 200, 200),
            )

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                x + 10 <= mouse_pos[0] <= x + width - 10
                and list_y <= mouse_pos[1] <= list_y + item_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.current_dialogue = dialogue

            list_y += item_height + 5

    def _render_dialogue_tree(self, x: int, y: int, width: int, height: int):
        """Render dialogue tree editor."""
        self.ui.panel(x, y, width, height, (30, 30, 45))

        # Dialogue name
        dialogue_name = self.current_dialogue.get("name", "Untitled Dialogue")
        self.ui.label(
            f"Dialogue: {dialogue_name}", x + 10, y + 10, size=18, color=(255, 255, 100)
        )

        # Node visualization area
        node_area_y = y + 50
        node_area_height = height - 100

        nodes = self.current_dialogue.get("nodes", [])

        if not nodes:
            self.ui.label(
                "No nodes yet. Add a node to start!",
                x + width // 2 - 100,
                y + height // 2,
                size=14,
                color=(150, 150, 150),
            )
        else:
            # Simple list view of nodes (in a full implementation, this would be a visual graph)
            current_y = node_area_y + 10

            for i, node in enumerate(nodes[:8]):
                node_text = node.get("text", "Empty node")
                node_type = node.get("type", "text")

                # Node item
                self.ui.panel(x + 10, current_y, width - 20, 60, (50, 50, 80))

                # Node number
                self.ui.label(
                    f"#{i}", x + 15, current_y + 10, size=14, color=(255, 200, 0)
                )

                # Node text (truncated)
                truncated_text = (
                    node_text[:50] + "..." if len(node_text) > 50 else node_text
                )
                self.ui.label(truncated_text, x + 50, current_y + 10, size=14)

                # Node type
                type_colors = {
                    "text": (200, 200, 200),
                    "choice": (100, 200, 255),
                    "end": (255, 100, 100),
                }
                self.ui.label(
                    node_type.capitalize(),
                    x + 50,
                    current_y + 32,
                    size=12,
                    color=type_colors.get(node_type, (200, 200, 200)),
                )

                # Edit button
                if self.ui.button(
                    "Edit", x + width - 90, current_y + 15, 70, 30, color=(0, 100, 150)
                ):
                    self.selected_node = i

                current_y += 65

        # Action buttons
        button_y = y + height - 45

        if self.ui.button("+ Add Node", x + 10, button_y, 140, 35, color=(0, 120, 0)):
            self.add_dialogue_node()

        if self.ui.button(
            "Save Dialogue", x + 160, button_y, 140, 35, color=(0, 150, 0)
        ):
            self.save_dialogue(self.current_dialogue)

        if self.ui.button(
            "Delete Dialogue", x + 310, button_y, 140, 35, color=(150, 0, 0)
        ):
            self.delete_dialogue(self.current_dialogue)

    # Data management methods

    def create_new_quest(self):
        """Create a new quest."""
        new_quest = {
            "name": f"New Quest {len(self.quests) + 1}",
            "description": "Quest description here",
            "objectives": [],
            "rewards": {},
            "status": "draft",
        }
        self.quests.append(new_quest)
        self.current_quest = new_quest

    def create_new_dialogue(self):
        """Create a new dialogue."""
        new_dialogue = {
            "name": f"New Dialogue {len(self.dialogues) + 1}",
            "nodes": [],
        }
        self.dialogues.append(new_dialogue)
        self.current_dialogue = new_dialogue

    def add_dialogue_node(self):
        """Add a node to the current dialogue."""
        if not self.current_dialogue:
            return

        if "nodes" not in self.current_dialogue:
            self.current_dialogue["nodes"] = []

        new_node = {
            "text": "Node text here",
            "type": "text",
            "next": None,
            "choices": [],
        }
        self.current_dialogue["nodes"].append(new_node)

    def save_quest(self, quest: Dict):
        """Save a quest to file."""
        filename = f"quests/{quest['name'].lower().replace(' ', '_')}.json"
        print(f"Saving quest to {filename}")
        # In a real implementation, would save to file

    def save_dialogue(self, dialogue: Dict):
        """Save a dialogue to file."""
        filename = f"dialogues/{dialogue['name'].lower().replace(' ', '_')}.json"
        print(f"Saving dialogue to {filename}")
        # In a real implementation, would save to file

    def delete_quest(self, quest: Dict):
        """Delete a quest."""
        if quest in self.quests:
            self.quests.remove(quest)
            self.current_quest = None

    def delete_dialogue(self, dialogue: Dict):
        """Delete a dialogue."""
        if dialogue in self.dialogues:
            self.dialogues.remove(dialogue)
            self.current_dialogue = None

    def load_quests(self):
        """Load quests from files."""
        # In a real implementation, would load from files
        pass

    def load_dialogues(self):
        """Load dialogues from files."""
        # In a real implementation, would load from files
        pass
