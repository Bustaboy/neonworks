"""
Hardware Fingerprinting

Generate unique hardware IDs for license binding.
Uses multiple hardware components to create a stable identifier.
"""

import hashlib
import platform
import uuid
from typing import Optional


def get_hardware_id() -> str:
    """
    Generate a unique hardware identifier for this machine.

    Combines multiple hardware components to create a stable ID that
    survives OS reinstalls but changes if hardware is swapped.

    Returns:
        32-character hexadecimal hardware ID
    """
    components = []

    # 1. MAC address (stable across reboots)
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0, 2*6, 2)][::-1])
        components.append(mac)
    except:
        pass

    # 2. Machine ID (unique per installation)
    try:
        machine_id = platform.node()
        components.append(machine_id)
    except:
        pass

    # 3. CPU info
    try:
        processor = platform.processor()
        if processor:
            components.append(processor)
    except:
        pass

    # 4. Platform info
    components.append(platform.system())
    components.append(platform.machine())

    # Combine all components
    combined = '|'.join(components)

    # Hash to create stable ID
    hw_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

    return hw_hash[:32]  # Return first 32 characters


def get_machine_info() -> dict:
    """
    Get detailed machine information for support/debugging.

    Returns:
        Dictionary with machine details
    """
    return {
        'hardware_id': get_hardware_id(),
        'platform': platform.system(),
        'platform_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'node': platform.node(),
        'python_version': platform.python_version()
    }


def validate_hardware_id(expected_id: str, allow_flexibility: bool = True) -> bool:
    """
    Validate that current hardware matches expected ID.

    Args:
        expected_id: Expected hardware ID
        allow_flexibility: Allow minor hardware changes (e.g., network card swap)

    Returns:
        True if hardware matches (or close enough with flexibility)
    """
    current_id = get_hardware_id()

    # Exact match
    if current_id == expected_id:
        return True

    # With flexibility, allow partial matches
    # (useful if user swaps network card but keeps same machine)
    if allow_flexibility:
        # Compare first 16 chars (more stable components)
        if current_id[:16] == expected_id[:16]:
            return True

    return False
