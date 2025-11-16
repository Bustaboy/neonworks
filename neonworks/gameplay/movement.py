"""
Movement Components for JRPG-style Exploration

Components for tile-based character movement, collision, and animation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, Tuple

from neonworks.core.ecs import Component


class Direction(Enum):
    """Cardinal directions for movement and facing"""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

    def to_vector(self) -> Tuple[int, int]:
        """Convert direction to movement vector (dx, dy)"""
        return {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }[self]

    def opposite(self) -> "Direction":
        """Get opposite direction"""
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]


@dataclass
class Movement(Component):
    """
    Movement component for tile-based character movement.

    Handles smooth movement between tiles and movement state.
    """

    # Movement speed (tiles per second)
    speed: float = 4.0

    # Current movement state
    is_moving: bool = False
    target_grid_x: int = 0
    target_grid_y: int = 0
    move_progress: float = 0.0  # 0.0 to 1.0

    # Movement properties
    can_move: bool = True
    can_move_diagonally: bool = False

    # Facing direction
    facing: Direction = Direction.DOWN

    # Callbacks
    on_move_start: Optional[Callable[[int, int], None]] = None  # (target_x, target_y)
    on_move_complete: Optional[Callable[[int, int], None]] = None  # (new_x, new_y)
    on_collision: Optional[Callable[[int, int], None]] = None  # (blocked_x, blocked_y)


@dataclass
class Collider2D(Component):
    """
    2D collision component for tile-based games.

    Defines which tiles can be walked on and collision layers.
    """

    # Collision properties
    is_solid: bool = True  # Can other entities pass through?
    is_trigger: bool = False  # Trigger events but don't block?

    # Layer mask (bit flags)
    collision_layer: int = 1  # Which layer is this on
    collision_mask: int = 0xFFFFFFFF  # Which layers to collide with

    # Callbacks
    on_trigger_enter: Optional[Callable[["Entity"], None]] = None
    on_trigger_exit: Optional[Callable[["Entity"], None]] = None


@dataclass
class Interactable(Component):
    """
    Component for objects/NPCs that can be interacted with.

    Allows player to interact by pressing action button when adjacent.
    """

    # Interaction properties
    can_interact: bool = True
    interaction_distance: int = 1  # Tiles away
    require_facing: bool = True  # Must face object to interact?

    # Interaction type
    interaction_type: str = "talk"  # talk, examine, open, use, etc.

    # Data for interaction
    dialogue_id: Optional[str] = None
    script_id: Optional[str] = None
    item_id: Optional[str] = None

    # Callbacks
    on_interact: Optional[Callable[["Entity"], None]] = None  # Called when interacted with

    # Visual feedback
    show_prompt: bool = True  # Show interaction prompt UI?
    prompt_text: str = "Press E"


@dataclass
class ZoneTrigger(Component):
    """
    Zone transition trigger for map changes.

    When player enters this tile, trigger a zone transition.
    """

    # Target zone
    target_zone: str = ""  # Zone/map name to load
    target_x: int = 0  # Spawn position in target zone
    target_y: int = 0
    target_direction: Direction = Direction.DOWN

    # Trigger properties
    is_active: bool = True
    requires_input: bool = False  # Require player to press button?

    # Transition effect
    transition_type: str = "fade"  # fade, slide, instant, etc.
    transition_duration: float = 0.5  # seconds

    # Callbacks
    on_trigger: Optional[Callable[[str], None]] = None  # Called when triggered


@dataclass
class NPCBehavior(Component):
    """
    NPC behavior component for non-player characters.

    Defines movement patterns, dialogue, and AI behavior.
    """

    # Behavior type
    behavior_type: str = "static"  # static, wander, patrol, follow, etc.

    # Movement properties
    move_speed: float = 2.0
    wander_radius: int = 3  # Tiles
    wander_interval: float = 3.0  # Seconds between moves
    wander_timer: float = 0.0

    # Patrol points (for patrol behavior)
    patrol_points: list = field(default_factory=list)  # List of (x, y) tuples
    current_patrol_index: int = 0
    patrol_loop: bool = True

    # Follow properties (for follow behavior)
    follow_target_id: Optional[str] = None
    follow_distance: int = 2  # Tiles

    # Dialogue
    dialogue_id: Optional[str] = None
    can_talk: bool = True

    # Visual
    sprite_facing: Direction = Direction.DOWN


@dataclass
class AnimationState(Component):
    """
    Animation state component for JRPG-style character animations.

    Manages animation states like idle, walk, run for each direction.
    """

    # Current state
    current_state: str = "idle"
    current_direction: Direction = Direction.DOWN

    # Animation properties
    frame_index: int = 0
    frame_timer: float = 0.0
    frame_duration: float = 0.15  # Seconds per frame

    # Animation definitions (state_direction -> frame list)
    # Example: "walk_down" -> [0, 1, 2, 1]
    animations: dict = field(default_factory=dict)

    # Default frame indices for each state/direction
    default_frames: dict = field(
        default_factory=lambda: {
            "idle_down": [0],
            "idle_up": [12],
            "idle_left": [4],
            "idle_right": [8],
            "walk_down": [0, 1, 2, 1],
            "walk_up": [12, 13, 14, 13],
            "walk_left": [4, 5, 6, 5],
            "walk_right": [8, 9, 10, 9],
        }
    )

    def get_animation_key(self) -> str:
        """Get current animation key (state_direction)"""
        direction_str = self.current_direction.value
        return f"{self.current_state}_{direction_str}"

    def get_current_frames(self) -> list:
        """Get current animation frame list"""
        key = self.get_animation_key()
        # Use custom animation if defined, otherwise use default
        if key in self.animations:
            return self.animations[key]
        return self.default_frames.get(key, [0])


@dataclass
class TileCollisionMap(Component):
    """
    Collision map component for tilemaps.

    Stores which tiles are walkable/blocked.
    """

    # Collision data (2D array of booleans)
    # True = walkable, False = blocked
    collision_data: list = field(default_factory=list)

    # Map dimensions
    width: int = 0
    height: int = 0

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if tile is walkable"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        if not self.collision_data:
            return True
        if y >= len(self.collision_data) or x >= len(self.collision_data[y]):
            return True
        return self.collision_data[y][x]

    def set_walkable(self, x: int, y: int, walkable: bool):
        """Set tile walkability"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if not self.collision_data:
                self.collision_data = [[True] * self.width for _ in range(self.height)]
            self.collision_data[y][x] = walkable

    def load_from_layer(self, layer_data: list, blocked_tiles: set):
        """
        Load collision data from a tilemap layer.

        Args:
            layer_data: 2D array of tile IDs
            blocked_tiles: Set of tile IDs that are blocked
        """
        self.height = len(layer_data)
        self.width = len(layer_data[0]) if self.height > 0 else 0

        self.collision_data = []
        for row in layer_data:
            collision_row = []
            for tile_id in row:
                walkable = tile_id not in blocked_tiles
                collision_row.append(walkable)
            self.collision_data.append(collision_row)


# Entity reference import (circular dependency workaround)
from neonworks.core.ecs import Entity
