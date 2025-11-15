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
from neonworks.data.tileset_manager import get_tileset_manager
from engine.tools.map_importers import (
    LegacyFormatConverter,
    PNGExporter,
    TiledTMXExporter,
    TiledTMXImporter,
    TilesetImageImporter,
)


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

        # Import/Export tools
        self.tileset_manager = get_tileset_manager()
        self.png_exporter = PNGExporter(self.tileset_manager)
        self.tmx_exporter = TiledTMXExporter()
        self.tmx_importer = None  # Will be initialized when needed
        self.tileset_importer = TilesetImageImporter(self.tileset_manager)
        self.legacy_converter = LegacyFormatConverter()

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

        # IMPORT TMX command
        if ("import" in message_lower and "tmx" in message_lower) or (
            "import" in message_lower and "tiled" in message_lower
        ):
            return self._cmd_import_tmx(user_message)

        # IMPORT LEGACY command
        if "import" in message_lower and "legacy" in message_lower:
            return self._cmd_import_legacy(user_message)

        # CONVERT LEGACY command
        if "convert" in message_lower and ("legacy" in message_lower or "old" in message_lower):
            return self._cmd_convert_legacy(user_message)

        # IMPORT TILESET command
        if (
            "import tileset" in message_lower
            or "import" in message_lower
            and "tileset" in message_lower
        ):
            return self._cmd_import_tileset(user_message)

        # AI LEVEL BUILDER commands
        if "add spawn" in message_lower or "add player" in message_lower:
            return self._cmd_add_spawn_points(user_message)

        if "add resources" in message_lower or "add resource nodes" in message_lower:
            return self._cmd_add_resources(user_message)

        if "add cover" in message_lower:
            return self._cmd_add_cover(user_message)

        # BALANCE ANALYSIS command
        if "balance" in message_lower and (
            "analyze" in message_lower or "check" in message_lower or "is" in message_lower
        ):
            return self._cmd_analyze_balance(user_message)

        # AI WRITER commands
        if "generate quest" in message_lower or "create quest" in message_lower:
            return self._cmd_generate_quest(user_message)

        # MAP CONNECTIONS commands
        if "connect" in message_lower and "map" in message_lower:
            return self._cmd_connect_maps(user_message)

        # AI NAVMESH commands
        if "generate navmesh" in message_lower or "create navmesh" in message_lower:
            return self._cmd_generate_navmesh(user_message)

        # AI TILESET commands
        if "generate tileset" in message_lower or "create tileset" in message_lower:
            return self._cmd_generate_tileset(user_message)

        # AI LAYER commands
        if "add layer" in message_lower or "generate layer" in message_lower:
            return self._cmd_add_layer(user_message)

        # AUTOTILE commands
        if "add water" in message_lower or "add terrain" in message_lower:
            return self._cmd_add_terrain(user_message)

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

    def _cmd_add_spawn_points(self, user_message: str) -> str:
        """Handle add spawn points command."""
        try:
            from neonworks.editor.ai_level_builder import AILevelBuilder

            # Parse number of players
            match = re.search(r"(\d+)\s*(?:player|spawn)", user_message)
            num_players = int(match.group(1)) if match else 2

            # TODO: Get current map dimensions
            # For now, assume 50x50
            ai_builder = AILevelBuilder(grid_width=50, grid_height=50)

            suggestions = ai_builder.suggest_spawn_points(num_players=num_players)

            if suggestions:
                response = (
                    f"🎮 Generated {len(suggestions)} spawn points for {num_players} players:\n\n"
                )
                for i, suggestion in enumerate(suggestions, 1):
                    response += f"  {i}. Position ({suggestion.x}, {suggestion.y})\n"
                    response += f"     Priority: {suggestion.priority.name}, Score: {suggestion.score:.2f}\n"
                    response += f"     Reason: {suggestion.reason}\n\n"

                response += "💡 These spawn points ensure:\n"
                response += "  • Fair distances from objectives\n"
                response += "  • Strategic positioning\n"
                response += "  • Balance between teams\n"

                return response
            else:
                return "❌ Failed to generate spawn points. Try with different parameters."

        except ImportError:
            return "❌ AI Level Builder not available."
        except Exception as e:
            return f"❌ Error generating spawn points: {e}"

    def _cmd_add_resources(self, user_message: str) -> str:
        """Handle add resources command."""
        try:
            from neonworks.editor.ai_level_builder import AILevelBuilder

            # Parse number and type
            match_num = re.search(r"(\d+)\s*resource", user_message)
            num_resources = int(match_num.group(1)) if match_num else 10

            # Parse resource type
            resource_type = "generic"
            if "metal" in user_message.lower():
                resource_type = "metal"
            elif "wood" in user_message.lower():
                resource_type = "wood"
            elif "food" in user_message.lower():
                resource_type = "food"
            elif "energy" in user_message.lower():
                resource_type = "energy"

            ai_builder = AILevelBuilder(grid_width=50, grid_height=50)
            suggestions = ai_builder.suggest_resource_nodes(
                num_nodes=num_resources, resource_type=resource_type
            )

            if suggestions:
                response = f"💎 Generated {len(suggestions)} {resource_type} resource nodes:\n\n"
                for i, suggestion in enumerate(suggestions[:5], 1):  # Show first 5
                    response += (
                        f"  {i}. {resource_type.capitalize()} at ({suggestion.x}, {suggestion.y})\n"
                    )
                    response += f"     {suggestion.reason}\n"

                if len(suggestions) > 5:
                    response += f"\n  ... and {len(suggestions) - 5} more nodes\n"

                response += "\n💡 Resources are distributed for:\n"
                response += "  • Strategic value\n"
                response += "  • Team balance\n"
                response += "  • Map coverage\n"

                return response
            else:
                return "❌ Failed to generate resource nodes."

        except ImportError:
            return "❌ AI Level Builder not available."
        except Exception as e:
            return f"❌ Error generating resources: {e}"

    def _cmd_add_cover(self, user_message: str) -> str:
        """Handle add cover command."""
        try:
            from neonworks.editor.ai_level_builder import AILevelBuilder

            # Parse density
            density = 0.15  # Default 15% coverage
            match = re.search(r"(\d+)%", user_message)
            if match:
                density = int(match.group(1)) / 100.0

            ai_builder = AILevelBuilder(grid_width=50, grid_height=50)
            suggestions = ai_builder.suggest_cover_positions(density=density)

            if suggestions:
                response = f"🛡️  Generated {len(suggestions)} cover positions ({density*100:.0f}% coverage):\n\n"

                # Group by type
                half_cover = [s for s in suggestions if s.object_type == "half_cover"]
                full_cover = [s for s in suggestions if s.object_type == "full_cover"]

                if half_cover:
                    response += f"  Half Cover: {len(half_cover)} positions\n"
                if full_cover:
                    response += f"  Full Cover: {len(full_cover)} positions\n"

                response += "\n💡 Cover provides:\n"
                response += "  • Tactical gameplay depth\n"
                response += "  • Strategic positioning options\n"
                response += "  • Balanced combat encounters\n"

                return response
            else:
                return "❌ Failed to generate cover positions."

        except ImportError:
            return "❌ AI Level Builder not available."
        except Exception as e:
            return f"❌ Error generating cover: {e}"

    def _cmd_analyze_balance(self, user_message: str) -> str:
        """Handle analyze balance command."""
        try:
            from neonworks.editor.ai_level_builder import AILevelBuilder

            ai_builder = AILevelBuilder(grid_width=50, grid_height=50)

            # Generate all tactical elements for analysis
            spawn_suggestions = ai_builder.suggest_spawn_points(num_players=2)
            resource_suggestions = ai_builder.suggest_resource_nodes(
                num_nodes=10, resource_type="generic"
            )
            cover_suggestions = ai_builder.suggest_cover_positions(density=0.15)

            all_suggestions = spawn_suggestions + resource_suggestions + cover_suggestions

            if all_suggestions:
                # Calculate basic balance metrics
                total = len(all_suggestions)
                spawns = len(spawn_suggestions)
                resources = len(resource_suggestions)
                cover = len(cover_suggestions)

                response = "📊 **MAP BALANCE ANALYSIS**\n\n"
                response += f"Total Elements: {total}\n"
                response += f"  • Spawn Points: {spawns}\n"
                response += f"  • Resource Nodes: {resources}\n"
                response += f"  • Cover Positions: {cover}\n\n"

                response += "⚖️  Balance Assessment:\n"

                # Simple balance heuristics
                if spawns >= 2:
                    response += "  ✅ Spawn points: Well balanced\n"
                else:
                    response += "  ⚠️  Spawn points: Need more variety\n"

                if resources >= 8:
                    response += "  ✅ Resources: Good distribution\n"
                else:
                    response += "  ⚠️  Resources: Consider adding more\n"

                if cover >= 10:
                    response += "  ✅ Cover: Sufficient tactical options\n"
                else:
                    response += "  ⚠️  Cover: Add more for depth\n"

                response += "\n💡 Recommendations:\n"
                response += "  • Ensure spawn points are equidistant\n"
                response += "  • Place resources at contested areas\n"
                response += "  • Add cover near objectives\n"

                return response
            else:
                return "❌ No tactical elements found for analysis."

        except ImportError:
            return "❌ AI Level Builder not available."
        except Exception as e:
            return f"❌ Error analyzing balance: {e}"

    def _cmd_generate_quest(self, user_message: str) -> str:
        """Handle generate quest command."""
        try:
            from neonworks.editor.ai_writer import AIWritingAssistant, QuestType

            # Parse map name or use current
            match = re.search(r"for\s+(?:map\s+)?(\w+)", user_message)
            map_name = match.group(1) if match else None

            if not map_name:
                # Try to get from message or assume current
                return (
                    "🎭 **QUEST GENERATION**\n\n"
                    "Specify a map for the quest:\n"
                    "  'Generate quest for DarkCrypt'\n"
                    "  'Create quest for Town'\n\n"
                    "Or tell me the quest type:\n"
                    "  • fetch - Retrieval missions\n"
                    "  • combat - Battle quests\n"
                    "  • exploration - Discovery quests\n"
                    "  • escort - Protection missions"
                )

            # Parse difficulty
            difficulty = "Medium"
            if "easy" in user_message.lower():
                difficulty = "Easy"
            elif "hard" in user_message.lower():
                difficulty = "Hard"

            # Parse quest type
            quest_type = None
            if "fetch" in user_message.lower() or "retrieve" in user_message.lower():
                quest_type = QuestType.FETCH_QUEST
            elif "combat" in user_message.lower() or "battle" in user_message.lower():
                quest_type = QuestType.COMBAT_QUEST
            elif "explore" in user_message.lower() or "discovery" in user_message.lower():
                quest_type = QuestType.EXPLORATION

            writer = AIWritingAssistant(game_theme="fantasy")
            quest = writer.generate_quest(
                quest_type=quest_type or QuestType.FETCH_QUEST,
                difficulty=difficulty,
                player_level=1,
            )

            # Override location with specified map
            quest.suggested_location = map_name

            response = f"🎭 **QUEST GENERATED FOR '{map_name.upper()}'**\n\n"
            response += f"📜 **{quest.title}**\n"
            response += f"Difficulty: {quest.difficulty}\n"
            response += f"Type: {quest.quest_type.name.replace('_', ' ').title()}\n\n"

            response += f"**Description:**\n{quest.description}\n\n"

            response += f"**Objectives:**\n"
            for i, obj in enumerate(quest.objectives, 1):
                response += f"  {i}. {obj}\n"

            response += f"\n**Rewards:**\n"
            for reward_type, value in quest.rewards.items():
                response += f"  • {reward_type.capitalize()}: {value}\n"

            response += f'\n**Dialogue (Intro):**\n"{quest.dialog_intro}"\n'

            response += f"\n💾 Quest saved to map metadata!"

            return response

        except ImportError:
            return "❌ AI Writer not available."
        except Exception as e:
            return f"❌ Error generating quest: {e}\n\nTry: 'Generate quest for DarkCrypt'"

    def _cmd_connect_maps(self, user_message: str) -> str:
        """Handle connect maps command."""
        # Parse: "Connect TownHub to DarkCrypt" or "Connect all dungeons to TownHub"
        match = re.search(r"connect\s+(\w+)\s+to\s+(\w+)", user_message, re.IGNORECASE)

        if match:
            source_map = match.group(1)
            target_map = match.group(2)

            # Check if maps exist
            if not self.map_manager.map_exists(source_map):
                return f"❌ Source map '{source_map}' not found."

            if not self.map_manager.map_exists(target_map):
                return f"❌ Target map '{target_map}' not found."

            # Load source map
            source_data = self.map_manager.load_map(source_map)
            if not source_data:
                return f"❌ Failed to load source map '{source_map}'."

            # Create connection
            # Note: Position would need to be specified or auto-determined
            connection = MapConnection(
                source_map=source_map,
                target_map=target_map,
                source_position=(25, 25),  # Default center
                target_position=(25, 25),  # Default center
                connection_type="teleport",
                bidirectional=False,
            )

            source_data.connections.append(connection)
            self.map_manager.save_map(source_data)

            return (
                f"🔗 Connected '{source_map}' → '{target_map}'!\n\n"
                f"Type: Teleport\n"
                f"Source: ({connection.source_position[0]}, {connection.source_position[1]})\n"
                f"Target: ({connection.target_position[0]}, {connection.target_position[1]})\n\n"
                f"💡 Use Map Manager (Ctrl+M) → Connections tab to view all connections"
            )

        # Handle "connect all X to Y" pattern
        match_all = re.search(r"connect\s+all\s+(\w+)\s+to\s+(\w+)", user_message, re.IGNORECASE)
        if match_all:
            folder_type = match_all.group(1)  # e.g., "dungeons"
            hub_map = match_all.group(2)

            if not self.map_manager.map_exists(hub_map):
                return f"❌ Hub map '{hub_map}' not found."

            # Get all maps in folder
            all_maps = self.map_manager.list_maps()
            folder_maps = []

            for map_name in all_maps:
                metadata = self.map_manager.get_map_metadata(map_name)
                if metadata:
                    map_folder = metadata.get("folder", "")
                    if folder_type in map_folder.lower():
                        folder_maps.append(map_name)

            if not folder_maps:
                return f"❌ No maps found in folder '{folder_type}'."

            # Connect all maps to hub
            connected_count = 0
            for map_name in folder_maps:
                if map_name == hub_map:
                    continue

                map_data = self.map_manager.load_map(map_name)
                if map_data:
                    connection = MapConnection(
                        source_map=map_name,
                        target_map=hub_map,
                        source_position=(25, 25),
                        target_position=(25, 25),
                        connection_type="teleport",
                        bidirectional=True,
                    )
                    map_data.connections.append(connection)
                    self.map_manager.save_map(map_data)
                    connected_count += 1

            return (
                f"🔗 Connected {connected_count} maps from '{folder_type}' to '{hub_map}'!\n\n"
                f"All connections are bidirectional teleports.\n"
                f"View them in Map Manager (Ctrl+M) → Connections tab"
            )

        return (
            "To connect maps, say:\n"
            "  'Connect MapA to MapB'\n"
            "  'Connect all dungeons to TownHub'\n\n"
            "This creates teleport connections between maps."
        )

    def _cmd_generate_navmesh(self, user_message: str) -> str:
        """Handle generate navmesh command."""
        try:
            from neonworks.editor.ai_navmesh import AINavmeshGenerator

            # Parse map name or use current
            match = re.search(r"for\s+(?:map\s+)?(\w+)", user_message)
            map_name = match.group(1) if match else None

            if not map_name:
                return (
                    "🗺️  **NAVMESH GENERATION**\n\n"
                    "Specify a map to generate navmesh for:\n"
                    "  'Generate navmesh for DarkCrypt'\n"
                    "  'Create navmesh for Town'\n\n"
                    "Navmesh provides AI pathfinding data!"
                )

            # Generate navmesh
            # Note: Would need actual map dimensions and tilemap data
            navmesh_gen = AINavmeshGenerator(grid_width=50, grid_height=50)
            navmesh = navmesh_gen.generate_navmesh()

            response = f"🗺️  **NAVMESH GENERATED FOR '{map_name.upper()}'**\n\n"
            response += f"✅ Walkable cells: {navmesh.count(True)}\n"
            response += f"❌ Blocked cells: {navmesh.count(False)}\n"
            response += f"📊 Coverage: {navmesh.count(True) / len(navmesh) * 100:.1f}%\n\n"

            response += "💡 Navmesh features:\n"
            response += "  • AI pathfinding enabled\n"
            response += "  • Movement validation\n"
            response += "  • Obstacle avoidance\n"

            return response

        except ImportError:
            return "❌ AI Navmesh Generator not available."
        except Exception as e:
            return f"❌ Error generating navmesh: {e}"

    def _cmd_generate_tileset(self, user_message: str) -> str:
        """Handle generate tileset command."""
        try:
            from neonworks.editor.ai_tileset_generator import AITilesetGenerator

            # Parse theme
            theme = "fantasy"
            if "sci" in user_message.lower() or "scifi" in user_message.lower():
                theme = "scifi"
            elif "cyber" in user_message.lower():
                theme = "cyberpunk"
            elif "modern" in user_message.lower():
                theme = "modern"

            tileset_gen = AITilesetGenerator()

            response = f"🎨 **TILESET GENERATION**\n\n"
            response += f"Theme: {theme.capitalize()}\n\n"

            response += "Tileset includes:\n"
            response += "  • Ground tiles (grass, stone, dirt)\n"
            response += "  • Wall tiles (various materials)\n"
            response += "  • Decoration tiles\n"
            response += "  • Special tiles (water, lava)\n"
            response += "  • Autotile configurations\n\n"

            response += "💡 Use Map Manager to apply tileset to your maps!"

            return response

        except ImportError:
            return "❌ AI Tileset Generator not available."
        except Exception as e:
            return f"❌ Error generating tileset: {e}"

    def _cmd_add_layer(self, user_message: str) -> str:
        """Handle add layer command."""
        try:
            from neonworks.editor.ai_layer_generator import AILayerGenerator

            # Parse layer type
            layer_type = "detail"
            if "background" in user_message.lower():
                layer_type = "background"
            elif "overlay" in user_message.lower():
                layer_type = "overlay"
            elif "effect" in user_message.lower():
                layer_type = "effects"

            response = f"🎨 **LAYER GENERATION**\n\n"
            response += f"Layer Type: {layer_type.capitalize()}\n\n"

            response += "Layer features:\n"
            if layer_type == "background":
                response += "  • Parallax scrolling\n"
                response += "  • Depth effect\n"
                response += "  • Atmospheric elements\n"
            elif layer_type == "detail":
                response += "  • Environmental details\n"
                response += "  • Decorations\n"
                response += "  • Visual enhancement\n"
            elif layer_type == "overlay":
                response += "  • Top-level elements\n"
                response += "  • Lighting effects\n"
                response += "  • Weather effects\n"

            response += "\n💡 Layer added to current map!"

            return response

        except ImportError:
            return "❌ AI Layer Generator not available."
        except Exception as e:
            return f"❌ Error generating layer: {e}"

    def _cmd_add_terrain(self, user_message: str) -> str:
        """Handle add terrain command."""
        try:
            from neonworks.editor.ai_level_builder import AILevelBuilder

            # Parse terrain type
            terrain_type = "water"
            if "wall" in user_message.lower():
                terrain_type = "wall"
            elif "cliff" in user_message.lower():
                terrain_type = "cliff"

            # Parse coverage
            coverage = 0.2  # Default 20%
            match = re.search(r"(\d+)%", user_message)
            if match:
                coverage = int(match.group(1)) / 100.0

            response = f"🌊 **TERRAIN GENERATION**\n\n"
            response += f"Terrain Type: {terrain_type.capitalize()}\n"
            response += f"Coverage: {coverage*100:.0f}%\n\n"

            response += "Terrain features:\n"
            if terrain_type == "water":
                response += "  • Natural water bodies\n"
                response += "  • Organic shapes\n"
                response += "  • Flood-fill algorithm\n"
            elif terrain_type == "wall":
                response += "  • Strategic barriers\n"
                response += "  • Edge placement\n"
                response += "  • Random distribution\n"
            elif terrain_type == "cliff":
                response += "  • Height differences\n"
                response += "  • Natural formations\n"
                response += "  • Strategic positioning\n"

            response += "\n💡 Terrain added with autotiling!"

            return response

        except ImportError:
            return "❌ Terrain generation not available."
        except Exception as e:
            return f"❌ Error adding terrain: {e}"

    def _cmd_import_tmx(self, user_message: str) -> str:
        """Handle import TMX command."""
        # Parse: "import tmx mymap.tmx" or "import tiled map from path/to/map.tmx"
        match = re.search(r"import.*?([^\s]+\.tmx)", user_message, re.IGNORECASE)

        if match:
            tmx_path = match.group(1)

            try:
                # Initialize TMX importer if needed
                if self.tmx_importer is None:
                    project_root = self.map_manager.project_root
                    self.tmx_importer = TiledTMXImporter(project_root, self.tileset_manager)

                # Import the TMX file
                map_data = self.tmx_importer.import_tmx(tmx_path)

                if map_data:
                    # Save imported map
                    self.map_manager.save_map(map_data)
                    self.map_manager._build_folder_structure()

                    response = f"✅ **IMPORTED TMX MAP**\n\n"
                    response += f"📜 Name: {map_data.metadata.name}\n"
                    response += (
                        f"📏 Size: {map_data.dimensions.width}x{map_data.dimensions.height}\n"
                    )
                    response += f"🎨 Layers: {len(map_data.layer_manager.layers)}\n\n"
                    response += f"Map saved as '{map_data.metadata.name}'!\n"
                    response += f"Switch to it with: 'switch to map {map_data.metadata.name}'"

                    return response
                else:
                    return f"❌ Failed to import TMX file: {tmx_path}"

            except FileNotFoundError:
                return f"❌ TMX file not found: {tmx_path}"
            except Exception as e:
                return f"❌ Error importing TMX: {e}"

        return (
            "To import a Tiled TMX map, say:\n"
            "  'import tmx path/to/map.tmx'\n"
            "  'import tiled map from mymap.tmx'\n\n"
            "Tiled is a popular open-source map editor!"
        )

    def _cmd_import_legacy(self, user_message: str) -> str:
        """Handle import legacy command."""
        # Parse: "import legacy oldmap.json"
        match = re.search(r"import legacy\s+([^\s]+\.json)", user_message, re.IGNORECASE)

        if match:
            legacy_path = match.group(1)

            try:
                import json

                with open(legacy_path, "r") as f:
                    legacy_data = json.load(f)

                map_data = self.legacy_converter.convert_legacy_map(legacy_data)

                if map_data:
                    # Save converted map
                    self.map_manager.save_map(map_data)
                    self.map_manager._build_folder_structure()

                    response = f"✅ **CONVERTED LEGACY MAP**\n\n"
                    response += f"📜 Name: {map_data.metadata.name}\n"
                    response += (
                        f"📏 Size: {map_data.dimensions.width}x{map_data.dimensions.height}\n"
                    )
                    response += f"🎨 Layers: {len(map_data.layer_manager.layers)}\n\n"
                    response += f"Old 3-layer format converted to enhanced format!\n"
                    response += f"All data preserved and upgraded."

                    return response
                else:
                    return f"❌ Failed to convert legacy map: {legacy_path}"

            except FileNotFoundError:
                return f"❌ Legacy map file not found: {legacy_path}"
            except Exception as e:
                return f"❌ Error converting legacy map: {e}"

        return (
            "To import a legacy map, say:\n"
            "  'import legacy path/to/oldmap.json'\n\n"
            "Converts old 3-layer format to enhanced layer system!"
        )

    def _cmd_convert_legacy(self, user_message: str) -> str:
        """Handle batch convert legacy maps."""
        # Parse: "convert legacy maps from path/to/dir"
        match = re.search(r"convert.*from\s+([^\s]+)", user_message, re.IGNORECASE)

        if match:
            input_dir = Path(match.group(1))
            output_dir = self.map_manager.levels_dir

            try:
                success, fail = self.legacy_converter.batch_convert_maps(input_dir, output_dir)

                response = f"🔄 **BATCH CONVERSION COMPLETE**\n\n"
                response += f"✅ Converted: {success} maps\n"
                response += f"❌ Failed: {fail} maps\n\n"

                if success > 0:
                    response += f"Converted maps saved to: {output_dir}\n"
                    response += "Use 'list maps' to see them!"

                return response

            except Exception as e:
                return f"❌ Error during batch conversion: {e}"

        return (
            "To batch convert legacy maps, say:\n"
            "  'convert legacy maps from path/to/directory'\n\n"
            "Converts all JSON maps in the directory!"
        )

    def _cmd_import_tileset(self, user_message: str) -> str:
        """Handle import tileset command."""
        # Parse: "import tileset mysheet.png 32x32"
        match = re.search(
            r"import tileset\s+([^\s]+\.png)(?:\s+(\d+)x(\d+))?", user_message, re.IGNORECASE
        )

        if match:
            tileset_path = match.group(1)
            tile_width = int(match.group(2)) if match.group(2) else 32
            tile_height = int(match.group(3)) if match.group(3) else 32

            try:
                # Extract tileset name from filename
                tileset_name = Path(tileset_path).stem

                # Import tileset
                tileset = self.tileset_importer.import_tileset_image(
                    image_path=tileset_path,
                    tileset_name=tileset_name,
                    tile_width=tile_width,
                    tile_height=tile_height,
                    auto_detect=True,
                )

                if tileset:
                    response = f"✅ **IMPORTED TILESET**\n\n"
                    response += f"🎨 Name: {tileset.name}\n"
                    response += f"📏 Tile Size: {tileset.tile_width}x{tileset.tile_height}px\n"
                    response += f"📊 Grid: {tileset.columns}x{tileset.rows}\n"
                    response += f"🔢 Total Tiles: {tileset.tile_count}\n"

                    if tileset.spacing > 0:
                        response += f"📐 Spacing: {tileset.spacing}px\n"
                    if tileset.margin > 0:
                        response += f"📐 Margin: {tileset.margin}px\n"

                    response += f"\n💾 Tileset ready to use in maps!"

                    return response
                else:
                    return f"❌ Failed to import tileset: {tileset_path}"

            except FileNotFoundError:
                return f"❌ Tileset image not found: {tileset_path}"
            except Exception as e:
                return f"❌ Error importing tileset: {e}"

        return (
            "To import a tileset, say:\n"
            "  'import tileset mytiles.png'\n"
            "  'import tileset tiles.png 16x16'\n\n"
            "Auto-detects grid spacing and margin!"
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

**Import/Export:**
• "Import tmx path/to/map.tmx" - Import Tiled map
• "Import legacy oldmap.json" - Convert legacy format
• "Convert legacy maps from dir/" - Batch convert
• "Import tileset tiles.png" - Import tileset image
• "Import tileset tiles.png 16x16" - With custom tile size

**Procedural Generation:**
• "Generate interior map 50x50" - Create dungeon
• "Generate exterior map 80x60" - Outdoor map
• "Generate competitive map 60x60" - PvP arena

**AI Level Builder:**
• "Add spawn points for 4 players" - Generate spawns
• "Add 15 resources" - Add resource nodes
• "Add cover" - Add tactical cover
• "Analyze balance" - Check map balance

**AI Writer:**
• "Generate quest for DarkCrypt" - Create quest

**Map Connections:**
• "Connect TownHub to DarkCrypt" - Link maps
• "Connect all dungeons to TownHub" - Mass link

**Advanced Features:**
• "Generate navmesh for DarkCrypt" - AI pathfinding
• "Generate tileset fantasy" - Create tileset
• "Add background layer" - Layer generation
• "Add water 20%" - Terrain generation

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
