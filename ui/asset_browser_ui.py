"""
NeonWorks Asset Browser UI - Visual Asset Management
Provides complete visual interface for browsing and managing game assets.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from ..rendering.assets import AssetManager
from ..rendering.ui import UI


class AssetBrowserUI:
    """
    Visual asset browser for managing sprites, sounds, music, and other assets.
    """

    def __init__(
        self, screen: pygame.Surface, asset_manager: Optional[AssetManager] = None
    ):
        self.screen = screen
        self.ui = UI(screen)
        self.asset_manager = asset_manager

        self.visible = False

        # Asset categories
        self.current_category = (
            "sprites"  # 'sprites', 'sounds', 'music', 'fonts', 'data'
        )

        # Asset data
        self.assets: Dict[str, List[Dict]] = {
            "sprites": [],
            "sounds": [],
            "music": [],
            "fonts": [],
            "data": [],
        }

        # UI state
        self.selected_asset = None
        self.scroll_offset = 0
        self.grid_view = True  # Grid vs list view
        self.search_query = ""

        # Preview
        self.preview_surface = None

        # Paths
        self.assets_dir = Path("assets")

    def toggle(self):
        """Toggle asset browser visibility."""
        self.visible = not self.visible
        if self.visible:
            self.refresh_assets()

    def refresh_assets(self):
        """Refresh asset lists from filesystem."""
        self._scan_assets()

    def render(self):
        """Render the asset browser UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Main panel
        panel_width = 1100
        panel_height = 750
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2

        self.ui.panel(panel_x, panel_y, panel_width, panel_height, (20, 20, 30))

        # Title
        self.ui.title(
            "Asset Browser",
            panel_x + panel_width // 2 - 80,
            panel_y + 10,
            size=24,
            color=(100, 200, 255),
        )

        # Close button
        if self.ui.button(
            "X", panel_x + panel_width - 50, panel_y + 10, 35, 35, color=(150, 0, 0)
        ):
            self.toggle()

        # Category tabs
        self._render_category_tabs(panel_x, panel_y + 60, panel_width)

        # Toolbar
        self._render_toolbar(panel_x, panel_y + 110, panel_width)

        # Content area (split into browser and preview)
        browser_width = panel_width - 350
        content_y = panel_y + 160

        # Asset browser
        self._render_asset_browser(
            panel_x + 10, content_y, browser_width, panel_height - 170
        )

        # Asset preview and details
        self._render_asset_preview(
            panel_x + browser_width + 20, content_y, 330, panel_height - 170
        )

    def _render_category_tabs(self, x: int, y: int, width: int):
        """Render category selection tabs."""
        categories = ["sprites", "sounds", "music", "fonts", "data"]
        tab_width = width // len(categories)

        for i, category in enumerate(categories):
            tab_x = x + i * tab_width
            is_active = category == self.current_category
            tab_color = (50, 100, 200) if is_active else (25, 25, 40)

            if self.ui.button(
                category.capitalize(), tab_x + 5, y, tab_width - 10, 40, color=tab_color
            ):
                self.current_category = category
                self.selected_asset = None

    def _render_toolbar(self, x: int, y: int, width: int):
        """Render toolbar with search and view options."""
        # Search bar
        search_width = 300
        self.ui.panel(x + 10, y, search_width, 35, (50, 50, 70))
        search_text = self.search_query if self.search_query else "Search assets..."
        search_color = (255, 255, 255) if self.search_query else (120, 120, 120)
        self.ui.label(search_text, x + 15, y + 8, size=14, color=search_color)

        # View toggle
        view_x = x + search_width + 30
        grid_color = (0, 150, 0) if self.grid_view else (50, 50, 70)
        if self.ui.button("Grid View", view_x, y, 100, 35, color=grid_color):
            self.grid_view = True

        list_color = (0, 150, 0) if not self.grid_view else (50, 50, 70)
        if self.ui.button("List View", view_x + 110, y, 100, 35, color=list_color):
            self.grid_view = False

        # Refresh button
        if self.ui.button("Refresh", x + width - 120, y, 100, 35, color=(0, 100, 150)):
            self.refresh_assets()

    def _render_asset_browser(self, x: int, y: int, width: int, height: int):
        """Render the asset browser area."""
        self.ui.panel(x, y, width, height, (30, 30, 45))

        assets = self.assets.get(self.current_category, [])

        if not assets:
            self.ui.label(
                f"No {self.current_category} found",
                x + width // 2 - 80,
                y + height // 2,
                size=16,
                color=(150, 150, 150),
            )
            return

        # Filter by search
        if self.search_query:
            assets = [
                a for a in assets if self.search_query.lower() in a["name"].lower()
            ]

        if self.grid_view:
            self._render_grid_view(assets, x, y, width, height)
        else:
            self._render_list_view(assets, x, y, width, height)

    def _render_grid_view(
        self, assets: List[Dict], x: int, y: int, width: int, height: int
    ):
        """Render assets in grid view."""
        item_size = 120
        padding = 10
        columns = (width - 20) // (item_size + padding)

        current_x = x + 10
        current_y = y + 10
        col = 0

        for asset in assets:
            if current_y + item_size > y + height - 10:
                break

            is_selected = self.selected_asset == asset

            # Asset tile
            tile_color = (80, 80, 120) if is_selected else (50, 50, 70)
            self.ui.panel(current_x, current_y, item_size, item_size, tile_color)

            # Asset preview/icon (placeholder)
            icon_color = asset.get("color", (100, 150, 200))
            pygame.draw.rect(
                self.screen,
                icon_color,
                (current_x + 10, current_y + 10, item_size - 20, item_size - 40),
            )

            # Asset name (truncated)
            asset_name = asset["name"]
            if len(asset_name) > 12:
                asset_name = asset_name[:12] + "..."

            self.ui.label(
                asset_name, current_x + 10, current_y + item_size - 25, size=12
            )

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                current_x <= mouse_pos[0] <= current_x + item_size
                and current_y <= mouse_pos[1] <= current_y + item_size
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.selected_asset = asset
                    self._load_asset_preview(asset)

            col += 1
            if col >= columns:
                col = 0
                current_x = x + 10
                current_y += item_size + padding
            else:
                current_x += item_size + padding

    def _render_list_view(
        self, assets: List[Dict], x: int, y: int, width: int, height: int
    ):
        """Render assets in list view."""
        item_height = 50
        current_y = y + 10

        for asset in assets:
            if current_y + item_height > y + height - 10:
                break

            is_selected = self.selected_asset == asset

            # Asset item
            item_color = (60, 60, 100) if is_selected else (40, 40, 60)
            self.ui.panel(x + 10, current_y, width - 20, item_height, item_color)

            # Icon (small)
            icon_color = asset.get("color", (100, 150, 200))
            pygame.draw.rect(self.screen, icon_color, (x + 15, current_y + 10, 30, 30))

            # Asset name
            self.ui.label(asset["name"], x + 55, current_y + 10, size=16)

            # Asset info
            asset_type = asset.get("type", "unknown")
            asset_size = asset.get("size", 0)
            size_text = self._format_file_size(asset_size)
            self.ui.label(
                f"{asset_type} - {size_text}",
                x + 55,
                current_y + 28,
                size=12,
                color=(180, 180, 180),
            )

            # Click to select
            mouse_pos = pygame.mouse.get_pos()
            if (
                x + 10 <= mouse_pos[0] <= x + width - 10
                and current_y <= mouse_pos[1] <= current_y + item_height
            ):
                if pygame.mouse.get_pressed()[0]:
                    self.selected_asset = asset
                    self._load_asset_preview(asset)

            current_y += item_height + 5

    def _render_asset_preview(self, x: int, y: int, width: int, height: int):
        """Render asset preview and details panel."""
        self.ui.panel(x, y, width, height, (30, 30, 45))

        if not self.selected_asset:
            self.ui.label(
                "No asset selected",
                x + width // 2 - 70,
                y + height // 2,
                size=14,
                color=(150, 150, 150),
            )
            return

        current_y = y + 10

        # Asset name
        asset_name = self.selected_asset["name"]
        self.ui.label(asset_name, x + 10, current_y, size=18, color=(255, 255, 100))
        current_y += 30

        # Preview area
        preview_height = 200
        self.ui.panel(x + 10, current_y, width - 20, preview_height, (50, 50, 70))

        # Show preview if available
        if self.preview_surface:
            # Center the preview
            preview_rect = self.preview_surface.get_rect()
            preview_rect.center = (x + width // 2, current_y + preview_height // 2)
            self.screen.blit(self.preview_surface, preview_rect)
        else:
            # Placeholder
            icon_color = self.selected_asset.get("color", (100, 150, 200))
            pygame.draw.rect(
                self.screen,
                icon_color,
                (x + width // 2 - 50, current_y + preview_height // 2 - 50, 100, 100),
            )

        current_y += preview_height + 15

        # Asset details
        self.ui.label("Details:", x + 10, current_y, size=16, color=(200, 200, 255))
        current_y += 25

        # Type
        asset_type = self.selected_asset.get("type", "unknown")
        self.ui.label(f"Type: {asset_type}", x + 15, current_y, size=14)
        current_y += 22

        # Path
        asset_path = self.selected_asset.get("path", "Unknown")
        path_display = str(asset_path)
        if len(path_display) > 30:
            path_display = "..." + path_display[-30:]
        self.ui.label(
            f"Path: {path_display}", x + 15, current_y, size=12, color=(180, 180, 180)
        )
        current_y += 22

        # Size
        asset_size = self.selected_asset.get("size", 0)
        size_text = self._format_file_size(asset_size)
        self.ui.label(f"Size: {size_text}", x + 15, current_y, size=14)
        current_y += 22

        # Dimensions (for images)
        if self.current_category == "sprites" and "dimensions" in self.selected_asset:
            dims = self.selected_asset["dimensions"]
            self.ui.label(
                f"Dimensions: {dims[0]}x{dims[1]}", x + 15, current_y, size=14
            )
            current_y += 22

        # Actions
        current_y += 20

        if self.ui.button(
            "Use Asset", x + 10, current_y, width - 20, 35, color=(0, 150, 0)
        ):
            self._use_asset(self.selected_asset)

        current_y += 45

        if self.ui.button(
            "Delete Asset", x + 10, current_y, width - 20, 35, color=(150, 0, 0)
        ):
            self._delete_asset(self.selected_asset)

    def _scan_assets(self):
        """Scan filesystem for assets."""
        # Clear current assets
        for category in self.assets:
            self.assets[category] = []

        if not self.assets_dir.exists():
            self.assets_dir.mkdir(parents=True)
            return

        # Scan sprites
        sprites_dir = self.assets_dir / "sprites"
        if sprites_dir.exists():
            for file_path in sprites_dir.glob("*.png"):
                self.assets["sprites"].append(
                    {
                        "name": file_path.stem,
                        "path": str(file_path),
                        "type": "PNG Image",
                        "size": file_path.stat().st_size,
                        "color": (100, 150, 200),
                    }
                )

        # Scan sounds
        sounds_dir = self.assets_dir / "sounds"
        if sounds_dir.exists():
            for file_path in sounds_dir.glob("*.wav"):
                self.assets["sounds"].append(
                    {
                        "name": file_path.stem,
                        "path": str(file_path),
                        "type": "WAV Audio",
                        "size": file_path.stat().st_size,
                        "color": (200, 100, 100),
                    }
                )

        # Scan music
        music_dir = self.assets_dir / "music"
        if music_dir.exists():
            for file_path in music_dir.glob("*.ogg"):
                self.assets["music"].append(
                    {
                        "name": file_path.stem,
                        "path": str(file_path),
                        "type": "OGG Music",
                        "size": file_path.stat().st_size,
                        "color": (150, 100, 200),
                    }
                )

        # Scan fonts
        fonts_dir = self.assets_dir / "fonts"
        if fonts_dir.exists():
            for file_path in fonts_dir.glob("*.ttf"):
                self.assets["fonts"].append(
                    {
                        "name": file_path.stem,
                        "path": str(file_path),
                        "type": "TrueType Font",
                        "size": file_path.stat().st_size,
                        "color": (100, 200, 100),
                    }
                )

        # Scan data files
        data_dir = self.assets_dir / "data"
        if data_dir.exists():
            for file_path in data_dir.glob("*.json"):
                self.assets["data"].append(
                    {
                        "name": file_path.stem,
                        "path": str(file_path),
                        "type": "JSON Data",
                        "size": file_path.stat().st_size,
                        "color": (200, 200, 100),
                    }
                )

    def _load_asset_preview(self, asset: Dict):
        """Load a preview for the selected asset."""
        self.preview_surface = None

        if self.current_category == "sprites":
            try:
                # Load image and scale it down for preview
                image = pygame.image.load(asset["path"])
                # Scale to fit preview area (max 180x180)
                max_size = 180
                image_rect = image.get_rect()

                if image_rect.width > max_size or image_rect.height > max_size:
                    scale_factor = min(
                        max_size / image_rect.width, max_size / image_rect.height
                    )
                    new_size = (
                        int(image_rect.width * scale_factor),
                        int(image_rect.height * scale_factor),
                    )
                    image = pygame.transform.scale(image, new_size)

                self.preview_surface = image
                asset["dimensions"] = image.get_rect().size
            except Exception as e:
                print(f"Failed to load preview: {e}")

    def _format_file_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def _use_asset(self, asset: Dict):
        """Use/load the selected asset."""
        print(f"Using asset: {asset['name']}")
        # In a real implementation, this would load the asset into the game/editor

    def _delete_asset(self, asset: Dict):
        """Delete the selected asset."""
        print(f"Deleting asset: {asset['name']}")
        # In a real implementation, this would show a confirmation dialog
        self.selected_asset = None
        self.refresh_assets()

    def handle_text_input(self, text: str):
        """Handle text input for search."""
        if self.visible:
            self.search_query += text

    def handle_key_press(self, key: int):
        """Handle key press for search."""
        if not self.visible:
            return

        if key == pygame.K_BACKSPACE:
            self.search_query = self.search_query[:-1]
