# Changelog

All notable changes to Neon Collapse will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed - Critical Bug Fixes (2025-11-12)

#### Combat System
- **[CRITICAL]** Fixed escape notification never showing to players
  - Issue: Logic was inverted - checked `escape_available` flag AFTER setting it to True
  - Impact: Players couldn't see when escape became available
  - Fix: Check flag BEFORE setting it (combat.py:119-121)

- **[HIGH]** Fixed IndexError crash with empty teams
  - Issue: Combat initialization crashed if both teams empty
  - Impact: Runtime crash on edge case
  - Fix: Added validation to raise ValueError if no characters (combat.py:18-19)

- **[MEDIUM]** Fixed state management when all characters dead
  - Issue: Combat could enter undefined state
  - Impact: Game could hang or crash
  - Fix: Added tracking flag and wrap-around logic (combat.py:84-100)

#### Dialogue System
- **[HIGH]** Fixed KeyError in dialogue requirement checking
  - Issue: Direct dict access without validation (`req["attribute"]`, `req["level"]`)
  - Impact: Crashes when checking dialogue options
  - Fix: Changed to `.get()` with None checks (dialogue.py:258-272)

- **[HIGH]** Fixed None reference in requirement checks
  - Issue: None could be used as dictionary key
  - Impact: Logic errors in dialogue system
  - Fix: Added `if value is None: return False` checks (dialogue.py:222-249)

#### Quest System
- **[HIGH]** Fixed KeyError in get_active_quests()
  - Issue: Assumed all quest IDs exist in dictionary
  - Impact: Crashes when loading corrupted saves
  - Fix: Added filter `if quest_id in self.quests` (quest.py:376)

#### Save/Load System
- **[MEDIUM]** Fixed fragile save system
  - Issue: No error handling for `.to_dict()` calls
  - Impact: Single manager failure caused complete save failure
  - Fix: Wrapped each serialization in try-except (save_load.py:75-114)

#### Inventory System
- **[MEDIUM]** Fixed silent item loss documentation
  - Issue: Excess items silently discarded when exceeding max_stack
  - Impact: Players lose items without warning
  - Fix: Added detailed documentation and comments (inventory.py:338-342)

- **[LOW]** Clarified confusing return semantics in remove_item()
  - Issue: Returns False even when items removed
  - Impact: API confusion
  - Fix: Updated docstring with clear behavior documentation (inventory.py:392-396)

#### Code Quality
- **[LOW]** Removed unused variable
  - Issue: `threat` variable calculated but never used
  - Impact: Wasted computation
  - Fix: Removed unused line (district_building.py:280)

### Changed - Code Quality Improvements (2025-11-12)

#### Import Management
- Replaced all star imports with explicit imports (PEP 8 compliance)
  - `character.py`: 11 explicit constants from config
  - `combat.py`: 4 explicit constants (GRID_WIDTH, GRID_HEIGHT, AP_BASIC_ATTACK, AP_MOVE)
  - `main.py`: 14 explicit constants (screens, colors, stats)
  - `ui.py`: 24 explicit constants (complete UI configuration)
  - **Benefit**: Better IDE support, clearer dependencies, no namespace pollution

#### Function Complexity Reduction
- **combat.py - enemy_ai_turn()**: Complexity 11 → 2 (82% reduction)
  - Extracted 6 helper methods for AI logic
  - Now follows Single Responsibility Principle

- **dialogue.py - check_option_available()**: Complexity 14 → 5 (64% reduction)
  - Extracted 5 requirement checker methods
  - Implemented strategy pattern with dictionary lookup

- **faction.py - get_faction_rewards()**: Complexity 11 → 3 (73% reduction)
  - Replaced 10 sequential if statements with data structure
  - Rewards now defined in configuration dictionary

### Added - Infrastructure (2025-11-12)

#### Type Checking
- Added mypy configuration (mypy.ini)
  - Python 3.11 type checking enabled
  - Incremental strictness flags configured
  - Ignores pygame/pytest (no type stubs available)
  - Ready for gradual type safety improvements

#### Type Fixes
- Fixed type hint in world_map.py: `List[str] = None` → `Optional[List[str]] = None`

#### Build System
- Updated Makefile to use mypy.ini configuration
  - `make typecheck` now runs with proper config

### Metrics

#### Test Coverage
- Tests Passing: 880/892 ✅
- Tests Skipped: 12 (UI/pygame requirements)
- Overall Coverage: 78%
- Critical Errors: 0

#### Code Quality
- Complex Functions (>10): 5 → 3 (40% reduction)
- Star Imports: 4 → 0 (100% eliminated)
- Type Safety: None → Configured ✅

## [Previous Releases]

### Phase 5: Game Polish & Meta Systems
- 71 tests passing
- Achievement system
- AI director for dynamic difficulty
- Save/load functionality

### Phase 4: Advanced Gameplay Systems
- 111 tests passing
- Crafting system
- Companion system
- District building

### Phase 3: Core Combat
- Turn-based combat with initiative
- Cover system
- Stealth mechanics
- Status effects

### Phase 2: Character & Quest Systems
- Character progression (XP/leveling)
- Quest system with objectives
- Faction reputation

### Phase 1: Foundation
- Core game loop
- World map navigation
- Inventory system
- Vendor trading
