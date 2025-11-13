"""
Neon Collapse - Combat System
Implements turn-based combat with initiative from TDD v3.0
"""

import random
from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    AP_BASIC_ATTACK,
    AP_MOVE
)


class CombatEncounter:
    """Manages a single combat encounter"""

    def __init__(self, player_team, enemy_team):
        self.player_team = player_team
        self.enemy_team = enemy_team

        # Validate that at least one team has characters
        if not player_team and not enemy_team:
            raise ValueError("Cannot initialize combat with no characters")

        self.all_characters = player_team + enemy_team

        self.turn_order = []
        self.current_turn_index = 0
        self.current_character = None
        self.combat_active = True
        self.turn_count = 0

        self.combat_log = []
        self.escape_available = False
        self.victor = None  # 'player' or 'enemy' or 'fled'

        # Initialize combat
        self.roll_initiative()

    def roll_initiative(self):
        """
        Roll initiative for all characters
        Initiative = (Reflexes × 2) + random(1, 10)
        """
        initiative_rolls = []

        for char in self.all_characters:
            initiative = char.get_initiative()
            initiative_rolls.append((initiative, char))

        # Sort by initiative (highest first)
        initiative_rolls.sort(key=lambda x: x[0], reverse=True)

        self.turn_order = [char for _, char in initiative_rolls]
        self.current_character = self.turn_order[0]

        # Log initiative
        self.add_log("=== COMBAT START ===")
        for init, char in initiative_rolls:
            self.add_log(f"{char.name} rolled initiative: {init}")

    def add_log(self, message):
        """Add message to combat log"""
        self.combat_log.append(message)
        if len(self.combat_log) > 20:  # Keep last 20 messages
            self.combat_log.pop(0)

    def next_turn(self):
        """Advance to next character's turn"""
        # End current character's turn
        if self.current_character:
            self.current_character.end_turn()

        # Move to next in turn order
        self.current_turn_index += 1

        # Check if round complete
        if self.current_turn_index >= len(self.turn_order):
            self.current_turn_index = 0
            self.turn_count += 1
            self.add_log(f"=== Turn {self.turn_count + 1} ===")

            # Check escape availability (Turn 3+)
            if self.turn_count >= 3:
                self.check_escape_conditions()

        # Find next alive character
        found_alive = False
        while self.current_turn_index < len(self.turn_order):
            char = self.turn_order[self.current_turn_index]
            if char.is_alive:
                self.current_character = char
                self.current_character.start_turn()
                self.add_log(f">>> {char.name}'s turn ({char.team}) <<<")
                found_alive = True
                break
            else:
                self.current_turn_index += 1

        # If no alive character found, wrap around to start of turn order
        if not found_alive and self.turn_order:
            self.current_turn_index = 0
            # All characters in current pass are dead, combat should end
            # Let check_victory handle this

        # Check victory conditions
        self.check_victory()

    def check_escape_conditions(self):
        """
        Check if escape is available based on TDD conditions:
        - Turn 3+
        - Party HP average < 50% OR
        - One party member dead OR
        - Outnumbered 2:1 OR
        - Elite detected
        """
        if self.turn_count < 3:
            return

        player_alive = [c for c in self.player_team if c.is_alive]
        enemy_alive = [c for c in self.enemy_team if c.is_alive]

        if not player_alive:
            return

        # Calculate average HP
        avg_hp = sum(c.get_hp_percentage() for c in player_alive) / len(player_alive)

        # Check conditions
        hp_critical = avg_hp < 50
        casualties = len(player_alive) < len(self.player_team)
        outnumbered = len(enemy_alive) >= len(player_alive) * 2

        if hp_critical or casualties or outnumbered:
            if not self.escape_available:  # Only log once
                self.add_log("⚠️ ESCAPE AVAILABLE - Press [E] to attempt retreat!")
            self.escape_available = True

    def attempt_escape(self, sacrifice_character=None):
        """
        Attempt to escape combat
        Base chance: 45% + (Reflex × 2)%
        With sacrifice: 90-95% (sacrifice dies regardless)
        """
        if not self.escape_available:
            return False, "Escape not available yet! (Turn 3+ required)"

        if sacrifice_character:
            # Sacrifice guarantees near-certain escape
            escape_chance = 93
            self.add_log(f"{sacrifice_character.name} stays behind to cover the retreat!")
        else:
            # Solo escape - risky
            player_leader = self.player_team[0]  # Use first player character
            escape_chance = 45 + (player_leader.reflexes * 2)
            escape_chance = min(95, max(5, escape_chance))
            self.add_log(f"Attempting solo escape... ({escape_chance}% chance)")

        # Roll escape
        roll = random.randint(1, 100)

        if roll <= escape_chance:
            # Escape successful
            if sacrifice_character:
                sacrifice_character.hp = 0
                sacrifice_character.is_alive = False
                self.add_log(f"✓ {sacrifice_character.name} died buying time. Party escaped.")
            else:
                self.add_log("✓ Escape successful! Retreated from combat.")

            # Apply morale penalty
            for char in self.player_team:
                if char.is_alive:
                    char.morale = max(0, char.morale - 20)

            self.combat_active = False
            self.victor = 'fled'
            return True, "Escaped successfully!"
        else:
            # Escape failed
            if sacrifice_character:
                sacrifice_character.hp = 0
                sacrifice_character.is_alive = False
                self.add_log(f"✗ Escape FAILED! {sacrifice_character.name} died in vain!")
            else:
                # Failed escape costs HP
                player_leader = self.player_team[0]
                penalty_damage = int(player_leader.max_hp * 0.2)
                player_leader.take_damage(penalty_damage)
                self.add_log(f"✗ Escape FAILED! Took {penalty_damage} damage.")

            return False, "Escape failed! Enemies caught you."

    def check_victory(self):
        """Check if combat has ended"""
        player_alive = any(c.is_alive for c in self.player_team)
        enemy_alive = any(c.is_alive for c in self.enemy_team)

        if not player_alive:
            self.combat_active = False
            self.victor = 'enemy'
            self.add_log("=== DEFEAT ===")
        elif not enemy_alive:
            self.combat_active = False
            self.victor = 'player'
            self.add_log("=== VICTORY ===")

    def get_current_team(self):
        """Get current character's team"""
        if self.current_character:
            return self.current_character.team
        return None

    def get_valid_moves(self, character):
        """Get valid movement positions for character"""
        valid_moves = []
        move_range = character.movement_range

        for dx in range(-move_range, move_range + 1):
            for dy in range(-move_range, move_range + 1):
                # Manhattan distance check
                if abs(dx) + abs(dy) <= move_range:
                    new_x = character.x + dx
                    new_y = character.y + dy

                    # Check bounds
                    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                        # Check if tile occupied
                        occupied = any(
                            c.x == new_x and c.y == new_y and c.is_alive
                            for c in self.all_characters if c != character
                        )
                        if not occupied:
                            valid_moves.append((new_x, new_y))

        return valid_moves

    def get_valid_targets(self, character):
        """Get valid attack targets for character"""
        return character.get_targets_in_range(self.all_characters)

    def _find_closest_character(self, from_char, character_list):
        """Find the closest character from a list using Manhattan distance"""
        if not character_list:
            return None
        return min(character_list, key=lambda t: abs(from_char.x - t.x) + abs(from_char.y - t.y))

    def _calculate_move_direction(self, from_char, to_char):
        """Calculate direction to move from one character towards another"""
        dx = 0
        dy = 0
        if to_char.x > from_char.x:
            dx = 1
        elif to_char.x < from_char.x:
            dx = -1

        if to_char.y > from_char.y:
            dy = 1
        elif to_char.y < from_char.y:
            dy = -1

        return dx, dy

    def _is_position_valid(self, x, y, moving_char):
        """Check if a position is valid (in bounds and unoccupied)"""
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False

        occupied = any(
            c.x == x and c.y == y and c.is_alive
            for c in self.all_characters if c != moving_char
        )
        return not occupied

    def _ai_try_attack(self, enemy):
        """Try to attack if targets in range. Returns True if attack was performed."""
        targets = self.get_valid_targets(enemy)
        if targets and enemy.ap >= AP_BASIC_ATTACK:
            target = self._find_closest_character(enemy, targets)
            if target:
                damage, log = enemy.attack(target)
                self.add_log(log)
                return True
        return False

    def _ai_try_move(self, enemy, player_alive):
        """Try to move towards closest player. Returns True if move was performed."""
        if enemy.ap < AP_MOVE:
            return False

        target = self._find_closest_character(enemy, player_alive)
        if not target:
            return False

        dx, dy = self._calculate_move_direction(enemy, target)
        new_x = enemy.x + dx
        new_y = enemy.y + dy

        if self._is_position_valid(new_x, new_y, enemy):
            success, log = enemy.move(new_x, new_y)
            if success:
                self.add_log(log)
                return True
        return False

    def enemy_ai_turn(self, enemy):
        """Simple AI for enemy turns"""
        player_alive = [c for c in self.player_team if c.is_alive]
        if not player_alive:
            return

        # Try to attack first, then move
        if not self._ai_try_attack(enemy):
            self._ai_try_move(enemy, player_alive)

        # End turn if no AP left
        if enemy.ap == 0:
            self.next_turn()
