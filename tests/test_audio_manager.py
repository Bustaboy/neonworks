"""
Comprehensive tests for Audio Manager

Tests sound effects, music, volume control, and spatial audio.
"""

import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from engine.audio.audio_manager import AudioManager, AudioCategory


@pytest.fixture
def audio_manager():
    """Create a fresh audio manager for each test"""
    with patch('pygame.mixer.init'):
        with patch('pygame.mixer.set_num_channels'):
            manager = AudioManager()
            manager._initialized = True  # Force initialization for testing
            return manager


class TestAudioManagerInit:
    """Test audio manager initialization"""

    def test_audio_manager_creation(self):
        """Test creating an audio manager"""
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.set_num_channels'):
                manager = AudioManager()
                manager._initialized = True

                assert manager._initialized
                assert manager.base_path == Path("assets/audio")

    def test_audio_manager_custom_path(self):
        """Test audio manager with custom base path"""
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.set_num_channels'):
                custom_path = Path("custom/audio")
                manager = AudioManager(base_path=custom_path)
                manager._initialized = True

                assert manager.base_path == custom_path

    def test_audio_manager_init_failure(self):
        """Test audio manager handles initialization failure gracefully"""
        with patch('pygame.mixer.init', side_effect=pygame.error("No audio device")):
            manager = AudioManager()

            assert not manager._initialized


class TestSoundLoading:
    """Test sound loading and caching"""

    def test_load_sound_success(self, audio_manager):
        """Test loading a sound file"""
        mock_sound = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch.object(Path, 'exists', return_value=True):
                sound = audio_manager.load_sound("test.wav")

                assert sound == mock_sound
                assert "test.wav" in audio_manager._sounds

    def test_load_sound_caching(self, audio_manager):
        """Test sound caching works"""
        mock_sound = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound) as mock_load:
            with patch.object(Path, 'exists', return_value=True):
                # Load sound twice
                sound1 = audio_manager.load_sound("test.wav")
                sound2 = audio_manager.load_sound("test.wav")

                # Should return same object
                assert sound1 == sound2
                # Should only load once
                assert mock_load.call_count == 1

    def test_load_sound_without_caching(self, audio_manager):
        """Test loading sound without caching"""
        mock_sound = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound) as mock_load:
            with patch.object(Path, 'exists', return_value=True):
                # Load sound twice without caching
                sound1 = audio_manager.load_sound("test.wav", cache=False)
                sound2 = audio_manager.load_sound("test.wav", cache=False)

                # Should load twice
                assert mock_load.call_count == 2

    def test_load_sound_failure(self, audio_manager):
        """Test loading non-existent sound"""
        with patch('pygame.mixer.Sound', side_effect=FileNotFoundError):
            sound = audio_manager.load_sound("nonexistent.wav")

            assert sound is None

    def test_preload_sounds(self, audio_manager):
        """Test preloading multiple sounds"""
        mock_sound = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch.object(Path, 'exists', return_value=True):
                paths = ["sound1.wav", "sound2.wav", "sound3.wav"]
                audio_manager.preload_sounds(paths)

                assert len(audio_manager._sounds) == 3


class TestSoundPlayback:
    """Test sound playback"""

    def test_play_sound(self, audio_manager):
        """Test playing a sound"""
        mock_sound = Mock()
        mock_sound.set_volume = Mock()
        mock_channel = Mock()
        mock_channel.play = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('pygame.mixer.find_channel', return_value=mock_channel):
                with patch.object(audio_manager, '_get_channel_id', return_value=0):
                    with patch.object(Path, 'exists', return_value=True):
                        channel_id = audio_manager.play_sound("test.wav")

                        assert channel_id is not None
                        mock_channel.play.assert_called_once()

    def test_play_sound_no_channel(self, audio_manager):
        """Test playing sound when no channel available"""
        mock_sound = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('pygame.mixer.find_channel', return_value=None):
                with patch.object(Path, 'exists', return_value=True):
                    channel_id = audio_manager.play_sound("test.wav")

                    assert channel_id is None

    def test_play_sound_with_volume(self, audio_manager):
        """Test playing sound with specific volume"""
        mock_sound = Mock()
        mock_sound.set_volume = Mock()
        mock_channel = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('pygame.mixer.find_channel', return_value=mock_channel):
                with patch.object(audio_manager, '_get_channel_id', return_value=0):
                    with patch.object(Path, 'exists', return_value=True):
                        audio_manager.play_sound("test.wav", volume=0.5)

                        # Should set volume
                        mock_sound.set_volume.assert_called_once()

    def test_play_sound_looping(self, audio_manager):
        """Test playing looping sound"""
        mock_sound = Mock()
        mock_sound.set_volume = Mock()
        mock_channel = Mock()
        mock_channel.play = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('pygame.mixer.find_channel', return_value=mock_channel):
                with patch.object(audio_manager, '_get_channel_id', return_value=0):
                    with patch.object(Path, 'exists', return_value=True):
                        audio_manager.play_sound("test.wav", loop=True)

                        # Should play with loops=-1
                        mock_channel.play.assert_called_with(mock_sound, loops=-1)

    def test_stop_sound(self, audio_manager):
        """Test stopping a sound"""
        mock_channel = Mock()
        mock_channel.stop = Mock()
        mock_sound = Mock()

        from engine.audio.audio_manager import SoundInstance
        audio_manager._playing_sounds[0] = SoundInstance(
            channel=mock_channel,
            sound=mock_sound,
            category=AudioCategory.SFX
        )

        audio_manager.stop_sound(0)

        mock_channel.stop.assert_called_once()
        assert 0 not in audio_manager._playing_sounds

    def test_stop_all_sounds(self, audio_manager):
        """Test stopping all sounds"""
        mock_channel1 = Mock()
        mock_channel2 = Mock()
        mock_sound = Mock()

        from engine.audio.audio_manager import SoundInstance
        audio_manager._playing_sounds[0] = SoundInstance(
            channel=mock_channel1,
            sound=mock_sound,
            category=AudioCategory.SFX
        )
        audio_manager._playing_sounds[1] = SoundInstance(
            channel=mock_channel2,
            sound=mock_sound,
            category=AudioCategory.SFX
        )

        audio_manager.stop_all_sounds()

        assert len(audio_manager._playing_sounds) == 0


class TestSpatialAudio:
    """Test spatial audio (3D positioned sound)"""

    def test_set_listener_position(self, audio_manager):
        """Test setting listener position"""
        audio_manager.set_listener_position(100, 200)

        x, y = audio_manager.get_listener_position()
        assert x == 100
        assert y == 200

    def test_play_sound_at_close_distance(self, audio_manager):
        """Test playing sound at close distance"""
        mock_sound = Mock()
        mock_sound.set_volume = Mock()
        mock_channel = Mock()

        audio_manager.set_listener_position(0, 0)

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('pygame.mixer.find_channel', return_value=mock_channel):
                with patch.object(audio_manager, '_get_channel_id', return_value=0):
                    with patch.object(Path, 'exists', return_value=True):
                        # Play sound close to listener
                        channel_id = audio_manager.play_sound_at("test.wav", 10, 10, max_distance=500)

                        assert channel_id is not None

    def test_play_sound_at_far_distance(self, audio_manager):
        """Test playing sound too far away doesn't play"""
        audio_manager.set_listener_position(0, 0)

        # Sound at 1000, 1000 with max_distance 500 should not play
        channel_id = audio_manager.play_sound_at("test.wav", 1000, 1000, max_distance=500)

        assert channel_id is None


class TestMusicPlayback:
    """Test music playback"""

    def test_play_music(self, audio_manager):
        """Test playing background music"""
        with patch('pygame.mixer.music.load') as mock_load:
            with patch('pygame.mixer.music.play') as mock_play:
                with patch('pygame.mixer.music.set_volume'):
                    with patch.object(Path, 'exists', return_value=True):
                        audio_manager.play_music("music.mp3")

                        mock_load.assert_called_once()
                        mock_play.assert_called_once()
                        assert audio_manager._current_music == "music.mp3"

    def test_play_music_with_fade_in(self, audio_manager):
        """Test playing music with fade in"""
        with patch('pygame.mixer.music.load'):
            with patch('pygame.mixer.music.play') as mock_play:
                with patch('pygame.mixer.music.set_volume'):
                    with patch.object(Path, 'exists', return_value=True):
                        audio_manager.play_music("music.mp3", fade_in_ms=1000)

                        # Should call play with fade_ms parameter
                        mock_play.assert_called_once()

    def test_stop_music(self, audio_manager):
        """Test stopping music"""
        with patch('pygame.mixer.music.stop') as mock_stop:
            audio_manager._current_music = "music.mp3"
            audio_manager.stop_music()

            mock_stop.assert_called_once()
            assert audio_manager._current_music is None

    def test_stop_music_with_fade_out(self, audio_manager):
        """Test stopping music with fade out"""
        with patch('pygame.mixer.music.fadeout') as mock_fadeout:
            audio_manager.stop_music(fade_out_ms=1000)

            mock_fadeout.assert_called_with(1000)

    def test_pause_unpause_music(self, audio_manager):
        """Test pausing and unpausing music"""
        with patch('pygame.mixer.music.pause') as mock_pause:
            with patch('pygame.mixer.music.unpause') as mock_unpause:
                audio_manager.pause_music()
                mock_pause.assert_called_once()

                audio_manager.unpause_music()
                mock_unpause.assert_called_once()

    def test_is_music_playing(self, audio_manager):
        """Test checking if music is playing"""
        with patch('pygame.mixer.music.get_busy', return_value=True):
            assert audio_manager.is_music_playing()

        with patch('pygame.mixer.music.get_busy', return_value=False):
            assert not audio_manager.is_music_playing()


class TestVolumeControl:
    """Test volume control"""

    def test_set_volume(self, audio_manager):
        """Test setting volume for a category"""
        audio_manager.set_volume(AudioCategory.SFX, 0.5)

        assert audio_manager.get_volume(AudioCategory.SFX) == 0.5

    def test_set_volume_clamping(self, audio_manager):
        """Test volume is clamped to 0.0-1.0"""
        audio_manager.set_volume(AudioCategory.SFX, 1.5)
        assert audio_manager.get_volume(AudioCategory.SFX) == 1.0

        audio_manager.set_volume(AudioCategory.SFX, -0.5)
        assert audio_manager.get_volume(AudioCategory.SFX) == 0.0

    def test_set_master_volume_updates_music(self, audio_manager):
        """Test setting master volume updates music"""
        with patch('pygame.mixer.music.set_volume') as mock_set_volume:
            audio_manager.set_volume(AudioCategory.MASTER, 0.5)

            # Should update music volume
            mock_set_volume.assert_called()

    def test_get_default_volumes(self, audio_manager):
        """Test default volume values"""
        assert audio_manager.get_volume(AudioCategory.MASTER) == 1.0
        assert audio_manager.get_volume(AudioCategory.MUSIC) == 0.7
        assert audio_manager.get_volume(AudioCategory.SFX) == 0.8


class TestAudioUpdate:
    """Test audio system updates"""

    def test_update_cleans_finished_sounds(self, audio_manager):
        """Test update removes finished sounds"""
        mock_channel = Mock()
        mock_channel.get_busy = Mock(return_value=False)  # Sound finished
        mock_sound = Mock()

        from engine.audio.audio_manager import SoundInstance
        audio_manager._playing_sounds[0] = SoundInstance(
            channel=mock_channel,
            sound=mock_sound,
            category=AudioCategory.SFX
        )

        audio_manager.update()

        # Finished sound should be removed
        assert 0 not in audio_manager._playing_sounds

    def test_update_keeps_playing_sounds(self, audio_manager):
        """Test update keeps playing sounds"""
        mock_channel = Mock()
        mock_channel.get_busy = Mock(return_value=True)  # Still playing
        mock_sound = Mock()

        from engine.audio.audio_manager import SoundInstance
        audio_manager._playing_sounds[0] = SoundInstance(
            channel=mock_channel,
            sound=mock_sound,
            category=AudioCategory.SFX
        )

        audio_manager.update()

        # Playing sound should remain
        assert 0 in audio_manager._playing_sounds


class TestCacheManagement:
    """Test cache management"""

    def test_clear_cache(self, audio_manager):
        """Test clearing audio cache"""
        audio_manager._sounds["test1.wav"] = Mock()
        audio_manager._sounds["test2.wav"] = Mock()

        audio_manager.clear_cache()

        assert len(audio_manager._sounds) == 0

    def test_get_cache_info(self, audio_manager):
        """Test getting cache information"""
        audio_manager._sounds["test1.wav"] = Mock()
        audio_manager._sounds["test2.wav"] = Mock()

        info = audio_manager.get_cache_info()

        assert info["sounds"] == 2
        assert "playing_sounds" in info


class TestSoundPools:
    """Test sound pools for repeated playback"""

    def test_create_sound_pool(self, audio_manager):
        """Test creating a sound pool"""
        mock_sound = Mock()

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch.object(Path, 'exists', return_value=True):
                audio_manager.create_sound_pool("gunshot", "gunshot.wav", max_instances=3)

                assert "gunshot" in audio_manager._sound_pools
                assert len(audio_manager._sound_pools["gunshot"].sounds) == 3

    def test_play_pooled_sound(self, audio_manager):
        """Test playing sound from pool"""
        mock_sound = Mock()
        mock_channel = Mock()
        mock_channel.get_busy.return_value = True

        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('pygame.mixer.find_channel', return_value=mock_channel):
                with patch('pygame.mixer.get_num_channels', return_value=8):
                    with patch('pygame.mixer.Channel', return_value=mock_channel):
                        with patch.object(Path, 'exists', return_value=True):
                            # Create pool
                            audio_manager.create_sound_pool("test", "test.wav", max_instances=2)

                            # Play from pool
                            channel_id = audio_manager.play_pooled_sound("test")

                            assert channel_id is not None
                            mock_channel.play.assert_called_once()

    def test_play_pooled_sound_nonexistent_pool(self, audio_manager):
        """Test playing from non-existent pool"""
        channel_id = audio_manager.play_pooled_sound("nonexistent")

        assert channel_id is None

    def test_sound_pool_round_robin(self, audio_manager):
        """Test sound pool uses round-robin selection"""
        mock_sounds = [Mock(), Mock(), Mock()]

        with patch('pygame.mixer.Sound', side_effect=mock_sounds):
            with patch.object(Path, 'exists', return_value=True):
                audio_manager.create_sound_pool("test", "test.wav", max_instances=3)

                pool = audio_manager._sound_pools["test"]

                # Get sounds in order
                sound1 = pool.get_sound()
                sound2 = pool.get_sound()
                sound3 = pool.get_sound()
                sound4 = pool.get_sound()  # Should wrap around

                assert sound1 == mock_sounds[0]
                assert sound2 == mock_sounds[1]
                assert sound3 == mock_sounds[2]
                assert sound4 == mock_sounds[0]  # Wrapped around


class TestMusicCrossfade:
    """Test music crossfading"""

    def test_crossfade_to_music_no_current(self, audio_manager):
        """Test crossfade when no music is playing"""
        with patch.object(audio_manager, 'play_music') as mock_play:
            audio_manager.crossfade_to_music("new_music.mp3", duration=1.0)

            # Should just play normally
            mock_play.assert_called_once()

    def test_crossfade_to_music_with_current(self, audio_manager):
        """Test crossfade from current music"""
        audio_manager._current_music = "old_music.mp3"

        audio_manager.crossfade_to_music("new_music.mp3", duration=2.0, volume=0.8)

        assert audio_manager._music_crossfade is not None
        assert audio_manager._music_crossfade.from_track == "old_music.mp3"
        assert audio_manager._music_crossfade.to_track == "new_music.mp3"
        assert audio_manager._music_crossfade.duration == 2.0

    def test_crossfade_progress(self, audio_manager):
        """Test crossfade progress calculation"""
        audio_manager._current_music = "old_music.mp3"
        audio_manager.crossfade_to_music("new_music.mp3", duration=2.0)

        # Update halfway through
        with patch.object(audio_manager, 'play_music'):
            with patch('pygame.mixer.music.set_volume'):
                audio_manager.update(1.0)

                assert audio_manager._music_crossfade.progress == 0.5
                assert not audio_manager._music_crossfade.is_complete

    def test_crossfade_completion(self, audio_manager):
        """Test crossfade completes and switches music"""
        audio_manager._current_music = "old_music.mp3"
        callback_called = []

        def on_complete():
            callback_called.append(True)

        audio_manager.crossfade_to_music("new_music.mp3", duration=1.0, on_complete=on_complete)

        with patch.object(audio_manager, 'play_music'):
            with patch('pygame.mixer.music.set_volume'):
                # Complete crossfade
                audio_manager.update(2.0)

                assert audio_manager._music_crossfade is None
                assert len(callback_called) == 1

    def test_get_current_music(self, audio_manager):
        """Test getting current music track"""
        audio_manager._current_music = "test_music.mp3"

        assert audio_manager.get_current_music() == "test_music.mp3"


class TestAudioDucking:
    """Test audio ducking"""

    def test_enable_ducking(self, audio_manager):
        """Test enabling audio ducking"""
        audio_manager.enable_ducking(AudioCategory.SFX, reduction=0.6)

        assert audio_manager._ducking_enabled
        assert audio_manager._ducking_target_category == AudioCategory.SFX
        assert audio_manager._ducking_reduction == 0.6

    def test_disable_ducking(self, audio_manager):
        """Test disabling audio ducking"""
        audio_manager.enable_ducking(AudioCategory.SFX)
        audio_manager._ducking_active = True

        with patch('pygame.mixer.music.set_volume'):
            audio_manager.disable_ducking()

            assert not audio_manager._ducking_enabled
            assert not audio_manager._ducking_active

    def test_ducking_activates_on_target_sound(self, audio_manager):
        """Test ducking activates when target sound plays"""
        audio_manager.enable_ducking(AudioCategory.SFX, reduction=0.5)

        # Add a playing SFX sound
        mock_instance = Mock()
        mock_instance.category = AudioCategory.SFX
        audio_manager._playing_sounds[0] = mock_instance

        with patch('pygame.mixer.music.set_volume'):
            audio_manager.update(0.016)

            assert audio_manager._ducking_active

    def test_ducking_deactivates_when_sound_stops(self, audio_manager):
        """Test ducking deactivates when target sound stops"""
        audio_manager.enable_ducking(AudioCategory.SFX)
        audio_manager._ducking_active = True

        # No playing sounds
        audio_manager._playing_sounds.clear()

        with patch('pygame.mixer.music.set_volume'):
            audio_manager.update(0.016)

            assert not audio_manager._ducking_active

    def test_ducking_ignores_other_categories(self, audio_manager):
        """Test ducking only applies to target category"""
        audio_manager.enable_ducking(AudioCategory.SFX)

        # Add a playing UI sound (not SFX)
        mock_instance = Mock()
        mock_instance.category = AudioCategory.UI
        audio_manager._playing_sounds[0] = mock_instance

        with patch('pygame.mixer.music.set_volume'):
            audio_manager.update(0.016)

            assert not audio_manager._ducking_active


class TestEnhancedUtilities:
    """Test enhanced utility functions"""

    def test_cache_info_includes_pools(self, audio_manager):
        """Test cache info includes sound pools"""
        from engine.audio.audio_manager import SoundPool

        audio_manager._sound_pools["test1"] = SoundPool()
        audio_manager._sound_pools["test2"] = SoundPool()

        info = audio_manager.get_cache_info()

        assert "sound_pools" in info
        assert info["sound_pools"] == 2

    def test_clear_cache_clears_pools(self, audio_manager):
        """Test clear cache also clears sound pools"""
        from engine.audio.audio_manager import SoundPool

        audio_manager._sound_pools["test"] = SoundPool()

        audio_manager.clear_cache()

        assert len(audio_manager._sound_pools) == 0


# Run tests with: pytest engine/tests/test_audio_manager.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
