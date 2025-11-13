"""
Neon Collapse - Combat Prototype
Main game loop

Controls:
- Mouse: Click to select characters and tiles
- Move: Click Move button, then click destination
- Attack: Click Attack button, then click target
- End Turn: Click End Turn button
- Escape: Press E (when available)
- Quit: ESC or close window
"""

import pygame
import sys
from character import Character
from combat import CombatEncounter
from ui import CombatUI
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GRID_WIDTH,
    GRID_HEIGHT,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    TILE_SIZE,
    AP_MOVE,
    AP_BASIC_ATTACK,
    AP_RETREAT,
    COLOR_BG,
    COLOR_SELECTED,
    COLOR_UI_TEXT,
    UI_PANEL_X,
    PLAYER_START_STATS,
    ALLY_START_STATS,
    ENEMY_GRUNT_STATS,
    ENEMY_ELITE_STATS
)


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Collapse - Combat Prototype")
        self.clock = pygame.time.Clock()

        self.ui = CombatUI(self.screen)
        self.ui.init_fonts()

        # Game state
        self.combat = None
        self.selected_character = None
        self.game_state = 'setup'  # 'setup', 'combat', 'victory'

        # Input state
        self.action_mode = None  # None, 'move', 'attack'
        self.action_buttons = {}

        # Initialize combat
        self.setup_combat()

    def setup_combat(self):
        """Create demo combat encounter"""
        # Player team
        player = Character(
            name="V",
            x=2, y=7,
            stats=PLAYER_START_STATS,
            weapon='assault_rifle',
            team='player'
        )

        ally = Character(
            name="Jackie",
            x=3, y=7,
            stats=ALLY_START_STATS,
            weapon='shotgun',
            team='player'
        )

        # Enemy team
        enemy1 = Character(
            name="Gang Grunt 1",
            x=17, y=6,
            stats=ENEMY_GRUNT_STATS,
            weapon='pistol',
            team='enemy'
        )

        enemy2 = Character(
            name="Gang Grunt 2",
            x=17, y=8,
            stats=ENEMY_GRUNT_STATS,
            weapon='pistol',
            team='enemy'
        )

        enemy3 = Character(
            name="Gang Elite",
            x=18, y=7,
            stats=ENEMY_ELITE_STATS,
            weapon='assault_rifle',
            team='enemy'
        )

        player_team = [player, ally]
        enemy_team = [enemy1, enemy2, enemy3]

        self.combat = CombatEncounter(player_team, enemy_team)
        self.game_state = 'combat'

        # Select first player character
        if self.combat.current_character.team == 'player':
            self.selected_character = self.combat.current_character

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # Escape key
                if event.key == pygame.K_e and self.combat.escape_available:
                    if self.combat.current_character.team == 'player':
                        success, msg = self.combat.attempt_escape()
                        if not success:
                            # Failed escape, continue combat
                            pass

                # Victory screen - press space to continue
                if event.key == pygame.K_SPACE and self.game_state == 'victory':
                    self.setup_combat()  # Restart combat

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos)

        return True

    def handle_click(self, pos):
        """Handle mouse click"""
        mouse_x, mouse_y = pos

        # Check if clicking on action buttons
        if self.combat.current_character and self.combat.current_character.team == 'player':
            for action, rect in self.action_buttons.items():
                if rect.collidepoint(pos):
                    self.handle_button_click(action)
                    return

        # Check if clicking on grid
        grid_x = (mouse_x - GRID_OFFSET_X) // TILE_SIZE
        grid_y = (mouse_y - GRID_OFFSET_Y) // TILE_SIZE

        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            self.handle_grid_click(grid_x, grid_y)

    def handle_button_click(self, action):
        """Handle action button click"""
        current = self.combat.current_character

        if action == 'move':
            if current.ap >= AP_MOVE:
                self.action_mode = 'move'
        elif action == 'attack':
            if current.ap >= AP_BASIC_ATTACK:
                self.action_mode = 'attack'
        elif action == 'end_turn':
            self.action_mode = None
            self.combat.next_turn()
            self.update_ai_turns()
        elif action == 'escape':
            if self.combat.escape_available:
                success, msg = self.combat.attempt_escape()

    def handle_grid_click(self, grid_x, grid_y):
        """Handle click on grid tile"""
        current = self.combat.current_character

        if not current or current.team != 'player':
            return

        if self.action_mode == 'move':
            # Attempt move
            valid_moves = self.combat.get_valid_moves(current)
            if (grid_x, grid_y) in valid_moves:
                success, log = current.move(grid_x, grid_y)
                if success:
                    self.combat.add_log(log)
                    self.action_mode = None

                    # Auto-end turn if no AP left
                    if current.ap == 0:
                        self.combat.next_turn()
                        self.update_ai_turns()

        elif self.action_mode == 'attack':
            # Check if clicking on valid target
            valid_targets = self.combat.get_valid_targets(current)
            for target in valid_targets:
                if target.x == grid_x and target.y == grid_y:
                    damage, log = current.attack(target)
                    if log:
                        self.combat.add_log(log)
                        self.action_mode = None

                        # Auto-end turn if no AP left
                        if current.ap == 0:
                            self.combat.next_turn()
                            self.update_ai_turns()
                    break

    def update_ai_turns(self):
        """Process AI turns until player turn"""
        while (self.combat.combat_active and
               self.combat.current_character and
               self.combat.current_character.team == 'enemy'):

            # AI turn
            self.combat.enemy_ai_turn(self.combat.current_character)

            # Render AI turn
            self.render()
            pygame.display.flip()
            pygame.time.wait(500)  # Delay so player can see AI actions

        # Check if combat ended
        if not self.combat.combat_active:
            self.game_state = 'victory'

    def render(self):
        """Render game"""
        self.screen.fill(COLOR_BG)

        # Draw grid
        self.ui.draw_grid()

        # Draw movement/attack range if in action mode
        if self.action_mode == 'move' and self.selected_character:
            valid_moves = self.combat.get_valid_moves(self.selected_character)
            self.ui.draw_movement_range(valid_moves)
        elif self.action_mode == 'attack' and self.selected_character:
            valid_targets = self.combat.get_valid_targets(self.selected_character)
            self.ui.draw_attack_range(valid_targets)

        # Draw all characters
        for char in self.combat.all_characters:
            if char.is_alive:
                selected = (char == self.selected_character)
                self.ui.draw_character(char, selected)

        # Draw UI panels
        ui_x = UI_PANEL_X
        ui_y = 20

        # Current character panel
        if self.combat.current_character:
            self.ui.draw_character_panel(self.combat.current_character, ui_x, ui_y)

        # Action buttons (only for player characters)
        if self.combat.current_character and self.combat.current_character.team == 'player':
            button_y = ui_y + 220
            self.action_buttons = self.ui.draw_action_buttons(
                self.combat.current_character, ui_x, button_y
            )

            # Update escape button state
            if self.combat.escape_available:
                escape_rect = self.action_buttons['escape']
                self.ui.draw_button(
                    f"Escape ({AP_RETREAT} AP)",
                    escape_rect.x, escape_rect.y,
                    escape_rect.width, escape_rect.height,
                    enabled=True
                )

        # Combat log
        log_y = ui_y + 350
        self.ui.draw_combat_log(self.combat.combat_log, ui_x, log_y)

        # Turn indicator
        turn_text = self.ui.font_medium.render(
            f"Turn {self.combat.turn_count + 1}",
            True, COLOR_UI_TEXT
        )
        self.screen.blit(turn_text, (20, 10))

        # Current action mode indicator
        if self.action_mode:
            mode_text = self.ui.font_medium.render(
                f"Mode: {self.action_mode.upper()}",
                True, COLOR_SELECTED
            )
            self.screen.blit(mode_text, (20, 40))

        # Victory screen
        if self.game_state == 'victory':
            self.ui.draw_victory_screen(self.combat.victor)

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            running = self.handle_events()

            # Render
            self.render()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
