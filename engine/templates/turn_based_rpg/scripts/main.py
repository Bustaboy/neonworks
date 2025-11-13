#!/usr/bin/env python3
"""
Turn-Based RPG Template - Main Script

A template demonstrating:
- Turn-based combat system
- Character stats and progression
- Enemy AI
- Health and damage calculations
- Menu and battle screens

Controls:
- SPACE: Start game / Select action
- Number keys (1-3): Choose actions in combat
- ESC: Quit game
"""

import pygame
import sys
import random
from pathlib import Path
from enum import Enum

# Add engine to Python path
engine_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(engine_path))

from engine.core.ecs import World, Entity, Component, System
from engine.core.game_loop import GameEngine
from engine.systems.turn_system import TurnSystem, TurnComponent
from engine.gameplay.combat import CombatComponent, DamageCalculator


# Game States
class GameState(Enum):
    MENU = 1
    BATTLE = 2
    VICTORY = 3
    DEFEAT = 4


# Components
class Stats(Component):
    """Character statistics"""
    def __init__(self, hp: int = 100, attack: int = 10, defense: int = 5, speed: int = 10):
        self.max_hp = hp
        self.current_hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed


class PlayerCharacter(Component):
    """Marks entity as player character"""
    pass


class Enemy(Component):
    """Enemy component with AI behavior"""
    def __init__(self, name: str = "Enemy", difficulty: int = 1):
        self.name = name
        self.difficulty = difficulty


class BattleAction(Component):
    """Pending battle action"""
    def __init__(self, action_type: str = "attack", target=None):
        self.action_type = action_type  # "attack", "defend", "skill"
        self.target = target


class DisplayInfo(Component):
    """Display information for rendering"""
    def __init__(self, name: str, color: tuple = (255, 255, 255)):
        self.name = name
        self.color = color


# Systems
class BattleSystem(System):
    """Handle battle logic"""

    def __init__(self):
        super().__init__()
        self.battle_log = []

    def update(self, world: World, delta_time: float):
        """Process battle actions"""
        # Find entities with pending actions
        for entity in world.get_entities_with_component(BattleAction):
            action = entity.get_component(BattleAction)
            stats = entity.get_component(Stats)
            display = entity.get_component(DisplayInfo)

            if action.action_type == "attack" and action.target:
                self._execute_attack(entity, action.target, world)

            # Remove action after execution
            entity.remove_component(BattleAction)

    def _execute_attack(self, attacker: Entity, target: Entity, world: World):
        """Execute an attack action"""
        attacker_stats = attacker.get_component(Stats)
        target_stats = target.get_component(Stats)
        attacker_display = attacker.get_component(DisplayInfo)
        target_display = target.get_component(DisplayInfo)

        if not all([attacker_stats, target_stats]):
            return

        # Calculate damage
        base_damage = attacker_stats.attack
        reduction = target_stats.defense * 0.5
        damage = max(1, int(base_damage - reduction + random.randint(-3, 3)))

        # Apply damage
        target_stats.current_hp -= damage
        target_stats.current_hp = max(0, target_stats.current_hp)

        # Log the action
        attacker_name = attacker_display.name if attacker_display else "Unknown"
        target_name = target_display.name if target_display else "Unknown"
        self.battle_log.append(f"{attacker_name} attacks {target_name} for {damage} damage!")

        if target_stats.current_hp <= 0:
            self.battle_log.append(f"{target_name} has been defeated!")


class TurnOrderSystem(System):
    """Manage turn order based on speed"""

    def __init__(self):
        super().__init__()
        self.turn_order = []
        self.current_turn_index = 0

    def initialize_battle(self, world: World):
        """Initialize turn order for battle"""
        # Gather all combatants
        combatants = []

        for entity in world.get_entities_with_component(Stats):
            if entity.has_component(PlayerCharacter) or entity.has_component(Enemy):
                stats = entity.get_component(Stats)
                combatants.append((entity, stats.speed))

        # Sort by speed (highest first)
        combatants.sort(key=lambda x: x[1], reverse=True)
        self.turn_order = [c[0] for c in combatants]
        self.current_turn_index = 0

    def get_current_turn(self) -> Entity:
        """Get the entity whose turn it is"""
        if not self.turn_order:
            return None
        return self.turn_order[self.current_turn_index]

    def next_turn(self):
        """Advance to next turn"""
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def update(self, world: World, delta_time: float):
        """Update turn order (remove defeated entities)"""
        self.turn_order = [
            entity for entity in self.turn_order
            if entity.get_component(Stats).current_hp > 0
        ]


class EnemyAISystem(System):
    """Simple enemy AI"""

    def execute_turn(self, enemy_entity: Entity, world: World):
        """Execute enemy turn"""
        # Find player
        players = world.get_entities_with_component(PlayerCharacter)
        if not players:
            return

        target = players[0]

        # Simple AI: always attack player
        enemy_entity.add_component(BattleAction(action_type="attack", target=target))


# Game Logic
class RPGGame:
    """Main game controller"""

    def __init__(self):
        pygame.init()

        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.FPS = 60

        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Turn-Based RPG - NeonWorks Template")

        self.clock = pygame.time.Clock()
        self.world = World()

        # Systems
        self.battle_system = BattleSystem()
        self.turn_order_system = TurnOrderSystem()
        self.enemy_ai = EnemyAISystem()

        self.world.add_system(self.battle_system)
        self.world.add_system(self.turn_order_system)
        self.world.add_system(self.enemy_ai)

        # Game state
        self.state = GameState.MENU
        self.player_entity = None
        self.enemy_entity = None

        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def create_player(self):
        """Create player character"""
        player = self.world.create_entity()
        player.add_component(Stats(hp=100, attack=15, defense=8, speed=12))
        player.add_component(PlayerCharacter())
        player.add_component(DisplayInfo("Hero", (100, 200, 255)))
        return player

    def create_enemy(self, difficulty: int = 1):
        """Create enemy"""
        enemy = self.world.create_entity()

        # Scale stats with difficulty
        hp = 50 + (difficulty * 20)
        attack = 8 + (difficulty * 3)
        defense = 5 + (difficulty * 2)
        speed = 8 + (difficulty * 1)

        enemy.add_component(Stats(hp=hp, attack=attack, defense=defense, speed=speed))
        enemy.add_component(Enemy(name=f"Slime Lv.{difficulty}", difficulty=difficulty))
        enemy.add_component(DisplayInfo(f"Slime Lv.{difficulty}", (100, 255, 100)))

        return enemy

    def start_battle(self):
        """Start a new battle"""
        self.state = GameState.BATTLE
        self.battle_system.battle_log = []

        # Create combatants
        self.player_entity = self.create_player()
        self.enemy_entity = self.create_enemy(difficulty=random.randint(1, 3))

        # Initialize turn order
        self.turn_order_system.initialize_battle(self.world)

        self.battle_system.battle_log.append("Battle started!")

    def handle_player_action(self, action_type: str):
        """Handle player action in battle"""
        if self.state != GameState.BATTLE:
            return

        current_turn = self.turn_order_system.get_current_turn()

        if current_turn == self.player_entity:
            if action_type == "attack":
                self.player_entity.add_component(
                    BattleAction(action_type="attack", target=self.enemy_entity)
                )
                self.process_turn()

    def process_turn(self):
        """Process current turn"""
        # Update battle system to execute actions
        self.world.update(0)

        # Check win/loss conditions
        if self.check_battle_end():
            return

        # Advance turn
        self.turn_order_system.next_turn()

        # If it's enemy turn, execute AI
        current_turn = self.turn_order_system.get_current_turn()
        if current_turn and current_turn.has_component(Enemy):
            self.enemy_ai.execute_turn(current_turn, self.world)
            self.world.update(0)
            self.check_battle_end()
            self.turn_order_system.next_turn()

    def check_battle_end(self) -> bool:
        """Check if battle has ended"""
        player_stats = self.player_entity.get_component(Stats) if self.player_entity else None
        enemy_stats = self.enemy_entity.get_component(Stats) if self.enemy_entity else None

        if player_stats and player_stats.current_hp <= 0:
            self.state = GameState.DEFEAT
            return True

        if enemy_stats and enemy_stats.current_hp <= 0:
            self.state = GameState.VICTORY
            return True

        return False

    def render(self):
        """Render game"""
        self.screen.fill((30, 30, 40))

        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.BATTLE:
            self.render_battle()
        elif self.state == GameState.VICTORY:
            self.render_victory()
        elif self.state == GameState.DEFEAT:
            self.render_defeat()

        pygame.display.flip()

    def render_menu(self):
        """Render main menu"""
        title = self.font.render("Turn-Based RPG", True, (255, 255, 255))
        self.screen.blit(title, (self.WINDOW_WIDTH // 2 - 150, 200))

        instruction = self.small_font.render("Press SPACE to Start Battle", True, (200, 200, 200))
        self.screen.blit(instruction, (self.WINDOW_WIDTH // 2 - 150, 300))

        esc_text = self.small_font.render("Press ESC to Quit", True, (150, 150, 150))
        self.screen.blit(esc_text, (self.WINDOW_WIDTH // 2 - 100, 350))

    def render_battle(self):
        """Render battle screen"""
        # Title
        title = self.font.render("BATTLE!", True, (255, 200, 100))
        self.screen.blit(title, (self.WINDOW_WIDTH // 2 - 60, 20))

        # Player stats
        if self.player_entity:
            stats = self.player_entity.get_component(Stats)
            display = self.player_entity.get_component(DisplayInfo)

            y_pos = 100
            self.screen.blit(
                self.font.render(display.name, True, display.color),
                (50, y_pos)
            )
            self.screen.blit(
                self.small_font.render(f"HP: {stats.current_hp}/{stats.max_hp}", True, (255, 255, 255)),
                (50, y_pos + 40)
            )
            self.screen.blit(
                self.small_font.render(f"ATK: {stats.attack} | DEF: {stats.defense}", True, (200, 200, 200)),
                (50, y_pos + 70)
            )

        # Enemy stats
        if self.enemy_entity:
            stats = self.enemy_entity.get_component(Stats)
            display = self.enemy_entity.get_component(DisplayInfo)

            y_pos = 100
            x_pos = self.WINDOW_WIDTH - 300

            self.screen.blit(
                self.font.render(display.name, True, display.color),
                (x_pos, y_pos)
            )
            self.screen.blit(
                self.small_font.render(f"HP: {stats.current_hp}/{stats.max_hp}", True, (255, 255, 255)),
                (x_pos, y_pos + 40)
            )

        # Turn indicator
        current_turn = self.turn_order_system.get_current_turn()
        if current_turn:
            is_player_turn = current_turn == self.player_entity
            turn_text = "Your Turn!" if is_player_turn else "Enemy Turn..."
            color = (100, 255, 100) if is_player_turn else (255, 100, 100)

            text = self.font.render(turn_text, True, color)
            self.screen.blit(text, (self.WINDOW_WIDTH // 2 - 100, 250))

        # Actions (only during player turn)
        if current_turn == self.player_entity:
            actions_y = 320
            self.screen.blit(
                self.small_font.render("Press 1: Attack", True, (255, 255, 255)),
                (self.WINDOW_WIDTH // 2 - 100, actions_y)
            )

        # Battle log
        log_y = 450
        self.screen.blit(
            self.font.render("Battle Log:", True, (200, 200, 200)),
            (50, log_y)
        )

        for i, log_entry in enumerate(self.battle_system.battle_log[-5:]):
            self.screen.blit(
                self.small_font.render(log_entry, True, (180, 180, 180)),
                (50, log_y + 40 + i * 30)
            )

    def render_victory(self):
        """Render victory screen"""
        title = self.font.render("VICTORY!", True, (100, 255, 100))
        self.screen.blit(title, (self.WINDOW_WIDTH // 2 - 80, 250))

        instruction = self.small_font.render("Press SPACE for next battle", True, (200, 200, 200))
        self.screen.blit(instruction, (self.WINDOW_WIDTH // 2 - 150, 350))

    def render_defeat(self):
        """Render defeat screen"""
        title = self.font.render("DEFEAT...", True, (255, 100, 100))
        self.screen.blit(title, (self.WINDOW_WIDTH // 2 - 80, 250))

        instruction = self.small_font.render("Press SPACE to try again", True, (200, 200, 200))
        self.screen.blit(instruction, (self.WINDOW_WIDTH // 2 - 150, 350))

    def run(self):
        """Main game loop"""
        print("Starting Turn-Based RPG...")
        running = True

        while running:
            delta_time = self.clock.tick(self.FPS) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.start_battle()
                        elif self.state in [GameState.VICTORY, GameState.DEFEAT]:
                            self.start_battle()
                    elif event.key == pygame.K_1:
                        self.handle_player_action("attack")

            # Render
            self.render()

        pygame.quit()
        print("Thanks for playing!")


def main():
    """Main entry point"""
    game = RPGGame()
    game.run()


if __name__ == "__main__":
    main()
