"""
Neon Collapse - District Building System
Manages player-owned settlement building, income, and population
"""

from typing import Dict, List, Any, Optional
import random


# Constants
MAX_DISTRICT_LEVEL = 10
MAX_DISTRICT_INCOME = 10000  # Credits per hour
MIN_DISTRICT_INCOME = 100    # Base scavenging income
BUILDING_TYPES = ["housing", "commerce", "defense", "infrastructure"]


# ============================================================================
# BUILDING CLASS
# ============================================================================

class Building:
    """Represents a building placed in the district."""

    def __init__(
        self,
        building_id: str,
        building_type: str,
        name: str,
        cost: int
    ):
        if cost < 0:
            raise ValueError(f"Building cost cannot be negative: {cost}")

        if building_type not in BUILDING_TYPES:
            raise ValueError(f"Invalid building type: {building_type}. Must be one of {BUILDING_TYPES}")

        self.building_id = building_id
        self.building_type = building_type
        self.name = name
        self.cost = cost

    def get_population_capacity(self) -> int:
        """Get population capacity provided by this building."""
        if self.building_type == "housing":
            return 10  # Each housing adds 10 capacity
        return 0

    def get_income_bonus(self) -> int:
        """Get income bonus provided by this building."""
        if self.building_type == "commerce":
            return 500  # +500 credits/hour per commerce building
        elif self.building_type == "infrastructure":
            return 200  # Infrastructure provides some income
        return 0

    def get_security_bonus(self) -> int:
        """Get security bonus provided by this building."""
        if self.building_type == "defense":
            return 10  # +10 security per defense building
        return 0

    def get_infrastructure_bonus(self) -> int:
        """Get infrastructure bonus (efficiency multiplier)."""
        if self.building_type == "infrastructure":
            return 5  # +5% efficiency per infrastructure
        return 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "building_id": self.building_id,
            "building_type": self.building_type,
            "name": self.name,
            "cost": self.cost
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Building':
        """Load from dictionary."""
        return cls(
            building_id=data["building_id"],
            building_type=data["building_type"],
            name=data["name"],
            cost=data["cost"]
        )


# ============================================================================
# DISTRICT CLASS
# ============================================================================

class District:
    """Represents a player-owned settlement district."""

    def __init__(
        self,
        district_id: str,
        name: str,
        location: str
    ):
        self.district_id = district_id
        self.name = name
        self.location = location

        # Progression
        self.level = 1
        self.population = 0

        # Buildings
        self.buildings: List[Building] = []
        self.max_building_slots = 10  # Increases with level

        # Security
        self.security_level = 0

    @property
    def population_capacity(self) -> int:
        """Calculate total population capacity."""
        base_capacity = 5  # Base capacity
        housing_capacity = sum(b.get_population_capacity() for b in self.buildings)
        return base_capacity + housing_capacity

    def calculate_income(self) -> int:
        """Calculate income per hour from district."""
        # Base income (scavenging)
        base_income = MIN_DISTRICT_INCOME

        # Income from commerce buildings
        building_income = sum(b.get_income_bonus() for b in self.buildings)

        # Population bonus (+5 credits per person)
        population_bonus = self.population * 5

        # Infrastructure efficiency bonus
        infrastructure_bonus = sum(b.get_infrastructure_bonus() for b in self.buildings)
        efficiency_multiplier = 1.0 + (infrastructure_bonus / 100)

        total_income = int((base_income + building_income + population_bonus) * efficiency_multiplier)

        # Cap at maximum
        return min(total_income, MAX_DISTRICT_INCOME)

    def calculate_security(self) -> int:
        """Calculate district security level (0-100)."""
        # Base security
        base_security = 5

        # Defense buildings
        defense_bonus = sum(b.get_security_bonus() for b in self.buildings)

        # Population provides some security (strength in numbers)
        population_security = self.population // 5

        total_security = base_security + defense_bonus + population_security

        # Cap at 100
        return min(total_security, 100)

    def calculate_threat_level(self) -> int:
        """Calculate current threat level (0-100)."""
        security = self.calculate_security()

        # Inverse of security
        base_threat = 100 - security

        # Higher population = more attractive target
        population_threat = min(self.population // 2, 20)

        # Higher income = more attractive target
        income = self.calculate_income()
        income_threat = min(income // 500, 20)

        total_threat = base_threat + population_threat + income_threat

        return min(total_threat, 100)

    def place_building(self, building: Building) -> bool:
        """
        Place a building in the district.

        Returns:
            True if placed successfully, False if no slots available
        """
        if len(self.buildings) >= self.max_building_slots:
            return False

        self.buildings.append(building)
        return True

    def remove_building(self, building_id: str) -> bool:
        """
        Remove a building from the district.

        Returns:
            True if removed, False if not found
        """
        for i, building in enumerate(self.buildings):
            if building.building_id == building_id:
                self.buildings.pop(i)
                return True
        return False

    def update_population(self, hours_passed: int):
        """Update population growth over time."""
        if self.population < self.population_capacity:
            # Population grows slowly
            growth_rate = 0.5  # 0.5 people per hour if under capacity
            growth = int(hours_passed * growth_rate)
            self.population = min(self.population + growth, self.population_capacity)

    def level_up(self) -> bool:
        """
        Level up the district.

        Returns:
            True if leveled up, False if already max level
        """
        if self.level >= MAX_DISTRICT_LEVEL:
            return False

        self.level += 1

        # Increase building slots with level
        self.max_building_slots = 10 + (self.level - 1) * 2

        return True

    def get_level_up_cost(self) -> int:
        """Get cost to level up district."""
        # Cost increases with level
        base_cost = 5000
        level_multiplier = self.level * 1.5

        return int(base_cost * level_multiplier)

    def get_available_buildings(self) -> List[Dict[str, Any]]:
        """Get list of buildings available at current level."""
        all_buildings = []

        # Level 1: Basic buildings
        if self.level >= 1:
            all_buildings.extend([
                {"type": "housing", "name": "Shack", "cost": 500, "level_required": 1},
                {"type": "commerce", "name": "Street Vendor", "cost": 800, "level_required": 1},
                {"type": "defense", "name": "Barricade", "cost": 1000, "level_required": 1}
            ])

        # Level 2+: Better buildings
        if self.level >= 2:
            all_buildings.extend([
                {"type": "housing", "name": "Apartment Block", "cost": 2000, "level_required": 2},
                {"type": "commerce", "name": "Shop", "cost": 3000, "level_required": 2},
                {"type": "defense", "name": "Auto-Turret", "cost": 4000, "level_required": 2},
                {"type": "infrastructure", "name": "Generator", "cost": 5000, "level_required": 2}
            ])

        # Level 5+: Advanced buildings
        if self.level >= 5:
            all_buildings.extend([
                {"type": "housing", "name": "Secure Complex", "cost": 8000, "level_required": 5},
                {"type": "commerce", "name": "Trade Hub", "cost": 10000, "level_required": 5},
                {"type": "defense", "name": "Defense Grid", "cost": 12000, "level_required": 5}
            ])

        return all_buildings

    def generate_random_event(self) -> Optional[Dict[str, Any]]:
        """
        Generate a random district event.

        Returns:
            Event dict or None if no event
        """
        # 20% chance of event per call
        if random.random() > 0.2:
            return None

        # Determine event type based on district state
        security = self.calculate_security()

        if security < 30 and random.random() < 0.7:
            # Attack event (more likely with low security)
            return {
                "event_type": "attack",
                "description": "Gang forces attacking the district!",
                "severity": "high"
            }
        elif self.population > 30 and random.random() < 0.5:
            # Positive event (more likely with high population)
            return {
                "event_type": "trade_opportunity",
                "description": "Traders offer lucrative deal",
                "severity": "low"
            }
        else:
            # Neutral event
            return {
                "event_type": "scavenger_find",
                "description": "Scavengers found useful supplies",
                "severity": "low"
            }

    def get_attack_chance(self) -> float:
        """Get probability of attack (0.0-1.0)."""
        threat = self.calculate_threat_level()

        # Threat translates to attack chance
        base_chance = threat / 200  # 50% threat = 25% attack chance

        return min(base_chance, 0.8)  # Cap at 80%

    def get_possible_event_types(self) -> List[str]:
        """Get list of possible event types based on district state."""
        event_types = ["scavenger_find"]

        # Attack possible if threat exists
        if self.calculate_threat_level() > 20:
            event_types.append("attack")

        # Trade opportunities with good population
        if self.population > 20:
            event_types.append("trade_opportunity")
            event_types.append("positive")

        return event_types

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "district_id": self.district_id,
            "name": self.name,
            "location": self.location,
            "level": self.level,
            "population": self.population,
            "security_level": self.security_level,
            "max_building_slots": self.max_building_slots,
            "buildings": [b.to_dict() for b in self.buildings]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'District':
        """Load from dictionary."""
        district = cls(
            district_id=data["district_id"],
            name=data["name"],
            location=data["location"]
        )

        district.level = data.get("level", 1)
        district.population = data.get("population", 0)
        district.security_level = data.get("security_level", 0)
        district.max_building_slots = data.get("max_building_slots", 10)

        # Restore buildings
        for building_data in data.get("buildings", []):
            building = Building.from_dict(building_data)
            district.buildings.append(building)

        return district
