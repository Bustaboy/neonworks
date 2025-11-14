"""
Asset Loading System

Load and cache sprites, textures, and other game assets.
Supports the NeonWorks asset library with manifest-based loading.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame


@dataclass
class SpriteSheet:
    """Sprite sheet data"""

    surface: pygame.Surface
    tile_width: int
    tile_height: int

    def get_sprite(self, x: int, y: int) -> pygame.Surface:
        """Get a sprite from the sheet at grid position (x, y)"""
        rect = pygame.Rect(
            x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height
        )
        sprite = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
        sprite.blit(self.surface, (0, 0), rect)
        return sprite

    def get_sprite_by_index(self, index: int, columns: int) -> pygame.Surface:
        """Get a sprite by its index in the sheet"""
        x = index % columns
        y = index // columns
        return self.get_sprite(x, y)


@dataclass
class AssetMetadata:
    """
    Metadata for a single asset from the manifest.

    This represents an entry from asset_manifest.json with all
    the metadata needed to load and manage the asset.
    """

    id: str
    name: str
    file_path: str
    format: str
    category: str
    tags: List[str] = field(default_factory=list)
    license: Optional[str] = None
    author: Optional[str] = None
    attribution_required: bool = False
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], category: str) -> "AssetMetadata":
        """Create AssetMetadata from a manifest dictionary entry."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            file_path=data.get("file_path", ""),
            format=data.get("format", ""),
            category=category,
            tags=data.get("tags", []),
            license=data.get("license"),
            author=data.get("author"),
            attribution_required=data.get("attribution_required", False),
            notes=data.get("notes"),
            metadata=data,  # Store full metadata for category-specific fields
        )


@dataclass
class LoadedAsset:
    """
    A loaded asset with its data and metadata.

    Combines the actual loaded resource (sprite, sound, etc.)
    with its metadata from the manifest.
    """

    metadata: AssetMetadata
    resource: Any  # pygame.Surface, pygame.mixer.Sound, etc.
    thumbnail: Optional[pygame.Surface] = None


class AssetManager:
    """
    Manages loading and caching of game assets.

    Features:
    - Sprite/texture loading with caching
    - Sprite sheet support
    - Asset manifest loading and management
    - Category-specific asset helpers
    - Lazy loading for performance
    - Thumbnail generation for asset browser
    - Asset search and filtering
    - Memory management
    """

    def __init__(self, base_path: Optional[Path] = None, manifest_path: Optional[Path] = None):
        """
        Initialize asset manager.

        Args:
            base_path: Base path for asset loading. Defaults to 'assets/'
            manifest_path: Path to asset_manifest.json. Defaults to 'assets/asset_manifest.json'
        """
        self.base_path = Path(base_path) if base_path else Path("assets")
        self.manifest_path = (
            Path(manifest_path) if manifest_path else self.base_path / "asset_manifest.json"
        )

        # Asset caches (legacy)
        self._sprites: Dict[str, pygame.Surface] = {}
        self._sprite_sheets: Dict[str, SpriteSheet] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}

        # Asset info (legacy)
        self._asset_sizes: Dict[str, int] = {}  # Track memory usage

        # Asset library (new manifest-based system)
        self._manifest: Dict[str, Any] = {}
        self._asset_metadata: Dict[str, AssetMetadata] = {}  # id -> metadata
        self._loaded_assets: Dict[str, LoadedAsset] = {}  # id -> loaded asset
        self._thumbnails: Dict[str, pygame.Surface] = {}  # id -> thumbnail

        # Lazy loading tracking
        self._lazy_load_enabled = True

        # Placeholder surfaces for missing assets
        self._create_placeholders()

        # Load manifest if it exists
        self._load_manifest()

    def _create_placeholders(self):
        """Create placeholder graphics for missing assets"""
        # Missing texture placeholder (subtle gray checkerboard with border)
        self._missing_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._missing_texture.fill((80, 80, 90, 255))

        # Add checkerboard pattern
        for y in range(32):
            for x in range(32):
                if (x // 8 + y // 8) % 2 == 0:
                    color = (100, 100, 110, 255)
                else:
                    color = (60, 60, 70, 255)
                self._missing_texture.set_at((x, y), color)

        # Add border
        pygame.draw.rect(self._missing_texture, (255, 100, 100, 255), (0, 0, 32, 32), 1)

        # Add "?" icon in center
        font_size = 20
        try:
            font = pygame.font.Font(None, font_size)
            text = font.render("?", True, (255, 100, 100, 255))
            text_rect = text.get_rect(center=(16, 16))
            self._missing_texture.blit(text, text_rect)
        except Exception:
            pass  # If font fails, just use the checkerboard

    def _load_manifest(self):
        """Load the asset manifest from disk."""
        if not self.manifest_path.exists():
            print(f"ℹ Asset manifest not found: {self.manifest_path}")
            print("  Asset library features will be limited.")
            return

        try:
            with open(self.manifest_path, "r") as f:
                self._manifest = json.load(f)

            # Parse asset metadata from manifest
            assets = self._manifest.get("assets", {})
            for category, asset_list in assets.items():
                for asset_data in asset_list:
                    metadata = AssetMetadata.from_dict(asset_data, category)
                    self._asset_metadata[metadata.id] = metadata

            asset_count = len(self._asset_metadata)
            print(f"✓ Loaded asset manifest: {asset_count} assets registered")

        except (json.JSONDecodeError, IOError) as e:
            print(f"✗ Failed to load asset manifest: {e}")
            print("  Asset library features will be limited.")

    def reload_manifest(self):
        """Reload the asset manifest from disk."""
        self._manifest = {}
        self._asset_metadata.clear()
        self._load_manifest()

    # ========== Sprite Loading ==========

    def load_sprite(
        self,
        path: str,
        color_key: Optional[Tuple[int, int, int]] = None,
        alpha: bool = True,
    ) -> pygame.Surface:
        """
        Load a sprite from file.

        Args:
            path: Path to sprite file relative to base_path
            color_key: Color to treat as transparent (e.g., (255, 0, 255) for magenta)
            alpha: Whether to convert with alpha channel

        Returns:
            Loaded sprite surface
        """
        # Check cache
        cache_key = f"{path}_{color_key}_{alpha}"
        if cache_key in self._sprites:
            return self._sprites[cache_key]

        full_path = self.base_path / path

        try:
            # Load the image
            if alpha:
                sprite = pygame.image.load(str(full_path)).convert_alpha()
            else:
                sprite = pygame.image.load(str(full_path)).convert()

            # Apply color key if specified
            if color_key:
                sprite.set_colorkey(color_key)

            # Cache the sprite
            self._sprites[cache_key] = sprite
            self._asset_sizes[cache_key] = (
                sprite.get_width() * sprite.get_height() * 4
            )  # Rough size estimate

            print(f"✓ Loaded sprite: {path}")
            return sprite

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to load sprite '{path}': {e}")
            print(f"  Using placeholder texture")
            # Cache the placeholder to avoid repeated load attempts
            placeholder = self._missing_texture.copy()
            self._sprites[cache_key] = placeholder
            self._asset_sizes[cache_key] = 32 * 32 * 4
            return placeholder

    def load_sprite_sheet(
        self,
        path: str,
        tile_width: int,
        tile_height: int,
        color_key: Optional[Tuple[int, int, int]] = None,
    ) -> SpriteSheet:
        """
        Load a sprite sheet.

        Args:
            path: Path to sprite sheet file
            tile_width: Width of each tile in pixels
            tile_height: Height of each tile in pixels
            color_key: Color to treat as transparent

        Returns:
            SpriteSheet object
        """
        # Check cache
        cache_key = f"{path}_{tile_width}_{tile_height}_{color_key}"
        if cache_key in self._sprite_sheets:
            return self._sprite_sheets[cache_key]

        full_path = self.base_path / path

        try:
            # Load the sheet
            surface = pygame.image.load(str(full_path)).convert_alpha()

            # Apply color key if specified
            if color_key:
                surface.set_colorkey(color_key)

            # Create sprite sheet
            sheet = SpriteSheet(surface, tile_width, tile_height)

            # Cache it
            self._sprite_sheets[cache_key] = sheet
            self._asset_sizes[cache_key] = surface.get_width() * surface.get_height() * 4

            print(f"✓ Loaded sprite sheet: {path} ({tile_width}x{tile_height})")
            return sheet

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to load sprite sheet '{path}': {e}")
            # Return a placeholder sheet
            placeholder_surface = pygame.Surface((tile_width, tile_height))
            placeholder_surface.fill((255, 0, 255))
            return SpriteSheet(placeholder_surface, tile_width, tile_height)

    def scale_sprite(self, sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """
        Scale a sprite by a factor.

        Args:
            sprite: Sprite to scale
            scale: Scale factor (1.0 = no change, 2.0 = double size)

        Returns:
            Scaled sprite
        """
        new_width = int(sprite.get_width() * scale)
        new_height = int(sprite.get_height() * scale)
        return pygame.transform.scale(sprite, (new_width, new_height))

    def rotate_sprite(self, sprite: pygame.Surface, angle: float) -> pygame.Surface:
        """
        Rotate a sprite.

        Args:
            sprite: Sprite to rotate
            angle: Angle in degrees (positive = counter-clockwise)

        Returns:
            Rotated sprite
        """
        return pygame.transform.rotate(sprite, angle)

    def flip_sprite(
        self, sprite: pygame.Surface, flip_x: bool = False, flip_y: bool = False
    ) -> pygame.Surface:
        """
        Flip a sprite horizontally and/or vertically.

        Args:
            sprite: Sprite to flip
            flip_x: Flip horizontally
            flip_y: Flip vertically

        Returns:
            Flipped sprite
        """
        return pygame.transform.flip(sprite, flip_x, flip_y)

    # ========== Batch Loading ==========

    def preload_sprites(self, paths: list):
        """
        Preload a list of sprites.

        Useful for loading screens to load all assets upfront.
        """
        total = len(paths)
        for i, path in enumerate(paths):
            self.load_sprite(path)
            if (i + 1) % 10 == 0 or i == total - 1:
                print(f"Preloading assets: {i+1}/{total}")

    # ========== Cache Management ==========

    def clear_cache(self):
        """Clear all cached assets"""
        self._sprites.clear()
        self._sprite_sheets.clear()
        self._sounds.clear()
        self._asset_sizes.clear()
        print("Asset cache cleared")

    def get_memory_usage(self) -> int:
        """Get approximate memory usage of cached assets in bytes"""
        return sum(self._asset_sizes.values())

    def get_cache_info(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "sprites": len(self._sprites),
            "sprite_sheets": len(self._sprite_sheets),
            "sounds": len(self._sounds),
            "memory_bytes": self.get_memory_usage(),
            "memory_mb": self.get_memory_usage() / (1024 * 1024),
        }

    # ========== Utility ==========

    def has_sprite(self, path: str) -> bool:
        """Check if a sprite is in the cache"""
        return any(path in key for key in self._sprites.keys())

    def remove_sprite(self, path: str):
        """Remove a sprite from the cache"""
        to_remove = [key for key in self._sprites.keys() if path in key]
        for key in to_remove:
            del self._sprites[key]
            if key in self._asset_sizes:
                del self._asset_sizes[key]

    # ========== Asset Library (Manifest-Based) ==========

    def get_asset_metadata(self, asset_id: str) -> Optional[AssetMetadata]:
        """
        Get metadata for an asset by ID.

        Args:
            asset_id: Asset ID from manifest

        Returns:
            AssetMetadata if found, None otherwise
        """
        return self._asset_metadata.get(asset_id)

    def load_asset(self, asset_id: str) -> Optional[LoadedAsset]:
        """
        Load an asset by ID from the manifest.

        Supports lazy loading - asset is only loaded from disk when first requested.

        Args:
            asset_id: Asset ID from manifest

        Returns:
            LoadedAsset if successful, None if asset not found or load failed
        """
        # Check if already loaded
        if asset_id in self._loaded_assets:
            return self._loaded_assets[asset_id]

        # Get metadata
        metadata = self._asset_metadata.get(asset_id)
        if not metadata:
            print(f"✗ Asset '{asset_id}' not found in manifest")
            return None

        # Load the asset based on category
        resource = self._load_asset_by_category(metadata)
        if resource is None:
            return None

        # Create loaded asset
        loaded_asset = LoadedAsset(metadata=metadata, resource=resource)

        # Cache it
        self._loaded_assets[asset_id] = loaded_asset

        return loaded_asset

    def _load_asset_by_category(self, metadata: AssetMetadata) -> Optional[Any]:
        """Load an asset based on its category."""
        full_path = self.base_path / metadata.file_path

        try:
            if metadata.category in ["characters", "enemies", "icons", "ui", "faces"]:
                # Image asset
                return pygame.image.load(str(full_path)).convert_alpha()

            elif metadata.category == "tilesets":
                # Tileset (sprite sheet)
                tile_width = metadata.metadata.get("tile_width", 32)
                tile_height = metadata.metadata.get("tile_height", 32)
                return self.load_sprite_sheet(metadata.file_path, tile_width, tile_height)

            elif metadata.category == "animations":
                # Animation (sprite sheet or gif)
                return pygame.image.load(str(full_path)).convert_alpha()

            elif metadata.category == "backgrounds":
                # Background (may be larger, allow jpg)
                return pygame.image.load(str(full_path)).convert()

            elif metadata.category in ["music", "sfx"]:
                # Audio asset
                try:
                    if metadata.category == "music":
                        # Music loaded via pygame.mixer.music (not returned as object)
                        return str(full_path)  # Return path for music
                    else:
                        # SFX loaded as Sound
                        return pygame.mixer.Sound(str(full_path))
                except pygame.error as e:
                    print(f"✗ Failed to load audio '{metadata.id}': {e}")
                    return None

            else:
                print(f"✗ Unknown asset category: {metadata.category}")
                return None

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to load asset '{metadata.id}': {e}")
            return None

    def get_thumbnail(
        self, asset_id: str, size: Tuple[int, int] = (64, 64)
    ) -> Optional[pygame.Surface]:
        """
        Get or generate a thumbnail for an asset.

        Args:
            asset_id: Asset ID from manifest
            size: Thumbnail size (width, height)

        Returns:
            Thumbnail surface if successful, None otherwise
        """
        # Check cache
        cache_key = f"{asset_id}_{size[0]}x{size[1]}"
        if cache_key in self._thumbnails:
            return self._thumbnails[cache_key]

        # Load asset if needed
        loaded_asset = self.load_asset(asset_id)
        if not loaded_asset:
            return None

        # Generate thumbnail based on category
        thumbnail = None
        metadata = loaded_asset.metadata

        if metadata.category in [
            "characters",
            "enemies",
            "icons",
            "ui",
            "faces",
            "backgrounds",
            "animations",
        ]:
            # Image asset - scale to thumbnail size
            if isinstance(loaded_asset.resource, pygame.Surface):
                thumbnail = pygame.transform.smoothscale(loaded_asset.resource, size)
            elif isinstance(loaded_asset.resource, SpriteSheet):
                # For sprite sheets, use first tile
                first_sprite = loaded_asset.resource.get_sprite(0, 0)
                thumbnail = pygame.transform.smoothscale(first_sprite, size)

        elif metadata.category == "tilesets":
            # Tileset - show first few tiles
            if isinstance(loaded_asset.resource, SpriteSheet):
                first_sprite = loaded_asset.resource.get_sprite(0, 0)
                thumbnail = pygame.transform.smoothscale(first_sprite, size)

        elif metadata.category in ["music", "sfx"]:
            # Audio - create visual representation
            thumbnail = pygame.Surface(size, pygame.SRCALPHA)
            thumbnail.fill((40, 40, 50, 255))

            # Add waveform icon
            color = (100, 200, 255, 255) if metadata.category == "music" else (255, 200, 100, 255)
            center_y = size[1] // 2
            for x in range(0, size[0], 4):
                height = (x % 20) + 5
                pygame.draw.line(
                    thumbnail, color, (x, center_y - height), (x, center_y + height), 2
                )

            # Add icon label
            try:
                font = pygame.font.Font(None, 16)
                label = "♫" if metadata.category == "music" else "♪"
                text = font.render(label, True, color)
                text_rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
                thumbnail.blit(text, text_rect)
            except Exception:
                pass

        if thumbnail:
            self._thumbnails[cache_key] = thumbnail
            loaded_asset.thumbnail = thumbnail

        return thumbnail

    # ========== Category-Specific Helpers ==========

    def get_character(self, character_id: str) -> Optional[pygame.Surface]:
        """Load a character sprite by ID."""
        loaded = self.load_asset(character_id)
        return loaded.resource if loaded else None

    def get_enemy(self, enemy_id: str) -> Optional[pygame.Surface]:
        """Load an enemy sprite by ID."""
        loaded = self.load_asset(enemy_id)
        return loaded.resource if loaded else None

    def get_animation(self, animation_id: str) -> Optional[pygame.Surface]:
        """Load an animation by ID."""
        loaded = self.load_asset(animation_id)
        return loaded.resource if loaded else None

    def get_music(self, music_id: str) -> Optional[str]:
        """
        Get music file path by ID.

        Note: Music is loaded via pygame.mixer.music, so this returns
        the file path rather than a Sound object.

        Returns:
            File path string if found, None otherwise
        """
        loaded = self.load_asset(music_id)
        return loaded.resource if loaded else None

    def get_sfx(self, sfx_id: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound effect by ID."""
        loaded = self.load_asset(sfx_id)
        return loaded.resource if loaded else None

    def get_tileset(self, tileset_id: str) -> Optional[SpriteSheet]:
        """Load a tileset by ID."""
        loaded = self.load_asset(tileset_id)
        return loaded.resource if loaded else None

    def get_icon(self, icon_id: str) -> Optional[pygame.Surface]:
        """Load an icon by ID."""
        loaded = self.load_asset(icon_id)
        return loaded.resource if loaded else None

    def get_ui_element(self, ui_id: str) -> Optional[pygame.Surface]:
        """Load a UI element by ID."""
        loaded = self.load_asset(ui_id)
        return loaded.resource if loaded else None

    def get_face(self, face_id: str) -> Optional[pygame.Surface]:
        """Load a character face/portrait by ID."""
        loaded = self.load_asset(face_id)
        return loaded.resource if loaded else None

    def get_background(self, background_id: str) -> Optional[pygame.Surface]:
        """Load a background by ID."""
        loaded = self.load_asset(background_id)
        return loaded.resource if loaded else None

    # ========== Asset Search and Filtering ==========

    def find_assets_by_tag(self, tag: str) -> List[AssetMetadata]:
        """
        Find all assets with a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of matching asset metadata
        """
        results = []
        for metadata in self._asset_metadata.values():
            if tag.lower() in [t.lower() for t in metadata.tags]:
                results.append(metadata)
        return results

    def find_assets_by_category(self, category: str) -> List[AssetMetadata]:
        """
        Find all assets in a specific category.

        Args:
            category: Category name (characters, enemies, music, etc.)

        Returns:
            List of matching asset metadata
        """
        results = []
        for metadata in self._asset_metadata.values():
            if metadata.category == category:
                results.append(metadata)
        return results

    def search_assets(self, query: str) -> List[AssetMetadata]:
        """
        Search assets by name, ID, or tags.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching asset metadata
        """
        query_lower = query.lower()
        results = []

        for metadata in self._asset_metadata.values():
            # Check ID
            if query_lower in metadata.id.lower():
                results.append(metadata)
                continue

            # Check name
            if query_lower in metadata.name.lower():
                results.append(metadata)
                continue

            # Check tags
            if any(query_lower in tag.lower() for tag in metadata.tags):
                results.append(metadata)
                continue

        return results

    def filter_assets(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        theme: Optional[str] = None,
        mood: Optional[str] = None,
        commercial_use_only: bool = False,
    ) -> List[AssetMetadata]:
        """
        Filter assets by multiple criteria.

        Args:
            category: Filter by category (optional)
            tags: Filter by tags (all must match, optional)
            author: Filter by author (optional)
            genre: Filter by genre (fantasy, scifi, etc., optional)
            theme: Filter by theme (medieval, modern, etc., optional)
            mood: Filter by mood (peaceful, intense, etc., optional) - for music
            commercial_use_only: If True, only return assets with commercial-use licenses

        Returns:
            List of matching asset metadata
        """
        results = list(self._asset_metadata.values())

        # Filter by category
        if category:
            results = [m for m in results if m.category == category]

        # Filter by tags (all must match)
        if tags:
            for tag in tags:
                tag_lower = tag.lower()
                results = [m for m in results if any(tag_lower in t.lower() for t in m.tags)]

        # Filter by author
        if author:
            author_lower = author.lower()
            results = [m for m in results if m.author and author_lower in m.author.lower()]

        # Filter by genre (check both metadata field and tags)
        if genre:
            genre_lower = genre.lower()
            results = [
                m
                for m in results
                if (m.metadata.get("genre", "").lower() == genre_lower)
                or any(genre_lower in tag.lower() for tag in m.tags)
            ]

        # Filter by theme (check both metadata field and tags)
        if theme:
            theme_lower = theme.lower()
            results = [
                m
                for m in results
                if (m.metadata.get("theme", "").lower() == theme_lower)
                or any(theme_lower in tag.lower() for tag in m.tags)
            ]

        # Filter by mood (primarily for music, check both metadata field and tags)
        if mood:
            mood_lower = mood.lower()
            results = [
                m
                for m in results
                if (m.metadata.get("mood", "").lower() == mood_lower)
                or any(mood_lower in tag.lower() for tag in m.tags)
            ]

        # Filter by commercial use
        if commercial_use_only:
            results = [m for m in results if self._is_commercial_use_allowed(m)]

        return results

    def _is_commercial_use_allowed(self, metadata: AssetMetadata) -> bool:
        """
        Check if an asset's license allows commercial use.

        Args:
            metadata: Asset metadata to check

        Returns:
            True if commercial use is allowed, False otherwise
        """
        if not metadata.license:
            # No license specified - assume not allowed to be safe
            return False

        license_lower = metadata.license.lower()

        # Allowed licenses
        commercial_licenses = [
            "cc0",
            "cc-by",
            "cc-by 3.0",
            "cc-by 4.0",
            "cc-by-sa",
            "cc-by-sa 3.0",
            "cc-by-sa 4.0",
            "oga-by",
            "oga-by 3.0",
            "mit",
            "public domain",
            "ofl",  # Open Font License
        ]

        # Check if license is in allowed list
        for allowed in commercial_licenses:
            if allowed in license_lower:
                # Make sure it's not NC (non-commercial)
                if "nc" in license_lower or "non-commercial" in license_lower:
                    return False
                return True

        return False

    def get_all_categories(self) -> List[str]:
        """Get list of all asset categories in the manifest."""
        categories = set()
        for metadata in self._asset_metadata.values():
            categories.add(metadata.category)
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """Get list of all unique tags across all assets."""
        tags = set()
        for metadata in self._asset_metadata.values():
            tags.update(metadata.tags)
        return sorted(list(tags))

    def get_all_genres(self) -> List[str]:
        """Get list of all unique genres across all assets."""
        genres = set()
        for metadata in self._asset_metadata.values():
            # Check genre field in metadata
            if "genre" in metadata.metadata:
                genres.add(metadata.metadata["genre"])
            # Also check tags for genre keywords
            genre_keywords = [
                "fantasy",
                "scifi",
                "medieval",
                "modern",
                "cyberpunk",
                "horror",
                "western",
            ]
            for tag in metadata.tags:
                if tag.lower() in genre_keywords:
                    genres.add(tag)
        return sorted(list(genres))

    def get_all_themes(self) -> List[str]:
        """Get list of all unique themes across all assets."""
        themes = set()
        for metadata in self._asset_metadata.values():
            # Check theme field in metadata
            if "theme" in metadata.metadata:
                themes.add(metadata.metadata["theme"])
        return sorted(list(themes))

    def get_all_moods(self) -> List[str]:
        """Get list of all unique moods across all assets (primarily for music)."""
        moods = set()
        for metadata in self._asset_metadata.values():
            # Check mood field in metadata
            if "mood" in metadata.metadata:
                moods.add(metadata.metadata["mood"])
            # Also check tags for mood keywords
            mood_keywords = [
                "peaceful",
                "intense",
                "mysterious",
                "heroic",
                "sad",
                "joyful",
                "tense",
                "relaxing",
            ]
            for tag in metadata.tags:
                if tag.lower() in mood_keywords:
                    moods.add(tag)
        return sorted(list(moods))

    def get_asset_count(self, category: Optional[str] = None) -> int:
        """
        Get count of assets.

        Args:
            category: Count only assets in this category (optional)

        Returns:
            Number of assets
        """
        if category:
            return len([m for m in self._asset_metadata.values() if m.category == category])
        return len(self._asset_metadata)

    def get_commercial_use_count(self) -> int:
        """Get count of assets that allow commercial use."""
        return len([m for m in self._asset_metadata.values() if self._is_commercial_use_allowed(m)])

    def validate_commercial_use(self) -> Dict[str, List[str]]:
        """
        Validate all assets for commercial use compatibility.

        Returns:
            Dictionary with 'allowed' and 'restricted' lists of asset IDs
        """
        allowed = []
        restricted = []

        for metadata in self._asset_metadata.values():
            if self._is_commercial_use_allowed(metadata):
                allowed.append(metadata.id)
            else:
                restricted.append(metadata.id)

        return {"allowed": allowed, "restricted": restricted}


# Global asset manager instance
_global_asset_manager: Optional[AssetManager] = None


def get_asset_manager(base_path: Optional[Path] = None) -> AssetManager:
    """Get or create the global asset manager"""
    global _global_asset_manager
    if _global_asset_manager is None:
        _global_asset_manager = AssetManager(base_path)
    return _global_asset_manager


def set_asset_manager(manager: AssetManager):
    """Set the global asset manager"""
    global _global_asset_manager
    _global_asset_manager = manager
