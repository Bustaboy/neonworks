# NeonWorks Game Engine - Comprehensive Architecture Overview

**Version**: 0.1.0
**Status**: Production Ready
**Type**: Reusable, Project-Based 2D Game Engine
**Python**: 3.8+
**Framework**: Pygame

---

## 1. DIRECTORY STRUCTURE

### Root Engine Organization (`/engine/`)

```
engine/
├── core/                 # Core ECS and engine systems (5 files)
│   ├── ecs.py           # Entity Component System - the heart of the engine
│   ├── game_loop.py     # Main game loop with fixed timestep
│   ├── events.py        # Event system for decoupled communication
│   ├── state.py         # State management (MenuState, GameplayState, etc.)
│   ├── scene.py         # Scene system with transitions
│   ├── project.py       # Project management and loading
│   └── serialization.py # Save/load system
│
├── rendering/           # All rendering and UI systems (9 files)
│   ├── renderer.py      # 2D grid-based renderer
│   ├── camera.py        # Camera system (pan, zoom, follow)
│   ├── ui.py            # UI widget system and layout
│   ├── assets.py        # Asset loading and caching
│   ├── asset_pipeline.py # Asset processing pipeline
│   ├── animation.py     # Sprite animation and state machines
│   ├── tilemap.py       # Tilemap rendering
│   ├── particles.py     # Particle system for effects
│   └── __init__.py
│
├── systems/             # Game logic systems (4 files)
│   ├── turn_system.py   # Turn-based strategy mechanics
│   ├── base_building.py # Construction and building upgrades
│   ├── survival.py      # Hunger, thirst, energy management
│   ├── pathfinding.py   # A* pathfinding on navmesh
│   └── __init__.py
│
├── physics/             # Physics and collision (3 files)
│   ├── collision.py     # Collision detection with spatial partitioning
│   ├── rigidbody.py     # Physics body component
│   └── __init__.py
│
├── input/               # Input handling (2 files)
│   ├── input_manager.py # Keyboard, mouse, gamepad input
│   └── __init__.py
│
├── audio/               # Audio management (2 files)
│   ├── audio_manager.py # Sound and music playback
│   └── __init__.py
│
├── gameplay/            # Game-specific systems (2 files)
│   ├── character_controller.py # Character movement and control
│   ├── combat.py        # Combat system
│   └── __init__.py
│
├── ui/                  # Advanced UI systems (2 files)
│   ├── ui_system.py     # Comprehensive UI widget framework
│   └── __init__.py
│
├── data/                # Data management (3 files)
│   ├── serialization.py # Entity and component serialization
│   ├── config_loader.py # Configuration file loading
│   └── __init__.py
│
├── editor/              # AI-assisted editor tools (4 files)
│   ├── ai_navmesh.py    # AI-assisted navmesh generation
│   ├── ai_level_builder.py # AI level generation
│   ├── ai_writer.py     # AI quest/dialogue writing
│   ├── procedural_gen.py # Procedural generation tools
│   └── __init__.py
│
├── export/              # Export and licensing (7 files)
│   ├── exporter.py      # Game export/build system
│   ├── package_builder.py # Package creation
│   ├── executable_bundler.py # Executable generation
│   ├── installer_builder.py # Installer creation
│   ├── code_protection.py # Code encryption/obfuscation
│   ├── package_format.py # Custom package format
│   ├── package_loader.py # Package loading and verification
│   ├── __init__.py
│   └── export_cli.py    # CLI for export operations
│
├── licensing/           # Licensing system (3 files)
│   ├── license_key.py   # License key generation/validation
│   ├── hardware_id.py   # Hardware fingerprinting
│   ├── license_validator.py # License validation
│   └── __init__.py
│
├── ai/                  # AI systems (2 files)
│   ├── pathfinding.py   # (duplicate of systems/pathfinding.py)
│   └── __init__.py
│
├── tests/               # Engine unit tests (16+ test files)
│   └── test_*.py        # Comprehensive test suite
│
├── main.py              # Entry point for running projects
├── export_cli.py        # CLI for exporting games
├── license_cli.py       # CLI for license management
├── setup.py             # Package setup for pip install
├── __init__.py          # Package initialization
└── README.md            # Engine documentation
```

### Projects Directory (`/projects/`)

```
projects/
└── neon_collapse/       # Example/template project
    ├── project.json     # Project configuration (defines engine settings)
    ├── README.md        # Project documentation
    ├── config/
    │   └── buildings.json # Example building definitions
    ├── assets/          # (to be created: sprites, tiles, UI, sounds)
    ├── levels/          # (to be created: level definitions)
    ├── scripts/         # (to be created: custom logic)
    ├── saves/           # (auto-generated: save files)
    └── ...
```

---

## 2. CORE ARCHITECTURE: ENTITY COMPONENT SYSTEM (ECS)

### Located in: `/engine/core/ecs.py` (352 lines)

The ECS is the fundamental architecture pattern for flexible entity management.

#### Key Classes:

**`Component` (Base Class)**
```python
class Component:
    """Base class for all components - just data containers"""
    pass
```

**Built-in Components (Included):**
- **Transform**: x, y position, rotation, scale
- **GridPosition**: grid-based positioning (for tile-based games)
- **Sprite**: texture, dimensions, visibility
- **Health**: current/max health, regeneration
- **Survival**: hunger, thirst, energy (with decay rates)
- **Building**: type, construction progress, level
- **ResourceStorage**: resources and capacity
- **Navmesh**: walkable cells, movement costs
- **TurnActor**: action points, initiative
- **Collider**: collision box (width, height, layer, mask)
- **RigidBody**: velocity, mass, friction, gravity

**`Entity` Class**
```python
class Entity:
    id: str                              # Unique identifier
    _components: Dict[Type, Component]  # Component storage
    tags: Set[str]                      # Tags for grouping
    active: bool                        # Whether entity is active
    _world: Optional[World]             # Reference to parent world
```

Methods:
- `add_component(component)` → Entity (fluent)
- `remove_component(component_type)` → Entity
- `get_component(component_type)` → Optional[Component]
- `has_component(component_type)` → bool
- `has_components(*component_types)` → bool (all required)
- `add_tag(tag)` → Entity
- `remove_tag(tag)` → Entity
- `has_tag(tag)` → bool

**`System` (Abstract Base Class)**
```python
class System(ABC):
    enabled: bool = True
    priority: int = 0  # Lower numbers run first

    @abstractmethod
    def update(self, world: World, delta_time: float):
        """Called each frame"""
        pass

    def on_entity_added(self, entity: Entity):
        """Called when entity added to world"""
        pass

    def on_entity_removed(self, entity: Entity):
        """Called when entity removed from world"""
        pass
```

**`World` Class**
```python
class World:
    _entities: Dict[str, Entity]                           # All entities
    _systems: List[System]                                 # All systems
    _tags_to_entities: Dict[str, Set[str]]                # Tag index
    _component_to_entities: Dict[Type[Component], Set[str]]  # Component index
```

Methods:
- `create_entity(entity_id=None)` → Entity
- `add_entity(entity)` → World
- `remove_entity(entity_id)` → World
- `get_entity(entity_id)` → Optional[Entity]
- `get_entities()` → List[Entity]
- **`get_entities_with_component(Component)` → List[Entity]** (indexed)
- **`get_entities_with_components(*Components)` → List[Entity]** (intersection)
- **`get_entities_with_tag(tag)` → List[Entity]** (indexed)
- `add_system(system)` → World
- `remove_system(system)` → World
- `update(delta_time)` → void (calls all enabled systems)

### Design Pattern: Composition Over Inheritance
- Entities are just containers of components
- Systems operate on entities with specific component combinations
- Very flexible - add new behaviors by adding components, not inheritance

### Performance Optimizations:
- Entities indexed by component type
- Entities indexed by tag
- Fast intersection queries for multi-component queries
- Systems sorted by priority for deterministic execution order

---

## 3. CORE CLASSES AND THEIR RELATIONSHIPS

### 3.1 Game Loop (`/engine/core/game_loop.py` - 226 lines)

**`GameEngine` Class**
```python
class GameEngine:
    target_fps: int = 60
    fixed_timestep: float = 1.0/60.0

    # Core systems
    world: World                    # ECS world
    event_manager: EventManager     # Event system
    state_manager: StateManager     # State management
    input_manager: InputManager     # Input handling
    audio_manager: AudioManager     # Audio playback

    # Stats
    stats: dict                     # Performance metrics
```

**Game Loop Pattern (Fixed Timestep with Variable Rendering)**
```
while running:
    frame_start = now
    frame_time = current_time - last_time
    accumulator += frame_time

    # Fixed update loop (can run 0+ times per frame)
    while accumulator >= fixed_timestep:
        _fixed_update(fixed_timestep)  # Physics, logic
        accumulator -= fixed_timestep

    # Variable rendering (always once per frame)
    _render()

    # FPS limiting
    frame_duration = now - frame_start
    if frame_duration < target_frame_time:
        sleep(target_frame_time - frame_duration)
```

Fixed timestep ensures consistent physics regardless of frame rate.

**`EngineConfig` Class**
```python
class EngineConfig:
    # Display
    window_width: int = 1280
    window_height: int = 720
    fullscreen: bool = False
    vsync: bool = True

    # Performance
    target_fps: int = 60
    fixed_timestep: float = 1.0/60.0

    # Grid settings
    tile_size: int = 32
    grid_width: int = 100
    grid_height: int = 100

    # Features
    enable_particles: bool = True
    enable_shadows: bool = False
    render_navmesh: bool = False

    # Debug
    show_fps: bool = True
    show_debug_info: bool = False
    show_collision_boxes: bool = False
```

### 3.2 Project System (`/engine/core/project.py` - 310 lines)

**Project Configuration Hierarchy:**

```
ProjectConfig
├── metadata: ProjectMetadata
│   ├── name: str
│   ├── version: str
│   ├── description: str
│   ├── author: str
│   ├── engine_version: str
│   ├── created_date: str
│   └── modified_date: str
│
├── paths: ProjectPaths
│   ├── assets: str = "assets"
│   ├── levels: str = "levels"
│   ├── scripts: str = "scripts"
│   ├── saves: str = "saves"
│   └── config: str = "config"
│
├── settings: ProjectSettings
│   ├── window_title, window_width, window_height, fullscreen
│   ├── tile_size, grid_width, grid_height
│   ├── initial_scene, initial_level
│   ├── enable_base_building, enable_survival, enable_turn_based, enable_combat
│   ├── building_definitions, item_definitions, character_definitions, quest_definitions
│   ├── export_version, export_publisher, export_description
│   ├── export_icon, export_license, export_readme
│   ├── export_encrypt, export_compress, export_console
│   └── ...
│
└── custom_data: Dict[str, Any]  # Game-specific data
    └── Can contain anything (theme, difficulty levels, etc.)
```

**`Project` Class**
- `load()` → bool: Load project.json from disk
- `save()` → bool: Save project configuration
- `get_asset_path(relative_path)` → Path
- `get_level_path(level_name)` → Path
- `get_save_path(save_name)` → Path
- `get_config_path(config_name)` → Path
- `list_levels()` → List[str]
- `list_saves()` → List[str]

**`ProjectManager` Class**
- Singleton pattern with `get_project_manager()` global function
- `create_project(name, metadata, settings)` → Optional[Project]
- `load_project(name)` → Optional[Project]
- `list_projects()` → List[str]

### 3.3 Event System (`/engine/core/events.py` - 154 lines)

**Event Types (Enum)**
```python
class EventType(Enum):
    # Turn-based events
    TURN_START, TURN_END, ACTION_PERFORMED

    # Combat
    COMBAT_START, COMBAT_END, DAMAGE_DEALT, UNIT_DIED

    # Base building
    BUILDING_PLACED, BUILDING_COMPLETED, BUILDING_UPGRADED, BUILDING_DESTROYED

    # Survival
    HUNGER_CRITICAL, THIRST_CRITICAL, ENERGY_DEPLETED

    # Resources
    RESOURCE_COLLECTED, RESOURCE_CONSUMED, RESOURCE_DEPLETED

    # UI
    UI_BUTTON_CLICKED, UI_TILE_SELECTED, UI_ENTITY_SELECTED

    # Editor
    EDITOR_MODE_CHANGED, LEVEL_LOADED, LEVEL_SAVED, NAVMESH_GENERATED

    # Game state
    GAME_PAUSED, GAME_RESUMED, GAME_SAVED, GAME_LOADED
```

**`Event` Dataclass**
```python
@dataclass
class Event:
    event_type: EventType
    data: Dict[str, Any] = None  # Event-specific data
```

**`EventManager` Class**
```python
class EventManager:
    def subscribe(event_type: EventType, handler: Callable)
    def unsubscribe(event_type: EventType, handler: Callable)
    def emit(event: Event)                    # Queued
    def emit_immediate(event: Event)          # Immediate dispatch
    def process_events()                      # Dispatch all queued events
    def set_immediate_mode(immediate: bool)
    def clear_queue()
    def clear_handlers()
```

Singleton: `get_event_manager()` global function

### 3.4 State System (`/engine/core/state.py` - 200+ lines)

**State Transitions**
```python
class StateTransition(Enum):
    PUSH = auto()          # Push state onto stack
    POP = auto()           # Pop current state
    REPLACE = auto()       # Replace current state
    CLEAR_AND_PUSH = auto() # Clear and push
```

**`GameState` (Abstract Base Class)**
```python
class GameState(ABC):
    name: str
    _state_manager: StateManager

    @abstractmethod
    def enter(data: Dict[str, Any] = None)
    @abstractmethod
    def exit()
    @abstractmethod
    def update(delta_time: float)
    @abstractmethod
    def render()
    def handle_event(event)

    # Request scene changes through manager
    def change_state(name, transition, duration, data)
    def push_state(name, transition, duration, data)
    def pop_state(transition, duration)
```

**Built-in States**
- `MenuState`: Main menu
- `GameplayState`: Active gameplay
- `EditorState`: Level editor
- `LoadingState`: Loading screen
- `PauseState`: Pause menu

---

## 4. EXISTING SYSTEMS (IMPLEMENTATIONS OF System CLASS)

### 4.1 Turn System (`/engine/systems/turn_system.py` - 171 lines)

**Purpose**: Manage turn-based gameplay mechanics

**Key Features:**
- Initiative-based turn order
- Action points per turn
- Turn number tracking
- Player vs NPC turn tracking

**`TurnSystem` Methods:**
```python
update(world, delta_time)           # Main update
start_turn()                        # Begin actor's turn
end_turn()                          # End current turn, advance to next
use_action_points(entity, cost)    # Cost action points
end_actor_turn(entity)             # Mark as finished
get_current_actor()                 # Who's turn is it?
add_to_turn_order(entity)          # Add mid-game
remove_from_turn_order(entity)     # Remove mid-game
```

**Events Emitted:**
- `TURN_START` with entity_id, turn_number, is_player
- `TURN_END` with entity_id, turn_number
- `UNIT_DIED` when entity dies

### 4.2 Survival System (`/engine/systems/survival.py` - 153 lines)

**Purpose**: Manage hunger, thirst, energy needs

**Key Features:**
- Decay rates for each need
- Critical thresholds (20, 40)
- Damage when needs are critical
- Event-based alerts

**`SurvivalSystem` Methods:**
```python
consume_food(entity, amount)        # Restore hunger
consume_water(entity, amount)       # Restore thirst
rest(entity, amount)                # Restore energy
get_survival_state(entity)          # Returns state dict
```

**Constants:**
- `critical_threshold = 20.0`
- `danger_threshold = 40.0`
- `starvation_damage = 5.0` per turn
- `dehydration_damage = 10.0` per turn
- `exhaustion_damage = 3.0` per turn

### 4.3 Base Building System (`/engine/systems/base_building.py` - 200+ lines)

**Purpose**: Construction, upgrades, and building management

**`BuildingTemplate` Dataclass**
```python
@dataclass
class BuildingTemplate:
    building_type: str                          # "warehouse", "generator", etc.
    name: str
    description: str
    construction_cost: Dict[str, float]         # Resource requirements
    construction_time: float                    # In turns
    upgrade_costs: Dict[int, Dict[str, float]] # Level -> resources
    provides_storage: Dict[str, float]          # Resource storage
    produces_per_turn: Dict[str, float]         # Resource production
    consumes_per_turn: Dict[str, float]         # Resource consumption
    requires_buildings: List[str]               # Dependencies
```

**Default Buildings:**
- `warehouse`: Storage (500 metal, 300 food, 200 water)
- `generator`: Energy production (10 per turn)
- `hydroponics`: Food production (5/turn, consumes water/energy)
- `turret`: Defense
- `solar_panels`: Alternative energy

**`BuildingLibrary` Class**
- `register_template(template)`
- `get_template(building_type)`
- `list_templates()`

**`BuildingSystem` Class (System)**
- Manages building construction, upgrades, production/consumption

### 4.4 Pathfinding System (`/engine/systems/pathfinding.py` - 150+ lines)

**Purpose**: A* pathfinding on navmesh

**Algorithm**: A* with Manhattan/Euclidean heuristic

**`PathfindingSystem` Methods:**
```python
find_path(start_x, start_y, goal_x, goal_y, navmesh=None) → Optional[List[Tuple]]
```

**Features:**
- Navmesh caching
- Cost multipliers for different terrain
- Optimal path finding
- Used by AI and NPCs

---

## 5. RENDERING SYSTEMS

### 5.1 Renderer (`/engine/rendering/renderer.py` - 200+ lines)

**`Renderer` Class**
```python
class Renderer:
    width: int
    height: int
    tile_size: int
    screen: pygame.Surface
    camera: Camera
    asset_manager: AssetManager
    font: pygame.font.Font
    small_font: pygame.font.Font
```

**Key Methods:**
```python
clear(color=BLACK)                  # Clear screen
render_world(world)                 # Render all entities
render_sprite(transform, sprite)    # Render single sprite
render_grid_sprite(grid_pos, sprite)  # Render on grid
render_grid()                       # Draw grid lines
render_debug_info()                 # Debug overlay
set_title(title)                    # Window title
```

**Color Constants:**
```python
class Color:
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA
    GRAY, DARK_GRAY, LIGHT_GRAY
```

### 5.2 Camera (`/engine/rendering/camera.py` - 200+ lines)

**`Camera` Class**
- Pan, zoom, follow entity
- World-to-screen coordinate conversion
- Viewport management
- Smooth transitions

### 5.3 Asset Manager (`/engine/rendering/assets.py` - 300+ lines)

**`AssetManager` Class**
```python
class AssetManager:
    base_path: Path = "assets"
    _sprites: Dict[str, pygame.Surface]      # Cache
    _sprite_sheets: Dict[str, SpriteSheet]   # Cache
    _sounds: Dict[str, pygame.mixer.Sound]   # Cache
    _asset_sizes: Dict[str, int]             # Memory tracking
```

**Key Methods:**
```python
load_sprite(path, colorkey=None) → pygame.Surface
load_sprite_sheet(path, tile_width, tile_height) → SpriteSheet
load_sound(path) → pygame.mixer.Sound
preload_assets(paths)                # Batch load
get_memory_usage()                   # Memory info
clear_cache()                        # Free memory
```

**`SpriteSheet` Class**
```python
class SpriteSheet:
    surface: pygame.Surface
    tile_width: int
    tile_height: int

    get_sprite(x, y) → pygame.Surface          # By grid position
    get_sprite_by_index(index, columns) → pygame.Surface  # By index
```

Singleton: `get_asset_manager()` global function

### 5.4 Animation System (`/engine/rendering/animation.py` - 450+ lines)

**`AnimationFrame` Dataclass**
```python
@dataclass
class AnimationFrame:
    sprite_index: int
    duration: float
    callback: Optional[Callable] = None
```

**`Animation` Class**
- Frame management
- Playback control (play, pause, stop)
- Looping support
- Frame callbacks

**`AnimationStateMachine` Class**
- Multiple animations
- State transitions
- Automatic playback

### 5.5 Tilemap (`/engine/rendering/tilemap.py` - 400+ lines)

**`Tile` Dataclass**
```python
@dataclass
class Tile:
    tile_id: int
    sprite_index: int
    layer: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)
```

**`TileMap` Class**
- Grid-based tile storage
- Layer support
- Terrain painting
- Collision information

### 5.6 Particle System (`/engine/rendering/particles.py` - 600+ lines)

**`Particle` Dataclass**
```python
@dataclass
class Particle:
    x, y: float
    vx, vy: float                    # Velocity
    lifetime: float
    color: Tuple[int, int, int]
    size: float
```

**`ParticleEmitter` Class**
- Burst emissions
- Continuous emissions
- Fade-out effects
- Collision response

---

## 6. INPUT AND AUDIO

### 6.1 Input Manager (`/engine/input/input_manager.py` - 300+ lines)

**`InputState` Enum**
```python
class InputState(Enum):
    RELEASED      # Button is up
    JUST_PRESSED  # Pressed this frame
    HELD          # Being held
    JUST_RELEASED # Released this frame
```

**`InputManager` Class**
```python
class InputManager:
    # Tracking
    _keys_current: Set[int]
    _keys_previous: Set[int]
    _mouse_position: Tuple[int, int]
    _mouse_buttons_current: Set[int]
    _mouse_buttons_previous: Set[int]

    # Action mapping
    _action_map: Dict[str, Set[int]]  # Action name -> key codes
    _action_callbacks: Dict[str, Callable]

    # Input buffer (for responsive controls)
    _input_buffer: list
    _buffer_size = 10
    _buffer_time = 0.15  # 150ms buffer window

    # Text input
    _text_input_enabled: bool
    _text_input: str
```

**Default Action Mappings:**
```python
"move_up"       → W, UP
"move_down"     → S, DOWN
"move_left"     → A, LEFT
"move_right"    → D, RIGHT
"confirm"       → RETURN, SPACE
"cancel"        → ESCAPE, BACKSPACE
"interact"      → E
"menu"          → ESCAPE
"inventory"     → I
"map"           → M
"attack"        → SPACE
"ability1-4"    → 1-4
"debug_console" → ` (backtick)
```

**Key Methods:**
```python
process_event(pygame_event)         # Handle pygame events
update(delta_time)                  # Update state
map_action(name, keycodes)         # Custom binding
is_action_pressed(name) → bool     # Just pressed
is_action_held(name) → bool        # Currently held
get_action_state(name) → InputState
get_mouse_position() → Tuple[int, int]
is_mouse_button_pressed(button) → bool
enable_text_input()                # For text fields
get_text_input() → str
```

### 6.2 Audio Manager (`/engine/audio/audio_manager.py` - 250+ lines)

**`AudioManager` Class**
```python
class AudioManager:
    _sounds: Dict[str, pygame.mixer.Sound]  # Cache
    _music: Optional[pygame.mixer.music]
    _master_volume: float = 1.0
    _music_volume: float = 0.7
    _sfx_volume: float = 0.8
```

**Key Methods:**
```python
play_sound(sound_path, volume=1.0, loops=0) → int  # Channel ID
play_music(music_path, volume=1.0, loops=-1)
stop_sound(channel_id)
stop_all_sounds()
stop_music()
set_master_volume(volume: 0.0-1.0)
set_music_volume(volume: 0.0-1.0)
set_sfx_volume(volume: 0.0-1.0)
pause_sound(channel_id)
resume_sound(channel_id)
get_cache_info() → dict  # Number of playing sounds, etc.
```

---

## 7. PHYSICS AND COLLISION

### 7.1 Collision System (`/engine/physics/collision.py` - 300+ lines)

**`ColliderType` Enum**
```python
class ColliderType(Enum):
    AABB = "aabb"      # Axis-aligned bounding box
    CIRCLE = "circle"
    POINT = "point"
```

**`Collider` Component**
```python
@dataclass
class Collider(Component):
    collider_type: ColliderType = AABB
    width: float = 0.0
    height: float = 0.0
    radius: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    layer: int = 0              # Which layer this is on
    mask: int = 0xFFFFFFFF      # Which layers to collide with
    is_trigger: bool = False    # Trigger vs solid
    on_collision_enter: Optional[Callable]
    on_collision_stay: Optional[Callable]
    on_collision_exit: Optional[Callable]
```

**`CollisionInfo` Dataclass**
```python
@dataclass
class CollisionInfo:
    entity_a: Entity
    entity_b: Entity
    normal: Tuple[float, float]  # Collision normal
    penetration: float           # Penetration depth
    point: Tuple[float, float]   # Contact point
```

**`CollisionDetector` Class**
- `check_collision(entity_a, entity_b)` → Optional[CollisionInfo]
- AABB vs AABB collision
- Circle vs Circle collision
- AABB vs Circle collision

**`CollisionSystem` (System)**
- Collision detection each frame
- Spatial partitioning with QuadTree
- Callback invocation

### 7.2 RigidBody (`/engine/physics/rigidbody.py` - 150+ lines)

**`RigidBody` Component**
```python
@dataclass
class RigidBody(Component):
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    mass: float = 1.0
    friction: float = 0.1
    is_static: bool = False    # Static bodies don't move
    gravity_scale: float = 0.0 # For top-down games
```

---

## 8. UI SYSTEM

### UI System (`/engine/ui/ui_system.py` - 400+ lines)

**`Anchor` Enum**
```python
class Anchor(Enum):
    TOP_LEFT, TOP_CENTER, TOP_RIGHT
    CENTER_LEFT, CENTER, CENTER_RIGHT
    BOTTOM_LEFT, BOTTOM_CENTER, BOTTOM_RIGHT
```

**`UIStyle` Dataclass**
```python
@dataclass
class UIStyle:
    # Colors (RGBA)
    background_color: Tuple = (50, 50, 50, 200)
    border_color: Tuple = (150, 150, 150, 255)
    text_color: Tuple = (255, 255, 255, 255)
    hover_color: Tuple = (70, 70, 70, 200)
    active_color: Tuple = (90, 90, 90, 200)
    disabled_color: Tuple = (80, 80, 80, 150)

    # Sizing
    padding: int = 10
    margin: int = 5
    border_width: int = 2

    # Font
    font_name: Optional[str] = None
    font_size: int = 16
```

**`UIWidget` (Abstract Base Class)**
```python
class UIWidget(ABC):
    x, y: int
    width, height: int
    visible: bool = True
    enabled: bool = True
    hovered: bool
    pressed: bool
    anchor: Anchor = TOP_LEFT
    parent: Optional[UIContainer] = None
    style: UIStyle
    on_click: Optional[Callable]
    on_hover_enter: Optional[Callable]
    on_hover_exit: Optional[Callable]
```

**Key Methods:**
```python
get_rect() → pygame.Rect
contains_point(x, y) → bool
handle_event(event) → bool  # True if handled
update(delta_time)
render(screen)
```

**Widget Types:**
- `UILabel`: Text display
- `UIButton`: Clickable button
- `UITextInput`: Text input field
- `UIPanel`: Container/background
- `UISlider`: Range input
- `UICheckbox`: Boolean toggle
- `UIDropdown`: Selection menu
- `UIProgressBar`: Progress indication
- `UIContainer`: Layout container

---

## 9. DATA SERIALIZATION

### Serialization System (`/engine/data/serialization.py` - 200+ lines)

**`GameSerializer` Class**
```python
@staticmethod
def serialize_component(component: Component) → Dict[str, Any]
@staticmethod
def deserialize_component(data: Dict[str, Any]) → Component
@staticmethod
def serialize_entity(entity: Entity) → Dict[str, Any]
@staticmethod
def deserialize_entity(data: Dict[str, Any]) → Entity
@staticmethod
def serialize_world(world: World) → Dict[str, Any]
@staticmethod
def deserialize_world(data: Dict[str, Any]) → World
```

**`SaveGameManager` Class**
```python
class SaveGameManager:
    project: Project

    save_game(filename) → bool     # Save current state
    load_game(filename) → bool     # Load game state
    list_saves() → List[str]
    delete_save(filename) → bool
    get_save_info(filename) → dict # Metadata
```

**Serialization Format**: JSON-compatible dictionaries

---

## 10. EXAMPLE: PROJECT.JSON CONFIGURATION

Located at: `/projects/neon_collapse/project.json`

```json
{
  "metadata": {
    "name": "Neon Collapse",
    "version": "1.0.0",
    "description": "A cyberpunk turn-based strategy game",
    "author": "Neon Collapse Team",
    "engine_version": "0.1.0",
    "created_date": "2025-11-12",
    "modified_date": "2025-11-12"
  },
  "paths": {
    "assets": "assets",
    "levels": "levels",
    "scripts": "scripts",
    "saves": "saves",
    "config": "config"
  },
  "settings": {
    "window_title": "Neon Collapse",
    "window_width": 1280,
    "window_height": 720,
    "fullscreen": false,
    "tile_size": 32,
    "grid_width": 100,
    "grid_height": 100,
    "initial_scene": "menu",
    "initial_level": "tutorial",
    "enable_base_building": true,
    "enable_survival": true,
    "enable_turn_based": true,
    "enable_combat": true,
    "building_definitions": "config/buildings.json",
    "item_definitions": "config/items.json",
    "character_definitions": "config/characters.json",
    "quest_definitions": "config/quests.json"
  },
  "custom_data": {
    "game_mode": "campaign",
    "difficulty_levels": ["easy", "normal", "hard", "extreme"],
    "default_difficulty": "normal",
    "theme": "cyberpunk",
    "color_scheme": {
      "primary": "#00FFFF",
      "secondary": "#FF00FF",
      "accent": "#00FF00",
      "background": "#0A0A1A",
      "ui_background": "#1A1A2E"
    }
  }
}
```

---

## 11. MAIN APPLICATION ENTRY POINT

### `/neonworks/main.py` (216 lines)

**`GameApplication` Class**
```python
class GameApplication:
    def __init__(self, project_name: str)
    def run()
    def shutdown()

    def _create_engine_config() → EngineConfig
    def _setup_systems()  # Add systems based on project config
    def _setup_states()   # Initialize game states
```

**Initialization Flow:**
1. Load project via ProjectManager
2. Create EngineConfig from project settings
3. Initialize GameEngine
4. Initialize Renderer
5. Initialize SaveGameManager
6. Setup systems based on project settings
7. Setup game states (MenuState, GameplayState)
8. Start game loop

**Supported Systems (based on project.json):**
- `PathfindingSystem` - Always added
- `TurnSystem` - if `enable_turn_based=true`
- `BuildingSystem` - if `enable_base_building=true`
- `SurvivalSystem` - if `enable_survival=true`

**Usage:**
```bash
python -m neonworks.main project_name
```

---

## 12. KEY DESIGN PATTERNS

### 12.1 Entity Component System (ECS)
- Flexible entity composition
- Systems operate on component queries
- Decoupled from inheritance

### 12.2 Singleton Pattern
```python
get_event_manager()         # Global event manager
get_asset_manager()         # Global asset manager
get_project_manager()       # Global project manager
```

### 12.3 Manager Pattern
- `EventManager`: Event handling
- `ProjectManager`: Project loading
- `SaveGameManager`: Save/load
- `AssetManager`: Asset loading

### 12.4 Observer Pattern
- Event system (subscribe/emit)
- UI callbacks (on_click, on_hover)
- System entity notifications (on_entity_added, on_entity_removed)

### 12.5 Factory Pattern
- `ProjectManager.create_project()`
- `World.create_entity()`
- `AssetManager.load_sprite()`

### 12.6 Fluent Interface
- `entity.add_component(...).add_component(...).add_tag(...)`
- `world.add_entity(...).add_system(...)`

### 12.7 Strategy Pattern
- `CollisionDetector` with different collision types
- `ParticleEmitter` with different emission strategies

---

## 13. TESTING INFRASTRUCTURE

### Test Organization
```
/engine/tests/          # Engine tests
├── test_ecs.py                   # ECS system tests
├── test_game_loop.py             # Game loop tests
├── test_collision.py             # Collision detection
├── test_pathfinding.py           # A* pathfinding
├── test_scene.py                 # Scene management
├── test_animation.py             # Animation system
├── test_asset_manager.py         # Asset loading
├── test_input_manager.py         # Input handling
├── test_audio_manager.py         # Audio system
├── test_ui_system.py             # UI widgets
├── test_serialization.py         # Save/load
├── test_camera.py                # Camera system
├── test_tilemap.py               # Tilemap
├── test_particles.py             # Particle system
├── test_character_controller.py  # Character control
├── test_combat.py                # Combat system
├── test_export.py                # Export system
└── ...
```

### Test Configuration
- `pytest.ini`: Pytest configuration
- Test timeout: Prevents infinite loops
- Verbose output: Clear test names and results

### Running Tests
```bash
cd engine
pytest tests/
pytest tests/ -v                    # Verbose
pytest tests/ --cov=engine         # With coverage
pytest tests/ -k "test_ecs"        # Specific tests
```

---

## 14. EXISTING EXAMPLE PROJECT

### Location: `/projects/neon_collapse/`

**Status**: Template/Configuration only (not a complete game)

**What's Included:**
- ✅ `project.json` - Complete project configuration
- ✅ `README.md` - Documentation
- ✅ `config/buildings.json` - Example building definitions

**What's Missing:**
- ❌ `assets/` - Sprites, tiles, sounds, music
- ❌ `levels/` - Level definitions
- ❌ `scripts/` - Custom game logic

**Example Config Structure:**
```
projects/neon_collapse/
├── project.json
├── README.md
├── config/
│   └── buildings.json      # Warehouse, Generator, Hydroponics, Turret, etc.
├── assets/                 # (Create this)
├── levels/                 # (Create this)
├── scripts/                # (Create this)
└── saves/                  # (Auto-generated)
```

---

## 15. CODE PATTERNS AND BEST PRACTICES

### Entity Creation Pattern
```python
# Create entity with components
entity = world.create_entity()
entity.add_component(Transform(x=100, y=200))
entity.add_component(Sprite(texture="player.png", width=32, height=32))
entity.add_component(Health(current=100, maximum=100))
entity.add_component(TurnActor(action_points=2, initiative=10))
entity.add_tag("player")

# Query
all_units = world.get_entities_with_component(TurnActor)
hostile_units = [e for e in world.get_entities() if e.has_tag("enemy")]
```

### System Implementation Pattern
```python
class MySystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 0

    def update(self, world: World, delta_time: float):
        # Query entities with specific components
        entities = world.get_entities_with_components(Transform, Sprite)

        for entity in entities:
            transform = entity.get_component(Transform)
            sprite = entity.get_component(Sprite)
            # Process entity

    def on_entity_added(self, entity: Entity):
        # React to new entities
        pass

    def on_entity_removed(self, entity: Entity):
        # Clean up
        pass
```

### Event Pattern
```python
# Subscribe
event_manager.subscribe(EventType.TURN_START, my_handler)

# Emit
event_manager.emit(Event(
    EventType.UNIT_DIED,
    {
        "entity_id": entity.id,
        "cause": "starvation"
    }
))

# Handler
def my_handler(event: Event):
    print(f"Event: {event.event_type}")
    print(f"Data: {event.data}")
```

---

## 16. REQUIREMENTS

### Runtime Dependencies
See `/engine/requirements.txt`

### Development Dependencies
See `/engine/requirements-dev.txt`

**Common packages:**
- `pygame>=2.0` - Graphics and input
- `numpy>=1.20` - Numerical operations
- `pytest>=7.0` - Testing
- `pytest-cov>=4.0` - Code coverage
- `black>=23.0` - Code formatting
- `mypy>=1.0` - Type checking
- `flake8>=6.0` - Linting
- `pylint>=3.0` - Code analysis

---

## 17. SETUP.PY CONFIGURATION

Location: `/engine/setup.py`

```python
setup(
    name="neon-works",
    version="0.1.0",
    description="A comprehensive, project-based 2D game engine for turn-based strategy games",
    author="Neon Works Team",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=requirements,  # From requirements.txt
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.1",
            "mypy>=1.7.1",
            "flake8>=6.1.0",
            "pylint>=3.0.3",
            "isort>=5.13.2",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8+",
    ],
    keywords="game-engine pygame 2d turn-based strategy",
)
```

---

## 18. KEY FILES SUMMARY TABLE

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `core/ecs.py` | 352 | Entity Component System | Entity, Component, System, World |
| `core/game_loop.py` | 226 | Game loop with fixed timestep | GameEngine, EngineConfig |
| `core/events.py` | 154 | Event system | EventManager, Event, EventType |
| `core/state.py` | 200+ | State management | GameState, StateManager |
| `core/project.py` | 310 | Project loading | Project, ProjectConfig, ProjectManager |
| `core/serialization.py` | 200+ | Save/load system | GameSerializer, SaveGameManager |
| `rendering/renderer.py` | 200+ | 2D rendering | Renderer, Color |
| `rendering/camera.py` | 200+ | Camera system | Camera |
| `rendering/assets.py` | 300+ | Asset loading | AssetManager, SpriteSheet |
| `rendering/animation.py` | 450+ | Animation system | Animation, AnimationStateMachine |
| `rendering/ui.py` | 400+ | UI rendering | (merged into ui_system) |
| `rendering/tilemap.py` | 400+ | Tilemap | TileMap, Tile |
| `rendering/particles.py` | 600+ | Particle effects | ParticleEmitter, Particle |
| `systems/turn_system.py` | 171 | Turn-based mechanics | TurnSystem |
| `systems/survival.py` | 153 | Survival mechanics | SurvivalSystem |
| `systems/base_building.py` | 200+ | Building system | BuildingSystem, BuildingTemplate |
| `systems/pathfinding.py` | 150+ | A* pathfinding | PathfindingSystem, PathNode |
| `physics/collision.py` | 300+ | Collision detection | CollisionSystem, CollisionDetector |
| `physics/rigidbody.py` | 150+ | Physics bodies | (RigidBody component) |
| `input/input_manager.py` | 300+ | Input handling | InputManager |
| `audio/audio_manager.py` | 250+ | Audio playback | AudioManager |
| `ui/ui_system.py` | 400+ | UI widgets | UIWidget, UIButton, etc. |
| `main.py` | 216 | Application entry point | GameApplication |
| `setup.py` | 60 | Package configuration | setup() |

---

## SUMMARY: QUICK REFERENCE

### Creating a New Game Project

1. **Create project directory**: `mkdir projects/my_game`
2. **Create project.json**: Configure metadata, settings, features
3. **Create project structure**: assets/, levels/, config/, scripts/, saves/
4. **Run game**: `python -m neonworks.main my_game`

### Creating Custom Systems

1. **Inherit from System class**
2. **Implement update(world, delta_time)**
3. **Query entities**: `world.get_entities_with_components(...)`
4. **Add to world**: `world.add_system(my_system)`

### Creating Game Entities

1. **Create entity**: `entity = world.create_entity()`
2. **Add components**: `entity.add_component(ComponentType(...))`
3. **Add tags**: `entity.add_tag("player")`
4. **Query**: `world.get_entities_with_tag("player")`

### Event System Flow

1. **Subscribe**: `event_manager.subscribe(EventType.X, handler)`
2. **Emit**: `event_manager.emit(Event(EventType.X, data))`
3. **Process**: `event_manager.process_events()` (automatic in game loop)
4. **Handle**: Handler functions called with Event

---

## NEXT STEPS FOR DOCUMENTATION

Recommended documentation to create:

1. **Component Reference Guide** - All built-in components with examples
2. **System Implementation Guide** - How to create custom systems
3. **Project Configuration Guide** - Detailed project.json options
4. **Save/Load System Guide** - Serialization best practices
5. **AI Tools Documentation** - Navmesh editor, level builder
6. **Example Game Walkthrough** - Complete project tutorial
7. **API Reference** - Auto-generated from docstrings
8. **Performance Tuning Guide** - Optimization tips
9. **Testing Guide** - Unit and integration testing patterns
10. **Export Guide** - Building and packaging games
