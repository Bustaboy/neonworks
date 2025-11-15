"""
Enhanced Error Handler with Helpful Suggestions

Provides user-friendly error messages with actionable suggestions.
"""

import traceback
from typing import Dict, List, Optional, Tuple


class ErrorSuggestion:
    """Container for error information and suggestions"""

    def __init__(
        self,
        error_type: str,
        message: str,
        suggestions: List[str],
        severity: str = "ERROR",
        context: Optional[Dict] = None,
    ):
        self.error_type = error_type
        self.message = message
        self.suggestions = suggestions
        self.severity = severity  # ERROR, WARNING, INFO
        self.context = context or {}

    def format_message(self) -> str:
        """Format error message with suggestions"""
        lines = []

        # Severity and error type
        lines.append(f"\n[{self.severity}] {self.error_type}")

        # Error message
        lines.append(f"Message: {self.message}")

        # Suggestions
        if self.suggestions:
            lines.append("\nSuggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        # Context
        if self.context:
            lines.append("\nContext:")
            for key, value in self.context.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class EnhancedErrorHandler:
    """Handles errors with helpful suggestions"""

    def __init__(self):
        self.error_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, Tuple[List[str], str]]:
        """
        Initialize error patterns and suggestions.

        Returns:
            Dict mapping error patterns to (suggestions, category)
        """
        return {
            # File errors
            "No such file or directory": (
                [
                    "Check if the file path is correct",
                    "Verify the file exists in the expected location",
                    "Check file permissions",
                    "Use an absolute path instead of relative path",
                ],
                "File Error",
            ),
            "Permission denied": (
                [
                    "Check file/directory permissions",
                    "Try running with appropriate permissions",
                    "Verify you have write access to the directory",
                ],
                "Permission Error",
            ),
            # Import errors
            "No module named": (
                [
                    "Install the missing module: pip install <module-name>",
                    "Check if the module name is spelled correctly",
                    "Verify the module is in PYTHONPATH",
                    "Check if you're using the correct Python environment",
                ],
                "Import Error",
            ),
            "cannot import name": (
                [
                    "Check if the import name is spelled correctly",
                    "Verify the module contains the specified name",
                    "Check for circular imports",
                    "Ensure the module is up to date",
                ],
                "Import Error",
            ),
            # pygame errors
            "pygame": (
                [
                    "Initialize pygame: pygame.init()",
                    "Install pygame: pip install pygame",
                    "Check if pygame display is initialized",
                ],
                "Pygame Error",
            ),
            "display not initialized": (
                [
                    "Call pygame.init() before creating display",
                    "Create display surface: pygame.display.set_mode((width, height))",
                ],
                "Pygame Display Error",
            ),
            # Data errors
            "KeyError": (
                [
                    "Check if the key exists in the dictionary",
                    "Use dict.get(key, default) to avoid KeyError",
                    "Verify the data structure matches expectations",
                ],
                "Data Error",
            ),
            "IndexError": (
                [
                    "Check if the index is within list bounds",
                    "Verify the list is not empty before accessing",
                    "Use len(list) to check list size",
                ],
                "Data Error",
            ),
            "AttributeError": (
                [
                    "Check if the object has the expected attribute",
                    "Verify the object is initialized correctly",
                    "Check for None values before accessing attributes",
                ],
                "Attribute Error",
            ),
            # Type errors
            "TypeError": (
                [
                    "Check if you're passing the correct types to the function",
                    "Verify function arguments match the expected signature",
                    "Check if the object supports the operation",
                ],
                "Type Error",
            ),
            "NoneType": (
                [
                    "Check if the value is None before using it",
                    "Verify the function returned a value (not None)",
                    "Add None checks: if value is not None:",
                ],
                "NoneType Error",
            ),
            # JSON errors
            "JSON": (
                [
                    "Check if the JSON file is properly formatted",
                    "Verify the file contains valid JSON",
                    "Use a JSON validator to check the file",
                    "Check for trailing commas in JSON",
                ],
                "JSON Error",
            ),
            # Asset errors
            "asset": (
                [
                    "Check if the asset file exists in the assets directory",
                    "Verify the asset path is correct",
                    "Ensure the asset is in the correct format",
                ],
                "Asset Error",
            ),
            "sprite": (
                [
                    "Check if the sprite file exists",
                    "Verify the image format is supported (PNG, JPG, etc.)",
                    "Ensure the sprite is loaded before use",
                ],
                "Sprite Error",
            ),
        }

    def analyze_error(self, exception: Exception) -> ErrorSuggestion:
        """
        Analyze exception and provide helpful suggestions.

        Args:
            exception: Exception to analyze

        Returns:
            ErrorSuggestion with helpful information
        """
        error_message = str(exception)
        error_type = type(exception).__name__

        # Find matching pattern
        suggestions = []
        category = error_type

        for pattern, (pattern_suggestions, pattern_category) in self.error_patterns.items():
            if pattern.lower() in error_message.lower() or pattern.lower() in error_type.lower():
                suggestions.extend(pattern_suggestions)
                category = pattern_category
                break

        # Add default suggestions if none found
        if not suggestions:
            suggestions = [
                "Check the stack trace for more details",
                "Verify your input data is correct",
                "Try running in debug mode for more information",
            ]

        # Determine severity
        severity = "ERROR"
        if isinstance(exception, (Warning, DeprecationWarning)):
            severity = "WARNING"

        # Collect context
        context = {"error_type": error_type, "traceback": traceback.format_exc()}

        return ErrorSuggestion(
            error_type=category,
            message=error_message,
            suggestions=suggestions,
            severity=severity,
            context=context,
        )

    def handle_error(
        self,
        exception: Exception,
        show_traceback: bool = True,
        additional_context: Optional[Dict] = None,
    ) -> ErrorSuggestion:
        """
        Handle error and display helpful message.

        Args:
            exception: Exception to handle
            show_traceback: Whether to show full traceback
            additional_context: Additional context to include

        Returns:
            ErrorSuggestion
        """
        suggestion = self.analyze_error(exception)

        # Add additional context
        if additional_context:
            suggestion.context.update(additional_context)

        # Print formatted message
        print(suggestion.format_message())

        # Print traceback if requested
        if show_traceback:
            print("\nFull Traceback:")
            traceback.print_exc()

        return suggestion


# Singleton instance
_error_handler: Optional[EnhancedErrorHandler] = None


def get_error_handler() -> EnhancedErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = EnhancedErrorHandler()
    return _error_handler


def handle_error(exception: Exception, **kwargs) -> ErrorSuggestion:
    """
    Convenience function to handle errors.

    Args:
        exception: Exception to handle
        **kwargs: Additional arguments for handle_error

    Returns:
        ErrorSuggestion
    """
    return get_error_handler().handle_error(exception, **kwargs)


# Decorator for error handling
def with_error_handling(show_traceback: bool = True):
    """
    Decorator to add error handling to functions.

    Args:
        show_traceback: Whether to show full traceback

    Example:
        @with_error_handling()
        def my_function():
            # Function code
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, show_traceback=show_traceback)
                raise

        return wrapper

    return decorator
