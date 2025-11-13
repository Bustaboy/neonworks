"""
Comprehensive tests for Game Loop System

Tests timing, FPS, fixed timestep, and stats.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import pygame
from engine.core.game_loop import GameEngine, EngineConfig


class TestEngineConfig:
    """Test engine configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = EngineConfig()

        assert config.window_width == 1280
        assert config.window_height == 720
        assert config.target_fps == 60
        assert config.fixed_timestep == 1.0 / 60.0

    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = EngineConfig()
        data = config.to_dict()

        assert isinstance(data, dict)
        assert "window_width" in data
        assert "target_fps" in data
        assert data["window_width"] == 1280

    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        data = {"window_width": 1920, "window_height": 1080, "target_fps": 120}

        config = EngineConfig.from_dict(data)

        assert config.window_width == 1920
        assert config.window_height == 1080
        assert config.target_fps == 120


class TestGameEngine:
    """Test game engine"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        yield

        # Cleanup
        pygame.quit()

    def test_engine_creation(self):
        """Test creating game engine"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine(target_fps=60)

            assert engine.target_fps == 60
            assert engine.fixed_timestep == 1.0 / 60.0
            assert not engine.running

    def test_engine_with_custom_params(self):
        """Test creating engine with custom parameters"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine(target_fps=120, fixed_timestep=1.0 / 120.0)

            assert engine.target_fps == 120
            assert engine.fixed_timestep == 1.0 / 120.0

    def test_get_stats(self):
        """Test getting performance stats"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()
            stats = engine.get_stats()

            assert isinstance(stats, dict)
            assert "fps" in stats
            assert "frame_time" in stats
            assert "update_time" in stats
            assert "render_time" in stats

    def test_get_fps_initial(self):
        """Test getting FPS initially returns 0"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()
            fps = engine.get_fps()

            assert fps == 0

    def test_fixed_update_called(self):
        """Test that fixed update is called"""
        with patch("engine.core.game_loop.World") as mock_world, patch(
            "engine.core.game_loop.get_event_manager"
        ) as mock_event_mgr, patch(
            "engine.core.game_loop.StateManager"
        ) as mock_state_mgr, patch(
            "engine.core.game_loop.InputManager"
        ) as mock_input, patch(
            "engine.core.game_loop.AudioManager"
        ) as mock_audio:

            # Setup mocks
            mock_event_mgr.return_value = Mock()
            mock_state_mgr.return_value = Mock()
            mock_input.return_value = Mock()
            mock_audio.return_value = Mock()
            mock_world.return_value = Mock()
            mock_world.return_value.get_entities.return_value = []

            engine = GameEngine()

            # Mock pygame events to return empty list
            with patch("pygame.event.get", return_value=[]):
                # Call fixed update directly
                engine._fixed_update(1.0 / 60.0)

                # Verify managers were updated
                engine.input_manager.update.assert_called_once()
                engine.audio_manager.update.assert_called_once()
                engine.state_manager.update.assert_called_once()

    def test_stop_engine(self):
        """Test stopping the engine"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()
            engine.running = True

            engine.stop()

            assert not engine.running

    def test_update_fps(self):
        """Test FPS counter update"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()

            # Simulate multiple frames over 1 second
            for _ in range(60):
                engine._update_fps(1.0 / 60.0)

            # FPS should be calculated after 1 second
            assert engine.get_fps() == 60

    def test_quit_event_stops_engine(self):
        """Test that pygame QUIT event stops the engine"""
        with patch("engine.core.game_loop.World") as mock_world, patch(
            "engine.core.game_loop.get_event_manager"
        ) as mock_event_mgr, patch(
            "engine.core.game_loop.StateManager"
        ) as mock_state_mgr, patch(
            "engine.core.game_loop.InputManager"
        ) as mock_input, patch(
            "engine.core.game_loop.AudioManager"
        ) as mock_audio:

            # Setup mocks
            mock_event_mgr.return_value = Mock()
            mock_state_mgr.return_value = Mock()
            mock_input.return_value = Mock()
            mock_audio.return_value = Mock()
            mock_world.return_value = Mock()

            engine = GameEngine()
            engine.running = True

            # Create a QUIT event
            quit_event = pygame.event.Event(pygame.QUIT)

            with patch("pygame.event.get", return_value=[quit_event]):
                engine._fixed_update(1.0 / 60.0)

                # Engine should be stopped
                assert not engine.running


class TestFixedTimestep:
    """Test fixed timestep behavior"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        if not pygame.get_init():
            pygame.init()

        yield

        pygame.quit()

    def test_accumulator_behavior(self):
        """Test that accumulator accumulates time correctly"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()

            # Initially accumulator is 0
            assert engine._accumulator == 0.0

            # Add some time
            engine._accumulator = 0.02

            # Accumulator should be updated
            assert engine._accumulator == 0.02

    def test_multiple_updates_per_frame(self):
        """Test that multiple updates can occur in one frame"""
        with patch("engine.core.game_loop.World") as mock_world, patch(
            "engine.core.game_loop.get_event_manager"
        ) as mock_event_mgr, patch(
            "engine.core.game_loop.StateManager"
        ) as mock_state_mgr, patch(
            "engine.core.game_loop.InputManager"
        ) as mock_input, patch(
            "engine.core.game_loop.AudioManager"
        ) as mock_audio:

            # Setup mocks
            mock_event_mgr.return_value = Mock()
            mock_state_mgr.return_value = Mock()
            mock_input.return_value = Mock()
            mock_audio.return_value = Mock()
            mock_world.return_value = Mock()
            mock_world.return_value.get_entities.return_value = []

            engine = GameEngine(fixed_timestep=1.0 / 60.0)

            # Set accumulator to simulate slow frame (2 updates needed)
            engine._accumulator = 2.0 / 60.0

            with patch("pygame.event.get", return_value=[]):
                # Track update calls
                update_count = 0
                original_update = engine._fixed_update

                def count_updates(*args):
                    nonlocal update_count
                    update_count += 1
                    original_update(*args)

                engine._fixed_update = count_updates

                # Manually trigger updates
                updates = 0
                max_updates = 5

                while (
                    engine._accumulator >= engine.fixed_timestep
                    and updates < max_updates
                ):
                    engine._fixed_update(engine.fixed_timestep)
                    engine._accumulator -= engine.fixed_timestep
                    updates += 1

                # Should have called update twice
                assert update_count == 2


class TestPerformanceStats:
    """Test performance statistics"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        if not pygame.get_init():
            pygame.init()

        yield

        pygame.quit()

    def test_stats_initialization(self):
        """Test that stats are initialized"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()

            assert "fps" in engine.stats
            assert "frame_time" in engine.stats
            assert "update_time" in engine.stats
            assert "render_time" in engine.stats
            assert "entity_count" in engine.stats

    def test_stats_are_numbers(self):
        """Test that stats are numeric values"""
        with patch("engine.core.game_loop.World"), patch(
            "engine.core.game_loop.get_event_manager"
        ), patch("engine.core.game_loop.StateManager"), patch(
            "engine.core.game_loop.InputManager"
        ), patch(
            "engine.core.game_loop.AudioManager"
        ):

            engine = GameEngine()
            stats = engine.get_stats()

            for key, value in stats.items():
                assert isinstance(value, (int, float))


# Run tests with: pytest engine/tests/test_game_loop.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
