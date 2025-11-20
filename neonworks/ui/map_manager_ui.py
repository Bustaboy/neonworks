"""
NeonWorks Map Manager UI - Visual Map Management Interface.

Provides comprehensive map management including:
- Map list with folder organization
- Map preview with minimap
- Map properties editing
- Quick switch between maps
- Map duplication and templates
- Batch operations (export all, batch resize)
- Map linking visualization
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pygame

from engine.tools.map_importers import PNGExporter, TiledTMXExporter, TiledTMXImporter, TilesetImageImporter
from neonworks.data.map_manager import (
    MapConnection,
    MapData,
    MapFolder,
    MapManager,
    get_map_manager,
    initialize_map_manager,
)
from neonworks.data.tileset_manager import get_tileset_manager
from neonworks.rendering.ui import UI


class MapManagerUI:
    """Visual UI for managing maps in a project."""

    def __init__(self, screen: pygame.Surface, project_root: Optional[Path] = None):
        """
        Initialize the map manager UI.

        Args:
            screen: Pygame surface to render to
            project_root: Root directory of the project
        """
        self.screen = screen
        self.ui = UI(screen)

        self.visible = False
        self.current_mode = "browser"  # browser, batch, connections

        # Map manager
        self.map_manager: Optional[MapManager] = None
        if project_root:
            self.map_manager = initialize_map_manager(project_root)
        else:
            self.map_manager = get_map_manager()

        # State
        self.selected_map: Optional[str] = None
        self.selected_maps: Set[str] = set()  # For batch operations
        self.current_folder: MapFolder = None
        self.expanded_folders: Set[str] = set()  # Folder paths that are expanded

        # Scroll state
        self.map_list_scroll = 0
        self.properties_scroll = 0

        # Dialogs
        self.show_new_map_dialog = False
        self.show_duplicate_dialog = False
        self.show_batch_dialog = False
        self.show_template_dialog = False
        self.show_delete_confirm = False
        self.show_import_dialog = False
        self.show_export_dialog = False
        self.show_tileset_import_dialog = False

        # Input buffers
        self.new_map_name = ""
        self.new_map_width = "50"
        self.new_map_height = "50"
        self.new_map_folder = ""
        self.duplicate_target_name = ""
        self.template_name = ""
        self.batch_resize_width = "50"
        self.batch_resize_height = "50"
        self.export_path = ""

        # Filter
        self.search_filter = ""
        self.tag_filter = ""

        # Import/Export tools
        self.tileset_manager = get_tileset_manager()
        self.png_exporter = PNGExporter(self.tileset_manager)
        self.tmx_exporter = TiledTMXExporter()
        self.tmx_importer = (
            TiledTMXImporter(project_root, self.tileset_manager) if project_root else None
        )
        self.tileset_importer = TilesetImageImporter(self.tileset_manager)
        # Import/Export state
        self.import_format = "tmx"
        self.export_format = "png"  # png, tmx, minimap
        self.import_file_path = ""
        self.export_file_path = ""
        self.export_scale = "1.0"
        self.minimap_size = "256"

    def toggle(self) -> None:
        """Toggle visibility of the map manager."""
        self.visible = not self.visible
        if self.visible and self.map_manager:
            # Refresh map list when opening
            self.map_manager._build_folder_structure()
            if self.current_folder is None:
                self.current_folder = self.map_manager.root_folder

    def render(self) -> None:
        """Render the map manager UI."""
        if not self.visible or not self.map_manager:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Main panel
        panel_width = min(1400, screen_width - 40)
        panel_height = min(800, screen_height - 40)
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (20, 20, 30))

        # Title
        self.ui.title(
            "Map Manager",
            panel_x + 20,
            panel_y + 10,
            size=24,
            color=(100, 200, 255),
        )

        # Close button
        if self.ui.button("X", panel_x + panel_width - 50, panel_y + 10, 35, 35, color=(150, 0, 0)):
            self.toggle()

        # Mode tabs
        self._render_mode_tabs(panel_x, panel_y + 50, panel_width)

        # Content area
        content_y = panel_y + 90
        content_height = panel_height - 100

        if self.current_mode == "browser":
            self._render_browser_mode(panel_x, content_y, panel_width, content_height)
        elif self.current_mode == "batch":
            self._render_batch_mode(panel_x, content_y, panel_width, content_height)
        elif self.current_mode == "connections":
            self._render_connections_mode(panel_x, content_y, panel_width, content_height)

        # Dialogs (render on top)
        self._render_dialogs(panel_x, panel_y, panel_width, panel_height)

    def _render_mode_tabs(self, x: int, y: int, width: int) -> None:
        """Render mode selection tabs."""
        tab_width = (width - 40) // 3

        # Browser tab
        browser_color = (0, 100, 200) if self.current_mode == "browser" else (50, 50, 70)
        if self.ui.button("Map Browser", x + 10, y, tab_width, 35, color=browser_color):
            self.current_mode = "browser"

        # Batch operations tab
        batch_color = (100, 150, 0) if self.current_mode == "batch" else (50, 50, 70)
        if self.ui.button(
            "Batch Operations", x + tab_width + 20, y, tab_width, 35, color=batch_color
        ):
            self.current_mode = "batch"

        # Connections tab
        conn_color = (150, 50, 150) if self.current_mode == "connections" else (50, 50, 70)
        if self.ui.button(
            "Map Connections", x + 2 * tab_width + 30, y, tab_width, 35, color=conn_color
        ):
            self.current_mode = "connections"

    def _render_browser_mode(self, x: int, y: int, width: int, height: int) -> None:
        """Render the map browser interface."""
        # Three-column layout
        list_width = 300
        preview_width = width - list_width - 320
        properties_width = 300

        # Map list (left)
        self._render_map_list(x + 10, y, list_width, height - 10)

        # Preview (center)
        preview_x = x + list_width + 20
        self._render_map_preview(preview_x, y, preview_width, height - 10)

        # Properties (right)
        properties_x = preview_x + preview_width + 10
        self._render_map_properties(properties_x, y, properties_width, height - 10)

    def _render_map_list(self, x: int, y: int, width: int, height: int) -> None:
        """Render the map list panel."""
        self.ui.panel(x, y, width, height, (25, 25, 40))

        # Header
        self.ui.label("Maps", x + 10, y + 10, size=18, color=(200, 200, 255))

        # Search bar
        search_y = y + 40
        self.ui.label("Search:", x + 10, search_y, size=14, color=(180, 180, 180))
        # Note: Input field would go here (simplified for now)

        # Toolbar
        toolbar_y = y + 70
        button_width = (width - 30) // 2

        if self.ui.button("+ New", x + 10, toolbar_y, button_width, 30, color=(0, 120, 0)):
            self.show_new_map_dialog = True

        if self.ui.button("Duplicate", x + button_width + 20, toolbar_y, button_width, 30):
            if self.selected_map:
                self.show_duplicate_dialog = True

        # Templates button
        if self.ui.button(
            "Templates", x + 10, toolbar_y + 35, button_width, 30, color=(80, 80, 120)
        ):
            self.show_template_dialog = True

        # Delete button
        delete_enabled = self.selected_map is not None
        delete_color = (150, 0, 0) if delete_enabled else (80, 40, 40)
        if self.ui.button(
            "Delete", x + button_width + 20, toolbar_y + 35, button_width, 30, color=delete_color
        ):
            if delete_enabled:
                self.show_delete_confirm = True

        # Map list
        list_y = y + 145
        list_height = height - 155

        self._render_folder_tree(x + 10, list_y, width - 20, list_height)

    def _render_folder_tree(self, x: int, y: int, width: int, height: int) -> None:
        """Render the folder tree with maps."""
        if not self.map_manager:
            return

        # Scrollable area
        self.ui.panel(x, y, width, height, (30, 30, 45))

        item_height = 30
        current_y = y + 5 - self.map_list_scroll
        indent_size = 20

        # Render root folder and its contents
        self._render_folder_recursive(
            self.map_manager.root_folder,
            x + 5,
            current_y,
            width - 10,
            item_height,
            0,
            indent_size,
            y,
            y + height,
        )

    def _render_folder_recursive(
        self,
        folder: MapFolder,
        x: int,
        y: int,
        width: int,
        item_height: int,
        depth: int,
        indent_size: int,
        clip_top: int,
        clip_bottom: int,
    ) -> int:
        """
        Recursively render a folder and its contents.

        Returns:
            Updated y position
        """
        current_y = y

        # Render folder (skip root)
        if folder.parent is not None:
            if current_y + item_height >= clip_top and current_y < clip_bottom:
                indent = depth * indent_size
                folder_path = folder.get_path()
                is_expanded = folder_path in self.expanded_folders

                # Folder icon and name
                icon = "▼" if is_expanded else "▶"
                folder_text = f"{icon} 📁 {folder.name}"

                if self.ui.button(
                    folder_text,
                    x + indent,
                    current_y,
                    width - indent,
                    item_height - 5,
                    color=(60, 60, 80),
                ):
                    # Toggle folder expansion
                    if is_expanded:
                        self.expanded_folders.discard(folder_path)
                    else:
                        self.expanded_folders.add(folder_path)

            current_y += item_height

            # Only render children if expanded
            if folder.get_path() not in self.expanded_folders:
                return current_y

        # Render maps in this folder
        for map_name in sorted(folder.maps):
            if current_y + item_height >= clip_top and current_y < clip_bottom:
                indent = (depth + (1 if folder.parent is not None else 0)) * indent_size
                is_selected = self.selected_map == map_name

                map_color = (0, 100, 150) if is_selected else (50, 50, 70)
                button_text = f"🗺️  {map_name}"

                if self.ui.button(
                    button_text,
                    x + indent,
                    current_y,
                    width - indent,
                    item_height - 5,
                    color=map_color,
                ):
                    self.selected_map = map_name
                    self.properties_scroll = 0

            current_y += item_height

        # Render child folders
        for child_folder in sorted(folder.children, key=lambda f: f.name):
            current_y = self._render_folder_recursive(
                child_folder,
                x,
                current_y,
                width,
                item_height,
                depth + 1,
                indent_size,
                clip_top,
                clip_bottom,
            )

        return current_y

    def _render_map_preview(self, x: int, y: int, width: int, height: int) -> None:
        """Render the map preview panel."""
        self.ui.panel(x, y, width, height, (25, 25, 40))

        if not self.selected_map:
            self.ui.label(
                "No map selected",
                x + width // 2 - 70,
                y + height // 2,
                size=18,
                color=(120, 120, 120),
            )
            return

        # Map info header
        self.ui.label(
            self.selected_map,
            x + 10,
            y + 10,
            size=20,
            color=(200, 200, 255),
        )

        # Load map metadata
        metadata = self.map_manager.get_map_metadata(self.selected_map)
        if metadata:
            info_y = y + 40
            line_height = 20

            # Description
            description = metadata.get("description", "No description")
            self.ui.label(
                f"Description: {description[:50]}",
                x + 10,
                info_y,
                size=14,
                color=(180, 180, 180),
            )

            # Author
            author = metadata.get("author", "Unknown")
            self.ui.label(
                f"Author: {author}",
                x + 10,
                info_y + line_height,
                size=14,
                color=(180, 180, 180),
            )

            # Created date
            created = metadata.get("created_date", "")[:10]
            self.ui.label(
                f"Created: {created}",
                x + 10,
                info_y + line_height * 2,
                size=14,
                color=(180, 180, 180),
            )

            # Folder
            folder = metadata.get("folder", "Root")
            if not folder:
                folder = "Root"
            self.ui.label(
                f"Folder: {folder}",
                x + 10,
                info_y + line_height * 3,
                size=14,
                color=(180, 180, 180),
            )

            # Tags
            tags = metadata.get("tags", [])
            if tags:
                tags_text = ", ".join(tags[:5])
                self.ui.label(
                    f"Tags: {tags_text}",
                    x + 10,
                    info_y + line_height * 4,
                    size=14,
                    color=(180, 180, 180),
                )

        # Minimap preview placeholder
        preview_y = y + 150
        preview_size = min(width - 20, height - 170)

        self.ui.panel(
            x + (width - preview_size) // 2,
            preview_y,
            preview_size,
            preview_size,
            (40, 40, 55),
        )

        self.ui.label(
            "Map Preview",
            x + width // 2 - 50,
            preview_y + preview_size // 2,
            size=16,
            color=(100, 100, 100),
        )

        # Actions
        action_y = preview_y + preview_size + 10
        button_width = (width - 30) // 3

        if self.ui.button("Open", x + 10, action_y, button_width, 35, color=(0, 150, 0)):
            # TODO: Emit event to open map in level editor
            pass

        if self.ui.button("Edit Props", x + button_width + 20, action_y, button_width, 35):
            # Scroll properties panel to top
            self.properties_scroll = 0

        if self.ui.button(
            "Export", x + 2 * button_width + 30, action_y, button_width, 35, color=(100, 100, 150)
        ):
            self.show_export_dialog = True

        # Import button (second row)
        action_y += 40
        if self.ui.button("Import Map", x + 10, action_y, button_width, 35, color=(0, 100, 150)):
            self.show_import_dialog = True

        if self.ui.button(
            "Import Tileset",
            x + button_width + 20,
            action_y,
            button_width,
            35,
            color=(150, 100, 0),
        ):
            self.show_tileset_import_dialog = True

    def _render_map_properties(self, x: int, y: int, width: int, height: int) -> None:
        """Render the map properties panel."""
        self.ui.panel(x, y, width, height, (25, 25, 40))

        self.ui.label("Properties", x + 10, y + 10, size=18, color=(200, 200, 255))

        if not self.selected_map:
            self.ui.label(
                "Select a map",
                x + width // 2 - 50,
                y + height // 2,
                size=14,
                color=(120, 120, 120),
            )
            return

        # Load full map data
        map_data = self.map_manager.load_map(self.selected_map, cache=False)
        if not map_data:
            self.ui.label(
                "Failed to load map",
                x + 10,
                y + 40,
                size=14,
                color=(200, 50, 50),
            )
            return

        # Scrollable properties
        props_y = y + 40
        line_height = 25

        current_y = props_y - self.properties_scroll

        # Dimensions
        self.ui.label(
            f"Dimensions: {map_data.dimensions.width} x {map_data.dimensions.height}",
            x + 10,
            current_y,
            size=14,
        )
        current_y += line_height

        self.ui.label(
            f"Tile Size: {map_data.dimensions.tile_size}px",
            x + 10,
            current_y,
            size=14,
        )
        current_y += line_height * 1.5

        # Tileset
        self.ui.label("Tileset:", x + 10, current_y, size=14, color=(200, 200, 255))
        current_y += line_height

        tileset_name = map_data.tileset.tileset_name or "None"
        self.ui.label(
            f"  {tileset_name}",
            x + 10,
            current_y,
            size=13,
            color=(180, 180, 180),
        )
        current_y += line_height * 1.5

        # Layers
        layer_count = len(map_data.layer_manager.layer_order)
        self.ui.label(
            f"Layers: {layer_count}",
            x + 10,
            current_y,
            size=14,
        )
        current_y += line_height * 1.5

        # Properties
        self.ui.label("Game Properties:", x + 10, current_y, size=14, color=(200, 200, 255))
        current_y += line_height

        if map_data.properties.bgm:
            self.ui.label(
                f"  BGM: {map_data.properties.bgm}",
                x + 10,
                current_y,
                size=13,
                color=(180, 180, 180),
            )
            current_y += line_height

        self.ui.label(
            f"  Encounters: {map_data.properties.encounter_rate}%",
            x + 10,
            current_y,
            size=13,
            color=(180, 180, 180),
        )
        current_y += line_height

        self.ui.label(
            f"  Weather: {map_data.properties.weather}",
            x + 10,
            current_y,
            size=13,
            color=(180, 180, 180),
        )
        current_y += line_height

        self.ui.label(
            f"  Time: {map_data.properties.time_of_day}",
            x + 10,
            current_y,
            size=13,
            color=(180, 180, 180),
        )
        current_y += line_height * 1.5

        # Connections
        connection_count = len(map_data.connections)
        self.ui.label(
            f"Connections: {connection_count}",
            x + 10,
            current_y,
            size=14,
        )
        current_y += line_height

        for i, conn in enumerate(map_data.connections[:5]):  # Show first 5
            self.ui.label(
                f"  → {conn.target_map}",
                x + 10,
                current_y,
                size=13,
                color=(150, 200, 150),
            )
            current_y += line_height

        if connection_count > 5:
            self.ui.label(
                f"  ... and {connection_count - 5} more",
                x + 10,
                current_y,
                size=12,
                color=(120, 120, 120),
            )

    def _render_batch_mode(self, x: int, y: int, width: int, height: int) -> None:
        """Render batch operations interface."""
        self.ui.panel(x + 10, y, width - 20, height, (25, 25, 40))

        self.ui.label(
            "Batch Operations",
            x + 20,
            y + 10,
            size=20,
            color=(200, 255, 200),
        )

        # Selection info
        selected_count = len(self.selected_maps)
        total_count = len(self.map_manager.list_maps())

        self.ui.label(
            f"Selected: {selected_count} / {total_count} maps",
            x + 20,
            y + 45,
            size=16,
            color=(180, 180, 180),
        )

        # Selection buttons
        button_y = y + 75
        button_width = 150

        if self.ui.button("Select All", x + 20, button_y, button_width, 30):
            self.selected_maps = set(self.map_manager.list_maps())

        if self.ui.button("Clear Selection", x + button_width + 30, button_y, button_width, 30):
            self.selected_maps.clear()

        # Batch operations
        ops_y = y + 120

        self.ui.label(
            "Operations:",
            x + 20,
            ops_y,
            size=18,
            color=(200, 200, 255),
        )

        ops_y += 35

        # Batch resize
        if self.ui.button(
            "Batch Resize",
            x + 20,
            ops_y,
            200,
            35,
            color=(100, 100, 150),
        ):
            if selected_count > 0:
                # TODO: Show batch resize dialog
                pass

        ops_y += 45

        # Batch export
        if self.ui.button(
            "Export Selected",
            x + 20,
            ops_y,
            200,
            35,
            color=(0, 150, 100),
        ):
            if selected_count > 0:
                # TODO: Show export dialog
                pass

        ops_y += 45

        # Batch tag
        if self.ui.button(
            "Add Tags",
            x + 20,
            ops_y,
            200,
            35,
            color=(150, 100, 0),
        ):
            if selected_count > 0:
                # TODO: Show tag dialog
                pass

        # Map selection list
        list_x = x + 250
        list_width = width - 280
        list_height = height - 40

        self._render_batch_selection_list(list_x, y + 20, list_width, list_height)

    def _render_batch_selection_list(self, x: int, y: int, width: int, height: int) -> None:
        """Render the map selection list for batch operations."""
        self.ui.panel(x, y, width, height, (30, 30, 45))

        self.ui.label("Select Maps:", x + 10, y + 10, size=16, color=(200, 200, 255))

        list_y = y + 40
        item_height = 35

        for i, map_name in enumerate(sorted(self.map_manager.list_maps())):
            if list_y + item_height > y + height:
                break

            is_selected = map_name in self.selected_maps
            checkbox = "☑" if is_selected else "☐"

            button_text = f"{checkbox}  {map_name}"
            button_color = (60, 80, 60) if is_selected else (50, 50, 70)

            if self.ui.button(
                button_text,
                x + 10,
                list_y,
                width - 20,
                item_height - 5,
                color=button_color,
            ):
                if is_selected:
                    self.selected_maps.discard(map_name)
                else:
                    self.selected_maps.add(map_name)

            list_y += item_height

    def _render_connections_mode(self, x: int, y: int, width: int, height: int) -> None:
        """Render map connections visualization."""
        self.ui.panel(x + 10, y, width - 20, height, (25, 25, 40))

        self.ui.label(
            "Map Connections Graph",
            x + 20,
            y + 10,
            size=20,
            color=(255, 200, 255),
        )

        # Get all connections
        all_connections = self.map_manager.get_all_connections()

        # Stats
        total_maps = len(self.map_manager.list_maps())
        connected_maps = len(all_connections)
        total_connections = sum(len(conns) for conns in all_connections.values())

        self.ui.label(
            f"Total Maps: {total_maps}",
            x + 20,
            y + 45,
            size=14,
            color=(180, 180, 180),
        )

        self.ui.label(
            f"Maps with Connections: {connected_maps}",
            x + 20,
            y + 70,
            size=14,
            color=(180, 180, 180),
        )

        self.ui.label(
            f"Total Connections: {total_connections}",
            x + 20,
            y + 95,
            size=14,
            color=(180, 180, 180),
        )

        # Connection list
        list_y = y + 130

        self.ui.label(
            "Connection Details:",
            x + 20,
            list_y,
            size=16,
            color=(200, 200, 255),
        )

        list_y += 30
        line_height = 25

        for map_name in sorted(all_connections.keys()):
            if list_y > y + height - 30:
                break

            connections = all_connections[map_name]

            self.ui.label(
                f"📍 {map_name}:",
                x + 30,
                list_y,
                size=14,
                color=(200, 255, 200),
            )
            list_y += line_height

            for conn in connections[:3]:  # Show first 3
                conn_text = f"  → {conn.target_map} ({conn.connection_type})"
                self.ui.label(
                    conn_text,
                    x + 50,
                    list_y,
                    size=13,
                    color=(150, 150, 200),
                )
                list_y += line_height

            if len(connections) > 3:
                self.ui.label(
                    f"  ... and {len(connections) - 3} more",
                    x + 50,
                    list_y,
                    size=12,
                    color=(120, 120, 120),
                )
                list_y += line_height

            list_y += 10  # Extra spacing between maps

    def _render_dialogs(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render any active dialogs."""
        if self.show_new_map_dialog:
            self._render_new_map_dialog(panel_x, panel_y, panel_width, panel_height)
        elif self.show_duplicate_dialog:
            self._render_duplicate_dialog(panel_x, panel_y, panel_width, panel_height)
        elif self.show_template_dialog:
            self._render_template_dialog(panel_x, panel_y, panel_width, panel_height)
        elif self.show_delete_confirm:
            self._render_delete_confirm(panel_x, panel_y, panel_width, panel_height)
        elif self.show_import_dialog:
            self._render_import_dialog(panel_x, panel_y, panel_width, panel_height)
        elif self.show_export_dialog:
            self._render_export_dialog(panel_x, panel_y, panel_width, panel_height)
        elif self.show_tileset_import_dialog:
            self._render_tileset_import_dialog(panel_x, panel_y, panel_width, panel_height)

    def _render_new_map_dialog(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render new map creation dialog."""
        dialog_width = 400
        dialog_height = 350
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        # Dialog background
        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (30, 30, 50))

        # Title
        self.ui.label(
            "Create New Map",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(100, 200, 255),
        )

        # Close button
        if self.ui.button(
            "X", dialog_x + dialog_width - 45, dialog_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.show_new_map_dialog = False
            return

        # Form
        form_y = dialog_y + 60
        line_height = 60

        # Name
        self.ui.label("Map Name:", dialog_x + 20, form_y, size=14)
        # TODO: Text input field
        self.ui.panel(dialog_x + 20, form_y + 25, dialog_width - 40, 30, (40, 40, 60))

        # Width
        self.ui.label("Width (tiles):", dialog_x + 20, form_y + line_height, size=14)
        self.ui.panel(
            dialog_x + 20, form_y + line_height + 25, (dialog_width - 50) // 2, 30, (40, 40, 60)
        )

        # Height
        self.ui.label(
            "Height (tiles):", dialog_x + dialog_width // 2, form_y + line_height, size=14
        )
        self.ui.panel(
            dialog_x + dialog_width // 2,
            form_y + line_height + 25,
            (dialog_width - 50) // 2,
            30,
            (40, 40, 60),
        )

        # Folder
        self.ui.label("Folder (optional):", dialog_x + 20, form_y + line_height * 2, size=14)
        self.ui.panel(
            dialog_x + 20, form_y + line_height * 2 + 25, dialog_width - 40, 30, (40, 40, 60)
        )

        # Buttons
        button_y = dialog_y + dialog_height - 50
        button_width = (dialog_width - 60) // 2

        if self.ui.button("Cancel", dialog_x + 20, button_y, button_width, 35):
            self.show_new_map_dialog = False

        if self.ui.button(
            "Create", dialog_x + button_width + 40, button_y, button_width, 35, color=(0, 150, 0)
        ):
            # TODO: Validate and create map
            # For now, just close dialog
            self.show_new_map_dialog = False

    def _render_duplicate_dialog(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render map duplication dialog."""
        dialog_width = 350
        dialog_height = 200
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (30, 30, 50))

        self.ui.label(
            "Duplicate Map",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(100, 200, 255),
        )

        if self.ui.button(
            "X", dialog_x + dialog_width - 45, dialog_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.show_duplicate_dialog = False
            return

        self.ui.label(
            f"Duplicate: {self.selected_map}",
            dialog_x + 20,
            dialog_y + 60,
            size=14,
            color=(180, 180, 180),
        )

        self.ui.label("New Name:", dialog_x + 20, dialog_y + 90, size=14)
        self.ui.panel(dialog_x + 20, dialog_y + 115, dialog_width - 40, 30, (40, 40, 60))

        button_y = dialog_y + dialog_height - 50
        button_width = (dialog_width - 60) // 2

        if self.ui.button("Cancel", dialog_x + 20, button_y, button_width, 35):
            self.show_duplicate_dialog = False

        if self.ui.button(
            "Duplicate", dialog_x + button_width + 40, button_y, button_width, 35, color=(0, 150, 0)
        ):
            # TODO: Validate and duplicate map
            self.show_duplicate_dialog = False

    def _render_template_dialog(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render template management dialog."""
        dialog_width = 500
        dialog_height = 400
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (30, 30, 50))

        self.ui.label(
            "Map Templates",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(100, 200, 255),
        )

        if self.ui.button(
            "X", dialog_x + dialog_width - 45, dialog_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.show_template_dialog = False
            return

        # Template list
        templates = self.map_manager.list_templates()

        self.ui.label(
            f"Available Templates ({len(templates)}):",
            dialog_x + 20,
            dialog_y + 60,
            size=16,
            color=(200, 200, 255),
        )

        list_y = dialog_y + 90
        item_height = 35

        for template in templates[:8]:  # Show first 8
            self.ui.button(
                f"📄 {template}",
                dialog_x + 20,
                list_y,
                dialog_width - 40,
                item_height - 5,
                color=(60, 60, 90),
            )
            list_y += item_height

        # Actions
        button_y = dialog_y + dialog_height - 50

        if self.ui.button("Close", dialog_x + 20, button_y, 120, 35):
            self.show_template_dialog = False

    def _render_delete_confirm(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render delete confirmation dialog."""
        dialog_width = 350
        dialog_height = 180
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (40, 20, 20))

        self.ui.label(
            "Confirm Deletion",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(255, 100, 100),
        )

        self.ui.label(
            f"Delete map: {self.selected_map}?",
            dialog_x + 20,
            dialog_y + 60,
            size=14,
            color=(255, 255, 255),
        )

        self.ui.label(
            "This action cannot be undone!",
            dialog_x + 20,
            dialog_y + 90,
            size=13,
            color=(255, 200, 100),
        )

        button_y = dialog_y + dialog_height - 50
        button_width = (dialog_width - 60) // 2

        if self.ui.button("Cancel", dialog_x + 20, button_y, button_width, 35, color=(80, 80, 80)):
            self.show_delete_confirm = False

        if self.ui.button(
            "Delete",
            dialog_x + button_width + 40,
            button_y,
            button_width,
            35,
            color=(200, 0, 0),
        ):
            if self.selected_map:
                self.map_manager.delete_map(self.selected_map)
                self.selected_map = None
                self.map_manager._build_folder_structure()
            self.show_delete_confirm = False

    def _render_import_dialog(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render import dialog."""
        dialog_width = 500
        dialog_height = 400
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (30, 30, 50))

        self.ui.label(
            "Import Map",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(100, 200, 255),
        )

        if self.ui.button(
            "X", dialog_x + dialog_width - 45, dialog_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.show_import_dialog = False
            return

        form_y = dialog_y + 60

        # Import format selection
        self.ui.label("Import Format:", dialog_x + 20, form_y, size=16, color=(200, 200, 255))
        form_y += 30

        button_width = 150
        tmx_color = (0, 120, 0) if self.import_format == "tmx" else (60, 60, 80)
        if self.ui.button("Tiled TMX", dialog_x + 20, form_y, button_width, 35, color=tmx_color):
            self.import_format = "tmx"

        form_y += 50

        # File path
        self.ui.label("Import File:", dialog_x + 20, form_y, size=14)
        form_y += 25
        self.ui.panel(dialog_x + 20, form_y, dialog_width - 40, 30, (40, 40, 60))
        self.ui.label(
            self.import_file_path or "Click Browse...",
            dialog_x + 30,
            form_y + 8,
            size=12,
            color=(150, 150, 150),
        )

        form_y += 40
        if self.ui.button("Browse...", dialog_x + 20, form_y, 120, 30):
            # TODO: File browser dialog
            pass

        form_y += 50

        # Info
        info_text = "Import maps from Tiled Map Editor (.tmx files)"

        self.ui.label(info_text, dialog_x + 20, form_y, size=12, color=(180, 180, 180))

        # Buttons
        button_y = dialog_y + dialog_height - 50
        button_width = (dialog_width - 60) // 2

        if self.ui.button("Cancel", dialog_x + 20, button_y, button_width, 35):
            self.show_import_dialog = False

        if self.ui.button(
            "Import", dialog_x + button_width + 40, button_y, button_width, 35, color=(0, 150, 0)
        ):
            self._perform_import()

    def _render_export_dialog(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render export dialog."""
        dialog_width = 500
        dialog_height = 450
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (30, 30, 50))

        self.ui.label(
            "Export Map",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(100, 200, 255),
        )

        if self.ui.button(
            "X", dialog_x + dialog_width - 45, dialog_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.show_export_dialog = False
            return

        if not self.selected_map:
            self.ui.label(
                "No map selected",
                dialog_x + 20,
                dialog_y + 60,
                size=14,
                color=(200, 50, 50),
            )
            return

        form_y = dialog_y + 60

        # Export format selection
        self.ui.label("Export Format:", dialog_x + 20, form_y, size=16, color=(200, 200, 255))
        form_y += 30

        button_width = 140
        png_color = (0, 120, 0) if self.export_format == "png" else (60, 60, 80)
        if self.ui.button("PNG Image", dialog_x + 20, form_y, button_width, 35, color=png_color):
            self.export_format = "png"

        minimap_color = (0, 100, 120) if self.export_format == "minimap" else (60, 60, 80)
        if self.ui.button(
            "Minimap", dialog_x + button_width + 20, form_y, button_width, 35, color=minimap_color
        ):
            self.export_format = "minimap"

        tmx_color = (100, 80, 0) if self.export_format == "tmx" else (60, 60, 80)
        if self.ui.button(
            "Tiled TMX", dialog_x + 2 * button_width + 30, form_y, button_width, 35, color=tmx_color
        ):
            self.export_format = "tmx"

        form_y += 50

        # Format-specific options
        if self.export_format in ["png", "minimap"]:
            if self.export_format == "png":
                self.ui.label("Scale Factor:", dialog_x + 20, form_y, size=14)
                form_y += 25
                self.ui.panel(dialog_x + 20, form_y, 100, 30, (40, 40, 60))
                self.ui.label(
                    self.export_scale,
                    dialog_x + 30,
                    form_y + 8,
                    size=12,
                    color=(200, 200, 200),
                )
            else:
                self.ui.label("Max Size (pixels):", dialog_x + 20, form_y, size=14)
                form_y += 25
                self.ui.panel(dialog_x + 20, form_y, 100, 30, (40, 40, 60))
                self.ui.label(
                    self.minimap_size,
                    dialog_x + 30,
                    form_y + 8,
                    size=12,
                    color=(200, 200, 200),
                )

            form_y += 40

        # Output path
        self.ui.label("Output File:", dialog_x + 20, form_y, size=14)
        form_y += 25
        self.ui.panel(dialog_x + 20, form_y, dialog_width - 40, 30, (40, 40, 60))
        self.ui.label(
            self.export_file_path or "Click Browse...",
            dialog_x + 30,
            form_y + 8,
            size=12,
            color=(150, 150, 150),
        )

        form_y += 40
        if self.ui.button("Browse...", dialog_x + 20, form_y, 120, 30):
            # TODO: File browser dialog
            pass

        form_y += 50

        # Info
        if self.export_format == "png":
            info_text = "Export map as PNG screenshot"
        elif self.export_format == "minimap":
            info_text = "Export scaled-down minimap image"
        else:
            info_text = "Export to Tiled Map Editor format"

        self.ui.label(info_text, dialog_x + 20, form_y, size=12, color=(180, 180, 180))

        # Buttons
        button_y = dialog_y + dialog_height - 50
        button_width = (dialog_width - 60) // 2

        if self.ui.button("Cancel", dialog_x + 20, button_y, button_width, 35):
            self.show_export_dialog = False

        if self.ui.button(
            "Export", dialog_x + button_width + 40, button_y, button_width, 35, color=(0, 150, 0)
        ):
            self._perform_export()

    def _render_tileset_import_dialog(
        self, panel_x: int, panel_y: int, panel_width: int, panel_height: int
    ) -> None:
        """Render tileset import dialog."""
        dialog_width = 450
        dialog_height = 400
        dialog_x = panel_x + (panel_width - dialog_width) // 2
        dialog_y = panel_y + (panel_height - dialog_height) // 2

        self.ui.panel(dialog_x, dialog_y, dialog_width, dialog_height, (30, 30, 50))

        self.ui.label(
            "Import Tileset",
            dialog_x + 20,
            dialog_y + 10,
            size=20,
            color=(100, 200, 255),
        )

        if self.ui.button(
            "X", dialog_x + dialog_width - 45, dialog_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.show_tileset_import_dialog = False
            return

        form_y = dialog_y + 60

        # Tileset name
        self.ui.label("Tileset Name:", dialog_x + 20, form_y, size=14)
        form_y += 25
        self.ui.panel(dialog_x + 20, form_y, dialog_width - 40, 30, (40, 40, 60))

        form_y += 40

        # Image path
        self.ui.label("Tileset Image:", dialog_x + 20, form_y, size=14)
        form_y += 25
        self.ui.panel(dialog_x + 20, form_y, dialog_width - 40, 30, (40, 40, 60))

        form_y += 40
        if self.ui.button("Browse...", dialog_x + 20, form_y, 120, 30):
            # TODO: File browser dialog
            pass

        form_y += 40

        # Tile dimensions
        self.ui.label("Tile Size:", dialog_x + 20, form_y, size=14)
        form_y += 25

        self.ui.label("Width:", dialog_x + 30, form_y, size=12)
        self.ui.panel(dialog_x + 80, form_y, 80, 25, (40, 40, 60))
        self.ui.label("32", dialog_x + 90, form_y + 5, size=12, color=(200, 200, 200))

        self.ui.label("Height:", dialog_x + 180, form_y, size=12)
        self.ui.panel(dialog_x + 235, form_y, 80, 25, (40, 40, 60))
        self.ui.label("32", dialog_x + 245, form_y + 5, size=12, color=(200, 200, 200))

        form_y += 40

        # Auto-detect
        if self.ui.button("Auto-Detect Grid", dialog_x + 20, form_y, 150, 30):
            # TODO: Auto-detect tileset grid
            pass

        form_y += 50

        # Info
        self.ui.label(
            "Import tileset images to use in maps",
            dialog_x + 20,
            form_y,
            size=12,
            color=(180, 180, 180),
        )

        # Buttons
        button_y = dialog_y + dialog_height - 50
        button_width = (dialog_width - 60) // 2

        if self.ui.button("Cancel", dialog_x + 20, button_y, button_width, 35):
            self.show_tileset_import_dialog = False

        if self.ui.button(
            "Import", dialog_x + button_width + 40, button_y, button_width, 35, color=(0, 150, 0)
        ):
            # TODO: Perform tileset import
            self.show_tileset_import_dialog = False

    def _perform_import(self) -> None:
        """Perform map import based on current settings."""
        if not self.import_file_path:
            print("No import file specified")
            return

        try:
            if self.import_format == "tmx":
                # Import TMX
                if self.tmx_importer:
                    map_data = self.tmx_importer.import_tmx(self.import_file_path)
                    if map_data:
                        # Save imported map
                        self.map_manager.save_map(map_data)
                        self.map_manager._build_folder_structure()
                        print(f"Successfully imported TMX map: {map_data.metadata.name}")
                    else:
                        print("Failed to import TMX map")
            self.show_import_dialog = False
            self.import_file_path = ""

        except Exception as e:
            print(f"Error importing map: {e}")

    def _perform_export(self) -> None:
        """Perform map export based on current settings."""
        if not self.selected_map:
            print("No map selected")
            return

        if not self.export_file_path:
            # Auto-generate filename
            if self.export_format == "png":
                self.export_file_path = f"{self.selected_map}.png"
            elif self.export_format == "minimap":
                self.export_file_path = f"{self.selected_map}_minimap.png"
            elif self.export_format == "tmx":
                self.export_file_path = f"{self.selected_map}.tmx"

        try:
            # Load map
            map_data = self.map_manager.load_map(self.selected_map)
            if not map_data:
                print("Failed to load map")
                return

            success = False

            if self.export_format == "png":
                # Export as PNG
                scale = float(self.export_scale) if self.export_scale else 1.0
                success = self.png_exporter.export_map_to_png(
                    map_data, self.export_file_path, scale=scale
                )
            elif self.export_format == "minimap":
                # Export as minimap
                max_size = int(self.minimap_size) if self.minimap_size else 256
                success = self.png_exporter.export_minimap(
                    map_data, self.export_file_path, max_size
                )
            elif self.export_format == "tmx":
                # Export as TMX
                success = self.tmx_exporter.export_to_tmx(map_data, self.export_file_path)

            if success:
                print(f"Successfully exported map to: {self.export_file_path}")
                self.show_export_dialog = False
                self.export_file_path = ""
            else:
                print("Export failed")

        except Exception as e:
            print(f"Error exporting map: {e}")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Args:
            event: Pygame event to handle

        Returns:
            True if event was consumed
        """
        if not self.visible:
            return False

        # Close on Escape
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Close dialogs first
                if any(
                    [
                        self.show_new_map_dialog,
                        self.show_duplicate_dialog,
                        self.show_template_dialog,
                        self.show_delete_confirm,
                        self.show_import_dialog,
                        self.show_export_dialog,
                        self.show_tileset_import_dialog,
                    ]
                ):
                    self.show_new_map_dialog = False
                    self.show_duplicate_dialog = False
                    self.show_template_dialog = False
                    self.show_delete_confirm = False
                    self.show_import_dialog = False
                    self.show_export_dialog = False
                    self.show_tileset_import_dialog = False
                    return True
                else:
                    self.toggle()
                    return True

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            # TODO: Detect which panel is hovered and scroll accordingly
            if self.current_mode == "browser":
                self.map_list_scroll = max(0, self.map_list_scroll - event.y * 20)
            return True

        return False

    def update(self, dt: float) -> None:
        """
        Update the map manager UI.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

        # Update logic here if needed
        pass
