"""
Physics-Based Animation System

Add realistic physics effects to sprite animations including gravity,
momentum, squash and stretch, spring dynamics, and particle effects.

Features:
- Gravity and projectile motion
- Momentum and inertia
- Squash and stretch deformation
- Spring and damping systems
- Collision response
- Particle effects integration
- Procedural secondary animation

Hardware Requirements:
- CPU: Any (all calculations are CPU-based)
- RAM: 4+ GB

Author: NeonWorks Team
License: MIT
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageTransform


@dataclass
class Vector2D:
    """2D vector for physics calculations."""

    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x / scalar, self.y / scalar)

    def magnitude(self) -> float:
        """Get vector length."""
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self) -> Vector2D:
        """Get unit vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return self / mag

    def dot(self, other: Vector2D) -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple."""
        return (self.x, self.y)


@dataclass
class PhysicsState:
    """Physical state of an object."""

    position: Vector2D = field(default_factory=Vector2D)
    velocity: Vector2D = field(default_factory=Vector2D)
    acceleration: Vector2D = field(default_factory=Vector2D)
    mass: float = 1.0
    drag: float = 0.0  # Air resistance (0-1)
    elasticity: float = 0.5  # Bounciness (0-1)
    angular_velocity: float = 0.0  # Radians per second
    rotation: float = 0.0  # Current rotation in radians

    def apply_force(self, force: Vector2D):
        """Apply force (F = ma)."""
        self.acceleration = self.acceleration + (force / self.mass)

    def update(self, dt: float):
        """Update physics (Euler integration)."""
        # Apply drag
        if self.drag > 0:
            drag_force = self.velocity * (-self.drag)
            self.apply_force(drag_force)

        # Update velocity
        self.velocity = self.velocity + self.acceleration * dt

        # Update position
        self.position = self.position + self.velocity * dt

        # Update rotation
        self.rotation += self.angular_velocity * dt

        # Reset acceleration (forces applied each frame)
        self.acceleration = Vector2D(0, 0)


@dataclass
class SquashStretchParams:
    """Parameters for squash and stretch deformation."""

    enabled: bool = True
    max_scale: float = 1.3  # Maximum stretch
    min_scale: float = 0.7  # Maximum squash
    preserve_volume: bool = True  # Preserve area during deformation
    speed_threshold: float = 5.0  # Min speed for effect
    direction_influence: float = 1.0  # How much velocity affects direction


@dataclass
class SpringSystem:
    """Spring-based secondary animation."""

    anchor: Vector2D = field(default_factory=Vector2D)
    position: Vector2D = field(default_factory=Vector2D)
    velocity: Vector2D = field(default_factory=Vector2D)

    stiffness: float = 100.0  # Spring constant (k)
    damping: float = 10.0  # Damping coefficient
    mass: float = 1.0

    def update(self, dt: float, target: Optional[Vector2D] = None):
        """
        Update spring simulation.

        Args:
            dt: Delta time
            target: Optional target position (overrides anchor)
        """
        if target is not None:
            self.anchor = target

        # Spring force: F = -k * displacement
        displacement = self.position - self.anchor
        spring_force = displacement * (-self.stiffness)

        # Damping force: F = -c * velocity
        damping_force = self.velocity * (-self.damping)

        # Total force
        total_force = spring_force + damping_force

        # Update velocity: a = F / m
        acceleration = total_force / self.mass
        self.velocity = self.velocity + acceleration * dt

        # Update position
        self.position = self.position + self.velocity * dt


class PhysicsAnimation:
    """
    Physics-based animation generator.

    Applies realistic physics effects to sprite animations.
    """

    def __init__(self, gravity: float = 980.0):  # pixels/s^2 (Earth-like)
        """
        Initialize physics animation system.

        Args:
            gravity: Gravity strength in pixels/second^2
        """
        self.gravity = gravity
        self.gravity_vector = Vector2D(0, gravity)

    def animate_jump(
        self,
        sprite: Image.Image,
        jump_velocity: float = 500.0,
        duration: float = 1.0,
        fps: int = 30,
        squash_stretch: bool = True,
    ) -> List[Image.Image]:
        """
        Generate jump animation with realistic physics.

        Args:
            sprite: Source sprite
            jump_velocity: Initial upward velocity (pixels/s)
            duration: Total duration in seconds
            fps: Frames per second
            squash_stretch: Apply squash and stretch

        Returns:
            List of animation frames
        """
        frames = []
        dt = 1.0 / fps
        num_frames = int(duration * fps)

        # Initialize physics state
        state = PhysicsState(
            position=Vector2D(sprite.width / 2, sprite.height / 2),
            velocity=Vector2D(0, -jump_velocity),
            mass=1.0,
            drag=0.1,
            elasticity=0.3,
        )

        ground_y = sprite.height / 2

        for i in range(num_frames):
            # Apply gravity
            state.apply_force(self.gravity_vector * state.mass)

            # Update physics
            state.update(dt)

            # Ground collision
            if state.position.y >= ground_y and state.velocity.y > 0:
                state.position.y = ground_y
                state.velocity.y *= -state.elasticity  # Bounce

                # Stop if bouncing is minimal
                if abs(state.velocity.y) < 10:
                    state.velocity.y = 0

            # Generate frame
            if squash_stretch:
                frame = self._apply_squash_stretch(sprite, state.velocity, SquashStretchParams())
            else:
                frame = sprite.copy()

            # Apply vertical offset based on position
            offset_y = int(ground_y - state.position.y)
            if offset_y != 0:
                frame = self._apply_offset(frame, 0, offset_y)

            frames.append(frame)

        return frames

    def animate_projectile(
        self,
        sprite: Image.Image,
        initial_velocity: Vector2D,
        duration: float = 2.0,
        fps: int = 30,
        rotation: bool = True,
    ) -> List[Tuple[Image.Image, Vector2D]]:
        """
        Generate projectile motion animation.

        Args:
            sprite: Source sprite
            initial_velocity: Initial velocity vector
            duration: Duration in seconds
            fps: Frames per second
            rotation: Rotate sprite to face velocity direction

        Returns:
            List of (frame, position) tuples
        """
        frames = []
        dt = 1.0 / fps
        num_frames = int(duration * fps)

        # Initialize physics
        state = PhysicsState(
            position=Vector2D(0, 0), velocity=initial_velocity, mass=1.0, drag=0.05
        )

        for i in range(num_frames):
            # Apply gravity
            state.apply_force(self.gravity_vector * state.mass)

            # Update physics
            state.update(dt)

            # Generate frame
            frame = sprite.copy()

            # Apply rotation if enabled
            if rotation and state.velocity.magnitude() > 0:
                angle = math.degrees(math.atan2(state.velocity.y, state.velocity.x))
                frame = frame.rotate(-angle, resample=Image.BICUBIC, expand=True)

            frames.append((frame, state.position))

        return frames

    def animate_bounce(
        self,
        sprite: Image.Image,
        bounce_height: float = 200.0,
        num_bounces: int = 5,
        fps: int = 30,
        squash_stretch: bool = True,
    ) -> List[Image.Image]:
        """
        Generate bouncing animation with diminishing returns.

        Args:
            sprite: Source sprite
            bounce_height: Initial bounce height in pixels
            num_bounces: Number of bounces
            fps: Frames per second
            squash_stretch: Apply squash and stretch

        Returns:
            List of animation frames
        """
        frames = []
        dt = 1.0 / fps

        # Calculate initial velocity needed for bounce height
        # v = sqrt(2 * g * h)
        initial_velocity = math.sqrt(2 * self.gravity * bounce_height)

        # Initialize physics
        state = PhysicsState(
            position=Vector2D(sprite.width / 2, 0),
            velocity=Vector2D(0, -initial_velocity),
            mass=1.0,
            elasticity=0.7,  # Energy retained per bounce
        )

        ground_y = 0
        bounces_count = 0
        is_grounded = False

        while bounces_count < num_bounces or not is_grounded:
            # Apply gravity
            state.apply_force(self.gravity_vector * state.mass)

            # Update physics
            state.update(dt)

            # Ground collision
            if state.position.y >= ground_y and state.velocity.y > 0:
                state.position.y = ground_y
                state.velocity.y *= -state.elasticity
                bounces_count += 1

                # Check if effectively stopped
                if abs(state.velocity.y) < 5:
                    is_grounded = True
                    state.velocity.y = 0

            # Generate frame
            if squash_stretch:
                frame = self._apply_squash_stretch(sprite, state.velocity, SquashStretchParams())
            else:
                frame = sprite.copy()

            # Apply vertical offset
            offset_y = int(-state.position.y)
            if offset_y != 0:
                frame = self._apply_offset(frame, 0, offset_y)

            frames.append(frame)

            # Prevent infinite loop
            if len(frames) > fps * 10:
                break

        return frames

    def animate_spring(
        self,
        sprite: Image.Image,
        displacement: Vector2D,
        duration: float = 2.0,
        fps: int = 30,
        stiffness: float = 200.0,
        damping: float = 15.0,
    ) -> List[Image.Image]:
        """
        Generate spring-based animation (wobble, overshoot, settle).

        Args:
            sprite: Source sprite
            displacement: Initial displacement from rest
            duration: Duration in seconds
            fps: Frames per second
            stiffness: Spring stiffness (higher = stiffer)
            damping: Damping coefficient (higher = less oscillation)

        Returns:
            List of animation frames
        """
        frames = []
        dt = 1.0 / fps
        num_frames = int(duration * fps)

        # Initialize spring system
        spring = SpringSystem(
            anchor=Vector2D(0, 0),
            position=displacement,
            velocity=Vector2D(0, 0),
            stiffness=stiffness,
            damping=damping,
        )

        for i in range(num_frames):
            # Update spring
            spring.update(dt)

            # Generate frame with offset
            offset_x = int(spring.position.x)
            offset_y = int(spring.position.y)

            frame = self._apply_offset(sprite, offset_x, offset_y)
            frames.append(frame)

        return frames

    def animate_swing(
        self,
        sprite: Image.Image,
        anchor_offset: Vector2D,
        max_angle: float = 30.0,
        period: float = 2.0,
        num_cycles: int = 3,
        fps: int = 30,
    ) -> List[Image.Image]:
        """
        Generate pendulum/swing animation.

        Args:
            sprite: Source sprite
            anchor_offset: Offset from sprite center to anchor point
            max_angle: Maximum swing angle in degrees
            period: Period of oscillation in seconds
            num_cycles: Number of swing cycles
            fps: Frames per second

        Returns:
            List of animation frames
        """
        frames = []
        dt = 1.0 / fps
        duration = period * num_cycles
        num_frames = int(duration * fps)

        max_angle_rad = math.radians(max_angle)
        omega = 2 * math.pi / period  # Angular frequency

        for i in range(num_frames):
            t = i * dt

            # Simple harmonic motion for angle
            angle = max_angle_rad * math.sin(omega * t)

            # Rotate sprite
            frame = sprite.rotate(-math.degrees(angle), resample=Image.BICUBIC, expand=True)

            # Calculate position offset due to pivot point
            # (This is simplified; proper pivot rotation is more complex)
            offset_x = int(anchor_offset.x * math.sin(angle))
            offset_y = int(anchor_offset.y * (1 - math.cos(angle)))

            frame = self._apply_offset(frame, offset_x, offset_y)
            frames.append(frame)

        return frames

    def _apply_squash_stretch(
        self, sprite: Image.Image, velocity: Vector2D, params: SquashStretchParams
    ) -> Image.Image:
        """
        Apply squash and stretch deformation based on velocity.

        Args:
            sprite: Source sprite
            velocity: Current velocity
            params: Squash/stretch parameters

        Returns:
            Deformed sprite
        """
        if not params.enabled:
            return sprite

        speed = velocity.magnitude()

        if speed < params.speed_threshold:
            return sprite

        # Calculate stretch factor based on speed
        # Normalize speed to 0-1 range
        speed_factor = min(speed / 1000.0, 1.0)

        # Calculate scale factors
        if params.preserve_volume:
            # Stretch in direction of motion, compress perpendicular
            stretch = 1.0 + (params.max_scale - 1.0) * speed_factor
            squash = 1.0 / stretch  # Preserve area: stretch * squash = 1
        else:
            stretch = 1.0 + (params.max_scale - 1.0) * speed_factor
            squash = 1.0 - (1.0 - params.min_scale) * speed_factor

        # Determine stretch direction
        if abs(velocity.x) > abs(velocity.y):
            # Horizontal motion: stretch horizontally
            scale_x = stretch
            scale_y = squash
        else:
            # Vertical motion: stretch vertically
            scale_x = squash
            scale_y = stretch

        # Apply transform
        width = int(sprite.width * scale_x)
        height = int(sprite.height * scale_y)

        deformed = sprite.resize((width, height), Image.BICUBIC)

        # Pad back to original size (centered)
        if deformed.size != sprite.size:
            padded = Image.new(sprite.mode, sprite.size, (0, 0, 0, 0))
            offset_x = (sprite.width - width) // 2
            offset_y = (sprite.height - height) // 2
            padded.paste(deformed, (offset_x, offset_y))
            return padded

        return deformed

    def _apply_offset(self, sprite: Image.Image, offset_x: int, offset_y: int) -> Image.Image:
        """Apply positional offset to sprite."""
        result = Image.new(sprite.mode, sprite.size, (0, 0, 0, 0))

        # Calculate paste position
        x = offset_x
        y = offset_y

        # Paste sprite at offset
        result.paste(sprite, (x, y), sprite if sprite.mode == "RGBA" else None)

        return result


class SecondaryAnimation:
    """
    Secondary animation effects (follow-through, overlapping action).

    Adds spring-based secondary motion to parts of sprites.
    """

    def __init__(self):
        """Initialize secondary animation system."""
        pass

    def add_follow_through(
        self, frames: List[Image.Image], delay_frames: int = 2, decay: float = 0.8
    ) -> List[Image.Image]:
        """
        Add follow-through effect to animation.

        Args:
            frames: Original animation frames
            delay_frames: Number of frames to delay secondary motion
            decay: How quickly secondary motion decays (0-1)

        Returns:
            Frames with follow-through effect
        """
        # This is a simplified implementation
        # Full implementation would track different sprite parts separately

        result_frames = []

        for i, frame in enumerate(frames):
            # Blend current frame with delayed frame
            if i >= delay_frames:
                delayed_frame = frames[i - delay_frames]

                # Blend
                blended = Image.blend(delayed_frame, frame, alpha=1.0 - decay)
                result_frames.append(blended)
            else:
                result_frames.append(frame.copy())

        return result_frames

    def add_overlap(self, frames: List[Image.Image], lag_pixels: int = 3) -> List[Image.Image]:
        """
        Add overlapping action (parts lag behind main motion).

        Args:
            frames: Original animation frames
            lag_pixels: Amount of lag in pixels

        Returns:
            Frames with overlapping action
        """
        result_frames = []

        for i, frame in enumerate(frames):
            # Apply slight horizontal offset that lags behind
            offset = lag_pixels if i > 0 else 0

            result = Image.new(frame.mode, frame.size, (0, 0, 0, 0))
            result.paste(frame, (offset, 0), frame if frame.mode == "RGBA" else None)

            result_frames.append(result)

        return result_frames


# Convenience functions


def create_jump_animation(
    sprite: Image.Image | str | Path, output_dir: Optional[str | Path] = None, **kwargs
) -> List[Image.Image]:
    """
    Quick jump animation creation.

    Args:
        sprite: Source sprite or path
        output_dir: Directory to save frames (optional)
        **kwargs: Parameters for animate_jump

    Returns:
        Animation frames
    """
    # Load sprite if path
    if isinstance(sprite, (str, Path)):
        sprite = Image.open(sprite)

    # Create animation
    physics = PhysicsAnimation()
    frames = physics.animate_jump(sprite, **kwargs)

    # Save if requested
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, frame in enumerate(frames):
            frame.save(output_dir / f"frame_{i:03d}.png")

        print(f"Saved {len(frames)} frames to {output_dir}")

    return frames


def create_bounce_animation(
    sprite: Image.Image | str | Path, output_dir: Optional[str | Path] = None, **kwargs
) -> List[Image.Image]:
    """
    Quick bounce animation creation.

    Args:
        sprite: Source sprite or path
        output_dir: Directory to save frames (optional)
        **kwargs: Parameters for animate_bounce

    Returns:
        Animation frames
    """
    # Load sprite if path
    if isinstance(sprite, (str, Path)):
        sprite = Image.open(sprite)

    # Create animation
    physics = PhysicsAnimation()
    frames = physics.animate_bounce(sprite, **kwargs)

    # Save if requested
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, frame in enumerate(frames):
            frame.save(output_dir / f"frame_{i:03d}.png")

        print(f"Saved {len(frames)} frames to {output_dir}")

    return frames


if __name__ == "__main__":
    print("Physics-Based Animation System - Example Usage\n")

    # Create test sprite
    test_sprite = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(test_sprite)
    draw.ellipse([12, 12, 52, 52], fill=(100, 150, 200, 255))

    # Create physics animator
    physics = PhysicsAnimation(gravity=980.0)

    # Generate jump animation
    print("Generating jump animation...")
    jump_frames = create_jump_animation(
        test_sprite, output_dir="test_jump", jump_velocity=400.0, duration=1.5, fps=30
    )

    # Generate bounce animation
    print("\nGenerating bounce animation...")
    bounce_frames = create_bounce_animation(
        test_sprite, output_dir="test_bounce", bounce_height=150.0, num_bounces=5, fps=30
    )

    # Generate spring animation
    print("\nGenerating spring animation...")
    spring_frames = physics.animate_spring(
        test_sprite,
        displacement=Vector2D(50, 0),
        duration=2.0,
        fps=30,
        stiffness=150.0,
        damping=12.0,
    )

    # Save spring animation
    output_dir = Path("test_spring")
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(spring_frames):
        frame.save(output_dir / f"frame_{i:03d}.png")

    print(f"\nSaved {len(spring_frames)} spring frames")
    print("\nExample complete!")
