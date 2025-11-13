"""
Comprehensive tests for Input Manager

Tests keyboard, mouse, action mapping, and axis input.
"""

import pytest
import pygame
from unittest.mock import Mock, patch
from neonworks.input.input_manager import InputManager, InputState, MouseButton


@pytest.fixture
def input_manager():
    """Create a fresh input manager for each test"""
    pygame.init()
    manager = InputManager()
    return manager


class TestKeyboardInput:
    """Test keyboard input tracking"""

    def test_key_pressed_detection(self, input_manager):
        """Test detecting when a key is pressed"""
        # Simulate W key press
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_key_pressed(pygame.K_w)
            assert not input_manager.is_key_pressed(pygame.K_s)

    def test_key_just_pressed(self, input_manager):
        """Test detecting when a key was just pressed this frame"""
        # First frame: no keys
        with patch("pygame.key.get_pressed") as mock_pressed:
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)

            assert not input_manager.is_key_just_pressed(pygame.K_w)

        # Second frame: W pressed
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_key_just_pressed(pygame.K_w)
            assert input_manager.is_key_pressed(pygame.K_w)

    def test_key_held(self, input_manager):
        """Test detecting when a key is held down"""
        # Frame 1: Press W
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)

        # Frame 2: Still holding W
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)

            assert not input_manager.is_key_just_pressed(pygame.K_w)
            assert input_manager.is_key_pressed(pygame.K_w)
            assert input_manager.get_key_state(pygame.K_w) == InputState.HELD

    def test_key_just_released(self, input_manager):
        """Test detecting when a key was just released"""
        # Frame 1: Press W
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)

        # Frame 2: Release W
        with patch("pygame.key.get_pressed") as mock_pressed:
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)

            assert input_manager.is_key_just_released(pygame.K_w)
            assert not input_manager.is_key_pressed(pygame.K_w)

    def test_key_states(self, input_manager):
        """Test all key states"""
        with patch("pygame.key.get_pressed") as mock_pressed:
            # Released state
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)
            assert input_manager.get_key_state(pygame.K_w) == InputState.RELEASED

            # Just pressed
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)
            assert input_manager.get_key_state(pygame.K_w) == InputState.JUST_PRESSED

            # Held
            input_manager.update(0.016)
            assert input_manager.get_key_state(pygame.K_w) == InputState.HELD

            # Just released
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)
            assert input_manager.get_key_state(pygame.K_w) == InputState.JUST_RELEASED


class TestMouseInput:
    """Test mouse input tracking"""

    def test_mouse_position(self, input_manager):
        """Test mouse position tracking"""
        with patch("pygame.mouse.get_pos", return_value=(100, 200)):
            with patch("pygame.mouse.get_pressed", return_value=(False, False, False)):
                input_manager.update(0.016)

                assert input_manager.get_mouse_position() == (100, 200)
                assert input_manager.get_mouse_x() == 100
                assert input_manager.get_mouse_y() == 200

    def test_mouse_button_pressed(self, input_manager):
        """Test mouse button press detection"""
        with patch("pygame.mouse.get_pos", return_value=(0, 0)):
            with patch("pygame.mouse.get_pressed", return_value=(True, False, False)):
                input_manager.update(0.016)

                assert input_manager.is_mouse_button_pressed(MouseButton.LEFT.value)
                assert not input_manager.is_mouse_button_pressed(
                    MouseButton.RIGHT.value
                )

    def test_mouse_button_just_pressed(self, input_manager):
        """Test detecting mouse button just pressed"""
        with patch("pygame.mouse.get_pos", return_value=(0, 0)):
            # Frame 1: No buttons
            with patch("pygame.mouse.get_pressed", return_value=(False, False, False)):
                input_manager.update(0.016)

            # Frame 2: Left button pressed
            with patch("pygame.mouse.get_pressed", return_value=(True, False, False)):
                input_manager.update(0.016)

                assert input_manager.is_mouse_button_just_pressed(
                    MouseButton.LEFT.value
                )

    def test_mouse_wheel(self, input_manager):
        """Test mouse wheel input"""
        # Create a mock event
        event = Mock()
        event.type = pygame.MOUSEWHEEL
        event.y = 1  # Scroll up

        input_manager.process_event(event)

        assert input_manager.get_mouse_wheel() == 1

        # Wheel resets after update
        with patch("pygame.mouse.get_pos", return_value=(0, 0)):
            with patch("pygame.mouse.get_pressed", return_value=(False, False, False)):
                input_manager.update(0.016)

        assert input_manager.get_mouse_wheel() == 0


class TestActionMapping:
    """Test action mapping system"""

    def test_action_mapping(self, input_manager):
        """Test mapping actions to keys"""
        input_manager.map_action("test_action", [pygame.K_SPACE, pygame.K_RETURN])

        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_SPACE] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_action_pressed("test_action")

    def test_multiple_keys_for_action(self, input_manager):
        """Test that multiple keys can trigger the same action"""
        # Use regular keys instead of scan codes
        input_manager.map_action("move_up", [pygame.K_w, pygame.K_i])

        # Test with W key
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_action_pressed("move_up")

        # Test with I key (alternate binding)
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_i] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_action_pressed("move_up")

    def test_action_just_pressed(self, input_manager):
        """Test action just pressed detection"""
        input_manager.map_action("jump", [pygame.K_SPACE])

        with patch("pygame.key.get_pressed") as mock_pressed:
            # Frame 1: No keys
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)

            # Frame 2: Space pressed
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_SPACE] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)

            assert input_manager.is_action_just_pressed("jump")

    def test_add_remove_keys_from_action(self, input_manager):
        """Test dynamically adding/removing keys from actions"""
        input_manager.map_action("attack", [pygame.K_SPACE])

        # Add another key (use regular key codes)
        input_manager.add_key_to_action("attack", pygame.K_x)

        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_x] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_action_pressed("attack")

        # Remove the key
        input_manager.remove_key_from_action("attack", pygame.K_x)

        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_x] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert not input_manager.is_action_pressed("attack")

    def test_action_callbacks(self, input_manager):
        """Test action callback registration"""
        callback_called = []

        def test_callback():
            callback_called.append(True)

        input_manager.map_action("test", [pygame.K_SPACE])
        input_manager.register_action_callback("test", test_callback)

        with patch("pygame.key.get_pressed") as mock_pressed:
            # Frame 1: No keys
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)

            # Frame 2: Space pressed
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_SPACE] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)

            assert len(callback_called) == 1


class TestAxisInput:
    """Test axis input for analog movement"""

    def test_get_axis(self, input_manager):
        """Test getting axis value from two actions"""
        input_manager.map_action("left", [pygame.K_a])
        input_manager.map_action("right", [pygame.K_d])

        with patch("pygame.key.get_pressed") as mock_pressed:
            # Press right
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_d] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.get_axis("left", "right") == 1.0

        with patch("pygame.key.get_pressed") as mock_pressed:
            # Press left
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_a] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.get_axis("left", "right") == -1.0

    def test_movement_vector(self, input_manager):
        """Test getting normalized movement vector"""
        with patch("pygame.key.get_pressed") as mock_pressed:
            # Press W
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            horizontal, vertical = input_manager.get_movement_vector()
            assert horizontal == 0.0
            assert vertical == -1.0

        with patch("pygame.key.get_pressed") as mock_pressed:
            # Press W and D (diagonal)
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            pressed_keys[pygame.K_d] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            horizontal, vertical = input_manager.get_movement_vector()

            # Diagonal should be normalized
            assert abs(horizontal - 0.7071) < 0.001
            assert abs(vertical - (-0.7071)) < 0.001


class TestTextInput:
    """Test text input mode"""

    def test_text_input_enable_disable(self, input_manager):
        """Test enabling and disabling text input"""
        assert not input_manager._text_input_enabled

        input_manager.enable_text_input()
        assert input_manager._text_input_enabled

        input_manager.disable_text_input()
        assert not input_manager._text_input_enabled

    def test_text_input_capture(self, input_manager):
        """Test capturing text input"""
        input_manager.enable_text_input()

        # Simulate typing "hello"
        events = [
            Mock(type=pygame.KEYDOWN, key=pygame.K_h, scancode=0, unicode="h"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_e, scancode=0, unicode="e"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_l, scancode=0, unicode="l"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_l, scancode=0, unicode="l"),
            Mock(type=pygame.KEYDOWN, key=pygame.K_o, scancode=0, unicode="o"),
        ]

        for event in events:
            input_manager.process_event(event)

        assert input_manager.get_text_input() == "hello"

    def test_text_input_backspace(self, input_manager):
        """Test backspace in text input"""
        input_manager.enable_text_input()

        # Type "test"
        for char in "test":
            event = Mock(type=pygame.KEYDOWN, key=ord(char), scancode=0, unicode=char)
            input_manager.process_event(event)

        assert input_manager.get_text_input() == "test"

        # Press backspace
        event = Mock(
            type=pygame.KEYDOWN, key=pygame.K_BACKSPACE, scancode=0, unicode=""
        )
        input_manager.process_event(event)

        assert input_manager.get_text_input() == "tes"


class TestUtilities:
    """Test utility functions"""

    def test_clear_all(self, input_manager):
        """Test clearing all input state"""
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            assert input_manager.is_key_pressed(pygame.K_w)

        input_manager.clear_all()

        assert not input_manager.is_key_pressed(pygame.K_w)

    def test_get_any_key_pressed(self, input_manager):
        """Test getting any pressed key"""
        with patch("pygame.key.get_pressed") as mock_pressed:
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys

            input_manager.update(0.016)

            key = input_manager.get_any_key_pressed()
            assert key == pygame.K_w

    def test_get_any_key_just_pressed(self, input_manager):
        """Test getting any key just pressed"""
        with patch("pygame.key.get_pressed") as mock_pressed:
            # Frame 1: No keys
            mock_pressed.return_value = [False] * 512
            input_manager.update(0.016)

            # Frame 2: W pressed
            pressed_keys = [False] * 512
            pressed_keys[pygame.K_w] = True
            mock_pressed.return_value = pressed_keys
            input_manager.update(0.016)

            key = input_manager.get_any_key_just_pressed()
            assert key == pygame.K_w


# Run tests with: pytest engine/tests/test_input_manager.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
