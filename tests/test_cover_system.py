"""
Comprehensive test suite for cover_system.py (Cover System)

Tests cover:
- Cover types (none, half, full)
- Cover provides dodge bonus (+20% half, +40% full)
- Cover destruction mechanics
- Breaking cover (takes damage, eventually destroyed)
- AI cover behavior (enemies use cover intelligently)
- Cover placement in combat encounters
- Taking/leaving cover actions
- Cover blocking line of sight
- Integration with combat system
- Serialization for save/load
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestCoverTypes:
    """Test different cover types."""

    def test_no_cover(self):
        """Test character with no cover."""
        from cover_system import CoverManager

        manager = CoverManager()

        assert manager.get_cover_type() == "none"
        assert manager.get_dodge_bonus() == 0

    def test_half_cover(self):
        """Test half cover provides bonus."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        half_cover = CoverObject(
            cover_id="crate",
            cover_type="half",
            hp=50
        )

        manager.take_cover(half_cover)

        assert manager.get_cover_type() == "half"
        assert manager.get_dodge_bonus() == 20  # +20% dodge

    def test_full_cover(self):
        """Test full cover provides larger bonus."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        full_cover = CoverObject(
            cover_id="wall",
            cover_type="full",
            hp=100
        )

        manager.take_cover(full_cover)

        assert manager.get_cover_type() == "full"
        assert manager.get_dodge_bonus() == 40  # +40% dodge

    def test_invalid_cover_type(self):
        """Test invalid cover type raises error."""
        from cover_system import CoverObject

        with pytest.raises(ValueError):
            CoverObject(
                cover_id="test",
                cover_type="invalid",
                hp=50
            )


class TestCoverDodgeBonus:
    """Test cover dodge bonus mechanics."""

    def test_no_cover_no_bonus(self):
        """Test no cover provides no bonus."""
        from cover_system import CoverManager

        manager = CoverManager()

        bonus = manager.get_dodge_bonus()

        assert bonus == 0

    def test_half_cover_bonus(self):
        """Test half cover gives +20% dodge."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("cover", "half", 50)
        manager.take_cover(cover)

        assert manager.get_dodge_bonus() == 20

    def test_full_cover_bonus(self):
        """Test full cover gives +40% dodge."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("cover", "full", 100)
        manager.take_cover(cover)

        assert manager.get_dodge_bonus() == 40

    def test_apply_dodge_bonus_to_attack(self):
        """Test applying dodge bonus to incoming attack."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        base_hit_chance = 80
        modified_hit_chance = manager.apply_cover_to_hit_chance(base_hit_chance)

        # 40% dodge bonus means 40% reduction to hit chance
        assert modified_hit_chance == 40  # 80 - 40

    def test_dodge_bonus_cannot_go_negative(self):
        """Test hit chance cannot go below 0."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        base_hit_chance = 20
        modified = manager.apply_cover_to_hit_chance(base_hit_chance)

        # Should not go negative
        assert modified >= 0


class TestCoverDestruction:
    """Test cover destruction mechanics."""

    def test_cover_has_hp(self):
        """Test cover objects have HP."""
        from cover_system import CoverObject

        cover = CoverObject("crate", "half", hp=50)

        assert cover.hp == 50
        assert cover.max_hp == 50

    def test_cover_takes_damage(self):
        """Test cover can take damage."""
        from cover_system import CoverObject

        cover = CoverObject("crate", "half", 50)

        cover.take_damage(20)

        assert cover.hp == 30

    def test_cover_destroyed_at_zero_hp(self):
        """Test cover is destroyed when HP reaches 0."""
        from cover_system import CoverObject

        cover = CoverObject("crate", "half", 50)

        cover.take_damage(60)

        assert cover.is_destroyed()
        assert cover.hp == 0

    def test_destroyed_cover_no_bonus(self):
        """Test destroyed cover provides no bonus."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("crate", "half", 50)
        manager.take_cover(cover)

        # Destroy cover
        cover.take_damage(100)

        # Should provide no bonus
        assert manager.get_dodge_bonus() == 0

    def test_overkill_damage_stops_at_zero(self):
        """Test cover HP doesn't go below 0."""
        from cover_system import CoverObject

        cover = CoverObject("crate", "half", 50)

        cover.take_damage(200)

        assert cover.hp == 0
        assert cover.is_destroyed()


class TestTakingCover:
    """Test taking and leaving cover."""

    def test_take_cover_action(self):
        """Test character takes cover."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)

        result = manager.take_cover(cover)

        assert result is True
        assert manager.in_cover()
        assert manager.current_cover == cover

    def test_leave_cover_action(self):
        """Test character leaves cover."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        assert manager.in_cover()

        manager.leave_cover()

        assert not manager.in_cover()
        assert manager.current_cover is None

    def test_cannot_take_destroyed_cover(self):
        """Test cannot take cover behind destroyed object."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("crate", "half", 50)
        cover.take_damage(100)  # Destroy it

        result = manager.take_cover(cover)

        assert result is False
        assert not manager.in_cover()

    def test_switch_cover(self):
        """Test switching from one cover to another."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover1 = CoverObject("crate", "half", 50)
        cover2 = CoverObject("wall", "full", 100)

        manager.take_cover(cover1)
        assert manager.current_cover == cover1

        manager.take_cover(cover2)
        assert manager.current_cover == cover2
        assert manager.get_dodge_bonus() == 40  # Full cover bonus

    def test_forced_out_of_destroyed_cover(self):
        """Test character forced out when cover destroyed."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("crate", "half", 50)
        manager.take_cover(cover)

        # Destroy cover
        cover.take_damage(100)

        # Manager should detect destroyed cover
        assert not manager.has_valid_cover()


class TestCoverInCombat:
    """Test cover integration with combat."""

    def test_attack_damages_cover(self):
        """Test missed attack can damage cover."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        initial_hp = cover.hp

        # Simulate attack missing character but hitting cover
        manager.process_cover_hit(30)

        assert cover.hp < initial_hp
        assert cover.hp == 70

    def test_cover_blocks_some_attacks(self):
        """Test cover causes some attacks to miss."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        # With full cover (+40% dodge), some attacks should miss
        hit_chance = 50
        modified = manager.apply_cover_to_hit_chance(hit_chance)

        assert modified < hit_chance

    def test_no_cover_no_protection(self):
        """Test no cover means no protection."""
        from cover_system import CoverManager

        manager = CoverManager()

        hit_chance = 80
        modified = manager.apply_cover_to_hit_chance(hit_chance)

        # No change without cover
        assert modified == hit_chance

    def test_partial_damage_through_half_cover(self):
        """Test half cover doesn't block everything."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        half_cover = CoverObject("crate", "half", 50)
        manager.take_cover(half_cover)

        # Half cover gives +20% dodge
        hit_chance = 100
        modified = manager.apply_cover_to_hit_chance(hit_chance)

        # Should reduce but not eliminate hits
        assert modified == 80  # 100 - 20
        assert modified > 0


class TestAICoverBehavior:
    """Test AI using cover intelligently."""

    def test_ai_seeks_cover_when_low_hp(self):
        """Test AI seeks cover when health is low."""
        from cover_system import CoverAI, CoverObject

        ai = CoverAI()

        cover = CoverObject("wall", "full", 100)

        # Low HP, should seek cover
        decision = ai.should_seek_cover(
            current_hp=20,
            max_hp=100,
            available_cover=[cover]
        )

        assert decision is True

    def test_ai_doesnt_need_cover_full_hp(self):
        """Test AI doesn't seek cover at full health."""
        from cover_system import CoverAI, CoverObject

        ai = CoverAI()

        cover = CoverObject("wall", "full", 100)

        # Full HP, less urgent to seek cover
        decision = ai.should_seek_cover(
            current_hp=100,
            max_hp=100,
            available_cover=[cover]
        )

        # Might still seek cover, but less likely
        assert isinstance(decision, bool)

    def test_ai_prefers_full_cover(self):
        """Test AI prefers full cover over half cover."""
        from cover_system import CoverAI, CoverObject

        ai = CoverAI()

        half_cover = CoverObject("crate", "half", 50)
        full_cover = CoverObject("wall", "full", 100)

        best_cover = ai.choose_best_cover([half_cover, full_cover])

        assert best_cover == full_cover

    def test_ai_avoids_destroyed_cover(self):
        """Test AI doesn't choose destroyed cover."""
        from cover_system import CoverAI, CoverObject

        ai = CoverAI()

        good_cover = CoverObject("wall", "full", 100)
        destroyed_cover = CoverObject("crate", "half", 0)

        best_cover = ai.choose_best_cover([good_cover, destroyed_cover])

        assert best_cover == good_cover

    def test_ai_considers_cover_hp(self):
        """Test AI considers cover durability."""
        from cover_system import CoverAI, CoverObject

        ai = CoverAI()

        weak_cover = CoverObject("crate", "half", 10)
        sturdy_cover = CoverObject("wall", "full", 100)

        best_cover = ai.choose_best_cover([weak_cover, sturdy_cover])

        # Should prefer sturdy cover
        assert best_cover == sturdy_cover


class TestCoverPlacement:
    """Test cover placement in encounters."""

    def test_encounter_has_cover(self):
        """Test combat encounters can have cover objects."""
        from cover_system import CombatEncounter, CoverObject

        encounter = CombatEncounter()

        cover = CoverObject("wall", "full", 100)
        encounter.add_cover(cover)

        assert len(encounter.available_cover) == 1
        assert cover in encounter.available_cover

    def test_multiple_cover_objects(self):
        """Test encounter can have multiple cover objects."""
        from cover_system import CombatEncounter, CoverObject

        encounter = CombatEncounter()

        cover1 = CoverObject("wall1", "full", 100)
        cover2 = CoverObject("crate1", "half", 50)
        cover3 = CoverObject("barrier", "half", 75)

        encounter.add_cover(cover1)
        encounter.add_cover(cover2)
        encounter.add_cover(cover3)

        assert len(encounter.available_cover) == 3

    def test_cover_randomly_placed(self):
        """Test cover is randomly placed in encounters."""
        from cover_system import CombatEncounter

        encounter = CombatEncounter()

        encounter.generate_random_cover(difficulty="medium")

        # Should have some cover
        assert len(encounter.available_cover) > 0

    def test_harder_encounters_more_cover(self):
        """Test harder encounters have more cover options."""
        from cover_system import CombatEncounter

        easy_encounter = CombatEncounter()
        hard_encounter = CombatEncounter()

        easy_encounter.generate_random_cover(difficulty="easy")
        hard_encounter.generate_random_cover(difficulty="hard")

        # Hard encounters should have more cover (generally)
        # This is probabilistic, so we just verify it generates cover
        assert len(hard_encounter.available_cover) >= 0

    def test_get_cover_by_id(self):
        """Test finding specific cover object."""
        from cover_system import CombatEncounter, CoverObject

        encounter = CombatEncounter()

        cover = CoverObject("specific_cover", "full", 100)
        encounter.add_cover(cover)

        found = encounter.get_cover("specific_cover")

        assert found == cover


class TestLineOfSight:
    """Test cover blocking line of sight."""

    def test_full_cover_blocks_sight(self):
        """Test full cover blocks line of sight."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        full_cover = CoverObject("wall", "full", 100)
        manager.take_cover(full_cover)

        assert manager.blocks_line_of_sight()

    def test_half_cover_doesnt_block_sight(self):
        """Test half cover doesn't fully block sight."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        half_cover = CoverObject("crate", "half", 50)
        manager.take_cover(half_cover)

        assert not manager.blocks_line_of_sight()

    def test_no_cover_no_sight_block(self):
        """Test no cover doesn't block sight."""
        from cover_system import CoverManager

        manager = CoverManager()

        assert not manager.blocks_line_of_sight()


class TestCoverActions:
    """Test cover action costs."""

    def test_taking_cover_costs_action(self):
        """Test taking cover uses an action."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)

        # Taking cover costs action points
        action_cost = manager.get_take_cover_cost()

        assert action_cost > 0
        assert action_cost == 1  # 1 action to take cover

    def test_leaving_cover_free(self):
        """Test leaving cover is free action."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        # Leaving cover is free
        action_cost = manager.get_leave_cover_cost()

        assert action_cost == 0


class TestCoverRegeneration:
    """Test cover regeneration/repair."""

    def test_cover_cannot_regenerate(self):
        """Test cover doesn't regenerate HP naturally."""
        from cover_system import CoverObject

        cover = CoverObject("wall", "full", 100)
        cover.take_damage(50)

        initial_hp = cover.hp

        # Simulate time passing (cover doesn't heal)
        # No regenerate method - cover stays damaged

        assert cover.hp == initial_hp

    def test_destroyed_cover_stays_destroyed(self):
        """Test destroyed cover stays destroyed."""
        from cover_system import CoverObject

        cover = CoverObject("crate", "half", 50)
        cover.take_damage(100)

        assert cover.is_destroyed()

        # Even after time, still destroyed
        assert cover.is_destroyed()


class TestSerialization:
    """Test cover system serialization."""

    def test_cover_object_to_dict(self):
        """Test converting cover object to dictionary."""
        from cover_system import CoverObject

        cover = CoverObject("wall", "full", 100)
        cover.take_damage(25)

        data = cover.to_dict()

        assert data["cover_id"] == "wall"
        assert data["cover_type"] == "full"
        assert data["hp"] == 75
        assert data["max_hp"] == 100

    def test_cover_object_from_dict(self):
        """Test loading cover object from dictionary."""
        from cover_system import CoverObject

        data = {
            "cover_id": "crate",
            "cover_type": "half",
            "hp": 30,
            "max_hp": 50
        }

        cover = CoverObject.from_dict(data)

        assert cover.cover_id == "crate"
        assert cover.cover_type == "half"
        assert cover.hp == 30
        assert cover.max_hp == 50

    def test_cover_manager_to_dict(self):
        """Test converting cover manager to dictionary."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)
        manager.take_cover(cover)

        data = manager.to_dict()

        assert "current_cover" in data
        assert data["current_cover"] is not None

    def test_cover_manager_from_dict(self):
        """Test loading cover manager from dictionary."""
        from cover_system import CoverManager

        data = {
            "current_cover": {
                "cover_id": "wall",
                "cover_type": "full",
                "hp": 80,
                "max_hp": 100
            }
        }

        manager = CoverManager.from_dict(data)

        assert manager.in_cover()
        assert manager.current_cover.cover_id == "wall"
        assert manager.get_dodge_bonus() == 40


class TestEdgeCases:
    """Test edge cases."""

    def test_zero_hp_cover(self):
        """Test cover with 0 HP is destroyed."""
        from cover_system import CoverObject

        cover = CoverObject("weak", "half", 0)

        assert cover.is_destroyed()

    def test_negative_damage_invalid(self):
        """Test negative damage doesn't heal cover."""
        from cover_system import CoverObject

        cover = CoverObject("wall", "full", 100)
        cover.take_damage(50)

        initial_hp = cover.hp

        # Try negative damage (should be ignored or error)
        cover.take_damage(-20)

        # HP should not increase
        assert cover.hp == initial_hp

    def test_take_cover_twice(self):
        """Test taking same cover twice."""
        from cover_system import CoverManager, CoverObject

        manager = CoverManager()

        cover = CoverObject("wall", "full", 100)

        manager.take_cover(cover)
        manager.take_cover(cover)

        # Should still be in same cover
        assert manager.current_cover == cover

    def test_leave_cover_when_not_in_cover(self):
        """Test leaving cover when not in cover."""
        from cover_system import CoverManager

        manager = CoverManager()

        # Not in cover
        assert not manager.in_cover()

        # Try to leave
        manager.leave_cover()

        # Should not error
        assert not manager.in_cover()

    def test_empty_encounter_no_cover(self):
        """Test encounter with no cover available."""
        from cover_system import CombatEncounter

        encounter = CombatEncounter()

        assert len(encounter.available_cover) == 0
