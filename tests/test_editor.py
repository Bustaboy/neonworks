"""
Comprehensive tests for Editor module

Tests AI-assisted level building, navmesh generation, and writing tools.
"""

from unittest.mock import Mock, patch
import pytest

from neonworks.core.ecs import World, Entity, GridPosition, Building, Navmesh
from neonworks.editor.ai_level_builder import (
    AILevelBuilder,
    PlacementSuggestion,
    PlacementPriority,
)
from neonworks.editor.ai_navmesh import AINavmeshGenerator, NavmeshConfig
from neonworks.editor.ai_writer import (
    AIWritingAssistant,
    DialogLine,
    DialogChoice,
    DialogTone,
    QuestType,
    QuestTemplate,
)


# ===========================
# AILevelBuilder Tests
# ===========================


class TestAILevelBuilder:
    """Test AI-assisted level building"""

    def test_level_builder_creation(self):
        """Test creating level builder"""
        builder = AILevelBuilder(grid_width=100, grid_height=100)

        assert builder.grid_width == 100
        assert builder.grid_height == 100
        assert len(builder.occupied_cells) == 0

    def test_suggest_spawn_points_two_players(self):
        """Test spawn point suggestions for 2 players"""
        builder = AILevelBuilder(grid_width=100, grid_height=100)

        suggestions = builder.suggest_spawn_points(num_players=2)

        assert len(suggestions) == 2
        assert all(isinstance(s, PlacementSuggestion) for s in suggestions)
        assert all(s.object_type.startswith("spawn_point_player_") for s in suggestions)

        # Should be far apart
        pos1 = (suggestions[0].x, suggestions[0].y)
        pos2 = (suggestions[1].x, suggestions[1].y)
        distance = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        assert distance > 50  # Should be reasonably far apart

    def test_suggest_spawn_points_four_players(self):
        """Test spawn point suggestions for 4 players"""
        builder = AILevelBuilder(grid_width=100, grid_height=100)

        suggestions = builder.suggest_spawn_points(num_players=4)

        assert len(suggestions) == 4
        # Should be in corners with offset
        for suggestion in suggestions:
            assert 0 < suggestion.x < 100
            assert 0 < suggestion.y < 100

    def test_spawn_point_properties(self):
        """Test spawn point suggestion properties"""
        builder = AILevelBuilder(grid_width=100, grid_height=100)

        suggestions = builder.suggest_spawn_points(num_players=2)

        for suggestion in suggestions:
            assert suggestion.priority == PlacementPriority.CRITICAL
            assert 0.0 <= suggestion.score <= 1.0
            assert len(suggestion.reason) > 0
            assert isinstance(suggestion.object_type, str)

    def test_occupied_cells_tracking(self):
        """Test tracking occupied cells"""
        builder = AILevelBuilder(grid_width=100, grid_height=100)

        # Mark some cells as occupied
        builder.occupied_cells.add((10, 10))
        builder.occupied_cells.add((20, 20))

        assert (10, 10) in builder.occupied_cells
        assert (20, 20) in builder.occupied_cells
        assert (15, 15) not in builder.occupied_cells


# ===========================
# AINavmeshGenerator Tests
# ===========================


class TestNavmeshConfig:
    """Test NavmeshConfig"""

    def test_config_defaults(self):
        """Test default configuration"""
        config = NavmeshConfig()

        assert config.detect_buildings
        assert config.detect_terrain
        assert config.auto_detect_chokepoints
        assert config.auto_detect_cover
        assert config.expand_walkable_areas

    def test_config_custom(self):
        """Test custom configuration"""
        config = NavmeshConfig(
            detect_buildings=False, auto_detect_chokepoints=False, expansion_passes=5
        )

        assert not config.detect_buildings
        assert not config.auto_detect_chokepoints
        assert config.expansion_passes == 5

    def test_terrain_cost_multipliers(self):
        """Test terrain cost multipliers"""
        config = NavmeshConfig()

        assert "floor" in config.terrain_cost_multipliers
        assert "grass" in config.terrain_cost_multipliers
        assert config.terrain_cost_multipliers["road"] < 1.0  # Faster
        assert config.terrain_cost_multipliers["mud"] > 1.0  # Slower


class TestAINavmeshGenerator:
    """Test AI navmesh generation"""

    def test_generator_creation(self):
        """Test creating navmesh generator"""
        generator = AINavmeshGenerator()

        assert generator.config is not None
        assert isinstance(generator.config, NavmeshConfig)

    def test_generator_with_custom_config(self):
        """Test generator with custom config"""
        config = NavmeshConfig(detect_buildings=False)
        generator = AINavmeshGenerator(config=config)

        assert not generator.config.detect_buildings

    def test_generate_basic_navmesh(self):
        """Test basic navmesh generation"""
        world = World()
        generator = AINavmeshGenerator()

        navmesh = generator.generate(world, grid_width=10, grid_height=10)

        assert isinstance(navmesh, Navmesh)
        # Initially all cells should be walkable
        assert len(navmesh.walkable_cells) > 0

    def test_generate_with_obstacles(self):
        """Test navmesh generation with obstacles"""
        world = World()

        # Add some buildings as obstacles
        building1 = world.create_entity()
        building1.add_component(GridPosition(grid_x=5, grid_y=5))
        building1.add_component(Building())

        building2 = world.create_entity()
        building2.add_component(GridPosition(grid_x=6, grid_y=5))
        building2.add_component(Building())

        config = NavmeshConfig(detect_buildings=True)
        generator = AINavmeshGenerator(config=config)

        navmesh = generator.generate(world, grid_width=10, grid_height=10)

        # Building cells should not be walkable
        assert (5, 5) not in navmesh.walkable_cells
        assert (6, 5) not in navmesh.walkable_cells

    def test_cost_multipliers(self):
        """Test movement cost multipliers"""
        world = World()
        generator = AINavmeshGenerator()

        navmesh = generator.generate(world, grid_width=10, grid_height=10)

        # All cells should have cost multipliers
        for cell in navmesh.walkable_cells:
            assert cell in navmesh.cost_multipliers
            assert navmesh.cost_multipliers[cell] >= 0.0


# ===========================
# AIWritingAssistant Tests
# ===========================


class TestDialogLine:
    """Test DialogLine"""

    def test_dialog_line_creation(self):
        """Test creating dialog line"""
        line = DialogLine(
            speaker="Hero", text="Hello, friend!", tone=DialogTone.FRIENDLY
        )

        assert line.speaker == "Hero"
        assert line.text == "Hello, friend!"
        assert line.tone == DialogTone.FRIENDLY
        assert line.choices == []

    def test_dialog_line_with_choices(self):
        """Test dialog line with choices"""
        choice1 = DialogChoice(text="Tell me more", leads_to="node_2")
        choice2 = DialogChoice(text="Goodbye", leads_to="end")

        line = DialogLine(
            speaker="NPC",
            text="What would you like to know?",
            tone=DialogTone.NEUTRAL,
            choices=[choice1, choice2],
        )

        assert len(line.choices) == 2
        assert line.choices[0].text == "Tell me more"


class TestDialogChoice:
    """Test DialogChoice"""

    def test_dialog_choice_creation(self):
        """Test creating dialog choice"""
        choice = DialogChoice(text="Accept quest", leads_to="quest_start")

        assert choice.text == "Accept quest"
        assert choice.leads_to == "quest_start"
        assert choice.requirements == {}

    def test_dialog_choice_with_requirements(self):
        """Test choice with requirements"""
        choice = DialogChoice(
            text="Use persuasion",
            leads_to="success",
            requirements={"charisma": 5, "has_item": "silver_tongue"},
        )

        assert choice.requirements["charisma"] == 5
        assert choice.requirements["has_item"] == "silver_tongue"


class TestQuestTemplate:
    """Test QuestTemplate"""

    def test_quest_template_creation(self):
        """Test creating quest template"""
        quest = QuestTemplate(
            title="Lost Item",
            description="Find the merchant's lost amulet",
            quest_type=QuestType.FETCH_QUEST,
            objectives=["Search the forest", "Return the amulet"],
            rewards={"gold": 100, "xp": 50},
            dialog_intro="Please help me find my amulet!",
            dialog_completion="Thank you so much!",
            suggested_location="Dark Forest",
            difficulty="Easy",
        )

        assert quest.title == "Lost Item"
        assert quest.quest_type == QuestType.FETCH_QUEST
        assert len(quest.objectives) == 2
        assert quest.rewards["gold"] == 100
        assert quest.difficulty == "Easy"


class TestAIWritingAssistant:
    """Test AI writing assistant"""

    def test_writing_assistant_creation(self):
        """Test creating writing assistant"""
        assistant = AIWritingAssistant(game_theme="cyberpunk")

        assert assistant.game_theme == "cyberpunk"
        assert isinstance(assistant.character_voices, dict)

    def test_writing_assistant_fantasy_theme(self):
        """Test writing assistant with fantasy theme"""
        assistant = AIWritingAssistant(game_theme="fantasy")

        assert assistant.game_theme == "fantasy"

    def test_character_voice_tracking(self):
        """Test tracking character personalities"""
        assistant = AIWritingAssistant()

        # Add character voice
        assistant.character_voices["Hero"] = {
            "personality": "brave",
            "speech_pattern": "direct",
        }

        assert "Hero" in assistant.character_voices
        assert assistant.character_voices["Hero"]["personality"] == "brave"

    def test_theme_vocabulary(self):
        """Test theme-specific vocabulary"""
        assistant = AIWritingAssistant(game_theme="cyberpunk")

        assert "cyberpunk" in assistant.theme_vocabulary
        assert isinstance(assistant.theme_vocabulary["cyberpunk"], dict)


# ===========================
# Integration Tests
# ===========================


class TestEditorIntegration:
    """Integration tests for editor tools"""

    def test_level_building_workflow(self):
        """Test complete level building workflow"""
        # Create builder
        builder = AILevelBuilder(grid_width=50, grid_height=50)

        # Get spawn points
        spawn_suggestions = builder.suggest_spawn_points(num_players=2)
        assert len(spawn_suggestions) == 2

        # Mark spawn points as occupied
        for suggestion in spawn_suggestions:
            builder.occupied_cells.add((suggestion.x, suggestion.y))

        # Verify they're tracked
        assert len(builder.occupied_cells) == 2

    def test_navmesh_with_level_builder(self):
        """Test using navmesh with level builder"""
        world = World()
        builder = AILevelBuilder(grid_width=20, grid_height=20)

        # Place some obstacles
        obstacle1 = world.create_entity()
        obstacle1.add_component(GridPosition(grid_x=10, grid_y=10))
        obstacle1.add_component(Building())

        # Generate navmesh
        generator = AINavmeshGenerator()
        navmesh = generator.generate(world, grid_width=20, grid_height=20)

        # Obstacle should not be walkable
        assert (10, 10) not in navmesh.walkable_cells

    def test_quest_and_dialog_workflow(self):
        """Test quest creation with dialog"""
        assistant = AIWritingAssistant(game_theme="fantasy")

        # Create quest template
        quest = QuestTemplate(
            title="Dragon Slayer",
            description="Defeat the dragon terrorizing the village",
            quest_type=QuestType.COMBAT_QUEST,
            objectives=["Find dragon lair", "Defeat dragon", "Return to village"],
            rewards={"gold": 1000, "xp": 500, "item": "dragon_scale_armor"},
            dialog_intro="A dragon has been attacking our village!",
            dialog_completion="You saved us! You're a true hero!",
            suggested_location="Mountain Peak",
            difficulty="Hard",
        )

        # Create dialog for quest
        intro_line = DialogLine(
            speaker="Village Elder",
            text=quest.dialog_intro,
            tone=DialogTone.DESPERATE,
            choices=[
                DialogChoice(text="I'll help you", leads_to="accept"),
                DialogChoice(text="Not my problem", leads_to="decline"),
            ],
        )

        assert intro_line.speaker == "Village Elder"
        assert len(intro_line.choices) == 2
        assert quest.quest_type == QuestType.COMBAT_QUEST

    def test_complete_level_design_workflow(self):
        """Test complete level design workflow"""
        world = World()

        # 1. Create level layout
        builder = AILevelBuilder(grid_width=30, grid_height=30)

        # 2. Place spawn points
        spawns = builder.suggest_spawn_points(num_players=4)
        for spawn in spawns:
            builder.occupied_cells.add((spawn.x, spawn.y))

        # 3. Place buildings
        for i in range(5):
            building = world.create_entity()
            building.add_component(GridPosition(grid_x=10 + i, grid_y=15))
            building.add_component(Building())

        # 4. Generate navmesh
        generator = AINavmeshGenerator()
        navmesh = generator.generate(world, grid_width=30, grid_height=30)

        # 5. Create quest
        assistant = AIWritingAssistant()
        quest = QuestTemplate(
            title="Test Quest",
            description="A test quest",
            quest_type=QuestType.EXPLORATION,
            objectives=["Explore the area"],
            rewards={"xp": 100},
            dialog_intro="Please explore!",
            dialog_completion="Well done!",
            suggested_location="Test Area",
            difficulty="Easy",
        )

        # Verify workflow completed
        assert len(spawns) == 4
        assert len(builder.occupied_cells) == 4
        assert isinstance(navmesh, Navmesh)
        assert quest.title == "Test Quest"
