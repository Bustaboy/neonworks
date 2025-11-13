"""Rendering systems"""

from neonworks.rendering.renderer import Renderer
from neonworks.rendering.camera import Camera
from neonworks.rendering.particles import (
    Particle,
    ParticleEmitter,
    ParticleSystem,
    ParticleRenderer,
    ParticlePresets,
    EmitterShape,
    ParticleBlendMode
)
from neonworks.rendering.animation import AnimationStateMachine, Animation
from neonworks.rendering.tilemap import Tilemap, TileLayer, Tileset, Tile
from neonworks.rendering.ui import UI, UIState, UIStyle, HUD
from neonworks.rendering.assets import AssetManager

# Asset pipeline utilities (requires Pillow)
try:
    from neonworks.rendering.asset_pipeline import (
        TextureAtlasBuilder,
        ImageOptimizer,
        ImageEffects,
        SpriteSheetExtractor,
        PygameConverter,
        AtlasRegion
    )
    ASSET_PIPELINE_AVAILABLE = True
except ImportError:
    ASSET_PIPELINE_AVAILABLE = False

__all__ = [
    'Renderer',
    'Camera',
    'Particle',
    'ParticleEmitter',
    'ParticleSystem',
    'ParticleRenderer',
    'ParticlePresets',
    'EmitterShape',
    'ParticleBlendMode',
    'AnimationStateMachine',
    'Animation',
    'Tilemap',
    'TileLayer',
    'Tileset',
    'Tile',
    'UI',
    'UIState',
    'UIStyle',
    'HUD',
    'AssetManager',
]

if ASSET_PIPELINE_AVAILABLE:
    __all__.extend([
        'TextureAtlasBuilder',
        'ImageOptimizer',
        'ImageEffects',
        'SpriteSheetExtractor',
        'PygameConverter',
        'AtlasRegion'
    ])
