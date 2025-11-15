"""
AI Assistant Panel

Persistent AI chat interface with screen awareness and context-aware suggestions.
The AI can see what's on screen and provide intelligent assistance.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pygame

from ..core.ecs import World
from ..rendering.tilemap import Tilemap
from .ai_vision_context import AIVisionContext, get_vision_exporter
from .workspace_system import get_workspace_manager


class AIAssistantPanel:
    """
    Persistent AI assistant with chat interface.

    Features:
    - Screen-aware AI (knows what's on the map)
    - Context-aware suggestions based on workspace
    - Natural language level editing
    - Asset inspection and modification
    - Proactive help based on user actions
    """

    def __init__(self, screen: pygame.Surface, world: World):
        """
        Initialize AI assistant panel.

        Args:
            screen: Pygame surface to render to
            world: ECS world reference
        """
        self.screen = screen
        self.world = world
        self.visible = False
        self.collapsed = False

        # AI state
        self.workspace_manager = get_workspace_manager()
        self.vision_exporter = get_vision_exporter()
        self.last_workspace = None
        self.vision_context: Optional[AIVisionContext] = None

        # Chat history
        self.chat_history: List[Tuple[str, str, str]] = []  # (sender, message, timestamp)
        self.current_input = ""
        self.input_active = False

        # UI layout
        self.panel_width = 400
        self.panel_collapsed_width = 50
        self.panel_height = 600
        self.panel_x = 0  # Will be set in render (right side)
        self.panel_y = 150  # Below workspace toolbar

        # Colors
        self.bg_color = (30, 30, 40, 240)
        self.header_color = (40, 40, 55)
        self.ai_message_color = (45, 55, 75)
        self.user_message_color = (55, 45, 65)
        self.input_bg_color = (50, 50, 65)
        self.text_color = (220, 220, 220)
        self.ai_name_color = (100, 200, 255)
        self.user_name_color = (255, 200, 100)

        # Fonts
        try:
            self.header_font = pygame.font.Font(None, 24)
            self.message_font = pygame.font.Font(None, 18)
            self.input_font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 14)
        except:
            self.header_font = pygame.font.SysFont("Arial", 24)
            self.message_font = pygame.font.SysFont("Arial", 18)
            self.input_font = pygame.font.SysFont("Arial", 20)
            self.small_font = pygame.font.SysFont("Arial", 14)

        # Scroll state
        self.scroll_offset = 0
        self.max_visible_messages = 10

        # Suggestions
        self.current_suggestions: List[str] = []

    def toggle(self):
        """Toggle panel visibility"""
        self.visible = not self.visible
        if self.visible:
            self._on_panel_opened()

    def toggle_collapse(self):
        """Toggle collapsed state"""
        self.collapsed = not self.collapsed

    def update(self, dt: float, tilemap: Optional[Tilemap], camera_offset: Tuple[int, int]):
        """
        Update AI assistant.

        Args:
            dt: Delta time
            tilemap: Current tilemap
            camera_offset: Camera position
        """
        if not self.visible:
            return

        # Check for workspace changes
        current_workspace = self.workspace_manager.get_current_workspace()
        if current_workspace and current_workspace != self.last_workspace:
            self._on_workspace_changed(current_workspace.name)
            self.last_workspace = current_workspace

        # Update vision context periodically
        if tilemap:
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            tile_size = 32  # TODO: Get from renderer

            # Calculate visible area
            min_x = max(0, camera_offset[0] // tile_size)
            min_y = max(0, camera_offset[1] // tile_size)
            max_x = min(tilemap.width - 1, (camera_offset[0] + screen_width) // tile_size)
            max_y = min(tilemap.height - 1, (camera_offset[1] + screen_height) // tile_size)

            visible_area = (min_x, min_y, max_x, max_y)

            # Export vision context
            self.vision_context = self.vision_exporter.export_vision(
                world=self.world,
                tilemap=tilemap,
                camera_offset=camera_offset,
                visible_area=visible_area,
                workspace=current_workspace.type.value if current_workspace else "unknown",
            )

    def render(self):
        """Render AI assistant panel"""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        self.panel_x = screen_width - (
            self.panel_collapsed_width if self.collapsed else self.panel_width
        )

        # Panel background
        panel_width = self.panel_collapsed_width if self.collapsed else self.panel_width
        panel_surface = pygame.Surface((panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        self.screen.blit(panel_surface, (self.panel_x, self.panel_y))

        if self.collapsed:
            self._render_collapsed()
        else:
            self._render_expanded()

    def _render_collapsed(self):
        """Render collapsed panel (just icon)"""
        # AI icon
        icon_text = self.header_font.render("🤖", True, self.text_color)
        icon_x = self.panel_x + (self.panel_collapsed_width - icon_text.get_width()) // 2
        self.screen.blit(icon_text, (icon_x, self.panel_y + 10))

        # Collapse button
        collapse_text = self.small_font.render("◄", True, self.text_color)
        collapse_x = self.panel_x + (self.panel_collapsed_width - collapse_text.get_width()) // 2
        self.screen.blit(collapse_text, (collapse_x, self.panel_y + 50))

    def _render_expanded(self):
        """Render expanded panel with chat"""
        # Header
        header_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, 40)
        pygame.draw.rect(self.screen, self.header_color, header_rect)

        header_text = self.header_font.render("🤖 AI Assistant", True, self.ai_name_color)
        self.screen.blit(header_text, (self.panel_x + 10, self.panel_y + 8))

        # Collapse button
        collapse_text = self.small_font.render("►", True, self.text_color)
        self.screen.blit(
            collapse_text, (self.panel_x + self.panel_width - 25, self.panel_y + 12)
        )

        # Chat area
        chat_y = self.panel_y + 45
        chat_height = self.panel_height - 145

        self._render_chat_messages(chat_y, chat_height)

        # Suggestions area
        suggestions_y = chat_y + chat_height + 5
        self._render_suggestions(suggestions_y)

        # Input area
        input_y = self.panel_y + self.panel_height - 50
        self._render_input(input_y)

    def _render_chat_messages(self, y: int, height: int):
        """Render chat message history"""
        message_y = y + 5
        visible_messages = self.chat_history[-self.max_visible_messages :]

        for sender, message, timestamp in visible_messages:
            is_ai = sender == "AI"

            # Message background
            bg_color = self.ai_message_color if is_ai else self.user_message_color
            message_height = self._calculate_message_height(message)

            if message_y + message_height > y + height:
                break  # Out of space

            message_rect = pygame.Rect(
                self.panel_x + 5, message_y, self.panel_width - 10, message_height
            )
            pygame.draw.rect(self.screen, bg_color, message_rect, border_radius=5)

            # Sender name
            name_color = self.ai_name_color if is_ai else self.user_name_color
            name_text = self.small_font.render(sender, True, name_color)
            self.screen.blit(name_text, (self.panel_x + 10, message_y + 3))

            # Message text (word-wrapped)
            self._render_wrapped_text(
                message, self.panel_x + 10, message_y + 20, self.panel_width - 20
            )

            message_y += message_height + 5

    def _render_suggestions(self, y: int):
        """Render AI suggestions"""
        if not self.current_suggestions:
            return

        suggestion_text = self.small_font.render(
            "Suggestions:", True, (150, 150, 150)
        )
        self.screen.blit(suggestion_text, (self.panel_x + 10, y))

        for i, suggestion in enumerate(self.current_suggestions[:3]):
            sug_y = y + 18 + i * 20
            sug_text = self.small_font.render(f"• {suggestion}", True, (180, 180, 180))
            self.screen.blit(sug_text, (self.panel_x + 15, sug_y))

    def _render_input(self, y: int):
        """Render input field"""
        input_rect = pygame.Rect(self.panel_x + 5, y, self.panel_width - 10, 40)
        border_color = (100, 150, 200) if self.input_active else (80, 80, 100)
        pygame.draw.rect(self.screen, self.input_bg_color, input_rect, border_radius=3)
        pygame.draw.rect(self.screen, border_color, input_rect, 2, border_radius=3)

        # Input text
        if self.current_input:
            input_text = self.input_font.render(self.current_input, True, self.text_color)
            self.screen.blit(input_text, (self.panel_x + 10, y + 10))
        elif self.input_active:
            placeholder = self.input_font.render(
                "Ask AI anything...", True, (100, 100, 100)
            )
            self.screen.blit(placeholder, (self.panel_x + 10, y + 10))

    def _render_wrapped_text(self, text: str, x: int, y: int, max_width: int):
        """Render word-wrapped text"""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_surface = self.message_font.render(test_line, True, self.text_color)

            if text_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            line_surface = self.message_font.render(line, True, self.text_color)
            self.screen.blit(line_surface, (x, y + i * 20))

    def _calculate_message_height(self, message: str) -> int:
        """Calculate height needed for message"""
        words = message.split(" ")
        lines = 1
        current_line = ""
        max_width = self.panel_width - 20

        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_surface = self.message_font.render(test_line, True, self.text_color)

            if text_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines += 1
                current_line = word

        return 25 + lines * 20  # Header + lines

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self._send_message()
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.current_input = self.current_input[:-1]
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                    return True

        elif event.type == pygame.TEXTINPUT:
            if self.input_active:
                self.current_input += event.text
                return True

        return False

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click"""
        mx, my = mouse_pos

        # Check collapse button
        if self.collapsed:
            if self.panel_x <= mx <= self.panel_x + self.panel_collapsed_width:
                if self.panel_y + 40 <= my <= self.panel_y + 70:
                    self.toggle_collapse()
                    return True
        else:
            # Collapse button
            if self.panel_x + self.panel_width - 30 <= mx <= self.panel_x + self.panel_width:
                if self.panel_y + 5 <= my <= self.panel_y + 35:
                    self.toggle_collapse()
                    return True

            # Input field
            input_y = self.panel_y + self.panel_height - 50
            if (
                self.panel_x + 5 <= mx <= self.panel_x + self.panel_width - 5
                and input_y <= my <= input_y + 40
            ):
                self.input_active = True
                return True

        return False

    def _send_message(self):
        """Send user message and get AI response"""
        if not self.current_input.strip():
            return

        user_message = self.current_input.strip()
        self.current_input = ""

        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_history.append(("User", user_message, timestamp))

        # Generate AI response
        ai_response = self._generate_ai_response(user_message)
        self.chat_history.append(("AI", ai_response, timestamp))

    def _generate_ai_response(self, user_message: str) -> str:
        """
        Generate AI response based on user message and context.

        This is where the magic happens - AI uses vision context to understand
        what's on screen and provide intelligent responses.
        """
        # Parse command intent
        message_lower = user_message.lower()

        # Screen-aware commands
        if "in the middle" in message_lower or "center" in message_lower:
            if self.vision_context:
                center = self.vision_context.spatial.center_point
                return f"I can see the center of your screen is at ({center[0]}, {center[1]}). I'll place objects there!"

        if "what do you see" in message_lower or "what's on screen" in message_lower:
            return self._describe_screen()

        if "make" in message_lower and ("town" in message_lower or "village" in message_lower):
            return "I'll generate a town for you! Generating houses, shops, NPCs, and roads..."

        if "market" in message_lower and "middle" in message_lower:
            if self.vision_context:
                center = self.vision_context.spatial.center_point
                return f"Creating a market at the center ({center[0]}, {center[1]}) of your town! Adding merchant stalls, NPCs, and goods..."

        if "bigger" in message_lower or "larger" in message_lower:
            return "I'll scale up the selected entity. Use Ctrl+Click to select an entity first!"

        if "smaller" in message_lower:
            return "I'll scale down the selected entity. Use Ctrl+Click to select an entity first!"

        if "color" in message_lower:
            return "I can change entity colors! Select an entity and tell me what color you want (e.g., 'change roof to red')."

        # General help
        if "help" in message_lower or "what can you do" in message_lower:
            return """I can help you build levels! Try commands like:
• "Make a town in the middle"
• "Create a market here"
• "What do you see on screen?"
• "Make this building bigger"
• "Change the roof color to red"

I can see what's on your map and understand spatial relationships!"""

        # Default response
        return f"I understand you want: '{user_message}'. This feature is coming soon! Try 'help' to see what I can do now."

    def _describe_screen(self) -> str:
        """Describe what AI sees on screen"""
        if not self.vision_context:
            return "I can't see the screen yet. Try moving around the map first!"

        entities = self.vision_context.entities
        spatial = self.vision_context.spatial

        description = f"I can see {len(entities)} entities on screen. "

        if spatial.entity_clusters:
            description += f"I found {len(spatial.entity_clusters)} clusters of entities. "

        if spatial.empty_regions:
            description += f"I see {len(spatial.empty_regions)} empty areas where you could place more objects. "

        if spatial.density_map:
            top_types = sorted(spatial.density_map.items(), key=lambda x: x[1], reverse=True)[:3]
            types_str = ", ".join([f"{count} {type}" for type, count in top_types])
            description += f"Most common types: {types_str}."

        return description

    def _on_panel_opened(self):
        """Called when panel is opened"""
        # Add welcome message
        if not self.chat_history:
            self.chat_history.append(
                ("AI", "Hello! I'm your AI assistant. I can help you build levels, place objects, and edit your map. Try asking 'what can you do?'", "Now")
            )

    def _on_workspace_changed(self, workspace_name: str):
        """Called when workspace changes"""
        timestamp = datetime.now().strftime("%H:%M")

        # Workspace-specific greetings
        if "level" in workspace_name.lower():
            self.chat_history.append(
                ("AI", "I see you're in the Level Editor! I can help you build maps, place entities, and generate content. Try 'make a town' or 'what can you do?'", timestamp)
            )
            self.current_suggestions = [
                "Generate a town",
                "Create terrain",
                "Place entities",
            ]

        elif "content" in workspace_name.lower():
            self.chat_history.append(
                ("AI", "Welcome to Content Creation! I can help you create sprites, animations, and assets.", timestamp)
            )
            self.current_suggestions = [
                "Create a sprite",
                "Generate animation",
                "Browse assets",
            ]
