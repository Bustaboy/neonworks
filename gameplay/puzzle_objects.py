"""
Puzzle Object Components

Components for dungeon puzzle mechanics like switches, plates, doors, etc.
"""

from typing import Optional, List, Callable, Dict
from dataclasses import dataclass, field
from enum import Enum
from neonworks.core.ecs import Component


class PuzzleState(Enum):
    """State of puzzle elements"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Switch(Component):
    """
    Switch/lever component for activating mechanisms.

    Can toggle doors, bridges, or other puzzle elements.
    """

    # State
    is_active: bool = False
    is_locked: bool = False  # Can't be toggled if locked

    # Type
    switch_type: str = "toggle"  # toggle, momentary, one-time
    is_momentary: bool = False  # Resets when not pressed
    is_one_time: bool = False  # Can only be activated once

    # Visual
    active_sprite: str = ""
    inactive_sprite: str = ""

    # Targets (entity IDs to activate/deactivate)
    target_ids: List[str] = field(default_factory=list)

    # Callbacks
    on_activate: Optional[Callable] = None
    on_deactivate: Optional[Callable] = None


@dataclass
class PressurePlate(Component):
    """
    Pressure plate component that activates when stepped on.

    Can require specific weight or number of objects.
    """

    # State
    is_pressed: bool = False
    is_locked: bool = False

    # Activation requirements
    required_weight: int = 1  # Number of entities required
    current_weight: int = 0  # Current entities on plate

    # Type
    stays_pressed: bool = False  # Stays pressed after activation
    reset_on_leave: bool = True  # Resets when nothing on it

    # What can activate it
    can_activate_by_player: bool = True
    can_activate_by_objects: bool = True
    can_activate_by_enemies: bool = False

    # Targets
    target_ids: List[str] = field(default_factory=list)

    # Callbacks
    on_press: Optional[Callable] = None
    on_release: Optional[Callable] = None

    # Currently on plate (entity IDs)
    entities_on_plate: List[str] = field(default_factory=list)


@dataclass
class PushableBlock(Component):
    """
    Pushable block component for block puzzles.

    Can be pushed by player onto plates or to create paths.
    """

    # State
    is_being_pushed: bool = False
    can_be_pulled: bool = False  # Can also be pulled

    # Properties
    weight: int = 1  # For pressure plates
    push_speed: float = 2.0  # Movement speed when pushed

    # Restrictions
    can_push_on_ice: bool = True  # Slides on ice floors
    stops_at_walls: bool = True
    can_fall_in_holes: bool = True

    # Visual
    normal_sprite: str = ""
    pushing_sprite: str = ""


@dataclass
class Door(Component):
    """
    Door component for locked/activated doors.

    Can be opened by switches, keys, or triggers.
    """

    # State
    is_open: bool = False
    is_locked: bool = True

    # Opening requirements
    requires_key: bool = False
    key_id: Optional[str] = None
    requires_switch: bool = True  # Opened by switches

    # Type
    door_type: str = "normal"  # normal, one-way, auto-close
    is_one_way: bool = False  # Can only pass in one direction
    auto_close: bool = False
    auto_close_delay: float = 2.0  # Seconds

    # Visual
    open_sprite: str = ""
    closed_sprite: str = ""

    # Callbacks
    on_open: Optional[Callable] = None
    on_close: Optional[Callable] = None


@dataclass
class TeleportPad(Component):
    """
    Teleport pad component for warping between locations.

    Instantly transports to target location when stepped on.
    """

    # Destination
    target_x: int = 0
    target_y: int = 0
    target_zone: Optional[str] = None  # None = same zone

    # Activation
    is_active: bool = True
    requires_activation: bool = False  # Must be activated first
    activation_switch_id: Optional[str] = None

    # Type
    is_two_way: bool = True  # Creates return teleport
    is_hidden: bool = False  # Invisible until activated

    # Visual
    active_sprite: str = ""
    inactive_sprite: str = ""
    teleport_effect: str = "sparkle"

    # Callbacks
    on_teleport: Optional[Callable[[int, int], None]] = None  # (from_x, from_y)


@dataclass
class IceTile(Component):
    """
    Ice floor component that makes entities slide.

    Entities slide until hitting obstacle.
    """

    # Properties
    is_active: bool = True
    friction: float = 0.0  # Very low friction

    # Slide behavior
    slide_speed: float = 8.0  # Speed of sliding
    stops_at_walls: bool = True
    stops_at_entities: bool = True


@dataclass
class Chest(Component):
    """
    Chest component for treasure containers.

    Contains items/gold that can be looted once.
    """

    # State
    is_open: bool = False
    is_locked: bool = False

    # Lock
    requires_key: bool = False
    key_id: Optional[str] = None

    # Contents
    gold: int = 0
    items: List[Dict[str, any]] = field(default_factory=list)  # item_id, quantity

    # Visual
    open_sprite: str = ""
    closed_sprite: str = ""

    # Callbacks
    on_open: Optional[Callable] = None


@dataclass
class CrackableWall(Component):
    """
    Crackable wall component for breakable barriers.

    Can be destroyed with special items/abilities.
    """

    # State
    is_destroyed: bool = False

    # Requirements
    required_item: Optional[str] = None  # e.g., "bomb", "pickaxe"
    required_spell: Optional[str] = None  # e.g., "earthquake"
    hp: int = 1  # Hits required to break

    # Visual
    intact_sprite: str = ""
    cracked_sprite: str = ""
    destroyed_sprite: str = ""

    # Rewards (optional)
    reveals_items: List[str] = field(default_factory=list)

    # Callbacks
    on_break: Optional[Callable] = None


@dataclass
class ConveyorBelt(Component):
    """
    Conveyor belt component that moves entities.

    Automatically moves entities in a direction.
    """

    # Direction (0=up, 1=right, 2=down, 3=left)
    direction: int = 2

    # Speed
    move_speed: float = 2.0

    # Properties
    is_active: bool = True
    affects_player: bool = True
    affects_objects: bool = True


@dataclass
class PuzzleController(Component):
    """
    Controller component for multi-part puzzles.

    Tracks completion state of complex puzzles.
    """

    # Puzzle definition
    puzzle_id: str = ""
    puzzle_type: str = "switch_combination"  # Type of puzzle

    # Requirements (switch IDs or conditions)
    required_switches: List[str] = field(default_factory=list)
    required_states: List[bool] = field(default_factory=list)  # Required states

    # Current state
    current_states: Dict[str, bool] = field(default_factory=dict)  # switch_id -> state
    is_solved: bool = False

    # Rewards
    reward_target_ids: List[str] = field(
        default_factory=list
    )  # What to activate when solved

    # Callbacks
    on_solve: Optional[Callable] = None
    on_reset: Optional[Callable] = None

    def check_solution(self) -> bool:
        """Check if puzzle is solved"""
        if len(self.required_switches) != len(self.required_states):
            return False

        for switch_id, required_state in zip(
            self.required_switches, self.required_states
        ):
            current_state = self.current_states.get(switch_id, False)
            if current_state != required_state:
                return False

        return True

    def update_switch_state(self, switch_id: str, state: bool):
        """Update state of a switch"""
        self.current_states[switch_id] = state

        # Check if solved
        if not self.is_solved and self.check_solution():
            self.is_solved = True
            if self.on_solve:
                self.on_solve()


@dataclass
class OneWayGate(Component):
    """
    One-way gate component that only allows passage in one direction.
    """

    # Direction that can pass through (0=up, 1=right, 2=down, 3=left)
    passable_direction: int = 2

    # Visual
    sprite: str = ""

    def can_pass_from_direction(self, from_direction: int) -> bool:
        """Check if can pass from given direction"""
        return from_direction == self.passable_direction
