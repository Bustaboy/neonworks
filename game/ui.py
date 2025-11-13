"""
Neon Collapse - UI Rendering
Handles all visual elements for the combat prototype
"""

import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRID_WIDTH,
    GRID_HEIGHT,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    TILE_SIZE,
    AP_BASIC_ATTACK,
    AP_MOVE,
    AP_RETREAT,
    COLOR_GRID,
    COLOR_PLAYER,
    COLOR_ALLY,
    COLOR_ENEMY,
    COLOR_SELECTED,
    COLOR_UI_BG,
    COLOR_UI_TEXT,
    COLOR_HP_FULL,
    COLOR_HP_MID,
    COLOR_HP_LOW,
    COLOR_AP_BAR,
    UI_PANEL_WIDTH,
    UI_LOG_HEIGHT
)


class CombatUI:
    """Handles rendering of combat interface"""

    def __init__(self, screen):
        self.screen = screen
        self.font_large = None
        self.font_medium = None
        self.font_small = None

    def init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)
        except:
            # Fallback to default font
            self.font_large = pygame.font.SysFont('arial', 36)
            self.font_medium = pygame.font.SysFont('arial', 28)
            self.font_small = pygame.font.SysFont('arial', 22)

    def draw_grid(self):
        """Draw combat grid"""
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * TILE_SIZE,
                    GRID_OFFSET_Y + y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

    def draw_movement_range(self, valid_moves):
        """Draw valid movement tiles"""
        for x, y in valid_moves:
            rect = pygame.Rect(
                GRID_OFFSET_X + x * TILE_SIZE,
                GRID_OFFSET_Y + y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            # Semi-transparent overlay
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.set_alpha(80)
            s.fill((100, 100, 255))
            self.screen.blit(s, rect)

    def draw_attack_range(self, valid_targets):
        """Highlight valid attack targets"""
        for target in valid_targets:
            rect = pygame.Rect(
                GRID_OFFSET_X + target.x * TILE_SIZE,
                GRID_OFFSET_Y + target.y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            # Red overlay
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.set_alpha(100)
            s.fill((255, 100, 100))
            self.screen.blit(s, rect)

    def draw_character(self, character, selected=False):
        """Draw a character on the grid"""
        x_pos = GRID_OFFSET_X + character.x * TILE_SIZE
        y_pos = GRID_OFFSET_Y + character.y * TILE_SIZE

        # Choose color based on team
        if character.team == 'player':
            if character == character:  # If it's the main player
                color = COLOR_PLAYER
            else:
                color = COLOR_ALLY
        else:
            color = COLOR_ENEMY

        # Draw character square
        rect = pygame.Rect(x_pos + 4, y_pos + 4, TILE_SIZE - 8, TILE_SIZE - 8)
        pygame.draw.rect(self.screen, color, rect)

        # Draw selection indicator
        if selected:
            pygame.draw.rect(self.screen, COLOR_SELECTED, rect, 3)

        # Draw HP bar above character
        self.draw_mini_hp_bar(character, x_pos, y_pos - 8)

        # Draw name label
        name_text = self.font_small.render(character.name[:8], True, COLOR_UI_TEXT)
        self.screen.blit(name_text, (x_pos, y_pos + TILE_SIZE + 2))

    def draw_mini_hp_bar(self, character, x, y):
        """Draw small HP bar above character"""
        bar_width = TILE_SIZE - 4
        bar_height = 4

        # Background
        bg_rect = pygame.Rect(x + 2, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)

        # HP fill
        hp_percent = character.get_hp_percentage() / 100
        fill_width = int(bar_width * hp_percent)

        # Color based on HP
        if hp_percent > 0.6:
            hp_color = COLOR_HP_FULL
        elif hp_percent > 0.3:
            hp_color = COLOR_HP_MID
        else:
            hp_color = COLOR_HP_LOW

        fill_rect = pygame.Rect(x + 2, y, fill_width, bar_height)
        pygame.draw.rect(self.screen, hp_color, fill_rect)

    def draw_character_panel(self, character, x, y):
        """Draw detailed character info panel"""
        panel_height = 200

        # Panel background
        panel_rect = pygame.Rect(x, y, UI_PANEL_WIDTH - 40, panel_height)
        pygame.draw.rect(self.screen, COLOR_UI_BG, panel_rect)
        pygame.draw.rect(self.screen, COLOR_PLAYER, panel_rect, 2)

        # Character name
        name_text = self.font_medium.render(character.name, True, COLOR_PLAYER)
        self.screen.blit(name_text, (x + 10, y + 10))

        # HP bar
        hp_text = self.font_small.render(f"HP: {character.hp}/{character.max_hp}", True, COLOR_UI_TEXT)
        self.screen.blit(hp_text, (x + 10, y + 45))

        hp_bar_width = UI_PANEL_WIDTH - 60
        hp_percent = character.get_hp_percentage() / 100

        # HP bar background
        hp_bg = pygame.Rect(x + 10, y + 70, hp_bar_width, 20)
        pygame.draw.rect(self.screen, (50, 50, 50), hp_bg)

        # HP bar fill
        hp_fill_width = int(hp_bar_width * hp_percent)
        hp_fill = pygame.Rect(x + 10, y + 70, hp_fill_width, 20)

        if hp_percent > 0.6:
            hp_color = COLOR_HP_FULL
        elif hp_percent > 0.3:
            hp_color = COLOR_HP_MID
        else:
            hp_color = COLOR_HP_LOW

        pygame.draw.rect(self.screen, hp_color, hp_fill)

        # AP bar
        ap_text = self.font_small.render(f"AP: {character.ap}/{character.max_ap}", True, COLOR_UI_TEXT)
        self.screen.blit(ap_text, (x + 10, y + 100))

        ap_bar_width = UI_PANEL_WIDTH - 60
        ap_percent = character.ap / character.max_ap

        # AP bar background
        ap_bg = pygame.Rect(x + 10, y + 125, ap_bar_width, 20)
        pygame.draw.rect(self.screen, (50, 50, 50), ap_bg)

        # AP bar fill
        ap_fill_width = int(ap_bar_width * ap_percent)
        ap_fill = pygame.Rect(x + 10, y + 125, ap_fill_width, 20)
        pygame.draw.rect(self.screen, COLOR_AP_BAR, ap_fill)

        # Weapon info
        weapon_text = self.font_small.render(f"Weapon: {character.weapon['name']}", True, COLOR_UI_TEXT)
        self.screen.blit(weapon_text, (x + 10, y + 160))

    def draw_combat_log(self, combat_log, x, y):
        """Draw combat log"""
        log_rect = pygame.Rect(x, y, UI_PANEL_WIDTH - 40, UI_LOG_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, log_rect)
        pygame.draw.rect(self.screen, COLOR_GRID, log_rect, 2)

        # Title
        title_text = self.font_medium.render("Combat Log", True, COLOR_UI_TEXT)
        self.screen.blit(title_text, (x + 10, y + 5))

        # Log entries (last 8 messages)
        start_y = y + 35
        visible_logs = combat_log[-8:]  # Last 8 messages

        for i, message in enumerate(visible_logs):
            log_text = self.font_small.render(message[:45], True, (180, 180, 200))
            self.screen.blit(log_text, (x + 10, start_y + i * 20))

    def draw_button(self, text, x, y, width, height, enabled=True):
        """Draw a button and return its rect"""
        rect = pygame.Rect(x, y, width, height)

        # Button background
        if enabled:
            bg_color = (40, 120, 180)
            text_color = (255, 255, 255)
        else:
            bg_color = (60, 60, 70)
            text_color = (100, 100, 110)

        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, COLOR_GRID, rect, 2)

        # Button text
        button_text = self.font_small.render(text, True, text_color)
        text_rect = button_text.get_rect(center=rect.center)
        self.screen.blit(button_text, text_rect)

        return rect

    def draw_action_buttons(self, character, x, y):
        """Draw action buttons for current character"""
        button_width = (UI_PANEL_WIDTH - 60) // 2
        button_height = 40
        spacing = 10

        buttons = {}

        # Move button
        move_enabled = character.ap >= AP_MOVE
        buttons['move'] = self.draw_button(
            f"Move ({AP_MOVE} AP)",
            x, y,
            button_width, button_height,
            move_enabled
        )

        # Attack button
        attack_enabled = character.ap >= AP_BASIC_ATTACK
        buttons['attack'] = self.draw_button(
            f"Attack ({AP_BASIC_ATTACK} AP)",
            x + button_width + spacing, y,
            button_width, button_height,
            attack_enabled
        )

        # End Turn button
        buttons['end_turn'] = self.draw_button(
            "End Turn",
            x, y + button_height + spacing,
            button_width, button_height,
            True
        )

        # Escape button (if available)
        escape_enabled = False  # Will be set by combat system
        buttons['escape'] = self.draw_button(
            f"Escape ({AP_RETREAT} AP)",
            x + button_width + spacing, y + button_height + spacing,
            button_width, button_height,
            escape_enabled
        )

        return buttons

    def draw_victory_screen(self, victor):
        """Draw victory/defeat screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Victory/Defeat text
        if victor == 'player':
            text = "VICTORY!"
            color = COLOR_HP_FULL
        elif victor == 'enemy':
            text = "DEFEAT"
            color = COLOR_HP_LOW
        else:  # fled
            text = "RETREATED"
            color = COLOR_UI_TEXT

        victory_text = self.font_large.render(text, True, color)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, text_rect)

        # Press Space to continue
        continue_text = self.font_medium.render("Press SPACE to continue", True, COLOR_UI_TEXT)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)
