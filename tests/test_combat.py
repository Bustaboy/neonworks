"""
Comprehensive tests for Combat System

Tests health, damage, combat stats, weapons, action points, and combat calculations.
"""

import pytest
from unittest.mock import Mock, patch
from engine.gameplay.combat import (
    Health,
    CombatStats,
    Weapon,
    ActionPoints,
    TeamComponent,
    Team,
    DamageType,
    DamageInstance,
    HealthSystem,
    CombatSystem,
)
from engine.core.ecs import World, Entity, Transform, GridPosition


@pytest.fixture
def world():
    """Create a test world"""
    return World()


@pytest.fixture
def health_system():
    """Create a health system"""
    return HealthSystem()


@pytest.fixture
def combat_system(health_system):
    """Create a combat system"""
    return CombatSystem(health_system)


class TestHealth:
    """Test Health component"""

    def test_health_creation(self):
        """Test creating health component"""
        health = Health(max_hp=100, hp=100)
        assert health.max_hp == 100
        assert health.hp == 100
        assert health.is_alive

    def test_health_defaults(self):
        """Test default health values"""
        health = Health()
        assert health.max_hp == 100
        assert health.hp == 100
        assert health.armor == 0
        assert health.is_alive

    def test_health_initialization(self):
        """Test health initializes to max if over"""
        health = Health(max_hp=50, hp=100)
        assert health.hp == 50

    def test_get_hp_percentage(self):
        """Test HP percentage calculation"""
        health = Health(max_hp=100, hp=75)
        assert health.get_hp_percentage() == 75.0

        health.hp = 50
        assert health.get_hp_percentage() == 50.0

    def test_is_full_health(self):
        """Test full health check"""
        health = Health(max_hp=100, hp=100)
        assert health.is_full_health()

        health.hp = 99
        assert not health.is_full_health()

    def test_is_critical(self):
        """Test critical health check (<25%)"""
        health = Health(max_hp=100, hp=24)
        assert health.is_critical()

        health.hp = 25
        assert not health.is_critical()


class TestCombatStats:
    """Test CombatStats component"""

    def test_stats_creation(self):
        """Test creating combat stats"""
        stats = CombatStats(body=8, reflexes=7, cool=6)
        assert stats.body == 8
        assert stats.reflexes == 7
        assert stats.cool == 6

    def test_stats_defaults(self):
        """Test default stat values"""
        stats = CombatStats()
        assert stats.body == 5
        assert stats.reflexes == 5
        assert stats.intelligence == 5
        assert stats.morale == 100

    def test_get_initiative_bonus(self):
        """Test initiative calculation"""
        stats = CombatStats(reflexes=8)
        assert stats.get_initiative_bonus() == 16

    def test_get_dodge_chance(self):
        """Test dodge chance calculation"""
        stats = CombatStats(reflexes=5)
        assert stats.get_dodge_chance() == 15.0

        # Test cap at 20
        stats.reflexes = 10
        assert stats.get_dodge_chance() == 20.0

    def test_get_crit_chance(self):
        """Test critical hit chance"""
        stats = CombatStats(cool=7)
        assert stats.get_crit_chance() == 14.0

    def test_get_morale_modifier(self):
        """Test morale damage modifier"""
        stats = CombatStats(morale=100)
        assert stats.get_morale_modifier() == 1.25

        stats.morale = 50
        assert stats.get_morale_modifier() == 1.0

        stats.morale = 0
        assert stats.get_morale_modifier() == 0.75

    def test_get_melee_damage_bonus(self):
        """Test melee damage bonus from body"""
        stats = CombatStats(body=8)
        assert stats.get_melee_damage_bonus() == 24.0

    def test_get_ranged_damage_bonus(self):
        """Test ranged damage bonus from reflexes"""
        stats = CombatStats(reflexes=7)
        assert stats.get_ranged_damage_bonus() == 14.0


class TestWeapon:
    """Test Weapon component"""

    def test_weapon_creation(self):
        """Test creating weapon"""
        weapon = Weapon(name="Pistol", damage=25, range=5, accuracy=80)
        assert weapon.name == "Pistol"
        assert weapon.damage == 25
        assert weapon.range == 5
        assert weapon.accuracy == 80

    def test_weapon_defaults(self):
        """Test default weapon values"""
        weapon = Weapon()
        assert weapon.name == "Unarmed"
        assert weapon.damage == 10
        assert weapon.accuracy == 75
        assert weapon.is_ranged

    def test_weapon_melee(self):
        """Test melee weapon"""
        weapon = Weapon(name="Sword", is_melee=True, is_ranged=False)
        assert weapon.is_melee
        assert not weapon.is_ranged

    def test_weapon_ammo(self):
        """Test weapon with ammo"""
        weapon = Weapon(has_ammo=True, ammo=30, max_ammo=30)
        assert weapon.has_ammo
        assert weapon.ammo == 30


class TestActionPoints:
    """Test ActionPoints component"""

    def test_ap_creation(self):
        """Test creating action points"""
        ap = ActionPoints(max_ap=5, ap=5)
        assert ap.max_ap == 5
        assert ap.ap == 5

    def test_ap_defaults(self):
        """Test default AP values"""
        ap = ActionPoints()
        assert ap.max_ap == 3
        assert ap.ap == 3

    def test_can_afford(self):
        """Test checking if can afford action"""
        ap = ActionPoints(ap=3)
        assert ap.can_afford(2)
        assert ap.can_afford(3)
        assert not ap.can_afford(4)

    def test_spend_ap(self):
        """Test spending AP"""
        ap = ActionPoints(ap=3)

        success = ap.spend(2)
        assert success
        assert ap.ap == 1
        assert ap.has_acted_this_turn

    def test_spend_insufficient_ap(self):
        """Test spending more AP than available"""
        ap = ActionPoints(ap=1)

        success = ap.spend(2)
        assert not success
        assert ap.ap == 1

    def test_refund_ap(self):
        """Test refunding AP"""
        ap = ActionPoints(max_ap=3, ap=1)

        ap.refund(1)
        assert ap.ap == 2

        # Test cap at max
        ap.refund(5)
        assert ap.ap == 3

    def test_reset_ap(self):
        """Test resetting AP"""
        ap = ActionPoints(max_ap=3, ap=0)
        ap.has_acted_this_turn = True

        ap.reset()
        assert ap.ap == 3
        assert not ap.has_acted_this_turn


class TestTeamComponent:
    """Test TeamComponent"""

    def test_team_creation(self):
        """Test creating team component"""
        team = TeamComponent(team=Team.PLAYER)
        assert team.team == Team.PLAYER

    def test_team_defaults(self):
        """Test default team values"""
        team = TeamComponent()
        assert team.team == Team.NEUTRAL
        assert not team.is_hostile_to_player

    def test_is_enemy_of_same_team(self):
        """Test same team not enemies"""
        player1 = TeamComponent(team=Team.PLAYER)
        player2 = TeamComponent(team=Team.PLAYER)

        assert not player1.is_enemy_of(player2)

    def test_is_enemy_of_different_teams(self):
        """Test player vs enemy"""
        player = TeamComponent(team=Team.PLAYER)
        enemy = TeamComponent(team=Team.ENEMY)

        assert player.is_enemy_of(enemy)
        assert enemy.is_enemy_of(player)

    def test_is_enemy_of_neutral(self):
        """Test neutral not enemies"""
        player = TeamComponent(team=Team.PLAYER)
        neutral = TeamComponent(team=Team.NEUTRAL)

        assert not player.is_enemy_of(neutral)
        assert not neutral.is_enemy_of(player)

    def test_friendly_fire(self):
        """Test friendly fire enabled"""
        player1 = TeamComponent(team=Team.PLAYER, is_friendly_fire_enabled=True)
        player2 = TeamComponent(team=Team.PLAYER)

        assert player1.is_enemy_of(player2)


class TestHealthSystem:
    """Test HealthSystem"""

    def test_health_system_creation(self):
        """Test creating health system"""
        system = HealthSystem()
        assert system.priority == 10

    def test_apply_damage(self, world, health_system):
        """Test applying damage"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=100, armor=0)
        entity.add_component(health)

        damage = DamageInstance(amount=30, damage_type=DamageType.PHYSICAL)
        dealt = health_system.apply_damage(entity, damage)

        assert dealt == 30
        assert health.hp == 70
        assert health.is_alive

    def test_apply_damage_with_armor(self, world, health_system):
        """Test damage with armor reduction"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=100, armor=50)  # 50% armor
        entity.add_component(health)

        damage = DamageInstance(amount=40, damage_type=DamageType.PHYSICAL)
        dealt = health_system.apply_damage(entity, damage)

        # Should deal 50% damage = 20
        assert dealt == 20
        assert health.hp == 80

    def test_apply_damage_armor_penetration(self, world, health_system):
        """Test armor penetration"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=100, armor=50)
        entity.add_component(health)

        # 50% armor pen
        damage = DamageInstance(
            amount=40, damage_type=DamageType.PHYSICAL, armor_penetration=0.5
        )
        dealt = health_system.apply_damage(entity, damage)

        # Effective armor = 50 * (1 - 0.5) = 25%
        # Damage = 40 * (1 - 0.25) = 30
        assert dealt == 30
        assert health.hp == 70

    def test_apply_damage_minimum(self, world, health_system):
        """Test minimum damage of 1"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=100, armor=99)  # 99% armor
        entity.add_component(health)

        damage = DamageInstance(amount=10, damage_type=DamageType.PHYSICAL)
        dealt = health_system.apply_damage(entity, damage)

        # Should deal at least 1 damage
        assert dealt >= 1
        assert health.hp < 100

    def test_apply_damage_kills(self, world, health_system):
        """Test damage kills entity"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=20)
        entity.add_component(health)

        damage = DamageInstance(amount=50, damage_type=DamageType.PHYSICAL)
        health_system.apply_damage(entity, damage)

        assert health.hp == 0
        assert not health.is_alive

    def test_apply_damage_invulnerable(self, world, health_system):
        """Test invulnerable entities take no damage"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=100, is_invulnerable=True)
        entity.add_component(health)

        damage = DamageInstance(amount=50, damage_type=DamageType.PHYSICAL)
        dealt = health_system.apply_damage(entity, damage)

        assert dealt == 0
        assert health.hp == 100

    def test_apply_damage_callback(self, world, health_system):
        """Test damage callback"""
        entity = world.create_entity()

        damage_taken = []
        health = Health(max_hp=100, hp=100)
        health.on_damage = lambda dmg, dtype: damage_taken.append(dmg)
        entity.add_component(health)

        damage = DamageInstance(amount=25, damage_type=DamageType.PHYSICAL)
        health_system.apply_damage(entity, damage)

        assert len(damage_taken) == 1
        assert damage_taken[0] == 25

    def test_apply_damage_morale_loss(self, world, health_system):
        """Test morale loss from high damage"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=100)
        stats = CombatStats(morale=100)
        entity.add_component(health)
        entity.add_component(stats)

        # 30% damage
        damage = DamageInstance(amount=30, damage_type=DamageType.PHYSICAL)
        health_system.apply_damage(entity, damage)

        # Should lose 20 morale
        assert stats.morale == 80

    def test_heal(self, world, health_system):
        """Test healing"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=50)
        entity.add_component(health)

        healed = health_system.heal(entity, 30)

        assert healed == 30
        assert health.hp == 80

    def test_heal_caps_at_max(self, world, health_system):
        """Test healing caps at max HP"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=90)
        entity.add_component(health)

        healed = health_system.heal(entity, 30)

        assert healed == 10
        assert health.hp == 100

    def test_heal_callback(self, world, health_system):
        """Test heal callback"""
        entity = world.create_entity()

        heals_received = []
        health = Health(max_hp=100, hp=50)
        health.on_heal = lambda amount: heals_received.append(amount)
        entity.add_component(health)

        health_system.heal(entity, 20)

        assert len(heals_received) == 1
        assert heals_received[0] == 20

    def test_kill(self, world, health_system):
        """Test killing entity"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=50)
        entity.add_component(health)

        health_system.kill(entity)

        assert health.hp == 0
        assert not health.is_alive

    def test_kill_callback(self, world, health_system):
        """Test death callback"""
        entity = world.create_entity()

        deaths = []
        health = Health(max_hp=100, hp=50)
        health.on_death = lambda: deaths.append(True)
        entity.add_component(health)

        health_system.kill(entity)

        assert len(deaths) == 1

    def test_revive(self, world, health_system):
        """Test reviving entity"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=0, is_alive=False)
        entity.add_component(health)

        health_system.revive(entity)

        assert health.hp == 100
        assert health.is_alive

    def test_revive_partial_hp(self, world, health_system):
        """Test reviving with partial HP"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=0, is_alive=False)
        entity.add_component(health)

        health_system.revive(entity, hp=50)

        assert health.hp == 50
        assert health.is_alive

    def test_regeneration(self, world, health_system):
        """Test health regeneration over time"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=50, regeneration_rate=10)  # 10 HP/sec
        entity.add_component(health)

        # Update for 1 second
        health_system.update(world, 1.0)

        assert health.hp == 60

    def test_regeneration_stops_at_max(self, world, health_system):
        """Test regeneration stops at max HP"""
        entity = world.create_entity()
        health = Health(max_hp=100, hp=95, regeneration_rate=10)
        entity.add_component(health)

        health_system.update(world, 1.0)

        assert health.hp == 100


class TestCombatSystem:
    """Test CombatSystem"""

    def test_combat_system_creation(self):
        """Test creating combat system"""
        system = CombatSystem()
        assert system.priority == 9

    def test_calculate_hit_chance_basic(self, world, combat_system):
        """Test basic hit chance calculation"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(accuracy=80)
        attacker.add_component(weapon)

        target_stats = CombatStats(reflexes=5)  # 15% dodge
        target.add_component(target_stats)

        hit_chance = combat_system.calculate_hit_chance(attacker, target)

        # 80 - 15 = 65
        assert hit_chance == 65

    def test_calculate_hit_chance_clamped(self, world, combat_system):
        """Test hit chance clamped to 5-95%"""
        attacker = world.create_entity()
        target = world.create_entity()

        # Very high accuracy
        weapon = Weapon(accuracy=200)
        attacker.add_component(weapon)

        target_stats = CombatStats(reflexes=0)
        target.add_component(target_stats)

        hit_chance = combat_system.calculate_hit_chance(attacker, target)
        assert hit_chance == 95  # Capped at 95

        # Very low accuracy
        weapon.accuracy = 0
        hit_chance = combat_system.calculate_hit_chance(attacker, target)
        assert hit_chance == 5  # Capped at 5

    def test_calculate_damage_basic(self, world, combat_system):
        """Test basic damage calculation"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(damage=50, damage_variance_min=1.0, damage_variance_max=1.0)
        attacker.add_component(weapon)

        stats = CombatStats(reflexes=5, morale=50)  # No bonus
        attacker.add_component(stats)

        with patch("random.uniform", return_value=1.0):
            with patch("random.randint", return_value=100):  # No crit
                damage, is_crit = combat_system.calculate_damage(attacker, target)

        # 50 base + 10 reflex bonus = 60
        assert damage == 60
        assert not is_crit

    def test_calculate_damage_melee_bonus(self, world, combat_system):
        """Test melee damage bonus from body"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(
            damage=20,
            is_melee=True,
            is_ranged=False,
            damage_variance_min=1.0,
            damage_variance_max=1.0,
        )
        attacker.add_component(weapon)

        stats = CombatStats(body=8, morale=50)
        attacker.add_component(stats)

        with patch("random.uniform", return_value=1.0):
            with patch("random.randint", return_value=100):  # No crit
                damage, _ = combat_system.calculate_damage(attacker, target)

        # 20 base + 24 body bonus = 44
        assert damage == 44

    def test_calculate_damage_critical(self, world, combat_system):
        """Test critical hit damage"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(
            damage=50,
            crit_multiplier=2.0,
            damage_variance_min=1.0,
            damage_variance_max=1.0,
        )
        attacker.add_component(weapon)

        stats = CombatStats(reflexes=5, cool=10, morale=50)
        attacker.add_component(stats)

        # Force critical hit
        with patch("random.uniform", return_value=1.0):  # variance
            with patch(
                "random.randint", return_value=1
            ):  # Guarantee crit (roll 1, crit chance 20%)
                damage, is_crit = combat_system.calculate_damage(attacker, target)

        # (50 + 10) * 2.0 = 120
        assert damage == 120
        assert is_crit

    def test_perform_attack_hit(self, world, combat_system, health_system):
        """Test successful attack"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(
            damage=30, accuracy=100, damage_variance_min=1.0, damage_variance_max=1.0
        )
        attacker.add_component(weapon)

        stats = CombatStats(reflexes=0, morale=50)
        attacker.add_component(stats)

        health = Health(max_hp=100, hp=100, armor=0)
        target.add_component(health)

        # Force hit, no crit
        with patch("random.uniform", return_value=1.0):  # Hit roll
            with patch("random.randint", return_value=100):  # No crit
                result = combat_system.perform_attack(attacker, target)

        assert result["hit"]
        assert result["damage"] == 30
        assert health.hp == 70

    def test_perform_attack_miss(self, world, combat_system):
        """Test missed attack"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(damage=30, accuracy=50)
        attacker.add_component(weapon)

        health = Health(max_hp=100, hp=100)
        target.add_component(health)

        # Force miss
        with patch("random.uniform", return_value=99.0):
            result = combat_system.perform_attack(attacker, target)

        assert not result["hit"]
        assert result["damage"] == 0
        assert health.hp == 100

    def test_perform_attack_no_ammo(self, world, combat_system):
        """Test attack with no ammo"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(has_ammo=True, ammo=0, max_ammo=10)
        attacker.add_component(weapon)

        health = Health(max_hp=100, hp=100)
        target.add_component(health)

        result = combat_system.perform_attack(attacker, target)

        assert not result["hit"]
        assert "ammo" in result["message"].lower()

    def test_perform_attack_consumes_ammo(self, world, combat_system):
        """Test attack consumes ammo"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(has_ammo=True, ammo=10, max_ammo=10, accuracy=100)
        attacker.add_component(weapon)

        health = Health(max_hp=100, hp=100)
        target.add_component(health)

        with patch("random.uniform", return_value=1.0):
            combat_system.perform_attack(attacker, target)

        assert weapon.ammo == 9

    def test_perform_attack_dead_target(self, world, combat_system):
        """Test attack on dead target"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(damage=30)
        attacker.add_component(weapon)

        health = Health(max_hp=100, hp=0, is_alive=False)
        target.add_component(health)

        result = combat_system.perform_attack(attacker, target)

        assert not result["hit"]
        assert "dead" in result["message"].lower()

    def test_check_range_grid(self, world, combat_system):
        """Test range check with grid positions"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(range=5)
        attacker.add_component(weapon)

        attacker_pos = GridPosition(grid_x=0, grid_y=0)
        target_pos = GridPosition(grid_x=3, grid_y=2)
        attacker.add_component(attacker_pos)
        target.add_component(target_pos)

        in_range, distance = combat_system.check_range(attacker, target, world)

        # Manhattan distance = 3 + 2 = 5
        assert distance == 5
        assert in_range

    def test_check_range_out_of_range(self, world, combat_system):
        """Test out of range check"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(range=3)
        attacker.add_component(weapon)

        attacker_pos = GridPosition(grid_x=0, grid_y=0)
        target_pos = GridPosition(grid_x=5, grid_y=5)
        attacker.add_component(attacker_pos)
        target.add_component(target_pos)

        in_range, distance = combat_system.check_range(attacker, target, world)

        assert distance == 10
        assert not in_range

    def test_check_range_continuous(self, world, combat_system):
        """Test range check with continuous positions"""
        attacker = world.create_entity()
        target = world.create_entity()

        weapon = Weapon(range=100)
        attacker.add_component(weapon)

        attacker_pos = Transform(x=0, y=0)
        target_pos = Transform(x=60, y=80)
        attacker.add_component(attacker_pos)
        target.add_component(target_pos)

        in_range, distance = combat_system.check_range(attacker, target, world)

        # Euclidean distance = sqrt(60^2 + 80^2) = 100
        assert distance == 100
        assert in_range

    def test_combat_log(self, combat_system):
        """Test combat logging"""
        combat_system.add_log("Player attacks!")
        combat_system.add_log("Enemy takes damage!")

        log = combat_system.get_log()
        assert len(log) == 2
        assert "Player attacks!" in log
        assert "Enemy takes damage!" in log

    def test_combat_log_max_size(self, combat_system):
        """Test combat log max size"""
        for i in range(60):
            combat_system.add_log(f"Message {i}")

        log = combat_system.get_log()
        assert len(log) == 50  # Max size

    def test_combat_log_clear(self, combat_system):
        """Test clearing combat log"""
        combat_system.add_log("Message")
        combat_system.clear_log()

        log = combat_system.get_log()
        assert len(log) == 0


# Run tests with: pytest engine/tests/test_combat.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
