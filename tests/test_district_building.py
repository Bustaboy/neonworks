"""
Comprehensive test suite for district_building.py (District Building System)

Tests cover:
- District creation and initialization
- Building placement (defenses, housing, commerce, infrastructure)
- Income generation (2000-10000 credits/hour based on development)
- District upgrades and progression
- Population management
- Security level and threats
- Random events
- Integration with world map
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestDistrictCreation:
    """Test creating and initializing player districts."""

    def test_create_district(self):
        """Test creating a new district."""
        from district_building import District

        district = District(
            district_id="watson_district",
            name="Watson Settlement",
            location="watson"
        )

        assert district.district_id == "watson_district"
        assert district.name == "Watson Settlement"
        assert district.location == "watson"

    def test_new_district_starts_basic(self):
        """Test new district starts with basic stats."""
        from district_building import District

        district = District(
            district_id="new_settlement",
            name="New Settlement",
            location="badlands"
        )

        assert district.level == 1
        assert district.population == 0
        assert district.security_level == 0
        assert len(district.buildings) == 0

    def test_district_has_income_tracking(self):
        """Test district tracks income generation."""
        from district_building import District

        district = District(
            district_id="test",
            name="Test",
            location="watson"
        )

        # Should have income tracking
        income = district.calculate_income()
        assert income >= 0


class TestBuildingPlacement:
    """Test placing buildings in district."""

    def test_place_housing_building(self):
        """Test placing a housing building."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        building = Building(
            building_id="housing_1",
            building_type="housing",
            name="Apartment Block",
            cost=1000
        )

        result = district.place_building(building)

        assert result is True
        assert len(district.buildings) == 1
        assert district.buildings[0].building_type == "housing"

    def test_place_commerce_building(self):
        """Test placing commerce building."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        shop = Building(
            building_id="shop_1",
            building_type="commerce",
            name="Night Market",
            cost=2000
        )

        district.place_building(shop)

        assert len(district.buildings) == 1
        assert district.buildings[0].building_type == "commerce"

    def test_place_defense_building(self):
        """Test placing defense building."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        turret = Building(
            building_id="turret_1",
            building_type="defense",
            name="Auto-Turret",
            cost=3000
        )

        district.place_building(turret)

        assert len(district.buildings) == 1
        assert district.buildings[0].building_type == "defense"

    def test_place_infrastructure_building(self):
        """Test placing infrastructure building."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        generator = Building(
            building_id="gen_1",
            building_type="infrastructure",
            name="Power Generator",
            cost=5000
        )

        district.place_building(generator)

        assert len(district.buildings) == 1
        assert district.buildings[0].building_type == "infrastructure"

    def test_building_placement_limit(self):
        """Test district has building slot limit."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        # Try to place more buildings than allowed
        max_buildings = district.max_building_slots

        for i in range(max_buildings + 5):
            building = Building(f"b_{i}", "housing", f"Building {i}", 100)
            result = district.place_building(building)

            if i < max_buildings:
                assert result is True
            else:
                assert result is False  # Should fail when slots full


class TestIncomeGeneration:
    """Test income generation from district."""

    def test_empty_district_minimal_income(self):
        """Test empty district has minimal income."""
        from district_building import District

        district = District("test", "Test", "watson")

        income = district.calculate_income()

        # Empty district should have low income (scavenging, etc.)
        assert 0 <= income <= 500

    def test_commerce_buildings_increase_income(self):
        """Test commerce buildings increase income."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        # Add commerce building
        shop = Building("shop", "commerce", "Shop", 1000)
        district.place_building(shop)

        income_with_commerce = district.calculate_income()

        assert income_with_commerce > 0

    def test_multiple_commerce_stacks_income(self):
        """Test multiple commerce buildings stack income."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        shop1 = Building("shop1", "commerce", "Shop 1", 1000)
        shop2 = Building("shop2", "commerce", "Shop 2", 1000)

        district.place_building(shop1)
        income_one = district.calculate_income()

        district.place_building(shop2)
        income_two = district.calculate_income()

        assert income_two > income_one

    def test_max_income_cap(self):
        """Test income is capped at maximum."""
        from district_building import District, Building, MAX_DISTRICT_INCOME

        district = District("test", "Test", "watson")

        # Fill district with commerce buildings
        for i in range(20):
            shop = Building(f"shop_{i}", "commerce", f"Shop {i}", 1000)
            district.place_building(shop)

        income = district.calculate_income()

        assert income <= MAX_DISTRICT_INCOME
        assert MAX_DISTRICT_INCOME == 10000  # Per hour

    def test_income_scales_with_population(self):
        """Test income scales with district population."""
        from district_building import District

        district = District("test", "Test", "watson")

        # Low population
        district.population = 10
        income_low = district.calculate_income()

        # High population
        district.population = 100
        income_high = district.calculate_income()

        assert income_high > income_low


class TestPopulationManagement:
    """Test population growth and management."""

    def test_housing_increases_capacity(self):
        """Test housing buildings increase population capacity."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        initial_capacity = district.population_capacity

        housing = Building("housing", "housing", "Apartments", 1000)
        district.place_building(housing)

        new_capacity = district.population_capacity

        assert new_capacity > initial_capacity

    def test_population_grows_over_time(self):
        """Test population grows when under capacity."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        # Add housing for capacity
        housing = Building("housing", "housing", "Apartments", 1000)
        district.place_building(housing)

        initial_pop = district.population

        # Simulate time passing
        district.update_population(hours_passed=24)

        assert district.population > initial_pop

    def test_population_capped_by_capacity(self):
        """Test population doesn't exceed capacity."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        housing = Building("housing", "housing", "Apartments", 1000)
        district.place_building(housing)

        capacity = district.population_capacity

        # Try to grow beyond capacity
        district.update_population(hours_passed=1000)

        assert district.population <= capacity


class TestSecurityLevel:
    """Test district security system."""

    def test_defense_buildings_increase_security(self):
        """Test defense buildings increase security level."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        initial_security = district.calculate_security()

        turret = Building("turret", "defense", "Turret", 2000)
        district.place_building(turret)

        new_security = district.calculate_security()

        assert new_security > initial_security

    def test_security_level_range(self):
        """Test security level is 0-100."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        # Fill with defenses
        for i in range(10):
            defense = Building(f"def_{i}", "defense", f"Defense {i}", 1000)
            district.place_building(defense)

        security = district.calculate_security()

        assert 0 <= security <= 100

    def test_low_security_increases_threat(self):
        """Test low security increases attack threat."""
        from district_building import District

        district = District("test", "Test", "watson")

        # No defenses = high threat
        threat = district.calculate_threat_level()

        assert threat > 0


class TestDistrictUpgrades:
    """Test district level progression."""

    def test_district_levels_up(self):
        """Test district can level up."""
        from district_building import District

        district = District("test", "Test", "watson")

        assert district.level == 1

        # Level up
        result = district.level_up()

        assert result is True
        assert district.level == 2

    def test_level_up_costs_resources(self):
        """Test leveling up requires resources."""
        from district_building import District

        district = District("test", "Test", "watson")

        cost = district.get_level_up_cost()

        assert cost > 0

    def test_max_district_level(self):
        """Test district has maximum level."""
        from district_building import District, MAX_DISTRICT_LEVEL

        district = District("test", "Test", "watson")

        # Level up to max
        for _ in range(20):
            district.level_up()

        assert district.level == MAX_DISTRICT_LEVEL
        assert MAX_DISTRICT_LEVEL == 10

    def test_higher_level_unlocks_buildings(self):
        """Test higher district levels unlock buildings."""
        from district_building import District

        district = District("test", "Test", "watson")

        # Level 1 buildings
        level_1_buildings = district.get_available_buildings()

        # Level up
        district.level_up()

        level_2_buildings = district.get_available_buildings()

        # Should have more options
        assert len(level_2_buildings) >= len(level_1_buildings)


class TestRandomEvents:
    """Test random district events."""

    def test_generate_random_event(self):
        """Test generating random events."""
        from district_building import District

        district = District("test", "Test", "watson")

        event = district.generate_random_event()

        # Event might be None (not always triggered)
        if event:
            assert "event_type" in event
            assert "description" in event

    def test_attack_event_based_on_security(self):
        """Test attack events more likely with low security."""
        from district_building import District

        district = District("test", "Test", "watson")

        # Low security district
        attack_chance = district.get_attack_chance()

        assert attack_chance > 0

    def test_positive_events_with_high_population(self):
        """Test positive events with high population."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        # Build up district
        housing = Building("housing", "housing", "Apartments", 1000)
        district.place_building(housing)
        district.population = 50

        # Should have chance of positive events
        event_types = district.get_possible_event_types()

        assert "positive" in event_types or "trade_opportunity" in event_types


class TestBuildingTypes:
    """Test different building types and effects."""

    def test_building_has_stats(self):
        """Test buildings have proper stats."""
        from district_building import Building

        building = Building(
            building_id="test_building",
            building_type="commerce",
            name="Test Shop",
            cost=1000
        )

        assert building.building_id == "test_building"
        assert building.building_type == "commerce"
        assert building.cost == 1000

    def test_housing_provides_capacity(self):
        """Test housing buildings provide population capacity."""
        from district_building import Building

        housing = Building("housing", "housing", "Apartments", 1000)

        capacity = housing.get_population_capacity()

        assert capacity > 0

    def test_commerce_provides_income(self):
        """Test commerce buildings provide income."""
        from district_building import Building

        shop = Building("shop", "commerce", "Shop", 2000)

        income = shop.get_income_bonus()

        assert income > 0

    def test_defense_provides_security(self):
        """Test defense buildings provide security."""
        from district_building import Building

        turret = Building("turret", "defense", "Turret", 3000)

        security = turret.get_security_bonus()

        assert security > 0

    def test_infrastructure_provides_bonuses(self):
        """Test infrastructure buildings provide bonuses."""
        from district_building import Building

        generator = Building("generator", "infrastructure", "Generator", 5000)

        bonus = generator.get_infrastructure_bonus()

        assert bonus > 0


class TestSerialization:
    """Test district serialization."""

    def test_district_to_dict(self):
        """Test converting district to dictionary."""
        from district_building import District, Building

        district = District("test", "Test District", "watson")
        building = Building("shop", "commerce", "Shop", 1000)
        district.place_building(building)
        district.population = 25

        data = district.to_dict()

        assert data["district_id"] == "test"
        assert data["name"] == "Test District"
        assert data["location"] == "watson"
        assert len(data["buildings"]) == 1
        assert data["population"] == 25

    def test_district_from_dict(self):
        """Test loading district from dictionary."""
        from district_building import District

        data = {
            "district_id": "loaded",
            "name": "Loaded District",
            "location": "pacifica",
            "level": 3,
            "population": 50,
            "buildings": [
                {
                    "building_id": "shop_1",
                    "building_type": "commerce",
                    "name": "Market",
                    "cost": 2000
                }
            ]
        }

        district = District.from_dict(data)

        assert district.district_id == "loaded"
        assert district.level == 3
        assert district.population == 50
        assert len(district.buildings) == 1

    def test_building_to_dict(self):
        """Test converting building to dictionary."""
        from district_building import Building

        building = Building("test", "housing", "Test Building", 1500)

        data = building.to_dict()

        assert data["building_id"] == "test"
        assert data["building_type"] == "housing"
        assert data["cost"] == 1500

    def test_building_from_dict(self):
        """Test loading building from dictionary."""
        from district_building import Building

        data = {
            "building_id": "loaded_building",
            "building_type": "defense",
            "name": "Loaded Turret",
            "cost": 3000
        }

        building = Building.from_dict(data)

        assert building.building_id == "loaded_building"
        assert building.building_type == "defense"
        assert building.cost == 3000


class TestEdgeCases:
    """Test edge cases."""

    def test_negative_cost_invalid(self):
        """Test negative building cost is invalid."""
        from district_building import Building

        with pytest.raises(ValueError):
            Building("test", "housing", "Test", cost=-100)

    def test_invalid_building_type(self):
        """Test invalid building type raises error."""
        from district_building import Building

        with pytest.raises(ValueError):
            Building("test", "invalid_type", "Test", 1000)

    def test_remove_building(self):
        """Test removing a building from district."""
        from district_building import District, Building

        district = District("test", "Test", "watson")

        building = Building("shop", "commerce", "Shop", 1000)
        district.place_building(building)

        assert len(district.buildings) == 1

        result = district.remove_building("shop")

        assert result is True
        assert len(district.buildings) == 0

    def test_remove_nonexistent_building(self):
        """Test removing nonexistent building returns False."""
        from district_building import District

        district = District("test", "Test", "watson")

        result = district.remove_building("nonexistent")

        assert result is False
