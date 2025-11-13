"""
Neon Collapse - Game Configuration
Based on Combat TDD v3.0
"""

# Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

# Grid Settings
GRID_WIDTH = 20
GRID_HEIGHT = 15
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50

# Combat Settings (from TDD)
MAX_ACTION_POINTS = 3
DODGE_CAP = 20  # Maximum dodge chance percentage

# Action Costs
AP_MOVE = 1
AP_BASIC_ATTACK = 2
AP_SPECIAL_ABILITY = 3
AP_USE_ITEM = 1
AP_RETREAT = 3

# Movement
BASE_MOVEMENT_RANGE = 4  # tiles

# Hit Chance Modifiers
COVER_HALF = 25
COVER_FULL = 40
FLANKING_BONUS = 15
BLINDED_PENALTY = 60
STUNNED_BONUS = 20

# Damage Calculation
DAMAGE_VARIANCE_MIN = 0.85
DAMAGE_VARIANCE_MAX = 1.15
ARMOR_REDUCTION_MULTIPLIER = 1.0  # Full armor protection

# Colors (Cyberpunk Neon Theme)
COLOR_BG = (10, 10, 15)
COLOR_GRID = (30, 30, 40)
COLOR_PLAYER = (0, 255, 255)  # Cyan
COLOR_ALLY = (0, 200, 100)  # Green
COLOR_ENEMY = (255, 50, 100)  # Pink/Red
COLOR_SELECTED = (255, 255, 0)  # Yellow
COLOR_MOVE_RANGE = (100, 100, 255, 80)  # Blue translucent
COLOR_ATTACK_RANGE = (255, 100, 100, 80)  # Red translucent
COLOR_UI_BG = (20, 20, 30)
COLOR_UI_TEXT = (200, 200, 220)
COLOR_HP_FULL = (0, 255, 100)
COLOR_HP_MID = (255, 200, 0)
COLOR_HP_LOW = (255, 50, 50)
COLOR_AP_BAR = (100, 200, 255)

# UI Layout
UI_PANEL_WIDTH = 400
UI_PANEL_X = SCREEN_WIDTH - UI_PANEL_WIDTH - 20
UI_LOG_HEIGHT = 200

# Character Starting Stats
PLAYER_START_STATS = {
    'body': 5,
    'reflexes': 6,
    'intelligence': 4,
    'tech': 4,
    'cool': 5,
    'max_hp': 150
}

ALLY_START_STATS = {
    'body': 6,
    'reflexes': 5,
    'intelligence': 3,
    'tech': 3,
    'cool': 4,
    'max_hp': 180
}

ENEMY_GRUNT_STATS = {
    'body': 4,
    'reflexes': 4,
    'intelligence': 2,
    'tech': 2,
    'cool': 3,
    'max_hp': 80
}

ENEMY_ELITE_STATS = {
    'body': 6,
    'reflexes': 6,
    'intelligence': 4,
    'tech': 4,
    'cool': 6,
    'max_hp': 150
}

# Weapons (from TDD examples)
WEAPONS = {
    'assault_rifle': {
        'name': 'Assault Rifle',
        'damage': 30,
        'accuracy': 85,
        'range': 12,
        'armor_pen': 0.15,
        'crit_multiplier': 2.0,
        'type': 'ranged'
    },
    'pistol': {
        'name': 'Pistol',
        'damage': 25,
        'accuracy': 90,
        'range': 10,
        'armor_pen': 0.1,
        'crit_multiplier': 2.0,
        'type': 'ranged'
    },
    'shotgun': {
        'name': 'Shotgun',
        'damage': 45,
        'accuracy': 75,
        'range': 6,
        'armor_pen': 0.05,
        'crit_multiplier': 1.5,
        'type': 'ranged'
    },
    'katana': {
        'name': 'Katana',
        'damage': 35,
        'accuracy': 95,
        'range': 1,
        'armor_pen': 0.2,
        'crit_multiplier': 2.5,
        'type': 'melee'
    }
}
