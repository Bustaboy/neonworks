"""
Input Manager

Handles keyboard, mouse, and gamepad input with action mapping and buffering.
"""

from typing import Dict, Set, Tuple, Optional, Callable
from enum import Enum, auto
import pygame


class InputState(Enum):
    """Input button states"""
    RELEASED = auto()  # Button is up
    JUST_PRESSED = auto()  # Button was just pressed this frame
    HELD = auto()  # Button is being held down
    JUST_RELEASED = auto()  # Button was just released this frame


class MouseButton(Enum):
    """Mouse button enumeration"""
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5


class InputManager:
    """
    Manages all input from keyboard, mouse, and gamepad.

    Features:
    - Key state tracking (pressed, held, released)
    - Mouse position and button tracking
    - Action mapping (rebindable controls)
    - Input buffering for responsive gameplay
    - Axis input (for analog sticks, WASD movement, etc.)
    """

    def __init__(self):
        # Keyboard state
        self._keys_current: Set[int] = set()
        self._keys_previous: Set[int] = set()

        # Mouse state
        self._mouse_position: Tuple[int, int] = (0, 0)
        self._mouse_buttons_current: Set[int] = set()
        self._mouse_buttons_previous: Set[int] = set()
        self._mouse_wheel: int = 0

        # Action mapping
        self._action_map: Dict[str, Set[int]] = {}
        self._action_callbacks: Dict[str, Callable] = {}

        # Input buffer (for responsive controls)
        self._input_buffer: list = []
        self._buffer_size = 10
        self._buffer_time = 0.15  # 150ms buffer window

        # Frame timing
        self._delta_time = 0.0

        # Text input mode
        self._text_input_enabled = False
        self._text_input = ""

        # Initialize default action mappings
        self._setup_default_mappings()

    def _setup_default_mappings(self):
        """Setup default key bindings"""
        # Movement
        self.map_action("move_up", [pygame.K_w, pygame.K_UP])
        self.map_action("move_down", [pygame.K_s, pygame.K_DOWN])
        self.map_action("move_left", [pygame.K_a, pygame.K_LEFT])
        self.map_action("move_right", [pygame.K_d, pygame.K_RIGHT])

        # Actions
        self.map_action("confirm", [pygame.K_RETURN, pygame.K_SPACE])
        self.map_action("cancel", [pygame.K_ESCAPE, pygame.K_BACKSPACE])
        self.map_action("interact", [pygame.K_e])

        # UI
        self.map_action("menu", [pygame.K_ESCAPE])
        self.map_action("inventory", [pygame.K_i])
        self.map_action("map", [pygame.K_m])

        # Combat
        self.map_action("attack", [pygame.K_SPACE])
        self.map_action("ability1", [pygame.K_1])
        self.map_action("ability2", [pygame.K_2])
        self.map_action("ability3", [pygame.K_3])
        self.map_action("ability4", [pygame.K_4])

        # Debug
        self.map_action("debug_console", [pygame.K_BACKQUOTE])  # ` key

    def update(self, delta_time: float):
        """
        Update input state. Call this once per frame.

        Args:
            delta_time: Time since last frame in seconds
        """
        self._delta_time = delta_time

        # Store previous frame state
        self._keys_previous = self._keys_current.copy()
        self._mouse_buttons_previous = self._mouse_buttons_current.copy()

        # Get current state from pygame
        self._keys_current = set()
        pressed_keys = pygame.key.get_pressed()
        for key_code in range(len(pressed_keys)):
            if pressed_keys[key_code]:
                self._keys_current.add(key_code)

        # Update mouse state (skip if video system not initialized)
        try:
            self._mouse_position = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            self._mouse_buttons_current = set()
            for i, pressed in enumerate(mouse_buttons):
                if pressed:
                    self._mouse_buttons_current.add(i + 1)  # Pygame uses 0-indexed, we use 1-indexed
        except pygame.error:
            # Video system not initialized, keep previous state
            pass

        # Clear mouse wheel (it's event-based)
        self._mouse_wheel = 0

        # Check action callbacks
        self._process_action_callbacks()

    def process_event(self, event: pygame.event.Event):
        """
        Process pygame events. Call this for each event in the event queue.

        Args:
            event: Pygame event to process
        """
        if event.type == pygame.KEYDOWN:
            # Add to input buffer
            self._add_to_buffer('key', event.key, event.scancode)

            # Handle text input
            if self._text_input_enabled:
                if event.key == pygame.K_BACKSPACE:
                    self._text_input = self._text_input[:-1]
                elif event.key == pygame.K_RETURN:
                    pass  # Handled by application
                else:
                    self._text_input += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._add_to_buffer('mouse', event.button, event.pos)

            # Handle mouse wheel
            if event.button == 4:  # Wheel up
                self._mouse_wheel = 1
            elif event.button == 5:  # Wheel down
                self._mouse_wheel = -1

        elif event.type == pygame.MOUSEWHEEL:
            self._mouse_wheel = event.y

    def _add_to_buffer(self, input_type: str, code: int, data: any):
        """Add input to buffer"""
        self._input_buffer.append({
            'type': input_type,
            'code': code,
            'data': data,
            'time': 0.0
        })

        # Limit buffer size
        if len(self._input_buffer) > self._buffer_size:
            self._input_buffer.pop(0)

    def _process_action_callbacks(self):
        """Process registered action callbacks"""
        for action_name, callback in self._action_callbacks.items():
            if self.is_action_just_pressed(action_name):
                try:
                    callback()
                except Exception as e:
                    print(f"Error in action callback '{action_name}': {e}")

    # ========== Keyboard Input ==========

    def is_key_pressed(self, key_code: int) -> bool:
        """Check if a key is currently pressed"""
        return key_code in self._keys_current

    def is_key_just_pressed(self, key_code: int) -> bool:
        """Check if a key was just pressed this frame"""
        return key_code in self._keys_current and key_code not in self._keys_previous

    def is_key_just_released(self, key_code: int) -> bool:
        """Check if a key was just released this frame"""
        return key_code not in self._keys_current and key_code in self._keys_previous

    def get_key_state(self, key_code: int) -> InputState:
        """Get the state of a key"""
        if self.is_key_just_pressed(key_code):
            return InputState.JUST_PRESSED
        elif self.is_key_just_released(key_code):
            return InputState.JUST_RELEASED
        elif self.is_key_pressed(key_code):
            return InputState.HELD
        else:
            return InputState.RELEASED

    # ========== Mouse Input ==========

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return self._mouse_position

    def get_mouse_x(self) -> int:
        """Get mouse X position"""
        return self._mouse_position[0]

    def get_mouse_y(self) -> int:
        """Get mouse Y position"""
        return self._mouse_position[1]

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is pressed"""
        return button in self._mouse_buttons_current

    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed"""
        return button in self._mouse_buttons_current and button not in self._mouse_buttons_previous

    def is_mouse_button_just_released(self, button: int) -> bool:
        """Check if a mouse button was just released"""
        return button not in self._mouse_buttons_current and button in self._mouse_buttons_previous

    def get_mouse_wheel(self) -> int:
        """Get mouse wheel delta (-1, 0, or 1)"""
        return self._mouse_wheel

    # ========== Action Mapping ==========

    def map_action(self, action_name: str, key_codes: list):
        """
        Map an action name to one or more keys.

        Args:
            action_name: Name of the action (e.g., "jump", "attack")
            key_codes: List of pygame key codes
        """
        self._action_map[action_name] = set(key_codes)

    def add_key_to_action(self, action_name: str, key_code: int):
        """Add an additional key to an action"""
        if action_name not in self._action_map:
            self._action_map[action_name] = set()
        self._action_map[action_name].add(key_code)

    def remove_key_from_action(self, action_name: str, key_code: int):
        """Remove a key from an action"""
        if action_name in self._action_map:
            self._action_map[action_name].discard(key_code)

    def is_action_pressed(self, action_name: str) -> bool:
        """Check if any key mapped to this action is pressed"""
        if action_name not in self._action_map:
            return False

        for key_code in self._action_map[action_name]:
            if self.is_key_pressed(key_code):
                return True
        return False

    def is_action_just_pressed(self, action_name: str) -> bool:
        """Check if any key mapped to this action was just pressed"""
        if action_name not in self._action_map:
            return False

        for key_code in self._action_map[action_name]:
            if self.is_key_just_pressed(key_code):
                return True
        return False

    def is_action_just_released(self, action_name: str) -> bool:
        """Check if any key mapped to this action was just released"""
        if action_name not in self._action_map:
            return False

        for key_code in self._action_map[action_name]:
            if self.is_key_just_released(key_code):
                return True
        return False

    def register_action_callback(self, action_name: str, callback: Callable):
        """Register a callback for when an action is triggered"""
        self._action_callbacks[action_name] = callback

    def unregister_action_callback(self, action_name: str):
        """Unregister an action callback"""
        if action_name in self._action_callbacks:
            del self._action_callbacks[action_name]

    # ========== Axis Input ==========

    def get_axis(self, negative_action: str, positive_action: str) -> float:
        """
        Get axis value from two actions (-1.0 to 1.0).

        Example:
            horizontal = input_manager.get_axis("move_left", "move_right")
        """
        value = 0.0

        if self.is_action_pressed(negative_action):
            value -= 1.0
        if self.is_action_pressed(positive_action):
            value += 1.0

        return value

    def get_movement_vector(self) -> Tuple[float, float]:
        """
        Get movement vector from WASD/Arrow keys.

        Returns:
            (horizontal, vertical) tuple with values from -1.0 to 1.0
        """
        horizontal = self.get_axis("move_left", "move_right")
        vertical = self.get_axis("move_up", "move_down")

        # Normalize diagonal movement
        if horizontal != 0 and vertical != 0:
            factor = 0.7071  # 1/sqrt(2)
            horizontal *= factor
            vertical *= factor

        return (horizontal, vertical)

    # ========== Text Input ==========

    def enable_text_input(self):
        """Enable text input mode"""
        self._text_input_enabled = True
        self._text_input = ""
        pygame.key.set_repeat(500, 50)  # Delay, interval in ms

    def disable_text_input(self):
        """Disable text input mode"""
        self._text_input_enabled = False
        pygame.key.set_repeat()

    def get_text_input(self) -> str:
        """Get current text input"""
        return self._text_input

    def clear_text_input(self):
        """Clear text input buffer"""
        self._text_input = ""

    # ========== Utility ==========

    def clear_all(self):
        """Clear all input state"""
        self._keys_current.clear()
        self._keys_previous.clear()
        self._mouse_buttons_current.clear()
        self._mouse_buttons_previous.clear()
        self._input_buffer.clear()

    def get_any_key_pressed(self) -> Optional[int]:
        """Get the first key that is currently pressed"""
        if self._keys_current:
            return next(iter(self._keys_current))
        return None

    def get_any_key_just_pressed(self) -> Optional[int]:
        """Get the first key that was just pressed this frame"""
        just_pressed = self._keys_current - self._keys_previous
        if just_pressed:
            return next(iter(just_pressed))
        return None


# Global input manager instance
_global_input_manager: Optional[InputManager] = None


def get_input_manager() -> InputManager:
    """Get the global input manager instance"""
    global _global_input_manager
    if _global_input_manager is None:
        _global_input_manager = InputManager()
    return _global_input_manager


def initialize_input() -> InputManager:
    """Initialize and return the input manager"""
    global _global_input_manager
    _global_input_manager = InputManager()
    return _global_input_manager
