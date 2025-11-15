"""
AI-Powered Animation Generator

Automatically generate sprite animations from static images using AI models.
Supports multiple animation types and integrates with the character generator system.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pygame
from PIL import Image


@dataclass
class AnimationConfig:
    """Configuration for animation generation"""

    animation_type: str  # idle, walk, run, attack, etc.
    frame_count: int  # Number of frames to generate
    frame_duration: float  # Duration per frame in seconds
    loop: bool  # Whether animation loops
    style: str  # Animation style (smooth, snappy, bouncy, etc.)
    intensity: float  # Animation intensity (0.0 to 1.0)


class AnimationType:
    """Standard animation types with default configurations"""

    IDLE = AnimationConfig("idle", 4, 0.2, True, "smooth", 0.3)
    WALK = AnimationConfig("walk", 6, 0.12, True, "smooth", 0.6)
    RUN = AnimationConfig("run", 6, 0.08, True, "snappy", 0.9)
    ATTACK = AnimationConfig("attack", 4, 0.1, False, "snappy", 1.0)
    CAST_SPELL = AnimationConfig("cast_spell", 6, 0.15, False, "smooth", 0.7)
    HURT = AnimationConfig("hurt", 2, 0.1, False, "snappy", 1.0)
    DEATH = AnimationConfig("death", 6, 0.15, False, "smooth", 0.8)
    JUMP = AnimationConfig("jump", 6, 0.1, False, "bouncy", 0.9)

    @classmethod
    def get_all(cls) -> List[AnimationConfig]:
        """Get all standard animation types"""
        return [
            cls.IDLE,
            cls.WALK,
            cls.RUN,
            cls.ATTACK,
            cls.CAST_SPELL,
            cls.HURT,
            cls.DEATH,
            cls.JUMP,
        ]

    @classmethod
    def get_by_name(cls, name: str) -> Optional[AnimationConfig]:
        """Get animation config by name"""
        for anim in cls.get_all():
            if anim.animation_type == name:
                return anim
        return None


class AIAnimator:
    """
    AI-powered sprite animation generator.

    This class provides the core functionality for generating sprite animations
    from static images using AI models. It supports multiple animation types
    and can be integrated with external AI services or local models.
    """

    def __init__(self, model_type: str = "local"):
        """
        Initialize AI animator.

        Args:
            model_type: Type of AI model to use ('local', 'api', 'hybrid')
        """
        self.model_type = model_type
        self.cache_dir = Path("cache/ai_animations")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # TODO: Initialize AI model based on model_type
        # - local: Load local ML model (e.g., ONNX, TensorFlow)
        # - api: Configure API client (e.g., Stability AI, Runway)
        # - hybrid: Use local for simple animations, API for complex

    def generate_animation(
        self,
        source_image: pygame.Surface,
        config: AnimationConfig,
        component_id: Optional[str] = None,
    ) -> List[pygame.Surface]:
        """
        Generate animation frames from source image.

        Args:
            source_image: Static sprite to animate
            config: Animation configuration
            component_id: Optional component ID for caching

        Returns:
            List of animation frames as pygame surfaces
        """
        # Check cache first
        if component_id:
            cached_frames = self._load_from_cache(component_id, config.animation_type)
            if cached_frames:
                return cached_frames

        # Generate frames using appropriate method
        if self.model_type == "local":
            frames = self._generate_local(source_image, config)
        elif self.model_type == "api":
            frames = self._generate_api(source_image, config)
        else:  # hybrid
            frames = self._generate_hybrid(source_image, config)

        # Cache results
        if component_id:
            self._save_to_cache(component_id, config.animation_type, frames)

        return frames

    def _generate_local(
        self, source_image: pygame.Surface, config: AnimationConfig
    ) -> List[pygame.Surface]:
        """
        Generate animation using local AI model.

        This is a placeholder for local ML model integration.
        Replace with actual model inference.

        TODO: Integrate local animation model
        - Option 1: Sprite interpolation using optical flow
        - Option 2: GAN-based sprite animation
        - Option 3: Diffusion model for sprite frames
        """
        print(f"[AI Animator] Generating {config.animation_type} locally...")

        # For now, use procedural animation as fallback
        return self._generate_procedural(source_image, config)

    def _generate_api(
        self, source_image: pygame.Surface, config: AnimationConfig
    ) -> List[pygame.Surface]:
        """
        Generate animation using external AI API.

        TODO: Integrate with AI animation API
        - Stability AI for general animation
        - Specialized pixel art animation services
        - Custom trained models hosted on cloud
        """
        print(f"[AI Animator] Generating {config.animation_type} via API...")

        # Fallback to procedural
        return self._generate_procedural(source_image, config)

    def _generate_hybrid(
        self, source_image: pygame.Surface, config: AnimationConfig
    ) -> List[pygame.Surface]:
        """
        Generate animation using hybrid approach.

        Simple animations use local generation, complex ones use API.
        """
        # Simple animations: idle, hurt
        simple_anims = ["idle", "hurt"]

        if config.animation_type in simple_anims:
            return self._generate_local(source_image, config)
        else:
            return self._generate_api(source_image, config)

    def _generate_procedural(
        self, source_image: pygame.Surface, config: AnimationConfig
    ) -> List[pygame.Surface]:
        """
        Generate animation using procedural techniques.

        This serves as a fallback when AI models are not available.
        Uses traditional animation techniques like squash/stretch, rotation, etc.
        """
        frames = []
        width, height = source_image.get_size()

        for frame_idx in range(config.frame_count):
            # Calculate animation progress (0.0 to 1.0)
            progress = frame_idx / max(1, config.frame_count - 1)

            # Create frame based on animation type
            frame = source_image.copy()

            if config.animation_type == "idle":
                frame = self._apply_idle_effect(frame, progress, config.intensity)
            elif config.animation_type == "walk":
                frame = self._apply_walk_effect(frame, progress, config.intensity)
            elif config.animation_type == "run":
                frame = self._apply_run_effect(frame, progress, config.intensity)
            elif config.animation_type == "attack":
                frame = self._apply_attack_effect(frame, progress, config.intensity)
            elif config.animation_type == "jump":
                frame = self._apply_jump_effect(frame, progress, config.intensity)
            elif config.animation_type == "hurt":
                frame = self._apply_hurt_effect(frame, progress, config.intensity)
            elif config.animation_type == "death":
                frame = self._apply_death_effect(frame, progress, config.intensity)
            elif config.animation_type == "cast_spell":
                frame = self._apply_cast_effect(frame, progress, config.intensity)

            frames.append(frame)

        return frames

    def _apply_idle_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply idle breathing animation effect"""
        # Gentle vertical oscillation (breathing)
        offset_y = int(np.sin(progress * np.pi * 2) * 2 * intensity)

        result = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        result.blit(frame, (0, offset_y))
        return result

    def _apply_walk_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply walking animation effect"""
        # Bob up and down + slight lean
        bob = int(np.sin(progress * np.pi * 2) * 3 * intensity)
        lean = int(np.sin(progress * np.pi * 2) * 1 * intensity)

        result = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        result.blit(frame, (lean, bob))
        return result

    def _apply_run_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply running animation effect"""
        # More pronounced bob + forward lean
        bob = int(np.sin(progress * np.pi * 2) * 4 * intensity)
        lean = int(-2 * intensity)  # Forward lean

        result = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        result.blit(frame, (lean, bob))
        return result

    def _apply_attack_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply attack animation effect"""
        # Forward thrust + recoil
        if progress < 0.5:
            # Wind up
            offset_x = int(-progress * 4 * intensity)
        else:
            # Strike
            offset_x = int((progress - 0.5) * 8 * intensity)

        result = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        result.blit(frame, (offset_x, 0))
        return result

    def _apply_jump_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply jump animation effect"""
        # Parabolic arc
        jump_height = 20 * intensity
        offset_y = int(-jump_height * (1 - (2 * progress - 1) ** 2))

        # Squash and stretch
        if progress < 0.2:
            # Squash before jump
            scale_y = 0.9
        elif progress > 0.8:
            # Squash on landing
            scale_y = 0.9
        else:
            # Stretch in air
            scale_y = 1.1

        result = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        scaled = pygame.transform.scale(
            frame, (frame.get_width(), int(frame.get_height() * scale_y))
        )
        y_offset = offset_y + int((frame.get_height() - scaled.get_height()) / 2)
        result.blit(scaled, (0, y_offset))
        return result

    def _apply_hurt_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply hurt recoil effect"""
        # Knockback + flash
        offset_x = int(-8 * (1 - progress) * intensity)

        result = frame.copy()
        result.scroll(offset_x, 0)

        # Flash effect (lighten sprite)
        if progress < 0.5:
            flash_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, int(128 * (1 - progress * 2))))
            result.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return result

    def _apply_death_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply death animation effect"""
        # Rotate and fade
        angle = progress * 90  # Rotate 90 degrees
        alpha = int(255 * (1 - progress))  # Fade out

        result = pygame.transform.rotate(frame, -angle)
        result.set_alpha(alpha)
        return result

    def _apply_cast_effect(
        self, frame: pygame.Surface, progress: float, intensity: float
    ) -> pygame.Surface:
        """Apply spellcasting animation effect"""
        # Raise hands + glow effect
        offset_y = int(-progress * 4 * intensity)

        result = frame.copy()
        result.scroll(0, offset_y)

        # Add glow
        if progress > 0.5:
            glow_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            glow_alpha = int(128 * (progress - 0.5) * 2)
            glow_surface.fill((150, 150, 255, glow_alpha))
            result.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return result

    def generate_animation_batch(
        self,
        source_image: pygame.Surface,
        animation_types: List[str],
        component_id: Optional[str] = None,
    ) -> Dict[str, List[pygame.Surface]]:
        """
        Generate multiple animations for a single sprite.

        Args:
            source_image: Static sprite to animate
            animation_types: List of animation type names
            component_id: Optional component ID

        Returns:
            Dictionary mapping animation names to frame lists
        """
        results = {}

        for anim_type in animation_types:
            config = AnimationType.get_by_name(anim_type)
            if config:
                print(f"Generating {anim_type} animation...")
                frames = self.generate_animation(source_image, config, component_id)
                results[anim_type] = frames

        return results

    def export_animation_frames(
        self,
        frames: List[pygame.Surface],
        output_dir: Path,
        component_id: str,
        animation_type: str,
    ):
        """
        Export animation frames to disk.

        Follows the naming convention: {component_id}_{animation}_{frame}.png

        Args:
            frames: List of animation frames
            output_dir: Directory to save frames
            component_id: Component identifier
            animation_type: Animation type name
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for idx, frame in enumerate(frames, start=1):
            filename = f"{component_id}_{animation_type}_{idx:02d}.png"
            filepath = output_dir / filename
            pygame.image.save(frame, str(filepath))
            print(f"Saved: {filepath}")

    def export_sprite_sheet(
        self,
        frames: List[pygame.Surface],
        output_path: Path,
        layout: str = "horizontal",
    ):
        """
        Export animation as a sprite sheet.

        Args:
            frames: List of animation frames
            output_path: Output file path
            layout: Layout style ('horizontal', 'vertical', 'grid')
        """
        if not frames:
            return

        frame_width, frame_height = frames[0].get_size()
        frame_count = len(frames)

        if layout == "horizontal":
            sheet_width = frame_width * frame_count
            sheet_height = frame_height
            positions = [(i * frame_width, 0) for i in range(frame_count)]
        elif layout == "vertical":
            sheet_width = frame_width
            sheet_height = frame_height * frame_count
            positions = [(0, i * frame_height) for i in range(frame_count)]
        else:  # grid
            cols = int(np.ceil(np.sqrt(frame_count)))
            rows = int(np.ceil(frame_count / cols))
            sheet_width = frame_width * cols
            sheet_height = frame_height * rows
            positions = [
                ((i % cols) * frame_width, (i // cols) * frame_height) for i in range(frame_count)
            ]

        # Create sprite sheet
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        sheet.fill((0, 0, 0, 0))

        for frame, pos in zip(frames, positions):
            sheet.blit(frame, pos)

        # Save
        pygame.image.save(sheet, str(output_path))
        print(f"Sprite sheet saved: {output_path}")

    def _load_from_cache(
        self, component_id: str, animation_type: str
    ) -> Optional[List[pygame.Surface]]:
        """Load cached animation frames"""
        cache_file = self.cache_dir / f"{component_id}_{animation_type}.json"

        if not cache_file.exists():
            return None

        # Load metadata
        with open(cache_file, "r") as f:
            metadata = json.load(f)

        # Load frames
        frames = []
        frame_dir = self.cache_dir / component_id / animation_type

        if not frame_dir.exists():
            return None

        for frame_path in sorted(frame_dir.glob("*.png")):
            frame = pygame.image.load(str(frame_path))
            frames.append(frame)

        if len(frames) == metadata.get("frame_count", 0):
            print(f"Loaded from cache: {component_id}/{animation_type}")
            return frames

        return None

    def _save_to_cache(self, component_id: str, animation_type: str, frames: List[pygame.Surface]):
        """Save animation frames to cache"""
        # Create cache directory
        frame_dir = self.cache_dir / component_id / animation_type
        frame_dir.mkdir(parents=True, exist_ok=True)

        # Save frames
        for idx, frame in enumerate(frames, start=1):
            frame_path = frame_dir / f"frame_{idx:02d}.png"
            pygame.image.save(frame, str(frame_path))

        # Save metadata
        cache_file = self.cache_dir / f"{component_id}_{animation_type}.json"
        metadata = {
            "component_id": component_id,
            "animation_type": animation_type,
            "frame_count": len(frames),
        }

        with open(cache_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Cached: {component_id}/{animation_type}")


class AnimationPostProcessor:
    """Post-processing tools for refining AI-generated animations"""

    @staticmethod
    def smooth_transitions(frames: List[pygame.Surface]) -> List[pygame.Surface]:
        """
        Smooth transitions between frames using interpolation.

        TODO: Implement optical flow-based frame interpolation
        """
        # For now, return original frames
        return frames

    @staticmethod
    def apply_motion_blur(
        frames: List[pygame.Surface], intensity: float = 0.5
    ) -> List[pygame.Surface]:
        """Apply motion blur effect to frames"""
        blurred_frames = []

        for i, frame in enumerate(frames):
            if i == 0:
                blurred_frames.append(frame)
                continue

            # Blend current frame with previous
            blended = frame.copy()
            prev_frame = frames[i - 1].copy()
            prev_frame.set_alpha(int(255 * intensity))
            blended.blit(prev_frame, (0, 0))

            blurred_frames.append(blended)

        return blurred_frames

    @staticmethod
    def adjust_timing(
        frames: List[pygame.Surface], hold_first: int = 0, hold_last: int = 0
    ) -> List[pygame.Surface]:
        """
        Adjust animation timing by duplicating frames.

        Args:
            frames: Original frames
            hold_first: How many times to duplicate first frame
            hold_last: How many times to duplicate last frame
        """
        result = []

        # Hold first frame
        if hold_first > 0 and frames:
            result.extend([frames[0]] * hold_first)

        result.extend(frames)

        # Hold last frame
        if hold_last > 0 and frames:
            result.extend([frames[-1]] * hold_last)

        return result

    @staticmethod
    def add_impact_frame(
        frames: List[pygame.Surface], position: int = -1, intensity: float = 1.0
    ) -> List[pygame.Surface]:
        """
        Add an impact frame (for attacks, hits, etc.).

        Args:
            frames: Animation frames
            position: Where to insert impact frame (-1 for end)
            intensity: Flash intensity
        """
        if position == -1:
            position = len(frames) - 1

        if 0 <= position < len(frames):
            impact_frame = frames[position].copy()

            # Add white flash
            flash = pygame.Surface(impact_frame.get_size(), pygame.SRCALPHA)
            flash.fill((255, 255, 255, int(200 * intensity)))
            impact_frame.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            frames.insert(position + 1, impact_frame)

        return frames


# Example usage
if __name__ == "__main__":
    # Initialize pygame for testing
    pygame.init()

    # Create AI animator
    animator = AIAnimator(model_type="local")

    # Load a test sprite
    # test_sprite = pygame.image.load("assets/characters/hero.png")

    # Generate walk animation
    # walk_config = AnimationType.WALK
    # walk_frames = animator.generate_animation(test_sprite, walk_config, "hero")

    # Export frames
    # animator.export_animation_frames(
    #     walk_frames,
    #     Path("output/animations/hero"),
    #     "hero",
    #     "walk"
    # )

    # Or export as sprite sheet
    # animator.export_sprite_sheet(
    #     walk_frames,
    #     Path("output/animations/hero_walk_sheet.png"),
    #     layout="horizontal"
    # )

    print("AI Animator initialized. Ready to generate animations!")
