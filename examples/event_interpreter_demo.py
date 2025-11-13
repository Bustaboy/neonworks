#!/usr/bin/env python
"""
Event Interpreter Demo

Demonstrates the event interpreter with sample events:
- Door event (locked and unlocked)
- Chest event (with items)
- NPC dialogue event (with choices)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from typing import Dict, List

from core.event_commands import (
    CommandType,
    EventCommand,
    EventContext,
    EventPage,
    GameEvent,
    GameState,
    TriggerType,
    ShowTextCommand,
    ShowChoicesCommand,
    ControlSwitchesCommand,
    ControlVariablesCommand,
    WaitCommand,
    PlaySECommand,
)
from core.events import EventManager
from engine.core.event_interpreter import EventInterpreter


class DemoGameState(GameState):
    """Demo game state implementation"""

    def __init__(self):
        self.switches: Dict[int, bool] = {}
        self.variables: Dict[int, int] = {}
        self.items: set = set()
        self.actors: set = set()

    def get_switch(self, switch_id: int) -> bool:
        return self.switches.get(switch_id, False)

    def set_switch(self, switch_id: int, value: bool):
        self.switches[switch_id] = value
        print(f"  [STATE] Switch {switch_id} = {value}")

    def get_variable(self, variable_id: int) -> int:
        return self.variables.get(variable_id, 0)

    def set_variable(self, variable_id: int, value: int):
        self.variables[variable_id] = value
        print(f"  [STATE] Variable {variable_id} = {value}")

    def has_item(self, item_id: int) -> bool:
        return item_id in self.items

    def has_actor(self, actor_id: int) -> bool:
        return actor_id in self.actors


def create_door_event(door_id: int, locked: bool = False) -> GameEvent:
    """Create a door event"""
    event = GameEvent(id=door_id, name=f"Door {door_id}", x=5, y=5)
    page = EventPage(trigger=TriggerType.ACTION_BUTTON)

    if locked:
        # Locked door requires key (variable 10 >= 1)
        page.commands = [
            ShowTextCommand("The door is locked."),
            EventCommand(
                command_type=CommandType.CONDITIONAL_BRANCH,
                parameters={
                    "condition_type": "variable",
                    "variable_id": 10,
                    "operator": ">=",
                    "value": 1,
                },
                indent=0,
            ),
            ShowTextCommand("You used the key!"),
            ControlSwitchesCommand(switch_id=door_id, value=True),
            PlaySECommand("door_open", volume=80),
            EventCommand(
                command_type=CommandType.CONDITIONAL_BRANCH,
                parameters={
                    "condition_type": "variable",
                    "variable_id": 10,
                    "operator": "<",
                    "value": 1,
                },
                indent=0,
            ),
            ShowTextCommand("You need a key to open this door."),
        ]
    else:
        # Simple unlocked door
        page.commands = [
            ShowTextCommand("You opened the door."),
            ControlSwitchesCommand(switch_id=door_id, value=True),
            PlaySECommand("door_open", volume=80),
        ]

    event.pages.append(page)
    return event


def create_chest_event(chest_id: int, item_name: str, item_id: int) -> GameEvent:
    """Create a chest event"""
    event = GameEvent(id=chest_id, name=f"Chest {chest_id}", x=10, y=10)

    # Page 1: Chest not yet opened
    page1 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page1.commands = [
        ShowTextCommand("You found a chest!"),
        WaitCommand(duration=30),  # Wait 0.5 seconds
        ShowTextCommand(f"You obtained {item_name}!"),
        ControlVariablesCommand(
            variable_id=item_id,
            operation="add",
            operand_type="constant",
            operand_value=1,
        ),
        ControlSwitchesCommand(switch_id=chest_id, value=True),
        PlaySECommand("item_get", volume=90),
    ]
    event.pages.append(page1)

    return event


def create_npc_event(npc_id: int, npc_name: str) -> GameEvent:
    """Create an NPC dialogue event"""
    event = GameEvent(id=npc_id, name=npc_name, x=15, y=15)
    page = EventPage(trigger=TriggerType.ACTION_BUTTON)

    page.commands = [
        ShowTextCommand(f"Hello! I'm {npc_name}."),
        ShowTextCommand("Welcome to NeonWorks!"),
        ShowChoicesCommand(
            choices=["Tell me about this place", "Goodbye"],
            cancel_type=1,
            default_choice=0,
        ),
        # Save choice result to variable 99
        ControlVariablesCommand(
            variable_id=99,
            operation="set",
            operand_type="constant",
            operand_value=0,  # Will be overwritten by choice
        ),
        # Mark as talked
        ControlSwitchesCommand(switch_id=npc_id, value=True),
    ]

    event.pages.append(page)
    return event


def create_loop_demo_event(event_id: int) -> GameEvent:
    """Create an event demonstrating loops"""
    event = GameEvent(id=event_id, name="Loop Demo", x=20, y=20)
    page = EventPage(trigger=TriggerType.ACTION_BUTTON)

    page.commands = [
        ShowTextCommand("Counting from 1 to 5..."),
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=0
        ),
        # Loop start
        EventCommand(command_type=CommandType.LOOP, parameters={}, indent=0),
        EventCommand(
            command_type=CommandType.CONTROL_VARIABLES,
            parameters={
                "variable_id": 1,
                "operation": "add",
                "operand_type": "constant",
                "operand_value": 1,
            },
            indent=1,
        ),
        # Check if >= 5
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={
                "condition_type": "variable",
                "variable_id": 1,
                "operator": ">=",
                "value": 5,
            },
            indent=1,
        ),
        EventCommand(command_type=CommandType.BREAK_LOOP, parameters={}, indent=2),
        ShowTextCommand("Counting complete!"),
    ]

    event.pages.append(page)
    return event


def run_event_demo(interpreter, event, game_state):
    """Run a single event demo"""
    print(f"\n{'='*60}")
    print(f"Running Event: {event.name} (ID: {event.id})")
    print(f"{'='*60}\n")

    page = event.pages[0]
    instance = interpreter.start_event(event, page)

    # Set up callbacks
    def on_show_text(text, params):
        print(f"  [TEXT] {text}")

    def on_show_choices(choices, default):
        print(f"  [CHOICE] Options:")
        for i, choice in enumerate(choices):
            print(f"    {i + 1}. {choice}")
        print(f"  [CHOICE] Selected: {choices[default]}")
        return default

    instance.on_show_text = on_show_text
    instance.on_show_choices = on_show_choices

    # Execute event
    max_iterations = 1000
    iterations = 0
    while not instance.is_finished() and iterations < max_iterations:
        interpreter.update(0.016)  # ~60fps
        iterations += 1

        # Auto-resume messages and choices for demo
        if instance.wait_for_message:
            interpreter.resume_message(event.id)
        if instance.wait_for_choice:
            interpreter.resume_choice(event.id, 0)

        if iterations >= max_iterations:
            print("  [ERROR] Maximum iterations reached!")
            break

    print(f"\n  [INFO] Event completed in {iterations} iterations")
    print(f"  [INFO] Commands executed: {interpreter.total_commands_executed}")


def main():
    """Main demo function"""
    print("\n" + "=" * 60)
    print("EVENT INTERPRETER DEMO")
    print("=" * 60)

    # Setup
    game_state = DemoGameState()
    event_manager = EventManager()
    interpreter = EventInterpreter(game_state, event_manager)

    # Demo 1: Simple unlocked door
    door_unlocked = create_door_event(door_id=100, locked=False)
    run_event_demo(interpreter, door_unlocked, game_state)

    # Demo 2: Locked door without key
    print("\n" + "-" * 60)
    print("Demo 2: Locked door (without key)")
    print("-" * 60)
    door_locked = create_door_event(door_id=101, locked=True)
    run_event_demo(interpreter, door_locked, game_state)

    # Demo 3: Locked door with key
    print("\n" + "-" * 60)
    print("Demo 3: Locked door (with key)")
    print("-" * 60)
    game_state.set_variable(10, 1)  # Give player a key
    door_locked2 = create_door_event(door_id=102, locked=True)
    run_event_demo(interpreter, door_locked2, game_state)

    # Demo 4: Chest event
    print("\n" + "-" * 60)
    print("Demo 4: Treasure chest")
    print("-" * 60)
    chest = create_chest_event(chest_id=200, item_name="Health Potion", item_id=50)
    run_event_demo(interpreter, chest, game_state)

    # Demo 5: NPC dialogue
    print("\n" + "-" * 60)
    print("Demo 5: NPC dialogue")
    print("-" * 60)
    npc = create_npc_event(npc_id=300, npc_name="Merchant Tom")
    run_event_demo(interpreter, npc, game_state)

    # Demo 6: Loop demonstration
    print("\n" + "-" * 60)
    print("Demo 6: Loop demonstration")
    print("-" * 60)
    loop_event = create_loop_demo_event(event_id=400)
    run_event_demo(interpreter, loop_event, game_state)

    # Final statistics
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    stats = interpreter.get_statistics()
    print(f"Total Events Completed: {stats['total_events_completed']}")
    print(f"Total Commands Executed: {stats['total_commands_executed']}")
    print(f"Running Events: {stats['running_events']}")
    print(f"Parallel Events: {stats['parallel_events']}")

    print("\n" + "=" * 60)
    print("GAME STATE")
    print("=" * 60)
    print(f"Switches: {dict(game_state.switches)}")
    print(f"Variables: {dict(game_state.variables)}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
