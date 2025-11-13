"""
Comprehensive test suite for hacking.py (Hacking System)

Tests cover:
- Network access levels (Guest, User, Admin, Root)
- Breach protocols (hacking minigame mechanics)
- Quickhacks (combat hacking abilities)
- Device control (cameras, turrets, doors, terminals)
- ICE (Intrusion Countermeasure Electronics)
- Trace mechanics (detection risk over time)
- Tech skill requirements for hacks
- Failed hacks and alert states
- Integration with combat and stealth
- Serialization for save/load
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestNetworkAccess:
    """Test network access level system."""

    def test_guest_access_level(self):
        """Test guest-level network access."""
        from hacking import NetworkAccess

        access = NetworkAccess(level="guest")

        assert access.level == "guest"
        assert access.can_read_public() is True
        assert access.can_write() is False

    def test_user_access_level(self):
        """Test user-level network access."""
        from hacking import NetworkAccess

        access = NetworkAccess(level="user")

        assert access.level == "user"
        assert access.can_read_public() is True
        assert access.can_write() is True
        assert access.can_admin() is False

    def test_admin_access_level(self):
        """Test admin-level network access."""
        from hacking import NetworkAccess

        access = NetworkAccess(level="admin")

        assert access.can_admin() is True
        assert access.can_control_devices() is True

    def test_root_access_level(self):
        """Test root-level network access."""
        from hacking import NetworkAccess

        access = NetworkAccess(level="root")

        assert access.level == "root"
        assert access.can_do_anything() is True

    def test_escalate_privileges(self):
        """Test escalating access privileges."""
        from hacking import NetworkAccess

        access = NetworkAccess(level="guest")

        access.escalate_to("user")
        assert access.level == "user"

        access.escalate_to("admin")
        assert access.level == "admin"


class TestBreachProtocol:
    """Test breach protocol hacking minigame."""

    def test_create_breach_protocol(self):
        """Test creating breach protocol puzzle."""
        from hacking import BreachProtocol

        breach = BreachProtocol(
            difficulty=2,
            buffer_size=6
        )

        assert breach.difficulty == 2
        assert breach.buffer_size == 6

    def test_breach_has_code_matrix(self):
        """Test breach protocol has code matrix."""
        from hacking import BreachProtocol

        breach = BreachProtocol(difficulty=2, buffer_size=6)

        matrix = breach.get_code_matrix()

        assert len(matrix) > 0
        assert len(matrix[0]) > 0

    def test_breach_has_sequences(self):
        """Test breach protocol has target sequences."""
        from hacking import BreachProtocol

        breach = BreachProtocol(difficulty=3, buffer_size=6)

        sequences = breach.get_target_sequences()

        assert len(sequences) >= 1

    def test_select_code_from_matrix(self):
        """Test selecting code from matrix."""
        from hacking import BreachProtocol

        breach = BreachProtocol(difficulty=1, buffer_size=4)

        # Select first code
        result = breach.select_code(0, 0)

        assert result is True
        assert len(breach.selected_codes) == 1

    def test_complete_sequence(self):
        """Test completing a target sequence."""
        from hacking import BreachProtocol

        breach = BreachProtocol(difficulty=1, buffer_size=6)

        # Get target sequence
        sequences = breach.get_target_sequences()
        target = sequences[0]["sequence"]

        # Try to match sequence (simplified test)
        # In real game, player would need to find path through matrix
        success = breach.check_sequence_match(target)

        assert isinstance(success, bool)

    def test_breach_difficulty_affects_complexity(self):
        """Test higher difficulty creates harder puzzles."""
        from hacking import BreachProtocol

        easy_breach = BreachProtocol(difficulty=1, buffer_size=4)
        hard_breach = BreachProtocol(difficulty=5, buffer_size=8)

        # Harder breaches have more/longer sequences
        easy_sequences = easy_breach.get_target_sequences()
        hard_sequences = hard_breach.get_target_sequences()

        assert hard_breach.buffer_size >= easy_breach.buffer_size

    def test_breach_buffer_limit(self):
        """Test buffer limits number of selections."""
        from hacking import BreachProtocol

        breach = BreachProtocol(difficulty=1, buffer_size=3)

        # Try to exceed buffer
        for i in range(5):
            breach.select_code(0, 0)

        # Should be capped at buffer size
        assert len(breach.selected_codes) <= breach.buffer_size


class TestQuickhacks:
    """Test quickhack abilities."""

    def test_create_quickhack(self):
        """Test creating a quickhack."""
        from hacking import Quickhack

        hack = Quickhack(
            hack_id="blind_enemy",
            name="Reboot Optics",
            ram_cost=4,
            tech_required=5
        )

        assert hack.hack_id == "blind_enemy"
        assert hack.ram_cost == 4
        assert hack.tech_required == 5

    def test_offensive_quickhacks(self):
        """Test offensive quickhacks."""
        from hacking import Quickhack

        # Damage hack
        overheat = Quickhack(
            hack_id="overheat",
            name="Overheat",
            ram_cost=6,
            tech_required=6,
            effect_type="damage",
            effect_value=50
        )

        assert overheat.effect_type == "damage"
        assert overheat.effect_value == 50

    def test_control_quickhacks(self):
        """Test control/disable quickhacks."""
        from hacking import Quickhack

        # Disable hack
        disable_cyberware = Quickhack(
            hack_id="disable",
            name="Weapon Glitch",
            ram_cost=5,
            tech_required=7,
            effect_type="disable",
            duration=2
        )

        assert disable_cyberware.effect_type == "disable"

    def test_stealth_quickhacks(self):
        """Test stealth-focused quickhacks."""
        from hacking import Quickhack

        # Distraction hack
        distract = Quickhack(
            hack_id="distract",
            name="Distract Enemies",
            ram_cost=3,
            tech_required=4,
            effect_type="distraction"
        )

        assert distract.effect_type == "distraction"

    def test_quickhack_requires_tech(self):
        """Test quickhack requires minimum tech level."""
        from hacking import Quickhack, HackingManager

        manager = HackingManager()

        advanced_hack = Quickhack(
            hack_id="ultimate_hack",
            name="System Reset",
            ram_cost=10,
            tech_required=10
        )

        # Player with low tech
        can_use_low = manager.can_use_quickhack(advanced_hack, player_tech=5)
        assert can_use_low is False

        # Player with high tech
        can_use_high = manager.can_use_quickhack(advanced_hack, player_tech=10)
        assert can_use_high is True

    def test_quickhack_costs_ram(self):
        """Test quickhacks cost RAM."""
        from hacking import Quickhack, HackingManager

        manager = HackingManager(current_ram=10, max_ram=20)

        hack = Quickhack("test", "Test", ram_cost=5, tech_required=1)

        initial_ram = manager.current_ram
        manager.use_quickhack(hack, player_tech=5)

        assert manager.current_ram == initial_ram - 5


class TestDeviceControl:
    """Test hacking and controlling devices."""

    def test_create_hackable_device(self):
        """Test creating hackable device."""
        from hacking import HackableDevice

        camera = HackableDevice(
            device_id="camera_01",
            device_type="camera",
            access_required="user"
        )

        assert camera.device_id == "camera_01"
        assert camera.device_type == "camera"

    def test_hack_camera(self):
        """Test hacking security camera."""
        from hacking import HackableDevice, HackingManager

        camera = HackableDevice("cam", "camera", "user")
        manager = HackingManager()

        # Hack camera
        result = manager.hack_device(camera, player_access="admin")

        assert result is True
        assert camera.is_hacked()

    def test_hack_turret(self):
        """Test hacking auto-turret."""
        from hacking import HackableDevice

        turret = HackableDevice("turret_01", "turret", "admin")

        # Requires admin access
        assert turret.access_required == "admin"

    def test_hack_door(self):
        """Test hacking door lock."""
        from hacking import HackableDevice, HackingManager

        door = HackableDevice("door_01", "door", "user")
        manager = HackingManager()

        result = manager.hack_device(door, player_access="admin")

        assert result is True
        assert door.state == "unlocked"

    def test_hack_terminal(self):
        """Test hacking data terminal."""
        from hacking import HackableDevice

        terminal = HackableDevice("terminal", "terminal", "admin")

        # Can read data
        assert terminal.device_type == "terminal"

    def test_insufficient_access_fails(self):
        """Test hacking fails with insufficient access."""
        from hacking import HackableDevice, HackingManager

        secure_device = HackableDevice("secure", "door", "root")
        manager = HackingManager()

        # Try with user access (too low)
        result = manager.hack_device(secure_device, player_access="user")

        assert result is False

    def test_control_hacked_device(self):
        """Test controlling hacked device."""
        from hacking import HackableDevice

        turret = HackableDevice("turret", "turret", "admin")

        # Hack it
        turret.hack()

        # Control it
        turret.set_target("enemy_npc")

        assert turret.current_target == "enemy_npc"


class TestICE:
    """Test ICE (Intrusion Countermeasure Electronics)."""

    def test_create_ice(self):
        """Test creating ICE countermeasure."""
        from hacking import ICE

        ice = ICE(
            ice_id="black_ice",
            name="Black ICE",
            strength=5
        )

        assert ice.ice_id == "black_ice"
        assert ice.strength == 5

    def test_ice_damages_hacker(self):
        """Test ICE deals damage to hacker."""
        from hacking import ICE

        dangerous_ice = ICE("lethal", "Lethal ICE", strength=8)

        damage = dangerous_ice.calculate_damage()

        assert damage > 0

    def test_ice_strength_affects_damage(self):
        """Test stronger ICE deals more damage."""
        from hacking import ICE

        weak_ice = ICE("weak", "Weak ICE", strength=2)
        strong_ice = ICE("strong", "Strong ICE", strength=10)

        weak_damage = weak_ice.calculate_damage()
        strong_damage = strong_ice.calculate_damage()

        assert strong_damage > weak_damage

    def test_break_through_ice(self):
        """Test breaking through ICE with tech skill."""
        from hacking import ICE, HackingManager

        ice = ICE("ice", "ICE", strength=5)
        manager = HackingManager()

        # High tech can break ICE
        success = manager.break_ice(ice, player_tech=8)

        assert success is True

    def test_ice_triggers_trace(self):
        """Test ICE triggers trace when encountered."""
        from hacking import ICE, HackingManager

        ice = ICE("ice", "Trace ICE", strength=3)
        manager = HackingManager()

        # Encountering ICE starts trace
        manager.encounter_ice(ice)

        assert manager.is_being_traced()


class TestTraceMechanics:
    """Test trace/detection mechanics."""

    def test_trace_starts_on_detection(self):
        """Test trace begins when hacking detected."""
        from hacking import HackingManager

        manager = HackingManager()

        manager.start_trace()

        assert manager.is_being_traced()
        assert manager.trace_progress == 0

    def test_trace_increases_over_time(self):
        """Test trace progress increases."""
        from hacking import HackingManager

        manager = HackingManager()

        manager.start_trace()
        initial_progress = manager.trace_progress

        manager.update_trace(time_passed=5)

        assert manager.trace_progress > initial_progress

    def test_trace_complete_triggers_alert(self):
        """Test completed trace triggers alert."""
        from hacking import HackingManager

        manager = HackingManager()

        manager.start_trace()

        # Max out trace
        manager.trace_progress = 100

        assert manager.is_trace_complete()

    def test_disconnect_stops_trace(self):
        """Test disconnecting stops trace."""
        from hacking import HackingManager

        manager = HackingManager()

        manager.start_trace()
        assert manager.is_being_traced()

        manager.disconnect()

        assert not manager.is_being_traced()

    def test_higher_tech_slows_trace(self):
        """Test high tech skill slows trace progress."""
        from hacking import HackingManager

        low_tech_manager = HackingManager(player_tech=3)
        high_tech_manager = HackingManager(player_tech=10)

        low_tech_manager.start_trace()
        high_tech_manager.start_trace()

        # Update both
        low_tech_manager.update_trace(5)
        high_tech_manager.update_trace(5)

        # High tech should have slower trace
        assert high_tech_manager.trace_progress < low_tech_manager.trace_progress


class TestHackingManager:
    """Test hacking manager."""

    def test_create_hacking_manager(self):
        """Test creating hacking manager."""
        from hacking import HackingManager

        manager = HackingManager()

        assert manager is not None

    def test_manager_tracks_ram(self):
        """Test manager tracks RAM for quickhacks."""
        from hacking import HackingManager

        manager = HackingManager(current_ram=15, max_ram=20)

        assert manager.current_ram == 15
        assert manager.max_ram == 20

    def test_ram_regenerates(self):
        """Test RAM regenerates over time."""
        from hacking import HackingManager

        manager = HackingManager(current_ram=5, max_ram=20)

        initial_ram = manager.current_ram

        manager.regenerate_ram(amount=5)

        assert manager.current_ram == initial_ram + 5

    def test_ram_capped_at_max(self):
        """Test RAM cannot exceed maximum."""
        from hacking import HackingManager

        manager = HackingManager(current_ram=18, max_ram=20)

        manager.regenerate_ram(amount=10)

        assert manager.current_ram == 20  # Capped

    def test_insufficient_ram_prevents_hack(self):
        """Test can't use quickhack without enough RAM."""
        from hacking import HackingManager, Quickhack

        manager = HackingManager(current_ram=3, max_ram=20)

        expensive_hack = Quickhack("hack", "Expensive", ram_cost=10, tech_required=1)

        result = manager.can_use_quickhack(expensive_hack, player_tech=5)

        # Should fail due to insufficient RAM
        assert result is False


class TestHackingIntegration:
    """Test hacking integration with other systems."""

    def test_quickhack_in_combat(self):
        """Test using quickhack during combat."""
        from hacking import Quickhack, HackingManager

        manager = HackingManager(current_ram=20, max_ram=20)

        combat_hack = Quickhack(
            hack_id="overheat",
            name="Overheat",
            ram_cost=6,
            tech_required=5,
            effect_type="damage",
            effect_value=40
        )

        # Use in combat
        result = manager.use_quickhack(combat_hack, player_tech=7, target="enemy_1")

        assert result is True
        assert manager.current_ram == 14  # 20 - 6

    def test_hacking_supports_stealth(self):
        """Test hacking cameras supports stealth."""
        from hacking import HackableDevice, HackingManager

        camera = HackableDevice("cam", "camera", "user")
        manager = HackingManager()

        # Hack camera to disable
        manager.hack_device(camera, player_access="admin")

        # Camera disabled = can sneak past
        assert camera.is_disabled()

    def test_hacked_turret_attacks_enemies(self):
        """Test hacked turret attacks enemies."""
        from hacking import HackableDevice

        turret = HackableDevice("turret", "turret", "admin")

        turret.hack()
        turret.set_faction("player")

        # Now attacks enemies instead of player
        assert turret.faction == "player"


class TestSerialization:
    """Test hacking system serialization."""

    def test_quickhack_to_dict(self):
        """Test converting quickhack to dictionary."""
        from hacking import Quickhack

        hack = Quickhack(
            hack_id="test",
            name="Test Hack",
            ram_cost=5,
            tech_required=6,
            effect_type="damage",
            effect_value=30
        )

        data = hack.to_dict()

        assert data["hack_id"] == "test"
        assert data["ram_cost"] == 5

    def test_quickhack_from_dict(self):
        """Test loading quickhack from dictionary."""
        from hacking import Quickhack

        data = {
            "hack_id": "loaded",
            "name": "Loaded Hack",
            "ram_cost": 8,
            "tech_required": 7,
            "effect_type": "disable",
            "effect_value": 0
        }

        hack = Quickhack.from_dict(data)

        assert hack.hack_id == "loaded"
        assert hack.ram_cost == 8

    def test_hacking_manager_to_dict(self):
        """Test converting hacking manager to dictionary."""
        from hacking import HackingManager

        manager = HackingManager(current_ram=12, max_ram=20)
        manager.start_trace()

        data = manager.to_dict()

        assert data["current_ram"] == 12
        assert data["is_being_traced"] is True

    def test_hacking_manager_from_dict(self):
        """Test loading hacking manager from dictionary."""
        from hacking import HackingManager

        data = {
            "current_ram": 15,
            "max_ram": 25,
            "is_being_traced": True,
            "trace_progress": 45
        }

        manager = HackingManager.from_dict(data)

        assert manager.current_ram == 15
        assert manager.is_being_traced()


class TestEdgeCases:
    """Test edge cases."""

    def test_hack_already_hacked_device(self):
        """Test hacking already-hacked device."""
        from hacking import HackableDevice, HackingManager

        device = HackableDevice("device", "camera", "user")
        manager = HackingManager()

        # Hack once
        manager.hack_device(device, player_access="admin")

        # Try again
        result = manager.hack_device(device, player_access="admin")

        # Should succeed (already hacked)
        assert result is True

    def test_zero_ram(self):
        """Test behavior with zero RAM."""
        from hacking import HackingManager, Quickhack

        manager = HackingManager(current_ram=0, max_ram=20)

        hack = Quickhack("hack", "Hack", ram_cost=5, tech_required=1)

        can_use = manager.can_use_quickhack(hack, player_tech=5)

        assert can_use is False

    def test_negative_trace_progress(self):
        """Test trace progress cannot go negative."""
        from hacking import HackingManager

        manager = HackingManager()
        manager.start_trace()

        manager.trace_progress = -10

        # Should be clamped to 0
        assert manager.trace_progress >= 0

    def test_disconnect_while_not_traced(self):
        """Test disconnecting when not being traced."""
        from hacking import HackingManager

        manager = HackingManager()

        # Not traced
        assert not manager.is_being_traced()

        # Try to disconnect
        manager.disconnect()

        # Should not error
        assert not manager.is_being_traced()

    def test_breach_protocol_empty_buffer(self):
        """Test breach protocol with no selections."""
        from hacking import BreachProtocol

        breach = BreachProtocol(difficulty=1, buffer_size=4)

        # No selections yet
        assert len(breach.selected_codes) == 0

        # Try to check sequence
        result = breach.check_sequence_match([])

        assert isinstance(result, bool)
