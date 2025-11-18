"""
Exploration UI

UI components for tile-based exploration, dialogue, and interactions.
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

import pygame

from ui.ui_system import UIWidget


@dataclass
class DialogueLine:
    """A single line of dialogue"""

    speaker: str
    text: str
    portrait: Optional[str] = None  # Portrait image path


class DialogueBox(UIWidget):
    """
    Dialogue box for NPC conversations.

    Features:
    - Speaker name display
    - Text with word wrapping
    - Portrait display
    - Continue indicator
    - Auto-advance or manual advance
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)

        self.dialogue_lines: List[DialogueLine] = []
        self.current_line_index = 0
        self.is_active = False

        # Text display
        self.displayed_text = ""
        self.full_text = ""
        self.text_speed = 30  # Characters per second
        self.text_timer = 0.0
        self.is_text_complete = False

        # Style
        self.bg_color = (20, 20, 40, 230)
        self.border_color = (150, 150, 200)
        self.text_color = (255, 255, 255)
        self.speaker_color = (255, 200, 100)

        # Portrait
        self.portrait_surface: Optional[pygame.Surface] = None
        self.portrait_size = 80

        # Callbacks
        self.on_dialogue_complete: Optional[Callable] = None

        # AI approval state (optional, used when integrating with Loremaster)
        self.ai_approval_mode: bool = False
        # Callable that should call the Loremaster to (re)generate a line.
        # Signature: (guidance: Optional[str]) -> str
        self.ai_generate_callback: Optional[Callable[[Optional[str]], str]] = None
        # Optional callback invoked when a line is finally accepted.
        self.ai_on_accept: Optional[Callable[[str], None]] = None
        self.ai_guidance_text: str = ""
        self.ai_waiting_for_guidance: bool = False
        self.ai_last_line: str = ""

    def start_dialogue(self, lines: List[DialogueLine]):
        """Start a new dialogue sequence"""
        self.dialogue_lines = lines
        self.current_line_index = 0
        self.is_active = True
        self.visible = True
        self._load_current_line()

    def _load_current_line(self):
        """Load current dialogue line"""
        if self.current_line_index < len(self.dialogue_lines):
            line = self.dialogue_lines[self.current_line_index]
            self.full_text = line.text
            self.displayed_text = ""
            self.text_timer = 0.0
            self.is_text_complete = False

            # Load portrait if specified
            # TODO: Load portrait from assets
            self.portrait_surface = None
        else:
            self._end_dialogue()

    def _end_dialogue(self):
        """End dialogue sequence"""
        self.is_active = False
        self.visible = False
        if self.on_dialogue_complete:
            self.on_dialogue_complete()

    def advance(self):
        """Advance to next line or complete current text"""
        if not self.is_text_complete:
            # Show full text immediately
            self.displayed_text = self.full_text
            self.is_text_complete = True
        else:
            # In AI approval mode we never auto-advance past the proposed line;
            # the user must explicitly accept it.
            if self.ai_approval_mode:
                return

            # Move to next line
            self.current_line_index += 1
            self._load_current_line()

    # --- AI dialogue approval -------------------------------------------------

    def start_ai_approval(
        self,
        proposed_line: str,
        generate_callback: Callable[[Optional[str]], str],
        on_accept: Optional[Callable[[str], None]] = None,
    ):
        """
        Start an AI dialogue approval workflow for a single line.

        Args:
            proposed_line: Initial line proposed by the Loremaster.
            generate_callback: Callable that, when invoked with an optional
                guidance string, returns a new line from the Loremaster. This
                is where the actual Loremaster call should happen.
            on_accept: Optional callback invoked with the final accepted line.
        """
        self.ai_approval_mode = True
        self.ai_generate_callback = generate_callback
        self.ai_on_accept = on_accept
        self.ai_guidance_text = ""
        self.ai_waiting_for_guidance = False
        self.ai_last_line = proposed_line

        # Treat the proposed line as a single-line dialogue sequence
        self.is_active = True
        self.visible = True
        self.full_text = proposed_line
        self.displayed_text = ""
        self.text_timer = 0.0
        self.is_text_complete = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.visible or not self.is_active:
            return False

        # AI guidance text entry mode
        if self.ai_approval_mode and self.ai_waiting_for_guidance:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Submit guidance and request a new line
                    guidance = self.ai_guidance_text.strip() or None
                    if self.ai_generate_callback:
                        new_line = self.ai_generate_callback(guidance)
                        self.ai_last_line = new_line
                        self.full_text = new_line
                        self.displayed_text = ""
                        self.text_timer = 0.0
                        self.is_text_complete = False
                    self.ai_waiting_for_guidance = False
                    self.ai_guidance_text = ""
                    return True
                if event.key == pygame.K_ESCAPE:
                    # Cancel guidance entry
                    self.ai_waiting_for_guidance = False
                    self.ai_guidance_text = ""
                    return True
                if event.key == pygame.K_BACKSPACE:
                    self.ai_guidance_text = self.ai_guidance_text[:-1]
                    return True

                # Append printable characters
                if event.unicode and event.unicode.isprintable():
                    if len(self.ai_guidance_text) < 200:
                        self.ai_guidance_text += event.unicode
                    return True

            return False

        if event.type == pygame.KEYDOWN:
            if self.ai_approval_mode and self.is_text_complete:
                # Approval shortcuts in AI mode
                if event.key in (pygame.K_a, pygame.K_RETURN):
                    # Accept
                    self.ai_approval_mode = False
                    if self.ai_on_accept:
                        self.ai_on_accept(self.ai_last_line)
                    self._end_dialogue()
                    return True
                if event.key == pygame.K_r:
                    # Rewrite using a generic rewrite hint
                    if self.ai_generate_callback:
                        new_line = self.ai_generate_callback("Please rewrite this line.")
                        self.ai_last_line = new_line
                        self.full_text = new_line
                        self.displayed_text = ""
                        self.text_timer = 0.0
                        self.is_text_complete = False
                    return True
                if event.key == pygame.K_g:
                    # Enter guidance mode
                    self.ai_waiting_for_guidance = True
                    self.ai_guidance_text = ""
                    return True
            else:
                # Normal dialogue advance
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self.advance()
                    return True

        # Mouse click support for AI approval buttons
        if (
            self.ai_approval_mode
            and self.is_text_complete
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            mouse_x, mouse_y = event.pos

            button_width = 100
            button_height = 36
            spacing = 15
            base_y = self.y + self.height - button_height - 15

            accept_rect = pygame.Rect(self.x + 20, base_y, button_width, button_height)
            rewrite_rect = pygame.Rect(
                self.x + 20 + button_width + spacing, base_y, button_width, button_height
            )
            guide_rect = pygame.Rect(
                self.x + 20 + 2 * (button_width + spacing), base_y, button_width, button_height
            )

            if accept_rect.collidepoint(mouse_x, mouse_y):
                self.ai_approval_mode = False
                if self.ai_on_accept:
                    self.ai_on_accept(self.ai_last_line)
                self._end_dialogue()
                return True
            if rewrite_rect.collidepoint(mouse_x, mouse_y):
                if self.ai_generate_callback:
                    new_line = self.ai_generate_callback("Please rewrite this line.")
                    self.ai_last_line = new_line
                    self.full_text = new_line
                    self.displayed_text = ""
                    self.text_timer = 0.0
                    self.is_text_complete = False
                return True
            if guide_rect.collidepoint(mouse_x, mouse_y):
                self.ai_waiting_for_guidance = True
                self.ai_guidance_text = ""
                return True

        return False

    def update(self, delta_time: float):
        """Update dialogue box"""
        if not self.is_active or self.is_text_complete:
            return

        # Animate text display
        self.text_timer += delta_time
        chars_to_show = int(self.text_timer * self.text_speed)
        self.displayed_text = self.full_text[:chars_to_show]

        if len(self.displayed_text) >= len(self.full_text):
            self.displayed_text = self.full_text
            self.is_text_complete = True

    def render(self, screen: pygame.Surface):
        """Render dialogue box"""
        if not self.visible:
            return

        # Draw background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (self.x, self.y))

        # Draw border
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.border_color, border_rect, 3)

        # Draw portrait (if available)
        portrait_x = self.x + 10
        if self.portrait_surface:
            portrait_rect = self.portrait_surface.get_rect(topleft=(portrait_x, self.y + 10))
            screen.blit(self.portrait_surface, portrait_rect)
            text_x = portrait_x + self.portrait_size + 20
        else:
            text_x = portrait_x + 10

        # Draw speaker name
        if self.dialogue_lines and self.current_line_index < len(self.dialogue_lines):
            speaker_font = pygame.font.Font(None, 24)
            speaker = self.dialogue_lines[self.current_line_index].speaker
            speaker_surface = speaker_font.render(speaker, True, self.speaker_color)
            screen.blit(speaker_surface, (text_x, self.y + 15))

            # Draw dialogue text with word wrapping
            text_font = pygame.font.Font(None, 22)
            text_y = self.y + 45
            text_width = self.width - (text_x - self.x) - 20

            self._render_wrapped_text(
                screen,
                self.displayed_text,
                text_font,
                self.text_color,
                text_x,
                text_y,
                text_width,
            )

        # Draw continue indicator
        if self.is_text_complete:
            indicator_text = "▼"
            indicator_font = pygame.font.Font(None, 28)
            indicator_surface = indicator_font.render(indicator_text, True, self.text_color)
            indicator_rect = indicator_surface.get_rect(
                bottomright=(self.x + self.width - 20, self.y + self.height - 10)
            )
            screen.blit(indicator_surface, indicator_rect)

    def _render_wrapped_text(
        self,
        screen: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple,
        x: int,
        y: int,
        max_width: int,
    ):
        """Render text with word wrapping"""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = font.render(test_line, True, color)

            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        # Render lines
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (x, y + i * line_height))


class InteractionPrompt(UIWidget):
    """
    Interaction prompt that appears when player can interact with something.

    Shows "Press E to Talk", "Press E to Open", etc.
    """

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 200, 40)
        self.prompt_text = ""

        # Style
        self.bg_color = (0, 0, 0, 180)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)

        # Animation
        self.pulse_timer = 0.0
        self.pulse_speed = 2.0

    def show_prompt(self, prompt_text: str):
        """Show interaction prompt"""
        self.prompt_text = prompt_text
        self.visible = True
        self.pulse_timer = 0.0

    def hide_prompt(self):
        """Hide interaction prompt"""
        self.visible = False
        self.prompt_text = ""

    def update(self, delta_time: float):
        """Update prompt animation"""
        self.pulse_timer += delta_time * self.pulse_speed

    def render(self, screen: pygame.Surface):
        """Render interaction prompt"""
        if not self.visible or not self.prompt_text:
            return

        # Create pulsing effect
        pulse_alpha = int(
            180 + 75 * abs(pygame.math.Vector2(1, 0).rotate(self.pulse_timer * 180).x)
        )

        # Draw background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_color = (*self.bg_color[:3], pulse_alpha)
        bg_surface.fill(bg_color)
        screen.blit(bg_surface, (self.x, self.y))

        # Draw border
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.border_color, border_rect, 2)

        # Draw text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.prompt_text, True, self.text_color)
        text_rect = text_surface.get_rect(
            center=(self.x + self.width // 2, self.y + self.height // 2)
        )
        screen.blit(text_surface, text_rect)


class ExplorationHUD(UIWidget):
    """
    HUD for exploration mode showing party status, location, etc.
    """

    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(0, 0, screen_width, screen_height)

        # Components
        self.dialogue_box = DialogueBox(50, screen_height - 180, screen_width - 100, 150)

        self.interaction_prompt = InteractionPrompt(
            screen_width // 2 - 100, screen_height // 2 + 50
        )

        # Location name display
        self.location_name = ""
        self.location_timer = 0.0
        self.location_duration = 3.0

        # Mini party status (top left corner)
        self.show_party_status = True

    def show_location(self, location_name: str, duration: float = 3.0):
        """Show location name"""
        self.location_name = location_name
        self.location_timer = duration
        self.location_duration = duration

    def start_dialogue(self, lines: List[DialogueLine]):
        """Start dialogue"""
        self.dialogue_box.start_dialogue(lines)

    def show_interaction_prompt(self, prompt_text: str):
        """Show interaction prompt"""
        self.interaction_prompt.show_prompt(prompt_text)

    def hide_interaction_prompt(self):
        """Hide interaction prompt"""
        self.interaction_prompt.hide_prompt()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events"""
        # Dialogue box gets priority
        if self.dialogue_box.visible:
            return self.dialogue_box.handle_event(event)

        return False

    def update(self, delta_time: float):
        """Update HUD"""
        self.dialogue_box.update(delta_time)
        self.interaction_prompt.update(delta_time)

        # Update location display timer
        if self.location_timer > 0:
            self.location_timer -= delta_time

    def render(self, screen: pygame.Surface):
        """Render exploration HUD"""
        # Render location name
        if self.location_timer > 0:
            font = pygame.font.Font(None, 48)
            location_surface = font.render(self.location_name, True, (255, 255, 255))

            # Fade effect
            alpha = int(255 * min(self.location_timer / self.location_duration, 1.0))
            location_surface.set_alpha(alpha)

            location_rect = location_surface.get_rect(center=(self.width // 2, 100))
            screen.blit(location_surface, location_rect)

        # Render interaction prompt
        self.interaction_prompt.render(screen)

        # Render dialogue box
        self.dialogue_box.render(screen)

        # TODO: Render mini party status (HP/MP bars for party members)
