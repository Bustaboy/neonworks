"""
Neon Collapse - World Map System
Manages districts, locations, navigation, and exploration
"""

from typing import Dict, List, Optional, Any


# ============================================================================
# LOCATION CLASS
# ============================================================================

class Location:
    """Represents a specific location within a district."""

    def __init__(
        self,
        location_id: str,
        name: str,
        description: str,
        district: str,
        danger_level: int,
        controlling_faction: Optional[str] = None,
        connected_to: Optional[List[str]] = None
    ):
        if danger_level < 0 or danger_level > 5:
            raise ValueError(f"Danger level must be 0-5, got {danger_level}")

        self.location_id = location_id
        self.name = name
        self.description = description
        self.district = district
        self.danger_level = danger_level
        self.controlling_faction = controlling_faction
        self.connected_to = connected_to or []
        self.discovered = False

    def discover(self):
        """Discover this location (unlock for travel)."""
        self.discovered = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary."""
        return {
            "location_id": self.location_id,
            "name": self.name,
            "description": self.description,
            "district": self.district,
            "danger_level": self.danger_level,
            "controlling_faction": self.controlling_faction,
            "connected_to": self.connected_to,
            "discovered": self.discovered
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create location from dictionary."""
        location = cls(
            location_id=data["location_id"],
            name=data["name"],
            description=data["description"],
            district=data["district"],
            danger_level=data["danger_level"],
            controlling_faction=data.get("controlling_faction"),
            connected_to=data.get("connected_to", [])
        )
        location.discovered = data.get("discovered", False)
        return location


# ============================================================================
# DISTRICT CLASS
# ============================================================================

class District:
    """Represents a major district of Night City."""

    def __init__(
        self,
        district_id: str,
        name: str,
        description: str,
        dominant_faction: Optional[str] = None
    ):
        self.district_id = district_id
        self.name = name
        self.description = description
        self.dominant_faction = dominant_faction
        self.locations: Dict[str, Location] = {}

    def add_location(self, location: Location):
        """Add a location to this district."""
        if location.location_id not in self.locations:
            self.locations[location.location_id] = location

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID."""
        return self.locations.get(location_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert district to dictionary."""
        return {
            "district_id": self.district_id,
            "name": self.name,
            "description": self.description,
            "dominant_faction": self.dominant_faction,
            "locations": {
                loc_id: location.to_dict()
                for loc_id, location in self.locations.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'District':
        """Create district from dictionary."""
        district = cls(
            district_id=data["district_id"],
            name=data["name"],
            description=data["description"],
            dominant_faction=data.get("dominant_faction")
        )

        # Restore locations
        for loc_id, loc_data in data.get("locations", {}).items():
            location = Location.from_dict(loc_data)
            district.add_location(location)

        return district


# ============================================================================
# SAFE HOUSE CLASS
# ============================================================================

class SafeHouse:
    """Represents player's personal safe house/apartment."""

    def __init__(
        self,
        location_id: str,
        district: str,
        rent_cost: int,
        quality_tier: str
    ):
        if quality_tier not in ["cheap", "mid", "luxury"]:
            raise ValueError(f"Invalid quality tier: {quality_tier}")

        self.location_id = location_id
        self.district = district
        self.rent_cost = rent_cost
        self.quality_tier = quality_tier

        # Default upgrades (all start basic)
        self.upgrades = {
            "bed_quality": "basic",
            "has_shower": False,
            "door_security": "broken"
        }

        # Stash storage (item_id -> quantity)
        self.stash: Dict[str, int] = {}

    def upgrade(self, upgrade_name: str, new_value: Any) -> bool:
        """Upgrade a safe house feature."""
        if upgrade_name not in self.upgrades:
            return False
        self.upgrades[upgrade_name] = new_value
        return True

    def get_upgrade_cost(self, upgrade_name: str, new_value: Any) -> int:
        """Get cost to upgrade a feature."""
        if upgrade_name not in self.upgrades:
            return 0

        # Bed upgrades
        if upgrade_name == "bed_quality":
            if new_value == "comfortable":
                return 500
            elif new_value == "luxury":
                return 1500
            else:
                return 0

        # Shower installation
        elif upgrade_name == "has_shower":
            if new_value is True:
                return 800
            else:
                return 0

        # Door security
        elif upgrade_name == "door_security":
            if new_value == "standard":
                return 300
            elif new_value == "reinforced":
                return 1000
            else:
                return 0

        return 0

    def store_in_stash(self, item_id: str, quantity: int):
        """Store items in stash."""
        if item_id in self.stash:
            self.stash[item_id] += quantity
        else:
            self.stash[item_id] = quantity

    def retrieve_from_stash(self, item_id: str, quantity: int) -> int:
        """Retrieve items from stash, returns actual quantity retrieved."""
        if item_id not in self.stash:
            return 0

        available = self.stash[item_id]
        retrieved = min(available, quantity)

        self.stash[item_id] -= retrieved
        if self.stash[item_id] == 0:
            del self.stash[item_id]

        return retrieved

    def get_stash_item_count(self, item_id: str) -> int:
        """Get quantity of an item in stash."""
        return self.stash.get(item_id, 0)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "location_id": self.location_id,
            "district": self.district,
            "rent_cost": self.rent_cost,
            "quality_tier": self.quality_tier,
            "upgrades": self.upgrades,
            "stash": self.stash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SafeHouse':
        """Deserialize from dictionary."""
        safe_house = cls(
            location_id=data["location_id"],
            district=data["district"],
            rent_cost=data["rent_cost"],
            quality_tier=data["quality_tier"]
        )
        safe_house.upgrades = data.get("upgrades", safe_house.upgrades)
        safe_house.stash = data.get("stash", {})
        return safe_house


# ============================================================================
# WORLD MAP MANAGER
# ============================================================================

class WorldMap:
    """Manages the entire game world - districts, locations, navigation."""

    def __init__(self):
        self.districts: Dict[str, District] = {}
        self.current_location: Optional[str] = None
        self.player_safe_house: Optional[SafeHouse] = None

    def add_district(self, district: District):
        """Add a district to the world map."""
        self.districts[district.district_id] = district

    def get_district(self, district_id: str) -> Optional[District]:
        """Get a district by ID."""
        return self.districts.get(district_id)

    def set_current_location(self, location_id: str):
        """Set the current location (starting point)."""
        self.current_location = location_id

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID (searches all districts)."""
        for district in self.districts.values():
            location = district.get_location(location_id)
            if location:
                return location
        return None

    def travel_to(self, location_id: str) -> bool:
        """
        Travel to a location.

        Returns:
            True if travel successful, False if cannot travel (not connected, doesn't exist, etc.)
        """
        # Cannot travel without current location
        if self.current_location is None:
            return False

        # Get current location
        current_loc = self.get_location(self.current_location)
        if current_loc is None:
            return False

        # Check if destination exists
        destination = self.get_location(location_id)
        if destination is None:
            return False

        # Check if destination is connected to current location
        if location_id not in current_loc.connected_to:
            return False

        # Travel successful
        self.current_location = location_id
        destination.discover()  # Auto-discover when traveling
        return True

    def get_available_locations(self) -> List[str]:
        """Get list of location IDs you can travel to from current location."""
        if self.current_location is None:
            return []

        current_loc = self.get_location(self.current_location)
        if current_loc is None:
            return []

        return current_loc.connected_to

    def get_discovered_locations(self) -> List[Location]:
        """Get all discovered locations across all districts."""
        discovered = []
        for district in self.districts.values():
            for location in district.locations.values():
                if location.discovered:
                    discovered.append(location)
        return discovered

    def get_locations_by_faction(self, faction_name: str) -> List[Location]:
        """Get all locations controlled by a faction."""
        controlled = []
        for district in self.districts.values():
            for location in district.locations.values():
                if location.controlling_faction == faction_name:
                    controlled.append(location)
        return controlled

    def get_locations_by_danger_level(self, danger_level: int) -> List[Location]:
        """Get all locations with a specific danger level."""
        matching = []
        for district in self.districts.values():
            for location in district.locations.values():
                if location.danger_level == danger_level:
                    matching.append(location)
        return matching

    def set_safe_house(self, safe_house: SafeHouse):
        """Set player's safe house."""
        self.player_safe_house = safe_house

    def get_safe_house_location(self) -> Optional[str]:
        """Get location ID of player's safe house."""
        if self.player_safe_house:
            return self.player_safe_house.location_id
        return None

    def is_at_safe_house(self) -> bool:
        """Check if player is currently at their safe house."""
        if self.player_safe_house is None:
            return False
        return self.current_location == self.player_safe_house.location_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert world map to dictionary."""
        return {
            "districts": {
                district_id: district.to_dict()
                for district_id, district in self.districts.items()
            },
            "current_location": self.current_location,
            "player_safe_house": self.player_safe_house.to_dict() if self.player_safe_house else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldMap':
        """Load world map from dictionary."""
        world_map = cls()

        # Restore districts
        for district_id, district_data in data.get("districts", {}).items():
            district = District.from_dict(district_data)
            world_map.add_district(district)

        # Restore current location
        world_map.current_location = data.get("current_location")

        # Restore safe house
        if data.get("player_safe_house"):
            world_map.player_safe_house = SafeHouse.from_dict(data["player_safe_house"])

        return world_map
