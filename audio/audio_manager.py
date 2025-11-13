"""
Audio Manager

Manages sound effects, music, and spatial audio.
"""

import pygame
from typing import Dict, Optional, Tuple, List, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import time


class AudioCategory(Enum):
    """Audio categories for volume control"""

    MASTER = "master"
    MUSIC = "music"
    SFX = "sfx"
    AMBIENT = "ambient"
    UI = "ui"


@dataclass
class SoundInstance:
    """Represents a playing sound instance"""

    channel: pygame.mixer.Channel
    sound: pygame.mixer.Sound
    category: AudioCategory
    loop: bool = False


@dataclass
class SoundPool:
    """Pool of pre-loaded sounds for efficient repeated playback"""

    sounds: List[pygame.mixer.Sound] = field(default_factory=list)
    current_index: int = 0
    max_instances: int = 4

    def add_sound(self, sound: pygame.mixer.Sound):
        """Add a sound to the pool"""
        if len(self.sounds) < self.max_instances:
            self.sounds.append(sound)

    def get_sound(self) -> Optional[pygame.mixer.Sound]:
        """Get next available sound from pool (round-robin)"""
        if not self.sounds:
            return None

        sound = self.sounds[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.sounds)
        return sound


@dataclass
class MusicCrossfade:
    """Manages music crossfade transition"""

    from_track: Optional[str]
    to_track: str
    duration: float
    elapsed: float = 0.0
    from_volume: float = 1.0
    to_volume: float = 0.0
    on_complete: Optional[Callable[[], None]] = None

    @property
    def progress(self) -> float:
        """Get crossfade progress (0.0 to 1.0)"""
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)

    @property
    def is_complete(self) -> bool:
        """Check if crossfade is complete"""
        return self.elapsed >= self.duration


class AudioManager:
    """
    Manages audio playback for the game.

    Features:
    - Sound effect playback
    - Background music with crossfading
    - Volume control per category
    - Sound caching
    - Spatial audio (distance-based volume/panning)
    - Multiple audio channels
    """

    def __init__(self, base_path: Optional[Path] = None, channels: int = 8):
        """
        Initialize audio manager.

        Args:
            base_path: Base path for audio files. Defaults to 'assets/audio/'
            channels: Number of audio channels for mixing
        """
        self.base_path = Path(base_path) if base_path else Path("assets/audio")

        # Sound caches
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._music_cache: Dict[str, Path] = {}

        # Sound pools
        self._sound_pools: Dict[str, SoundPool] = {}

        # Playing sounds tracking
        self._playing_sounds: Dict[int, SoundInstance] = (
            {}
        )  # channel_id -> SoundInstance

        # Volume settings (0.0 to 1.0)
        self._volumes: Dict[AudioCategory, float] = {
            AudioCategory.MASTER: 1.0,
            AudioCategory.MUSIC: 0.7,
            AudioCategory.SFX: 0.8,
            AudioCategory.AMBIENT: 0.5,
            AudioCategory.UI: 0.9,
        }

        # Music state
        self._current_music: Optional[str] = None
        self._music_volume: float = 0.7
        self._music_crossfade: Optional[MusicCrossfade] = None

        # Audio ducking (automatic volume reduction)
        self._ducking_enabled = False
        self._ducking_target_category: Optional[AudioCategory] = None
        self._ducking_reduction: float = 0.5  # Reduce to 50% volume
        self._ducking_active = False

        # Listener position for spatial audio
        self._listener_x: float = 0.0
        self._listener_y: float = 0.0

        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(channels)
            self._initialized = True
        except pygame.error as e:
            print(f"⚠️  Failed to initialize audio: {e}")
            self._initialized = False

    # ========== Sound Loading ==========

    def load_sound(self, path: str, cache: bool = True) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound effect from file.

        Args:
            path: Path to sound file relative to base_path
            cache: Whether to cache the sound

        Returns:
            Sound object or None if loading failed
        """
        if not self._initialized:
            return None

        # Check cache
        if cache and path in self._sounds:
            return self._sounds[path]

        full_path = self.base_path / path

        try:
            sound = pygame.mixer.Sound(str(full_path))

            if cache:
                self._sounds[path] = sound
                print(f"✓ Loaded sound: {path}")

            return sound

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to load sound '{path}': {e}")
            return None

    def preload_sounds(self, paths: List[str]):
        """Preload a list of sounds"""
        total = len(paths)
        loaded = 0

        for path in paths:
            if self.load_sound(path):
                loaded += 1

        print(f"Preloaded {loaded}/{total} sounds")

    # ========== Sound Pools ==========

    def create_sound_pool(self, pool_name: str, path: str, max_instances: int = 4):
        """
        Create a sound pool for efficient repeated playback.

        Args:
            pool_name: Name for the sound pool
            path: Path to sound file
            max_instances: Maximum number of simultaneous instances
        """
        pool = SoundPool(max_instances=max_instances)

        # Load multiple copies of the sound
        for _ in range(max_instances):
            sound = self.load_sound(path, cache=False)
            if sound:
                pool.add_sound(sound)

        self._sound_pools[pool_name] = pool
        print(f"✓ Created sound pool '{pool_name}' with {len(pool.sounds)} instances")

    def play_pooled_sound(
        self,
        pool_name: str,
        category: AudioCategory = AudioCategory.SFX,
        volume: float = 1.0,
    ) -> Optional[int]:
        """
        Play a sound from a pool.

        Args:
            pool_name: Name of the sound pool
            category: Audio category
            volume: Sound volume

        Returns:
            Channel ID or None if playback failed
        """
        if pool_name not in self._sound_pools:
            print(f"⚠️  Sound pool '{pool_name}' not found")
            return None

        pool = self._sound_pools[pool_name]
        sound = pool.get_sound()

        if not sound:
            return None

        # Find available channel
        channel = pygame.mixer.find_channel()
        if not channel:
            return None

        # Calculate final volume
        final_volume = (
            volume * self._volumes[category] * self._volumes[AudioCategory.MASTER]
        )
        sound.set_volume(final_volume)

        # Play sound
        channel.play(sound)

        # Track playing sound
        channel_id = self._get_channel_id(channel)
        self._playing_sounds[channel_id] = SoundInstance(
            channel=channel, sound=sound, category=category, loop=False
        )

        return channel_id

    # ========== Sound Playback ==========

    def play_sound(
        self,
        path: str,
        category: AudioCategory = AudioCategory.SFX,
        volume: float = 1.0,
        loop: bool = False,
    ) -> Optional[int]:
        """
        Play a sound effect.

        Args:
            path: Path to sound file
            category: Audio category for volume control
            volume: Sound volume (0.0 to 1.0), multiplied with category volume
            loop: Whether to loop the sound

        Returns:
            Channel ID or None if playback failed
        """
        if not self._initialized:
            return None

        sound = self.load_sound(path)
        if not sound:
            return None

        # Find available channel
        channel = pygame.mixer.find_channel()
        if not channel:
            print("⚠️  No available audio channels")
            return None

        # Calculate final volume
        final_volume = (
            volume * self._volumes[category] * self._volumes[AudioCategory.MASTER]
        )
        sound.set_volume(final_volume)

        # Play sound
        loops = -1 if loop else 0
        channel.play(sound, loops=loops)

        # Track playing sound
        channel_id = self._get_channel_id(channel)
        self._playing_sounds[channel_id] = SoundInstance(
            channel=channel, sound=sound, category=category, loop=loop
        )

        return channel_id

    def play_sound_at(
        self,
        path: str,
        x: float,
        y: float,
        category: AudioCategory = AudioCategory.SFX,
        max_distance: float = 500.0,
    ) -> Optional[int]:
        """
        Play a sound at a specific position with spatial audio.

        Args:
            path: Path to sound file
            x: X position in world space
            y: Y position in world space
            category: Audio category
            max_distance: Maximum hearing distance

        Returns:
            Channel ID or None if playback failed
        """
        if not self._initialized:
            return None

        # Calculate distance from listener
        dx = x - self._listener_x
        dy = y - self._listener_y
        distance = (dx * dx + dy * dy) ** 0.5

        # Don't play if too far
        if distance > max_distance:
            return None

        # Calculate volume based on distance
        volume = 1.0 - (distance / max_distance)
        volume = max(0.0, min(1.0, volume))

        # Play sound with distance-based volume
        channel_id = self.play_sound(path, category, volume)

        if channel_id is not None:
            # Calculate panning (left/right balance)
            # Simple panning based on x position
            if abs(dx) > 0.01:
                # -1.0 = full left, 1.0 = full right
                pan = dx / max_distance
                pan = max(-1.0, min(1.0, pan))
                self._set_channel_pan(channel_id, pan)

        return channel_id

    def stop_sound(self, channel_id: int):
        """Stop a playing sound"""
        if channel_id in self._playing_sounds:
            self._playing_sounds[channel_id].channel.stop()
            del self._playing_sounds[channel_id]

    def stop_all_sounds(self):
        """Stop all playing sounds"""
        for channel_id in list(self._playing_sounds.keys()):
            self.stop_sound(channel_id)

    # ========== Music Playback ==========

    def play_music(
        self, path: str, volume: float = 1.0, loop: bool = True, fade_in_ms: int = 0
    ):
        """
        Play background music.

        Args:
            path: Path to music file
            volume: Music volume (0.0 to 1.0)
            loop: Whether to loop the music
            fade_in_ms: Fade-in duration in milliseconds
        """
        if not self._initialized:
            return

        full_path = self.base_path / path

        try:
            # Stop current music
            if self._current_music:
                pygame.mixer.music.stop()

            # Load and play new music
            pygame.mixer.music.load(str(full_path))

            # Set volume
            self._music_volume = volume
            final_volume = (
                volume
                * self._volumes[AudioCategory.MUSIC]
                * self._volumes[AudioCategory.MASTER]
            )
            pygame.mixer.music.set_volume(final_volume)

            # Play
            loops = -1 if loop else 0
            if fade_in_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_in_ms)
            else:
                pygame.mixer.music.play(loops)

            self._current_music = path
            print(f"♪ Playing music: {path}")

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to play music '{path}': {e}")

    def stop_music(self, fade_out_ms: int = 0):
        """
        Stop background music.

        Args:
            fade_out_ms: Fade-out duration in milliseconds
        """
        if not self._initialized:
            return

        if fade_out_ms > 0:
            pygame.mixer.music.fadeout(fade_out_ms)
        else:
            pygame.mixer.music.stop()

        self._current_music = None

    def pause_music(self):
        """Pause background music"""
        if self._initialized:
            pygame.mixer.music.pause()

    def unpause_music(self):
        """Unpause background music"""
        if self._initialized:
            pygame.mixer.music.unpause()

    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        if not self._initialized:
            return False
        return pygame.mixer.music.get_busy()

    def crossfade_to_music(
        self,
        path: str,
        duration: float = 2.0,
        volume: float = 1.0,
        loop: bool = True,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        """
        Crossfade from current music to new music.

        Args:
            path: Path to new music file
            duration: Crossfade duration in seconds
            volume: Target music volume
            loop: Whether to loop the new music
            on_complete: Optional callback when crossfade completes
        """
        if not self._initialized:
            return

        # If no music playing, just play normally
        if not self._current_music:
            self.play_music(path, volume, loop)
            if on_complete:
                on_complete()
            return

        # Start crossfade
        self._music_crossfade = MusicCrossfade(
            from_track=self._current_music,
            to_track=path,
            duration=duration,
            from_volume=self._music_volume,
            to_volume=volume,
            on_complete=on_complete,
        )

        # Store loop setting for when crossfade completes
        self._music_crossfade.loop = loop  # Add this attribute dynamically

    def get_current_music(self) -> Optional[str]:
        """Get currently playing music track"""
        return self._current_music

    # ========== Volume Control ==========

    def set_volume(self, category: AudioCategory, volume: float):
        """
        Set volume for a category.

        Args:
            category: Audio category
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        self._volumes[category] = volume

        # Update music volume if category is master or music
        if category in [AudioCategory.MASTER, AudioCategory.MUSIC]:
            if self._initialized:
                final_volume = (
                    self._music_volume
                    * self._volumes[AudioCategory.MUSIC]
                    * self._volumes[AudioCategory.MASTER]
                )
                pygame.mixer.music.set_volume(final_volume)

        # Update playing sound volumes if category is master or matches their category
        if category == AudioCategory.MASTER:
            for instance in self._playing_sounds.values():
                self._update_sound_volume(instance)
        else:
            for instance in self._playing_sounds.values():
                if instance.category == category:
                    self._update_sound_volume(instance)

    def get_volume(self, category: AudioCategory) -> float:
        """Get volume for a category"""
        return self._volumes[category]

    def _update_sound_volume(self, instance: SoundInstance):
        """Update volume for a playing sound instance"""
        final_volume = (
            self._volumes[instance.category] * self._volumes[AudioCategory.MASTER]
        )
        instance.sound.set_volume(final_volume)

    # ========== Audio Ducking ==========

    def enable_ducking(self, target_category: AudioCategory, reduction: float = 0.5):
        """
        Enable audio ducking (automatic volume reduction when target sounds play).

        Args:
            target_category: Category that triggers ducking (e.g., SFX)
            reduction: Volume reduction multiplier (0.5 = reduce to 50%)
        """
        self._ducking_enabled = True
        self._ducking_target_category = target_category
        self._ducking_reduction = reduction

    def disable_ducking(self):
        """Disable audio ducking"""
        self._ducking_enabled = False
        self._ducking_active = False

        # Restore music volume if it was ducked
        if self._initialized:
            final_volume = (
                self._music_volume
                * self._volumes[AudioCategory.MUSIC]
                * self._volumes[AudioCategory.MASTER]
            )
            pygame.mixer.music.set_volume(final_volume)

    # ========== Spatial Audio ==========

    def set_listener_position(self, x: float, y: float):
        """
        Set listener position for spatial audio.

        Args:
            x: X position in world space
            y: Y position in world space
        """
        self._listener_x = x
        self._listener_y = y

    def get_listener_position(self) -> Tuple[float, float]:
        """Get listener position"""
        return (self._listener_x, self._listener_y)

    # ========== Utilities ==========

    def update(self, delta_time: float = 0.016):
        """
        Update audio system (call once per frame).

        Args:
            delta_time: Time since last update in seconds (default: 16ms)
        """
        if not self._initialized:
            return

        # Update music crossfade
        if self._music_crossfade:
            self._music_crossfade.elapsed += delta_time

            if self._music_crossfade.is_complete:
                # Crossfade complete - switch to new music
                loop = getattr(self._music_crossfade, "loop", True)
                self.play_music(
                    self._music_crossfade.to_track,
                    self._music_crossfade.to_volume,
                    loop,
                )

                # Call completion callback
                if self._music_crossfade.on_complete:
                    self._music_crossfade.on_complete()

                self._music_crossfade = None
            else:
                # Update volumes during crossfade
                progress = self._music_crossfade.progress
                current_volume = self._music_crossfade.from_volume * (1.0 - progress)

                final_volume = (
                    current_volume
                    * self._volumes[AudioCategory.MUSIC]
                    * self._volumes[AudioCategory.MASTER]
                )
                pygame.mixer.music.set_volume(final_volume)

        # Update audio ducking
        if self._ducking_enabled and self._ducking_target_category:
            # Check if any sounds of target category are playing
            has_target_sounds = any(
                instance.category == self._ducking_target_category
                for instance in self._playing_sounds.values()
            )

            if has_target_sounds and not self._ducking_active:
                # Start ducking
                self._ducking_active = True
                reduced_volume = self._music_volume * self._ducking_reduction
                final_volume = (
                    reduced_volume
                    * self._volumes[AudioCategory.MUSIC]
                    * self._volumes[AudioCategory.MASTER]
                )
                pygame.mixer.music.set_volume(final_volume)

            elif not has_target_sounds and self._ducking_active:
                # Stop ducking
                self._ducking_active = False
                final_volume = (
                    self._music_volume
                    * self._volumes[AudioCategory.MUSIC]
                    * self._volumes[AudioCategory.MASTER]
                )
                pygame.mixer.music.set_volume(final_volume)

        # Clean up finished sounds
        finished_channels = []
        for channel_id, instance in self._playing_sounds.items():
            if not instance.channel.get_busy():
                finished_channels.append(channel_id)

        for channel_id in finished_channels:
            del self._playing_sounds[channel_id]

    def clear_cache(self):
        """Clear cached sounds"""
        self._sounds.clear()
        self._music_cache.clear()
        self._sound_pools.clear()
        print("Audio cache cleared")

    def get_cache_info(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "sounds": len(self._sounds),
            "playing_sounds": len(self._playing_sounds),
            "sound_pools": len(self._sound_pools),
        }

    def _get_channel_id(self, channel: pygame.mixer.Channel) -> int:
        """Get numeric ID for a channel"""
        # Pygame channels have numeric IDs
        for i in range(pygame.mixer.get_num_channels()):
            if pygame.mixer.Channel(i) == channel:
                return i
        return -1

    def _set_channel_pan(self, channel_id: int, pan: float):
        """
        Set stereo panning for a channel.

        Args:
            channel_id: Channel ID
            pan: Pan value (-1.0 = full left, 0.0 = center, 1.0 = full right)
        """
        if channel_id in self._playing_sounds:
            instance = self._playing_sounds[channel_id]

            # Calculate left/right volumes
            # pan = -1.0: left = 1.0, right = 0.0
            # pan = 0.0: left = 1.0, right = 1.0
            # pan = 1.0: left = 0.0, right = 1.0
            if pan < 0:
                left = 1.0
                right = 1.0 + pan
            elif pan > 0:
                left = 1.0 - pan
                right = 1.0
            else:
                left = 1.0
                right = 1.0

            # Note: pygame doesn't have built-in stereo panning
            # This is a simplified implementation
            # For proper stereo panning, you'd need to use pygame's Sound.set_volume()
            # on separate left/right channel copies of the sound


# Global audio manager instance
_global_audio_manager: Optional[AudioManager] = None


def get_audio_manager(
    base_path: Optional[Path] = None, channels: int = 8
) -> AudioManager:
    """Get or create the global audio manager"""
    global _global_audio_manager
    if _global_audio_manager is None:
        _global_audio_manager = AudioManager(base_path, channels)
    return _global_audio_manager


def set_audio_manager(manager: AudioManager):
    """Set the global audio manager"""
    global _global_audio_manager
    _global_audio_manager = manager
