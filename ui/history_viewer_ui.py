"""
NeonWorks History Viewer UI - Command History Visualization

Provides a visual interface for viewing and navigating the undo/redo history.
"""

from typing import List, Optional, Tuple

import pygame

from ..core.undo_manager import UndoManager
from ..rendering.ui import UI


class HistoryViewerUI:
    """
    Visual command history viewer.

    Displays undo/redo history with timestamps, allows jumping to specific
    states, and shows memory usage statistics.
    """

    def __init__(self, screen: pygame.Surface, undo_manager: UndoManager):
        """
        Initialize history viewer.

        Args:
            screen: Pygame surface to render to
            undo_manager: UndoManager instance to visualize
        """
        self.screen = screen
        self.undo_manager = undo_manager
        self.ui = UI(screen)

        self.visible = False

        # UI positioning
        screen_width, screen_height = screen.get_size()
        self.panel_width = 500
        self.panel_height = 600
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2

        # Scrolling
        self.scroll_offset = 0
        self.max_visible_items = 20

        # Selection
        self.selected_index = -1

        # Statistics display
        self.show_stats = True

    def toggle(self):
        """Toggle history viewer visibility."""
        self.visible = not self.visible
        if self.visible:
            # Reset scroll to bottom (most recent)
            self.scroll_offset = 0

    def render(self):
        """Render the history viewer UI."""
        if not self.visible:
            return

        # Background panel
        self.ui.panel(
            self.panel_x, self.panel_y, self.panel_width, self.panel_height, (20, 20, 30, 240)
        )

        # Title
        self.ui.title("Undo History", self.panel_x + 180, self.panel_y + 10, size=24)

        # Close button
        if self.ui.button("X", self.panel_x + self.panel_width - 40, self.panel_y + 10, 30, 30):
            self.toggle()

        # Render statistics if enabled
        current_y = self.panel_y + 50
        if self.show_stats:
            current_y = self._render_statistics(current_y)
            current_y += 10

        # Render action buttons
        current_y = self._render_action_buttons(current_y)
        current_y += 10

        # Render history list
        self._render_history_list(current_y)

    def _render_statistics(self, start_y: int) -> int:
        """
        Render statistics panel.

        Args:
            start_y: Y coordinate to start rendering

        Returns:
            Y coordinate after rendering
        """
        stats = self.undo_manager.get_statistics()
        memory = self.undo_manager.get_memory_usage()

        stat_panel_height = 100
        self.ui.panel(
            self.panel_x + 10,
            start_y,
            self.panel_width - 20,
            stat_panel_height,
            (30, 30, 40, 200),
        )

        # Title
        self.ui.label("Statistics", self.panel_x + 20, start_y + 5, size=14, color=(200, 200, 255))

        # Stats in two columns
        col1_x = self.panel_x + 20
        col2_x = self.panel_x + 260
        stat_y = start_y + 25

        # Column 1
        self.ui.label(
            f"Total Commands: {stats['total_commands_executed']}", col1_x, stat_y, size=12
        )
        stat_y += 18
        self.ui.label(f"Total Undos: {stats['total_undos']}", col1_x, stat_y, size=12)
        stat_y += 18
        self.ui.label(f"Total Redos: {stats['total_redos']}", col1_x, stat_y, size=12)

        # Column 2
        stat_y = start_y + 25
        self.ui.label(f"Undo Stack: {stats['current_undo_count']}", col2_x, stat_y, size=12)
        stat_y += 18
        self.ui.label(f"Redo Stack: {stats['current_redo_count']}", col2_x, stat_y, size=12)
        stat_y += 18
        self.ui.label(
            f"Memory: {stats['memory_usage_kb']:.1f} KB",
            col2_x,
            stat_y,
            size=12,
            color=(100, 255, 100) if stats["memory_usage_kb"] < 1000 else (255, 200, 100),
        )

        return start_y + stat_panel_height

    def _render_action_buttons(self, start_y: int) -> int:
        """
        Render action buttons.

        Args:
            start_y: Y coordinate to start rendering

        Returns:
            Y coordinate after rendering
        """
        button_y = start_y
        button_height = 30
        button_width = 110

        # Undo button
        undo_enabled = self.undo_manager.can_undo()
        undo_color = (0, 150, 0) if undo_enabled else (50, 50, 50)
        undo_desc = self.undo_manager.get_undo_description() or "Nothing to undo"

        if self.ui.button(
            "Undo (Ctrl+Z)",
            self.panel_x + 10,
            button_y,
            button_width,
            button_height,
            color=undo_color,
        ):
            if undo_enabled:
                self.undo_manager.undo()

        # Show undo description
        if undo_enabled:
            self.ui.label(
                f"← {undo_desc[:30]}",
                self.panel_x + 125,
                button_y + 8,
                size=11,
                color=(150, 255, 150),
            )

        # Redo button
        redo_enabled = self.undo_manager.can_redo()
        redo_color = (0, 100, 150) if redo_enabled else (50, 50, 50)
        redo_desc = self.undo_manager.get_redo_description() or "Nothing to redo"

        if self.ui.button(
            "Redo (Ctrl+Y)",
            self.panel_x + 10,
            button_y + button_height + 5,
            button_width,
            button_height,
            color=redo_color,
        ):
            if redo_enabled:
                self.undo_manager.redo()

        # Show redo description
        if redo_enabled:
            self.ui.label(
                f"→ {redo_desc[:30]}",
                self.panel_x + 125,
                button_y + button_height + 13,
                size=11,
                color=(150, 200, 255),
            )

        # Clear history button
        if self.ui.button(
            "Clear All",
            self.panel_x + self.panel_width - 120,
            button_y,
            button_width,
            button_height,
            color=(150, 0, 0),
        ):
            if self._confirm_clear():
                self.undo_manager.clear()

        # Toggle stats button
        stats_text = "Hide Stats" if self.show_stats else "Show Stats"
        if self.ui.button(
            stats_text,
            self.panel_x + self.panel_width - 120,
            button_y + button_height + 5,
            button_width,
            button_height,
        ):
            self.show_stats = not self.show_stats

        return button_y + (button_height + 5) * 2

    def _render_history_list(self, start_y: int):
        """
        Render the scrollable history list.

        Args:
            start_y: Y coordinate to start rendering
        """
        list_y = start_y + 10
        list_height = self.panel_y + self.panel_height - list_y - 10
        list_x = self.panel_x + 10
        list_width = self.panel_width - 20

        # Background
        self.ui.panel(list_x, list_y, list_width, list_height, (15, 15, 20, 220))

        # Header
        self.ui.label(
            "History (newest first):", list_x + 5, list_y + 5, size=12, color=(200, 200, 200)
        )

        # Get history
        history = self.undo_manager.get_history(max_items=100)

        if not history:
            self.ui.label(
                "No history yet",
                list_x + list_width // 2 - 40,
                list_y + list_height // 2,
                size=14,
                color=(100, 100, 100),
            )
            return

        # Reverse to show newest first
        history = list(reversed(history))

        # Calculate visible range
        item_height = 25
        max_visible = int(list_height / item_height) - 2
        start_idx = self.scroll_offset
        end_idx = min(start_idx + max_visible, len(history))

        # Render visible items
        item_y = list_y + 30
        for i in range(start_idx, end_idx):
            description, timestamp, is_undo_stack = history[i]

            # Highlight current position (most recent undo)
            is_current = i == 0 and is_undo_stack
            bg_color = (40, 60, 40) if is_current else (25, 25, 30)

            # Draw item background
            item_rect = pygame.Rect(list_x + 5, item_y, list_width - 10, item_height - 2)
            pygame.draw.rect(self.screen, bg_color, item_rect, border_radius=3)

            # Draw border for current item
            if is_current:
                pygame.draw.rect(self.screen, (0, 255, 0), item_rect, width=2, border_radius=3)

            # Render timestamp
            self.ui.label(timestamp, list_x + 10, item_y + 4, size=10, color=(150, 150, 150))

            # Render description
            desc_text = description[:50] + "..." if len(description) > 50 else description
            desc_color = (200, 255, 200) if is_current else (200, 200, 200)
            self.ui.label(desc_text, list_x + 70, item_y + 4, size=11, color=desc_color)

            # Stack indicator
            stack_text = "●" if is_undo_stack else "○"
            stack_color = (100, 255, 100) if is_undo_stack else (100, 100, 100)
            self.ui.label(
                stack_text, list_x + list_width - 25, item_y + 4, size=14, color=stack_color
            )

            item_y += item_height

        # Scroll indicator
        if len(history) > max_visible:
            scroll_text = f"Showing {start_idx + 1}-{end_idx} of {len(history)}"
            self.ui.label(
                scroll_text,
                list_x + list_width - 150,
                list_y + 5,
                size=10,
                color=(150, 150, 150),
            )

    def _confirm_clear(self) -> bool:
        """
        Show confirmation dialog for clearing history.

        Returns:
            True if user confirms
        """
        # Simple confirmation (in a real implementation, show a proper dialog)
        return True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        # Handle scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, self.scroll_offset - event.y)
            return True

        # Handle keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
                return True

            # Check for Ctrl modifier
            ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL

            if ctrl_pressed:
                if event.key == pygame.K_z:
                    self.undo_manager.undo()
                    return True
                elif event.key == pygame.K_y:
                    self.undo_manager.redo()
                    return True

        return False

    def update(self, dt: float):
        """
        Update history viewer state.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

        # Update scroll limits based on history size
        history = self.undo_manager.get_history(max_items=100)
        max_scroll = max(0, len(history) - self.max_visible_items)
        self.scroll_offset = min(self.scroll_offset, max_scroll)
