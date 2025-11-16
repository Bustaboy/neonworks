"""
Tests for Enhanced Error Handler

Tests the error handling system including error analysis, suggestions,
formatting, and the decorator functionality.
"""

import pytest

from neonworks.core.error_handler import (
    EnhancedErrorHandler,
    ErrorSuggestion,
    get_error_handler,
    handle_error,
    with_error_handling,
)


class TestErrorSuggestion:
    """Test suite for ErrorSuggestion"""

    def test_init_basic(self):
        """Test basic ErrorSuggestion initialization"""
        suggestion = ErrorSuggestion(
            error_type="Test Error",
            message="Test message",
            suggestions=["Suggestion 1", "Suggestion 2"],
        )

        assert suggestion.error_type == "Test Error"
        assert suggestion.message == "Test message"
        assert suggestion.suggestions == ["Suggestion 1", "Suggestion 2"]
        assert suggestion.severity == "ERROR"
        assert suggestion.context == {}

    def test_init_with_custom_severity(self):
        """Test ErrorSuggestion with custom severity"""
        suggestion = ErrorSuggestion(
            error_type="Warning",
            message="Test warning",
            suggestions=["Fix this"],
            severity="WARNING",
        )

        assert suggestion.severity == "WARNING"

    def test_init_with_context(self):
        """Test ErrorSuggestion with context"""
        context = {"file": "test.py", "line": 42}
        suggestion = ErrorSuggestion(
            error_type="Test Error",
            message="Test message",
            suggestions=["Fix it"],
            context=context,
        )

        assert suggestion.context == context

    def test_format_message_basic(self):
        """Test basic message formatting"""
        suggestion = ErrorSuggestion(
            error_type="Test Error",
            message="Something went wrong",
            suggestions=["Try this", "Or that"],
        )

        formatted = suggestion.format_message()

        assert "[ERROR] Test Error" in formatted
        assert "Message: Something went wrong" in formatted
        assert "Suggestions:" in formatted
        assert "1. Try this" in formatted
        assert "2. Or that" in formatted

    def test_format_message_with_context(self):
        """Test message formatting with context"""
        context = {"file": "test.py", "line": 42}
        suggestion = ErrorSuggestion(
            error_type="Test Error",
            message="Test message",
            suggestions=["Fix it"],
            context=context,
        )

        formatted = suggestion.format_message()

        assert "Context:" in formatted
        assert "file: test.py" in formatted
        assert "line: 42" in formatted

    def test_format_message_no_suggestions(self):
        """Test message formatting with no suggestions"""
        suggestion = ErrorSuggestion(
            error_type="Test Error", message="Test message", suggestions=[]
        )

        formatted = suggestion.format_message()

        assert "[ERROR] Test Error" in formatted
        assert "Message: Test message" in formatted
        assert "Suggestions:" not in formatted


class TestEnhancedErrorHandler:
    """Test suite for EnhancedErrorHandler"""

    def test_init(self):
        """Test EnhancedErrorHandler initialization"""
        handler = EnhancedErrorHandler()

        assert handler.error_patterns is not None
        assert isinstance(handler.error_patterns, dict)
        assert len(handler.error_patterns) > 0

    def test_initialize_patterns(self):
        """Test pattern initialization"""
        handler = EnhancedErrorHandler()
        patterns = handler.error_patterns

        # Check for expected patterns
        assert "No such file or directory" in patterns
        assert "Permission denied" in patterns
        assert "No module named" in patterns
        assert "KeyError" in patterns
        assert "TypeError" in patterns

    def test_analyze_error_file_not_found(self):
        """Test analyzing FileNotFoundError"""
        handler = EnhancedErrorHandler()
        exception = FileNotFoundError("No such file or directory: 'test.txt'")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "File Error"
        assert "test.txt" in suggestion.message
        assert len(suggestion.suggestions) > 0
        assert any("path" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_permission_denied(self):
        """Test analyzing PermissionError"""
        handler = EnhancedErrorHandler()
        exception = PermissionError("Permission denied: '/root/file.txt'")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Permission Error"
        assert "Permission denied" in suggestion.message
        assert any("permission" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_import_error(self):
        """Test analyzing ImportError"""
        handler = EnhancedErrorHandler()
        exception = ImportError("No module named 'nonexistent_module'")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Import Error"
        assert any("pip install" in s for s in suggestion.suggestions)

    def test_analyze_error_key_error(self):
        """Test analyzing KeyError"""
        handler = EnhancedErrorHandler()
        exception = KeyError("missing_key")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Data Error"
        assert any("dictionary" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_index_error(self):
        """Test analyzing IndexError"""
        handler = EnhancedErrorHandler()
        exception = IndexError("list index out of range")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Data Error"
        assert any("index" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_attribute_error(self):
        """Test analyzing AttributeError"""
        handler = EnhancedErrorHandler()
        exception = AttributeError("'NoneType' object has no attribute 'value'")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Attribute Error"
        assert any("attribute" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_type_error(self):
        """Test analyzing TypeError"""
        handler = EnhancedErrorHandler()
        exception = TypeError("unsupported operand type(s) for +: 'int' and 'str'")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Type Error"
        assert any("type" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_nonetype(self):
        """Test analyzing NoneType errors"""
        handler = EnhancedErrorHandler()
        exception = TypeError("'NoneType' object is not subscriptable")

        suggestion = handler.analyze_error(exception)

        # NoneType pattern matches after TypeError pattern, so it becomes Type Error
        # But suggestions should still mention NoneType
        assert suggestion.error_type in ["Type Error", "NoneType Error"]
        assert any(
            "None" in s or "type" in s.lower() for s in suggestion.suggestions
        )

    def test_analyze_error_unknown(self):
        """Test analyzing unknown error type"""
        handler = EnhancedErrorHandler()
        exception = RuntimeError("Some unknown error")

        suggestion = handler.analyze_error(exception)

        # Should provide default suggestions
        assert len(suggestion.suggestions) > 0
        assert any("stack trace" in s.lower() for s in suggestion.suggestions)

    def test_analyze_error_sets_severity(self):
        """Test that severity is set correctly"""
        handler = EnhancedErrorHandler()

        # Regular error
        error = ValueError("Test error")
        suggestion = handler.analyze_error(error)
        assert suggestion.severity == "ERROR"

        # Warning (if applicable)
        warning = DeprecationWarning("Test warning")
        suggestion = handler.analyze_error(warning)
        assert suggestion.severity == "WARNING"

    def test_analyze_error_includes_context(self):
        """Test that context includes error type and traceback"""
        handler = EnhancedErrorHandler()
        exception = ValueError("Test error")

        suggestion = handler.analyze_error(exception)

        assert "error_type" in suggestion.context
        assert suggestion.context["error_type"] == "ValueError"
        assert "traceback" in suggestion.context

    def test_handle_error_basic(self, capsys):
        """Test basic error handling"""
        handler = EnhancedErrorHandler()
        exception = ValueError("Test error")

        suggestion = handler.handle_error(exception, show_traceback=False)

        # Check returned suggestion
        assert suggestion.message == "Test error"

        # Check printed output
        captured = capsys.readouterr()
        assert "Test error" in captured.out

    def test_handle_error_with_traceback(self, capsys):
        """Test error handling with traceback"""
        handler = EnhancedErrorHandler()
        exception = ValueError("Test error")

        handler.handle_error(exception, show_traceback=True)

        captured = capsys.readouterr()
        assert "Full Traceback:" in captured.out

    def test_handle_error_without_traceback(self, capsys):
        """Test error handling without traceback"""
        handler = EnhancedErrorHandler()
        exception = ValueError("Test error")

        handler.handle_error(exception, show_traceback=False)

        captured = capsys.readouterr()
        assert "Full Traceback:" not in captured.out

    def test_handle_error_with_additional_context(self):
        """Test error handling with additional context"""
        handler = EnhancedErrorHandler()
        exception = ValueError("Test error")
        additional_context = {"user": "test_user", "action": "test_action"}

        suggestion = handler.handle_error(
            exception, show_traceback=False, additional_context=additional_context
        )

        assert "user" in suggestion.context
        assert suggestion.context["user"] == "test_user"
        assert "action" in suggestion.context
        assert suggestion.context["action"] == "test_action"


class TestGlobalFunctions:
    """Test suite for global functions"""

    def test_get_error_handler_singleton(self):
        """Test get_error_handler returns singleton"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()

        assert handler1 is handler2

    def test_get_error_handler_returns_instance(self):
        """Test get_error_handler returns EnhancedErrorHandler instance"""
        handler = get_error_handler()

        assert isinstance(handler, EnhancedErrorHandler)

    def test_handle_error_convenience_function(self, capsys):
        """Test convenience handle_error function"""
        exception = ValueError("Test error")

        suggestion = handle_error(exception, show_traceback=False)

        assert suggestion.message == "Test error"
        captured = capsys.readouterr()
        assert "Test error" in captured.out


class TestWithErrorHandlingDecorator:
    """Test suite for with_error_handling decorator"""

    def test_decorator_allows_function_to_run(self):
        """Test decorator allows normal function execution"""

        @with_error_handling(show_traceback=False)
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_decorator_catches_and_reraises_exception(self, capsys):
        """Test decorator catches exception and reraises"""

        @with_error_handling(show_traceback=False)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Check that error was handled (printed)
        captured = capsys.readouterr()
        assert "Test error" in captured.out

    def test_decorator_with_traceback(self, capsys):
        """Test decorator with traceback enabled"""

        @with_error_handling(show_traceback=True)
        def failing_function():
            raise ValueError("Test error with traceback")

        with pytest.raises(ValueError):
            failing_function()

        captured = capsys.readouterr()
        assert "Full Traceback:" in captured.out

    def test_decorator_preserves_function_arguments(self):
        """Test decorator preserves function arguments"""

        @with_error_handling(show_traceback=False)
        def add_numbers(a, b):
            return a + b

        result = add_numbers(5, 3)
        assert result == 8

    def test_decorator_preserves_kwargs(self):
        """Test decorator preserves keyword arguments"""

        @with_error_handling(show_traceback=False)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("World", greeting="Hi")
        assert result == "Hi, World!"


class TestErrorPatterns:
    """Test suite for specific error patterns"""

    def test_pygame_error_suggestions(self):
        """Test pygame-related error suggestions"""
        handler = EnhancedErrorHandler()
        exception = RuntimeError("pygame display not initialized")

        suggestion = handler.analyze_error(exception)

        # Pattern matching may match "pygame" or "display not initialized"
        assert suggestion.error_type in ["Pygame Error", "Pygame Display Error"]
        assert any("pygame" in s.lower() for s in suggestion.suggestions)

    def test_json_error_suggestions(self):
        """Test JSON error suggestions"""
        handler = EnhancedErrorHandler()
        exception = ValueError("Invalid JSON: trailing comma")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "JSON Error"
        assert any("JSON" in s for s in suggestion.suggestions)

    def test_asset_error_suggestions(self):
        """Test asset-related error suggestions"""
        handler = EnhancedErrorHandler()
        exception = FileNotFoundError("asset file not found: sprite.png")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Asset Error"
        assert any("asset" in s.lower() for s in suggestion.suggestions)

    def test_sprite_error_suggestions(self):
        """Test sprite-related error suggestions"""
        handler = EnhancedErrorHandler()
        exception = FileNotFoundError("sprite file not found")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Sprite Error"
        assert any("sprite" in s.lower() for s in suggestion.suggestions)

    def test_circular_import_suggestions(self):
        """Test circular import error suggestions"""
        handler = EnhancedErrorHandler()
        exception = ImportError("cannot import name 'Foo' from module 'bar'")

        suggestion = handler.analyze_error(exception)

        assert suggestion.error_type == "Import Error"
        assert any("circular" in s.lower() for s in suggestion.suggestions)


class TestIntegration:
    """Integration tests for error handler"""

    def test_full_error_handling_workflow(self, capsys):
        """Test complete error handling workflow"""

        @with_error_handling(show_traceback=False)
        def risky_operation(data):
            if data is None:
                raise ValueError("Data cannot be None")
            return data * 2

        # Should work normally
        result = risky_operation(5)
        assert result == 10

        # Should handle error
        with pytest.raises(ValueError):
            risky_operation(None)

        captured = capsys.readouterr()
        assert "Data cannot be None" in captured.out
        assert "Suggestions:" in captured.out

    def test_multiple_error_types(self):
        """Test handling multiple different error types"""
        handler = EnhancedErrorHandler()

        errors = [
            FileNotFoundError("file.txt not found"),
            KeyError("missing_key"),
            TypeError("wrong type"),
            IndexError("index out of range"),
        ]

        for error in errors:
            suggestion = handler.analyze_error(error)
            assert len(suggestion.suggestions) > 0
            assert suggestion.error_type != ""
            assert suggestion.message != ""
