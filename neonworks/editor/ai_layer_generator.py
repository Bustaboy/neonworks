"""
AI Layer Generator - Intelligent layer creation and configuration

Uses AI to automatically generate appropriate layer structures for different game types:
- Platformers with parallax backgrounds
- Top-down RPGs with organized layer groups
- Strategy games with tactical overlays
- Auto-scrolling shooters with dynamic backgrounds
"""

from typing import List, Optional, Tuple

from neonworks.data.map_layers import LayerProperties, LayerType, ParallaxMode
from neonworks.rendering.tilemap import Tilemap, TilemapBuilder


class AILayerGenerator:
    """
    AI-powered layer structure generator.

    Analyzes game requirements and automatically creates an optimal
    layer structure with appropriate properties.
    """

    @staticmethod
    def generate_platformer_layers(
        tilemap: Tilemap, has_parallax: bool = True, depth_layers: int = 3
    ) -> List[str]:
        """
        Generate layer structure for a platformer game.

        Args:
            tilemap: Tilemap to add layers to
            has_parallax: Whether to add parallax background layers
            depth_layers: Number of background depth layers (1-5)

        Returns:
            List of created layer IDs
        """
        print("🤖 AI: Generating platformer layer structure...")
        layer_ids = []

        if has_parallax and depth_layers > 0:
            # Generate background layers with increasing parallax
            parallax_configs = [
                ("Sky", 0.1, 0.1),  # Very far
                ("Distant Mountains", 0.3, 0.3),
                ("Far Hills", 0.5, 0.5),
                ("Near Trees", 0.7, 0.7),
                ("Close Bushes", 0.85, 0.85),
            ]

            for i in range(min(depth_layers, len(parallax_configs))):
                name, px, py = parallax_configs[i]
                layer_id = tilemap.create_parallax_background(name, parallax_x=px, parallax_y=py)
                layer_ids.append(layer_id)
                print(f"   ✅ Created parallax layer: {name} (parallax: {px}x)")

        # Main gameplay layers
        ground_id = tilemap.create_enhanced_layer(
            "Ground", layer_type=LayerType.STANDARD, opacity=1.0
        )
        layer_ids.append(ground_id)
        print("   ✅ Created ground layer")

        platforms_id = tilemap.create_enhanced_layer(
            "Platforms", layer_type=LayerType.STANDARD, opacity=1.0
        )
        layer_ids.append(platforms_id)
        print("   ✅ Created platforms layer")

        decorations_id = tilemap.create_enhanced_layer(
            "Decorations", layer_type=LayerType.STANDARD, opacity=1.0
        )
        layer_ids.append(decorations_id)
        print("   ✅ Created decorations layer")

        # Foreground with parallax
        if has_parallax:
            fg_props = LayerProperties(
                name="Foreground",
                layer_type=LayerType.PARALLAX_FOREGROUND,
                parallax_x=1.15,
                parallax_y=1.0,
                opacity=0.7,
            )
            fg_layer = tilemap.layer_manager.create_layer("Foreground", properties=fg_props)
            layer_ids.append(fg_layer.properties.layer_id)
            print("   ✅ Created foreground parallax layer")

        # Collision layer
        collision_props = LayerProperties(
            name="Collision", layer_type=LayerType.COLLISION, visible=False
        )
        collision_layer = tilemap.layer_manager.create_layer(
            "Collision", properties=collision_props
        )
        layer_ids.append(collision_layer.properties.layer_id)
        print("   ✅ Created collision layer")

        print(f"   🎨 Generated {len(layer_ids)} layers for platformer")
        return layer_ids

    @staticmethod
    def generate_rpg_layers(tilemap: Tilemap, organized: bool = True) -> List[str]:
        """
        Generate organized layer structure for top-down RPG.

        Args:
            tilemap: Tilemap to add layers to
            organized: Whether to use groups for organization

        Returns:
            List of created layer IDs
        """
        print("🤖 AI: Generating RPG layer structure...")
        layer_ids = []

        if organized:
            # Create organized groups
            bg_group = tilemap.create_layer_group("Background")
            print("   📁 Created Background group")

            # Background layers in group
            floor_id = tilemap.create_enhanced_layer("Floor", parent_group_id=bg_group)
            carpet_id = tilemap.create_enhanced_layer("Carpet", parent_group_id=bg_group)
            shadows_id = tilemap.create_enhanced_layer(
                "Shadows", parent_group_id=bg_group, opacity=0.5
            )

            layer_ids.extend([floor_id, carpet_id, shadows_id])
            print("   ✅ Created background layers (Floor, Carpet, Shadows)")

            # Objects group
            obj_group = tilemap.create_layer_group("Objects")
            print("   📁 Created Objects group")

            furniture_id = tilemap.create_enhanced_layer("Furniture", parent_group_id=obj_group)
            items_id = tilemap.create_enhanced_layer("Items", parent_group_id=obj_group)
            npcs_id = tilemap.create_enhanced_layer("NPCs", parent_group_id=obj_group)

            layer_ids.extend([furniture_id, items_id, npcs_id])
            print("   ✅ Created object layers (Furniture, Items, NPCs)")

            # Overlay group
            overlay_group = tilemap.create_layer_group("Overlay")
            print("   📁 Created Overlay group")

            roof_id = tilemap.create_enhanced_layer(
                "Roof", parent_group_id=overlay_group, opacity=0.6
            )
            lighting_id = tilemap.create_enhanced_layer(
                "Lighting", parent_group_id=overlay_group, opacity=0.8
            )

            layer_ids.extend([roof_id, lighting_id])
            print("   ✅ Created overlay layers (Roof, Lighting)")

        else:
            # Simple flat structure
            layer_names = [
                "Floor",
                "Carpet",
                "Shadows",
                "Furniture",
                "Items",
                "NPCs",
                "Roof",
                "Lighting",
            ]

            for name in layer_names:
                opacity = 0.6 if name == "Roof" else 1.0
                layer_id = tilemap.create_enhanced_layer(name, opacity=opacity)
                layer_ids.append(layer_id)
                print(f"   ✅ Created layer: {name}")

        print(f"   🎨 Generated {len(layer_ids)} layers for RPG")
        return layer_ids

    @staticmethod
    def generate_space_shooter_layers(tilemap: Tilemap, star_layers: int = 3) -> List[str]:
        """
        Generate auto-scrolling layer structure for space shooter.

        Args:
            tilemap: Tilemap to add layers to
            star_layers: Number of star field layers (1-5)

        Returns:
            List of created layer IDs
        """
        print("🤖 AI: Generating space shooter layer structure...")
        layer_ids = []

        # Auto-scrolling star fields with different speeds
        star_configs = [
            ("Distant Stars", 0.1, -3.0),  # Slowest
            ("Far Stars", 0.3, -8.0),
            ("Mid Stars", 0.5, -15.0),
            ("Near Stars", 0.7, -25.0),
            ("Close Stars", 0.9, -40.0),  # Fastest
        ]

        for i in range(min(star_layers, len(star_configs))):
            name, parallax, scroll_speed = star_configs[i]
            layer_id = tilemap.create_parallax_background(
                name, parallax_x=parallax, parallax_y=parallax, auto_scroll_y=scroll_speed
            )
            layer_ids.append(layer_id)
            print(f"   ✅ Created auto-scrolling layer: {name} (scroll: {scroll_speed}px/s)")

        # Game layer
        game_id = tilemap.create_enhanced_layer("Game", layer_type=LayerType.STANDARD)
        layer_ids.append(game_id)
        print("   ✅ Created game layer")

        # Effects layer
        effects_id = tilemap.create_enhanced_layer(
            "Effects", layer_type=LayerType.STANDARD, opacity=0.9
        )
        layer_ids.append(effects_id)
        print("   ✅ Created effects layer")

        # UI overlay
        ui_props = LayerProperties(name="UI Overlay", layer_type=LayerType.OVERLAY, opacity=1.0)
        ui_layer = tilemap.layer_manager.create_layer("UI Overlay", properties=ui_props)
        layer_ids.append(ui_layer.properties.layer_id)
        print("   ✅ Created UI overlay layer")

        print(f"   🎨 Generated {len(layer_ids)} layers for space shooter")
        return layer_ids

    @staticmethod
    def generate_strategy_layers(tilemap: Tilemap, use_groups: bool = True) -> List[str]:
        """
        Generate layer structure for strategy game.

        Args:
            tilemap: Tilemap to add layers to
            use_groups: Whether to organize with groups

        Returns:
            List of created layer IDs
        """
        print("🤖 AI: Generating strategy game layer structure...")
        layer_ids = []

        if use_groups:
            # Terrain group
            terrain_group = tilemap.create_layer_group("Terrain")
            print("   📁 Created Terrain group")

            ground_id = tilemap.create_enhanced_layer("Ground", parent_group_id=terrain_group)
            elevation_id = tilemap.create_enhanced_layer("Elevation", parent_group_id=terrain_group)
            vegetation_id = tilemap.create_enhanced_layer(
                "Vegetation", parent_group_id=terrain_group
            )

            layer_ids.extend([ground_id, elevation_id, vegetation_id])
            print("   ✅ Created terrain layers")

            # Structures group
            structures_group = tilemap.create_layer_group("Structures")
            print("   📁 Created Structures group")

            buildings_id = tilemap.create_enhanced_layer(
                "Buildings", parent_group_id=structures_group
            )
            walls_id = tilemap.create_enhanced_layer("Walls", parent_group_id=structures_group)
            roads_id = tilemap.create_enhanced_layer("Roads", parent_group_id=structures_group)

            layer_ids.extend([buildings_id, walls_id, roads_id])
            print("   ✅ Created structure layers")

            # Tactical overlays group
            tactical_group = tilemap.create_layer_group("Tactical Overlays")
            print("   📁 Created Tactical Overlays group")

            fog_id = tilemap.create_enhanced_layer(
                "Fog of War", parent_group_id=tactical_group, opacity=0.7
            )
            movement_id = tilemap.create_enhanced_layer(
                "Movement Range", parent_group_id=tactical_group, opacity=0.5
            )
            attack_id = tilemap.create_enhanced_layer(
                "Attack Range", parent_group_id=tactical_group, opacity=0.6
            )

            layer_ids.extend([fog_id, movement_id, attack_id])
            print("   ✅ Created tactical overlay layers")

        else:
            # Flat structure
            layer_configs = [
                ("Ground", 1.0),
                ("Elevation", 1.0),
                ("Vegetation", 1.0),
                ("Buildings", 1.0),
                ("Walls", 1.0),
                ("Roads", 1.0),
                ("Fog of War", 0.7),
                ("Movement Range", 0.5),
                ("Attack Range", 0.6),
            ]

            for name, opacity in layer_configs:
                layer_id = tilemap.create_enhanced_layer(name, opacity=opacity)
                layer_ids.append(layer_id)
                print(f"   ✅ Created layer: {name}")

        # Collision layer
        collision_props = LayerProperties(
            name="Collision", layer_type=LayerType.COLLISION, visible=False
        )
        collision_layer = tilemap.layer_manager.create_layer(
            "Collision", properties=collision_props
        )
        layer_ids.append(collision_layer.properties.layer_id)
        print("   ✅ Created collision layer")

        print(f"   🎨 Generated {len(layer_ids)} layers for strategy game")
        return layer_ids

    @staticmethod
    def suggest_layer_optimization(tilemap: Tilemap) -> List[str]:
        """
        Analyze tilemap and suggest optimizations.

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        manager = tilemap.layer_manager
        layer_count = len(manager.layers)
        group_count = len(manager.groups)

        print(f"🤖 AI: Analyzing {layer_count} layers, {group_count} groups...")

        # Check for too many layers without groups
        if layer_count > 5 and group_count == 0:
            suggestions.append(
                f"💡 {layer_count} layers detected. Consider organizing with groups for better management"
            )

        # Check for invisible layers
        invisible_count = sum(
            1 for layer in manager.layers.values() if not layer.properties.visible
        )
        if invisible_count > 0:
            suggestions.append(
                f"👁️ {invisible_count} invisible layers found. Consider removing if not needed"
            )

        # Check for duplicate names
        names = [layer.properties.name for layer in manager.layers.values()]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        if duplicates:
            suggestions.append(
                f"📝 Duplicate layer names found: {', '.join(duplicates)}. Consider renaming for clarity"
            )

        # Check for layers that could be merged
        empty_layers = []
        for layer_id, layer in manager.layers.items():
            if all(tile == 0 for row in layer.tiles for tile in row):
                empty_layers.append(layer.properties.name)

        if empty_layers:
            suggestions.append(
                f"🗑️ Empty layers found: {', '.join(empty_layers)}. Consider removing to reduce memory"
            )

        # Check for parallax without auto-scroll
        parallax_layers = [
            layer.properties.name
            for layer in manager.layers.values()
            if layer.properties.layer_type
            in [LayerType.PARALLAX_BACKGROUND, LayerType.PARALLAX_FOREGROUND]
            and layer.properties.parallax_mode == ParallaxMode.MANUAL
        ]

        if parallax_layers:
            suggestions.append(
                f"🌊 Parallax layers without auto-scroll: {', '.join(parallax_layers)}. "
                "Consider adding auto-scroll for dynamic backgrounds"
            )

        if not suggestions:
            suggestions.append("✅ Layer structure looks optimized!")

        return suggestions

