"""
Comprehensive tests for Scene Management System

Tests scenes, transitions, scene stack, and lifecycle.
"""

from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from neonworks.core.scene import (
    Scene,
    SceneManager,
    SceneState,
    SceneTransition,
    TransitionType,
)


@pytest.fixture
def screen():
    """Create a test screen surface"""
    pygame.init()
    return pygame.Surface((800, 600))


@pytest.fixture
def manager():
    """Create a test scene manager"""
    return SceneManager(screen_width=800, screen_height=600)


class DummyScene(Scene):
    """Helper scene implementation for testing (renamed to avoid pytest collection)"""

    def __init__(self, name: str):
        super().__init__(name)
        self.on_enter_called = False
        self.on_exit_called = False
        self.on_pause_called = False
        self.on_resume_called = False
        self.update_called = False
        self.render_called = False
        self.enter_data = None

    def on_enter(self, data=None):
        self.on_enter_called = True
        self.enter_data = data
        self.state = SceneState.ACTIVE

    def on_exit(self):
        self.on_exit_called = True
        self.state = SceneState.INACTIVE

    def on_pause(self):
        super().on_pause()
        self.on_pause_called = True

    def on_resume(self):
        super().on_resume()
        self.on_resume_called = True

    def update(self, delta_time: float):
        self.update_called = True

    def render(self, screen: pygame.Surface):
        self.render_called = True
        screen.fill((0, 0, 0))


class TestSceneBasic:
    """Test basic Scene class"""

    def test_scene_creation(self):
        """Test creating a scene"""
        scene = DummyScene("test")

        assert scene.name == "test"
        assert scene.state == SceneState.INACTIVE
        assert scene.manager is None

    def test_scene_lifecycle_callbacks(self):
        """Test scene lifecycle callbacks"""
        scene = DummyScene("test")

        scene.on_enter()
        assert scene.on_enter_called
        assert scene.state == SceneState.ACTIVE

        scene.on_exit()
        assert scene.on_exit_called
        assert scene.state == SceneState.INACTIVE

    def test_scene_pause_resume(self):
        """Test scene pause and resume"""
        scene = DummyScene("test")

        scene.on_pause()
        assert scene.on_pause_called
        assert scene.state == SceneState.PAUSED

        scene.on_resume()
        assert scene.on_resume_called
        assert scene.state == SceneState.ACTIVE

    def test_scene_update(self):
        """Test scene update"""
        scene = DummyScene("test")
        scene.update(0.016)

        assert scene.update_called

    def test_scene_render(self, screen):
        """Test scene render"""
        scene = DummyScene("test")
        scene.render(screen)

        assert scene.render_called

    def test_scene_data_dict(self):
        """Test scene data dictionary"""
        scene = DummyScene("test")
        scene.data["foo"] = "bar"

        assert scene.data["foo"] == "bar"


class TestSceneManager:
    """Test SceneManager class"""

    def test_manager_creation(self, manager):
        """Test creating scene manager"""
        assert manager.screen_width == 800
        assert manager.screen_height == 600
        assert manager.current_scene is None
        assert len(manager.scenes) == 0

    def test_register_scene(self, manager):
        """Test registering a scene"""
        scene = DummyScene("test")
        manager.register_scene(scene)

        assert "test" in manager.scenes
        assert scene.manager is manager

    def test_unregister_scene(self, manager):
        """Test unregistering a scene"""
        scene = DummyScene("test")
        manager.register_scene(scene)
        manager.unregister_scene("test")

        assert "test" not in manager.scenes
        assert scene.manager is None

    def test_get_scene(self, manager):
        """Test getting registered scene"""
        scene = DummyScene("test")
        manager.register_scene(scene)

        retrieved = manager.get_scene("test")
        assert retrieved is scene

    def test_get_nonexistent_scene(self, manager):
        """Test getting non-existent scene"""
        retrieved = manager.get_scene("nonexistent")
        assert retrieved is None

    def test_change_scene_instant(self, manager):
        """Test instant scene change"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        assert manager.current_scene is scene1
        assert scene1.on_enter_called

        manager.change_scene("scene2", TransitionType.NONE, 0)
        assert manager.current_scene is scene2
        assert scene1.on_exit_called
        assert scene2.on_enter_called

    def test_change_scene_with_data(self, manager):
        """Test scene change with data"""
        scene = DummyScene("test")
        manager.register_scene(scene)

        data = {"level": 5, "score": 1000}
        manager.change_scene("test", TransitionType.NONE, 0, data)

        assert scene.enter_data == data

    def test_change_scene_nonexistent(self, manager):
        """Test changing to non-existent scene raises error"""
        with pytest.raises(ValueError, match="not registered"):
            manager.change_scene("nonexistent", TransitionType.NONE, 0)

    def test_update_active_scene(self, manager):
        """Test manager updates active scene"""
        scene = DummyScene("test")
        manager.register_scene(scene)
        manager.change_scene("test", TransitionType.NONE, 0)

        manager.update(0.016)
        assert scene.update_called

    def test_render_active_scene(self, manager, screen):
        """Test manager renders active scene"""
        scene = DummyScene("test")
        manager.register_scene(scene)
        manager.change_scene("test", TransitionType.NONE, 0)

        manager.render(screen)
        assert scene.render_called

    def test_handle_event(self, manager):
        """Test manager passes events to scene"""
        scene = DummyScene("test")
        scene.handle_event = Mock(return_value=True)

        manager.register_scene(scene)
        manager.change_scene("test", TransitionType.NONE, 0)

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = manager.handle_event(event)

        assert result
        scene.handle_event.assert_called_once_with(event)


class TestSceneTransitions:
    """Test scene transitions"""

    def test_transition_with_fade(self, manager):
        """Test scene change with fade transition"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.change_scene("scene2", TransitionType.FADE, 1.0)

        assert manager.transition is not None
        assert manager.is_transitioning()
        assert scene1.state == SceneState.TRANSITIONING_OUT

    def test_transition_completion(self, manager):
        """Test transition completes after duration"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.change_scene("scene2", TransitionType.FADE, 0.5)

        # Update past transition duration
        manager.update(1.0)

        assert manager.transition is None
        assert not manager.is_transitioning()
        assert manager.current_scene is scene2
        assert scene2.state == SceneState.ACTIVE

    def test_transition_types(self, manager):
        """Test different transition types"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        transition_types = [
            TransitionType.FADE,
            TransitionType.SLIDE_LEFT,
            TransitionType.SLIDE_RIGHT,
            TransitionType.SLIDE_UP,
            TransitionType.SLIDE_DOWN,
            TransitionType.DISSOLVE,
            TransitionType.ZOOM_IN,
            TransitionType.ZOOM_OUT,
        ]

        for trans_type in transition_types:
            manager.change_scene("scene1", TransitionType.NONE, 0)
            manager.change_scene("scene2", trans_type, 0.1)

            assert manager.transition is not None
            assert manager.transition.type == trans_type

            # Complete transition
            manager.update(0.2)

    def test_no_transition_on_inactive_scene(self, manager):
        """Test scene doesn't update during transition out"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        scene1.update_called = False

        manager.change_scene("scene2", TransitionType.FADE, 0.5)

        # Scene1 should not update during transition
        manager.update(0.1)
        assert not scene1.update_called


class TestSceneStack:
    """Test scene stack (push/pop)"""

    def test_push_scene(self, manager):
        """Test pushing scene onto stack"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.push_scene("scene2", TransitionType.NONE, 0)

        assert manager.get_stack_size() == 1
        assert manager.current_scene is scene2
        assert scene1.on_pause_called

    def test_pop_scene(self, manager):
        """Test popping scene from stack"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.push_scene("scene2", TransitionType.NONE, 0)
        manager.pop_scene(TransitionType.NONE, 0)

        assert manager.get_stack_size() == 0
        assert manager.current_scene is scene1
        assert scene1.on_resume_called
        assert scene2.on_exit_called

    def test_push_multiple_scenes(self, manager):
        """Test pushing multiple scenes"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")
        scene3 = DummyScene("scene3")

        manager.register_scene(scene1)
        manager.register_scene(scene2)
        manager.register_scene(scene3)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.push_scene("scene2", TransitionType.NONE, 0)
        manager.push_scene("scene3", TransitionType.NONE, 0)

        assert manager.get_stack_size() == 2
        assert manager.current_scene is scene3

    def test_pop_multiple_scenes(self, manager):
        """Test popping multiple scenes"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")
        scene3 = DummyScene("scene3")

        manager.register_scene(scene1)
        manager.register_scene(scene2)
        manager.register_scene(scene3)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.push_scene("scene2", TransitionType.NONE, 0)
        manager.push_scene("scene3", TransitionType.NONE, 0)

        manager.pop_scene(TransitionType.NONE, 0)
        assert manager.current_scene is scene2

        manager.pop_scene(TransitionType.NONE, 0)
        assert manager.current_scene is scene1

    def test_pop_empty_stack_raises_error(self, manager):
        """Test popping empty stack raises error"""
        scene = DummyScene("test")
        manager.register_scene(scene)
        manager.change_scene("test", TransitionType.NONE, 0)

        with pytest.raises(RuntimeError, match="No scenes to pop"):
            manager.pop_scene(TransitionType.NONE, 0)

    def test_clear_stack(self, manager):
        """Test clearing scene stack"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)
        manager.push_scene("scene2", TransitionType.NONE, 0)

        manager.clear_stack()
        assert manager.get_stack_size() == 0

    def test_push_nonexistent_scene(self, manager):
        """Test pushing non-existent scene raises error"""
        scene1 = DummyScene("scene1")
        manager.register_scene(scene1)
        manager.change_scene("scene1", TransitionType.NONE, 0)

        with pytest.raises(ValueError, match="not registered"):
            manager.push_scene("nonexistent", TransitionType.NONE, 0)


class TestSceneTransitionClass:
    """Test SceneTransition class"""

    def test_transition_creation(self):
        """Test creating transition"""
        transition = SceneTransition(TransitionType.FADE, 1.0, 800, 600)

        assert transition.type == TransitionType.FADE
        assert transition.duration == 1.0
        assert transition.elapsed == 0.0
        assert not transition.is_complete

    def test_transition_progress(self):
        """Test transition progress calculation"""
        transition = SceneTransition(TransitionType.FADE, 2.0, 800, 600)

        assert transition.progress == 0.0

        transition.update(1.0)
        assert transition.progress == 0.5

        transition.update(1.0)
        assert transition.progress == 1.0

    def test_transition_completion(self):
        """Test transition completes"""
        transition = SceneTransition(TransitionType.FADE, 0.5, 800, 600)

        transition.update(1.0)
        assert transition.is_complete

    def test_transition_zero_duration(self):
        """Test transition with zero duration"""
        transition = SceneTransition(TransitionType.FADE, 0.0, 800, 600)

        assert transition.progress == 1.0
        assert transition.is_complete

    def test_apply_fade_transition(self, screen):
        """Test applying fade transition"""
        transition = SceneTransition(TransitionType.FADE, 1.0, 800, 600)

        old_surface = pygame.Surface((800, 600))
        old_surface.fill((255, 0, 0))

        new_surface = pygame.Surface((800, 600))
        new_surface.fill((0, 0, 255))

        transition.update(0.5)
        transition.apply(screen, old_surface, new_surface)

        # Should render without error
        assert True

    def test_apply_slide_transitions(self, screen):
        """Test applying slide transitions"""
        new_surface = pygame.Surface((800, 600))
        new_surface.fill((0, 0, 255))

        slide_types = [
            TransitionType.SLIDE_LEFT,
            TransitionType.SLIDE_RIGHT,
            TransitionType.SLIDE_UP,
            TransitionType.SLIDE_DOWN,
        ]

        for slide_type in slide_types:
            transition = SceneTransition(slide_type, 1.0, 800, 600)
            transition.update(0.5)
            transition.apply(screen, None, new_surface)

    def test_apply_dissolve_transition(self, screen):
        """Test applying dissolve transition"""
        transition = SceneTransition(TransitionType.DISSOLVE, 1.0, 800, 600)

        old_surface = pygame.Surface((800, 600))
        new_surface = pygame.Surface((800, 600))

        transition.update(0.5)
        transition.apply(screen, old_surface, new_surface)

    def test_apply_zoom_transitions(self, screen):
        """Test applying zoom transitions"""
        new_surface = pygame.Surface((800, 600))
        new_surface.fill((0, 0, 255))

        zoom_types = [TransitionType.ZOOM_IN, TransitionType.ZOOM_OUT]

        for zoom_type in zoom_types:
            transition = SceneTransition(zoom_type, 1.0, 800, 600)
            transition.update(0.5)
            transition.apply(screen, None, new_surface)


class TestSceneIntegration:
    """Integration tests for scene system"""

    def test_scene_change_methods(self, manager):
        """Test scene change through scene methods"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)

        # Change scene through scene method
        scene1.change_scene("scene2", TransitionType.NONE, 0)

        assert manager.current_scene is scene2

    def test_push_pop_through_scene_methods(self, manager):
        """Test push/pop through scene methods"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        manager.change_scene("scene1", TransitionType.NONE, 0)

        # Push through scene method
        scene1.push_scene("scene2", TransitionType.NONE, 0)
        assert manager.current_scene is scene2

        # Pop through scene method
        scene2.pop_scene(TransitionType.NONE, 0)
        assert manager.current_scene is scene1

    def test_full_game_loop_simulation(self, manager, screen):
        """Test full game loop with scenes"""
        menu_scene = DummyScene("menu")
        game_scene = DummyScene("game")
        pause_scene = DummyScene("pause")

        manager.register_scene(menu_scene)
        manager.register_scene(game_scene)
        manager.register_scene(pause_scene)

        # Start at menu
        manager.change_scene("menu", TransitionType.NONE, 0)

        # Simulate frames
        for _ in range(10):
            manager.update(0.016)
            manager.render(screen)

        # Start game
        manager.change_scene("game", TransitionType.FADE, 0.5)

        # Complete transition
        for _ in range(40):
            manager.update(0.016)
            manager.render(screen)

        assert manager.current_scene is game_scene

        # Pause game
        manager.push_scene("pause", TransitionType.FADE, 0.3)

        # Complete transition
        for _ in range(20):
            manager.update(0.016)
            manager.render(screen)

        assert manager.current_scene is pause_scene
        assert game_scene.on_pause_called

        # Resume game
        manager.pop_scene(TransitionType.FADE, 0.3)

        # Complete transition
        for _ in range(20):
            manager.update(0.016)
            manager.render(screen)

        assert manager.current_scene is game_scene
        assert game_scene.on_resume_called

    def test_scene_state_tracking(self, manager):
        """Test scene state is properly tracked"""
        scene1 = DummyScene("scene1")
        scene2 = DummyScene("scene2")

        manager.register_scene(scene1)
        manager.register_scene(scene2)

        # Initial state
        assert scene1.state == SceneState.INACTIVE

        # Activate scene1
        manager.change_scene("scene1", TransitionType.NONE, 0)
        assert scene1.state == SceneState.ACTIVE

        # Transition to scene2
        manager.change_scene("scene2", TransitionType.FADE, 0.5)
        assert scene1.state == SceneState.TRANSITIONING_OUT

        # Complete transition
        manager.update(1.0)
        assert scene1.state == SceneState.INACTIVE
        assert scene2.state == SceneState.ACTIVE

    def test_scene_data_persistence(self, manager):
        """Test scene data persists across transitions"""
        scene = DummyScene("test")
        manager.register_scene(scene)

        scene.data["persistent"] = "value"

        manager.change_scene("test", TransitionType.NONE, 0)
        assert scene.data["persistent"] == "value"


# Run tests with: pytest engine/tests/test_scene.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
