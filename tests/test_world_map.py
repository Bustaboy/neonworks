"""
Comprehensive test suite for world_map.py (World Map System)

Tests cover:
- Location class (discovery, danger levels, faction control)
- District class (collections of locations)
- WorldMap manager (navigation, travel, discovery)
- Location connections (which locations connect to which)
- Faction-controlled territories
- Serialization (save/load)
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestLocationCreation:
    """Test creating locations."""

    def test_location_creation(self):
        """Test creating a location."""
        from world_map import Location

        location = Location(
            location_id="watson_plaza",
            name="Watson Plaza",
            description="Bustling marketplace in the heart of Watson",
            district="watson",
            danger_level=2,
            controlling_faction="tyger_claws"
        )

        assert location.location_id == "watson_plaza"
        assert location.name == "Watson Plaza"
        assert location.danger_level == 2
        assert location.controlling_faction == "tyger_claws"
        assert location.discovered is False  # Starts undiscovered

    def test_location_starts_undiscovered(self):
        """Test locations start undiscovered by default."""
        from world_map import Location

        location = Location("test_loc", "Test", "Desc", "watson", 1)
        assert location.discovered is False

    def test_location_danger_level_validation(self):
        """Test danger level must be 0-5."""
        from world_map import Location

        # Valid danger levels
        Location("loc1", "Test", "Desc", "watson", 0)  # Min
        Location("loc2", "Test", "Desc", "watson", 5)  # Max

        # Invalid danger levels
        with pytest.raises(ValueError):
            Location("loc3", "Test", "Desc", "watson", -1)

        with pytest.raises(ValueError):
            Location("loc4", "Test", "Desc", "watson", 6)


class TestLocationDiscovery:
    """Test location discovery mechanics."""

    def test_discover_location(self):
        """Test discovering a location."""
        from world_map import Location

        location = Location("test_loc", "Test", "Desc", "watson", 1)
        assert location.discovered is False

        location.discover()
        assert location.discovered is True

    def test_cannot_undiscover_location(self):
        """Test locations stay discovered."""
        from world_map import Location

        location = Location("test_loc", "Test", "Desc", "watson", 1)
        location.discover()
        assert location.discovered is True

        # Should stay discovered (no undiscover method)
        location.discover()
        assert location.discovered is True


class TestLocationConnections:
    """Test location connections (navigation)."""

    def test_location_has_connections(self):
        """Test locations can connect to other locations."""
        from world_map import Location

        location = Location(
            location_id="watson_plaza",
            name="Watson Plaza",
            description="Plaza",
            district="watson",
            danger_level=2,
            connected_to=["watson_market", "watson_alley"]
        )

        assert "watson_market" in location.connected_to
        assert "watson_alley" in location.connected_to
        assert len(location.connected_to) == 2

    def test_location_can_connect_bidirectionally(self):
        """Test two locations can connect to each other."""
        from world_map import Location

        loc_a = Location("loc_a", "A", "Desc", "watson", 1, connected_to=["loc_b"])
        loc_b = Location("loc_b", "B", "Desc", "watson", 1, connected_to=["loc_a"])

        assert "loc_b" in loc_a.connected_to
        assert "loc_a" in loc_b.connected_to


class TestDistrictCreation:
    """Test creating districts."""

    def test_district_creation(self):
        """Test creating a district."""
        from world_map import District

        district = District(
            district_id="watson",
            name="Watson",
            description="Industrial district, home to the working class",
            dominant_faction="tyger_claws"
        )

        assert district.district_id == "watson"
        assert district.name == "Watson"
        assert district.dominant_faction == "tyger_claws"
        assert len(district.locations) == 0  # No locations yet

    def test_district_add_location(self):
        """Test adding locations to a district."""
        from world_map import District, Location

        district = District("watson", "Watson", "Industrial district")

        location = Location("watson_plaza", "Watson Plaza", "Plaza", "watson", 2)
        district.add_location(location)

        assert len(district.locations) == 1
        assert "watson_plaza" in district.locations

    def test_district_get_location(self):
        """Test getting a location from a district."""
        from world_map import District, Location

        district = District("watson", "Watson", "Industrial district")
        location = Location("watson_plaza", "Watson Plaza", "Plaza", "watson", 2)
        district.add_location(location)

        retrieved = district.get_location("watson_plaza")
        assert retrieved.location_id == "watson_plaza"


class TestWorldMapCreation:
    """Test creating world map."""

    def test_world_map_creation(self):
        """Test creating an empty world map."""
        from world_map import WorldMap

        world_map = WorldMap()

        assert world_map is not None
        assert len(world_map.districts) == 0
        assert world_map.current_location is None

    def test_world_map_add_district(self):
        """Test adding districts to world map."""
        from world_map import WorldMap, District

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        world_map.add_district(district)

        assert len(world_map.districts) == 1
        assert "watson" in world_map.districts

    def test_world_map_get_district(self):
        """Test getting a district from world map."""
        from world_map import WorldMap, District

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")
        world_map.add_district(district)

        retrieved = world_map.get_district("watson")
        assert retrieved.district_id == "watson"


class TestWorldMapNavigation:
    """Test navigation and travel."""

    def test_travel_to_location(self):
        """Test traveling to a location."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1, connected_to=["loc_b"])
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 2, connected_to=["loc_a"])

        district.add_location(loc_a)
        district.add_location(loc_b)
        world_map.add_district(district)

        # Start at location A
        world_map.set_current_location("loc_a")
        assert world_map.current_location == "loc_a"

        # Travel to location B
        success = world_map.travel_to("loc_b")
        assert success is True
        assert world_map.current_location == "loc_b"

    def test_cannot_travel_to_unconnected_location(self):
        """Test cannot travel to location not connected."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1, connected_to=["loc_b"])
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 2, connected_to=["loc_a"])
        loc_c = Location("loc_c", "Location C", "Desc", "watson", 3)  # Not connected

        district.add_location(loc_a)
        district.add_location(loc_b)
        district.add_location(loc_c)
        world_map.add_district(district)

        world_map.set_current_location("loc_a")

        # Cannot travel to loc_c (not connected)
        success = world_map.travel_to("loc_c")
        assert success is False
        assert world_map.current_location == "loc_a"  # Still at loc_a

    def test_travel_auto_discovers_location(self):
        """Test traveling to a location automatically discovers it."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1, connected_to=["loc_b"])
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 2, connected_to=["loc_a"])

        district.add_location(loc_a)
        district.add_location(loc_b)
        world_map.add_district(district)

        world_map.set_current_location("loc_a")
        loc_a.discover()  # Discover starting location

        assert loc_b.discovered is False

        world_map.travel_to("loc_b")

        assert loc_b.discovered is True

    def test_get_available_locations(self):
        """Test getting available travel destinations."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1, connected_to=["loc_b", "loc_c"])
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 2)
        loc_c = Location("loc_c", "Location C", "Desc", "watson", 3)

        district.add_location(loc_a)
        district.add_location(loc_b)
        district.add_location(loc_c)
        world_map.add_district(district)

        world_map.set_current_location("loc_a")

        available = world_map.get_available_locations()

        assert len(available) == 2
        assert "loc_b" in available
        assert "loc_c" in available


class TestLocationQueries:
    """Test querying locations."""

    def test_get_all_discovered_locations(self):
        """Test getting all discovered locations."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1)
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 2)
        loc_c = Location("loc_c", "Location C", "Desc", "watson", 3)

        district.add_location(loc_a)
        district.add_location(loc_b)
        district.add_location(loc_c)
        world_map.add_district(district)

        # Discover only A and B
        loc_a.discover()
        loc_b.discover()

        discovered = world_map.get_discovered_locations()

        assert len(discovered) == 2
        assert "loc_a" in [loc.location_id for loc in discovered]
        assert "loc_b" in [loc.location_id for loc in discovered]

    def test_get_locations_by_faction(self):
        """Test getting locations controlled by a faction."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1, controlling_faction="tyger_claws")
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 2, controlling_faction="tyger_claws")
        loc_c = Location("loc_c", "Location C", "Desc", "watson", 3, controlling_faction="militech")

        district.add_location(loc_a)
        district.add_location(loc_b)
        district.add_location(loc_c)
        world_map.add_district(district)

        tyger_locs = world_map.get_locations_by_faction("tyger_claws")

        assert len(tyger_locs) == 2
        assert "loc_a" in [loc.location_id for loc in tyger_locs]
        assert "loc_b" in [loc.location_id for loc in tyger_locs]

    def test_get_locations_by_danger_level(self):
        """Test getting locations by danger level."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1)
        loc_b = Location("loc_b", "Location B", "Desc", "watson", 3)
        loc_c = Location("loc_c", "Location C", "Desc", "watson", 3)

        district.add_location(loc_a)
        district.add_location(loc_b)
        district.add_location(loc_c)
        world_map.add_district(district)

        danger_3_locs = world_map.get_locations_by_danger_level(3)

        assert len(danger_3_locs) == 2
        assert "loc_b" in [loc.location_id for loc in danger_3_locs]
        assert "loc_c" in [loc.location_id for loc in danger_3_locs]


class TestSerialization:
    """Test world map serialization."""

    def test_location_to_dict(self):
        """Test converting location to dictionary."""
        from world_map import Location

        location = Location(
            location_id="watson_plaza",
            name="Watson Plaza",
            description="Plaza",
            district="watson",
            danger_level=2,
            controlling_faction="tyger_claws",
            connected_to=["watson_market"]
        )
        location.discover()

        data = location.to_dict()

        assert data["location_id"] == "watson_plaza"
        assert data["danger_level"] == 2
        assert data["controlling_faction"] == "tyger_claws"
        assert data["discovered"] is True
        assert "watson_market" in data["connected_to"]

    def test_location_from_dict(self):
        """Test loading location from dictionary."""
        from world_map import Location

        data = {
            "location_id": "watson_plaza",
            "name": "Watson Plaza",
            "description": "Plaza",
            "district": "watson",
            "danger_level": 2,
            "controlling_faction": "tyger_claws",
            "connected_to": ["watson_market"],
            "discovered": True
        }

        location = Location.from_dict(data)

        assert location.location_id == "watson_plaza"
        assert location.danger_level == 2
        assert location.discovered is True

    def test_world_map_to_dict(self):
        """Test converting world map to dictionary."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")
        location = Location("loc_a", "Location A", "Desc", "watson", 1)
        district.add_location(location)
        world_map.add_district(district)
        world_map.set_current_location("loc_a")

        data = world_map.to_dict()

        assert "districts" in data
        assert "watson" in data["districts"]
        assert data["current_location"] == "loc_a"

    def test_world_map_from_dict(self):
        """Test loading world map from dictionary."""
        from world_map import WorldMap

        data = {
            "districts": {
                "watson": {
                    "district_id": "watson",
                    "name": "Watson",
                    "description": "Industrial district",
                    "dominant_faction": None,
                    "locations": {
                        "loc_a": {
                            "location_id": "loc_a",
                            "name": "Location A",
                            "description": "Desc",
                            "district": "watson",
                            "danger_level": 1,
                            "controlling_faction": None,
                            "connected_to": [],
                            "discovered": True
                        }
                    }
                }
            },
            "current_location": "loc_a"
        }

        world_map = WorldMap.from_dict(data)

        assert len(world_map.districts) == 1
        assert world_map.current_location == "loc_a"
        district = world_map.get_district("watson")
        assert len(district.locations) == 1


class TestEdgeCases:
    """Test edge cases."""

    def test_travel_with_no_current_location(self):
        """Test cannot travel without setting current location."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")
        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1)
        district.add_location(loc_a)
        world_map.add_district(district)

        # No current location set
        success = world_map.travel_to("loc_a")
        assert success is False

    def test_invalid_location_id(self):
        """Test traveling to non-existent location."""
        from world_map import WorldMap, District, Location

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")
        loc_a = Location("loc_a", "Location A", "Desc", "watson", 1)
        district.add_location(loc_a)
        world_map.add_district(district)

        world_map.set_current_location("loc_a")

        success = world_map.travel_to("nonexistent_location")
        assert success is False

    def test_district_cannot_add_duplicate_location(self):
        """Test cannot add same location twice to district."""
        from world_map import District, Location

        district = District("watson", "Watson", "Industrial district")
        location = Location("loc_a", "Location A", "Desc", "watson", 1)

        district.add_location(location)
        assert len(district.locations) == 1

        # Try to add again (should fail or be ignored)
        district.add_location(location)
        assert len(district.locations) == 1  # Still only 1


class TestSafeHouseCreation:
    """Test creating player safe houses."""

    def test_safe_house_creation(self):
        """Test creating a safe house."""
        from world_map import SafeHouse

        safe_house = SafeHouse(
            location_id="watson_apartment",
            district="watson",
            rent_cost=100,
            quality_tier="cheap"
        )

        assert safe_house.location_id == "watson_apartment"
        assert safe_house.district == "watson"
        assert safe_house.rent_cost == 100
        assert safe_house.quality_tier == "cheap"

    def test_safe_house_starts_with_basic_upgrades(self):
        """Test safe house starts with basic upgrades."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        assert safe_house.upgrades["bed_quality"] == "basic"
        assert safe_house.upgrades["has_shower"] is False
        assert safe_house.upgrades["door_security"] == "broken"

    def test_safe_house_quality_tiers(self):
        """Test different quality tiers."""
        from world_map import SafeHouse

        # Cheap tier
        cheap = SafeHouse("watson_apt", "watson", 100, "cheap")
        assert cheap.quality_tier == "cheap"

        # Mid tier
        mid = SafeHouse("japantown_apt", "japantown", 300, "mid")
        assert mid.quality_tier == "mid"

        # Luxury tier
        luxury = SafeHouse("corpo_apt", "corpo_plaza", 800, "luxury")
        assert luxury.quality_tier == "luxury"


class TestSafeHouseUpgrades:
    """Test safe house upgrade system."""

    def test_upgrade_bed(self):
        """Test upgrading bed quality."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        assert safe_house.upgrades["bed_quality"] == "basic"

        success = safe_house.upgrade("bed_quality", "comfortable")
        assert success is True
        assert safe_house.upgrades["bed_quality"] == "comfortable"

    def test_install_shower(self):
        """Test installing a shower."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        assert safe_house.upgrades["has_shower"] is False

        success = safe_house.upgrade("has_shower", True)
        assert success is True
        assert safe_house.upgrades["has_shower"] is True

    def test_upgrade_door_security(self):
        """Test upgrading door security."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        assert safe_house.upgrades["door_security"] == "broken"

        safe_house.upgrade("door_security", "standard")
        assert safe_house.upgrades["door_security"] == "standard"

        safe_house.upgrade("door_security", "reinforced")
        assert safe_house.upgrades["door_security"] == "reinforced"

    def test_invalid_upgrade(self):
        """Test upgrading with invalid upgrade name."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        success = safe_house.upgrade("invalid_upgrade", "value")
        assert success is False

    def test_get_upgrade_cost(self):
        """Test getting upgrade costs."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        # Bed upgrade
        cost = safe_house.get_upgrade_cost("bed_quality", "comfortable")
        assert cost > 0

        # Shower installation
        cost = safe_house.get_upgrade_cost("has_shower", True)
        assert cost > 0


class TestSafeHouseStash:
    """Test safe house stash storage."""

    def test_stash_starts_empty(self):
        """Test stash starts empty."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        assert len(safe_house.stash) == 0

    def test_store_item_in_stash(self):
        """Test storing items in stash."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        # Store an item (just item_id for now)
        safe_house.store_in_stash("weapon_ar_01", 1)

        assert len(safe_house.stash) == 1
        assert "weapon_ar_01" in safe_house.stash
        assert safe_house.stash["weapon_ar_01"] == 1

    def test_retrieve_item_from_stash(self):
        """Test retrieving items from stash."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        safe_house.store_in_stash("weapon_ar_01", 1)
        quantity = safe_house.retrieve_from_stash("weapon_ar_01", 1)

        assert quantity == 1
        assert "weapon_ar_01" not in safe_house.stash

    def test_stack_items_in_stash(self):
        """Test stacking same items in stash."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        safe_house.store_in_stash("medkit", 5)
        safe_house.store_in_stash("medkit", 3)

        assert safe_house.stash["medkit"] == 8

    def test_retrieve_more_than_available(self):
        """Test retrieving more items than available."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        safe_house.store_in_stash("medkit", 5)
        quantity = safe_house.retrieve_from_stash("medkit", 10)

        # Should return only what's available
        assert quantity == 5
        assert "medkit" not in safe_house.stash


class TestWorldMapSafeHouse:
    """Test world map integration with safe house."""

    def test_set_player_safe_house(self):
        """Test setting player's safe house."""
        from world_map import WorldMap, SafeHouse

        world_map = WorldMap()
        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")

        world_map.set_safe_house(safe_house)

        assert world_map.player_safe_house is not None
        assert world_map.player_safe_house.location_id == "watson_apt"

    def test_get_safe_house_location(self):
        """Test getting safe house location."""
        from world_map import WorldMap, SafeHouse

        world_map = WorldMap()
        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        world_map.set_safe_house(safe_house)

        location_id = world_map.get_safe_house_location()
        assert location_id == "watson_apt"

    def test_is_at_safe_house(self):
        """Test checking if player is at safe house."""
        from world_map import WorldMap, District, Location, SafeHouse

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        apartment = Location("watson_apt", "Your Apartment", "Your safe house", "watson", 0)
        district.add_location(apartment)
        world_map.add_district(district)

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        world_map.set_safe_house(safe_house)

        world_map.set_current_location("watson_apt")

        assert world_map.is_at_safe_house() is True

    def test_is_not_at_safe_house(self):
        """Test checking when not at safe house."""
        from world_map import WorldMap, District, Location, SafeHouse

        world_map = WorldMap()
        district = District("watson", "Watson", "Industrial district")

        apartment = Location("watson_apt", "Your Apartment", "Safe house", "watson", 0)
        other_loc = Location("watson_plaza", "Plaza", "Marketplace", "watson", 2)
        district.add_location(apartment)
        district.add_location(other_loc)
        world_map.add_district(district)

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        world_map.set_safe_house(safe_house)

        world_map.set_current_location("watson_plaza")

        assert world_map.is_at_safe_house() is False

    def test_change_safe_house(self):
        """Test changing to a new safe house."""
        from world_map import WorldMap, SafeHouse

        world_map = WorldMap()

        # Start in Watson
        watson_apt = SafeHouse("watson_apt", "watson", 100, "cheap")
        world_map.set_safe_house(watson_apt)
        assert world_map.player_safe_house.district == "watson"

        # Move to Japantown
        japantown_apt = SafeHouse("japantown_apt", "japantown", 300, "mid")
        world_map.set_safe_house(japantown_apt)
        assert world_map.player_safe_house.district == "japantown"
        assert world_map.player_safe_house.rent_cost == 300


class TestSafeHouseSerialization:
    """Test safe house serialization."""

    def test_safe_house_to_dict(self):
        """Test converting safe house to dictionary."""
        from world_map import SafeHouse

        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        safe_house.upgrade("bed_quality", "comfortable")
        safe_house.store_in_stash("medkit", 5)

        data = safe_house.to_dict()

        assert data["location_id"] == "watson_apt"
        assert data["district"] == "watson"
        assert data["rent_cost"] == 100
        assert data["upgrades"]["bed_quality"] == "comfortable"
        assert data["stash"]["medkit"] == 5

    def test_safe_house_from_dict(self):
        """Test loading safe house from dictionary."""
        from world_map import SafeHouse

        data = {
            "location_id": "watson_apt",
            "district": "watson",
            "rent_cost": 100,
            "quality_tier": "cheap",
            "upgrades": {
                "bed_quality": "comfortable",
                "has_shower": True,
                "door_security": "standard"
            },
            "stash": {
                "medkit": 5,
                "weapon_ar_01": 1
            }
        }

        safe_house = SafeHouse.from_dict(data)

        assert safe_house.location_id == "watson_apt"
        assert safe_house.upgrades["bed_quality"] == "comfortable"
        assert safe_house.stash["medkit"] == 5

    def test_world_map_with_safe_house_serialization(self):
        """Test world map serialization with safe house."""
        from world_map import WorldMap, SafeHouse

        world_map = WorldMap()
        safe_house = SafeHouse("watson_apt", "watson", 100, "cheap")
        world_map.set_safe_house(safe_house)

        data = world_map.to_dict()

        assert "player_safe_house" in data
        assert data["player_safe_house"]["location_id"] == "watson_apt"

    def test_world_map_from_dict_with_safe_house(self):
        """Test loading world map with safe house."""
        from world_map import WorldMap

        data = {
            "districts": {},
            "current_location": None,
            "player_safe_house": {
                "location_id": "watson_apt",
                "district": "watson",
                "rent_cost": 100,
                "quality_tier": "cheap",
                "upgrades": {
                    "bed_quality": "basic",
                    "has_shower": False,
                    "door_security": "broken"
                },
                "stash": {}
            }
        }

        world_map = WorldMap.from_dict(data)

        assert world_map.player_safe_house is not None
        assert world_map.player_safe_house.location_id == "watson_apt"
