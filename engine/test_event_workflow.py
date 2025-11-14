"""
Event System Workflow Test

Tests the complete event editor workflow:
1. Create event
2. Add commands
3. Place on map
4. Save/load
5. Verify data integrity
"""

import json
from pathlib import Path

from engine.core.event_data import (
    EventManager,
    EventPage,
    EventTrigger,
    GameEvent,
    create_chest_event,
    create_door_event,
    create_npc_event,
)


def test_event_creation():
    """Test creating events with different configurations."""
    print("\n" + "=" * 60)
    print("TEST 1: Event Creation")
    print("=" * 60)

    # Test basic event creation
    event = GameEvent(id=1, name="Test Event", x=5, y=10)
    assert event.name == "Test Event"
    assert event.x == 5
    assert event.y == 10
    assert len(event.pages) == 1
    print("✓ Basic event creation works")

    # Test event with commands
    event.pages[0].commands = [
        {"code": "SHOW_TEXT", "parameters": {"text": "Hello World!"}},
        {"code": "WAIT", "parameters": {"duration": 60}},
    ]
    assert len(event.pages[0].commands) == 2
    print("✓ Adding commands works")

    # Test multiple pages
    page2 = EventPage()
    page2.self_switch_valid = True
    page2.self_switch_ch = "A"
    event.pages.append(page2)
    assert len(event.pages) == 2
    print("✓ Multiple pages work")

    print("\n✅ Event Creation: PASSED")
    return True


def test_event_serialization():
    """Test converting events to/from dictionaries."""
    print("\n" + "=" * 60)
    print("TEST 2: Event Serialization")
    print("=" * 60)

    # Create event with complex data
    event = GameEvent(id=42, name="Complex Event", x=15, y=20)
    event.pages[0].trigger = EventTrigger.PLAYER_TOUCH
    event.pages[0].commands = [
        {"code": "SHOW_TEXT", "parameters": {"text": "Test message"}},
        {
            "code": "CONDITIONAL_BRANCH",
            "parameters": {
                "condition_type": "switch",
                "switch_id": 1,
                "switch_value": True,
            },
        },
    ]

    # Convert to dict
    data = event.to_dict()
    assert data["id"] == 42
    assert data["name"] == "Complex Event"
    assert len(data["pages"]) == 1
    print("✓ Event to dict conversion works")

    # Convert back to event
    restored = GameEvent.from_dict(data)
    assert restored.id == 42
    assert restored.name == "Complex Event"
    assert restored.x == 15
    assert restored.y == 20
    assert len(restored.pages[0].commands) == 2
    print("✓ Dict to event conversion works")

    print("\n✅ Event Serialization: PASSED")
    return True


def test_save_load():
    """Test saving and loading events to/from files."""
    print("\n" + "=" * 60)
    print("TEST 3: Save/Load Events")
    print("=" * 60)

    # Create event manager and events
    manager = EventManager()

    event1 = manager.create_event("Event 1", 5, 5)
    event1.pages[0].commands = [
        {"code": "SHOW_TEXT", "parameters": {"text": "First event"}},
    ]

    event2 = manager.create_event("Event 2", 10, 10)
    event2.pages[0].trigger = EventTrigger.AUTORUN
    event2.pages[0].commands = [
        {"code": "SHOW_TEXT", "parameters": {"text": "Second event"}},
    ]

    # Save to file
    test_file = Path("data/test_events.json")
    manager.save_to_file(test_file)
    assert test_file.exists()
    print(f"✓ Saved events to {test_file}")

    # Create new manager and load
    manager2 = EventManager()
    success = manager2.load_from_file(test_file)
    assert success
    print(f"✓ Loaded events from {test_file}")

    # Verify data
    assert len(manager2.events) == 2
    loaded_event1 = manager2.get_event(1)
    assert loaded_event1 is not None
    assert loaded_event1.name == "Event 1"
    assert loaded_event1.x == 5
    assert loaded_event1.y == 5
    print("✓ Event data integrity verified")

    # Cleanup
    test_file.unlink()
    print("✓ Test file cleaned up")

    print("\n✅ Save/Load Events: PASSED")
    return True


def test_template_events():
    """Test creating events from templates."""
    print("\n" + "=" * 60)
    print("TEST 4: Template Events")
    print("=" * 60)

    # Test door event
    door = create_door_event(x=5, y=5, target_map="map_002", target_x=10, target_y=10)
    assert door.name == "Door"
    assert len(door.pages[0].commands) == 1
    assert door.pages[0].commands[0]["code"] == "TRANSFER_PLAYER"
    print("✓ Door event template works")

    # Test chest event
    chest = create_chest_event(x=7, y=8, item_id=1, item_name="Potion")
    assert chest.name == "Chest"
    assert len(chest.pages) == 2  # Closed and opened states
    assert chest.pages[0].commands[0]["code"] == "SHOW_TEXT"
    print("✓ Chest event template works")

    # Test NPC event
    npc = create_npc_event(x=3, y=3, name="Villager", dialogue="Hello!", sprite="NPC1")
    assert npc.name == "Villager"
    assert npc.pages[0].graphic.character_name == "NPC1"
    print("✓ NPC event template works")

    print("\n✅ Template Events: PASSED")
    return True


def test_event_conditions():
    """Test event page conditions."""
    print("\n" + "=" * 60)
    print("TEST 5: Event Page Conditions")
    print("=" * 60)

    # Create event with multiple conditional pages
    event = GameEvent(id=1, name="Conditional Event")

    # Page 1: Requires switch 1 ON
    page1 = event.pages[0]
    page1.switch1_valid = True
    page1.switch1_id = 1
    page1.commands = [{"code": "SHOW_TEXT", "parameters": {"text": "Switch 1 is ON"}}]

    # Page 2: Requires self-switch A
    page2 = EventPage()
    page2.self_switch_valid = True
    page2.self_switch_ch = "A"
    page2.commands = [{"code": "SHOW_TEXT", "parameters": {"text": "Self-switch A is ON"}}]
    event.pages.append(page2)

    # Page 3: No conditions (default)
    page3 = EventPage()
    page3.commands = [{"code": "SHOW_TEXT", "parameters": {"text": "Default page"}}]
    event.pages.append(page3)

    # Test with switch 1 OFF
    switches = {1: False}
    variables = {}
    self_switches = {"A": False}

    active = event.get_active_page(switches, variables, self_switches)
    assert active is not None
    assert active.commands[0]["parameters"]["text"] == "Default page"
    print("✓ Default page activated correctly")

    # Test with switch 1 ON
    switches[1] = True
    active = event.get_active_page(switches, variables, self_switches)
    assert active.commands[0]["parameters"]["text"] == "Switch 1 is ON"
    print("✓ Conditional page activated correctly")

    print("\n✅ Event Page Conditions: PASSED")
    return True


def test_complete_workflow():
    """Test the complete event workflow."""
    print("\n" + "=" * 60)
    print("TEST 6: Complete Workflow")
    print("=" * 60)

    # Step 1: Create event
    print("\n→ Step 1: Create event")
    manager = EventManager()
    event = manager.create_event("Workflow Test", 12, 15)
    print(f"  Created event: {event.name} at ({event.x}, {event.y})")

    # Step 2: Add commands
    print("\n→ Step 2: Add commands")
    event.pages[0].commands = [
        {"code": "SHOW_TEXT", "parameters": {"text": "This is a test event!"}},
        {"code": "WAIT", "parameters": {"duration": 30}},
        {"code": "SHOW_TEXT", "parameters": {"text": "Testing complete!"}},
    ]
    print(f"  Added {len(event.pages[0].commands)} commands")

    # Step 3: Configure properties
    print("\n→ Step 3: Configure properties")
    event.pages[0].trigger = EventTrigger.ACTION_BUTTON
    event.pages[0].graphic.character_name = "Actor1"
    print(f"  Trigger: {event.pages[0].trigger.value}")
    print(f"  Graphic: {event.pages[0].graphic.character_name}")

    # Step 4: Save to file
    print("\n→ Step 4: Save to file")
    test_file = Path("data/workflow_test.json")
    manager.save_to_file(test_file)
    print(f"  Saved to: {test_file}")

    # Step 5: Load from file
    print("\n→ Step 5: Load from file")
    manager2 = EventManager()
    manager2.load_from_file(test_file)
    loaded_event = manager2.get_event(event.id)
    print(f"  Loaded event: {loaded_event.name}")

    # Step 6: Verify integrity
    print("\n→ Step 6: Verify data integrity")
    assert loaded_event.name == event.name
    assert loaded_event.x == event.x
    assert loaded_event.y == event.y
    assert len(loaded_event.pages[0].commands) == len(event.pages[0].commands)
    assert loaded_event.pages[0].graphic.character_name == event.pages[0].graphic.character_name
    print("  ✓ All data verified successfully")

    # Cleanup
    test_file.unlink()
    print("\n  ✓ Cleanup complete")

    print("\n✅ Complete Workflow: PASSED")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NEONWORKS EVENT SYSTEM - TEST SUITE")
    print("=" * 60)

    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)

    tests = [
        test_event_creation,
        test_event_serialization,
        test_save_load,
        test_template_events,
        test_event_conditions,
        test_complete_workflow,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
