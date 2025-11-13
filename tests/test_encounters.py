"""
Comprehensive test suite for encounters.py (Multiple Encounters System)

Tests cover:
- Encounter template creation (different difficulty tiers)
- Enemy scaling by player phase (0-4)
- Loot table generation based on difficulty
- Encounter randomization
- Enemy composition balancing
- Serialization (to_dict/from_dict)
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestEncounterCreation:
    """Test creating encounters with different configurations."""

    def test_create_basic_encounter(self):
        """Test creating a basic encounter."""
        from encounters import Encounter

        encounter = Encounter(
            encounter_id="street_thugs_1",
            name="Street Thugs",
            description="A group of low-level gangers looking for trouble",
            difficulty="EASY",
            location_type="street"
        )

        assert encounter.encounter_id == "street_thugs_1"
        assert encounter.name == "Street Thugs"
        assert encounter.difficulty == "EASY"
        assert encounter.location_type == "street"

    def test_encounter_has_enemies(self):
        """Test encounter contains enemy definitions."""
        from encounters import Encounter

        encounter = Encounter(
            encounter_id="ganger_ambush",
            name="Ganger Ambush",
            description="Tyger Claws ambush",
            difficulty="MEDIUM",
            location_type="alley"
        )

        # Add enemies to encounter
        encounter.add_enemy("ganger_basic", count=2)
        encounter.add_enemy("ganger_heavy", count=1)

        assert len(encounter.enemies) == 2
        assert encounter.enemies["ganger_basic"] == 2
        assert encounter.enemies["ganger_heavy"] == 1

    def test_difficulty_validation(self):
        """Test encounter validates difficulty tier."""
        from encounters import Encounter

        # Valid difficulties should work
        for difficulty in ["EASY", "MEDIUM", "HARD", "EXTREME"]:
            encounter = Encounter(
                encounter_id=f"test_{difficulty}",
                name="Test",
                description="Test",
                difficulty=difficulty,
                location_type="street"
            )
            assert encounter.difficulty == difficulty

        # Invalid difficulty should raise error
        with pytest.raises(ValueError):
            Encounter(
                encounter_id="invalid",
                name="Invalid",
                description="Invalid",
                difficulty="IMPOSSIBLE",
                location_type="street"
            )

    def test_encounter_rewards(self):
        """Test encounters have reward definitions."""
        from encounters import Encounter

        encounter = Encounter(
            encounter_id="corpo_patrol",
            name="Corporate Patrol",
            description="Militech security patrol",
            difficulty="HARD",
            location_type="corpo_plaza"
        )

        encounter.set_rewards(
            eddies_min=500,
            eddies_max=1000,
            xp_reward=100,
            loot_table="corpo_gear"
        )

        assert encounter.eddies_min == 500
        assert encounter.eddies_max == 1000
        assert encounter.xp_reward == 100
        assert encounter.loot_table == "corpo_gear"


class TestEnemyScaling:
    """Test enemy scaling by player phase."""

    def test_phase_0_enemies_basic(self):
        """Test Phase 0 (starting) enemies are basic."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=0,
            difficulty="EASY",
            location_type="street"
        )

        # Phase 0 EASY should have 1-2 basic enemies
        total_enemies = sum(encounter.enemies.values())
        assert 1 <= total_enemies <= 3

    def test_phase_2_enemies_scaled(self):
        """Test Phase 2 (mid-game) enemies are stronger."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=2,
            difficulty="MEDIUM",
            location_type="corpo_building"
        )

        # Phase 2 should have more enemies and heavier types
        total_enemies = sum(encounter.enemies.values())
        assert 3 <= total_enemies <= 6

    def test_phase_4_enemies_maximum(self):
        """Test Phase 4 (end-game) enemies are maximum difficulty."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=4,
            difficulty="EXTREME",
            location_type="combat_zone"
        )

        # Phase 4 EXTREME should have many enemies
        total_enemies = sum(encounter.enemies.values())
        assert total_enemies >= 6

    def test_phase_affects_enemy_stats(self):
        """Test player phase affects enemy stats."""
        from encounters import EncounterManager, Enemy

        manager = EncounterManager()

        # Generate same enemy type at different phases
        enemy_p0 = manager.generate_enemy("ganger_basic", player_phase=0)
        enemy_p4 = manager.generate_enemy("ganger_basic", player_phase=4)

        # Higher phase enemies should be stronger
        assert enemy_p4.hp > enemy_p0.hp
        assert enemy_p4.damage > enemy_p0.damage

    def test_phase_validation(self):
        """Test player phase is validated (0-4)."""
        from encounters import EncounterManager

        manager = EncounterManager()

        # Valid phases
        for phase in range(5):
            encounter = manager.generate_encounter(
                player_phase=phase,
                difficulty="EASY",
                location_type="street"
            )
            assert encounter is not None

        # Invalid phase should raise error
        with pytest.raises(ValueError):
            manager.generate_encounter(
                player_phase=5,
                difficulty="EASY",
                location_type="street"
            )


class TestDifficultyScaling:
    """Test difficulty tier scaling."""

    def test_easy_encounter_scaling(self):
        """Test EASY encounters have appropriate scaling."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=1,
            difficulty="EASY",
            location_type="street"
        )

        # EASY should have fewer, weaker enemies
        total_enemies = sum(encounter.enemies.values())
        assert 1 <= total_enemies <= 3
        assert encounter.eddies_min < 500

    def test_medium_encounter_scaling(self):
        """Test MEDIUM encounters have appropriate scaling."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=1,
            difficulty="MEDIUM",
            location_type="alley"
        )

        # MEDIUM should have moderate enemies
        total_enemies = sum(encounter.enemies.values())
        assert 2 <= total_enemies <= 5
        assert 300 <= encounter.eddies_min <= 800

    def test_hard_encounter_scaling(self):
        """Test HARD encounters have appropriate scaling."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=2,
            difficulty="HARD",
            location_type="corpo_building"
        )

        # HARD should have many strong enemies
        total_enemies = sum(encounter.enemies.values())
        assert 4 <= total_enemies <= 7
        assert encounter.eddies_min >= 600

    def test_extreme_encounter_scaling(self):
        """Test EXTREME encounters are extremely difficult."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=3,
            difficulty="EXTREME",
            location_type="combat_zone"
        )

        # EXTREME should have maximum enemies
        total_enemies = sum(encounter.enemies.values())
        assert total_enemies >= 6
        assert encounter.eddies_min >= 1000


class TestLootTables:
    """Test loot generation from encounters."""

    def test_loot_table_generation(self):
        """Test generating loot from encounter."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=1,
            difficulty="MEDIUM",
            location_type="street"
        )

        loot = encounter.generate_loot()

        assert "eddies" in loot
        assert "items" in loot
        assert loot["eddies"] >= encounter.eddies_min
        assert loot["eddies"] <= encounter.eddies_max

    def test_difficulty_affects_loot_quality(self):
        """Test higher difficulty gives better loot."""
        from encounters import EncounterManager

        manager = EncounterManager()

        easy_encounter = manager.generate_encounter(
            player_phase=2,
            difficulty="EASY",
            location_type="street"
        )

        hard_encounter = manager.generate_encounter(
            player_phase=2,
            difficulty="HARD",
            location_type="corpo_building"
        )

        # HARD should have higher rewards
        assert hard_encounter.eddies_max > easy_encounter.eddies_max
        assert hard_encounter.xp_reward > easy_encounter.xp_reward

    def test_location_affects_loot_type(self):
        """Test location type affects loot table."""
        from encounters import EncounterManager

        manager = EncounterManager()

        street_encounter = manager.generate_encounter(
            player_phase=1,
            difficulty="MEDIUM",
            location_type="street"
        )

        corpo_encounter = manager.generate_encounter(
            player_phase=1,
            difficulty="MEDIUM",
            location_type="corpo_building"
        )

        # Different locations should have different loot tables
        assert street_encounter.loot_table != corpo_encounter.loot_table

    def test_loot_includes_items(self):
        """Test loot can include items from inventory."""
        from encounters import EncounterManager

        manager = EncounterManager()
        encounter = manager.generate_encounter(
            player_phase=2,
            difficulty="HARD",
            location_type="corpo_building"
        )

        loot = encounter.generate_loot()

        # Should have chance of item drops
        assert isinstance(loot["items"], list)
        # HARD difficulty should have good chance of items
        if len(loot["items"]) > 0:
            assert all("item_id" in item for item in loot["items"])


class TestEncounterTemplates:
    """Test pre-defined encounter templates."""

    def test_get_template_by_name(self):
        """Test retrieving encounter template by name."""
        from encounters import EncounterManager

        manager = EncounterManager()

        # Get predefined template
        template = manager.get_template("street_thugs")

        assert template is not None
        assert template.name == "Street Thugs"
        assert template.difficulty == "EASY"

    def test_all_templates_valid(self):
        """Test all predefined templates are valid."""
        from encounters import EncounterManager

        manager = EncounterManager()

        templates = manager.get_all_templates()

        assert len(templates) >= 10  # Should have at least 10 templates
        for template in templates:
            assert template.difficulty in ["EASY", "MEDIUM", "HARD", "EXTREME"]
            assert len(template.enemies) > 0

    def test_template_instantiation(self):
        """Test creating encounter instance from template."""
        from encounters import EncounterManager

        manager = EncounterManager()

        template = manager.get_template("ganger_ambush")
        encounter = manager.instantiate_template(template, player_phase=2)

        # Should create scaled instance from template
        assert encounter.name == template.name
        assert encounter.difficulty == template.difficulty
        assert len(encounter.enemies) > 0


class TestEnemyDefinitions:
    """Test enemy type definitions."""

    def test_basic_enemy_creation(self):
        """Test creating basic enemy."""
        from encounters import Enemy

        enemy = Enemy(
            enemy_id="ganger_basic",
            name="Street Ganger",
            enemy_type="humanoid",
            base_hp=50,
            base_damage=10,
            base_defense=5
        )

        assert enemy.enemy_id == "ganger_basic"
        assert enemy.name == "Street Ganger"
        assert enemy.base_hp == 50

    def test_enemy_scaling(self):
        """Test enemy stats scale with phase."""
        from encounters import Enemy

        enemy = Enemy(
            enemy_id="ganger_basic",
            name="Street Ganger",
            enemy_type="humanoid",
            base_hp=50,
            base_damage=10,
            base_defense=5
        )

        # Scale to phase 3
        scaled = enemy.scale_to_phase(3)

        assert scaled.hp > enemy.base_hp
        assert scaled.damage > enemy.base_damage
        assert scaled.defense >= enemy.base_defense

    def test_enemy_types(self):
        """Test different enemy types exist."""
        from encounters import EncounterManager

        manager = EncounterManager()

        # Should have various enemy types
        types = ["ganger_basic", "ganger_heavy", "corpo_security",
                 "netrunner", "solo", "boss"]

        for enemy_type in types:
            enemy = manager.generate_enemy(enemy_type, player_phase=1)
            assert enemy is not None


class TestEncounterRandomization:
    """Test encounter randomization."""

    def test_random_encounter_generation(self):
        """Test generating random encounter."""
        from encounters import EncounterManager

        manager = EncounterManager()

        # Generate multiple random encounters (larger sample for variety)
        encounters = [
            manager.generate_random_encounter(player_phase=2, location_type="street")
            for _ in range(20)
        ]

        # Should generate valid encounters
        assert all(e is not None for e in encounters)
        # Should have some variety (with 20 samples, very likely to get different difficulties)
        difficulties = [e.difficulty for e in encounters]
        assert len(set(difficulties)) > 1  # Not all same difficulty

    def test_location_appropriate_encounters(self):
        """Test encounters match location type."""
        from encounters import EncounterManager

        manager = EncounterManager()

        street_encounter = manager.generate_random_encounter(
            player_phase=1,
            location_type="street"
        )

        corpo_encounter = manager.generate_random_encounter(
            player_phase=1,
            location_type="corpo_building"
        )

        # Location should influence encounter type
        assert street_encounter.location_type == "street"
        assert corpo_encounter.location_type == "corpo_building"


class TestSerialization:
    """Test encounter serialization."""

    def test_encounter_to_dict(self):
        """Test converting encounter to dictionary."""
        from encounters import Encounter

        encounter = Encounter(
            encounter_id="test_encounter",
            name="Test Encounter",
            description="Test",
            difficulty="MEDIUM",
            location_type="street"
        )

        encounter.add_enemy("ganger_basic", count=2)
        encounter.set_rewards(
            eddies_min=300,
            eddies_max=600,
            xp_reward=50,
            loot_table="street_gear"
        )

        data = encounter.to_dict()

        assert data["encounter_id"] == "test_encounter"
        assert data["difficulty"] == "MEDIUM"
        assert data["enemies"]["ganger_basic"] == 2
        assert data["eddies_min"] == 300

    def test_encounter_from_dict(self):
        """Test loading encounter from dictionary."""
        from encounters import Encounter

        data = {
            "encounter_id": "saved_encounter",
            "name": "Saved Encounter",
            "description": "Loaded from save",
            "difficulty": "HARD",
            "location_type": "alley",
            "enemies": {"corpo_security": 3},
            "eddies_min": 500,
            "eddies_max": 1000,
            "xp_reward": 100,
            "loot_table": "corpo_gear"
        }

        encounter = Encounter.from_dict(data)

        assert encounter.encounter_id == "saved_encounter"
        assert encounter.difficulty == "HARD"
        assert encounter.enemies["corpo_security"] == 3
        assert encounter.xp_reward == 100

    def test_encounter_manager_serialization(self):
        """Test serializing entire encounter manager."""
        from encounters import EncounterManager

        manager = EncounterManager()

        # Generate some encounters
        encounter1 = manager.generate_encounter(1, "EASY", "street")
        encounter2 = manager.generate_encounter(2, "HARD", "corpo_building")

        data = manager.to_dict()

        assert "templates" in data

        # Load from data
        loaded_manager = EncounterManager.from_dict(data)
        assert loaded_manager is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_encounter(self):
        """Test encounter with no enemies raises error."""
        from encounters import Encounter

        encounter = Encounter(
            encounter_id="empty",
            name="Empty",
            description="No enemies",
            difficulty="EASY",
            location_type="street"
        )

        # Generating loot with no enemies should still work
        loot = encounter.generate_loot()
        assert loot["eddies"] == 0
        assert len(loot["items"]) == 0

    def test_invalid_enemy_type(self):
        """Test adding invalid enemy type."""
        from encounters import EncounterManager

        manager = EncounterManager()

        with pytest.raises(ValueError):
            manager.generate_enemy("invalid_enemy_type", player_phase=1)

    def test_phase_boundary_conditions(self):
        """Test phase 0 and phase 4 (boundaries)."""
        from encounters import EncounterManager

        manager = EncounterManager()

        # Phase 0 (minimum)
        encounter_p0 = manager.generate_encounter(0, "EASY", "street")
        assert encounter_p0 is not None

        # Phase 4 (maximum)
        encounter_p4 = manager.generate_encounter(4, "EXTREME", "combat_zone")
        assert encounter_p4 is not None
