"""
Magic Menu UI

Spell selection interface for JRPG battles and field use.
"""

import pygame
from typing import List, Optional, Callable, Dict
from dataclasses import dataclass
from ui.ui_system import UIWidget


@dataclass
class SpellDisplayInfo:
    """Information for displaying a spell"""

    spell_id: str
    name: str
    mp_cost: int
    description: str
    element: str
    target_type: str
    is_available: bool = True  # Has enough MP


class MagicMenuUI(UIWidget):
    """
    Magic menu for spell selection.

    Features:
    - List of available spells
    - MP cost display
    - Spell descriptions
    - Unavailable spells greyed out
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)

        self.spells: List[SpellDisplayInfo] = []
        self.selected_index = 0
        self.current_mp = 0
        self.max_mp = 0

        # Style
        self.bg_color = (20, 20, 40, 230)
        self.border_color = (100, 100, 200)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 200, 0)
        self.unavailable_color = (100, 100, 100)
        self.mp_cost_color = (100, 200, 255)

        # Layout
        self.item_height = 40
        self.scroll_offset = 0
        self.visible_items = (height - 100) // self.item_height

        # Callbacks
        self.on_spell_selected: Optional[Callable[[str], None]] = None
        self.on_cancel: Optional[Callable] = None

    def set_spells(self, spells: List[SpellDisplayInfo], current_mp: int, max_mp: int):
        """Set available spells"""
        self.spells = spells
        self.current_mp = current_mp
        self.max_mp = max_mp
        self.selected_index = 0
        self.scroll_offset = 0

        # Update availability
        for spell in self.spells:
            spell.is_available = spell.mp_cost <= current_mp

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.visible or not self.enabled or not self.spells:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.spells)
                self._adjust_scroll()
                return True

            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.spells)
                self._adjust_scroll()
                return True

            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.spells[self.selected_index].is_available:
                    if self.on_spell_selected:
                        spell_id = self.spells[self.selected_index].spell_id
                        self.on_spell_selected(spell_id)
                return True

            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                if self.on_cancel:
                    self.on_cancel()
                return True

        return False

    def _adjust_scroll(self):
        """Adjust scroll offset to keep selected item visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.selected_index - self.visible_items + 1

    def update(self, delta_time: float):
        """Update menu"""
        pass

    def render(self, screen: pygame.Surface):
        """Render magic menu"""
        if not self.visible:
            return

        # Draw background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (self.x, self.y))

        # Draw border
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.border_color, border_rect, 3)

        # Draw title
        title_font = pygame.font.Font(None, 28)
        title_text = "Magic"
        title_surface = title_font.render(title_text, True, self.text_color)
        screen.blit(title_surface, (self.x + 20, self.y + 10))

        # Draw MP display
        mp_font = pygame.font.Font(None, 24)
        mp_text = f"MP: {self.current_mp}/{self.max_mp}"
        mp_surface = mp_font.render(mp_text, True, self.mp_cost_color)
        mp_rect = mp_surface.get_rect(topright=(self.x + self.width - 20, self.y + 10))
        screen.blit(mp_surface, mp_rect)

        # Draw spell list
        spell_font = pygame.font.Font(None, 22)
        desc_font = pygame.font.Font(None, 18)

        list_y_start = self.y + 50
        visible_end = min(self.scroll_offset + self.visible_items, len(self.spells))

        for i in range(self.scroll_offset, visible_end):
            spell = self.spells[i]
            list_index = i - self.scroll_offset
            item_y = list_y_start + list_index * self.item_height

            # Draw selection highlight
            if i == self.selected_index:
                highlight_rect = pygame.Rect(
                    self.x + 10, item_y, self.width - 20, self.item_height - 2
                )
                pygame.draw.rect(screen, self.selected_color, highlight_rect, 2)

            # Draw spell name
            text_color = (
                self.text_color if spell.is_available else self.unavailable_color
            )
            name_surface = spell_font.render(spell.name, True, text_color)
            screen.blit(name_surface, (self.x + 20, item_y + 5))

            # Draw MP cost
            mp_cost_text = f"{spell.mp_cost} MP"
            mp_cost_surface = spell_font.render(mp_cost_text, True, self.mp_cost_color)
            mp_cost_rect = mp_cost_surface.get_rect(
                topright=(self.x + self.width - 20, item_y + 5)
            )
            screen.blit(mp_cost_surface, mp_cost_rect)

            # Draw element
            element_surface = desc_font.render(spell.element, True, (150, 150, 150))
            screen.blit(element_surface, (self.x + 20, item_y + 25))

        # Draw description of selected spell
        if self.spells:
            selected_spell = self.spells[self.selected_index]
            desc_y = self.y + self.height - 60

            # Description background
            desc_bg_rect = pygame.Rect(self.x + 10, desc_y - 5, self.width - 20, 50)
            pygame.draw.rect(screen, (30, 30, 60, 200), desc_bg_rect)
            pygame.draw.rect(screen, self.border_color, desc_bg_rect, 1)

            # Description text
            desc_surface = desc_font.render(
                selected_spell.description, True, self.text_color
            )
            screen.blit(desc_surface, (self.x + 20, desc_y))

            # Target type
            target_text = f"Target: {selected_spell.target_type}"
            target_surface = desc_font.render(target_text, True, (180, 180, 180))
            screen.blit(target_surface, (self.x + 20, desc_y + 20))

        # Draw scroll indicator
        if len(self.spells) > self.visible_items:
            scroll_text = (
                f"▲ {self.scroll_offset + 1}-{visible_end}/{len(self.spells)} ▼"
            )
            scroll_surface = desc_font.render(scroll_text, True, (150, 150, 150))
            scroll_rect = scroll_surface.get_rect(
                bottomright=(self.x + self.width - 20, self.y + self.height - 70)
            )
            screen.blit(scroll_surface, scroll_rect)


class FieldMagicMenuUI(MagicMenuUI):
    """
    Magic menu for field use (outside of battle).

    Only shows spells that can be used outside of battle (healing, etc.)
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.title_text = "Magic - Field"

    def set_spells(self, spells: List[SpellDisplayInfo], current_mp: int, max_mp: int):
        """Set available spells (filter for field use)"""
        # Filter to only healing/buff spells that work outside battle
        field_usable = []
        for spell in spells:
            # Only allow healing spells in field
            if "heal" in spell.name.lower() or "cure" in spell.name.lower():
                field_usable.append(spell)

        super().set_spells(field_usable, current_mp, max_mp)


class QuickMagicBar(UIWidget):
    """
    Quick access magic bar for common spells.

    Shows 1-4 most used spells for quick casting with number keys.
    """

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 400, 60)
        self.quick_spells: List[Optional[SpellDisplayInfo]] = [None, None, None, None]

        # Style
        self.bg_color = (20, 20, 40, 200)
        self.border_color = (100, 100, 200)
        self.slot_size = 90

    def set_quick_spell(self, slot: int, spell: Optional[SpellDisplayInfo]):
        """Set spell in quick slot (0-3)"""
        if 0 <= slot < 4:
            self.quick_spells[slot] = spell

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle quick cast keys (1-4)"""
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.KEYDOWN:
            slot = -1
            if event.key == pygame.K_1:
                slot = 0
            elif event.key == pygame.K_2:
                slot = 1
            elif event.key == pygame.K_3:
                slot = 2
            elif event.key == pygame.K_4:
                slot = 3

            if slot >= 0 and self.quick_spells[slot]:
                spell = self.quick_spells[slot]
                if spell.is_available:
                    # TODO: Trigger spell cast
                    return True

        return False

    def render(self, screen: pygame.Surface):
        """Render quick magic bar"""
        if not self.visible:
            return

        # Draw background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (self.x, self.y))

        # Draw border
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.border_color, border_rect, 2)

        # Draw spell slots
        font = pygame.font.Font(None, 20)
        for i, spell in enumerate(self.quick_spells):
            slot_x = self.x + 10 + i * (self.slot_size + 5)
            slot_y = self.y + 10
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.height - 20)

            # Slot background
            slot_bg_color = (40, 40, 60) if spell else (30, 30, 40)
            pygame.draw.rect(screen, slot_bg_color, slot_rect)
            pygame.draw.rect(screen, self.border_color, slot_rect, 1)

            # Key number
            key_text = str(i + 1)
            key_surface = font.render(key_text, True, (200, 200, 200))
            screen.blit(key_surface, (slot_x + 5, slot_y + 5))

            if spell:
                # Spell name
                name_surface = font.render(spell.name, True, self.border_color)
                name_rect = name_surface.get_rect(
                    center=(slot_x + self.slot_size // 2, slot_y + 20)
                )
                screen.blit(name_surface, name_rect)

                # MP cost
                mp_text = f"{spell.mp_cost} MP"
                mp_color = (100, 200, 255) if spell.is_available else (100, 100, 100)
                mp_surface = font.render(mp_text, True, mp_color)
                mp_rect = mp_surface.get_rect(
                    center=(slot_x + self.slot_size // 2, slot_y + 35)
                )
                screen.blit(mp_surface, mp_rect)
