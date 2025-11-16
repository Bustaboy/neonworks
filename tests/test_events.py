"""
Tests for AI Service Pygame Events

Validates event constant definitions and uniqueness.
"""

import pygame
import pytest

from ai.events import (
    IMAGE_GENERATION_COMPLETE,
    IMAGE_GENERATION_ERROR,
    IMAGE_MODEL_LOADED,
    IMAGE_MODEL_UNLOADED,
    VRAM_ALLOCATED,
    VRAM_ALLOCATION_FAILED,
    VRAM_RELEASED,
    VRAM_UNLOAD_REQUESTED,
)


class TestEventConstants:
    """Test suite for event constant definitions."""

    def test_event_types_are_integers(self):
        """Test that all event constants are integers."""
        assert isinstance(IMAGE_GENERATION_COMPLETE, int)
        assert isinstance(IMAGE_GENERATION_ERROR, int)
        assert isinstance(IMAGE_MODEL_LOADED, int)
        assert isinstance(IMAGE_MODEL_UNLOADED, int)
        assert isinstance(VRAM_ALLOCATED, int)
        assert isinstance(VRAM_RELEASED, int)
        assert isinstance(VRAM_ALLOCATION_FAILED, int)
        assert isinstance(VRAM_UNLOAD_REQUESTED, int)

    def test_event_types_are_unique(self):
        """Test that all event constants have unique values."""
        events = [
            IMAGE_GENERATION_COMPLETE,
            IMAGE_GENERATION_ERROR,
            IMAGE_MODEL_LOADED,
            IMAGE_MODEL_UNLOADED,
            VRAM_ALLOCATED,
            VRAM_RELEASED,
            VRAM_ALLOCATION_FAILED,
            VRAM_UNLOAD_REQUESTED,
        ]

        # Check uniqueness
        assert len(events) == len(set(events))

    def test_events_are_userevent_based(self):
        """Test that events are based on pygame.USEREVENT."""
        # All custom events should be >= pygame.USEREVENT
        assert IMAGE_GENERATION_COMPLETE >= pygame.USEREVENT
        assert IMAGE_GENERATION_ERROR >= pygame.USEREVENT
        assert IMAGE_MODEL_LOADED >= pygame.USEREVENT
        assert IMAGE_MODEL_UNLOADED >= pygame.USEREVENT
        assert VRAM_ALLOCATED >= pygame.USEREVENT
        assert VRAM_RELEASED >= pygame.USEREVENT
        assert VRAM_ALLOCATION_FAILED >= pygame.USEREVENT
        assert VRAM_UNLOAD_REQUESTED >= pygame.USEREVENT

    def test_event_offset_values(self):
        """Test that events have correct offsets from pygame.USEREVENT."""
        assert IMAGE_GENERATION_COMPLETE == pygame.USEREVENT + 1
        assert IMAGE_GENERATION_ERROR == pygame.USEREVENT + 2
        assert IMAGE_MODEL_LOADED == pygame.USEREVENT + 3
        assert IMAGE_MODEL_UNLOADED == pygame.USEREVENT + 4

        assert VRAM_ALLOCATED == pygame.USEREVENT + 9
        assert VRAM_RELEASED == pygame.USEREVENT + 10
        assert VRAM_ALLOCATION_FAILED == pygame.USEREVENT + 11
        assert VRAM_UNLOAD_REQUESTED == pygame.USEREVENT + 12

    def test_event_range_valid(self):
        """Test that events are within valid Pygame range (USEREVENT to USEREVENT+20)."""
        max_offset = 20  # Reserve up to USEREVENT+20

        events = [
            IMAGE_GENERATION_COMPLETE,
            IMAGE_GENERATION_ERROR,
            IMAGE_MODEL_LOADED,
            IMAGE_MODEL_UNLOADED,
            VRAM_ALLOCATED,
            VRAM_RELEASED,
            VRAM_ALLOCATION_FAILED,
            VRAM_UNLOAD_REQUESTED,
        ]

        for event in events:
            offset = event - pygame.USEREVENT
            assert (
                0 <= offset <= max_offset
            ), f"Event {event} has offset {offset} (max: {max_offset})"

    def test_image_events_grouped(self):
        """Test that image events are grouped together (1-4)."""
        assert IMAGE_GENERATION_COMPLETE < IMAGE_GENERATION_ERROR
        assert IMAGE_GENERATION_ERROR < IMAGE_MODEL_LOADED
        assert IMAGE_MODEL_LOADED < IMAGE_MODEL_UNLOADED

        # All in range 1-4
        assert IMAGE_GENERATION_COMPLETE == pygame.USEREVENT + 1
        assert IMAGE_MODEL_UNLOADED == pygame.USEREVENT + 4

    def test_vram_events_grouped(self):
        """Test that VRAM events are grouped together (9-12)."""
        assert VRAM_ALLOCATED < VRAM_RELEASED
        assert VRAM_RELEASED < VRAM_ALLOCATION_FAILED
        assert VRAM_ALLOCATION_FAILED < VRAM_UNLOAD_REQUESTED

        # All in range 9-12
        assert VRAM_ALLOCATED == pygame.USEREVENT + 9
        assert VRAM_UNLOAD_REQUESTED == pygame.USEREVENT + 12

    def test_gap_for_llm_events(self):
        """Test that gap exists for future LLM events (5-8)."""
        # Verify gap between image and VRAM events
        last_image_event = IMAGE_MODEL_UNLOADED
        first_vram_event = VRAM_ALLOCATED

        gap = first_vram_event - last_image_event
        assert gap == 5  # Offsets 5, 6, 7, 8 reserved for LLM events
