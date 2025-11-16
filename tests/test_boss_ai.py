"""
Tests for Boss AI System

Tests the multi-phase boss battle system including phase transitions,
stat changes, AI modifications, and add summoning.
"""

import pytest

from neonworks.core.ecs import World
from neonworks.core.events import Event, EventManager, EventType
from neonworks.gameplay.combat import Health
from neonworks.gameplay.jrpg_combat import BattleAI, BossPhase, JRPGStats, MagicPoints, SpellList
from neonworks.systems.boss_ai import BOSS_TEMPLATES, BossAISystem, create_boss_entity


class TestBossAISystem:
    """Test suite for BossAISystem"""

    def test_init(self, event_manager):
        """Test BossAISystem initialization"""
        system = BossAISystem(event_manager)

        assert system.event_manager is event_manager
        assert system.priority == 35
        assert system.active_bosses == {}

    def test_register_boss(self, world, event_manager):
        """Test registering a boss for AI processing"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        boss.add_component(BossPhase(current_phase=1, max_phases=2, phase_triggers=[50.0]))

        system.register_boss(boss)

        assert boss.id in system.active_bosses
        assert system.active_bosses[boss.id] == boss

    def test_register_boss_without_boss_phase(self, world, event_manager):
        """Test registering a boss without BossPhase component (should not register)"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")

        system.register_boss(boss)

        assert boss.id not in system.active_bosses

    def test_unregister_boss(self, world, event_manager):
        """Test unregistering a boss"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        boss.add_component(BossPhase(current_phase=1, max_phases=2, phase_triggers=[50.0]))

        system.register_boss(boss)
        assert boss.id in system.active_bosses

        system.unregister_boss(boss.id)
        assert boss.id not in system.active_bosses

    def test_unregister_nonexistent_boss(self, event_manager):
        """Test unregistering a boss that doesn't exist (should not raise error)"""
        system = BossAISystem(event_manager)

        # Should not raise an error
        system.unregister_boss("nonexistent_id")

    def test_update_with_no_bosses(self, world, event_manager):
        """Test update with no active bosses"""
        system = BossAISystem(event_manager)

        # Should not raise an error
        system.update(world, 0.016)

    def test_check_phase_transitions_no_transition(self, world, event_manager):
        """Test phase transition check when boss HP is above threshold"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        boss.add_component(Health(hp=100, max_hp=100))
        boss.add_component(BossPhase(current_phase=1, max_phases=2, phase_triggers=[50.0]))

        system.register_boss(boss)
        system.update(world, 0.016)

        # Boss should still be in phase 1
        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.current_phase == 1

    def test_check_phase_transitions_with_transition(self, world, event_manager):
        """Test phase transition when boss HP drops below threshold"""
        from neonworks.core.events import EventType

        # Set immediate mode for synchronous event processing
        event_manager.set_immediate_mode(True)

        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        boss.add_component(Health(hp=40, max_hp=100))  # 40% HP
        boss.add_component(BossPhase(
            current_phase=1,
            max_phases=2,
            phase_triggers=[50.0],
            phases={
                1: {"name": "Phase 1"},
                2: {"name": "Phase 2"}
            }
        ))

        # Track events
        events_received = []
        def track_event(event):
            if event.data.get("type") == "boss_phase_change":
                events_received.append(event)
        event_manager.subscribe(EventType.CUSTOM, track_event)

        system.register_boss(boss)
        system.update(world, 0.016)

        # Boss should transition to phase 2
        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.current_phase == 2

        # Event should have been emitted
        assert len(events_received) > 0

    def test_phase_transition_with_dead_boss(self, world, event_manager):
        """Test that dead bosses don't trigger phase transitions"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        boss.add_component(Health(hp=0, max_hp=100, is_alive=False))  # Dead boss
        boss.add_component(BossPhase(current_phase=1, max_phases=2, phase_triggers=[50.0]))

        system.register_boss(boss)
        system.update(world, 0.016)

        # Boss should still be in phase 1 (no transition for dead bosses)
        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.current_phase == 1

    def test_trigger_phase_transition_emits_event(self, world, event_manager):
        """Test that phase transitions emit events"""
        from neonworks.core.events import EventType

        event_manager.set_immediate_mode(True)

        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        boss_phase = BossPhase(
            current_phase=1,
            max_phases=2,
            phase_triggers=[50.0],
            phases={
                1: {"name": "Phase 1"},
                2: {"name": "Phase 2", "dialogue": "Phase 2!"}
            }
        )
        boss.add_component(boss_phase)

        events_received = []
        def capture_event(event):
            if event.data.get("type") == "boss_phase_change":
                events_received.append(event)
        event_manager.subscribe(EventType.CUSTOM, capture_event)

        system._trigger_phase_transition(world, boss, boss_phase)

        assert len(events_received) == 1
        event_data = events_received[0].data
        assert event_data["type"] == "boss_phase_change"
        assert event_data["boss_id"] == boss.id
        assert event_data["old_phase"] == 1
        assert event_data["new_phase"] == 2

    def test_apply_phase_changes_stat_changes(self, world, event_manager):
        """Test applying stat changes during phase transition"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        stats = JRPGStats(attack=10, defense=10)
        boss.add_component(stats)

        phase_data = {
            "stat_changes": {
                "attack": 5,
                "defense": 3
            }
        }

        system._apply_phase_changes(world, boss, phase_data)

        assert stats.attack == 15
        assert stats.defense == 13

    def test_apply_phase_changes_ai_changes(self, world, event_manager):
        """Test applying AI changes during phase transition"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        ai = BattleAI(ai_type="boss", attack_pattern=["attack"], preferred_spells=[])
        boss.add_component(ai)

        phase_data = {
            "ai_changes": {
                "attack_pattern": ["spell", "spell", "attack"],
                "preferred_spells": ["fireball", "lightning"]
            }
        }

        system._apply_phase_changes(world, boss, phase_data)

        assert ai.attack_pattern == ["spell", "spell", "attack"]
        assert ai.preferred_spells == ["fireball", "lightning"]

    def test_apply_phase_changes_heal(self, world, event_manager):
        """Test healing during phase transition"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        health = Health(hp=50, max_hp=100)
        boss.add_component(health)

        phase_data = {
            "heal_percentage": 20.0  # Heal 20% of max HP
        }

        system._apply_phase_changes(world, boss, phase_data)

        # Should heal 20% of 100 = 20 HP, so 50 + 20 = 70
        assert health.hp == 70

    def test_apply_phase_changes_heal_cap_at_max(self, world, event_manager):
        """Test that healing doesn't exceed max HP"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")
        health = Health(hp=95, max_hp=100)
        boss.add_component(health)

        phase_data = {
            "heal_percentage": 20.0  # Would heal to 115, but should cap at 100
        }

        system._apply_phase_changes(world, boss, phase_data)

        assert health.hp == 100

    def test_apply_phase_changes_summon_enemies(self, world, event_manager):
        """Test summoning adds during phase transition"""
        from neonworks.core.events import EventType

        event_manager.set_immediate_mode(True)

        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")

        events_received = []
        def capture_event(event):
            if event.data.get("type") == "boss_summon_add":
                events_received.append(event)
        event_manager.subscribe(EventType.CUSTOM, capture_event)

        phase_data = {
            "summon_enemies": [
                {"enemy_id": "skeleton", "level": 5, "position": 0},
                {"enemy_id": "skeleton", "level": 5, "position": 2}
            ]
        }

        system._apply_phase_changes(world, boss, phase_data)

        # Should emit 2 summon events
        assert len(events_received) == 2
        assert events_received[0].data["enemy_id"] == "skeleton"
        assert events_received[0].data["level"] == 5
        assert events_received[0].data["position"] == 0

    def test_summon_adds(self, world, event_manager):
        """Test summoning adds emits correct events"""
        from neonworks.core.events import EventType

        event_manager.set_immediate_mode(True)

        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")

        events_received = []
        def capture_event(event):
            if event.data.get("type") == "boss_summon_add":
                events_received.append(event)
        event_manager.subscribe(EventType.CUSTOM, capture_event)

        add_data = [
            {"enemy_id": "goblin", "level": 3, "position": 1},
            {"enemy_id": "orc", "level": 5, "position": 3}
        ]

        system._summon_adds(world, boss, add_data)

        assert len(events_received) == 2
        assert events_received[0].data["enemy_id"] == "goblin"
        assert events_received[0].data["level"] == 3
        assert events_received[1].data["enemy_id"] == "orc"
        assert events_received[1].data["level"] == 5

    def test_create_boss_template_default(self, event_manager):
        """Test creating a default boss template"""
        system = BossAISystem(event_manager)
        template = system.create_boss_template("test_boss", "Test Boss")

        assert template["boss_id"] == "test_boss"
        assert template["name"] == "Test Boss"
        assert template["max_phases"] == 2
        assert len(template["phase_triggers"]) == 1
        assert template["phase_triggers"][0] == 70.0
        assert 1 in template["phases"]
        assert 2 in template["phases"]

    def test_create_boss_template_three_phases(self, event_manager):
        """Test creating a boss template with 3 phases"""
        system = BossAISystem(event_manager)
        template = system.create_boss_template("test_boss", "Test Boss", phases=3)

        assert template["max_phases"] == 3
        assert len(template["phase_triggers"]) == 2
        assert template["phase_triggers"] == [70.0, 40.0]
        assert 1 in template["phases"]
        assert 2 in template["phases"]
        assert 3 in template["phases"]

    def test_create_boss_template_four_phases(self, event_manager):
        """Test creating a boss template with 4 phases"""
        system = BossAISystem(event_manager)
        template = system.create_boss_template("test_boss", "Test Boss", phases=4)

        assert template["max_phases"] == 4
        assert len(template["phase_triggers"]) == 3
        assert template["phase_triggers"] == [70.0, 40.0, 15.0]


class TestCreateBossEntity:
    """Test suite for create_boss_entity function"""

    def test_create_basic_boss(self, world):
        """Test creating a basic boss entity"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        assert boss is not None
        assert boss.has_tag("enemy")
        assert boss.has_tag("boss")

    def test_boss_has_required_components(self, world):
        """Test that created boss has all required components"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        # Check for required components
        from neonworks.core.ecs import Transform, GridPosition, Sprite
        from neonworks.gameplay.jrpg_combat import EnemyData, BattleRewards

        assert boss.has_component(Transform)
        assert boss.has_component(GridPosition)
        assert boss.has_component(Sprite)
        assert boss.has_component(Health)
        assert boss.has_component(MagicPoints)
        assert boss.has_component(JRPGStats)
        assert boss.has_component(BossPhase)
        assert boss.has_component(BattleAI)
        assert boss.has_component(SpellList)
        assert boss.has_component(EnemyData)
        assert boss.has_component(BattleRewards)

    def test_boss_stats_scale_with_level(self, world):
        """Test that boss stats scale with level"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss_low = create_boss_entity(world, template, level=5)
        boss_high = create_boss_entity(world, template, level=15)

        health_low = boss_low.get_component(Health)
        health_high = boss_high.get_component(Health)

        # Higher level boss should have more HP
        assert health_high.max_hp > health_low.max_hp

        stats_low = boss_low.get_component(JRPGStats)
        stats_high = boss_high.get_component(JRPGStats)

        # Higher level boss should have better stats
        assert stats_high.attack > stats_low.attack
        assert stats_high.defense > stats_low.defense

    def test_boss_phase_component(self, world):
        """Test that boss has correct phase configuration"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.current_phase == 1
        assert boss_phase.max_phases == 2
        assert boss_phase.phase_triggers == [50.0]

    def test_boss_initial_ai_from_phase_1(self, world):
        """Test that boss AI is initialized from phase 1 data"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        ai = boss.get_component(BattleAI)
        phase_1_data = template["phases"][1]

        assert ai.ai_type == "boss"
        assert ai.attack_pattern == phase_1_data["attack_pattern"]
        assert ai.preferred_spells == phase_1_data["preferred_spells"]

    def test_boss_spell_list_includes_all_phases(self, world):
        """Test that boss spell list includes spells from all phases"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        spell_list = boss.get_component(SpellList)

        # Should have spells from both phase 1 and phase 2
        all_spells = set()
        for phase_data in template["phases"].values():
            all_spells.update(phase_data.get("preferred_spells", []))

        assert set(spell_list.learned_spells) == all_spells

    def test_boss_rewards_scale_with_level(self, world):
        """Test that boss rewards scale with level"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss_low = create_boss_entity(world, template, level=5)
        boss_high = create_boss_entity(world, template, level=15)

        from neonworks.gameplay.jrpg_combat import BattleRewards

        rewards_low = boss_low.get_component(BattleRewards)
        rewards_high = boss_high.get_component(BattleRewards)

        assert rewards_high.experience > rewards_low.experience
        assert rewards_high.gold > rewards_low.gold

    def test_boss_cannot_escape_from(self, world):
        """Test that boss battles cannot be escaped from"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        from neonworks.gameplay.jrpg_combat import EnemyData

        enemy_data = boss.get_component(EnemyData)
        assert enemy_data.is_boss is True
        assert enemy_data.can_escape_from is False

    def test_dragon_boss_creation(self, world):
        """Test creating the dragon boss with 3 phases"""
        template = BOSS_TEMPLATES["dragon"]
        boss = create_boss_entity(world, template, level=20)

        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.max_phases == 3
        assert len(boss_phase.phase_triggers) == 2
        assert boss_phase.phase_triggers == [66.0, 33.0]

    def test_dark_sorcerer_boss_creation(self, world):
        """Test creating the dark sorcerer boss with 3 phases"""
        template = BOSS_TEMPLATES["dark_sorcerer"]
        boss = create_boss_entity(world, template, level=15)

        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.max_phases == 3
        assert len(boss_phase.phase_triggers) == 2
        assert boss_phase.phase_triggers == [75.0, 40.0]


class TestBossTemplates:
    """Test suite for predefined boss templates"""

    def test_skeleton_king_template_structure(self):
        """Test skeleton king template has correct structure"""
        template = BOSS_TEMPLATES["skeleton_king"]

        assert template["boss_id"] == "skeleton_king"
        assert template["name"] == "Skeleton King"
        assert template["max_phases"] == 2
        assert 1 in template["phases"]
        assert 2 in template["phases"]

    def test_dragon_template_structure(self):
        """Test dragon template has correct structure"""
        template = BOSS_TEMPLATES["dragon"]

        assert template["boss_id"] == "dragon"
        assert template["name"] == "Ancient Dragon"
        assert template["max_phases"] == 3
        assert 1 in template["phases"]
        assert 2 in template["phases"]
        assert 3 in template["phases"]

    def test_dark_sorcerer_template_structure(self):
        """Test dark sorcerer template has correct structure"""
        template = BOSS_TEMPLATES["dark_sorcerer"]

        assert template["boss_id"] == "dark_sorcerer"
        assert template["name"] == "Dark Sorcerer"
        assert template["max_phases"] == 3

    def test_all_templates_have_required_fields(self):
        """Test that all boss templates have required fields"""
        required_fields = ["boss_id", "name", "max_phases", "phase_triggers", "phases"]

        for template_name, template in BOSS_TEMPLATES.items():
            for field in required_fields:
                assert field in template, f"{template_name} missing {field}"

    def test_phase_triggers_match_phase_count(self):
        """Test that phase triggers align with phase count"""
        for template_name, template in BOSS_TEMPLATES.items():
            max_phases = template["max_phases"]
            trigger_count = len(template["phase_triggers"])

            # Should have (max_phases - 1) triggers
            assert trigger_count == max_phases - 1, \
                f"{template_name} has {max_phases} phases but {trigger_count} triggers"


class TestBossAIIntegration:
    """Integration tests for boss AI system"""

    def test_full_boss_battle_phase_transition(self, world, event_manager):
        """Test a complete boss battle with phase transition"""
        from neonworks.core.events import EventType

        event_manager.set_immediate_mode(True)

        # Create boss
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        # Create AI system
        system = BossAISystem(event_manager)
        system.register_boss(boss)

        # Track events
        phase_changes = []
        def track_phase_change(event):
            if event.data.get("type") == "boss_phase_change":
                phase_changes.append(event)
        event_manager.subscribe(EventType.CUSTOM, track_phase_change)

        # Boss starts at full HP in phase 1
        health = boss.get_component(Health)
        boss_phase = boss.get_component(BossPhase)
        assert boss_phase.current_phase == 1

        # Damage boss to trigger phase 2 (50% HP threshold)
        health.hp = int(health.max_hp * 0.4)  # 40% HP

        # Update system to check for phase transition
        system.update(world, 0.016)

        # Boss should transition to phase 2
        assert boss_phase.current_phase == 2
        assert len(phase_changes) == 1

    def test_boss_removal_after_death(self, world, event_manager):
        """Test that dead bosses can be unregistered"""
        template = BOSS_TEMPLATES["skeleton_king"]
        boss = create_boss_entity(world, template, level=10)

        system = BossAISystem(event_manager)
        system.register_boss(boss)

        # Kill the boss
        health = boss.get_component(Health)
        health.hp = 0

        # Unregister
        system.unregister_boss(boss.id)
        assert boss.id not in system.active_bosses

    def test_multiple_bosses_simultaneously(self, world, event_manager):
        """Test managing multiple bosses at once"""
        system = BossAISystem(event_manager)

        # Create multiple bosses
        boss1 = create_boss_entity(world, BOSS_TEMPLATES["skeleton_king"], level=10)
        boss2 = create_boss_entity(world, BOSS_TEMPLATES["dragon"], level=15)

        system.register_boss(boss1)
        system.register_boss(boss2)

        assert len(system.active_bosses) == 2
        assert boss1.id in system.active_bosses
        assert boss2.id in system.active_bosses

        # Update should handle both
        system.update(world, 0.016)

    def test_boss_phase_transition_with_all_changes(self, world, event_manager):
        """Test phase transition that applies stat changes, AI changes, and healing"""
        system = BossAISystem(event_manager)
        boss = world.create_entity("TestBoss")

        # Add components
        health = Health(hp=40, max_hp=100)
        stats = JRPGStats(attack=10, defense=10)
        ai = BattleAI(ai_type="boss", attack_pattern=["attack"], preferred_spells=[])
        boss_phase = BossPhase(
            current_phase=1,
            max_phases=2,
            phase_triggers=[50.0],
            phases={
                1: {"name": "Phase 1"},
                2: {
                    "name": "Phase 2",
                    "stat_changes": {"attack": 5, "defense": 3},
                    "ai_changes": {
                        "attack_pattern": ["spell", "attack"],
                        "preferred_spells": ["fireball"]
                    },
                    "heal_percentage": 25.0
                }
            }
        )

        boss.add_component(health)
        boss.add_component(stats)
        boss.add_component(ai)
        boss.add_component(boss_phase)

        system.register_boss(boss)

        # Trigger transition
        system.update(world, 0.016)

        # Check all changes were applied
        assert boss_phase.current_phase == 2
        assert stats.attack == 15  # 10 + 5
        assert stats.defense == 13  # 10 + 3
        assert ai.attack_pattern == ["spell", "attack"]
        assert ai.preferred_spells == ["fireball"]
        assert health.hp == 65  # 40 + 25% of 100
