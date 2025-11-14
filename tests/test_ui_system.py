"""
Comprehensive tests for UI System

Tests widgets, layouts, event handling, and rendering.
"""

from unittest.mock import MagicMock, Mock

import pygame
import pytest

from neonworks.ui.ui_system import (
    Anchor,
    HorizontalLayout,
    UIBuilder,
    UIButton,
    UIContainer,
    UILabel,
    UIManager,
    UIPanel,
    UIStyle,
    VerticalLayout,
)


@pytest.fixture
def screen():
    """Create a test screen surface"""
    pygame.init()
    return pygame.Surface((800, 600))


class TestUIStyle:
    """Test UI style"""

    def test_style_creation(self):
        """Test creating a UI style"""
        style = UIStyle()

        assert style.background_color == (50, 50, 50, 200)
        assert style.padding == 10
        assert style.font_size == 16

    def test_style_custom_values(self):
        """Test custom style values"""
        style = UIStyle(background_color=(255, 0, 0, 255), padding=20, font_size=24)

        assert style.background_color == (255, 0, 0, 255)
        assert style.padding == 20
        assert style.font_size == 24


class TestUILabel:
    """Test label widget"""

    def test_label_creation(self):
        """Test creating a label"""
        label = UILabel(text="Hello", x=10, y=20, width=100, height=30)

        assert label.text == "Hello"
        assert label.x == 10
        assert label.y == 20

    def test_label_set_text(self):
        """Test changing label text"""
        label = UILabel(text="Hello")
        label.set_text("World")

        assert label.text == "World"

    def test_label_render(self, screen):
        """Test rendering a label"""
        label = UILabel(text="Test", x=100, y=100, width=100, height=30)

        # Should not crash
        label.render(screen)

    def test_label_invisible(self, screen):
        """Test invisible label doesn't render"""
        label = UILabel(text="Test", x=100, y=100)
        label.visible = False

        # Should not crash
        label.render(screen)


class TestUIButton:
    """Test button widget"""

    def test_button_creation(self):
        """Test creating a button"""
        button = UIButton(text="Click Me", x=10, y=20, width=120, height=40)

        assert button.text == "Click Me"
        assert button.x == 10
        assert button.enabled

    def test_button_click_callback(self):
        """Test button click callback"""
        clicked = []

        def on_click():
            clicked.append(True)

        button = UIButton(text="Click", x=10, y=10, width=100, height=40)
        button.on_click = on_click

        # Simulate click
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (50, 25)})
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (50, 25)})

        button.handle_event(event_down)
        button.handle_event(event_up)

        assert len(clicked) == 1

    def test_button_hover(self):
        """Test button hover state"""
        button = UIButton(x=10, y=10, width=100, height=40)

        # Mouse enter
        event = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (50, 25)})
        button.handle_event(event)

        assert button.hovered

        # Mouse leave
        event = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (200, 200)})
        button.handle_event(event)

        assert not button.hovered

    def test_button_disabled_no_click(self):
        """Test disabled button doesn't trigger click"""
        clicked = []

        button = UIButton(x=10, y=10, width=100, height=40)
        button.on_click = lambda: clicked.append(True)
        button.enabled = False

        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (50, 25)})
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (50, 25)})

        button.handle_event(event_down)
        button.handle_event(event_up)

        assert len(clicked) == 0

    def test_button_render(self, screen):
        """Test rendering a button"""
        button = UIButton(text="Test", x=100, y=100, width=120, height=40)

        # Should not crash
        button.render(screen)


class TestUIPanel:
    """Test panel widget"""

    def test_panel_creation(self):
        """Test creating a panel"""
        panel = UIPanel(x=10, y=10, width=200, height=150)

        assert panel.x == 10
        assert panel.width == 200

    def test_panel_render(self, screen):
        """Test rendering a panel"""
        panel = UIPanel(x=100, y=100, width=200, height=150)

        # Should not crash
        panel.render(screen)


class TestUIContainer:
    """Test container widget"""

    def test_container_creation(self):
        """Test creating a container"""
        container = UIContainer(x=10, y=10, width=300, height=200)

        assert container.x == 10
        assert len(container.children) == 0

    def test_container_add_child(self):
        """Test adding children to container"""
        container = UIContainer()
        button = UIButton(text="Child")

        container.add_child(button)

        assert len(container.children) == 1
        assert button.parent == container

    def test_container_remove_child(self):
        """Test removing children from container"""
        container = UIContainer()
        button = UIButton(text="Child")

        container.add_child(button)
        container.remove_child(button)

        assert len(container.children) == 0
        assert button.parent is None

    def test_container_clear_children(self):
        """Test clearing all children"""
        container = UIContainer()
        container.add_child(UIButton(text="1"))
        container.add_child(UIButton(text="2"))

        container.clear_children()

        assert len(container.children) == 0

    def test_container_event_propagation(self):
        """Test events propagate to children"""
        container = UIContainer(x=0, y=0, width=300, height=200)

        clicked = []
        button = UIButton(text="Child", x=50, y=50, width=100, height=40)
        button.on_click = lambda: clicked.append(True)

        container.add_child(button)

        # Click on button
        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (75, 65)})
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (75, 65)})

        container.handle_event(event_down)
        container.handle_event(event_up)

        assert len(clicked) == 1

    def test_container_render_children(self, screen):
        """Test container renders children"""
        container = UIContainer(x=0, y=0, width=300, height=200)
        button = UIButton(text="Child", x=50, y=50)

        container.add_child(button)

        # Should not crash
        container.render(screen)


class TestUIManager:
    """Test UI manager"""

    def test_manager_creation(self):
        """Test creating a UI manager"""
        manager = UIManager(screen_width=800, screen_height=600)

        assert manager.screen_width == 800
        assert manager.screen_height == 600

    def test_manager_add_widget(self):
        """Test adding widgets to manager"""
        manager = UIManager(800, 600)
        button = UIButton(text="Test")

        manager.add_widget(button)

        assert len(manager.root.children) == 1

    def test_manager_remove_widget(self):
        """Test removing widgets from manager"""
        manager = UIManager(800, 600)
        button = UIButton(text="Test")

        manager.add_widget(button)
        manager.remove_widget(button)

        assert len(manager.root.children) == 0

    def test_manager_clear(self):
        """Test clearing all widgets"""
        manager = UIManager(800, 600)
        manager.add_widget(UIButton(text="1"))
        manager.add_widget(UIButton(text="2"))

        manager.clear()

        assert len(manager.root.children) == 0

    def test_manager_handle_event(self):
        """Test manager handles events"""
        manager = UIManager(800, 600)

        clicked = []
        button = UIButton(text="Test", x=50, y=50, width=100, height=40)
        button.on_click = lambda: clicked.append(True)

        manager.add_widget(button)

        event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (75, 65)})
        event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (75, 65)})

        manager.handle_event(event_down)
        manager.handle_event(event_up)

        assert len(clicked) == 1

    def test_manager_update(self):
        """Test manager updates widgets"""
        manager = UIManager(800, 600)
        button = UIButton(text="Test")
        manager.add_widget(button)

        # Should not crash
        manager.update(0.016)

    def test_manager_render(self, screen):
        """Test manager renders widgets"""
        manager = UIManager(800, 600)
        button = UIButton(text="Test", x=100, y=100)
        manager.add_widget(button)

        # Should not crash
        manager.render(screen)

    def test_manager_apply_anchor(self):
        """Test applying anchor positioning"""
        manager = UIManager(800, 600)

        # Test center
        widget1 = UIButton(width=100, height=40)
        manager.apply_anchor(widget1, Anchor.CENTER)
        assert widget1.x == (800 - 100) // 2
        assert widget1.y == (600 - 40) // 2

        # Test top right
        widget2 = UIButton(width=100, height=40)
        manager.apply_anchor(widget2, Anchor.TOP_RIGHT)
        assert widget2.x == 800 - 100
        assert widget2.y == 0

        # Test bottom center
        widget3 = UIButton(width=100, height=40)
        manager.apply_anchor(widget3, Anchor.BOTTOM_CENTER)
        assert widget3.x == (800 - 100) // 2
        assert widget3.y == 600 - 40


class TestUIBuilder:
    """Test UI builder helpers"""

    def test_create_button(self):
        """Test creating button with builder"""
        clicked = []
        button = UIBuilder.create_button(
            text="Test", x=10, y=20, on_click=lambda: clicked.append(True)
        )

        assert button.text == "Test"
        assert button.x == 10
        assert button.on_click is not None

    def test_create_label(self):
        """Test creating label with builder"""
        label = UIBuilder.create_label(text="Test", x=10, y=20)

        assert label.text == "Test"
        assert label.x == 10

    def test_create_panel(self):
        """Test creating panel with builder"""
        panel = UIBuilder.create_panel(x=10, y=20, width=200, height=150)

        assert panel.x == 10
        assert panel.width == 200

    def test_create_vertical_layout(self):
        """Test creating vertical layout"""
        layout = UIBuilder.create_vertical_layout(x=10, y=20, spacing=5)

        assert layout.x == 10
        assert layout.spacing == 5

    def test_create_horizontal_layout(self):
        """Test creating horizontal layout"""
        layout = UIBuilder.create_horizontal_layout(x=10, y=20, spacing=10)

        assert layout.x == 10
        assert layout.spacing == 10


class TestVerticalLayout:
    """Test vertical layout"""

    def test_vertical_layout_creation(self):
        """Test creating vertical layout"""
        layout = VerticalLayout(x=10, y=10, spacing=10)

        assert layout.x == 10
        assert layout.spacing == 10

    def test_vertical_layout_arranges_children(self):
        """Test vertical layout arranges children vertically"""
        layout = VerticalLayout(x=10, y=10, spacing=5)

        button1 = UIButton(text="1", width=100, height=30)
        button2 = UIButton(text="2", width=100, height=30)

        layout.add_child(button1)
        layout.add_child(button2)

        # First button at layout position
        assert button1.x == 10
        assert button1.y == 10

        # Second button below first with spacing
        assert button2.x == 10
        assert button2.y == 10 + 30 + 5

    def test_vertical_layout_updates_size(self):
        """Test vertical layout updates its size"""
        layout = VerticalLayout(x=10, y=10, spacing=5)

        button1 = UIButton(width=100, height=30)
        button2 = UIButton(width=150, height=40)

        layout.add_child(button1)
        layout.add_child(button2)

        # Width should be max of children
        assert layout.width == 150

        # Height should be sum of children + spacing
        assert layout.height == 30 + 5 + 40


class TestHorizontalLayout:
    """Test horizontal layout"""

    def test_horizontal_layout_creation(self):
        """Test creating horizontal layout"""
        layout = HorizontalLayout(x=10, y=10, spacing=10)

        assert layout.x == 10
        assert layout.spacing == 10

    def test_horizontal_layout_arranges_children(self):
        """Test horizontal layout arranges children horizontally"""
        layout = HorizontalLayout(x=10, y=10, spacing=5)

        button1 = UIButton(text="1", width=100, height=30)
        button2 = UIButton(text="2", width=120, height=30)

        layout.add_child(button1)
        layout.add_child(button2)

        # First button at layout position
        assert button1.x == 10
        assert button1.y == 10

        # Second button to the right with spacing
        assert button2.x == 10 + 100 + 5
        assert button2.y == 10

    def test_horizontal_layout_updates_size(self):
        """Test horizontal layout updates its size"""
        layout = HorizontalLayout(x=10, y=10, spacing=5)

        button1 = UIButton(width=100, height=30)
        button2 = UIButton(width=120, height=50)

        layout.add_child(button1)
        layout.add_child(button2)

        # Width should be sum of children + spacing
        assert layout.width == 100 + 5 + 120

        # Height should be max of children
        assert layout.height == 50


# Run tests with: pytest engine/tests/test_ui_system.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
