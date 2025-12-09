"""
Autotile System Demo

Demonstrates the autotile system with sample water, wall, and cliff autotile sets.
Shows automatic tile matching and neighbor updates.
"""

import pygame

from neonworks.rendering.autotiles import (
    AutotileFormat,
    AutotileManager,
    AutotileSet,
    get_autotile_manager,
)
from neonworks.data.map_layers import EnhancedTileLayer
from neonworks.rendering.tilemap import Tilemap, TilemapBuilder, Tileset
from neonworks.ui.autotile_editor_ui import AutotileEditorUI


def create_sample_autotile_sets():
    """
    Create sample autotile sets for water, walls, and cliffs.

    Returns:
        List of AutotileSet objects
    """
    autotile_sets = []

    # Water autotile (16-tile format)
    # Assumes tiles 0-15 in tileset are water autotiles
    water_autotile = AutotileSet(
        name="Water",
        tileset_name="terrain",
        format=AutotileFormat.TILE_16,
        base_tile_id=0,  # Starting tile ID in tileset
        match_same_type=True,
    )
    autotile_sets.append(water_autotile)

    # Wall autotile (16-tile format)
    # Assumes tiles 16-31 in tileset are wall autotiles
    wall_autotile = AutotileSet(
        name="Wall",
        tileset_name="terrain",
        format=AutotileFormat.TILE_16,
        base_tile_id=16,
        match_same_type=True,
    )
    autotile_sets.append(wall_autotile)

    # Cliff autotile (16-tile format)
    # Assumes tiles 32-47 in tileset are cliff autotiles
    cliff_autotile = AutotileSet(
        name="Cliff",
        tileset_name="terrain",
        format=AutotileFormat.TILE_16,
        base_tile_id=32,
        match_same_type=True,
    )
    autotile_sets.append(cliff_autotile)

    # Grass autotile (47-tile format example)
    # Assumes tiles 48-94 in tileset are grass autotiles
    grass_autotile = AutotileSet(
        name="Grass",
        tileset_name="terrain",
        format=AutotileFormat.TILE_47,
        base_tile_id=48,
        match_same_type=True,
    )
    autotile_sets.append(grass_autotile)

    return autotile_sets


def main():
    """Run the autotile demo."""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("NeonWorks Autotile Demo")
    clock = pygame.time.Clock()

    # Create sample autotile sets
    autotile_sets = create_sample_autotile_sets()

    # Register autotile sets with manager
    autotile_manager = get_autotile_manager()
    for autotile_set in autotile_sets:
        autotile_manager.register_autotile_set(autotile_set)

    # Create test tilemap
    tilemap = TilemapBuilder.create_simple_tilemap(width=20, height=15, tile_size=32)
    layer = tilemap.get_layer(0)

    # Create tileset (placeholder - in real use, load from image)
    tileset = Tileset(
        name="terrain",
        texture_path="assets/tilesets/terrain.png",
        tile_width=32,
        tile_height=32,
        columns=16,
        tile_count=96,
    )
    tilemap.add_tileset(tileset)

    # Open autotile editor
    autotile_editor = AutotileEditorUI(screen)
    autotile_editor.toggle()  # Open by default

    # Demo: Paint some water tiles
    water_autotile = autotile_sets[0]  # Water

    # Paint a pond
    for y in range(5, 10):
        for x in range(5, 12):
            autotile_manager.paint_autotile(layer, x, y, water_autotile)

    # Paint some walls
    wall_autotile = autotile_sets[1]  # Wall

    # Paint a wall
    for x in range(2, 18):
        autotile_manager.paint_autotile(layer, x, 2, wall_autotile)

    # Main loop
    running = True
    mouse_down = False
    current_autotile = water_autotile

    while running:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    autotile_editor.toggle()
                elif event.key == pygame.K_1:
                    current_autotile = autotile_sets[0]  # Water
                    print("Selected: Water")
                elif event.key == pygame.K_2:
                    current_autotile = autotile_sets[1]  # Wall
                    print("Selected: Wall")
                elif event.key == pygame.K_3:
                    current_autotile = autotile_sets[2]  # Cliff
                    print("Selected: Cliff")
                elif event.key == pygame.K_4:
                    current_autotile = autotile_sets[3]  # Grass
                    print("Selected: Grass")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                # Paint on tilemap if not in editor
                if not autotile_editor.visible:
                    mouse_x, mouse_y = event.pos
                    tile_x = mouse_x // 32
                    tile_y = mouse_y // 32

                    if event.button == 1:  # Left click - paint
                        autotile_manager.paint_autotile(layer, tile_x, tile_y, current_autotile)
                    elif event.button == 3:  # Right click - erase
                        autotile_manager.erase_autotile(layer, tile_x, tile_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down and not autotile_editor.visible:
                    mouse_x, mouse_y = event.pos
                    tile_x = mouse_x // 32
                    tile_y = mouse_y // 32

                    buttons = pygame.mouse.get_pressed()
                    if buttons[0]:  # Left button
                        autotile_manager.paint_autotile(layer, tile_x, tile_y, current_autotile)
                    elif buttons[2]:  # Right button
                        autotile_manager.erase_autotile(layer, tile_x, tile_y)

            # Let autotile editor handle events
            autotile_editor.handle_event(event)

        # Update
        autotile_editor.update(dt)

        # Render
        screen.fill((50, 50, 60))

        # Draw tilemap
        if not autotile_editor.visible:
            for y in range(layer.height):
                for x in range(layer.width):
                    tile = layer.get_tile(x, y)
                    if tile and not tile.is_empty():
                        # Draw colored tiles based on autotile set
                        color = (100, 100, 100)
                        if tile.tile_id < 16:  # Water
                            color = (100, 150, 255)
                        elif tile.tile_id < 32:  # Wall
                            color = (128, 128, 128)
                        elif tile.tile_id < 48:  # Cliff
                            color = (139, 90, 43)
                        else:  # Grass
                            color = (100, 200, 50)

                        pygame.draw.rect(
                            screen,
                            color,
                            (x * 32, y * 32, 32, 32),
                        )

                        # Draw tile ID
                        font = pygame.font.Font(None, 16)
                        text = font.render(str(tile.tile_id), True, (255, 255, 255))
                        screen.blit(text, (x * 32 + 2, y * 32 + 2))

                    # Draw grid
                    pygame.draw.rect(
                        screen,
                        (80, 80, 90),
                        (x * 32, y * 32, 32, 32),
                        1,
                    )

        # Draw UI
        autotile_editor.render(screen)

        # Draw instructions if editor not visible
        if not autotile_editor.visible:
            font = pygame.font.Font(None, 24)
            instructions = [
                "Autotile Demo - Press keys to select autotile:",
                "1: Water  2: Wall  3: Cliff  4: Grass",
                "Left Click: Paint  Right Click: Erase",
                "F11: Open Autotile Editor  ESC: Quit",
            ]
            for i, text in enumerate(instructions):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
