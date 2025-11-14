"""
Comprehensive tests for state management module

Tests game states, state transitions, and state manager functionality.
"""

import pytest

from neonworks.core.ecs import World
from neonworks.core.state import (
    EditorState,
    GameplayState,
    GameState,
    LoadingState,
    MenuState,
    StateManager,
    StateTransition,
)

# ===========================
# Mock World for Testing
# ===========================


class MockWorld:
    """Mock world for testing"""

    def __init__(self):
        self.update_called = False
        self.update_delta = 0.0

    def update(self, delta_time: float):
        self.update_called = True
        self.update_delta = delta_time


# ===========================
# StateTransition Tests
# ===========================


class TestStateTransition:
    """Test StateTransition enum"""

    def test_transition_types_exist(self):
        """Test all transition types are defined"""
        assert StateTransition.PUSH
        assert StateTransition.POP
        assert StateTransition.REPLACE
        assert StateTransition.CLEAR_AND_PUSH

    def test_transition_values_unique(self):
        """Test transition values are unique"""
        transitions = [
            StateTransition.PUSH,
            StateTransition.POP,
            StateTransition.REPLACE,
            StateTransition.CLEAR_AND_PUSH,
        ]
        values = [t.value for t in transitions]
        assert len(values) == len(set(values))


# ===========================
# MenuState Tests
# ===========================


class TestMenuState:
    """Test MenuState implementation"""

    def test_menu_state_initialization(self):
        """Test MenuState initialization"""
        state = MenuState()
        assert state.name == "menu"
        assert state.selected_option == 0

    def test_menu_state_enter(self, capsys):
        """Test MenuState enter method"""
        state = MenuState()
        state.enter()
        captured = capsys.readouterr()
        assert "Entering menu state" in captured.out

    def test_menu_state_enter_with_data(self):
        """Test MenuState enter with data"""
        state = MenuState()
        state.enter({"selected": 2})
        # Should not error even with data

    def test_menu_state_exit(self, capsys):
        """Test MenuState exit method"""
        state = MenuState()
        state.exit()
        captured = capsys.readouterr()
        assert "Exiting menu state" in captured.out

    def test_menu_state_update(self):
        """Test MenuState update method"""
        state = MenuState()
        state.update(0.016)
        # Should not error

    def test_menu_state_render(self):
        """Test MenuState render method"""
        state = MenuState()
        state.render()
        # Should not error

    def test_menu_state_handle_event(self):
        """Test MenuState handle_event method"""
        state = MenuState()
        state.handle_event({"type": "keypress", "key": "down"})
        # Should not error


# ===========================
# GameplayState Tests
# ===========================


class TestGameplayState:
    """Test GameplayState implementation"""

    def test_gameplay_state_initialization(self):
        """Test GameplayState initialization"""
        world = MockWorld()
        state = GameplayState(world)

        assert state.name == "gameplay"
        assert state.world is world
        assert state.paused is False

    def test_gameplay_state_enter(self, capsys):
        """Test GameplayState enter method"""
        world = MockWorld()
        state = GameplayState(world)
        state.enter()

        captured = capsys.readouterr()
        assert "Entering gameplay state" in captured.out

    def test_gameplay_state_enter_with_level(self, capsys):
        """Test GameplayState enter with level data"""
        world = MockWorld()
        state = GameplayState(world)
        state.enter({"level": "level1.json"})

        captured = capsys.readouterr()
        assert "Loading level: level1.json" in captured.out

    def test_gameplay_state_exit(self, capsys):
        """Test GameplayState exit method"""
        world = MockWorld()
        state = GameplayState(world)
        state.exit()

        captured = capsys.readouterr()
        assert "Exiting gameplay state" in captured.out

    def test_gameplay_state_update_not_paused(self):
        """Test GameplayState updates world when not paused"""
        world = MockWorld()
        state = GameplayState(world)
        state.update(0.016)

        assert world.update_called is True
        assert world.update_delta == 0.016

    def test_gameplay_state_update_paused(self):
        """Test GameplayState does not update world when paused"""
        world = MockWorld()
        state = GameplayState(world)
        state.paused = True
        state.update(0.016)

        assert world.update_called is False

    def test_gameplay_state_toggle_pause(self):
        """Test GameplayState pause toggling"""
        world = MockWorld()
        state = GameplayState(world)

        assert state.paused is False

        state.toggle_pause()
        assert state.paused is True

        state.toggle_pause()
        assert state.paused is False

    def test_gameplay_state_load_level(self, capsys):
        """Test GameplayState level loading"""
        world = MockWorld()
        state = GameplayState(world)
        state.load_level("test_level.json")

        captured = capsys.readouterr()
        assert "Loading level: test_level.json" in captured.out

    def test_gameplay_state_render(self):
        """Test GameplayState render method"""
        world = MockWorld()
        state = GameplayState(world)
        state.render()
        # Should not error


# ===========================
# EditorState Tests
# ===========================


class TestEditorState:
    """Test EditorState implementation"""

    def test_editor_state_initialization(self):
        """Test EditorState initialization"""
        world = MockWorld()
        state = EditorState(world)

        assert state.name == "editor"
        assert state.world is world
        assert state.editor_mode == "tile_placement"
        assert state.selected_tile is None

    def test_editor_state_enter(self, capsys):
        """Test EditorState enter method"""
        world = MockWorld()
        state = EditorState(world)
        state.enter()

        captured = capsys.readouterr()
        assert "Entering editor state" in captured.out

    def test_editor_state_exit(self, capsys):
        """Test EditorState exit method"""
        world = MockWorld()
        state = EditorState(world)
        state.exit()

        captured = capsys.readouterr()
        assert "Exiting editor state" in captured.out

    def test_editor_state_update(self):
        """Test EditorState update method"""
        world = MockWorld()
        state = EditorState(world)
        state.update(0.016)
        # Should not error

    def test_editor_state_render(self):
        """Test EditorState render method"""
        world = MockWorld()
        state = EditorState(world)
        state.render()
        # Should not error

    def test_editor_state_set_mode(self, capsys):
        """Test EditorState mode setting"""
        world = MockWorld()
        state = EditorState(world)

        state.set_mode("entity_placement")
        assert state.editor_mode == "entity_placement"

        captured = capsys.readouterr()
        assert "Editor mode: entity_placement" in captured.out


# ===========================
# LoadingState Tests
# ===========================


class TestLoadingState:
    """Test LoadingState implementation"""

    def test_loading_state_initialization(self):
        """Test LoadingState initialization"""
        state = LoadingState()

        assert state.name == "loading"
        assert state.progress == 0.0
        assert state.target_state is None
        assert state.target_data is None

    def test_loading_state_enter_no_data(self):
        """Test LoadingState enter without data"""
        state = LoadingState()
        state.enter()

        assert state.progress == 0.0
        assert state.target_state is None

    def test_loading_state_enter_with_data(self):
        """Test LoadingState enter with target data"""
        state = LoadingState()
        state.enter({"target_state": "gameplay", "target_data": {"level": "level1"}})

        assert state.progress == 0.0
        assert state.target_state == "gameplay"
        assert state.target_data == {"level": "level1"}

    def test_loading_state_exit(self):
        """Test LoadingState exit method"""
        state = LoadingState()
        state.exit()
        # Should not error

    def test_loading_state_update_progress(self):
        """Test LoadingState updates progress"""
        state = LoadingState()
        state.enter()

        state.update(0.5)
        assert state.progress == 0.25  # 0.5 * 0.5

        state.update(1.0)
        assert state.progress == 0.75  # 0.25 + (1.0 * 0.5)

    def test_loading_state_transitions_when_complete(self):
        """Test LoadingState transitions to target state when complete"""
        manager = StateManager()
        gameplay_world = MockWorld()

        menu_state = MenuState()
        gameplay_state = GameplayState(gameplay_world)
        loading_state = LoadingState()

        manager.register_state(menu_state)
        manager.register_state(gameplay_state)
        manager.register_state(loading_state)

        # Start with loading state
        manager.change_state("loading", StateTransition.PUSH)
        manager._execute_transition()

        # Set target and simulate loading
        loading_state.target_state = "gameplay"
        loading_state.target_data = {"level": "test"}

        # Update until progress complete
        loading_state.update(3.0)  # Progress will exceed 1.0
        assert loading_state.progress >= 1.0

    def test_loading_state_render(self):
        """Test LoadingState render method"""
        state = LoadingState()
        state.render()
        # Should not error


# ===========================
# StateManager Tests
# ===========================


class TestStateManager:
    """Test StateManager implementation"""

    def test_state_manager_initialization(self):
        """Test StateManager initialization"""
        manager = StateManager()

        assert manager._states == {}
        assert manager._state_stack == []
        assert manager._pending_transition is None

    def test_register_state(self):
        """Test registering states"""
        manager = StateManager()
        state = MenuState()

        result = manager.register_state(state)

        assert "menu" in manager._states
        assert manager._states["menu"] is state
        assert state._state_manager is manager
        assert result is manager  # Should return self for chaining

    def test_register_multiple_states_chaining(self):
        """Test registering multiple states with chaining"""
        manager = StateManager()
        menu = MenuState()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(menu).register_state(gameplay)

        assert "menu" in manager._states
        assert "gameplay" in manager._states

    def test_get_current_state_empty(self):
        """Test getting current state when stack is empty"""
        manager = StateManager()
        assert manager.get_current_state() is None

    def test_change_state_unregistered(self):
        """Test changing to unregistered state raises error"""
        manager = StateManager()

        with pytest.raises(ValueError, match="State 'invalid' not registered"):
            manager.change_state("invalid", StateTransition.PUSH)

    def test_change_state_push(self, capsys):
        """Test PUSH state transition"""
        manager = StateManager()
        menu = MenuState()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(menu).register_state(gameplay)

        # Push menu state
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()

        assert manager.get_current_state() is menu
        captured = capsys.readouterr()
        assert "Entering menu state" in captured.out

        # Push gameplay state
        manager.change_state("gameplay", StateTransition.PUSH)
        manager._execute_transition()

        assert manager.get_current_state() is gameplay
        captured = capsys.readouterr()
        assert "Exiting menu state" in captured.out
        assert "Entering gameplay state" in captured.out

    def test_change_state_pop(self, capsys):
        """Test POP state transition"""
        manager = StateManager()
        menu = MenuState()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(menu).register_state(gameplay)

        # Push two states
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()
        manager.change_state("gameplay", StateTransition.PUSH)
        manager._execute_transition()

        # Pop gameplay state
        manager.pop_state()
        manager._execute_transition()

        assert manager.get_current_state() is menu
        captured = capsys.readouterr()
        assert "Exiting gameplay state" in captured.out
        assert "Entering menu state" in captured.out

    def test_change_state_replace(self, capsys):
        """Test REPLACE state transition"""
        manager = StateManager()
        menu = MenuState()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(menu).register_state(gameplay)

        # Push menu state
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()

        # Replace with gameplay
        manager.change_state("gameplay", StateTransition.REPLACE)
        manager._execute_transition()

        assert manager.get_current_state() is gameplay
        assert len(manager._state_stack) == 1
        captured = capsys.readouterr()
        assert "Exiting menu state" in captured.out
        assert "Entering gameplay state" in captured.out

    def test_change_state_replace_empty_stack(self, capsys):
        """Test REPLACE on empty stack pushes state"""
        manager = StateManager()
        menu = MenuState()

        manager.register_state(menu)

        manager.change_state("menu", StateTransition.REPLACE)
        manager._execute_transition()

        assert manager.get_current_state() is menu
        assert len(manager._state_stack) == 1

    def test_change_state_clear_and_push(self, capsys):
        """Test CLEAR_AND_PUSH state transition"""
        manager = StateManager()
        menu = MenuState()
        world1 = MockWorld()
        world2 = MockWorld()
        gameplay = GameplayState(world1)
        editor = EditorState(world2)

        manager.register_state(menu).register_state(gameplay).register_state(editor)

        # Push multiple states
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()
        manager.change_state("gameplay", StateTransition.PUSH)
        manager._execute_transition()

        # Clear and push editor
        manager.change_state("editor", StateTransition.CLEAR_AND_PUSH)
        manager._execute_transition()

        assert manager.get_current_state() is editor
        assert len(manager._state_stack) == 1
        captured = capsys.readouterr()
        assert "Exiting gameplay state" in captured.out
        assert "Exiting menu state" in captured.out
        assert "Entering editor state" in captured.out

    def test_state_data_passing(self, capsys):
        """Test data is passed to states on enter"""
        manager = StateManager()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(gameplay)

        # Change state with data
        manager.change_state("gameplay", StateTransition.PUSH, {"level": "test_level.json"})
        manager._execute_transition()

        captured = capsys.readouterr()
        assert "Loading level: test_level.json" in captured.out

    def test_update_current_state(self):
        """Test updating current state"""
        manager = StateManager()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(gameplay)
        manager.change_state("gameplay", StateTransition.PUSH)
        manager._execute_transition()

        manager.update(0.016)

        assert world.update_called is True
        assert world.update_delta == 0.016

    def test_update_executes_pending_transition(self, capsys):
        """Test update executes pending transitions"""
        manager = StateManager()
        menu = MenuState()

        manager.register_state(menu)

        # Queue transition
        manager.change_state("menu", StateTransition.PUSH)

        # Should not be executed yet
        assert manager.get_current_state() is None

        # Update should execute it
        manager.update(0.016)

        assert manager.get_current_state() is menu

    def test_render_current_state(self):
        """Test rendering current state"""
        manager = StateManager()
        menu = MenuState()

        manager.register_state(menu)
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()

        manager.render()
        # Should not error

    def test_render_empty_stack(self):
        """Test rendering with empty stack"""
        manager = StateManager()
        manager.render()
        # Should not error

    def test_handle_event_current_state(self):
        """Test event handling in current state"""
        manager = StateManager()
        menu = MenuState()

        manager.register_state(menu)
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()

        manager.handle_event({"type": "keypress", "key": "enter"})
        # Should not error

    def test_handle_event_empty_stack(self):
        """Test event handling with empty stack"""
        manager = StateManager()
        manager.handle_event({"type": "keypress"})
        # Should not error

    def test_state_stack_integrity(self):
        """Test state stack maintains integrity through multiple operations"""
        manager = StateManager()
        menu = MenuState()
        world1 = MockWorld()
        world2 = MockWorld()
        gameplay = GameplayState(world1)
        editor = EditorState(world2)

        manager.register_state(menu).register_state(gameplay).register_state(editor)

        # Complex sequence of transitions
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()
        assert len(manager._state_stack) == 1

        manager.change_state("gameplay", StateTransition.PUSH)
        manager._execute_transition()
        assert len(manager._state_stack) == 2

        manager.change_state("editor", StateTransition.PUSH)
        manager._execute_transition()
        assert len(manager._state_stack) == 3

        manager.pop_state()
        manager._execute_transition()
        assert len(manager._state_stack) == 2
        assert manager.get_current_state() is gameplay

        manager.change_state("menu", StateTransition.REPLACE)
        manager._execute_transition()
        assert len(manager._state_stack) == 2
        assert manager.get_current_state() is menu

    def test_pop_state_method(self):
        """Test pop_state method queues transition"""
        manager = StateManager()
        menu = MenuState()

        manager.register_state(menu)
        manager.change_state("menu", StateTransition.PUSH)
        manager._execute_transition()

        manager.pop_state()
        assert manager._pending_transition is not None
        assert manager._pending_transition[1] == StateTransition.POP

    def test_multiple_updates_single_transition(self):
        """Test only one transition executes per update"""
        manager = StateManager()
        menu = MenuState()
        world = MockWorld()
        gameplay = GameplayState(world)

        manager.register_state(menu).register_state(gameplay)

        # Queue first transition
        manager.change_state("menu", StateTransition.PUSH)
        # Queue second transition (should overwrite)
        manager.change_state("gameplay", StateTransition.PUSH)

        # Execute - should only do the last queued transition
        manager._execute_transition()

        # Should have both states (gameplay pushed on top of menu)
        assert manager.get_current_state() is gameplay


# ===========================
# Custom GameState Tests
# ===========================


class CustomTestState(GameState):
    """Custom state for testing abstract base class"""

    def __init__(self):
        super().__init__("custom")
        self.entered = False
        self.exited = False
        self.updated = False
        self.rendered = False
        self.event_handled = False

    def enter(self, data=None):
        self.entered = True

    def exit(self):
        self.exited = True

    def update(self, delta_time):
        self.updated = True

    def render(self):
        self.rendered = True

    def handle_event(self, event):
        self.event_handled = True


class TestCustomGameState:
    """Test custom GameState implementation"""

    def test_custom_state_lifecycle(self):
        """Test custom state lifecycle methods"""
        manager = StateManager()
        custom = CustomTestState()

        manager.register_state(custom)
        manager.change_state("custom", StateTransition.PUSH)
        manager._execute_transition()

        assert custom.entered is True

        manager.update(0.016)
        assert custom.updated is True

        manager.render()
        assert custom.rendered is True

        manager.handle_event({"type": "test"})
        assert custom.event_handled is True

        manager.pop_state()
        manager._execute_transition()
        assert custom.exited is True

    def test_set_manager(self):
        """Test set_manager method"""
        state = CustomTestState()
        manager = StateManager()

        state.set_manager(manager)
        assert state._state_manager is manager
