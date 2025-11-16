"""
NeonWorks Shortcuts Overlay UI - Keyboard Shortcuts Help Display
Shows all available keyboard shortcuts organized by category.
Press ? (Shift+/) to toggle.
"""

from typing import Dict, List, Tuple

import pygame

from ..core.hotkey_manager import HotkeyContext, get_hotkey_manager
from ..rendering.ui import UI


class ShortcutsOverlayUI:
    """
    Visual overlay showing all keyboard shortcuts.

    Press ? (Shift+/) to toggle this overlay.
    Displays shortcuts organized by category with descriptions.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize shortcuts overlay.

        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.ui = UI(screen)
        self.visible = False
        self.hotkey_manager = get_hotkey_manager()

        # UI state
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 30

        # Categories to show (can be filtered)
        self.show_categories = None  # None = show all

        # Context filter
        self.context_filter: HotkeyContext = HotkeyContext.GLOBAL

    def toggle(self):
        """Toggle overlay visibility."""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0

    def show(self):
        """Show the overlay."""
        self.visible = True
        self.scroll_offset = 0

    def hide(self):
        """Hide the overlay."""
        self.visible = False

    def set_context_filter(self, context: HotkeyContext):
        """
        Set which context's shortcuts to show.

        Args:
            context: Context to filter by
        """
        self.context_filter = context

    def render(self):
        """Render the shortcuts overlay."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Semi-transparent dark overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Main panel
        panel_width = min(1000, screen_width - 100)
        panel_height = min(700, screen_height - 100)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (15, 15, 25))

        # Title
        title_y = panel_y + 15
        self.ui.title(
            "Keyboard Shortcuts",
            panel_x + panel_width // 2 - 150,
            title_y,
            size=32,
            color=(100, 200, 255),
        )

        # Close button
        close_x = panel_x + panel_width - 60
        close_y = panel_y + 15
        if self.ui.button("X", close_x, close_y, 40, 40, color=(150, 0, 0)):
            self.hide()

        # Context selector
        self._render_context_selector(panel_x, title_y + 50, panel_width)

        # Shortcuts content (scrollable)
        content_y = title_y + 110
        content_height = panel_height - 130
        self._render_shortcuts_content(panel_x, content_y, panel_width, content_height)

        # Scroll indicator
        if self.max_scroll > 0:
            self._render_scroll_indicator(panel_x + panel_width - 20, content_y, 10, content_height)

        # Footer help text
        footer_y = panel_y + panel_height - 30
        self.ui.label(
            "Press ? to hide | Use mouse wheel to scroll",
            panel_x + 20,
            footer_y,
            size=14,
            color=(150, 150, 150),
        )

    def _render_context_selector(self, x: int, y: int, width: int):
        """Render context selection buttons."""
        contexts = [
            (HotkeyContext.GLOBAL, "All"),
            (HotkeyContext.GAME, "Game"),
            (HotkeyContext.EDITOR, "Editor"),
            (HotkeyContext.COMBAT, "Combat"),
            (HotkeyContext.BUILDING, "Building"),
        ]

        button_width = 120
        button_spacing = 10
        total_width = len(contexts) * (button_width + button_spacing) - button_spacing
        start_x = x + (width - total_width) // 2

        for i, (context, label) in enumerate(contexts):
            button_x = start_x + i * (button_width + button_spacing)
            is_active = self.context_filter == context
            button_color = (50, 100, 200) if is_active else (30, 30, 50)

            if self.ui.button(label, button_x, y, button_width, 35, color=button_color):
                self.context_filter = context
                self.scroll_offset = 0

    def _render_shortcuts_content(self, x: int, y: int, width: int, height: int):
        """Render the scrollable shortcuts content."""
        # Create clipping rect for scrolling
        clip_rect = pygame.Rect(x + 10, y, width - 20, height)
        original_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        # Get shortcuts organized by category
        help_data = self._get_filtered_help_data()

        # Render categories and shortcuts
        current_y = y - self.scroll_offset
        column_width = (width - 40) // 2
        left_column_x = x + 20
        right_column_x = x + width // 2 + 10

        # Split categories into two columns
        categories = list(help_data.keys())
        mid_point = (len(categories) + 1) // 2

        # Render left column
        current_y = self._render_column(
            left_column_x, current_y, column_width, categories[:mid_point], help_data
        )

        # Render right column
        self._render_column(
            right_column_x,
            y - self.scroll_offset,
            column_width,
            categories[mid_point:],
            help_data,
        )

        # Calculate max scroll
        total_height = current_y - (y - self.scroll_offset)
        self.max_scroll = max(0, total_height - height + 20)

        # Restore clip
        self.screen.set_clip(original_clip)

    def _render_column(
        self,
        x: int,
        start_y: int,
        width: int,
        categories: List[str],
        help_data: Dict[str, List[Tuple[str, str]]],
    ) -> int:
        """
        Render a column of shortcuts.

        Args:
            x: X position
            start_y: Starting Y position
            width: Column width
            categories: Categories to render
            help_data: Help data dictionary

        Returns:
            Final Y position after rendering
        """
        current_y = start_y

        for category in categories:
            shortcuts = help_data[category]

            # Category header
            self.ui.label(category, x, current_y, size=18, color=(255, 200, 100))
            current_y += 25

            # Shortcuts in category
            for shortcut, description in shortcuts:
                # Shortcut key (left-aligned)
                self.ui.label(shortcut, x + 10, current_y, size=14, color=(150, 200, 255))

                # Description (right-aligned with wrap)
                desc_x = x + 150
                desc_width = width - 160

                # Simple word wrapping
                words = description.split()
                lines = []
                current_line = []

                for word in words:
                    test_line = " ".join(current_line + [word])
                    # Approximate width check (6 pixels per char)
                    if len(test_line) * 6 > desc_width:
                        if current_line:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)
                            current_line = []
                    else:
                        current_line.append(word)

                if current_line:
                    lines.append(" ".join(current_line))

                # Render wrapped lines
                for line in lines:
                    self.ui.label(line, desc_x, current_y, size=14, color=(200, 200, 200))
                    current_y += 18

            current_y += 15  # Spacing between categories

        return current_y

    def _get_filtered_help_data(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Get help data filtered by current context.

        Returns:
            Dictionary mapping category to list of (shortcut, description) tuples
        """
        help_data: Dict[str, List[Tuple[str, str]]] = {}

        # Get hotkeys for current context
        if self.context_filter == HotkeyContext.GLOBAL:
            hotkeys = self.hotkey_manager.hotkeys
        else:
            hotkeys = self.hotkey_manager.get_hotkeys_by_context(self.context_filter)

        # Organize by category
        for hotkey in hotkeys:
            if not hotkey.enabled:
                continue

            category = hotkey.category
            if self.show_categories and category not in self.show_categories:
                continue

            if category not in help_data:
                help_data[category] = []

            help_data[category].append((hotkey.get_display_name(), hotkey.description))

        # Sort shortcuts within each category
        for category in help_data:
            help_data[category].sort(key=lambda x: x[0])

        return help_data

    def _render_scroll_indicator(self, x: int, y: int, width: int, height: int):
        """Render scroll bar indicator."""
        if self.max_scroll <= 0:
            return

        # Background track
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height))

        # Scrollbar handle
        handle_height = max(20, height * height // (height + self.max_scroll))
        handle_y = y + (self.scroll_offset / self.max_scroll) * (height - handle_height)

        pygame.draw.rect(
            self.screen, (100, 100, 150), (x, int(handle_y), width, int(handle_height))
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.scroll_speed
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
            return True

        # Key presses
        if event.type == pygame.KEYDOWN:
            # Close on Escape or ?
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True

            # Check for ? key (Shift+/)
            mods = pygame.key.get_mods()
            if event.key == pygame.K_SLASH and (mods & pygame.KMOD_SHIFT):
                self.hide()
                return True

            # Arrow key scrolling
            if event.key == pygame.K_UP:
                self.scroll_offset -= self.scroll_speed
                self.scroll_offset = max(0, self.scroll_offset)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset += self.scroll_speed
                self.scroll_offset = min(self.scroll_offset, self.max_scroll)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset -= self.scroll_speed * 5
                self.scroll_offset = max(0, self.scroll_offset)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset += self.scroll_speed * 5
                self.scroll_offset = min(self.scroll_offset, self.max_scroll)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_END:
                self.scroll_offset = self.max_scroll
                return True

        return False

    def update(self, dt: float):
        """
        Update overlay state.

        Args:
            dt: Delta time in seconds
        """
        # Nothing to update currently
        pass
