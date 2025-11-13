"""
Event Command System

RPG-style event command system for cutscenes, dialogue, and scripted sequences.
Inspired by RPG Maker's event system but adapted for NeonWorks.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json


class CommandType(Enum):
    """Types of event commands"""

    # Message commands
    SHOW_TEXT = auto()
    SHOW_CHOICES = auto()
    INPUT_NUMBER = auto()

    # Flow control
    CONDITIONAL_BRANCH = auto()
    LOOP = auto()
    BREAK_LOOP = auto()
    EXIT_EVENT = auto()
    COMMON_EVENT = auto()
    LABEL = auto()
    JUMP_TO_LABEL = auto()
    COMMENT = auto()

    # Game progression
    CONTROL_SWITCHES = auto()
    CONTROL_VARIABLES = auto()
    CONTROL_SELF_SWITCH = auto()
    CONTROL_TIMER = auto()

    # Character control
    TRANSFER_PLAYER = auto()
    SET_MOVEMENT_ROUTE = auto()
    SHOW_ANIMATION = auto()
    SHOW_BALLOON = auto()
    ERASE_EVENT = auto()

    # Screen effects
    FADEOUT_SCREEN = auto()
    FADEIN_SCREEN = auto()
    TINT_SCREEN = auto()
    FLASH_SCREEN = auto()
    SHAKE_SCREEN = auto()
    WAIT = auto()

    # Picture/UI commands
    SHOW_PICTURE = auto()
    MOVE_PICTURE = auto()
    ERASE_PICTURE = auto()

    # Audio commands
    PLAY_BGM = auto()
    FADEOUT_BGM = auto()
    PLAY_BGS = auto()
    FADEOUT_BGS = auto()
    PLAY_ME = auto()
    PLAY_SE = auto()

    # Battle/Scene
    BATTLE_PROCESSING = auto()
    SHOP_PROCESSING = auto()
    NAME_INPUT_PROCESSING = auto()

    # Party/Actor
    CHANGE_PARTY_MEMBER = auto()
    CHANGE_HP = auto()
    CHANGE_MP = auto()
    CHANGE_STATE = auto()
    RECOVER_ALL = auto()
    CHANGE_EXP = auto()
    CHANGE_LEVEL = auto()
    CHANGE_SKILLS = auto()
    CHANGE_EQUIPMENT = auto()
    CHANGE_NAME = auto()
    CHANGE_CLASS = auto()

    # Items/Weapons/Armor
    CHANGE_ITEMS = auto()
    CHANGE_WEAPONS = auto()
    CHANGE_ARMOR = auto()
    CHANGE_GOLD = auto()

    # Script/Advanced
    SCRIPT = auto()
    PLUGIN_COMMAND = auto()


class TriggerType(Enum):
    """Event trigger conditions"""

    ACTION_BUTTON = auto()  # Triggered when player presses action button
    PLAYER_TOUCH = auto()  # Triggered when player touches event
    EVENT_TOUCH = auto()  # Triggered when event touches player
    AUTORUN = auto()  # Runs automatically every frame
    PARALLEL = auto()  # Runs in parallel with other events


class MoveType(Enum):
    """Event movement types"""

    FIXED = auto()
    RANDOM = auto()
    APPROACH = auto()
    CUSTOM = auto()


class MoveSpeed(Enum):
    """Movement speed levels"""

    SLOWEST = 1
    SLOWER = 2
    SLOW = 3
    NORMAL = 4
    FAST = 5
    FASTER = 6
    FASTEST = 7


class MoveFrequency(Enum):
    """Movement frequency levels"""

    LOWEST = 1
    LOWER = 2
    LOW = 3
    NORMAL = 4
    HIGH = 5


class ComparisonOperator(Enum):
    """Comparison operators for conditional branches"""

    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="


@dataclass
class EventCommand:
    """
    Base class for event commands.

    Each command represents a single action in an event sequence.
    """

    command_type: CommandType
    parameters: Dict[str, Any] = field(default_factory=dict)
    indent: int = 0  # Indentation level for nested commands

    def execute(self, context: "EventContext") -> bool:
        """
        Execute this command.

        Args:
            context: Event execution context

        Returns:
            True if command completed, False if waiting
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "command_type": self.command_type.name,
            "parameters": self.parameters,
            "indent": self.indent,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventCommand":
        """Deserialize from dictionary"""
        command_type = CommandType[data["command_type"]]
        return cls(
            command_type=command_type,
            parameters=data.get("parameters", {}),
            indent=data.get("indent", 0),
        )


@dataclass
class ShowTextCommand(EventCommand):
    """Display text message to the player"""

    def __init__(
        self,
        text: str,
        face_name: Optional[str] = None,
        face_index: int = 0,
        background: int = 0,
        position: int = 2,
    ):
        super().__init__(
            command_type=CommandType.SHOW_TEXT,
            parameters={
                "text": text,
                "face_name": face_name,
                "face_index": face_index,
                "background": background,  # 0=normal, 1=dim, 2=transparent
                "position": position,  # 0=top, 1=middle, 2=bottom
            },
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would show text box and wait for player input
        return True


@dataclass
class ShowChoicesCommand(EventCommand):
    """Display choice selection to the player"""

    def __init__(
        self, choices: List[str], cancel_type: int = -1, default_choice: int = 0
    ):
        super().__init__(
            command_type=CommandType.SHOW_CHOICES,
            parameters={
                "choices": choices,
                "cancel_type": cancel_type,  # -1=disallow, 0-N=choice index
                "default_choice": default_choice,
            },
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would show choice box and store result
        return True


@dataclass
class ConditionalBranchCommand(EventCommand):
    """Conditional branch based on game state"""

    def __init__(self, condition_type: str, **kwargs):
        """
        Create conditional branch.

        condition_type can be:
        - "switch": Check switch state
        - "variable": Compare variable value
        - "self_switch": Check self switch
        - "timer": Check timer value
        - "actor": Check actor state
        - "enemy": Check enemy state
        - "character": Check character state
        - "gold": Check gold amount
        - "item": Check item possession
        - "weapon": Check weapon possession
        - "armor": Check armor possession
        - "button": Check button press
        - "script": Evaluate custom script
        """
        super().__init__(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={"condition_type": condition_type, **kwargs},
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would evaluate condition and set context branch
        return True


@dataclass
class ControlSwitchesCommand(EventCommand):
    """Control game switches"""

    def __init__(self, switch_id: int, value: bool, end_id: Optional[int] = None):
        """
        Set switch(es) to a value.

        Args:
            switch_id: Starting switch ID
            value: True for ON, False for OFF
            end_id: Optional ending switch ID for batch operations
        """
        super().__init__(
            command_type=CommandType.CONTROL_SWITCHES,
            parameters={"switch_id": switch_id, "value": value, "end_id": end_id},
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would set switches in game state
        return True


@dataclass
class ControlVariablesCommand(EventCommand):
    """Control game variables"""

    def __init__(
        self,
        variable_id: int,
        operation: str,
        operand_type: str,
        operand_value: Any,
        end_id: Optional[int] = None,
    ):
        """
        Modify game variable(s).

        Args:
            variable_id: Starting variable ID
            operation: "set", "add", "sub", "mul", "div", "mod"
            operand_type: "constant", "variable", "random"
            operand_value: Value or variable ID or random range
            end_id: Optional ending variable ID for batch operations
        """
        super().__init__(
            command_type=CommandType.CONTROL_VARIABLES,
            parameters={
                "variable_id": variable_id,
                "operation": operation,
                "operand_type": operand_type,
                "operand_value": operand_value,
                "end_id": end_id,
            },
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would modify variables in game state
        return True


@dataclass
class TransferPlayerCommand(EventCommand):
    """Transfer player to different location"""

    def __init__(
        self, map_id: int, x: int, y: int, direction: int = 0, fade_type: int = 0
    ):
        """
        Transfer player to a new location.

        Args:
            map_id: Target map ID (0 for current map)
            x: Target X coordinate
            y: Target Y coordinate
            direction: Player direction after transfer (0=retain, 2=down, 4=left, 6=right, 8=up)
            fade_type: 0=black, 1=white, 2=none
        """
        super().__init__(
            command_type=CommandType.TRANSFER_PLAYER,
            parameters={
                "map_id": map_id,
                "x": x,
                "y": y,
                "direction": direction,
                "fade_type": fade_type,
            },
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would transfer player
        return True


@dataclass
class WaitCommand(EventCommand):
    """Wait for specified duration"""

    def __init__(self, duration: int):
        """
        Wait command.

        Args:
            duration: Wait duration in frames (60 = 1 second at 60fps)
        """
        super().__init__(
            command_type=CommandType.WAIT, parameters={"duration": duration}
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would wait for duration
        return True


@dataclass
class PlayBGMCommand(EventCommand):
    """Play background music"""

    def __init__(self, name: str, volume: int = 90, pitch: int = 100, pan: int = 0):
        super().__init__(
            command_type=CommandType.PLAY_BGM,
            parameters={"name": name, "volume": volume, "pitch": pitch, "pan": pan},
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would play BGM
        return True


@dataclass
class PlaySECommand(EventCommand):
    """Play sound effect"""

    def __init__(self, name: str, volume: int = 90, pitch: int = 100, pan: int = 0):
        super().__init__(
            command_type=CommandType.PLAY_SE,
            parameters={"name": name, "volume": volume, "pitch": pitch, "pan": pan},
        )

    def execute(self, context: "EventContext") -> bool:
        # Implementation would play SE
        return True


@dataclass
class ScriptCommand(EventCommand):
    """Execute custom Python script"""

    def __init__(self, script: str):
        """
        Execute custom script.

        Args:
            script: Python code to execute
        """
        super().__init__(command_type=CommandType.SCRIPT, parameters={"script": script})

    def execute(self, context: "EventContext") -> bool:
        # Implementation would execute script in safe context
        return True


@dataclass
class EventPage:
    """
    A single page of an event with its own conditions and commands.

    Events can have multiple pages with different conditions.
    The highest priority page whose conditions are met will be active.
    """

    # Conditions
    condition_switch1_valid: bool = False
    condition_switch1_id: int = 1
    condition_switch2_valid: bool = False
    condition_switch2_id: int = 1
    condition_variable_valid: bool = False
    condition_variable_id: int = 1
    condition_variable_value: int = 0
    condition_self_switch_valid: bool = False
    condition_self_switch_ch: str = "A"
    condition_item_valid: bool = False
    condition_item_id: int = 1
    condition_actor_valid: bool = False
    condition_actor_id: int = 1

    # Graphics
    character_name: str = ""
    character_index: int = 0
    direction: int = 2  # 2=down, 4=left, 6=right, 8=up
    pattern: int = 0

    # Movement
    move_type: MoveType = MoveType.FIXED
    move_speed: MoveSpeed = MoveSpeed.NORMAL
    move_frequency: MoveFrequency = MoveFrequency.NORMAL
    move_route: List[Dict[str, Any]] = field(default_factory=list)

    # Options
    walk_anime: bool = True  # Animate while walking
    step_anime: bool = False  # Animate while stopped
    direction_fix: bool = False  # Fix direction
    through: bool = False  # Can pass through
    priority_type: int = 1  # 0=below, 1=same, 2=above

    # Trigger
    trigger: TriggerType = TriggerType.ACTION_BUTTON

    # Commands
    commands: List[EventCommand] = field(default_factory=list)

    def check_conditions(self, game_state: "GameState") -> bool:
        """
        Check if this page's conditions are met.

        Args:
            game_state: Current game state

        Returns:
            True if all conditions are met
        """
        # Check switch 1
        if self.condition_switch1_valid:
            if not game_state.get_switch(self.condition_switch1_id):
                return False

        # Check switch 2
        if self.condition_switch2_valid:
            if not game_state.get_switch(self.condition_switch2_id):
                return False

        # Check variable
        if self.condition_variable_valid:
            if (
                game_state.get_variable(self.condition_variable_id)
                < self.condition_variable_value
            ):
                return False

        # Check self switch
        if self.condition_self_switch_valid:
            # Would check self switch from event instance
            pass

        # Check item
        if self.condition_item_valid:
            if not game_state.has_item(self.condition_item_id):
                return False

        # Check actor
        if self.condition_actor_valid:
            if not game_state.has_actor(self.condition_actor_id):
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "conditions": {
                "switch1_valid": self.condition_switch1_valid,
                "switch1_id": self.condition_switch1_id,
                "switch2_valid": self.condition_switch2_valid,
                "switch2_id": self.condition_switch2_id,
                "variable_valid": self.condition_variable_valid,
                "variable_id": self.condition_variable_id,
                "variable_value": self.condition_variable_value,
                "self_switch_valid": self.condition_self_switch_valid,
                "self_switch_ch": self.condition_self_switch_ch,
                "item_valid": self.condition_item_valid,
                "item_id": self.condition_item_id,
                "actor_valid": self.condition_actor_valid,
                "actor_id": self.condition_actor_id,
            },
            "graphics": {
                "character_name": self.character_name,
                "character_index": self.character_index,
                "direction": self.direction,
                "pattern": self.pattern,
            },
            "movement": {
                "move_type": self.move_type.name,
                "move_speed": self.move_speed.value,
                "move_frequency": self.move_frequency.value,
                "move_route": self.move_route,
            },
            "options": {
                "walk_anime": self.walk_anime,
                "step_anime": self.step_anime,
                "direction_fix": self.direction_fix,
                "through": self.through,
                "priority_type": self.priority_type,
            },
            "trigger": self.trigger.name,
            "commands": [cmd.to_dict() for cmd in self.commands],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventPage":
        """Deserialize from dictionary"""
        conditions = data.get("conditions", {})
        graphics = data.get("graphics", {})
        movement = data.get("movement", {})
        options = data.get("options", {})

        page = cls(
            # Conditions
            condition_switch1_valid=conditions.get("switch1_valid", False),
            condition_switch1_id=conditions.get("switch1_id", 1),
            condition_switch2_valid=conditions.get("switch2_valid", False),
            condition_switch2_id=conditions.get("switch2_id", 1),
            condition_variable_valid=conditions.get("variable_valid", False),
            condition_variable_id=conditions.get("variable_id", 1),
            condition_variable_value=conditions.get("variable_value", 0),
            condition_self_switch_valid=conditions.get("self_switch_valid", False),
            condition_self_switch_ch=conditions.get("self_switch_ch", "A"),
            condition_item_valid=conditions.get("item_valid", False),
            condition_item_id=conditions.get("item_id", 1),
            condition_actor_valid=conditions.get("actor_valid", False),
            condition_actor_id=conditions.get("actor_id", 1),
            # Graphics
            character_name=graphics.get("character_name", ""),
            character_index=graphics.get("character_index", 0),
            direction=graphics.get("direction", 2),
            pattern=graphics.get("pattern", 0),
            # Movement
            move_type=MoveType[movement.get("move_type", "FIXED")],
            move_speed=MoveSpeed(movement.get("move_speed", 4)),
            move_frequency=MoveFrequency(movement.get("move_frequency", 4)),
            move_route=movement.get("move_route", []),
            # Options
            walk_anime=options.get("walk_anime", True),
            step_anime=options.get("step_anime", False),
            direction_fix=options.get("direction_fix", False),
            through=options.get("through", False),
            priority_type=options.get("priority_type", 1),
            # Trigger
            trigger=TriggerType[data.get("trigger", "ACTION_BUTTON")],
        )

        # Deserialize commands
        for cmd_data in data.get("commands", []):
            page.commands.append(EventCommand.from_dict(cmd_data))

        return page


@dataclass
class GameEvent:
    """
    A game event that can be triggered by player interaction or conditions.

    Events can have multiple pages, each with different conditions, graphics,
    and command lists. The active page is determined by condition priority.
    """

    id: int
    name: str
    x: int  # Map X position
    y: int  # Map Y position
    pages: List[EventPage] = field(default_factory=list)

    def get_active_page(self, game_state: "GameState") -> Optional[EventPage]:
        """
        Get the currently active page based on conditions.

        Pages are checked in reverse order (highest priority first).

        Args:
            game_state: Current game state

        Returns:
            Active EventPage or None if no conditions met
        """
        # Check pages in reverse order (last page has highest priority)
        for page in reversed(self.pages):
            if page.check_conditions(game_state):
                return page
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "pages": [page.to_dict() for page in self.pages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameEvent":
        """Deserialize from dictionary"""
        event = cls(id=data["id"], name=data["name"], x=data["x"], y=data["y"])

        for page_data in data.get("pages", []):
            event.pages.append(EventPage.from_dict(page_data))

        return event

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "GameEvent":
        """Deserialize from JSON string"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class EventContext:
    """
    Context for event execution.

    Maintains state during event processing including current command index,
    wait timers, and branch results.
    """

    event: GameEvent
    page: EventPage
    command_index: int = 0
    wait_count: int = 0
    branch_result: Optional[bool] = None
    loop_stack: List[int] = field(default_factory=list)

    def is_finished(self) -> bool:
        """Check if event has finished executing"""
        return self.command_index >= len(self.page.commands)

    def get_current_command(self) -> Optional[EventCommand]:
        """Get the current command to execute"""
        if self.is_finished():
            return None
        return self.page.commands[self.command_index]

    def advance(self):
        """Advance to next command"""
        self.command_index += 1

    def jump_to_label(self, label: str) -> bool:
        """
        Jump to a labeled command.

        Args:
            label: Label name to jump to

        Returns:
            True if label found, False otherwise
        """
        for i, cmd in enumerate(self.page.commands):
            if (
                cmd.command_type == CommandType.LABEL
                and cmd.parameters.get("name") == label
            ):
                self.command_index = i
                return True
        return False


# Type hints for external classes (to be implemented elsewhere)
class GameState:
    """Game state interface - to be implemented in game logic"""

    def get_switch(self, switch_id: int) -> bool:
        """Get switch value"""
        raise NotImplementedError

    def set_switch(self, switch_id: int, value: bool):
        """Set switch value"""
        raise NotImplementedError

    def get_variable(self, variable_id: int) -> int:
        """Get variable value"""
        raise NotImplementedError

    def set_variable(self, variable_id: int, value: int):
        """Set variable value"""
        raise NotImplementedError

    def has_item(self, item_id: int) -> bool:
        """Check if player has item"""
        raise NotImplementedError

    def has_actor(self, actor_id: int) -> bool:
        """Check if actor is in party"""
        raise NotImplementedError


def create_sample_event() -> GameEvent:
    """Create a sample event for demonstration"""
    event = GameEvent(id=1, name="Sample NPC", x=5, y=5)

    # Page 1: Default greeting
    page1 = EventPage(
        trigger=TriggerType.ACTION_BUTTON,
        character_name="Actor1",
        character_index=0,
        direction=2,
    )
    page1.commands = [
        ShowTextCommand("Hello, adventurer!"),
        ShowTextCommand("Welcome to NeonWorks!"),
        ShowChoicesCommand(["Tell me more", "Goodbye"], cancel_type=1),
        # Branch commands would go here based on choice
    ]
    event.pages.append(page1)

    # Page 2: After completing a quest (switch 1 is ON)
    page2 = EventPage(
        condition_switch1_valid=True,
        condition_switch1_id=1,
        trigger=TriggerType.ACTION_BUTTON,
        character_name="Actor1",
        character_index=0,
        direction=2,
    )
    page2.commands = [
        ShowTextCommand("Thank you for your help!"),
        ShowTextCommand("Here's a reward."),
        ControlVariablesCommand(
            variable_id=1, operation="add", operand_type="constant", operand_value=100
        ),
    ]
    event.pages.append(page2)

    return event
