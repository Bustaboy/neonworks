"""Rendering systems"""

from neonworks.rendering.animation import Animation, AnimationStateMachine
from neonworks.rendering.assets import AssetManager
from neonworks.rendering.camera import Camera
from neonworks.rendering.particles import (
    EmitterShape,
    Particle,
    ParticleBlendMode,
    ParticleEmitter,
    ParticlePresets,
    ParticleRenderer,
    ParticleSystem,
)
from neonworks.rendering.renderer import Renderer
from neonworks.rendering.tilemap import Tile, TileLayer, Tilemap, Tileset
from neonworks.rendering.ui import HUD, UI, UIState, UIStyle

# Asset pipeline utilities (requires Pillow)
try:
    from neonworks.rendering.asset_pipeline import (
        AtlasRegion,
        ImageEffects,
        ImageOptimizer,
        PygameConverter,
        SpriteSheetExtractor,
        TextureAtlasBuilder,
    )

    ASSET_PIPELINE_AVAILABLE = True
except ImportError:
    ASSET_PIPELINE_AVAILABLE = False

__all__ = [
    "Renderer",
    "Camera",
    "Particle",
    "ParticleEmitter",
    "ParticleSystem",
    "ParticleRenderer",
    "ParticlePresets",
    "EmitterShape",
    "ParticleBlendMode",
    "AnimationStateMachine",
    "Animation",
    "Tilemap",
    "TileLayer",
    "Tileset",
    "Tile",
    "UI",
    "UIState",
    "UIStyle",
    "HUD",
    "AssetManager",
]

if ASSET_PIPELINE_AVAILABLE:
    __all__.extend(
        [
            "TextureAtlasBuilder",
            "ImageOptimizer",
            "ImageEffects",
            "SpriteSheetExtractor",
            "PygameConverter",
            "AtlasRegion",
        ]
    )
