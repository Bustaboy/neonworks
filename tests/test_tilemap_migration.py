import pygame

from neonworks.core.ecs import World
from neonworks.ui.level_builder_ui import LevelBuilderUI


def test_legacy_numeric_layers_deserializes_to_enhanced():
    """Legacy saves with numeric 'layers' migrate to enhanced layers on load."""
    pygame.init()
    screen = pygame.Surface((800, 600))
    ui = LevelBuilderUI(screen=screen, world=World())

    legacy_tilemap_data = {
        "width": 5,
        "height": 5,
        "layers": 2,  # legacy numeric count
        "tiles": [
            {"x": 0, "y": 0, "layer": 1, "tile_type": "grass", "walkable": True},
            {"x": 4, "y": 4, "layer": 0, "tile_type": "rock", "walkable": False},
        ],
    }

    ui._deserialize_tilemap(legacy_tilemap_data)  # type: ignore[attr-defined]

    tilemap = ui.tilemap
    assert tilemap is not None
    assert tilemap.get_layer_count() == 2

    tile_a = tilemap.get_tile(0, 0, 1)
    tile_b = tilemap.get_tile(4, 4, 0)

    assert tile_a is not None and tile_a.tile_type == "grass"
    assert tile_b is not None and tile_b.tile_type == "rock"
