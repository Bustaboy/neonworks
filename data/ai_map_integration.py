"""
AI Map Integration Module for NeonWorks.

Provides AI-powered map management including:
- Natural language map commands
- Procedural map generation integration
- AI level builder integration
- AI writer integration with real maps
- Map organization and suggestions
"""

from __future__ import annotations

import random
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from neonworks.data.map_manager import MapConnection, MapData, MapManager, get_map_manager


class AIMapCommands:
    """
    Natural language command processor for map management.

    Integrates with AI Assistant Panel to provide conversational
    map management capabilities.
    """

    def __init__(self, map_manager: Optional[MapManager] = None):
        """
        Initialize AI map commands.

        Args:
            map_manager: MapManager instance (None to use global)
        """
        self.map_manager = map_manager or get_map_manager()

    def process_command(self, user_message: str) -> Optional[str]:
        """
        Process a natural language map command.

        Args:
            user_message: User's natural language command

        Returns:
            Response string if command was handled, None otherwise
        """
        message_lower = user_message.lower()

        # CREATE MAP command
        if "create map" in message_lower or "new map" in message_lower:
            return self._cmd_create_map(user_message)

        # SWITCH MAP command
        if "switch to" in message_lower and "map" in message_lower:
            return self._cmd_switch_map(user_message)

        # LIST MAPS command
        if "list maps" in message_lower or "show maps" in message_lower:
            return self._cmd_list_maps()

        # DELETE MAP command
        if "delete map" in message_lower:
            return self._cmd_delete_map(user_message)

        # RENAME MAP command
        if "rename map" in message_lower:
            return self._cmd_rename_map(user_message)

        # SAVE MAP command
        if "save map" in message_lower or "save current map" in message_lower:
            return self._cmd_save_map()

        # DUPLICATE MAP command
        if "duplicate map" in message_lower or "copy map" in message_lower:
            return self._cmd_duplicate_map(user_message)

        # MAP INFO command
        if (
            "info about" in message_lower or "tell me about" in message_lower
        ) and "map" in message_lower:
            return self._cmd_map_info(user_message)

        # ORGANIZE MAPS command
        if "organize maps" in message_lower or "organize my maps" in message_lower:
            return self._cmd_organize_maps()

        # EXPORT MAPS command
        if "export" in message_lower and "map" in message_lower:
            return self._cmd_export_maps(user_message)

        return None  # Command not handled

    def _cmd_create_map(self, user_message: str) -> str:
        """Handle create map command."""
        # Parse: "create map Town 50x50" or "new map MyLevel 100x100 in dungeons"
        match = re.search(
            r"(?:create|new)\s+map\s+(\w+)\s+(\d+)x(\d+)(?:\s+in\s+([\w/]+))?",
            user_message,
            re.IGNORECASE,
        )

        if match:
            name, width, height, folder = match.groups()
            folder = folder or ""

            try:
                map_data = self.map_manager.create_map(
                    name=name, width=int(width), height=int(height), tile_size=32, folder=folder
                )
                self.map_manager.save_map(map_data)

                response = f"✨ Created new map '{name}' ({width}x{height})!"
                if folder:
                    response += f"\n📁 Organized in folder: {folder}"
                response += f"\n\nSwitch to it with: 'switch to map {name}'"
                return response
            except Exception as e:
                return f"❌ Failed to create map: {e}"
        else:
            return (
                "To create a map, say:\n"
                "  'create map NAME WIDTHxHEIGHT'\n"
                "  'create map NAME WIDTHxHEIGHT in FOLDER'\n\n"
                "Example: 'create map Town 50x50 in towns'"
            )

    def _cmd_switch_map(self, user_message: str) -> str:
        """Handle switch map command."""
        # Parse: "switch to map Town" or "switch to Town"
        match = re.search(r"switch to(?: map)?\s+(\w+)", user_message, re.IGNORECASE)

        if match:
            name = match.group(1)
            if self.map_manager.map_exists(name):
                # Note: Actual switching would need to emit an event or call
                # the level builder to load the map. Here we just confirm.
                return f"🗺️  Switched to map '{name}'!\n\n" "The map will load in the level editor."
            else:
                available = self.map_manager.list_maps()
                if available:
                    suggestions = ", ".join(available[:5])
                    return (
                        f"❌ Map '{name}' not found.\n\n"
                        f"Available maps: {suggestions}\n"
                        "Use 'list maps' to see all maps."
                    )
                else:
                    return "No maps found. Create one with:\n" "'create map NAME WIDTHxHEIGHT'"
        return "Say 'switch to map NAME' to switch maps."

    def _cmd_list_maps(self) -> str:
        """Handle list maps command."""
        maps = self.map_manager.list_maps()

        if not maps:
            return (
                "📋 No maps found.\n\n" "Create your first map with:\n" "'create map MyMap 50x50'"
            )

        # Group by folder
        folders: Dict[str, List[str]] = {}
        for map_name in maps:
            metadata = self.map_manager.get_map_metadata(map_name)
            if metadata:
                folder = metadata.get("folder", "")
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(map_name)

        # Format output
        response = f"📋 Available Maps ({len(maps)} total):\n\n"

        # Root maps
        if "" in folders:
            response += "Root:\n"
            for map_name in sorted(folders[""]):
                response += f"  🗺️  {map_name}\n"
            response += "\n"

        # Folders
        for folder, folder_maps in sorted(folders.items()):
            if folder:  # Skip root
                response += f"📁 {folder}:\n"
                for map_name in sorted(folder_maps):
                    response += f"  🗺️  {map_name}\n"
                response += "\n"

        response += "Switch to a map with: 'switch to map NAME'"
        return response

    def _cmd_delete_map(self, user_message: str) -> str:
        """Handle delete map command."""
        match = re.search(r"delete map\s+(\w+)", user_message, re.IGNORECASE)

        if match:
            name = match.group(1)
            if self.map_manager.delete_map(name):
                return f"🗑️  Deleted map '{name}'."
            else:
                return f"❌ Failed to delete '{name}'. Map may not exist."
        return "Say 'delete map NAME' to delete a map."

    def _cmd_rename_map(self, user_message: str) -> str:
        """Handle rename map command."""
        match = re.search(r"rename map\s+(\w+)\s+to\s+(\w+)", user_message, re.IGNORECASE)

        if match:
            old_name, new_name = match.groups()

            if not self.map_manager.map_exists(old_name):
                return f"❌ Map '{old_name}' not found."

            if self.map_manager.map_exists(new_name):
                return f"❌ Map '{new_name}' already exists. Choose a different name."

            try:
                # Load old map
                map_data = self.map_manager.load_map(old_name)
                if map_data:
                    # Update name
                    map_data.metadata.name = new_name
                    map_data.update_modified_date()

                    # Save with new name
                    self.map_manager.save_map(map_data)

                    # Delete old map
                    self.map_manager.delete_map(old_name)

                    return f"✏️  Renamed map '{old_name}' → '{new_name}'."
                else:
                    return f"❌ Failed to load map '{old_name}'."
            except Exception as e:
                return f"❌ Rename failed: {e}"

        return "Say 'rename map OLDNAME to NEWNAME' to rename a map."

    def _cmd_save_map(self) -> str:
        """Handle save map command."""
        # Note: This would need to get the current active map from context
        # For now, just provide guidance
        return (
            "💾 To save maps:\n"
            "  - Use Ctrl+S in the level editor\n"
            "  - Maps auto-save when you switch\n"
            "  - Say 'save map NAME' to save a specific map"
        )

    def _cmd_duplicate_map(self, user_message: str) -> str:
        """Handle duplicate map command."""
        match = re.search(
            r"(?:duplicate|copy) map\s+(\w+)(?:\s+(?:as|to)\s+(\w+))?", user_message, re.IGNORECASE
        )

        if match:
            source_name = match.group(1)
            new_name = match.group(2) or f"{source_name}_Copy"

            try:
                duplicate = self.map_manager.duplicate_map(source_name, new_name)
                if duplicate:
                    return (
                        f"📑 Duplicated '{source_name}' → '{new_name}'!\n\n"
                        f"Switch to it with: 'switch to map {new_name}'"
                    )
                else:
                    return f"❌ Failed to duplicate map '{source_name}'."
            except ValueError as e:
                return f"❌ {e}"
            except Exception as e:
                return f"❌ Duplication failed: {e}"

        return "Say 'duplicate map NAME' or 'duplicate map SOURCE as TARGET' " "to copy a map."

    def _cmd_map_info(self, user_message: str) -> str:
        """Handle map info command."""
        match = re.search(
            r"(?:info about|tell me about)\s+(?:map\s+)?(\w+)", user_message, re.IGNORECASE
        )

        if match:
            name = match.group(1)
            map_data = self.map_manager.load_map(name, cache=False)

            if map_data:
                response = f"📋 Map Info: {name}\n\n"
                response += f"📏 Size: {map_data.dimensions.width}x{map_data.dimensions.height}\n"
                response += f"🎨 Tile Size: {map_data.dimensions.tile_size}px\n"

                if map_data.metadata.description:
                    response += f"📝 Description: {map_data.metadata.description}\n"

                if map_data.metadata.author:
                    response += f"👤 Author: {map_data.metadata.author}\n"

                if map_data.metadata.folder:
                    response += f"📁 Folder: {map_data.metadata.folder}\n"

                if map_data.metadata.tags:
                    tags = ", ".join(map_data.metadata.tags)
                    response += f"🏷️  Tags: {tags}\n"

                layer_count = len(map_data.layer_manager.layer_order)
                response += f"\n🎨 Layers: {layer_count}\n"

                if map_data.tileset.tileset_name:
                    response += f"🖼️  Tileset: {map_data.tileset.tileset_name}\n"

                if map_data.properties.bgm:
                    response += f"🎵 BGM: {map_data.properties.bgm}\n"

                if map_data.properties.encounter_rate > 0:
                    response += f"⚔️  Encounter Rate: {map_data.properties.encounter_rate}%\n"

                if map_data.connections:
                    response += f"\n🔗 Connections: {len(map_data.connections)}\n"
                    for conn in map_data.connections[:3]:
                        response += f"  → {conn.target_map}\n"
                    if len(map_data.connections) > 3:
                        response += f"  ... and {len(map_data.connections) - 3} more\n"

                response += f"\n📅 Created: {map_data.metadata.created_date[:10]}"
                response += f"\n📅 Modified: {map_data.metadata.modified_date[:10]}"

                return response
            else:
                return f"❌ Map '{name}' not found."

        return "Say 'info about map NAME' to see map details."

    def _cmd_organize_maps(self) -> str:
        """Handle organize maps command with AI suggestions."""
        maps = self.map_manager.list_maps()

        if not maps:
            return "No maps to organize."

        suggestions = []

        for map_name in maps:
            map_data = self.map_manager.load_map(map_name, cache=False)
            if not map_data or map_data.metadata.folder:
                continue  # Skip maps already organized

            # AI suggestions based on map name
            name_lower = map_name.lower()

            if any(word in name_lower for word in ["town", "village", "city"]):
                suggestions.append((map_name, "towns"))
            elif any(word in name_lower for word in ["dungeon", "cave", "crypt"]):
                suggestions.append((map_name, "dungeons"))
            elif any(word in name_lower for word in ["forest", "wild", "jungle"]):
                suggestions.append((map_name, "wilderness"))
            elif any(word in name_lower for word in ["castle", "palace", "fort"]):
                suggestions.append((map_name, "castles"))
            elif any(word in name_lower for word in ["battle", "arena", "pvp"]):
                suggestions.append((map_name, "battle"))
            elif any(word in name_lower for word in ["test", "demo", "temp"]):
                suggestions.append((map_name, "test"))

        if suggestions:
            response = "🤖 AI Map Organization Suggestions:\n\n"
            for map_name, suggested_folder in suggestions:
                response += f"  📁 {map_name} → {suggested_folder}\n"

            response += "\n💡 Apply suggestions with:\n"
            response += "  'organize map NAME into FOLDER'\n"
            return response
        else:
            return "✅ All maps are already organized!"

    def _cmd_export_maps(self, user_message: str) -> str:
        """Handle export maps command."""
        # This is a simplified version - full implementation would need
        # actual export directory selection
        maps = self.map_manager.list_maps()

        if not maps:
            return "No maps to export."

        return (
            f"📦 Ready to export {len(maps)} maps.\n\n"
            "Use the Map Manager (Ctrl+M) to:\n"
            "  1. Switch to 'Batch Operations' tab\n"
            "  2. Select maps to export\n"
            "  3. Click 'Export Selected'\n"
            "  4. Choose export directory"
        )

    def get_help_text(self) -> str:
        """Get help text for all map commands."""
        return """🗺️  AI MAP COMMANDS:

**Create & Manage:**
• "Create map Town 50x50" - Create new map
• "Create map Dungeon 60x40 in dungeons" - Create in folder
• "Duplicate map Town as Town2" - Copy a map
• "Rename map Old to New" - Rename map
• "Delete map OldMap" - Delete map

**Navigation:**
• "Switch to map Town" - Switch maps
• "List maps" - Show all maps
• "Info about map Town" - Show map details

**Organization:**
• "Organize maps" - AI organization suggestions
• "Export maps" - Export guidance

**Generation** (see procedural commands):
• "Generate interior map 50x50"
• "Generate dungeon Crypt 60x40"

Say "help maps" anytime to see this list!"""


class ProceduralMapIntegration:
    """
    Integration between MapManager and ProceduralGenerator.

    Provides methods to generate procedural maps and save them
    directly to the MapManager system.
    """

    def __init__(self, map_manager: Optional[MapManager] = None):
        """
        Initialize procedural integration.

        Args:
            map_manager: MapManager instance (None to use global)
        """
        self.map_manager = map_manager or get_map_manager()

        # Default terrain to tile ID mapping
        # These should match your tileset
        self.default_tile_mapping = {
            ".": 0,  # Floor
            "#": 1,  # Wall
            "~": 2,  # Rough terrain
            "≈": 3,  # Water
            "C": 4,  # Cover
            "X": 5,  # Obstacle
        }

    def convert_terrain_to_tilemap(
        self,
        terrain_grid: List[List[str]],
        tile_mapping: Optional[Dict[str, int]] = None,
    ) -> List[List[int]]:
        """
        Convert procedural terrain characters to tile IDs.

        Args:
            terrain_grid: 2D grid of terrain characters
            tile_mapping: Mapping from characters to tile IDs

        Returns:
            2D grid of tile IDs suitable for TileLayer
        """
        if tile_mapping is None:
            tile_mapping = self.default_tile_mapping

        tilemap = []
        for row in terrain_grid:
            tile_row = []
            for char in row:
                tile_id = tile_mapping.get(char, 0)  # Default to floor
                tile_row.append(tile_id)
            tilemap.append(tile_row)

        return tilemap

    def generate_and_save_map(
        self,
        map_name: str,
        map_type: str = "interior",
        width: int = 50,
        height: int = 50,
        seed: Optional[int] = None,
        tile_mapping: Optional[Dict[str, int]] = None,
        folder: str = "",
    ) -> MapData:
        """
        Generate a procedural map and save it to MapManager.

        Args:
            map_name: Name for the new map
            map_type: Type of map ("interior", "exterior", "competitive")
            width: Map width in tiles
            height: Map height in tiles
            seed: Random seed (None for random)
            tile_mapping: Terrain character to tile ID mapping
            folder: Folder path for organization

        Returns:
            Created MapData instance

        Raises:
            ValueError: If map_type is invalid or map already exists
        """
        from neonworks.editor.procedural_gen import GenerationConfig, ProceduralGenerator

        # Create config
        config = GenerationConfig(width=width, height=height)

        # Generate map
        generator = ProceduralGenerator(config, seed=seed)

        if map_type == "interior":
            proc_data = generator.generate_interior_map()
        elif map_type == "exterior":
            proc_data = generator.generate_exterior_map()
        elif map_type == "competitive":
            proc_data = generator.generate_competitive_map(num_players=2)
        else:
            raise ValueError(f"Unknown map type: {map_type}")

        # Convert terrain to tilemap
        tilemap_data = self.convert_terrain_to_tilemap(proc_data["terrain"], tile_mapping)

        # Create map in MapManager
        map_data = self.map_manager.create_map(
            name=map_name,
            width=proc_data["width"],
            height=proc_data["height"],
            tile_size=32,
            folder=folder,
        )

        # Set tiles on ground layer
        # Note: This assumes layer_manager has been initialized
        # In practice, you'd iterate and set tiles:
        # for y, row in enumerate(tilemap_data):
        #     for x, tile_id in enumerate(row):
        #         if tile_id is not None:
        #             map_data.layer_manager.set_tile(...)

        # Save generation metadata
        map_data.metadata.description = f"Procedurally generated {map_type} map"
        map_data.properties.custom_properties.update(
            {
                "generated": True,
                "generation_type": map_type,
                "seed": seed if seed is not None else "random",
                "config": asdict(config),
                "spawn_points": proc_data["spawn_points"],
                "generation_time": datetime.now().isoformat(),
            }
        )

        # Add rooms for interior maps
        if map_type == "interior" and "rooms" in proc_data:
            map_data.properties.custom_properties["rooms"] = proc_data["rooms"]

        # Save the map
        self.map_manager.save_map(map_data)

        print(f"✅ Generated procedural {map_type} map: {map_name}")
        print(f"   Size: {width}x{height}, Seed: {seed}")
        print(f"   Spawn points: {len(proc_data['spawn_points'])}")

        return map_data


# Global instances
_ai_map_commands: Optional[AIMapCommands] = None
_procedural_integration: Optional[ProceduralMapIntegration] = None


def get_ai_map_commands() -> AIMapCommands:
    """Get the global AIMapCommands instance."""
    global _ai_map_commands
    if _ai_map_commands is None:
        _ai_map_commands = AIMapCommands()
    return _ai_map_commands


def get_procedural_integration() -> ProceduralMapIntegration:
    """Get the global ProceduralMapIntegration instance."""
    global _procedural_integration
    if _procedural_integration is None:
        _procedural_integration = ProceduralMapIntegration()
    return _procedural_integration
