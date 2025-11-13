"""
State Management

Game state and scene management system.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Optional


class StateTransition(Enum):
    """State transition types"""

    PUSH = auto()  # Push new state onto stack
    POP = auto()  # Pop current state
    REPLACE = auto()  # Replace current state
    CLEAR_AND_PUSH = auto()  # Clear stack and push new state


class GameState(ABC):
    """Base class for game states"""

    def __init__(self, name: str):
        self.name = name
        self._state_manager: Optional["StateManager"] = None

    def set_manager(self, manager: "StateManager"):
        """Set the state manager"""
        self._state_manager = manager

    @abstractmethod
    def enter(self, data: Dict[str, Any] = None):
        """Called when entering this state"""
        pass

    @abstractmethod
    def exit(self):
        """Called when exiting this state"""
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """Update the state"""
        pass

    @abstractmethod
    def render(self):
        """Render the state"""
        pass

    def handle_event(self, event):
        """Handle an event"""
        pass


class MenuState(GameState):
    """Main menu state"""

    def __init__(self):
        super().__init__("menu")
        self.selected_option = 0

    def enter(self, data: Dict[str, Any] = None):
        print("Entering menu state")

    def exit(self):
        print("Exiting menu state")

    def update(self, delta_time: float):
        pass

    def render(self):
        pass


class GameplayState(GameState):
    """Main gameplay state"""

    def __init__(self, world):
        super().__init__("gameplay")
        self.world = world
        self.paused = False

    def enter(self, data: Dict[str, Any] = None):
        print("Entering gameplay state")
        if data and "level" in data:
            self.load_level(data["level"])

    def exit(self):
        print("Exiting gameplay state")

    def update(self, delta_time: float):
        if not self.paused:
            self.world.update(delta_time)

    def render(self):
        # Rendering handled by renderer system
        pass

    def load_level(self, level_path: str):
        """Load a level"""
        print(f"Loading level: {level_path}")

    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused


class EditorState(GameState):
    """Level editor state"""

    def __init__(self, world):
        super().__init__("editor")
        self.world = world
        self.editor_mode = "tile_placement"
        self.selected_tile = None

    def enter(self, data: Dict[str, Any] = None):
        print("Entering editor state")

    def exit(self):
        print("Exiting editor state")

    def update(self, delta_time: float):
        # Editor updates handled by editor systems
        pass

    def render(self):
        # Rendering handled by editor UI
        pass

    def set_mode(self, mode: str):
        """Set editor mode"""
        self.editor_mode = mode
        print(f"Editor mode: {mode}")


class LoadingState(GameState):
    """Loading screen state"""

    def __init__(self):
        super().__init__("loading")
        self.progress = 0.0
        self.target_state = None
        self.target_data = None

    def enter(self, data: Dict[str, Any] = None):
        if data:
            self.target_state = data.get("target_state")
            self.target_data = data.get("target_data")
        self.progress = 0.0

    def exit(self):
        pass

    def update(self, delta_time: float):
        # Simulate loading
        self.progress += delta_time * 0.5

        if self.progress >= 1.0 and self.target_state:
            self._state_manager.change_state(
                self.target_state, StateTransition.REPLACE, self.target_data
            )

    def render(self):
        # Render loading bar
        pass


class StateManager:
    """Manages game states"""

    def __init__(self):
        self._states: Dict[str, GameState] = {}
        self._state_stack: list[GameState] = []
        self._pending_transition: Optional[tuple] = None

    def register_state(self, state: GameState) -> "StateManager":
        """Register a game state"""
        state.set_manager(self)
        self._states[state.name] = state
        return self

    def change_state(
        self, state_name: str, transition: StateTransition, data: Dict[str, Any] = None
    ):
        """Change to a different state"""
        if state_name not in self._states:
            raise ValueError(f"State '{state_name}' not registered")

        # Queue the transition to happen at the end of the update
        self._pending_transition = (state_name, transition, data)

    def _execute_transition(self):
        """Execute a pending state transition"""
        if not self._pending_transition:
            return

        state_name, transition, data = self._pending_transition
        self._pending_transition = None

        new_state = self._states[state_name]

        if transition == StateTransition.PUSH:
            if self._state_stack:
                self._state_stack[-1].exit()
            self._state_stack.append(new_state)
            new_state.enter(data)

        elif transition == StateTransition.POP:
            if self._state_stack:
                self._state_stack[-1].exit()
                self._state_stack.pop()
            if self._state_stack:
                self._state_stack[-1].enter(data)

        elif transition == StateTransition.REPLACE:
            if self._state_stack:
                self._state_stack[-1].exit()
                self._state_stack[-1] = new_state
            else:
                self._state_stack.append(new_state)
            new_state.enter(data)

        elif transition == StateTransition.CLEAR_AND_PUSH:
            while self._state_stack:
                self._state_stack[-1].exit()
                self._state_stack.pop()
            self._state_stack.append(new_state)
            new_state.enter(data)

    def pop_state(self):
        """Pop the current state"""
        self._pending_transition = (None, StateTransition.POP, None)

    def get_current_state(self) -> Optional[GameState]:
        """Get the current state"""
        return self._state_stack[-1] if self._state_stack else None

    def update(self, delta_time: float):
        """Update the current state"""
        if self._state_stack:
            self._state_stack[-1].update(delta_time)

        # Execute any pending transitions
        self._execute_transition()

    def render(self):
        """Render the current state"""
        if self._state_stack:
            self._state_stack[-1].render()

    def handle_event(self, event):
        """Handle an event in the current state"""
        if self._state_stack:
            self._state_stack[-1].handle_event(event)
