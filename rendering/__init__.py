"""Rendering systems"""

from engine.rendering.renderer import Renderer
from engine.rendering.camera import Camera
from engine.rendering.particles import (
    Particle,
    ParticleEmitter,
    ParticleSystem,
    ParticleRenderer,
    ParticlePresets,
    EmitterShape,
    ParticleBlendMode,
)
from engine.rendering.animation import AnimationStateMachine, Animation
from engine.rendering.tilemap import Tilemap, TileLayer, Tileset, Tile
from engine.rendering.ui import UI, UIState, UIStyle, HUD
from engine.rendering.assets import AssetManager

# Asset pipeline utilities (requires Pillow)
try:
    from engine.rendering.asset_pipeline import (
        TextureAtlasBuilder,
        ImageOptimizer,
        ImageEffects,
        SpriteSheetExtractor,
        PygameConverter,
        AtlasRegion,
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
