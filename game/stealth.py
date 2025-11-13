"""
Neon Collapse - Stealth System
Manages stealth detection, sight cones, noise, and AI awareness
"""

from typing import Dict, List, Any, Optional, Tuple
import math


# Constants
DETECTION_STATES = ["undetected", "suspicious", "alerted", "combat"]
AWARENESS_LEVELS = ["relaxed", "alert", "combat"]

# Noise levels
NOISE_FOOTSTEP = 20
NOISE_CROUCH_FOOTSTEP = 5
NOISE_GUNFIRE = 100
NOISE_DOOR = 30


# ============================================================================
# STEALTH STATE CLASS
# ============================================================================

class StealthState:
    """Manages player's stealth/detection state."""

    def __init__(self):
        self.detection_level = "undetected"
        self.detection_progress = 0
        self.light_level = 0.5  # 0.0 = darkness, 1.0 = bright light

    def is_detected(self) -> bool:
        """Check if player is detected."""
        return self.detection_level in ["alerted", "combat"]

    def is_in_combat(self) -> bool:
        """Check if in combat state."""
        return self.detection_level == "combat"

    def is_stealthy(self) -> bool:
        """Check if player is stealthy."""
        return self.detection_level == "undetected"

    def set_detection_level(self, level: str):
        """Set detection level."""
        if level in DETECTION_STATES:
            self.detection_level = level

    def increase_detection(self, amount: int):
        """
        Increase detection progress.

        Args:
            amount: Amount to increase
        """
        self.detection_progress += amount
        self.detection_progress = min(100, self.detection_progress)

        # Trigger state changes
        if self.detection_progress >= 100:
            self.detection_level = "alerted"
        elif self.detection_progress >= 50:
            self.detection_level = "suspicious"

    def decay_detection(self, time_passed: int):
        """
        Decay detection over time when hidden.

        Args:
            time_passed: Time units passed
        """
        decay_rate = 5  # Per time unit
        self.detection_progress -= decay_rate * time_passed
        self.detection_progress = max(0, self.detection_progress)

        # Return to undetected if progress drops
        if self.detection_progress < 25:
            self.detection_level = "undetected"

    def set_light_level(self, level: float):
        """Set ambient light level (0.0-1.0)."""
        self.light_level = max(0.0, min(1.0, level))

    def get_detection_modifier(self) -> float:
        """
        Get detection modifier based on light level.

        Returns:
            Multiplier for detection (lower = harder to detect)
        """
        # Dark = harder to detect
        if self.light_level < 0.3:
            return 0.5
        elif self.light_level > 0.7:
            return 1.5
        else:
            return 1.0

    def enter_combat(self):
        """Enter combat (breaks stealth)."""
        self.detection_level = "combat"
        self.detection_progress = 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "detection_level": self.detection_level,
            "detection_progress": self.detection_progress,
            "light_level": self.light_level
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StealthState':
        """Load from dictionary."""
        state = cls()
        state.detection_level = data.get("detection_level", "undetected")
        state.detection_progress = data.get("detection_progress", 0)
        state.light_level = data.get("light_level", 0.5)
        return state


# ============================================================================
# NOISE EVENT CLASS
# ============================================================================

class NoiseEvent:
    """Represents a noise/sound event."""

    def __init__(
        self,
        noise_type: str,
        position: Tuple[float, float],
        noise_level: int
    ):
        if noise_level < 0:
            raise ValueError(f"Noise level cannot be negative: {noise_level}")

        self.noise_type = noise_type
        self.position = position
        self.noise_level = noise_level

    def get_effective_radius(self) -> float:
        """Get radius at which noise can be heard."""
        return self.noise_level / 10


# ============================================================================
# PLAYER CLASS
# ============================================================================

class Player:
    """Player character for stealth."""

    def __init__(self):
        self.is_crouching = False
        self.position = (0, 0)

    def set_crouching(self, crouching: bool):
        """Set crouch state."""
        self.is_crouching = crouching

    def get_movement_speed(self, crouching: bool) -> float:
        """Get movement speed based on crouch state."""
        base_speed = 5.0

        if crouching:
            return base_speed * 0.6  # 40% slower when crouching

        return base_speed

    def get_footstep_noise(self) -> int:
        """Get footstep noise level."""
        if self.is_crouching:
            return NOISE_CROUCH_FOOTSTEP
        else:
            return NOISE_FOOTSTEP

    def get_detection_profile(self) -> float:
        """Get detection profile (visibility)."""
        if self.is_crouching:
            return 0.6  # Harder to spot when crouched
        else:
            return 1.0

    def get_stealth_rating(self, light_level: float) -> float:
        """
        Get overall stealth rating.

        Args:
            light_level: Ambient light (0.0-1.0)

        Returns:
            Stealth rating (higher = stealthier)
        """
        base_stealth = 50

        # Crouch bonus
        if self.is_crouching:
            base_stealth += 20

        # Darkness bonus
        darkness_bonus = (1.0 - light_level) * 30

        return base_stealth + darkness_bonus

    def attempt_takedown(
        self,
        enemy: 'EnemyAI',
        from_behind: bool,
        detected: bool
    ) -> bool:
        """
        Attempt stealth takedown.

        Args:
            enemy: Target enemy
            from_behind: Whether behind enemy
            detected: Whether player is detected

        Returns:
            True if successful
        """
        if not from_behind:
            return False

        if detected:
            return False

        return True

    def perform_stealth_kill_xp(self) -> int:
        """Get XP reward for stealth kill."""
        return 50  # Cool attribute XP


# ============================================================================
# ENEMY AI CLASS
# ============================================================================

class EnemyAI:
    """Enemy AI for stealth detection."""

    def __init__(
        self,
        enemy_id: str,
        position: Tuple[float, float],
        facing_direction: float  # Degrees
    ):
        self.enemy_id = enemy_id
        self.position = position
        self.facing_direction = facing_direction

        # Vision
        self.fov_angle = 90  # Field of view in degrees
        self.vision_range = 10
        self.light_level = 0.5

        # Awareness
        self.awareness_level = "relaxed"
        self.detection_state = "undetected"

        # Investigation
        self.is_investigating_flag = False
        self.investigation_target: Optional[Tuple[float, float]] = None
        self.investigation_timer = 0

    def can_see_position(self, target_pos: Tuple[float, float]) -> bool:
        """
        Check if can see target position.

        Args:
            target_pos: Target position to check

        Returns:
            True if in sight
        """
        # Calculate distance
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Zero distance means same position (can see)
        if distance < 0.1:
            return True

        # Check vision range
        effective_range = self.get_effective_vision_range()
        if distance > effective_range:
            return False

        # Check if in FOV cone
        # Convert to angle where 0=North, 90=East, 180=South, 270=West
        angle_to_target = (math.degrees(math.atan2(dx, dy)) + 360) % 360
        angle_diff = abs((angle_to_target - self.facing_direction + 180) % 360 - 180)

        if angle_diff > self.fov_angle / 2:
            return False

        return True

    def get_effective_vision_range(self) -> float:
        """Get effective vision range (affected by light)."""
        base_range = self.vision_range

        # Darkness reduces vision
        light_modifier = 0.5 + (self.light_level * 0.5)

        return base_range * light_modifier

    def set_light_level(self, level: float):
        """Set ambient light level."""
        self.light_level = max(0.0, min(1.0, level))

    def can_hear_noise(self, noise: NoiseEvent) -> bool:
        """
        Check if can hear noise.

        Args:
            noise: Noise event

        Returns:
            True if within hearing range
        """
        # Calculate distance to noise
        dx = noise.position[0] - self.position[0]
        dy = noise.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Check if within noise radius
        return distance <= noise.get_effective_radius()

    def increase_awareness(self, amount: int):
        """Increase awareness level."""
        # Simplified awareness tracking
        if amount >= 50:
            self.awareness_level = "alert"
        elif amount >= 80:
            self.awareness_level = "combat"

    def investigate_noise(self, noise: NoiseEvent):
        """Start investigating noise source."""
        self.start_investigation(noise.position)

    def start_investigation(self, position: Tuple[float, float]):
        """Start investigating a position."""
        self.is_investigating_flag = True
        self.investigation_target = position
        self.investigation_timer = 0

    def is_investigating(self) -> bool:
        """Check if currently investigating."""
        return self.is_investigating_flag

    def update_investigation(self, time_passed: int):
        """
        Update investigation state.

        Args:
            time_passed: Time units passed
        """
        if not self.is_investigating_flag:
            return

        self.investigation_timer += time_passed

        # Timeout after 20 time units
        if self.investigation_timer >= 20:
            self.is_investigating_flag = False
            self.investigation_target = None
            self.investigation_timer = 0

    def spot_player(self, player_pos: Tuple[float, float]):
        """Player spotted - enter combat."""
        self.detection_state = "combat"
        self.awareness_level = "combat"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enemy_id": self.enemy_id,
            "position": self.position,
            "facing_direction": self.facing_direction,
            "awareness_level": self.awareness_level,
            "detection_state": self.detection_state,
            "is_investigating": self.is_investigating_flag,
            "investigation_target": self.investigation_target
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnemyAI':
        """Load from dictionary."""
        enemy = cls(
            enemy_id=data["enemy_id"],
            position=tuple(data["position"]),
            facing_direction=data["facing_direction"]
        )

        enemy.awareness_level = data.get("awareness_level", "relaxed")
        enemy.detection_state = data.get("detection_state", "undetected")
        enemy.is_investigating_flag = data.get("is_investigating", False)

        target = data.get("investigation_target")
        if target:
            enemy.investigation_target = tuple(target)

        return enemy
