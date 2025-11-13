"""
Neon Collapse - Hacking System
Manages network access, breach protocols, quickhacks, device control, and ICE
"""

from typing import Dict, List, Any, Optional
import random


# Constants
ACCESS_LEVELS = ["guest", "user", "admin", "root"]
ACCESS_HIERARCHY = {"guest": 0, "user": 1, "admin": 2, "root": 3}

DEVICE_TYPES = ["camera", "turret", "door", "terminal"]

# Code matrix symbols for breach protocol
BREACH_CODES = ["1C", "55", "7A", "BD", "E9", "FF"]


# ============================================================================
# NETWORK ACCESS CLASS
# ============================================================================

class NetworkAccess:
    """Represents network access level."""

    def __init__(self, level: str = "guest"):
        if level not in ACCESS_LEVELS:
            raise ValueError(f"Invalid access level: {level}")

        self.level = level

    def can_read_public(self) -> bool:
        """Check if can read public data."""
        return True  # All levels can read public

    def can_write(self) -> bool:
        """Check if can write data."""
        return ACCESS_HIERARCHY[self.level] >= ACCESS_HIERARCHY["user"]

    def can_admin(self) -> bool:
        """Check if has admin privileges."""
        return ACCESS_HIERARCHY[self.level] >= ACCESS_HIERARCHY["admin"]

    def can_do_anything(self) -> bool:
        """Check if has root access."""
        return self.level == "root"

    def can_control_devices(self) -> bool:
        """Check if can control devices."""
        return self.can_admin()

    def escalate_to(self, new_level: str):
        """Escalate to higher access level."""
        if ACCESS_HIERARCHY[new_level] > ACCESS_HIERARCHY[self.level]:
            self.level = new_level


# ============================================================================
# BREACH PROTOCOL CLASS
# ============================================================================

class BreachProtocol:
    """Breach protocol hacking minigame."""

    def __init__(self, difficulty: int, buffer_size: int):
        self.difficulty = difficulty
        self.buffer_size = buffer_size
        self.selected_codes: List[str] = []

        # Generate code matrix
        matrix_size = 5 + difficulty
        self.code_matrix = self._generate_matrix(matrix_size)

        # Generate target sequences
        self.target_sequences = self._generate_sequences()

    def _generate_matrix(self, size: int) -> List[List[str]]:
        """Generate random code matrix."""
        matrix = []
        for _ in range(size):
            row = [random.choice(BREACH_CODES) for _ in range(size)]
            matrix.append(row)
        return matrix

    def _generate_sequences(self) -> List[Dict[str, Any]]:
        """Generate target sequences to match."""
        sequences = []

        # Number of sequences based on difficulty
        num_sequences = min(self.difficulty, 3)

        for i in range(num_sequences):
            sequence_length = 2 + (self.difficulty // 2)
            sequence = [random.choice(BREACH_CODES) for _ in range(sequence_length)]

            sequences.append({
                "sequence": sequence,
                "reward": f"reward_{i}"
            })

        return sequences

    def get_code_matrix(self) -> List[List[str]]:
        """Get the code matrix."""
        return self.code_matrix

    def get_target_sequences(self) -> List[Dict[str, Any]]:
        """Get target sequences."""
        return self.target_sequences

    def select_code(self, row: int, col: int) -> bool:
        """
        Select a code from the matrix.

        Args:
            row: Row index
            col: Column index

        Returns:
            True if selection valid
        """
        if len(self.selected_codes) >= self.buffer_size:
            return False

        if row < 0 or row >= len(self.code_matrix):
            return False
        if col < 0 or col >= len(self.code_matrix[0]):
            return False

        code = self.code_matrix[row][col]
        self.selected_codes.append(code)

        return True

    def check_sequence_match(self, target_sequence: List[str]) -> bool:
        """
        Check if selected codes match target sequence.

        Args:
            target_sequence: Sequence to match

        Returns:
            True if matched
        """
        if len(target_sequence) == 0:
            return False

        # Check if target sequence is in selected codes
        target_str = "".join(target_sequence)
        selected_str = "".join(self.selected_codes)

        return target_str in selected_str


# ============================================================================
# QUICKHACK CLASS
# ============================================================================

class Quickhack:
    """Represents a quickhack ability."""

    def __init__(
        self,
        hack_id: str,
        name: str,
        ram_cost: int,
        tech_required: int,
        effect_type: str = "damage",
        effect_value: int = 0,
        duration: int = 0
    ):
        self.hack_id = hack_id
        self.name = name
        self.ram_cost = ram_cost
        self.tech_required = tech_required
        self.effect_type = effect_type  # damage, disable, distraction, etc.
        self.effect_value = effect_value
        self.duration = duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hack_id": self.hack_id,
            "name": self.name,
            "ram_cost": self.ram_cost,
            "tech_required": self.tech_required,
            "effect_type": self.effect_type,
            "effect_value": self.effect_value,
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quickhack':
        """Load from dictionary."""
        return cls(
            hack_id=data["hack_id"],
            name=data["name"],
            ram_cost=data["ram_cost"],
            tech_required=data["tech_required"],
            effect_type=data.get("effect_type", "damage"),
            effect_value=data.get("effect_value", 0),
            duration=data.get("duration", 0)
        )


# ============================================================================
# HACKABLE DEVICE CLASS
# ============================================================================

class HackableDevice:
    """Represents a hackable device (camera, turret, door, etc)."""

    def __init__(
        self,
        device_id: str,
        device_type: str,
        access_required: str
    ):
        if device_type not in DEVICE_TYPES:
            # Allow it for now, just validate known types
            pass

        self.device_id = device_id
        self.device_type = device_type
        self.access_required = access_required
        self.hacked = False
        self.state = "active"  # active, disabled, unlocked
        self.current_target: Optional[str] = None
        self.faction = "enemy"

    def hack(self):
        """Mark device as hacked."""
        self.hacked = True

        if self.device_type == "door":
            self.state = "unlocked"
        elif self.device_type in ["camera", "turret"]:
            self.state = "disabled"

    def is_hacked(self) -> bool:
        """Check if device is hacked."""
        return self.hacked

    def is_disabled(self) -> bool:
        """Check if device is disabled."""
        return self.state == "disabled"

    def set_target(self, target: str):
        """Set device target (for turrets)."""
        if self.device_type == "turret" and self.hacked:
            self.current_target = target

    def set_faction(self, faction: str):
        """Set device faction (player/enemy)."""
        if self.hacked:
            self.faction = faction


# ============================================================================
# ICE CLASS
# ============================================================================

class ICE:
    """Intrusion Countermeasure Electronics."""

    def __init__(
        self,
        ice_id: str,
        name: str,
        strength: int
    ):
        self.ice_id = ice_id
        self.name = name
        self.strength = strength

    def calculate_damage(self) -> int:
        """Calculate damage dealt to hacker."""
        base_damage = 10
        return base_damage + (self.strength * 5)


# ============================================================================
# HACKING MANAGER CLASS
# ============================================================================

class HackingManager:
    """Manages hacking state and operations."""

    def __init__(
        self,
        current_ram: int = 20,
        max_ram: int = 20,
        player_tech: int = 0
    ):
        self.current_ram = current_ram
        self.max_ram = max_ram
        self.player_tech = player_tech

        # Trace tracking
        self.is_traced = False
        self._trace_progress = 0

    @property
    def trace_progress(self) -> int:
        """Get trace progress."""
        return self._trace_progress

    @trace_progress.setter
    def trace_progress(self, value: int):
        """Set trace progress (clamped 0-100)."""
        self._trace_progress = max(0, min(100, value))

    def can_use_quickhack(self, hack: Quickhack, player_tech: int) -> bool:
        """
        Check if player can use quickhack.

        Args:
            hack: Quickhack to check
            player_tech: Player's tech level

        Returns:
            True if can use
        """
        # Check tech requirement
        if player_tech < hack.tech_required:
            return False

        # Check RAM cost
        if self.current_ram < hack.ram_cost:
            return False

        return True

    def use_quickhack(
        self,
        hack: Quickhack,
        player_tech: int,
        target: Optional[str] = None
    ) -> bool:
        """
        Use a quickhack.

        Args:
            hack: Quickhack to use
            player_tech: Player's tech level
            target: Target of hack

        Returns:
            True if successful
        """
        if not self.can_use_quickhack(hack, player_tech):
            return False

        # Deduct RAM
        self.current_ram -= hack.ram_cost
        self.current_ram = max(0, self.current_ram)

        return True

    def regenerate_ram(self, amount: int):
        """Regenerate RAM."""
        self.current_ram = min(self.current_ram + amount, self.max_ram)

    def hack_device(
        self,
        device: HackableDevice,
        player_access: str
    ) -> bool:
        """
        Hack a device.

        Args:
            device: Device to hack
            player_access: Player's access level

        Returns:
            True if successful
        """
        # Check if player has sufficient access
        required_level = ACCESS_HIERARCHY[device.access_required]
        player_level = ACCESS_HIERARCHY[player_access]

        if player_level < required_level:
            return False

        # Hack device
        device.hack()
        return True

    def break_ice(self, ice: ICE, player_tech: int) -> bool:
        """
        Attempt to break through ICE.

        Args:
            ice: ICE to break
            player_tech: Player's tech skill

        Returns:
            True if successful
        """
        # Tech skill vs ICE strength
        return player_tech >= ice.strength

    def encounter_ice(self, ice: ICE):
        """Encounter ICE (starts trace)."""
        self.start_trace()

    def start_trace(self):
        """Start trace/detection."""
        self.is_traced = True
        self._trace_progress = 0

    def is_being_traced(self) -> bool:
        """Check if being traced."""
        return self.is_traced

    def update_trace(self, time_passed: int):
        """
        Update trace progress.

        Args:
            time_passed: Time units passed
        """
        if not self.is_traced:
            return

        # Base trace rate
        trace_rate = 10  # Base progress per time unit

        # Tech skill slows trace
        tech_reduction = self.player_tech * 0.5
        effective_rate = max(1, trace_rate - tech_reduction)

        self.trace_progress += effective_rate * time_passed
        self.trace_progress = max(0, min(100, self.trace_progress))

    def is_trace_complete(self) -> bool:
        """Check if trace is complete (100%)."""
        return self.trace_progress >= 100

    def disconnect(self):
        """Disconnect from network (stops trace)."""
        self.is_traced = False
        self._trace_progress = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_ram": self.current_ram,
            "max_ram": self.max_ram,
            "is_being_traced": self.is_traced,
            "trace_progress": self.trace_progress
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HackingManager':
        """Load from dictionary."""
        manager = cls(
            current_ram=data["current_ram"],
            max_ram=data["max_ram"]
        )

        manager.is_traced = data.get("is_being_traced", False)
        manager.trace_progress = data.get("trace_progress", 0)

        return manager
