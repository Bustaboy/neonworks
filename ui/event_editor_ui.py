"""
Visual Event Editor UI

Provides a visual interface for creating and editing game events with
triggers, conditions, and actions.

Hotkey: Ctrl+E
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

import pygame

from neonworks.ui.ui_system import (
    Panel,
    Button,
    Label,
    TextInput,
    Dropdown,
    Checkbox,
    ScrollPanel,
)


class EventEditorUI:
    """
    Visual event editor for creating game events.

    Features:
    - Event creation and editing
    - Trigger configuration (on_enter, on_interact, on_flag, etc.)
    - Condition builder
    - Action sequencing (message, battle, set_flag, etc.)
    - Visual event list
    - Save/load to map files
    """

    # Event trigger types
    TRIGGER_TYPES = [
        "on_enter",
        "on_exit",
        "on_interact",
        "on_flag",
        "on_timer",
        "on_battle_win",
        "on_battle_lose",
        "on_item_get",
        "boss_defeated",
    ]

    # Action types
    ACTION_TYPES = [
        "message",
        "battle",
        "set_flag",
        "give_item",
        "take_item",
        "give_gold",
        "heal_party",
        "play_sound",
        "play_music",
        "camera_shake",
        "screen_flash",
        "teleport",
        "change_map",
        "start_quest",
        "update_quest",
        "complete_quest",
        "open_shop",
        "show_dialogue",
        "spawn_entity",
        "remove_entity",
        "unlock_door",
        "credits",
    ]

    def __init__(self, world, renderer):
        """Initialize event editor UI."""
        self.world = world
        self.renderer = renderer
        self.visible = False

        # State
        self.current_map = None
        self.events = []
        self.selected_event = None
        self.selected_action_index = None

        # UI elements
        self._create_ui()

    def _create_ui(self):
        """Create UI elements."""
        screen_width = 1280
        screen_height = 720

        # Main panel
        self.main_panel = Panel(
            x=50,
            y=50,
            width=screen_width - 100,
            height=screen_height - 100,
            color=(40, 40, 50),
        )

        # Title
        self.title_label = Label(
            text="Event Editor (Ctrl+E)", x=70, y=70, font_size=24, color=(255, 255, 255)
        )

        # Event list panel (left side)
        self.event_list_panel = ScrollPanel(
            x=70, y=120, width=300, height=500, color=(50, 50, 60)
        )

        self.event_list_label = Label(
            text="Events:", x=80, y=130, font_size=16, color=(200, 200, 200)
        )

        # Event details panel (right side)
        self.details_panel = Panel(
            x=400, y=120, width=800, height=500, color=(50, 50, 60)
        )

        self.details_label = Label(
            text="Event Details:", x=410, y=130, font_size=16, color=(200, 200, 200)
        )

        # Event ID input
        self.id_label = Label(text="Event ID:", x=410, y=170, font_size=14)
        self.id_input = TextInput(x=500, y=165, width=200, height=30)

        # Trigger type dropdown
        self.trigger_label = Label(text="Trigger:", x=410, y=210, font_size=14)
        self.trigger_dropdown = Dropdown(
            x=500, y=205, width=200, height=30, options=self.TRIGGER_TYPES
        )

        # Condition input
        self.condition_label = Label(text="Condition:", x=410, y=250, font_size=14)
        self.condition_input = TextInput(x=500, y=245, width=300, height=30)
        self.condition_help = Label(
            text="e.g., game_flags.visited_forest",
            x=810,
            y=250,
            font_size=10,
            color=(150, 150, 150),
        )

        # Probability (for random events)
        self.probability_label = Label(text="Probability:", x=410, y=290, font_size=14)
        self.probability_input = TextInput(x=500, y=285, width=100, height=30)
        self.probability_help = Label(
            text="0.0 - 1.0 (0.3 = 30% chance)",
            x=610,
            y=290,
            font_size=10,
            color=(150, 150, 150),
        )

        # Actions list
        self.actions_label = Label(text="Actions:", x=410, y=330, font_size=14)
        self.actions_scroll = ScrollPanel(
            x=410, y=360, width=750, height=200, color=(40, 40, 50)
        )

        # Action buttons
        self.add_action_button = Button(
            text="Add Action", x=410, y=570, width=120, height=30, on_click=self.add_action
        )

        self.remove_action_button = Button(
            text="Remove Action",
            x=540,
            y=570,
            width=120,
            height=30,
            on_click=self.remove_action,
        )

        self.move_action_up_button = Button(
            text="Move Up", x=670, y=570, width=80, height=30, on_click=self.move_action_up
        )

        self.move_action_down_button = Button(
            text="Move Down",
            x=760,
            y=570,
            width=100,
            height=30,
            on_click=self.move_action_down,
        )

        # Bottom buttons
        self.new_event_button = Button(
            text="New Event", x=70, y=640, width=120, height=35, on_click=self.new_event
        )

        self.delete_event_button = Button(
            text="Delete Event",
            x=200,
            y=640,
            width=120,
            height=35,
            on_click=self.delete_event,
        )

        self.save_button = Button(
            text="Save Events", x=950, y=640, width=120, height=35, on_click=self.save_events
        )

        self.close_button = Button(
            text="Close", x=1080, y=640, width=100, height=35, on_click=self.close
        )

    def load_map_events(self, map_path: str):
        """Load events from a map file."""
        try:
            map_file = Path(map_path)
            if not map_file.exists():
                return

            with open(map_file, "r") as f:
                map_data = json.load(f)

            self.current_map = map_path
            self.events = map_data.get("events", [])
            self.selected_event = None
            self.selected_action_index = None

        except Exception as e:
            print(f"Error loading map events: {e}")

    def save_events(self):
        """Save events back to map file."""
        if not self.current_map:
            print("No map loaded")
            return

        try:
            map_file = Path(self.current_map)
            with open(map_file, "r") as f:
                map_data = json.load(f)

            map_data["events"] = self.events

            with open(map_file, "w") as f:
                json.dump(map_data, f, indent=2)

            print(f"Events saved to {self.current_map}")

        except Exception as e:
            print(f"Error saving events: {e}")

    def new_event(self):
        """Create a new event."""
        event_id = f"event_{len(self.events) + 1}"
        new_event = {
            "id": event_id,
            "trigger": "on_enter",
            "condition": "",
            "actions": [],
        }
        self.events.append(new_event)
        self.selected_event = new_event

    def delete_event(self):
        """Delete the selected event."""
        if self.selected_event and self.selected_event in self.events:
            self.events.remove(self.selected_event)
            self.selected_event = None

    def add_action(self):
        """Add a new action to the selected event."""
        if not self.selected_event:
            return

        # Default action (message)
        new_action = {"type": "message", "text": "New message"}

        if "actions" not in self.selected_event:
            self.selected_event["actions"] = []

        self.selected_event["actions"].append(new_action)

    def remove_action(self):
        """Remove the selected action."""
        if (
            self.selected_event
            and self.selected_action_index is not None
            and "actions" in self.selected_event
        ):
            actions = self.selected_event["actions"]
            if 0 <= self.selected_action_index < len(actions):
                actions.pop(self.selected_action_index)
                self.selected_action_index = None

    def move_action_up(self):
        """Move selected action up."""
        if (
            self.selected_event
            and self.selected_action_index is not None
            and self.selected_action_index > 0
        ):
            actions = self.selected_event["actions"]
            idx = self.selected_action_index
            actions[idx], actions[idx - 1] = actions[idx - 1], actions[idx]
            self.selected_action_index -= 1

    def move_action_down(self):
        """Move selected action down."""
        if (
            self.selected_event
            and self.selected_action_index is not None
            and "actions" in self.selected_event
        ):
            actions = self.selected_event["actions"]
            idx = self.selected_action_index
            if idx < len(actions) - 1:
                actions[idx], actions[idx + 1] = actions[idx + 1], actions[idx]
                self.selected_action_index += 1

    def update(self, dt: float):
        """Update event editor."""
        if not self.visible:
            return

        # Update UI elements
        self.main_panel.update(dt)
        self.event_list_panel.update(dt)
        self.details_panel.update(dt)

        # Update inputs
        if self.selected_event:
            self.id_input.update(dt)
            self.trigger_dropdown.update(dt)
            self.condition_input.update(dt)
            self.probability_input.update(dt)
            self.actions_scroll.update(dt)

        # Update buttons
        self.new_event_button.update(dt)
        self.delete_event_button.update(dt)
        self.add_action_button.update(dt)
        self.remove_action_button.update(dt)
        self.move_action_up_button.update(dt)
        self.move_action_down_button.update(dt)
        self.save_button.update(dt)
        self.close_button.update(dt)

        # Sync selected event with UI
        if self.selected_event:
            self.selected_event["id"] = self.id_input.text
            self.selected_event["trigger"] = self.trigger_dropdown.selected
            self.selected_event["condition"] = self.condition_input.text

            prob_text = self.probability_input.text
            if prob_text:
                try:
                    self.selected_event["probability"] = float(prob_text)
                except ValueError:
                    pass

    def render(self, screen: pygame.Surface):
        """Render event editor UI."""
        if not self.visible:
            return

        # Render panels
        self.main_panel.render(screen)
        self.title_label.render(screen)

        # Render event list
        self.event_list_panel.render(screen)
        self.event_list_label.render(screen)

        y_offset = 160
        for i, event in enumerate(self.events):
            event_id = event.get("id", f"event_{i}")
            color = (100, 200, 100) if event == self.selected_event else (200, 200, 200)

            event_label = Label(text=f"• {event_id}", x=80, y=y_offset, color=color)
            event_label.render(screen)
            y_offset += 25

        # Render details panel
        self.details_panel.render(screen)

        if self.selected_event:
            self.details_label.render(screen)
            self.id_label.render(screen)
            self.id_input.render(screen)
            self.trigger_label.render(screen)
            self.trigger_dropdown.render(screen)
            self.condition_label.render(screen)
            self.condition_input.render(screen)
            self.condition_help.render(screen)
            self.probability_label.render(screen)
            self.probability_input.render(screen)
            self.probability_help.render(screen)

            # Render actions
            self.actions_label.render(screen)
            self.actions_scroll.render(screen)

            actions = self.selected_event.get("actions", [])
            y_offset = 370
            for i, action in enumerate(actions):
                action_type = action.get("type", "unknown")
                color = (100, 200, 100) if i == self.selected_action_index else (200, 200, 200)

                # Truncate action display
                action_str = json.dumps(action)
                if len(action_str) > 60:
                    action_str = action_str[:57] + "..."

                action_label = Label(
                    text=f"{i + 1}. {action_type}: {action_str}",
                    x=420,
                    y=y_offset,
                    font_size=12,
                    color=color,
                )
                action_label.render(screen)
                y_offset += 30

            # Render action buttons
            self.add_action_button.render(screen)
            self.remove_action_button.render(screen)
            self.move_action_up_button.render(screen)
            self.move_action_down_button.render(screen)

        # Render bottom buttons
        self.new_event_button.render(screen)
        self.delete_event_button.render(screen)
        self.save_button.render(screen)
        self.close_button.render(screen)

    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if not self.visible:
            return

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return

            # Ctrl+E to toggle
            if event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.toggle()
                return

        # Handle UI events
        if self.selected_event:
            self.id_input.handle_event(event)
            self.trigger_dropdown.handle_event(event)
            self.condition_input.handle_event(event)
            self.probability_input.handle_event(event)
            self.add_action_button.handle_event(event)
            self.remove_action_button.handle_event(event)
            self.move_action_up_button.handle_event(event)
            self.move_action_down_button.handle_event(event)

        self.new_event_button.handle_event(event)
        self.delete_event_button.handle_event(event)
        self.save_button.handle_event(event)
        self.close_button.handle_event(event)

        # Event list click detection
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check event list clicks
            if 80 <= mouse_x <= 350 and 160 <= mouse_y <= 620:
                index = (mouse_y - 160) // 25
                if 0 <= index < len(self.events):
                    self.selected_event = self.events[index]
                    self._load_selected_event()

            # Check action list clicks
            if self.selected_event and 420 <= mouse_x <= 1140 and 370 <= mouse_y <= 560:
                index = (mouse_y - 370) // 30
                actions = self.selected_event.get("actions", [])
                if 0 <= index < len(actions):
                    self.selected_action_index = index

    def _load_selected_event(self):
        """Load selected event data into UI."""
        if not self.selected_event:
            return

        self.id_input.text = self.selected_event.get("id", "")
        self.trigger_dropdown.selected = self.selected_event.get("trigger", "on_enter")
        self.condition_input.text = self.selected_event.get("condition", "")

        probability = self.selected_event.get("probability", "")
        self.probability_input.text = str(probability) if probability else ""

    def toggle(self):
        """Toggle event editor visibility."""
        self.visible = not self.visible

    def close(self):
        """Close event editor."""
        self.visible = False


def get_event_editor(world, renderer):
    """Get or create event editor instance."""
    if not hasattr(get_event_editor, "_instance"):
        get_event_editor._instance = EventEditorUI(world, renderer)
    return get_event_editor._instance
