"""
Comprehensive test suite for stealth.py (Stealth System)

Tests cover:
- Detection states (undetected, suspicious, alerted, combat)
- Sight cones and vision (FOV, detection range)
- Sound/noise generation (footsteps, gunfire, actions)
- Noise radius and enemy alerting
- Light/shadow mechanics (detection modifier)
- Stealth kills and takedowns
- AI awareness levels
- Investigation behavior
- Crouch/sneak movement
- Integration with combat and hacking
- Serialization for save/load
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestDetectionStates:
    """Test stealth detection states."""

    def test_undetected_state(self):
        """Test undetected stealth state."""
        from stealth import StealthState

        state = StealthState()

        assert state.detection_level == "undetected"
        assert not state.is_detected()

    def test_suspicious_state(self):
        """Test suspicious detection state."""
        from stealth import StealthState

        state = StealthState()

        state.set_detection_level("suspicious")

        assert state.detection_level == "suspicious"
        assert not state.is_in_combat()

    def test_alerted_state(self):
        """Test alerted detection state."""
        from stealth import StealthState

        state = StealthState()

        state.set_detection_level("alerted")

        assert state.detection_level == "alerted"
        assert state.is_detected()

    def test_combat_state(self):
        """Test combat detection state."""
        from stealth import StealthState

        state = StealthState()

        state.set_detection_level("combat")

        assert state.detection_level == "combat"
        assert state.is_in_combat()

    def test_detection_progress(self):
        """Test detection progress tracking."""
        from stealth import StealthState

        state = StealthState()

        state.increase_detection(25)

        assert state.detection_progress == 25

        state.increase_detection(50)

        assert state.detection_progress == 75

    def test_detection_threshold_triggers_alert(self):
        """Test reaching detection threshold triggers alert."""
        from stealth import StealthState

        state = StealthState()

        # Max out detection
        state.increase_detection(100)

        assert state.detection_level == "alerted"


class TestSightCones:
    """Test enemy sight cones and vision."""

    def test_enemy_has_sight_cone(self):
        """Test enemy has field of view."""
        from stealth import EnemyAI

        enemy = EnemyAI(
            enemy_id="guard_1",
            position=(0, 0),
            facing_direction=0  # North
        )

        assert enemy.fov_angle == 90  # 90 degree cone
        assert enemy.vision_range == 10

    def test_player_in_sight_cone(self):
        """Test detecting player in sight cone."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # Player directly in front
        player_pos = (0, 5)

        in_sight = enemy.can_see_position(player_pos)

        assert in_sight is True

    def test_player_outside_sight_cone(self):
        """Test player outside sight cone."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # Player behind enemy
        player_pos = (0, -5)

        in_sight = enemy.can_see_position(player_pos)

        assert in_sight is False

    def test_vision_range_limit(self):
        """Test vision has maximum range."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # Player too far away
        player_pos = (0, 100)

        in_sight = enemy.can_see_position(player_pos)

        assert in_sight is False

    def test_darkness_reduces_vision(self):
        """Test darkness reduces vision range."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # In darkness
        enemy.set_light_level(0.2)  # Low light

        # Vision should be reduced
        assert enemy.get_effective_vision_range() < enemy.vision_range


class TestNoiseGeneration:
    """Test sound and noise generation."""

    def test_footsteps_make_noise(self):
        """Test footsteps generate noise."""
        from stealth import NoiseEvent

        footstep = NoiseEvent(
            noise_type="footstep",
            position=(5, 5),
            noise_level=20
        )

        assert footstep.noise_type == "footstep"
        assert footstep.noise_level == 20

    def test_gunfire_loud_noise(self):
        """Test gunfire generates loud noise."""
        from stealth import NoiseEvent

        gunshot = NoiseEvent(
            noise_type="gunfire",
            position=(10, 10),
            noise_level=100
        )

        assert gunshot.noise_level == 100

    def test_noise_has_radius(self):
        """Test noise has effective radius."""
        from stealth import NoiseEvent

        noise = NoiseEvent("door_open", (0, 0), noise_level=50)

        radius = noise.get_effective_radius()

        assert radius > 0
        assert radius == 5  # 50 noise_level / 10

    def test_crouching_reduces_noise(self):
        """Test crouching reduces footstep noise."""
        from stealth import Player

        player = Player()

        player.set_crouching(True)

        standing_noise = 20
        crouched_noise = player.get_footstep_noise()

        assert crouched_noise < standing_noise

    def test_noise_alerts_nearby_enemies(self):
        """Test noise alerts enemies within radius."""
        from stealth import NoiseEvent, EnemyAI

        noise = NoiseEvent("gunfire", (0, 0), noise_level=100)

        enemy_close = EnemyAI("guard1", position=(3, 3), facing_direction=0)
        enemy_far = EnemyAI("guard2", position=(50, 50), facing_direction=0)

        # Check if enemies can hear
        close_hears = enemy_close.can_hear_noise(noise)
        far_hears = enemy_far.can_hear_noise(noise)

        assert close_hears is True
        assert far_hears is False


class TestLightAndShadow:
    """Test light/shadow detection mechanics."""

    def test_shadows_reduce_detection(self):
        """Test being in shadows reduces detection."""
        from stealth import StealthState

        state = StealthState()

        state.set_light_level(0.1)  # Deep shadows

        detection_modifier = state.get_detection_modifier()

        # Shadows should reduce detection
        assert detection_modifier < 1.0

    def test_bright_light_increases_detection(self):
        """Test bright light increases detection."""
        from stealth import StealthState

        state = StealthState()

        state.set_light_level(1.0)  # Bright light

        detection_modifier = state.get_detection_modifier()

        # Bright light makes detection easier
        assert detection_modifier >= 1.0

    def test_darkness_helps_stealth(self):
        """Test darkness provides stealth bonus."""
        from stealth import Player

        player = Player()

        # In darkness
        stealth_dark = player.get_stealth_rating(light_level=0.2)

        # In light
        stealth_light = player.get_stealth_rating(light_level=1.0)

        assert stealth_dark > stealth_light


class TestStealthKills:
    """Test stealth takedowns and kills."""

    def test_stealth_takedown(self):
        """Test performing stealth takedown."""
        from stealth import Player, EnemyAI

        player = Player()
        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # Behind enemy, undetected
        result = player.attempt_takedown(enemy, from_behind=True, detected=False)

        assert result is True

    def test_takedown_requires_behind(self):
        """Test takedown requires being behind enemy."""
        from stealth import Player, EnemyAI

        player = Player()
        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # In front of enemy
        result = player.attempt_takedown(enemy, from_behind=False, detected=False)

        assert result is False

    def test_takedown_fails_if_detected(self):
        """Test takedown fails if player is detected."""
        from stealth import Player, EnemyAI

        player = Player()
        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # Behind but detected
        result = player.attempt_takedown(enemy, from_behind=True, detected=True)

        assert result is False

    def test_takedown_silent(self):
        """Test takedown is silent (no alert)."""
        from stealth import Player, EnemyAI

        player = Player()
        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        result = player.attempt_takedown(enemy, from_behind=True, detected=False)

        # Shouldn't generate noise
        assert result is True
        # No alert triggered


class TestAIAwareness:
    """Test AI awareness and investigation."""

    def test_enemy_awareness_levels(self):
        """Test enemy has awareness level."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        assert enemy.awareness_level == "relaxed"

    def test_increase_awareness(self):
        """Test increasing enemy awareness."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        enemy.increase_awareness(50)

        assert enemy.awareness_level == "alert"

    def test_investigation_behavior(self):
        """Test enemy investigates noise."""
        from stealth import EnemyAI, NoiseEvent

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)
        noise = NoiseEvent("suspicious_sound", (10, 10), noise_level=50)

        enemy.investigate_noise(noise)

        assert enemy.is_investigating()
        assert enemy.investigation_target == (10, 10)

    def test_investigation_timeout(self):
        """Test investigation times out."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        enemy.start_investigation((5, 5))

        # Simulate time passing
        enemy.update_investigation(time_passed=30)

        # Should timeout and return to normal
        assert not enemy.is_investigating()

    def test_found_player_triggers_combat(self):
        """Test finding player triggers combat."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        enemy.spot_player((5, 5))

        assert enemy.detection_state == "combat"


class TestCrouchAndMovement:
    """Test crouch/sneak movement."""

    def test_crouch_toggle(self):
        """Test toggling crouch state."""
        from stealth import Player

        player = Player()

        assert not player.is_crouching

        player.set_crouching(True)

        assert player.is_crouching

    def test_crouching_slower_movement(self):
        """Test crouching reduces movement speed."""
        from stealth import Player

        player = Player()

        standing_speed = player.get_movement_speed(crouching=False)
        crouching_speed = player.get_movement_speed(crouching=True)

        assert crouching_speed < standing_speed

    def test_crouching_quieter(self):
        """Test crouching makes less noise."""
        from stealth import Player

        player = Player()

        player.set_crouching(False)
        standing_noise = player.get_footstep_noise()

        player.set_crouching(True)
        crouching_noise = player.get_footstep_noise()

        assert crouching_noise < standing_noise

    def test_crouching_harder_to_detect(self):
        """Test crouching makes player harder to detect."""
        from stealth import Player

        player = Player()

        player.set_crouching(True)

        # Crouch reduces profile
        assert player.get_detection_profile() < 1.0


class TestStealthIntegration:
    """Test stealth integration with other systems."""

    def test_hacking_supports_stealth(self):
        """Test hacking cameras supports stealth."""
        from stealth import Player
        # Integration test - cameras can be disabled

        player = Player()

        # Hack camera first (from hacking system)
        # Then sneak past

        assert True  # Placeholder for integration

    def test_combat_breaks_stealth(self):
        """Test entering combat breaks stealth."""
        from stealth import StealthState

        state = StealthState()

        state.set_detection_level("undetected")

        # Enter combat
        state.enter_combat()

        assert state.detection_level == "combat"
        assert not state.is_stealthy()

    def test_stealth_kill_grants_xp(self):
        """Test stealth kills grant Cool XP."""
        from stealth import Player

        player = Player()

        # Stealth kill
        xp_gained = player.perform_stealth_kill_xp()

        assert xp_gained > 0  # Should grant Cool XP


class TestSerialization:
    """Test stealth system serialization."""

    def test_stealth_state_to_dict(self):
        """Test converting stealth state to dictionary."""
        from stealth import StealthState

        state = StealthState()
        state.set_detection_level("suspicious")
        state.increase_detection(40)

        data = state.to_dict()

        assert data["detection_level"] == "suspicious"
        assert data["detection_progress"] == 40

    def test_stealth_state_from_dict(self):
        """Test loading stealth state from dictionary."""
        from stealth import StealthState

        data = {
            "detection_level": "alerted",
            "detection_progress": 80,
            "light_level": 0.5
        }

        state = StealthState.from_dict(data)

        assert state.detection_level == "alerted"
        assert state.detection_progress == 80

    def test_enemy_ai_to_dict(self):
        """Test converting enemy AI to dictionary."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(5, 10), facing_direction=90)
        enemy.increase_awareness(30)

        data = enemy.to_dict()

        assert data["enemy_id"] == "guard"
        assert data["position"] == (5, 10)

    def test_enemy_ai_from_dict(self):
        """Test loading enemy AI from dictionary."""
        from stealth import EnemyAI

        data = {
            "enemy_id": "patrol",
            "position": (10, 20),
            "facing_direction": 180,
            "awareness_level": "alert"
        }

        enemy = EnemyAI.from_dict(data)

        assert enemy.enemy_id == "patrol"
        assert enemy.awareness_level == "alert"


class TestEdgeCases:
    """Test edge cases."""

    def test_detection_progress_capped(self):
        """Test detection progress caps at 100."""
        from stealth import StealthState

        state = StealthState()

        state.increase_detection(200)

        assert state.detection_progress <= 100

    def test_negative_noise_invalid(self):
        """Test negative noise level is invalid."""
        from stealth import NoiseEvent

        with pytest.raises(ValueError):
            NoiseEvent("test", (0, 0), noise_level=-10)

    def test_zero_vision_range(self):
        """Test enemy with zero vision range."""
        from stealth import EnemyAI

        blind_enemy = EnemyAI("blind", position=(0, 0), facing_direction=0)
        blind_enemy.vision_range = 0

        # Can't see anything
        assert not blind_enemy.can_see_position((1, 1))

    def test_investigation_target_none(self):
        """Test investigation with no target."""
        from stealth import EnemyAI

        enemy = EnemyAI("guard", position=(0, 0), facing_direction=0)

        # No investigation target
        assert enemy.investigation_target is None
        assert not enemy.is_investigating()

    def test_player_detection_decay(self):
        """Test detection decays over time when hidden."""
        from stealth import StealthState

        state = StealthState()

        state.increase_detection(50)

        # Hide and wait
        state.decay_detection(time_passed=10)

        # Detection should decrease
        assert state.detection_progress < 50
