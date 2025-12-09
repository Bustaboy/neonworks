"""Rendering systems"""

# Lazy imports to avoid loading pygame during test collection

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
    "Tileset",
    "Tile",
    "UI",
    "UIState",
    "UIStyle",
    "HUD",
    "AssetManager",
    # Asset pipeline (optional, requires Pillow)
    "TextureAtlasBuilder",
    "ImageOptimizer",
    "ImageEffects",
    "SpriteSheetExtractor",
    "PygameConverter",
    "AtlasRegion",
]

ASSET_PIPELINE_AVAILABLE = None  # Lazy check


def __getattr__(name):
    """Lazy load rendering modules"""
    global ASSET_PIPELINE_AVAILABLE

    if name == "ASSET_PIPELINE_AVAILABLE":
        if ASSET_PIPELINE_AVAILABLE is None:
            try:
                import neonworks.rendering.asset_pipeline

                ASSET_PIPELINE_AVAILABLE = True
            except ImportError:
                ASSET_PIPELINE_AVAILABLE = False
        return ASSET_PIPELINE_AVAILABLE

    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    # Import from appropriate module
    if name in ["Animation", "AnimationStateMachine"]:
        from neonworks.rendering.animation import Animation, AnimationStateMachine

        globals().update({"Animation": Animation, "AnimationStateMachine": AnimationStateMachine})
    elif name == "AssetManager":
        from neonworks.rendering.assets import AssetManager

        globals()["AssetManager"] = AssetManager
    elif name == "Camera":
        from neonworks.rendering.camera import Camera

        globals()["Camera"] = Camera
    elif name in [
        "Particle",
        "ParticleEmitter",
        "ParticleSystem",
        "ParticleRenderer",
        "ParticlePresets",
        "EmitterShape",
        "ParticleBlendMode",
    ]:
        from neonworks.rendering.particles import (
            EmitterShape,
            Particle,
            ParticleBlendMode,
            ParticleEmitter,
            ParticlePresets,
            ParticleRenderer,
            ParticleSystem,
        )

        globals().update(
            {
                "Particle": Particle,
                "ParticleEmitter": ParticleEmitter,
                "ParticleSystem": ParticleSystem,
                "ParticleRenderer": ParticleRenderer,
                "ParticlePresets": ParticlePresets,
                "EmitterShape": EmitterShape,
                "ParticleBlendMode": ParticleBlendMode,
            }
        )
    elif name == "Renderer":
        from neonworks.rendering.renderer import Renderer

        globals()["Renderer"] = Renderer
    elif name in ["Tile", "Tilemap", "Tileset"]:
        from neonworks.rendering.tilemap import Tile, Tilemap, Tileset

        globals().update(
            {
                "Tile": Tile,
                "Tilemap": Tilemap,
                "Tileset": Tileset,
            }
        )
    elif name in ["HUD", "UI", "UIState", "UIStyle"]:
        from neonworks.rendering.ui import HUD, UI, UIState, UIStyle

        globals().update({"HUD": HUD, "UI": UI, "UIState": UIState, "UIStyle": UIStyle})
    elif name in [
        "TextureAtlasBuilder",
        "ImageOptimizer",
        "ImageEffects",
        "SpriteSheetExtractor",
        "PygameConverter",
        "AtlasRegion",
    ]:
        try:
            from neonworks.rendering.asset_pipeline import (
                AtlasRegion,
                ImageEffects,
                ImageOptimizer,
                PygameConverter,
                SpriteSheetExtractor,
                TextureAtlasBuilder,
            )

            globals().update(
                {
                    "TextureAtlasBuilder": TextureAtlasBuilder,
                    "ImageOptimizer": ImageOptimizer,
                    "ImageEffects": ImageEffects,
                    "SpriteSheetExtractor": SpriteSheetExtractor,
                    "PygameConverter": PygameConverter,
                    "AtlasRegion": AtlasRegion,
                }
            )
        except ImportError:
            raise AttributeError(f"Asset pipeline not available. Install Pillow to use {name}")

    return globals()[name]
