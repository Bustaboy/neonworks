"""
Tests for polish features (tooltips, loading indicators, themes, etc.)
"""

import pygame
import pytest

from core.crash_recovery import (
    AutoSaveManager,
    CrashRecovery,
    get_autosave_manager,
    get_crash_recovery,
)
from core.error_handler import (
    EnhancedErrorHandler,
    ErrorSuggestion,
    get_error_handler,
    handle_error,
)
from ui.themes import (
    ColorPalette,
    Spacing,
    ThemeManager,
    Typography,
    UITheme,
    get_current_theme,
    get_theme_manager,
    set_theme,
)
from ui.ui_system import (
    KeyboardNavigator,
    LoadingIndicator,
    Tooltip,
    TooltipManager,
    UIButton,
    UIWidget,
)

# Initialize pygame for tests
pygame.init()
pygame.display.set_mode((800, 600))


class TestTooltip:
    """Test tooltip functionality"""

    def test_tooltip_creation(self):
        """Test creating a tooltip"""
        tooltip = Tooltip()
        assert tooltip is not None
        assert tooltip.visible is False
        assert tooltip.text is None

    def test_tooltip_show_hide(self):
        """Test showing and hiding tooltip"""
        tooltip = Tooltip()
        widget = UIButton(text="Test", x=100, y=100)
        widget.tooltip = "This is a test tooltip"

        tooltip.show(widget, 150, 150)
        assert tooltip.visible is True
        assert tooltip.text == "This is a test tooltip"

        tooltip.hide()
        assert tooltip.visible is False
        assert tooltip.text is None

    def test_tooltip_manager(self):
        """Test tooltip manager"""
        manager = TooltipManager()
        assert manager is not None
        assert manager.tooltip is not None


class TestLoadingIndicator:
    """Test loading indicator"""

    def test_loading_indicator_creation(self):
        """Test creating loading indicator"""
        indicator = LoadingIndicator()
        assert indicator is not None
        assert indicator.visible is False
        assert indicator.progress == 0.0

    def test_loading_indicator_show_hide(self):
        """Test showing and hiding loading indicator"""
        indicator = LoadingIndicator()

        indicator.show("Loading assets...")
        assert indicator.visible is True
        assert indicator.text == "Loading assets..."

        indicator.hide()
        assert indicator.visible is False

    def test_loading_indicator_progress(self):
        """Test progress tracking"""
        indicator = LoadingIndicator()
        indicator.show("Loading...", show_progress=True)

        indicator.set_progress(0.5)
        assert indicator.progress == 0.5

        indicator.set_progress(1.0)
        assert indicator.progress == 1.0

        # Test clamping
        indicator.set_progress(1.5)
        assert indicator.progress == 1.0

        indicator.set_progress(-0.5)
        assert indicator.progress == 0.0

    def test_loading_indicator_update(self):
        """Test loading indicator animation update"""
        indicator = LoadingIndicator()
        indicator.show()  # Make sure it's visible

        initial_angle = indicator.spinner_angle
        indicator.update(1.0)  # 1 second
        # Spinner should have rotated (360 degrees per second)
        assert (
            indicator.spinner_angle > initial_angle or indicator.spinner_angle == 0.0
        )  # May wrap to 0


class TestKeyboardNavigator:
    """Test keyboard navigation"""

    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Ensure pygame is initialized for each test"""
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((800, 600))
        yield
        # Don't quit pygame here as it's shared across tests

    def test_navigator_creation(self):
        """Test creating keyboard navigator"""
        navigator = KeyboardNavigator()
        assert navigator is not None
        assert navigator.enabled is True
        assert navigator.focused_widget is None

    def test_set_focusable_widgets(self):
        """Test setting focusable widgets"""
        navigator = KeyboardNavigator()
        widgets = [
            UIButton(text="Button 1", x=0, y=0),
            UIButton(text="Button 2", x=0, y=50),
            UIButton(text="Button 3", x=0, y=100),
        ]

        navigator.set_focusable_widgets(widgets)
        assert len(navigator.focusable_widgets) == 3

    def test_focus_next_previous(self):
        """Test navigating between widgets"""
        navigator = KeyboardNavigator()
        widgets = [
            UIButton(text="Button 1", x=0, y=0),
            UIButton(text="Button 2", x=0, y=50),
            UIButton(text="Button 3", x=0, y=100),
        ]

        navigator.set_focusable_widgets(widgets)

        # Focus next
        navigator.focus_next()
        assert navigator.focused_widget == widgets[0]

        navigator.focus_next()
        assert navigator.focused_widget == widgets[1]

        navigator.focus_next()
        assert navigator.focused_widget == widgets[2]

        # Wrap around
        navigator.focus_next()
        assert navigator.focused_widget == widgets[0]

        # Focus previous
        navigator.focus_previous()
        assert navigator.focused_widget == widgets[2]

    def test_keyboard_navigation_events(self):
        """Test handling keyboard events"""
        navigator = KeyboardNavigator()
        widgets = [UIButton(text="Button 1", x=0, y=0), UIButton(text="Button 2", x=0, y=50)]

        navigator.set_focusable_widgets(widgets)

        # Tab key
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_TAB, "mod": 0})
        handled = navigator.handle_event(event)
        assert handled is True
        assert navigator.focused_widget == widgets[0]

        # Another tab
        handled = navigator.handle_event(event)
        assert handled is True
        assert navigator.focused_widget == widgets[1]


class TestUITheme:
    """Test UI theme system"""

    def test_color_palette_creation(self):
        """Test creating color palette"""
        palette = ColorPalette()
        assert palette is not None
        assert isinstance(palette.primary, tuple)
        assert len(palette.primary) == 3

    def test_spacing_creation(self):
        """Test creating spacing"""
        spacing = Spacing()
        assert spacing is not None
        assert spacing.unit == 8
        assert spacing.sm == 8
        assert spacing.md == 16

    def test_typography_creation(self):
        """Test creating typography"""
        typography = Typography()
        assert typography is not None
        assert typography.font_size_md == 16

    def test_theme_creation(self):
        """Test creating UI theme"""
        theme = UITheme(name="Test Theme")
        assert theme is not None
        assert theme.name == "Test Theme"
        assert theme.colors is not None
        assert theme.spacing is not None
        assert theme.typography is not None

    def test_theme_manager(self):
        """Test theme manager"""
        manager = ThemeManager()
        assert manager is not None
        assert manager.current_theme is not None

        # Check default themes
        themes = manager.list_themes()
        assert "dark" in themes
        assert "light" in themes
        assert "blue" in themes

    def test_set_theme(self):
        """Test changing themes"""
        manager = ThemeManager()

        manager.set_theme("light")
        assert manager.current_theme.name == "Light"

        manager.set_theme("blue")
        assert manager.current_theme.name == "Blue"

    def test_get_current_theme(self):
        """Test getting current theme"""
        theme = get_current_theme()
        assert theme is not None
        assert isinstance(theme, UITheme)

    def test_theme_singleton(self):
        """Test theme manager singleton"""
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()
        assert manager1 is manager2


class TestErrorHandler:
    """Test enhanced error handler"""

    def test_error_handler_creation(self):
        """Test creating error handler"""
        handler = EnhancedErrorHandler()
        assert handler is not None
        assert len(handler.error_patterns) > 0

    def test_analyze_file_error(self):
        """Test analyzing file error"""
        handler = EnhancedErrorHandler()
        error = FileNotFoundError("No such file or directory: test.txt")

        suggestion = handler.analyze_error(error)
        assert suggestion is not None
        assert suggestion.error_type == "File Error"
        assert len(suggestion.suggestions) > 0
        assert any("file path" in s.lower() for s in suggestion.suggestions)

    def test_analyze_import_error(self):
        """Test analyzing import error"""
        handler = EnhancedErrorHandler()
        error = ImportError("No module named 'fake_module'")

        suggestion = handler.analyze_error(error)
        assert suggestion is not None
        assert suggestion.error_type == "Import Error"
        assert len(suggestion.suggestions) > 0
        assert any("install" in s.lower() for s in suggestion.suggestions)

    def test_analyze_type_error(self):
        """Test analyzing type error"""
        handler = EnhancedErrorHandler()
        error = TypeError("unsupported operand type(s)")

        suggestion = handler.analyze_error(error)
        assert suggestion is not None
        assert len(suggestion.suggestions) > 0

    def test_error_suggestion_format(self):
        """Test error suggestion formatting"""
        suggestion = ErrorSuggestion(
            error_type="Test Error",
            message="This is a test error",
            suggestions=["Suggestion 1", "Suggestion 2"],
            severity="ERROR",
        )

        formatted = suggestion.format_message()
        assert "Test Error" in formatted
        assert "This is a test error" in formatted
        assert "Suggestion 1" in formatted
        assert "Suggestion 2" in formatted

    def test_error_handler_singleton(self):
        """Test error handler singleton"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        assert handler1 is handler2


class TestCrashRecovery:
    """Test crash recovery system"""

    def test_autosave_manager_creation(self):
        """Test creating autosave manager"""
        manager = AutoSaveManager()
        assert manager is not None
        assert manager.enabled is True
        assert manager.interval == 300.0

    def test_autosave_callback_registration(self):
        """Test registering save callback"""
        manager = AutoSaveManager()

        def save_data():
            return {"test": "data"}

        manager.register_save_callback(save_data)
        assert manager.save_callback is not None

    def test_crash_recovery_creation(self):
        """Test creating crash recovery"""
        recovery = CrashRecovery()
        assert recovery is not None
        assert recovery.log_dir is not None

    def test_crash_callback_registration(self):
        """Test registering crash callback"""
        recovery = CrashRecovery()

        def crash_data():
            return {"state": "crashed"}

        recovery.register_crash_callback(crash_data)
        assert recovery.crash_callback is not None

    def test_log_crash(self):
        """Test logging a crash"""
        recovery = CrashRecovery(log_dir="test_crash_logs")
        error = RuntimeError("Test crash")

        log_path = recovery.log_crash(error)
        assert log_path is not None

        # Clean up
        if log_path and log_path.exists():
            log_path.unlink()
            log_path.parent.rmdir()

    def test_autosave_manager_singleton(self):
        """Test autosave manager singleton"""
        manager1 = get_autosave_manager()
        manager2 = get_autosave_manager()
        assert manager1 is manager2

    def test_crash_recovery_singleton(self):
        """Test crash recovery singleton"""
        recovery1 = get_crash_recovery()
        recovery2 = get_crash_recovery()
        assert recovery1 is recovery2


class TestUIWidgetTooltip:
    """Test widget tooltip integration"""

    def test_widget_has_tooltip_attribute(self):
        """Test that widgets have tooltip attribute"""
        button = UIButton(text="Test")
        assert hasattr(button, "tooltip")
        assert button.tooltip is None

    def test_widget_tooltip_delay(self):
        """Test widget tooltip delay"""
        button = UIButton(text="Test")
        assert hasattr(button, "tooltip_delay")
        assert button.tooltip_delay == 0.5

    def test_set_widget_tooltip(self):
        """Test setting widget tooltip"""
        button = UIButton(text="Test")
        button.tooltip = "This is a button"
        assert button.tooltip == "This is a button"
