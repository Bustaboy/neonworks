"""
Comprehensive tests for Particle System

Tests particles, emitters, rendering, and presets.
"""

import pytest
import pygame
from unittest.mock import Mock, MagicMock
from neonworks.rendering.particles import (
    Particle,
    ParticleEmitter,
    ParticleSystem,
    ParticleRenderer,
    ParticlePresets,
    EmitterShape,
    ParticleBlendMode
)
from neonworks.rendering.camera import Camera


@pytest.fixture
def screen():
    """Create a test screen surface"""
    pygame.init()
    return pygame.Surface((800, 600))


@pytest.fixture
def camera():
    """Create a test camera"""
    return Camera(screen_width=800, screen_height=600)


class TestParticle:
    """Test Particle class"""

    def test_particle_creation(self):
        """Test creating a particle"""
        particle = Particle(x=100, y=200, lifetime=2.0)

        assert particle.x == 100
        assert particle.y == 200
        assert particle.lifetime == 2.0
        assert particle.is_alive

    def test_particle_defaults(self):
        """Test default particle values"""
        particle = Particle()

        assert particle.lifetime == 1.0
        assert particle.age == 0.0
        assert particle.is_alive
        assert particle.size == 4.0

    def test_particle_update_position(self):
        """Test particle position updates with velocity"""
        particle = Particle(x=0, y=0, velocity_x=100, velocity_y=50)

        particle.update(0.1)  # 0.1 seconds

        assert particle.x == 10  # 100 * 0.1
        assert particle.y == 5  # 50 * 0.1

    def test_particle_update_age(self):
        """Test particle age increases"""
        particle = Particle(lifetime=2.0)

        particle.update(0.5)

        assert particle.age == 0.5
        assert particle.is_alive

    def test_particle_dies_after_lifetime(self):
        """Test particle dies after lifetime expires"""
        particle = Particle(lifetime=1.0)

        particle.update(1.5)

        assert not particle.is_alive

    def test_particle_gravity(self):
        """Test gravity affects particle velocity"""
        particle = Particle(velocity_y=0, gravity_y=100)

        particle.update(0.1)

        # Velocity should increase by gravity * time
        assert particle.velocity_y == 10  # 100 * 0.1

    def test_particle_drag(self):
        """Test drag slows particle"""
        particle = Particle(velocity_x=100, drag=5.0)

        particle.update(0.1)

        # Velocity should decrease due to drag
        assert particle.velocity_x < 100

    def test_particle_rotation(self):
        """Test particle rotation"""
        particle = Particle(rotation=0, rotation_speed=90, lifetime=2.0)

        particle.update(1.0)

        assert particle.rotation == 90

    def test_get_life_progress(self):
        """Test life progress calculation"""
        particle = Particle(lifetime=2.0, age=1.0)

        progress = particle.get_life_progress()

        assert progress == 0.5


class TestParticleEmitter:
    """Test ParticleEmitter class"""

    def test_emitter_creation(self):
        """Test creating emitter"""
        emitter = ParticleEmitter(x=100, y=200)

        assert emitter.x == 100
        assert emitter.y == 200
        assert emitter.is_emitting

    def test_emitter_defaults(self):
        """Test default emitter values"""
        emitter = ParticleEmitter()

        assert emitter.emit_rate == 10.0
        assert emitter.max_particles == 100
        assert emitter.auto_emit
        assert emitter.shape == EmitterShape.POINT

    def test_emit_single_particle(self):
        """Test emitting a single particle"""
        emitter = ParticleEmitter(x=100, y=200)

        particle = emitter.emit_particle()

        assert particle.x == 100
        assert particle.y == 200
        assert particle.is_alive

    def test_emit_particle_with_speed(self):
        """Test particle has initial velocity"""
        emitter = ParticleEmitter(
            initial_speed=100,
            initial_speed_variance=0,
            emission_angle=0,
            emission_spread=0
        )

        particle = emitter.emit_particle()

        # Should have velocity in direction of emission angle (exactly 100 with no variance)
        assert abs(particle.velocity_x - 100) < 1

    def test_burst(self):
        """Test burst emission"""
        emitter = ParticleEmitter()

        emitter.burst(10)

        assert len(emitter.particles) == 10

    def test_burst_respects_max_particles(self):
        """Test burst doesn't exceed max particles"""
        emitter = ParticleEmitter(max_particles=5)

        emitter.burst(10)

        assert len(emitter.particles) == 5

    def test_start_stop_emitting(self):
        """Test starting and stopping emission"""
        emitter = ParticleEmitter()

        emitter.stop()
        assert not emitter.is_emitting

        emitter.start()
        assert emitter.is_emitting

    def test_clear_particles(self):
        """Test clearing all particles"""
        emitter = ParticleEmitter()
        emitter.burst(10)

        emitter.clear()

        assert len(emitter.particles) == 0

    def test_emitter_shape_point(self):
        """Test point emitter spawns at origin"""
        emitter = ParticleEmitter(shape=EmitterShape.POINT)

        spawn_x, spawn_y = emitter._get_spawn_position()

        assert spawn_x == 0
        assert spawn_y == 0

    def test_emitter_shape_circle(self):
        """Test circle emitter spawns within radius"""
        emitter = ParticleEmitter(shape=EmitterShape.CIRCLE, shape_radius=50)

        spawn_x, spawn_y = emitter._get_spawn_position()

        # Should be within radius
        distance = (spawn_x ** 2 + spawn_y ** 2) ** 0.5
        assert distance <= 50

    def test_emitter_shape_box(self):
        """Test box emitter spawns within box"""
        emitter = ParticleEmitter(shape=EmitterShape.BOX, shape_width=100, shape_height=100)

        spawn_x, spawn_y = emitter._get_spawn_position()

        # Should be within box bounds
        assert -50 <= spawn_x <= 50
        assert -50 <= spawn_y <= 50

    def test_particle_lifetime_variance(self):
        """Test particles have varying lifetimes"""
        emitter = ParticleEmitter(
            particle_lifetime=2.0,
            particle_lifetime_variance=1.0
        )

        lifetimes = set()
        for _ in range(10):
            particle = emitter.emit_particle()
            lifetimes.add(particle.lifetime)

        # Should have variation
        assert len(lifetimes) > 1

    def test_particle_color(self):
        """Test particles get start color"""
        emitter = ParticleEmitter(start_color=(255, 0, 0, 255))

        particle = emitter.emit_particle()

        assert particle.color == (255, 0, 0, 255)


class TestParticleSystem:
    """Test ParticleSystem class"""

    def test_system_creation(self):
        """Test creating particle system"""
        system = ParticleSystem()

        assert len(system.emitters) == 0

    def test_add_emitter(self):
        """Test adding emitter to system"""
        system = ParticleSystem()
        emitter = ParticleEmitter()

        system.add_emitter(emitter)

        assert len(system.emitters) == 1

    def test_remove_emitter(self):
        """Test removing emitter from system"""
        system = ParticleSystem()
        emitter = ParticleEmitter()

        system.add_emitter(emitter)
        system.remove_emitter(emitter)

        assert len(system.emitters) == 0

    def test_update_emits_particles(self):
        """Test update emits particles over time"""
        system = ParticleSystem()
        emitter = ParticleEmitter(emit_rate=10, auto_emit=True)
        system.add_emitter(emitter)

        # Update for 1 second
        system.update(1.0)

        # Should have emitted ~10 particles
        assert len(emitter.particles) > 0

    def test_update_respects_max_particles(self):
        """Test system respects max particle limit"""
        system = ParticleSystem()
        emitter = ParticleEmitter(emit_rate=100, max_particles=10)
        system.add_emitter(emitter)

        system.update(1.0)

        assert len(emitter.particles) <= 10

    def test_update_removes_dead_particles(self):
        """Test dead particles are removed"""
        system = ParticleSystem()
        emitter = ParticleEmitter(particle_lifetime=0.1)
        system.add_emitter(emitter)

        emitter.burst(10)

        # Update past lifetime
        system.update(1.0)

        # All particles should be dead and removed
        assert len(emitter.particles) == 0

    def test_color_interpolation(self):
        """Test particles interpolate color over lifetime"""
        system = ParticleSystem()
        emitter = ParticleEmitter(
            start_color=(255, 0, 0, 255),
            end_color=(0, 0, 255, 255),
            particle_lifetime=1.0
        )
        system.add_emitter(emitter)

        emitter.burst(1)
        particle = emitter.particles[0]

        # At start
        assert particle.color == (255, 0, 0, 255)

        # Halfway through life
        particle.age = 0.5
        system.update(0.01)

        # Should be between red and blue
        assert 0 < particle.color[0] < 255
        assert 0 < particle.color[2] < 255

    def test_size_interpolation(self):
        """Test particles interpolate size over lifetime"""
        system = ParticleSystem()
        emitter = ParticleEmitter(
            start_size=10.0,
            end_size=2.0,
            particle_lifetime=1.0
        )
        system.add_emitter(emitter)

        emitter.burst(1)
        particle = emitter.particles[0]

        initial_size = particle.size

        # Halfway through life
        particle.age = 0.5
        system.update(0.01)

        # Size should have decreased
        assert particle.size < initial_size

    def test_emitter_lifetime(self):
        """Test emitter stops after lifetime"""
        system = ParticleSystem()
        emitter = ParticleEmitter(emitter_lifetime=1.0)
        system.add_emitter(emitter)

        # Update past lifetime
        system.update(2.0)

        assert not emitter.is_emitting

    def test_emitter_removed_after_lifetime_and_no_particles(self):
        """Test emitter is removed when done"""
        system = ParticleSystem()
        emitter = ParticleEmitter(
            emitter_lifetime=0.1,
            particle_lifetime=0.1
        )
        system.add_emitter(emitter)

        # Update past both lifetimes
        system.update(1.0)

        # Emitter should be removed
        assert len(system.emitters) == 0

    def test_burst_count(self):
        """Test burst_count triggers burst"""
        system = ParticleSystem()
        emitter = ParticleEmitter(burst_count=10, auto_emit=False)
        system.add_emitter(emitter)

        system.update(0.1)

        assert len(emitter.particles) == 10
        assert emitter.burst_count == 0  # Reset after burst


class TestParticleRenderer:
    """Test ParticleRenderer class"""

    def test_renderer_creation(self):
        """Test creating renderer"""
        renderer = ParticleRenderer()

        assert renderer.draw_count == 0

    def test_render_particles(self, screen):
        """Test rendering particles"""
        renderer = ParticleRenderer()
        emitter = ParticleEmitter()
        emitter.burst(10)

        renderer.render(screen, emitter)

        assert renderer.draw_count == 10

    def test_render_with_camera(self, screen, camera):
        """Test rendering with camera"""
        renderer = ParticleRenderer()
        emitter = ParticleEmitter(x=400, y=300)
        emitter.burst(5)

        renderer.render(screen, emitter, camera)

        # Should render particles (camera at center)
        assert renderer.draw_count == 5

    def test_render_skips_dead_particles(self, screen):
        """Test dead particles are not rendered"""
        renderer = ParticleRenderer()
        emitter = ParticleEmitter()
        emitter.burst(10)

        # Kill some particles
        for i in range(5):
            emitter.particles[i].is_alive = False

        renderer.render(screen, emitter)

        assert renderer.draw_count == 5

    def test_render_skips_offscreen_particles(self, screen):
        """Test off-screen particles are culled"""
        renderer = ParticleRenderer()
        emitter = ParticleEmitter()

        # Create particles far off screen
        for _ in range(5):
            particle = Particle(x=10000, y=10000)
            emitter.particles.append(particle)

        renderer.render(screen, emitter)

        # Should cull off-screen particles
        assert renderer.draw_count == 0


class TestParticlePresets:
    """Test ParticlePresets"""

    def test_explosion_preset(self):
        """Test explosion preset"""
        emitter = ParticlePresets.explosion(100, 200)

        assert emitter.x == 100
        assert emitter.y == 200
        assert emitter.burst_count > 0
        assert emitter.emitter_lifetime is not None

    def test_smoke_preset(self):
        """Test smoke preset"""
        emitter = ParticlePresets.smoke(100, 200)

        assert emitter.x == 100
        assert emitter.auto_emit
        assert emitter.gravity_y < 0  # Floats up

    def test_fire_preset(self):
        """Test fire preset"""
        emitter = ParticlePresets.fire(100, 200)

        assert emitter.auto_emit
        assert emitter.gravity_y < 0  # Floats up

    def test_sparks_preset(self):
        """Test sparks preset"""
        emitter = ParticlePresets.sparks(100, 200)

        assert emitter.burst_count > 0
        assert emitter.gravity_y > 0  # Falls down

    def test_trail_preset(self):
        """Test trail preset"""
        emitter = ParticlePresets.trail(100, 200, angle=45)

        assert emitter.auto_emit
        assert emitter.particle_lifetime < 1.0  # Short lived

    def test_heal_preset(self):
        """Test heal preset"""
        emitter = ParticlePresets.heal(100, 200)

        assert emitter.auto_emit
        assert emitter.emitter_lifetime is not None


class TestParticleIntegration:
    """Integration tests for particle system"""

    def test_full_particle_lifecycle(self):
        """Test complete particle lifecycle"""
        system = ParticleSystem()
        emitter = ParticleEmitter(
            emit_rate=10,
            particle_lifetime=0.5,
            particle_lifetime_variance=0,  # No variance for predictable test
            auto_emit=True
        )
        system.add_emitter(emitter)

        # Emit particles
        system.update(0.1)
        assert len(emitter.particles) > 0

        # Particles age
        system.update(0.3)
        assert all(p.age > 0 for p in emitter.particles)

        # Particles die
        system.update(0.5)
        # All particles should be removed by now (0.1 + 0.3 + 0.5 = 0.9s, lifetime = 0.5s)
        assert len(emitter.particles) == 0

    def test_explosion_effect(self, screen):
        """Test explosion effect works end-to-end"""
        system = ParticleSystem()
        renderer = ParticleRenderer()

        emitter = ParticlePresets.explosion(400, 300)
        system.add_emitter(emitter)

        # Initial burst
        system.update(0.01)
        assert len(emitter.particles) > 0

        # Render
        renderer.render(screen, emitter)
        assert renderer.draw_count > 0

        # Particles fade out
        system.update(2.0)
        assert len(emitter.particles) == 0

    def test_continuous_emission(self):
        """Test continuous particle emission"""
        system = ParticleSystem()
        emitter = ParticleEmitter(
            emit_rate=30,
            max_particles=50,
            particle_lifetime=2.0
        )
        system.add_emitter(emitter)

        # Run for a while
        for _ in range(10):
            system.update(0.1)

        # Should have active particles
        assert len(emitter.particles) > 0
        # Should not exceed max
        assert len(emitter.particles) <= 50

    def test_multiple_emitters(self):
        """Test multiple emitters in one system"""
        system = ParticleSystem()

        emitter1 = ParticleEmitter(x=100, y=100, auto_emit=False, particle_lifetime=10.0)
        emitter2 = ParticleEmitter(x=200, y=200, auto_emit=False, particle_lifetime=10.0)

        system.add_emitter(emitter1)
        system.add_emitter(emitter2)

        emitter1.burst(10)
        emitter2.burst(10)

        system.update(0.1)

        # All particles should still be alive (long lifetime, no auto emit)
        assert len(emitter1.particles) == 10
        assert len(emitter2.particles) == 10


# Run tests with: pytest engine/tests/test_particles.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
