"""
Tests for Event Interpreter

Comprehensive tests for the event command interpreter including
flow control, wait states, and sample game events.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock

import pytest

from neonworks.core.event_commands import (
    CommandType,
    ConditionalBranchCommand,
    ControlSwitchesCommand,
    ControlVariablesCommand,
    EventCommand,
    EventContext,
    EventPage,
    GameEvent,
    GameState,
    PlayBGMCommand,
    PlaySECommand,
    ShowChoicesCommand,
    ShowTextCommand,
    TriggerType,
    WaitCommand,
)
from neonworks.core.events import Event, EventManager, EventType
from neonworks.engine.core.event_interpreter import (
    CommandExecutionError,
    EventInterpreter,
    InterpreterInstance,
    InterpreterState,
)


class MockGameState(GameState):
    """Mock game state for testing"""

    def __init__(self):
        self.switches: Dict[int, bool] = {}
        self.variables: Dict[int, int] = {}
        self.items: set = set()
        self.actors: set = set()

    def get_switch(self, switch_id: int) -> bool:
        return self.switches.get(switch_id, False)

    def set_switch(self, switch_id: int, value: bool):
        self.switches[switch_id] = value

    def get_variable(self, variable_id: int) -> int:
        return self.variables.get(variable_id, 0)

    def set_variable(self, variable_id: int, value: int):
        self.variables[variable_id] = value

    def has_item(self, item_id: int) -> bool:
        return item_id in self.items

    def has_actor(self, actor_id: int) -> bool:
        return actor_id in self.actors


@pytest.fixture
def game_state():
    """Create a mock game state"""
    return MockGameState()


@pytest.fixture
def event_manager():
    """Create an event manager"""
    return EventManager()


@pytest.fixture
def interpreter(game_state, event_manager):
    """Create an event interpreter"""
    return EventInterpreter(game_state, event_manager)


# ========== Basic Execution Tests ==========


def test_simple_command_execution(interpreter, game_state):
    """Test executing simple commands sequentially"""
    event = GameEvent(id=1, name="Test Event", x=0, y=0)
    page = EventPage()
    page.commands = [
        ControlSwitchesCommand(switch_id=1, value=True),
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=42
        ),
        ControlSwitchesCommand(switch_id=2, value=True),
    ]

    instance = interpreter.start_event(event, page)

    # Execute all commands
    while not instance.is_finished():
        interpreter.update(0.016)  # ~60fps

    assert game_state.get_switch(1) == True
    assert game_state.get_switch(2) == True
    assert game_state.get_variable(1) == 42


def test_wait_command(interpreter):
    """Test wait command functionality"""
    event = GameEvent(id=1, name="Wait Event", x=0, y=0)
    page = EventPage()
    page.commands = [
        WaitCommand(duration=30),  # Wait 30 frames
    ]

    instance = interpreter.start_event(event, page)

    # Should be waiting
    interpreter.update(0.016)
    assert instance.wait_frames == 29
    assert instance.is_waiting()

    # Update 29 more times
    for _ in range(29):
        interpreter.update(0.016)

    assert instance.wait_frames == 0
    assert not instance.is_waiting()
    assert instance.is_finished()


# ========== Flow Control Tests ==========


def test_conditional_branch_true(interpreter, game_state):
    """Test conditional branch when condition is true"""
    game_state.set_switch(1, True)

    event = GameEvent(id=1, name="Branch Event", x=0, y=0)
    page = EventPage()

    # Create commands manually to control indent levels
    branch_cmd = EventCommand(
        command_type=CommandType.CONDITIONAL_BRANCH,
        parameters={"condition_type": "switch", "switch_id": 1, "value": True},
        indent=0,
    )

    true_branch_cmd = EventCommand(
        command_type=CommandType.CONTROL_VARIABLES,
        parameters={
            "variable_id": 1,
            "operation": "set",
            "operand_type": "constant",
            "operand_value": 100,
        },
        indent=1,
    )

    page.commands = [branch_cmd, true_branch_cmd]

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    # Variable should be set because condition was true
    assert game_state.get_variable(1) == 100


def test_conditional_branch_false(interpreter, game_state):
    """Test conditional branch when condition is false"""
    game_state.set_switch(1, False)

    event = GameEvent(id=1, name="Branch Event", x=0, y=0)
    page = EventPage()

    branch_cmd = EventCommand(
        command_type=CommandType.CONDITIONAL_BRANCH,
        parameters={"condition_type": "switch", "switch_id": 1, "value": True},
        indent=0,
    )

    false_branch_cmd = EventCommand(
        command_type=CommandType.CONTROL_VARIABLES,
        parameters={
            "variable_id": 1,
            "operation": "set",
            "operand_type": "constant",
            "operand_value": 100,
        },
        indent=1,
    )

    page.commands = [branch_cmd, false_branch_cmd]

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    # Variable should NOT be set because condition was false
    assert game_state.get_variable(1) == 0


def test_loop_execution(interpreter, game_state):
    """Test loop execution"""
    event = GameEvent(id=1, name="Loop Event", x=0, y=0)
    page = EventPage()

    # Create a loop that increments a variable 5 times
    page.commands = [
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
        # Break loop when variable reaches 5
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
    ]

    instance = interpreter.start_event(event, page)

    # Execute with iteration limit to prevent infinite loop
    max_iterations = 1000
    iterations = 0
    while not instance.is_finished() and iterations < max_iterations:
        interpreter.update(0.016)
        iterations += 1

    assert game_state.get_variable(1) == 5
    assert iterations < max_iterations, "Loop did not break properly"


def test_label_jump(interpreter, game_state):
    """Test label and jump functionality"""
    event = GameEvent(id=1, name="Jump Event", x=0, y=0)
    page = EventPage()

    page.commands = [
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=1
        ),
        EventCommand(
            command_type=CommandType.JUMP_TO_LABEL,
            parameters={"label": "skip"},
            indent=0,
        ),
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=999
        ),  # Should be skipped
        EventCommand(
            command_type=CommandType.LABEL, parameters={"name": "skip"}, indent=0
        ),
        ControlVariablesCommand(
            variable_id=2, operation="set", operand_type="constant", operand_value=2
        ),
    ]

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    assert game_state.get_variable(1) == 1  # Should not be 999
    assert game_state.get_variable(2) == 2


def test_exit_event(interpreter, game_state):
    """Test exit event command"""
    event = GameEvent(id=1, name="Exit Event", x=0, y=0)
    page = EventPage()

    page.commands = [
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=1
        ),
        EventCommand(command_type=CommandType.EXIT_EVENT, parameters={}, indent=0),
        ControlVariablesCommand(
            variable_id=2, operation="set", operand_type="constant", operand_value=2
        ),  # Should not execute
    ]

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    assert game_state.get_variable(1) == 1
    assert game_state.get_variable(2) == 0  # Should not be set


# ========== Parallel Execution Tests ==========


def test_parallel_event_execution(interpreter, game_state):
    """Test parallel event execution"""
    event1 = GameEvent(id=1, name="Parallel Event 1", x=0, y=0)
    page1 = EventPage(trigger=TriggerType.PARALLEL)
    page1.commands = [
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=10
        ),
    ]

    event2 = GameEvent(id=2, name="Parallel Event 2", x=0, y=0)
    page2 = EventPage(trigger=TriggerType.PARALLEL)
    page2.commands = [
        ControlVariablesCommand(
            variable_id=2, operation="set", operand_type="constant", operand_value=20
        ),
    ]

    # Start both as parallel
    interpreter.start_event(event1, page1, is_parallel=True)
    interpreter.start_event(event2, page2, is_parallel=True)

    # Update both
    while len(interpreter.parallel_interpreters) > 0:
        interpreter.update(0.016)

    assert game_state.get_variable(1) == 10
    assert game_state.get_variable(2) == 20


# ========== Sample Game Events ==========


def create_door_event(door_id: int, locked: bool = False) -> GameEvent:
    """Create a sample door event"""
    event = GameEvent(id=door_id, name=f"Door {door_id}", x=5, y=5)

    page = EventPage(trigger=TriggerType.ACTION_BUTTON)

    if locked:
        # Locked door requires key
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
            ShowTextCommand("You used the key!", indent=1),
            ControlSwitchesCommand(switch_id=door_id, value=True, indent=1),
            PlaySECommand("door_open", volume=80, indent=1),
        ]
    else:
        # Simple door that opens
        page.commands = [
            ShowTextCommand("You opened the door."),
            ControlSwitchesCommand(switch_id=door_id, value=True),
            PlaySECommand("door_open", volume=80),
        ]

    event.pages.append(page)
    return event


def create_chest_event(chest_id: int, item_name: str, item_id: int) -> GameEvent:
    """Create a sample chest event"""
    event = GameEvent(id=chest_id, name=f"Chest {chest_id}", x=10, y=10)

    # Page 1: Chest not opened yet
    page1 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page1.commands = [
        ShowTextCommand("You found a chest!"),
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

    # Page 2: Chest already opened
    page2 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page2.condition_switch1_valid = True
    page2.condition_switch1_id = chest_id
    page2.commands = [
        ShowTextCommand("The chest is empty."),
    ]
    event.pages.append(page2)

    return event


def create_npc_dialogue_event(npc_id: int, npc_name: str) -> GameEvent:
    """Create a sample NPC dialogue event"""
    event = GameEvent(id=npc_id, name=npc_name, x=15, y=15)

    # Page 1: First meeting
    page1 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page1.commands = [
        ShowTextCommand(f"Hello! I'm {npc_name}."),
        ShowTextCommand("Welcome to NeonWorks!"),
        ShowChoicesCommand(
            choices=["Tell me about this place", "What can you do?", "Goodbye"],
            cancel_type=2,
            default_choice=0,
        ),
        # Choice 0: Tell me about this place
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={
                "condition_type": "variable",
                "variable_id": 0,
                "operator": "==",
                "value": 0,
            },
            indent=0,
        ),
        ShowTextCommand("This is a bustling city full of adventure!", indent=1),
        ShowTextCommand("Many travelers come here seeking their fortune.", indent=1),
        # Choice 1: What can you do?
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={
                "condition_type": "variable",
                "variable_id": 0,
                "operator": "==",
                "value": 1,
            },
            indent=0,
        ),
        ShowTextCommand("I'm a merchant! I sell various goods.", indent=1),
        ShowTextCommand("Come back when you have some gold!", indent=1),
        # Choice 2: Goodbye
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={
                "condition_type": "variable",
                "variable_id": 0,
                "operator": "==",
                "value": 2,
            },
            indent=0,
        ),
        ShowTextCommand("Safe travels, adventurer!", indent=1),
        # Mark as talked to
        ControlSwitchesCommand(switch_id=npc_id, value=True),
    ]
    event.pages.append(page1)

    # Page 2: Already met
    page2 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page2.condition_switch1_valid = True
    page2.condition_switch1_id = npc_id
    page2.commands = [
        ShowTextCommand(f"Hello again!"),
        ShowTextCommand("What can I help you with today?"),
    ]
    event.pages.append(page2)

    return event


def test_door_event(interpreter, game_state):
    """Test door event execution"""
    door = create_door_event(door_id=100, locked=False)
    page = door.pages[0]

    # Mock text display
    displayed_texts = []

    instance = interpreter.start_event(door, page)
    instance.on_show_text = lambda text, params: displayed_texts.append(text)

    # Execute first command (show text)
    interpreter.update(0.016)
    assert instance.wait_for_message == True

    # Resume after message
    interpreter.resume_message(door.id)

    # Continue execution
    while not instance.is_finished():
        interpreter.update(0.016)
        if instance.wait_for_message:
            interpreter.resume_message(door.id)

    assert "You opened the door." in displayed_texts
    assert game_state.get_switch(100) == True


def test_chest_event(interpreter, game_state):
    """Test chest event execution"""
    chest = create_chest_event(chest_id=200, item_name="Health Potion", item_id=50)
    page = chest.pages[0]

    displayed_texts = []

    instance = interpreter.start_event(chest, page)
    instance.on_show_text = lambda text, params: displayed_texts.append(text)

    # Execute event
    while not instance.is_finished():
        interpreter.update(0.016)
        if instance.wait_for_message:
            interpreter.resume_message(chest.id)

    assert "You found a chest!" in displayed_texts
    assert "You obtained Health Potion!" in displayed_texts
    assert game_state.get_variable(50) == 1  # Item obtained
    assert game_state.get_switch(200) == True  # Chest opened


def test_npc_dialogue_event(interpreter, game_state):
    """Test NPC dialogue event execution"""
    npc = create_npc_dialogue_event(npc_id=300, npc_name="Merchant Tom")
    page = npc.pages[0]

    displayed_texts = []

    instance = interpreter.start_event(npc, page)
    instance.on_show_text = lambda text, params: displayed_texts.append(text)
    instance.on_show_choices = lambda choices, default: 0  # Select first choice

    # Execute event
    while not instance.is_finished():
        interpreter.update(0.016)
        if instance.wait_for_message:
            interpreter.resume_message(npc.id)
        if instance.wait_for_choice:
            interpreter.resume_choice(npc.id, 0)

    assert "Hello! I'm Merchant Tom." in displayed_texts
    assert game_state.get_switch(300) == True  # Talked to NPC


# ========== Error Handling Tests ==========


def test_error_handling(interpreter, game_state):
    """Test error handling for invalid commands"""
    event = GameEvent(id=1, name="Error Event", x=0, y=0)
    page = EventPage()

    # Create command with invalid script
    page.commands = [
        EventCommand(
            command_type=CommandType.SCRIPT,
            parameters={"script": "raise ValueError('Test error')"},
            indent=0,
        ),
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=99
        ),
    ]

    errors_caught = []
    interpreter.on_error = lambda instance, error: errors_caught.append(error)

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    # Error should have been caught
    assert len(errors_caught) > 0 or instance.state == InterpreterState.ERROR


def test_label_not_found(interpreter, game_state):
    """Test jumping to non-existent label"""
    event = GameEvent(id=1, name="Jump Event", x=0, y=0)
    page = EventPage()

    page.commands = [
        EventCommand(
            command_type=CommandType.JUMP_TO_LABEL,
            parameters={"label": "nonexistent"},
            indent=0,
        ),
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=1
        ),
    ]

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    # Should continue to next command
    assert game_state.get_variable(1) == 1


# ========== Statistics Tests ==========


def test_interpreter_statistics(interpreter, game_state):
    """Test interpreter statistics tracking"""
    event = GameEvent(id=1, name="Stats Event", x=0, y=0)
    page = EventPage()
    page.commands = [
        ControlSwitchesCommand(switch_id=1, value=True),
        ControlSwitchesCommand(switch_id=2, value=True),
        ControlSwitchesCommand(switch_id=3, value=True),
    ]

    instance = interpreter.start_event(event, page)

    while not instance.is_finished():
        interpreter.update(0.016)

    stats = interpreter.get_statistics()
    assert stats["total_commands_executed"] >= 3
    assert stats["total_events_completed"] >= 1


# ========== Integration Tests ==========


def test_complex_event_flow(interpreter, game_state):
    """Test complex event with multiple flow control elements"""
    event = GameEvent(id=1, name="Complex Event", x=0, y=0)
    page = EventPage()

    page.commands = [
        # Set initial value
        ControlVariablesCommand(
            variable_id=1, operation="set", operand_type="constant", operand_value=0
        ),
        # Loop to increment
        EventCommand(command_type=CommandType.LOOP, parameters={}, indent=0),
        ControlVariablesCommand(
            variable_id=1,
            operation="add",
            operand_type="constant",
            operand_value=1,
            indent=1,
        ),
        # Break if >= 3
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={
                "condition_type": "variable",
                "variable_id": 1,
                "operator": ">=",
                "value": 3,
            },
            indent=1,
        ),
        EventCommand(command_type=CommandType.BREAK_LOOP, parameters={}, indent=2),
        # After loop, check value
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={
                "condition_type": "variable",
                "variable_id": 1,
                "operator": "==",
                "value": 3,
            },
            indent=0,
        ),
        ControlSwitchesCommand(switch_id=1, value=True, indent=1),
    ]

    instance = interpreter.start_event(event, page)

    max_iterations = 1000
    iterations = 0
    while not instance.is_finished() and iterations < max_iterations:
        interpreter.update(0.016)
        iterations += 1

    assert game_state.get_variable(1) == 3
    assert game_state.get_switch(1) == True
    assert iterations < max_iterations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
