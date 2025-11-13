"""
Particle System

Flexible particle system for visual effects like explosions, trails, smoke, etc.
Optimized with NumPy for batch particle updates.
"""

import pygame
import random
import math
import numpy as np
from typing import Tuple, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from engine.core.ecs import Component


class EmitterShape(Enum):
    """Particle emitter shapes"""

    POINT = "point"
    CIRCLE = "circle"
    CONE = "cone"
    BOX = "box"
    SPHERE = "sphere"


class ParticleBlendMode(Enum):
    """Particle blending modes"""

    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"


@dataclass
class Particle:
    """Single particle in the system"""

    # Position and velocity
    x: float = 0.0
    y: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    # Life
    lifetime: float = 1.0  # Total lifetime in seconds
    age: float = 0.0  # Current age in seconds
    is_alive: bool = True

    # Visual
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    size: float = 4.0
    rotation: float = 0.0
    rotation_speed: float = 0.0

    # Physics
    gravity_x: float = 0.0
    gravity_y: float = 0.0
    drag: float = 0.0

    def update(self, delta_time: float):
        """Update particle state"""
        if not self.is_alive:
            return

        # Update age
        self.age += delta_time
        if self.age >= self.lifetime:
            self.is_alive = False
            return

        # Apply gravity
        self.velocity_x += self.gravity_x * delta_time
        self.velocity_y += self.gravity_y * delta_time

        # Apply drag
        if self.drag > 0:
            drag_factor = 1.0 - (self.drag * delta_time)
            drag_factor = max(0.0, drag_factor)
            self.velocity_x *= drag_factor
            self.velocity_y *= drag_factor

        # Update position
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        # Update rotation
        self.rotation += self.rotation_speed * delta_time

    def get_life_progress(self) -> float:
        """Get life progress (0 = just born, 1 = about to die)"""
        if self.lifetime <= 0:
            return 1.0
        return min(1.0, self.age / self.lifetime)


@dataclass
class ParticleEmitter(Component):
    """
    Particle emitter component.

    Emits particles with configurable properties and behaviors.
    """

    # Position (world coordinates, if not attached to entity)
    x: float = 0.0
    y: float = 0.0

    # Emission
    emit_rate: float = 10.0  # Particles per second
    max_particles: int = 100
    auto_emit: bool = True
    is_emitting: bool = True
    burst_count: int = 0  # Emit this many particles immediately

    # Emitter shape
    shape: EmitterShape = EmitterShape.POINT
    shape_radius: float = 0.0  # For circle/sphere
    shape_width: float = 10.0  # For box/cone
    shape_height: float = 10.0  # For box
    shape_angle: float = 45.0  # For cone (degrees)

    # Particle properties
    particle_lifetime: float = 1.0
    particle_lifetime_variance: float = 0.2

    # Initial velocity
    initial_speed: float = 100.0
    initial_speed_variance: float = 20.0
    emission_angle: float = 0.0  # Degrees
    emission_spread: float = 360.0  # Degrees

    # Particle color
    start_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    end_color: Optional[Tuple[int, int, int, int]] = None

    # Particle size
    start_size: float = 4.0
    end_size: Optional[float] = None
    size_variance: float = 1.0

    # Particle rotation
    rotation_speed: float = 0.0
    rotation_speed_variance: float = 0.0

    # Physics
    gravity_x: float = 0.0
    gravity_y: float = 100.0  # Positive = down
    drag: float = 0.0

    # Rendering
    blend_mode: ParticleBlendMode = ParticleBlendMode.NORMAL
    texture: Optional[pygame.Surface] = None

    # Internal state
    particles: List[Particle] = field(default_factory=list)
    emission_accumulator: float = 0.0

    # Lifetime (emitter can have limited lifetime)
    emitter_lifetime: Optional[float] = None
    emitter_age: float = 0.0

    def emit_particle(self) -> Particle:
        """Create and emit a single particle"""
        # Determine spawn position based on shape
        spawn_x, spawn_y = self._get_spawn_position()

        # Determine velocity based on emission angle and spread
        angle_rad = math.radians(
            self.emission_angle
            + random.uniform(-self.emission_spread / 2, self.emission_spread / 2)
        )
        speed = self.initial_speed + random.uniform(
            -self.initial_speed_variance, self.initial_speed_variance
        )

        velocity_x = math.cos(angle_rad) * speed
        velocity_y = math.sin(angle_rad) * speed

        # Determine lifetime
        lifetime = self.particle_lifetime + random.uniform(
            -self.particle_lifetime_variance, self.particle_lifetime_variance
        )
        lifetime = max(0.1, lifetime)

        # Determine size
        size = self.start_size + random.uniform(-self.size_variance, self.size_variance)
        size = max(0.5, size)

        # Determine rotation speed
        rot_speed = self.rotation_speed + random.uniform(
            -self.rotation_speed_variance, self.rotation_speed_variance
        )

        # Create particle
        particle = Particle(
            x=self.x + spawn_x,
            y=self.y + spawn_y,
            velocity_x=velocity_x,
            velocity_y=velocity_y,
            lifetime=lifetime,
            color=self.start_color,
            size=size,
            rotation=random.uniform(0, 360),
            rotation_speed=rot_speed,
            gravity_x=self.gravity_x,
            gravity_y=self.gravity_y,
            drag=self.drag,
        )

        return particle

    def _get_spawn_position(self) -> Tuple[float, float]:
        """Get spawn position based on emitter shape"""
        if self.shape == EmitterShape.POINT:
            return (0.0, 0.0)

        elif self.shape == EmitterShape.CIRCLE:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, self.shape_radius)
            return (math.cos(angle) * radius, math.sin(angle) * radius)

        elif self.shape == EmitterShape.BOX:
            x = random.uniform(-self.shape_width / 2, self.shape_width / 2)
            y = random.uniform(-self.shape_height / 2, self.shape_height / 2)
            return (x, y)

        elif self.shape == EmitterShape.CONE:
            # Emit from a cone shape
            angle = random.uniform(-self.shape_angle / 2, self.shape_angle / 2)
            distance = random.uniform(0, self.shape_radius)
            angle_rad = math.radians(angle + self.emission_angle)
            return (math.cos(angle_rad) * distance, math.sin(angle_rad) * distance)

        else:
            return (0.0, 0.0)

    def burst(self, count: int):
        """Emit a burst of particles immediately"""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                particle = self.emit_particle()
                self.particles.append(particle)

    def start(self):
        """Start emitting particles"""
        self.is_emitting = True

    def stop(self):
        """Stop emitting particles"""
        self.is_emitting = False

    def clear(self):
        """Clear all particles"""
        self.particles.clear()


class ParticleSystem:
    """
    System that updates and manages particle emitters.
    Optimized with NumPy for batch particle updates.
    """

    def __init__(self, use_vectorized: bool = True):
        self.emitters: List[ParticleEmitter] = []
        self.use_vectorized = use_vectorized  # Enable NumPy batch processing

    def add_emitter(self, emitter: ParticleEmitter):
        """Add emitter to system"""
        if emitter not in self.emitters:
            self.emitters.append(emitter)

    def remove_emitter(self, emitter: ParticleEmitter):
        """Remove emitter from system"""
        if emitter in self.emitters:
            self.emitters.remove(emitter)

    def update(self, delta_time: float):
        """Update all particle emitters"""
        for emitter in self.emitters[:]:  # Copy list to allow removal
            # Update emitter lifetime
            if emitter.emitter_lifetime is not None:
                emitter.emitter_age += delta_time
                if emitter.emitter_age >= emitter.emitter_lifetime:
                    emitter.is_emitting = False

            # Emit new particles
            if emitter.is_emitting and emitter.auto_emit:
                emitter.emission_accumulator += emitter.emit_rate * delta_time

                while (
                    emitter.emission_accumulator >= 1.0
                    and len(emitter.particles) < emitter.max_particles
                ):
                    particle = emitter.emit_particle()
                    emitter.particles.append(particle)
                    emitter.emission_accumulator -= 1.0

            # Handle burst
            if emitter.burst_count > 0:
                emitter.burst(emitter.burst_count)
                emitter.burst_count = 0

            # Update existing particles
            if self.use_vectorized and len(emitter.particles) > 10:
                # Use vectorized update for better performance with many particles
                self._update_particles_vectorized(emitter, delta_time)
            else:
                # Use standard update for few particles
                for particle in emitter.particles[:]:  # Copy to allow removal
                    particle.update(delta_time)

                    # Apply color interpolation
                    if emitter.end_color is not None:
                        progress = particle.get_life_progress()
                        particle.color = self._interpolate_color(
                            emitter.start_color, emitter.end_color, progress
                        )

                    # Apply size interpolation
                    if emitter.end_size is not None:
                        progress = particle.get_life_progress()
                        particle.size = (
                            emitter.start_size
                            + (emitter.end_size - emitter.start_size) * progress
                        )

                    # Remove dead particles
                    if not particle.is_alive:
                        emitter.particles.remove(particle)

            # Remove emitter if it's done and has no particles
            if emitter.emitter_lifetime is not None:
                if (
                    emitter.emitter_age >= emitter.emitter_lifetime
                    and len(emitter.particles) == 0
                ):
                    self.remove_emitter(emitter)

    def _update_particles_vectorized(self, emitter: ParticleEmitter, delta_time: float):
        """
        Vectorized particle update using NumPy for better performance.
        Updates all particles in a single batch operation.
        """
        if not emitter.particles:
            return

        n = len(emitter.particles)

        # Extract particle data into NumPy arrays
        ages = np.array([p.age for p in emitter.particles], dtype=np.float32)
        lifetimes = np.array([p.lifetime for p in emitter.particles], dtype=np.float32)
        x = np.array([p.x for p in emitter.particles], dtype=np.float32)
        y = np.array([p.y for p in emitter.particles], dtype=np.float32)
        vx = np.array([p.velocity_x for p in emitter.particles], dtype=np.float32)
        vy = np.array([p.velocity_y for p in emitter.particles], dtype=np.float32)
        gx = np.array([p.gravity_x for p in emitter.particles], dtype=np.float32)
        gy = np.array([p.gravity_y for p in emitter.particles], dtype=np.float32)
        drags = np.array([p.drag for p in emitter.particles], dtype=np.float32)
        rotations = np.array([p.rotation for p in emitter.particles], dtype=np.float32)
        rot_speeds = np.array(
            [p.rotation_speed for p in emitter.particles], dtype=np.float32
        )

        # Update ages
        ages += delta_time
        alive_mask = ages < lifetimes

        # Apply gravity
        vx += gx * delta_time
        vy += gy * delta_time

        # Apply drag
        drag_factor = np.maximum(0.0, 1.0 - drags * delta_time)
        vx *= drag_factor
        vy *= drag_factor

        # Update positions
        x += vx * delta_time
        y += vy * delta_time

        # Update rotations
        rotations += rot_speeds * delta_time

        # Calculate life progress for interpolations
        progress = np.clip(ages / np.maximum(lifetimes, 0.001), 0.0, 1.0)

        # Apply updates back to particles and remove dead ones
        alive_particles = []
        for i, particle in enumerate(emitter.particles):
            if alive_mask[i]:
                particle.age = float(ages[i])
                particle.x = float(x[i])
                particle.y = float(y[i])
                particle.velocity_x = float(vx[i])
                particle.velocity_y = float(vy[i])
                particle.rotation = float(rotations[i])
                particle.is_alive = True

                # Apply color interpolation
                if emitter.end_color is not None:
                    t = float(progress[i])
                    particle.color = self._interpolate_color(
                        emitter.start_color, emitter.end_color, t
                    )

                # Apply size interpolation
                if emitter.end_size is not None:
                    t = float(progress[i])
                    particle.size = (
                        emitter.start_size + (emitter.end_size - emitter.start_size) * t
                    )

                alive_particles.append(particle)
            else:
                particle.is_alive = False

        emitter.particles = alive_particles

    def _interpolate_color(
        self, start: Tuple[int, int, int, int], end: Tuple[int, int, int, int], t: float
    ) -> Tuple[int, int, int, int]:
        """Interpolate between two colors"""
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        a = int(start[3] + (end[3] - start[3]) * t)
        return (r, g, b, a)


class ParticleRenderer:
    """
    Renders particles to screen.
    """

    def __init__(self):
        self.draw_count = 0

    def render(self, screen: pygame.Surface, emitter: ParticleEmitter, camera=None):
        """
        Render particles from an emitter.

        Args:
            screen: Surface to render to
            emitter: Particle emitter to render
            camera: Optional camera for world-to-screen conversion
        """
        self.draw_count = 0

        for particle in emitter.particles:
            if not particle.is_alive:
                continue

            # Convert world to screen coordinates
            if camera:
                screen_x, screen_y = camera.world_to_screen(particle.x, particle.y)
            else:
                screen_x, screen_y = int(particle.x), int(particle.y)

            # Skip if off-screen
            if screen_x < -100 or screen_x > screen.get_width() + 100:
                continue
            if screen_y < -100 or screen_y > screen.get_height() + 100:
                continue

            # Render particle
            if emitter.texture:
                self._render_textured_particle(
                    screen, particle, screen_x, screen_y, emitter.texture
                )
            else:
                self._render_circle_particle(screen, particle, screen_x, screen_y)

            self.draw_count += 1

    def _render_circle_particle(
        self, screen: pygame.Surface, particle: Particle, x: int, y: int
    ):
        """Render particle as colored circle"""
        size = int(particle.size)
        if size < 1:
            size = 1

        # Create surface for particle with alpha
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, particle.color, (size, size), size)

        # Blit to screen
        screen.blit(particle_surface, (x - size, y - size))

    def _render_textured_particle(
        self,
        screen: pygame.Surface,
        particle: Particle,
        x: int,
        y: int,
        texture: pygame.Surface,
    ):
        """Render particle with texture"""
        # Scale texture to particle size
        size = int(particle.size * 2)
        if size < 1:
            size = 1

        scaled_texture = pygame.transform.scale(texture, (size, size))

        # Apply rotation
        if particle.rotation != 0:
            scaled_texture = pygame.transform.rotate(scaled_texture, -particle.rotation)

        # Apply color tint
        scaled_texture = scaled_texture.copy()
        scaled_texture.fill(particle.color[:3], special_flags=pygame.BLEND_MULT)

        # Apply alpha
        scaled_texture.set_alpha(particle.color[3])

        # Blit to screen
        rect = scaled_texture.get_rect(center=(x, y))
        screen.blit(scaled_texture, rect)


class ParticlePresets:
    """Pre-configured particle emitter presets"""

    @staticmethod
    def explosion(x: float, y: float) -> ParticleEmitter:
        """Create explosion effect"""
        return ParticleEmitter(
            x=x,
            y=y,
            emit_rate=0,  # Burst only
            burst_count=50,
            auto_emit=False,
            max_particles=50,
            particle_lifetime=1.0,
            particle_lifetime_variance=0.3,
            initial_speed=200.0,
            initial_speed_variance=100.0,
            emission_angle=0,
            emission_spread=360,
            start_color=(255, 200, 50, 255),
            end_color=(255, 50, 0, 0),
            start_size=8.0,
            end_size=2.0,
            gravity_y=50,
            drag=2.0,
            emitter_lifetime=1.5,
        )

    @staticmethod
    def smoke(x: float, y: float) -> ParticleEmitter:
        """Create smoke effect"""
        return ParticleEmitter(
            x=x,
            y=y,
            emit_rate=20,
            max_particles=100,
            particle_lifetime=2.0,
            particle_lifetime_variance=0.5,
            initial_speed=30.0,
            initial_speed_variance=15.0,
            emission_angle=-90,  # Up
            emission_spread=30,
            start_color=(100, 100, 100, 200),
            end_color=(50, 50, 50, 0),
            start_size=6.0,
            end_size=12.0,
            gravity_y=-20,  # Float up
            drag=0.5,
        )

    @staticmethod
    def fire(x: float, y: float) -> ParticleEmitter:
        """Create fire effect"""
        return ParticleEmitter(
            x=x,
            y=y,
            emit_rate=30,
            max_particles=100,
            particle_lifetime=0.8,
            particle_lifetime_variance=0.2,
            initial_speed=50.0,
            initial_speed_variance=25.0,
            emission_angle=-90,  # Up
            emission_spread=20,
            start_color=(255, 150, 0, 255),
            end_color=(255, 0, 0, 0),
            start_size=8.0,
            end_size=2.0,
            gravity_y=-50,  # Float up
            drag=0.3,
        )

    @staticmethod
    def sparks(x: float, y: float) -> ParticleEmitter:
        """Create sparks effect"""
        return ParticleEmitter(
            x=x,
            y=y,
            emit_rate=0,
            burst_count=30,
            auto_emit=False,
            max_particles=30,
            particle_lifetime=0.5,
            particle_lifetime_variance=0.2,
            initial_speed=300.0,
            initial_speed_variance=150.0,
            emission_angle=0,
            emission_spread=360,
            start_color=(255, 255, 100, 255),
            end_color=(255, 100, 0, 0),
            start_size=3.0,
            end_size=1.0,
            gravity_y=400,
            drag=3.0,
            emitter_lifetime=1.0,
        )

    @staticmethod
    def trail(x: float, y: float, angle: float = 0) -> ParticleEmitter:
        """Create trail effect (for moving objects)"""
        return ParticleEmitter(
            x=x,
            y=y,
            emit_rate=50,
            max_particles=50,
            particle_lifetime=0.5,
            particle_lifetime_variance=0.1,
            initial_speed=0,
            initial_speed_variance=10,
            emission_angle=angle + 180,  # Trail behind
            emission_spread=10,
            start_color=(100, 200, 255, 200),
            end_color=(50, 100, 200, 0),
            start_size=5.0,
            end_size=1.0,
            gravity_y=0,
            drag=1.0,
        )

    @staticmethod
    def heal(x: float, y: float) -> ParticleEmitter:
        """Create healing effect"""
        return ParticleEmitter(
            x=x,
            y=y,
            emit_rate=20,
            max_particles=50,
            particle_lifetime=1.5,
            particle_lifetime_variance=0.3,
            initial_speed=40.0,
            initial_speed_variance=20.0,
            emission_angle=-90,  # Up
            emission_spread=30,
            start_color=(50, 255, 100, 255),
            end_color=(100, 255, 150, 0),
            start_size=4.0,
            end_size=8.0,
            gravity_y=-30,  # Float up
            drag=0.5,
            emitter_lifetime=2.0,
        )
