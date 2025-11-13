"""
JRPG Battle UI

Traditional JRPG battle interface with HP/MP bars, command menus, and battle display.
"""

import pygame
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from ui.ui_system import UIWidget, UIStyle, Anchor


class BattleMenuState(Enum):
    """State of the battle menu"""

    COMMAND_SELECT = "command"  # Selecting command (Attack, Magic, etc.)
    TARGET_SELECT = "target"  # Selecting target
    MAGIC_SELECT = "magic"  # Selecting spell
    ITEM_SELECT = "item"  # Selecting item
    ANIMATING = "animating"  # Battle animation playing


@dataclass
class BattleCommand:
    """Battle command option"""

    name: str
    enabled: bool = True
    icon: Optional[str] = None
    callback: Optional[Callable] = None


class HPBar(UIWidget):
    """HP/MP bar widget for battle UI"""

    def __init__(self, x: int, y: int, width: int, height: int, max_value: int):
        super().__init__(x, y, width, height)
        self.max_value = max_value
        self.current_value = max_value
        self.bar_color = (0, 255, 0)  # Green
        self.bg_color = (50, 50, 50)
        self.border_color = (200, 200, 200)
        self.show_numbers = True

    def set_value(self, value: int):
        """Set current value"""
        self.current_value = max(0, min(value, self.max_value))

        # Change color based on percentage
        percentage = (self.current_value / self.max_value) * 100
        if percentage > 50:
            self.bar_color = (0, 255, 0)  # Green
        elif percentage > 25:
            self.bar_color = (255, 255, 0)  # Yellow
        else:
            self.bar_color = (255, 0, 0)  # Red

    def update(self, delta_time: float):
        """Update bar (for animations)"""
        pass

    def render(self, screen: pygame.Surface):
        """Render HP/MP bar"""
        if not self.visible:
            return

        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect)

        # Draw filled bar
        if self.max_value > 0:
            fill_width = int((self.current_value / self.max_value) * self.width)
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(screen, self.bar_color, fill_rect)

        # Draw border
        pygame.draw.rect(screen, self.border_color, bg_rect, 2)

        # Draw numbers
        if self.show_numbers:
            font = pygame.font.Font(None, 18)
            text = f"{self.current_value}/{self.max_value}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(self.x + self.width // 2, self.y + self.height // 2)
            )
            screen.blit(text_surface, text_rect)


class BattlerDisplay(UIWidget):
    """Display for a single battler (party member or enemy)"""

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.name = ""
        self.level = 1
        self.hp_bar = HPBar(x, y + height - 30, width - 20, 20, 100)
        self.mp_bar = HPBar(x, y + height - 10, width - 20, 10, 50)
        self.mp_bar.bar_color = (0, 150, 255)  # Blue
        self.sprite: Optional[pygame.Surface] = None
        self.is_selected = False
        self.is_enemy = False

    def set_stats(
        self, name: str, level: int, hp: int, max_hp: int, mp: int, max_mp: int
    ):
        """Set battler stats"""
        self.name = name
        self.level = level
        self.hp_bar.max_value = max_hp
        self.hp_bar.set_value(hp)
        self.mp_bar.max_value = max_mp
        self.mp_bar.set_value(mp)

    def update(self, delta_time: float):
        """Update battler display"""
        self.hp_bar.update(delta_time)
        self.mp_bar.update(delta_time)

    def render(self, screen: pygame.Surface):
        """Render battler display"""
        if not self.visible:
            return

        # Draw sprite (if available)
        if self.sprite:
            sprite_rect = self.sprite.get_rect(
                center=(self.x + self.width // 2, self.y + 40)
            )
            screen.blit(self.sprite, sprite_rect)

        # Draw name and level
        font = pygame.font.Font(None, 20)
        name_text = f"{self.name} Lv.{self.level}"
        name_surface = font.render(name_text, True, (255, 255, 255))
        screen.blit(name_surface, (self.x + 10, self.y + 5))

        # Draw HP/MP bars
        self.hp_bar.render(screen)
        if not self.is_enemy:  # Only show MP for party members
            self.mp_bar.render(screen)

        # Draw selection indicator
        if self.is_selected:
            indicator_rect = pygame.Rect(
                self.x - 5, self.y - 5, self.width + 10, self.height + 10
            )
            pygame.draw.rect(screen, (255, 255, 0), indicator_rect, 3)


class BattleCommandMenu(UIWidget):
    """Command menu for battle actions"""

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.commands: List[BattleCommand] = []
        self.selected_index = 0
        self.on_command_selected: Optional[Callable[[str], None]] = None

        # Style
        self.bg_color = (30, 30, 50, 220)
        self.border_color = (150, 150, 200)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 200, 0)
        self.disabled_color = (100, 100, 100)

    def add_command(
        self, name: str, enabled: bool = True, callback: Optional[Callable] = None
    ):
        """Add a command to the menu"""
        self.commands.append(BattleCommand(name, enabled, callback=callback))

    def clear_commands(self):
        """Clear all commands"""
        self.commands.clear()
        self.selected_index = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.commands)
                return True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.commands)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.commands and self.commands[self.selected_index].enabled:
                    command = self.commands[self.selected_index]
                    if self.on_command_selected:
                        self.on_command_selected(command.name)
                    if command.callback:
                        command.callback()
                return True

        return False

    def update(self, delta_time: float):
        """Update menu"""
        pass

    def render(self, screen: pygame.Surface):
        """Render command menu"""
        if not self.visible:
            return

        # Draw background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (self.x, self.y))

        # Draw border
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.border_color, border_rect, 2)

        # Draw commands
        font = pygame.font.Font(None, 24)
        item_height = self.height // max(len(self.commands), 1)

        for i, command in enumerate(self.commands):
            item_y = self.y + i * item_height

            # Draw selection highlight
            if i == self.selected_index:
                highlight_rect = pygame.Rect(
                    self.x + 5, item_y + 5, self.width - 10, item_height - 10
                )
                pygame.draw.rect(screen, self.selected_color, highlight_rect, 2)

            # Draw command text
            text_color = self.text_color if command.enabled else self.disabled_color
            text_surface = font.render(command.name, True, text_color)
            text_rect = text_surface.get_rect(
                midleft=(self.x + 20, item_y + item_height // 2)
            )
            screen.blit(text_surface, text_rect)


class JRPGBattleUI:
    """
    Complete JRPG battle UI system.

    Features:
    - Party member displays with HP/MP bars
    - Enemy displays
    - Command menu (Attack, Magic, Item, Defend, Run)
    - Target selection
    - Battle messages
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # State
        self.menu_state = BattleMenuState.COMMAND_SELECT
        self.current_actor_index = 0

        # Party displays (left side)
        self.party_displays: List[BattlerDisplay] = []
        party_x = 50
        party_y_start = 100
        for i in range(4):
            display = BattlerDisplay(party_x, party_y_start + i * 100, 200, 90)
            self.party_displays.append(display)

        # Enemy displays (right side)
        self.enemy_displays: List[BattlerDisplay] = []
        enemy_x = screen_width - 250
        enemy_y_start = 100
        for i in range(4):
            display = BattlerDisplay(enemy_x, enemy_y_start + i * 100, 200, 90)
            display.is_enemy = True
            self.enemy_displays.append(display)

        # Command menu (bottom center)
        menu_width = 400
        menu_height = 200
        menu_x = (screen_width - menu_width) // 2
        menu_y = screen_height - menu_height - 20
        self.command_menu = BattleCommandMenu(menu_x, menu_y, menu_width, menu_height)

        # Setup default commands
        self.setup_default_commands()

        # Battle message display
        self.message_text = ""
        self.message_timer = 0.0
        self.message_duration = 2.0

        # Callbacks
        self.on_attack_selected: Optional[Callable] = None
        self.on_magic_selected: Optional[Callable] = None
        self.on_item_selected: Optional[Callable] = None
        self.on_defend_selected: Optional[Callable] = None
        self.on_run_selected: Optional[Callable] = None
        self.on_target_selected: Optional[Callable[[int], None]] = None

    def setup_default_commands(self):
        """Setup default battle commands"""
        self.command_menu.clear_commands()
        self.command_menu.add_command("Attack", callback=self.on_attack_command)
        self.command_menu.add_command("Magic", callback=self.on_magic_command)
        self.command_menu.add_command("Item", callback=self.on_item_command)
        self.command_menu.add_command("Defend", callback=self.on_defend_command)
        self.command_menu.add_command("Run", callback=self.on_run_command)

    def on_attack_command(self):
        """Handle Attack command"""
        self.menu_state = BattleMenuState.TARGET_SELECT
        if self.on_attack_selected:
            self.on_attack_selected()

    def on_magic_command(self):
        """Handle Magic command"""
        self.menu_state = BattleMenuState.MAGIC_SELECT
        if self.on_magic_selected:
            self.on_magic_selected()

    def on_item_command(self):
        """Handle Item command"""
        self.menu_state = BattleMenuState.ITEM_SELECT
        if self.on_item_selected:
            self.on_item_selected()

    def on_defend_command(self):
        """Handle Defend command"""
        if self.on_defend_selected:
            self.on_defend_selected()

    def on_run_command(self):
        """Handle Run command"""
        if self.on_run_selected:
            self.on_run_selected()

    def update_party_member(
        self,
        index: int,
        name: str,
        level: int,
        hp: int,
        max_hp: int,
        mp: int,
        max_mp: int,
    ):
        """Update party member display"""
        if 0 <= index < len(self.party_displays):
            self.party_displays[index].set_stats(name, level, hp, max_hp, mp, max_mp)
            self.party_displays[index].visible = True

    def update_enemy(self, index: int, name: str, level: int, hp: int, max_hp: int):
        """Update enemy display"""
        if 0 <= index < len(self.enemy_displays):
            self.enemy_displays[index].set_stats(name, level, hp, max_hp, 0, 0)
            self.enemy_displays[index].visible = True

    def show_message(self, message: str, duration: float = 2.0):
        """Show battle message"""
        self.message_text = message
        self.message_timer = duration
        self.message_duration = duration

    def set_command_menu_visible(self, visible: bool):
        """Show or hide command menu"""
        self.command_menu.visible = visible

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events"""
        # Command menu handles input
        if self.menu_state == BattleMenuState.COMMAND_SELECT:
            return self.command_menu.handle_event(event)

        # Target selection
        elif self.menu_state == BattleMenuState.TARGET_SELECT:
            if event.type == pygame.KEYDOWN:
                # TODO: Implement target selection navigation
                if event.key == pygame.K_RETURN:
                    if self.on_target_selected:
                        self.on_target_selected(0)  # Select first target for now
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = BattleMenuState.COMMAND_SELECT
                    return True

        return False

    def update(self, delta_time: float):
        """Update UI"""
        # Update party displays
        for display in self.party_displays:
            display.update(delta_time)

        # Update enemy displays
        for display in self.enemy_displays:
            display.update(delta_time)

        # Update command menu
        self.command_menu.update(delta_time)

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= delta_time

    def render(self, screen: pygame.Surface):
        """Render battle UI"""
        # Render party displays
        for display in self.party_displays:
            display.render(screen)

        # Render enemy displays
        for display in self.enemy_displays:
            display.render(screen)

        # Render command menu
        self.command_menu.render(screen)

        # Render battle message
        if self.message_timer > 0:
            font = pygame.font.Font(None, 32)
            text_surface = font.render(self.message_text, True, (255, 255, 255))

            # Background for message
            padding = 20
            bg_rect = text_surface.get_rect()
            bg_rect.inflate_ip(padding * 2, padding * 2)
            bg_rect.center = (self.screen_width // 2, 50)

            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            screen.blit(bg_surface, bg_rect)

            # Message text
            text_rect = text_surface.get_rect(center=bg_rect.center)
            screen.blit(text_surface, text_rect)
