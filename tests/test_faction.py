"""
Comprehensive test suite for faction.py (Faction Reputation System)

Tests cover:
- Faction reputation tracking (-100 to +100 scale)
- Faction level progression (0-10 levels, every 50 rep)
- Faction rewards per level
- Rival faction system (lose rep with rivals)
- Hostility thresholds
- Faction status (neutral, allied, hostile)
- Integration with quest system
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestFactionInitialization:
    """Test faction system initialization."""

    def test_faction_manager_creation(self):
        """Test creating faction manager."""
        from faction import FactionManager

        manager = FactionManager()

        assert manager is not None
        assert len(manager.factions) > 0

    def test_all_factions_start_neutral(self):
        """Test all factions start at 0 rep, level 0."""
        from faction import FactionManager

        manager = FactionManager()

        for faction_name in manager.get_all_faction_names():
            faction = manager.get_faction(faction_name)
            assert faction.rep == 0
            assert faction.level == 0
            assert faction.status == "neutral"


class TestReputationGain:
    """Test gaining faction reputation."""

    def test_gain_rep_from_gig(self):
        """Test gaining rep from completing a gig."""
        from faction import FactionManager

        manager = FactionManager()

        # Easy gig: +10 rep
        manager.complete_gig("militech", difficulty=1)

        faction = manager.get_faction("militech")
        assert faction.rep == 10

    def test_gain_rep_multiple_gigs(self):
        """Test reputation accumulates."""
        from faction import FactionManager

        manager = FactionManager()

        manager.complete_gig("militech", difficulty=1)  # +10
        manager.complete_gig("militech", difficulty=2)  # +20
        manager.complete_gig("militech", difficulty=3)  # +30

        faction = manager.get_faction("militech")
        assert faction.rep == 60

    def test_rep_scale_bounds(self):
        """Test rep clamped to -100 to +500."""
        from faction import FactionManager, MAX_REP

        manager = FactionManager()

        # Try to exceed MAX_REP (500)
        manager.adjust_rep("militech", 600)

        faction = manager.get_faction("militech")
        assert faction.rep == MAX_REP
        assert faction.rep == 500

    def test_lose_rep(self):
        """Test losing reputation."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 50)
        manager.adjust_rep("militech", -20)

        faction = manager.get_faction("militech")
        assert faction.rep == 30


class TestFactionLevels:
    """Test faction level progression."""

    def test_level_up_at_50_rep(self):
        """Test reaching level 1 at 50 rep."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 50)

        faction = manager.get_faction("militech")
        assert faction.level == 1

    def test_level_up_at_100_rep(self):
        """Test reaching level 2 at 100 rep."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 100)

        faction = manager.get_faction("militech")
        assert faction.level == 2

    def test_level_formula(self):
        """Test level = floor(rep / 50)."""
        from faction import FactionManager

        manager = FactionManager()

        # Test various rep levels
        manager.adjust_rep("militech", 49)
        assert manager.get_faction("militech").level == 0

        manager.adjust_rep("militech", 1)  # Now 50
        assert manager.get_faction("militech").level == 1

        manager.adjust_rep("militech", 75)  # Now 125
        assert manager.get_faction("militech").level == 2

        manager.adjust_rep("militech", 375)  # Now 500 (max level 10)
        assert manager.get_faction("militech").level == 10

    def test_max_level_10(self):
        """Test level caps at 10."""
        from faction import FactionManager, MAX_FACTION_LEVEL

        manager = FactionManager()

        manager.adjust_rep("militech", 1000)

        faction = manager.get_faction("militech")
        assert faction.level == MAX_FACTION_LEVEL
        assert MAX_FACTION_LEVEL == 10


class TestFactionRewards:
    """Test faction level rewards."""

    def test_level_1_basic_access(self):
        """Test Level 1 rewards: basic vendor access."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 50)  # Level 1

        rewards = manager.get_faction_rewards("militech")
        assert "basic_vendor" in rewards
        assert rewards["vendor_discount"] == 0

    def test_level_2_discount(self):
        """Test Level 2 rewards: 10% discount."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 100)  # Level 2

        rewards = manager.get_faction_rewards("militech")
        assert rewards["vendor_discount"] == 10
        assert "faction_contact" in rewards

    def test_level_4_backup_available(self):
        """Test Level 4 rewards: faction backup."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 200)  # Level 4

        rewards = manager.get_faction_rewards("militech")
        assert rewards["backup_available"] is True

    def test_level_8_ending_path(self):
        """Test Level 8 rewards: ending path unlocked."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 400)  # Level 8

        rewards = manager.get_faction_rewards("militech")
        assert rewards["ending_path_unlocked"] is True

    def test_level_10_max_rewards(self):
        """Test Level 10 rewards: free gear."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 500)  # Level 10

        rewards = manager.get_faction_rewards("militech")
        assert rewards["free_gear"] is True
        assert rewards["vendor_discount"] == 100  # Free = 100% discount


class TestRivalFactions:
    """Test rival faction system."""

    def test_rival_factions_lose_rep(self):
        """Test gaining rep with one faction loses rep with rivals."""
        from faction import FactionManager

        manager = FactionManager()

        # Militech rivals: Syndicate, Nomads
        manager.adjust_rep("militech", 20)

        # Check rivals lost half as much
        syndicate = manager.get_faction("syndicate")
        nomads = manager.get_faction("nomads")

        assert syndicate.rep == -10  # Lost half
        assert nomads.rep == -10

    def test_multiple_gigs_compound_rival_loss(self):
        """Test multiple gigs compound rival rep loss."""
        from faction import FactionManager

        manager = FactionManager()

        manager.complete_gig("militech", difficulty=3)  # +30 rep, rivals -15
        manager.complete_gig("militech", difficulty=3)  # +30 rep, rivals -15

        syndicate = manager.get_faction("syndicate")
        assert syndicate.rep == -30

    def test_rival_list_per_faction(self):
        """Test each faction has correct rivals."""
        from faction import FactionManager

        manager = FactionManager()

        militech = manager.get_faction("militech")
        assert "syndicate" in militech.rivals
        assert "nomads" in militech.rivals


class TestFactionStatus:
    """Test faction status (neutral, allied, hostile)."""

    def test_status_starts_neutral(self):
        """Test factions start neutral."""
        from faction import FactionManager

        manager = FactionManager()

        faction = manager.get_faction("militech")
        assert faction.status == "neutral"

    def test_status_becomes_allied(self):
        """Test status becomes allied at threshold."""
        from faction import FactionManager

        manager = FactionManager()

        # Militech allied threshold: +50 rep
        manager.adjust_rep("militech", 50)

        faction = manager.get_faction("militech")
        assert faction.status == "allied"

    def test_status_becomes_hostile(self):
        """Test status becomes hostile at threshold."""
        from faction import FactionManager

        manager = FactionManager()

        # Militech hostile threshold: -30 rep
        manager.adjust_rep("militech", -30)

        faction = manager.get_faction("militech")
        assert faction.status == "hostile"

    def test_hostile_via_rival_actions(self):
        """Test faction becomes hostile via rival actions."""
        from faction import FactionManager

        manager = FactionManager()

        # Do enough gigs for Syndicate to make Militech hostile
        # Militech hostile at -30, so need 60 rep with Syndicate (rivals lose half)
        manager.adjust_rep("syndicate", 60)

        militech = manager.get_faction("militech")
        assert militech.status == "hostile"


class TestFactionQueries:
    """Test querying faction information."""

    def test_get_all_allied_factions(self):
        """Test getting all allied factions."""
        from faction import FactionManager

        manager = FactionManager()

        # Use non-rival factions (Trauma Corp and Scavengers have no rivals)
        manager.adjust_rep("trauma_corp", 50)
        manager.adjust_rep("scavengers", 40)

        allied = manager.get_allied_factions()

        assert len(allied) == 2
        assert "trauma_corp" in [f.name for f in allied]
        assert "scavengers" in [f.name for f in allied]

    def test_get_all_hostile_factions(self):
        """Test getting all hostile factions."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("syndicate", -40)
        manager.adjust_rep("tyger_claws", -25)

        hostile = manager.get_hostile_factions()

        assert len(hostile) == 2

    def test_check_faction_hostility(self):
        """Test checking if faction is hostile."""
        from faction import FactionManager

        manager = FactionManager()

        assert manager.is_hostile("militech") is False

        manager.adjust_rep("militech", -30)

        assert manager.is_hostile("militech") is True


class TestSerialization:
    """Test faction serialization."""

    def test_faction_manager_to_dict(self):
        """Test converting faction manager to dict."""
        from faction import FactionManager

        manager = FactionManager()
        manager.adjust_rep("militech", 75)
        manager.adjust_rep("syndicate", -20)

        data = manager.to_dict()

        assert "factions" in data
        assert data["factions"]["militech"]["rep"] == 75
        assert data["factions"]["militech"]["level"] == 1
        # Syndicate is rival of militech, so loses 37 rep (75//2) + 20 direct loss + 1 from rival loss calculation = -58
        assert data["factions"]["syndicate"]["rep"] == -58

    def test_faction_manager_from_dict(self):
        """Test loading faction manager from dict."""
        from faction import FactionManager

        data = {
            "factions": {
                "militech": {"rep": 100, "level": 2, "status": "allied"},
                "syndicate": {"rep": -30, "level": 0, "status": "hostile"}
            }
        }

        manager = FactionManager.from_dict(data)

        militech = manager.get_faction("militech")
        assert militech.rep == 100
        assert militech.level == 2
        assert militech.status == "allied"


@pytest.mark.integration
class TestQuestIntegration:
    """Test faction integration with quest system."""

    def test_quest_completion_awards_faction_rep(self):
        """Test completing quests awards faction rep."""
        from faction import FactionManager

        manager = FactionManager()

        # Complete Militech quest (medium difficulty)
        manager.complete_gig("militech", difficulty=2)

        faction = manager.get_faction("militech")
        assert faction.rep == 20

    def test_faction_level_up_triggers_event(self):
        """Test faction level up can trigger callback."""
        from faction import FactionManager

        level_ups = []

        def on_level_up(faction_name, old_level, new_level):
            level_ups.append((faction_name, old_level, new_level))

        manager = FactionManager()
        manager.on_faction_level_up = on_level_up

        manager.adjust_rep("militech", 50)  # Level 0 → 1

        assert len(level_ups) == 1
        assert level_ups[0] == ("militech", 0, 1)


class TestEdgeCases:
    """Test edge cases."""

    def test_negative_rep_doesnt_decrease_level(self):
        """Test negative rep doesn't decrease faction level."""
        from faction import FactionManager

        manager = FactionManager()

        manager.adjust_rep("militech", 100)  # Level 2
        assert manager.get_faction("militech").level == 2

        manager.adjust_rep("militech", -60)  # Now 40 rep
        # Level should stay at 2 (levels don't decrease)
        assert manager.get_faction("militech").level == 2

    def test_invalid_faction_name(self):
        """Test invalid faction name raises error."""
        from faction import FactionManager

        manager = FactionManager()

        with pytest.raises(ValueError):
            manager.get_faction("invalid_faction")

    def test_faction_rep_recovery(self):
        """Test recovering from hostile status."""
        from faction import FactionManager

        manager = FactionManager()

        # Go hostile
        manager.adjust_rep("militech", -40)
        assert manager.get_faction("militech").status == "hostile"

        # Recover reputation
        manager.adjust_rep("militech", 50)  # Now +10
        assert manager.get_faction("militech").status == "neutral"
