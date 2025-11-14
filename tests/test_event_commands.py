"""
Comprehensive tests for Event Command System

Tests event commands, event pages, and game events with serialization.
"""

import json
from dataclasses import dataclass

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
    MoveFrequency,
    MoveSpeed,
    MoveType,
    PlayBGMCommand,
    PlaySECommand,
    ScriptCommand,
    ShowChoicesCommand,
    ShowTextCommand,
    TransferPlayerCommand,
    TriggerType,
    WaitCommand,
    create_sample_event,
)


# Mock GameState for testing
class MockGameState:
    """Mock game state for testing"""

    def __init__(self):
        self.switches = {}
        self.variables = {}
        self.items = set()
        self.actors = set()

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


class TestEventCommand:
    """Test basic event command functionality"""

    def test_command_creation(self):
        """Test creating basic event command"""
        cmd = EventCommand(
            command_type=CommandType.SHOW_TEXT, parameters={"text": "Hello"}, indent=0
        )
        assert cmd.command_type == CommandType.SHOW_TEXT
        assert cmd.parameters["text"] == "Hello"
        assert cmd.indent == 0

    def test_command_serialization(self):
        """Test command to_dict/from_dict"""
        cmd = EventCommand(command_type=CommandType.WAIT, parameters={"duration": 60}, indent=1)

        data = cmd.to_dict()
        assert data["command_type"] == "WAIT"
        assert data["parameters"]["duration"] == 60
        assert data["indent"] == 1

        # Deserialize
        cmd2 = EventCommand.from_dict(data)
        assert cmd2.command_type == CommandType.WAIT
        assert cmd2.parameters["duration"] == 60
        assert cmd2.indent == 1


class TestShowTextCommand:
    """Test ShowTextCommand"""

    def test_creation(self):
        """Test creating show text command"""
        cmd = ShowTextCommand(
            text="Hello, World!",
            face_name="Actor1",
            face_index=2,
            background=1,
            position=0,
        )

        assert cmd.command_type == CommandType.SHOW_TEXT
        assert cmd.parameters["text"] == "Hello, World!"
        assert cmd.parameters["face_name"] == "Actor1"
        assert cmd.parameters["face_index"] == 2
        assert cmd.parameters["background"] == 1
        assert cmd.parameters["position"] == 0

    def test_default_parameters(self):
        """Test default parameters"""
        cmd = ShowTextCommand("Test message")
        assert cmd.parameters["text"] == "Test message"
        assert cmd.parameters["face_name"] is None
        assert cmd.parameters["position"] == 2


class TestShowChoicesCommand:
    """Test ShowChoicesCommand"""

    def test_creation(self):
        """Test creating show choices command"""
        cmd = ShowChoicesCommand(choices=["Yes", "No", "Maybe"], cancel_type=2, default_choice=0)

        assert cmd.command_type == CommandType.SHOW_CHOICES
        assert cmd.parameters["choices"] == ["Yes", "No", "Maybe"]
        assert cmd.parameters["cancel_type"] == 2
        assert cmd.parameters["default_choice"] == 0


class TestConditionalBranchCommand:
    """Test ConditionalBranchCommand"""

    def test_switch_condition(self):
        """Test switch condition"""
        cmd = ConditionalBranchCommand(condition_type="switch", switch_id=5, value=True)

        assert cmd.command_type == CommandType.CONDITIONAL_BRANCH
        assert cmd.parameters["condition_type"] == "switch"
        assert cmd.parameters["switch_id"] == 5
        assert cmd.parameters["value"] is True

    def test_variable_condition(self):
        """Test variable condition"""
        cmd = ConditionalBranchCommand(
            condition_type="variable", variable_id=10, operator=">=", value=100
        )

        assert cmd.parameters["condition_type"] == "variable"
        assert cmd.parameters["variable_id"] == 10
        assert cmd.parameters["operator"] == ">="
        assert cmd.parameters["value"] == 100


class TestControlCommands:
    """Test control commands (switches, variables)"""

    def test_control_switches_single(self):
        """Test controlling single switch"""
        cmd = ControlSwitchesCommand(switch_id=1, value=True)

        assert cmd.command_type == CommandType.CONTROL_SWITCHES
        assert cmd.parameters["switch_id"] == 1
        assert cmd.parameters["value"] is True
        assert cmd.parameters["end_id"] is None

    def test_control_switches_range(self):
        """Test controlling switch range"""
        cmd = ControlSwitchesCommand(switch_id=1, value=False, end_id=5)

        assert cmd.parameters["switch_id"] == 1
        assert cmd.parameters["end_id"] == 5
        assert cmd.parameters["value"] is False

    def test_control_variables(self):
        """Test controlling variables"""
        cmd = ControlVariablesCommand(
            variable_id=1, operation="add", operand_type="constant", operand_value=10
        )

        assert cmd.command_type == CommandType.CONTROL_VARIABLES
        assert cmd.parameters["variable_id"] == 1
        assert cmd.parameters["operation"] == "add"
        assert cmd.parameters["operand_type"] == "constant"
        assert cmd.parameters["operand_value"] == 10


class TestTransferPlayerCommand:
    """Test TransferPlayerCommand"""

    def test_creation(self):
        """Test creating transfer command"""
        cmd = TransferPlayerCommand(map_id=5, x=10, y=20, direction=2, fade_type=0)

        assert cmd.command_type == CommandType.TRANSFER_PLAYER
        assert cmd.parameters["map_id"] == 5
        assert cmd.parameters["x"] == 10
        assert cmd.parameters["y"] == 20
        assert cmd.parameters["direction"] == 2
        assert cmd.parameters["fade_type"] == 0


class TestAudioCommands:
    """Test audio commands"""

    def test_play_bgm(self):
        """Test BGM command"""
        cmd = PlayBGMCommand(name="Theme1", volume=80, pitch=110, pan=10)

        assert cmd.command_type == CommandType.PLAY_BGM
        assert cmd.parameters["name"] == "Theme1"
        assert cmd.parameters["volume"] == 80
        assert cmd.parameters["pitch"] == 110
        assert cmd.parameters["pan"] == 10

    def test_play_se(self):
        """Test SE command"""
        cmd = PlaySECommand(name="Coin", volume=100)

        assert cmd.command_type == CommandType.PLAY_SE
        assert cmd.parameters["name"] == "Coin"
        assert cmd.parameters["volume"] == 100


class TestScriptCommand:
    """Test ScriptCommand"""

    def test_creation(self):
        """Test creating script command"""
        script = "player.hp += 50"
        cmd = ScriptCommand(script=script)

        assert cmd.command_type == CommandType.SCRIPT
        assert cmd.parameters["script"] == script


class TestEventPage:
    """Test EventPage functionality"""

    def test_page_creation(self):
        """Test creating event page"""
        page = EventPage(
            trigger=TriggerType.ACTION_BUTTON,
            character_name="NPC1",
            direction=2,
            move_type=MoveType.RANDOM,
        )

        assert page.trigger == TriggerType.ACTION_BUTTON
        assert page.character_name == "NPC1"
        assert page.direction == 2
        assert page.move_type == MoveType.RANDOM

    def test_page_conditions_all_false(self):
        """Test page with no conditions active"""
        page = EventPage()
        game_state = MockGameState()

        # No conditions set, should return True
        assert page.check_conditions(game_state) is True

    def test_page_condition_switch(self):
        """Test page with switch condition"""
        page = EventPage(condition_switch1_valid=True, condition_switch1_id=5)

        game_state = MockGameState()

        # Switch not set, should fail
        assert page.check_conditions(game_state) is False

        # Set switch, should pass
        game_state.set_switch(5, True)
        assert page.check_conditions(game_state) is True

    def test_page_condition_multiple_switches(self):
        """Test page with multiple switch conditions"""
        page = EventPage(
            condition_switch1_valid=True,
            condition_switch1_id=1,
            condition_switch2_valid=True,
            condition_switch2_id=2,
        )

        game_state = MockGameState()

        # Both switches off
        assert page.check_conditions(game_state) is False

        # Only one switch on
        game_state.set_switch(1, True)
        assert page.check_conditions(game_state) is False

        # Both switches on
        game_state.set_switch(2, True)
        assert page.check_conditions(game_state) is True

    def test_page_condition_variable(self):
        """Test page with variable condition"""
        page = EventPage(
            condition_variable_valid=True,
            condition_variable_id=10,
            condition_variable_value=50,
        )

        game_state = MockGameState()

        # Variable below threshold
        game_state.set_variable(10, 30)
        assert page.check_conditions(game_state) is False

        # Variable at threshold
        game_state.set_variable(10, 50)
        assert page.check_conditions(game_state) is True

        # Variable above threshold
        game_state.set_variable(10, 100)
        assert page.check_conditions(game_state) is True

    def test_page_condition_item(self):
        """Test page with item condition"""
        page = EventPage(condition_item_valid=True, condition_item_id=15)

        game_state = MockGameState()

        # Don't have item
        assert page.check_conditions(game_state) is False

        # Have item
        game_state.items.add(15)
        assert page.check_conditions(game_state) is True

    def test_page_serialization(self):
        """Test page to_dict/from_dict"""
        page = EventPage(
            condition_switch1_valid=True,
            condition_switch1_id=10,
            character_name="Hero",
            character_index=1,
            direction=4,
            move_type=MoveType.APPROACH,
            move_speed=MoveSpeed.FAST,
            trigger=TriggerType.PLAYER_TOUCH,
        )

        # Add commands
        page.commands.append(ShowTextCommand("Hello!"))
        page.commands.append(WaitCommand(60))

        # Serialize
        data = page.to_dict()

        assert data["conditions"]["switch1_valid"] is True
        assert data["conditions"]["switch1_id"] == 10
        assert data["graphics"]["character_name"] == "Hero"
        assert data["movement"]["move_type"] == "APPROACH"
        assert data["trigger"] == "PLAYER_TOUCH"
        assert len(data["commands"]) == 2

        # Deserialize
        page2 = EventPage.from_dict(data)
        assert page2.condition_switch1_valid is True
        assert page2.condition_switch1_id == 10
        assert page2.character_name == "Hero"
        assert page2.move_type == MoveType.APPROACH
        assert page2.trigger == TriggerType.PLAYER_TOUCH
        assert len(page2.commands) == 2


class TestGameEvent:
    """Test GameEvent functionality"""

    def test_event_creation(self):
        """Test creating game event"""
        event = GameEvent(id=1, name="Test Event", x=5, y=10)

        assert event.id == 1
        assert event.name == "Test Event"
        assert event.x == 5
        assert event.y == 10
        assert len(event.pages) == 0

    def test_event_with_pages(self):
        """Test event with multiple pages"""
        event = GameEvent(id=1, name="NPC", x=0, y=0)

        # Page 1: Default
        page1 = EventPage()
        page1.commands.append(ShowTextCommand("Default message"))
        event.pages.append(page1)

        # Page 2: After switch 1
        page2 = EventPage(condition_switch1_valid=True, condition_switch1_id=1)
        page2.commands.append(ShowTextCommand("After quest"))
        event.pages.append(page2)

        assert len(event.pages) == 2

    def test_get_active_page_default(self):
        """Test getting active page with no conditions"""
        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage()
        event.pages.append(page)

        game_state = MockGameState()
        active_page = event.get_active_page(game_state)

        assert active_page == page

    def test_get_active_page_priority(self):
        """Test page priority (last page wins)"""
        event = GameEvent(id=1, name="Test", x=0, y=0)

        # Page 1: No conditions
        page1 = EventPage()
        event.pages.append(page1)

        # Page 2: Requires switch 1
        page2 = EventPage(condition_switch1_valid=True, condition_switch1_id=1)
        event.pages.append(page2)

        # Page 3: Requires switch 2
        page3 = EventPage(condition_switch1_valid=True, condition_switch1_id=2)
        event.pages.append(page3)

        game_state = MockGameState()

        # No switches set, should get page 1
        active = event.get_active_page(game_state)
        assert active == page1

        # Set switch 1, should get page 2
        game_state.set_switch(1, True)
        active = event.get_active_page(game_state)
        assert active == page2

        # Set switch 2, should get page 3 (higher priority)
        game_state.set_switch(2, True)
        active = event.get_active_page(game_state)
        assert active == page3

    def test_event_serialization(self):
        """Test event to_dict/from_dict"""
        event = GameEvent(id=5, name="Treasure Chest", x=10, y=15)

        page = EventPage()
        page.commands.append(ShowTextCommand("You found treasure!"))
        page.commands.append(ControlSwitchesCommand(1, True))
        event.pages.append(page)

        # Serialize
        data = event.to_dict()

        assert data["id"] == 5
        assert data["name"] == "Treasure Chest"
        assert data["x"] == 10
        assert data["y"] == 15
        assert len(data["pages"]) == 1

        # Deserialize
        event2 = GameEvent.from_dict(data)
        assert event2.id == 5
        assert event2.name == "Treasure Chest"
        assert event2.x == 10
        assert event2.y == 15
        assert len(event2.pages) == 1

    def test_event_json_serialization(self):
        """Test event to_json/from_json"""
        event = GameEvent(id=1, name="Test", x=5, y=5)
        page = EventPage()
        page.commands.append(ShowTextCommand("Test"))
        event.pages.append(page)

        # To JSON
        json_str = event.to_json()
        assert isinstance(json_str, str)
        assert "Test" in json_str

        # From JSON
        event2 = GameEvent.from_json(json_str)
        assert event2.id == 1
        assert event2.name == "Test"
        assert len(event2.pages) == 1


class TestEventContext:
    """Test EventContext functionality"""

    def test_context_creation(self):
        """Test creating event context"""
        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage()
        page.commands.append(ShowTextCommand("Hello"))
        page.commands.append(WaitCommand(30))

        context = EventContext(event=event, page=page)

        assert context.event == event
        assert context.page == page
        assert context.command_index == 0
        assert context.wait_count == 0

    def test_context_command_navigation(self):
        """Test navigating through commands"""
        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage()
        page.commands.append(ShowTextCommand("1"))
        page.commands.append(ShowTextCommand("2"))
        page.commands.append(ShowTextCommand("3"))

        context = EventContext(event=event, page=page)

        # First command
        cmd = context.get_current_command()
        assert cmd.parameters["text"] == "1"
        assert not context.is_finished()

        # Advance
        context.advance()
        cmd = context.get_current_command()
        assert cmd.parameters["text"] == "2"

        # Advance
        context.advance()
        cmd = context.get_current_command()
        assert cmd.parameters["text"] == "3"

        # Advance past end
        context.advance()
        assert context.is_finished()
        assert context.get_current_command() is None

    def test_context_jump_to_label(self):
        """Test jumping to label"""
        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage()

        # Create commands with labels
        page.commands.append(ShowTextCommand("Start"))
        page.commands.append(
            EventCommand(command_type=CommandType.LABEL, parameters={"name": "middle"})
        )
        page.commands.append(ShowTextCommand("Middle"))
        page.commands.append(
            EventCommand(command_type=CommandType.LABEL, parameters={"name": "end"})
        )
        page.commands.append(ShowTextCommand("End"))

        context = EventContext(event=event, page=page)

        # Jump to "middle"
        result = context.jump_to_label("middle")
        assert result is True
        assert context.command_index == 1

        # Jump to "end"
        result = context.jump_to_label("end")
        assert result is True
        assert context.command_index == 3

        # Jump to non-existent label
        result = context.jump_to_label("nonexistent")
        assert result is False


class TestSampleEvent:
    """Test sample event creation"""

    def test_create_sample_event(self):
        """Test creating sample event"""
        event = create_sample_event()

        assert event.id == 1
        assert event.name == "Sample NPC"
        assert event.x == 5
        assert event.y == 5
        assert len(event.pages) == 2

        # Check first page
        page1 = event.pages[0]
        assert page1.trigger == TriggerType.ACTION_BUTTON
        assert len(page1.commands) > 0

        # Check second page
        page2 = event.pages[1]
        assert page2.condition_switch1_valid is True
        assert page2.condition_switch1_id == 1


class TestEnums:
    """Test enum definitions"""

    def test_command_type_enum(self):
        """Test CommandType enum"""
        assert CommandType.SHOW_TEXT
        assert CommandType.CONDITIONAL_BRANCH
        assert CommandType.CONTROL_SWITCHES
        assert CommandType.PLAY_BGM

    def test_trigger_type_enum(self):
        """Test TriggerType enum"""
        assert TriggerType.ACTION_BUTTON
        assert TriggerType.PLAYER_TOUCH
        assert TriggerType.AUTORUN
        assert TriggerType.PARALLEL

    def test_move_type_enum(self):
        """Test MoveType enum"""
        assert MoveType.FIXED
        assert MoveType.RANDOM
        assert MoveType.APPROACH

    def test_move_speed_enum(self):
        """Test MoveSpeed enum values"""
        assert MoveSpeed.SLOWEST.value == 1
        assert MoveSpeed.NORMAL.value == 4
        assert MoveSpeed.FASTEST.value == 7
