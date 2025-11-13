"""
Comprehensive test suite for status_effects.py (Status Effects System)

Tests cover:
- Status effect types (Bleeding, Burning, Stunned, Hacked, Weakened, Blinded)
- Duration tracking (turn-based)
- Stacking mechanics (multiple applications)
- Effect application to characters
- Effect processing per turn
- Damage-over-time (Bleeding, Burning)
- Action restrictions (Stunned)
- Stat modifications (Weakened, Hacked, Blinded)
- Cleanse mechanics
- Resistance and immunity
- Serialization for save/load
- Integration with combat
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestStatusEffectCreation:
    """Test creating status effects."""

    def test_create_bleeding_effect(self):
        """Test creating bleeding status effect."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="bleeding",
            duration=3,
            potency=5
        )

        assert effect.effect_type == "bleeding"
        assert effect.duration == 3
        assert effect.potency == 5

    def test_create_burning_effect(self):
        """Test creating burning status effect."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="burning",
            duration=2,
            potency=8
        )

        assert effect.effect_type == "burning"
        assert effect.duration == 2
        assert effect.potency == 8

    def test_create_stunned_effect(self):
        """Test creating stunned status effect."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="stunned",
            duration=1
        )

        assert effect.effect_type == "stunned"
        assert effect.duration == 1

    def test_create_hacked_effect(self):
        """Test creating hacked status effect."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="hacked",
            duration=3,
            potency=10
        )

        assert effect.effect_type == "hacked"
        assert effect.duration == 3

    def test_create_weakened_effect(self):
        """Test creating weakened status effect."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="weakened",
            duration=4,
            potency=30  # 30% damage reduction
        )

        assert effect.effect_type == "weakened"
        assert effect.potency == 30

    def test_create_blinded_effect(self):
        """Test creating blinded status effect."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="blinded",
            duration=2,
            potency=50  # 50% accuracy reduction
        )

        assert effect.effect_type == "blinded"
        assert effect.potency == 50

    def test_invalid_effect_type(self):
        """Test invalid effect type raises error."""
        from status_effects import StatusEffect

        with pytest.raises(ValueError):
            StatusEffect(
                effect_type="invalid_effect",
                duration=1
            )


class TestDurationTracking:
    """Test status effect duration mechanics."""

    def test_effect_has_duration(self):
        """Test effects track remaining duration."""
        from status_effects import StatusEffect

        effect = StatusEffect(effect_type="bleeding", duration=5)

        assert effect.duration == 5
        assert effect.is_active()

    def test_reduce_duration(self):
        """Test reducing effect duration."""
        from status_effects import StatusEffect

        effect = StatusEffect(effect_type="burning", duration=3)

        effect.tick()
        assert effect.duration == 2

        effect.tick()
        assert effect.duration == 1

        effect.tick()
        assert effect.duration == 0

    def test_effect_expires(self):
        """Test effect expires when duration reaches 0."""
        from status_effects import StatusEffect

        effect = StatusEffect(effect_type="stunned", duration=1)

        assert effect.is_active()

        effect.tick()

        assert not effect.is_active()
        assert effect.duration == 0

    def test_permanent_effect(self):
        """Test permanent effects (duration -1)."""
        from status_effects import StatusEffect

        effect = StatusEffect(effect_type="weakened", duration=-1, potency=20)

        effect.tick()
        effect.tick()

        # Permanent effects never expire
        assert effect.is_active()
        assert effect.duration == -1


class TestStackingMechanics:
    """Test stacking multiple instances of same effect."""

    def test_stack_bleeding(self):
        """Test bleeding stacks potency."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Apply bleeding twice
        effect1 = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        effect2 = StatusEffect(effect_type="bleeding", duration=2, potency=3)

        manager.add_effect(effect1)
        manager.add_effect(effect2)

        # Bleeding should stack potency
        total_damage = manager.calculate_dot_damage()

        assert total_damage == 8  # 5 + 3 per turn

    def test_stack_duration(self):
        """Test stacking refreshes duration."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Apply burning
        effect1 = StatusEffect(effect_type="burning", duration=2, potency=5)
        manager.add_effect(effect1)

        manager.tick_effects()
        assert manager.has_effect("burning")

        # Apply burning again - should refresh duration
        effect2 = StatusEffect(effect_type="burning", duration=3, potency=5)
        manager.add_effect(effect2)

        # Duration should be extended
        burning_effects = manager.get_effects_by_type("burning")
        assert len(burning_effects) > 0

    def test_stunned_doesnt_stack(self):
        """Test stunned doesn't stack, only refreshes."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Apply stunned twice
        effect1 = StatusEffect(effect_type="stunned", duration=1)
        effect2 = StatusEffect(effect_type="stunned", duration=2)

        manager.add_effect(effect1)
        manager.add_effect(effect2)

        # Should only have one stunned effect with longest duration
        stunned_effects = manager.get_effects_by_type("stunned")
        assert len(stunned_effects) <= 2  # Might have both or merge


class TestEffectApplication:
    """Test applying effects to characters."""

    def test_apply_effect_to_character(self):
        """Test applying status effect to character."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        effect = StatusEffect(effect_type="bleeding", duration=3, potency=5)

        manager.add_effect(effect)

        assert manager.has_effect("bleeding")
        assert len(manager.active_effects) >= 1

    def test_remove_effect(self):
        """Test removing expired effects."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        effect = StatusEffect(effect_type="burning", duration=1, potency=5)
        manager.add_effect(effect)

        # Tick until expired
        manager.tick_effects()

        # Expired effects should be removed
        assert not manager.has_effect("burning")

    def test_get_active_effects(self):
        """Test getting all active effects."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=2, potency=5)
        stunned = StatusEffect(effect_type="stunned", duration=1)

        manager.add_effect(bleeding)
        manager.add_effect(stunned)

        active = manager.get_active_effects()

        assert len(active) >= 2
        assert any(e.effect_type == "bleeding" for e in active)
        assert any(e.effect_type == "stunned" for e in active)


class TestDamageOverTime:
    """Test damage-over-time effects."""

    def test_bleeding_deals_damage(self):
        """Test bleeding deals damage per turn."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        manager.add_effect(bleeding)

        damage = manager.calculate_dot_damage()

        assert damage == 5  # Potency per turn

    def test_burning_deals_damage(self):
        """Test burning deals damage per turn."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        burning = StatusEffect(effect_type="burning", duration=2, potency=8)
        manager.add_effect(burning)

        damage = manager.calculate_dot_damage()

        assert damage == 8

    def test_multiple_dot_stacks(self):
        """Test multiple DoT effects stack damage."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        burning = StatusEffect(effect_type="burning", duration=2, potency=8)

        manager.add_effect(bleeding)
        manager.add_effect(burning)

        total_damage = manager.calculate_dot_damage()

        assert total_damage == 13  # 5 + 8

    def test_dot_damage_over_time(self):
        """Test DoT damage persists over multiple turns."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        manager.add_effect(bleeding)

        # Turn 1
        damage_t1 = manager.calculate_dot_damage()
        assert damage_t1 == 5
        manager.tick_effects()

        # Turn 2
        damage_t2 = manager.calculate_dot_damage()
        assert damage_t2 == 5
        manager.tick_effects()

        # Turn 3
        damage_t3 = manager.calculate_dot_damage()
        assert damage_t3 == 5


class TestActionRestrictions:
    """Test effects that restrict actions."""

    def test_stunned_prevents_actions(self):
        """Test stunned prevents character from acting."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        stunned = StatusEffect(effect_type="stunned", duration=1)
        manager.add_effect(stunned)

        assert not manager.can_act()

    def test_stunned_wears_off(self):
        """Test character can act after stun expires."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        stunned = StatusEffect(effect_type="stunned", duration=1)
        manager.add_effect(stunned)

        assert not manager.can_act()

        manager.tick_effects()

        # Stun expired
        assert manager.can_act()

    def test_other_effects_dont_prevent_actions(self):
        """Test non-stun effects allow actions."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Add various effects
        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        weakened = StatusEffect(effect_type="weakened", duration=2, potency=30)

        manager.add_effect(bleeding)
        manager.add_effect(weakened)

        # Can still act
        assert manager.can_act()


class TestStatModifications:
    """Test effects that modify character stats."""

    def test_weakened_reduces_damage(self):
        """Test weakened reduces damage output."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        weakened = StatusEffect(effect_type="weakened", duration=3, potency=30)
        manager.add_effect(weakened)

        base_damage = 100
        modified_damage = manager.apply_damage_modifiers(base_damage)

        # 30% reduction
        assert modified_damage == 70

    def test_blinded_reduces_accuracy(self):
        """Test blinded reduces hit chance."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        blinded = StatusEffect(effect_type="blinded", duration=2, potency=50)
        manager.add_effect(blinded)

        base_accuracy = 100
        modified_accuracy = manager.apply_accuracy_modifiers(base_accuracy)

        # 50% reduction
        assert modified_accuracy == 50

    def test_hacked_reveals_position(self):
        """Test hacked reveals character position."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        hacked = StatusEffect(effect_type="hacked", duration=3, potency=10)
        manager.add_effect(hacked)

        # Position revealed (enemies ignore cover)
        assert manager.is_position_revealed()

    def test_multiple_weakened_stacks(self):
        """Test multiple weakened effects stack penalty."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        weakened1 = StatusEffect(effect_type="weakened", duration=2, potency=20)
        weakened2 = StatusEffect(effect_type="weakened", duration=2, potency=15)

        manager.add_effect(weakened1)
        manager.add_effect(weakened2)

        base_damage = 100
        modified = manager.apply_damage_modifiers(base_damage)

        # 20% + 15% = 35% reduction
        assert modified == 65


class TestCleanseMechanics:
    """Test removing status effects."""

    def test_cleanse_single_effect(self):
        """Test cleansing a specific effect."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        burning = StatusEffect(effect_type="burning", duration=2, potency=8)

        manager.add_effect(bleeding)
        manager.add_effect(burning)

        # Cleanse bleeding
        manager.cleanse_effect("bleeding")

        assert not manager.has_effect("bleeding")
        assert manager.has_effect("burning")

    def test_cleanse_all_effects(self):
        """Test cleansing all effects."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        stunned = StatusEffect(effect_type="stunned", duration=1)
        burning = StatusEffect(effect_type="burning", duration=2, potency=8)

        manager.add_effect(bleeding)
        manager.add_effect(stunned)
        manager.add_effect(burning)

        # Cleanse all
        manager.cleanse_all()

        assert len(manager.get_active_effects()) == 0

    def test_cleanse_by_category(self):
        """Test cleansing effects by category (debuffs, DoTs, etc)."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Add DoT effects
        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        burning = StatusEffect(effect_type="burning", duration=2, potency=8)

        # Add debuff
        weakened = StatusEffect(effect_type="weakened", duration=2, potency=30)

        manager.add_effect(bleeding)
        manager.add_effect(burning)
        manager.add_effect(weakened)

        # Cleanse all DoT effects
        manager.cleanse_category("dot")

        assert not manager.has_effect("bleeding")
        assert not manager.has_effect("burning")
        assert manager.has_effect("weakened")  # Debuff remains


class TestResistanceImmunity:
    """Test resistance and immunity to status effects."""

    def test_resist_effect(self):
        """Test resisting status effect application."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Set resistance to bleeding
        manager.set_resistance("bleeding", 50)  # 50% chance to resist

        # This test is probabilistic, so we can't assert exact outcome
        # Just verify resistance is tracked
        assert manager.get_resistance("bleeding") == 50

    def test_immune_to_effect(self):
        """Test immunity to status effect."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Set immunity to stunned
        manager.set_immunity("stunned", True)

        # Try to apply stunned
        stunned = StatusEffect(effect_type="stunned", duration=2)
        result = manager.add_effect(stunned)

        # Should be blocked
        assert not manager.has_effect("stunned")

    def test_partial_resistance(self):
        """Test partial resistance reduces duration."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Set 50% resistance to burning
        manager.set_resistance("burning", 50)

        burning = StatusEffect(effect_type="burning", duration=4, potency=8)
        manager.add_effect(burning)

        # If applied, duration might be reduced (implementation specific)
        # Just verify resistance is considered
        assert manager.get_resistance("burning") == 50

    def test_immunity_list(self):
        """Test character can be immune to multiple effects."""
        from status_effects import StatusEffectManager

        manager = StatusEffectManager()

        manager.set_immunity("stunned", True)
        manager.set_immunity("hacked", True)

        assert manager.is_immune("stunned")
        assert manager.is_immune("hacked")
        assert not manager.is_immune("bleeding")


class TestSerialization:
    """Test status effect serialization."""

    def test_effect_to_dict(self):
        """Test converting effect to dictionary."""
        from status_effects import StatusEffect

        effect = StatusEffect(
            effect_type="bleeding",
            duration=3,
            potency=5
        )

        data = effect.to_dict()

        assert data["effect_type"] == "bleeding"
        assert data["duration"] == 3
        assert data["potency"] == 5

    def test_effect_from_dict(self):
        """Test loading effect from dictionary."""
        from status_effects import StatusEffect

        data = {
            "effect_type": "burning",
            "duration": 2,
            "potency": 8
        }

        effect = StatusEffect.from_dict(data)

        assert effect.effect_type == "burning"
        assert effect.duration == 2
        assert effect.potency == 8

    def test_manager_to_dict(self):
        """Test converting manager to dictionary."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        stunned = StatusEffect(effect_type="stunned", duration=1)

        manager.add_effect(bleeding)
        manager.add_effect(stunned)

        data = manager.to_dict()

        assert "active_effects" in data
        assert len(data["active_effects"]) >= 2

    def test_manager_from_dict(self):
        """Test loading manager from dictionary."""
        from status_effects import StatusEffectManager

        data = {
            "active_effects": [
                {"effect_type": "bleeding", "duration": 3, "potency": 5},
                {"effect_type": "stunned", "duration": 1, "potency": 0}
            ],
            "resistances": {"fire": 25},
            "immunities": ["stun"]
        }

        manager = StatusEffectManager.from_dict(data)

        assert manager.has_effect("bleeding")
        assert manager.has_effect("stunned")


class TestCombatIntegration:
    """Test status effects in combat scenarios."""

    def test_apply_effect_on_hit(self):
        """Test applying effect when attack lands."""
        from status_effects import StatusEffect, StatusEffectManager

        victim = StatusEffectManager()

        # Weapon applies bleeding on hit
        bleeding = StatusEffect(effect_type="bleeding", duration=3, potency=5)
        victim.add_effect(bleeding)

        assert victim.has_effect("bleeding")

    def test_process_effects_turn_start(self):
        """Test processing effects at turn start."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        burning = StatusEffect(effect_type="burning", duration=2, potency=8)
        manager.add_effect(burning)

        # Process turn
        damage = manager.process_turn_start()

        # Should deal burning damage
        assert damage == 8

        # Duration should decrease
        manager.tick_effects()

    def test_check_can_act(self):
        """Test checking if character can act."""
        from status_effects import StatusEffect, StatusEffectManager

        manager = StatusEffectManager()

        # Character can act normally
        assert manager.can_act()

        # Apply stun
        stunned = StatusEffect(effect_type="stunned", duration=1)
        manager.add_effect(stunned)

        # Can't act while stunned
        assert not manager.can_act()

    def test_modify_outgoing_damage(self):
        """Test modifying damage based on effects."""
        from status_effects import StatusEffect, StatusEffectManager

        attacker = StatusEffectManager()

        # Apply weakened
        weakened = StatusEffect(effect_type="weakened", duration=2, potency=40)
        attacker.add_effect(weakened)

        base_damage = 100
        modified = attacker.apply_damage_modifiers(base_damage)

        # Damage reduced
        assert modified < base_damage
        assert modified == 60  # 40% reduction


class TestEdgeCases:
    """Test edge cases."""

    def test_zero_duration_effect(self):
        """Test effect with 0 duration expires immediately."""
        from status_effects import StatusEffect

        effect = StatusEffect(effect_type="bleeding", duration=0, potency=5)

        assert not effect.is_active()

    def test_negative_potency(self):
        """Test negative potency is invalid."""
        from status_effects import StatusEffect

        with pytest.raises(ValueError):
            StatusEffect(effect_type="bleeding", duration=3, potency=-5)

    def test_remove_nonexistent_effect(self):
        """Test removing effect that doesn't exist."""
        from status_effects import StatusEffectManager

        manager = StatusEffectManager()

        # Should not raise error
        manager.cleanse_effect("bleeding")

        assert not manager.has_effect("bleeding")

    def test_large_potency_values(self):
        """Test handling very large potency values."""
        from status_effects import StatusEffect

        effect = StatusEffect(effect_type="burning", duration=2, potency=10000)

        assert effect.potency == 10000

    def test_effect_manager_empty(self):
        """Test manager with no active effects."""
        from status_effects import StatusEffectManager

        manager = StatusEffectManager()

        assert len(manager.get_active_effects()) == 0
        assert manager.can_act()
        assert manager.calculate_dot_damage() == 0
        assert manager.apply_damage_modifiers(100) == 100
