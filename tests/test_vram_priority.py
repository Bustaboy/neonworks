"""
Tests for VRAM Priority Levels

Simple validation tests for VRAMPriority constants.
"""

import pytest

from ai.vram_priority import VRAMPriority


class TestVRAMPriority:
    """Test suite for VRAMPriority constants."""

    def test_priority_values(self):
        """Test that priority constants have correct values."""
        assert VRAMPriority.BACKGROUND == 1
        assert VRAMPriority.NORMAL == 5
        assert VRAMPriority.USER_REQUESTED == 8
        assert VRAMPriority.UI_CRITICAL == 10

    def test_priority_ordering(self):
        """Test that priorities are correctly ordered (higher = more important)."""
        assert VRAMPriority.BACKGROUND < VRAMPriority.NORMAL
        assert VRAMPriority.NORMAL < VRAMPriority.USER_REQUESTED
        assert VRAMPriority.USER_REQUESTED < VRAMPriority.UI_CRITICAL

    def test_priority_comparison(self):
        """Test priority comparisons for eviction logic."""
        # Higher priority can evict lower priority
        assert VRAMPriority.USER_REQUESTED > VRAMPriority.NORMAL
        assert VRAMPriority.NORMAL > VRAMPriority.BACKGROUND

        # Same priority should be equal
        assert VRAMPriority.NORMAL == VRAMPriority.NORMAL

    def test_priority_differences(self):
        """Test that priority levels are spaced appropriately."""
        # Ensure meaningful gaps between levels
        assert VRAMPriority.NORMAL - VRAMPriority.BACKGROUND == 4
        assert VRAMPriority.USER_REQUESTED - VRAMPriority.NORMAL == 3
        assert VRAMPriority.UI_CRITICAL - VRAMPriority.USER_REQUESTED == 2
