"""
Comprehensive test suite for dialogue.py (Dialogue & Choice System)

Tests cover:
- Dialogue node creation and branching
- Dialogue options with requirements
- Skill/attribute checks (Persuade, Intimidate, Technical)
- Choice consequences (faction rep, quest progress)
- Dialogue history tracking
- Multiple conversation paths
- Failed skill checks
- Repeatable vs one-time dialogues
- Integration with faction and quest systems
- Serialization for save/load
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestDialogueNodes:
    """Test dialogue node creation."""

    def test_create_dialogue_node(self):
        """Test creating a dialogue node."""
        from dialogue import DialogueNode

        node = DialogueNode(
            node_id="greeting_1",
            speaker="NPC Name",
            text="Hello, stranger.",
            options=[]
        )

        assert node.node_id == "greeting_1"
        assert node.speaker == "NPC Name"
        assert node.text == "Hello, stranger."

    def test_dialogue_node_with_options(self):
        """Test dialogue node with response options."""
        from dialogue import DialogueNode, DialogueOption

        option1 = DialogueOption("opt1", "Who are you?", next_node="info_1")
        option2 = DialogueOption("opt2", "Goodbye.", next_node="end")

        node = DialogueNode(
            node_id="greeting",
            speaker="Stranger",
            text="Greetings.",
            options=[option1, option2]
        )

        assert len(node.options) == 2
        assert node.options[0].text == "Who are you?"

    def test_terminal_dialogue_node(self):
        """Test dialogue node with no options (conversation end)."""
        from dialogue import DialogueNode

        node = DialogueNode(
            node_id="end",
            speaker="NPC",
            text="Farewell.",
            options=[]
        )

        assert len(node.options) == 0
        assert node.is_terminal()


class TestDialogueOptions:
    """Test dialogue option creation and requirements."""

    def test_create_simple_option(self):
        """Test creating simple dialogue option."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="opt1",
            text="Tell me more.",
            next_node="info_1"
        )

        assert option.option_id == "opt1"
        assert option.text == "Tell me more."
        assert option.next_node == "info_1"

    def test_option_with_skill_requirement(self):
        """Test option requiring skill check."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="persuade_1",
            text="[Persuade] Let me help you.",
            next_node="success",
            requirement_type="skill",
            requirement_value={"skill": "cool", "level": 5}
        )

        assert option.requirement_type == "skill"
        assert option.requirement_value["skill"] == "cool"

    def test_option_with_attribute_requirement(self):
        """Test option requiring attribute level."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="tech_1",
            text="[Tech] I can fix that.",
            next_node="tech_success",
            requirement_type="attribute",
            requirement_value={"attribute": "tech", "level": 8}
        )

        assert option.requirement_type == "attribute"

    def test_option_with_item_requirement(self):
        """Test option requiring item in inventory."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="show_pass",
            text="[Show Access Pass]",
            next_node="granted",
            requirement_type="item",
            requirement_value={"item_id": "access_pass"}
        )

        assert option.requirement_type == "item"

    def test_option_with_faction_requirement(self):
        """Test option requiring faction reputation."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="militech_option",
            text="[Militech] We have a deal.",
            next_node="militech_path",
            requirement_type="faction",
            requirement_value={"faction": "militech", "min_rep": 50}
        )

        assert option.requirement_type == "faction"


class TestSkillChecks:
    """Test skill/attribute checks for dialogue options."""

    def test_check_skill_requirement_pass(self):
        """Test passing skill check."""
        from dialogue import DialogueOption, DialogueManager

        manager = DialogueManager()

        option = DialogueOption(
            option_id="persuade",
            text="[Persuade] Trust me.",
            next_node="success",
            requirement_type="skill",
            requirement_value={"skill": "cool", "level": 5}
        )

        # Player has Cool 7
        player_stats = {"cool": 7}

        can_select = manager.check_option_available(option, player_stats)

        assert can_select is True

    def test_check_skill_requirement_fail(self):
        """Test failing skill check."""
        from dialogue import DialogueOption, DialogueManager

        manager = DialogueManager()

        option = DialogueOption(
            option_id="persuade",
            text="[Persuade] Trust me.",
            next_node="success",
            requirement_type="skill",
            requirement_value={"skill": "cool", "level": 8}
        )

        # Player has Cool 3 (too low)
        player_stats = {"cool": 3}

        can_select = manager.check_option_available(option, player_stats)

        assert can_select is False

    def test_check_attribute_requirement(self):
        """Test checking attribute requirement."""
        from dialogue import DialogueOption, DialogueManager

        manager = DialogueManager()

        option = DialogueOption(
            option_id="tech",
            text="[Tech] Bypass security.",
            next_node="hacked",
            requirement_type="attribute",
            requirement_value={"attribute": "tech", "level": 6}
        )

        player_stats = {"tech": 6}

        assert manager.check_option_available(option, player_stats) is True

    def test_check_multiple_requirements(self):
        """Test option with multiple requirements."""
        from dialogue import DialogueOption, DialogueManager

        manager = DialogueManager()

        option = DialogueOption(
            option_id="complex",
            text="[Tech + Cool] Impressive hack.",
            next_node="double_success",
            requirement_type="multiple",
            requirement_value={
                "requirements": [
                    {"type": "attribute", "attribute": "tech", "level": 5},
                    {"type": "attribute", "attribute": "cool", "level": 5}
                ]
            }
        )

        # Player has both
        player_stats = {"tech": 6, "cool": 7}

        assert manager.check_option_available(option, player_stats) is True


class TestChoiceConsequences:
    """Test consequences of dialogue choices."""

    def test_choice_grants_reputation(self):
        """Test choice that gives faction reputation."""
        from dialogue import DialogueNode, DialogueOption

        option = DialogueOption(
            option_id="help_militech",
            text="I'll help Militech.",
            next_node="militech_thanks",
            consequences=[
                {"type": "faction_rep", "faction": "militech", "amount": 25}
            ]
        )

        assert len(option.consequences) == 1
        assert option.consequences[0]["type"] == "faction_rep"

    def test_choice_removes_reputation(self):
        """Test choice that removes faction reputation."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="betray_militech",
            text="Betray Militech.",
            next_node="militech_angry",
            consequences=[
                {"type": "faction_rep", "faction": "militech", "amount": -50},
                {"type": "faction_rep", "faction": "syndicate", "amount": 25}
            ]
        )

        assert len(option.consequences) == 2

    def test_choice_advances_quest(self):
        """Test choice that advances quest."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="accept_quest",
            text="I'll do it.",
            next_node="quest_accepted",
            consequences=[
                {"type": "quest_progress", "quest_id": "main_2", "action": "activate"}
            ]
        )

        assert option.consequences[0]["type"] == "quest_progress"

    def test_choice_gives_item(self):
        """Test choice that gives item."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="take_reward",
            text="Thanks for the reward.",
            next_node="end",
            consequences=[
                {"type": "give_item", "item_id": "access_pass", "quantity": 1}
            ]
        )

        assert option.consequences[0]["type"] == "give_item"

    def test_choice_removes_item(self):
        """Test choice that removes item."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="hand_over",
            text="Here's the data chip.",
            next_node="thanks",
            consequences=[
                {"type": "remove_item", "item_id": "data_chip", "quantity": 1}
            ]
        )

        assert option.consequences[0]["type"] == "remove_item"

    def test_choice_gives_credits(self):
        """Test choice that gives credits."""
        from dialogue import DialogueOption

        option = DialogueOption(
            option_id="payment",
            text="I'll take the credits.",
            next_node="paid",
            consequences=[
                {"type": "give_credits", "amount": 1000}
            ]
        )

        assert option.consequences[0]["amount"] == 1000


class TestDialogueManager:
    """Test dialogue manager."""

    def test_create_dialogue_manager(self):
        """Test creating dialogue manager."""
        from dialogue import DialogueManager

        manager = DialogueManager()

        assert manager is not None

    def test_start_conversation(self):
        """Test starting a conversation."""
        from dialogue import DialogueManager, DialogueNode

        manager = DialogueManager()

        greeting = DialogueNode(
            node_id="greeting",
            speaker="Vendor",
            text="What do you want?",
            options=[]
        )

        manager.add_node(greeting)
        manager.start_conversation("greeting")

        assert manager.current_node.node_id == "greeting"

    def test_select_dialogue_option(self):
        """Test selecting a dialogue option."""
        from dialogue import DialogueManager, DialogueNode, DialogueOption

        manager = DialogueManager()

        # Create nodes
        greeting = DialogueNode(
            node_id="greeting",
            speaker="NPC",
            text="Hello.",
            options=[
                DialogueOption("opt1", "Who are you?", next_node="info")
            ]
        )

        info = DialogueNode(
            node_id="info",
            speaker="NPC",
            text="I'm a vendor.",
            options=[]
        )

        manager.add_node(greeting)
        manager.add_node(info)

        manager.start_conversation("greeting")
        manager.select_option("opt1")

        # Should navigate to info node
        assert manager.current_node.node_id == "info"

    def test_conversation_history(self):
        """Test tracking conversation history."""
        from dialogue import DialogueManager, DialogueNode, DialogueOption

        manager = DialogueManager()

        node1 = DialogueNode("n1", "NPC", "First.", [DialogueOption("o1", "Next", "n2")])
        node2 = DialogueNode("n2", "NPC", "Second.", [])

        manager.add_node(node1)
        manager.add_node(node2)

        manager.start_conversation("n1")
        manager.select_option("o1")

        history = manager.get_conversation_history()

        assert len(history) == 2
        assert history[0] == "n1"
        assert history[1] == "n2"

    def test_end_conversation(self):
        """Test ending a conversation."""
        from dialogue import DialogueManager, DialogueNode

        manager = DialogueManager()

        node = DialogueNode("end", "NPC", "Goodbye.", [])
        manager.add_node(node)

        manager.start_conversation("end")
        manager.end_conversation()

        assert manager.current_node is None


class TestConversationBranching:
    """Test branching conversation paths."""

    def test_multiple_paths(self):
        """Test conversation with multiple branching paths."""
        from dialogue import DialogueManager, DialogueNode, DialogueOption

        manager = DialogueManager()

        # Create branching conversation
        start = DialogueNode(
            node_id="start",
            speaker="Fixer",
            text="Need a job?",
            options=[
                DialogueOption("yes", "Yes, I'm interested.", next_node="job_offer"),
                DialogueOption("no", "Not now.", next_node="maybe_later")
            ]
        )

        job_offer = DialogueNode("job_offer", "Fixer", "Here's the deal...", [])
        maybe_later = DialogueNode("maybe_later", "Fixer", "Your loss.", [])

        manager.add_node(start)
        manager.add_node(job_offer)
        manager.add_node(maybe_later)

        # Test path 1: Accept
        manager.start_conversation("start")
        manager.select_option("yes")
        assert manager.current_node.node_id == "job_offer"

        # Test path 2: Decline
        manager.start_conversation("start")
        manager.select_option("no")
        assert manager.current_node.node_id == "maybe_later"

    def test_conditional_options(self):
        """Test options that appear conditionally."""
        from dialogue import DialogueManager, DialogueNode, DialogueOption

        manager = DialogueManager()

        node = DialogueNode(
            node_id="negotiation",
            speaker="Client",
            text="Can you do it?",
            options=[
                DialogueOption("normal", "I'll do it for 1000.", next_node="accept"),
                DialogueOption(
                    "persuade",
                    "[Persuade] I need 2000.",
                    next_node="higher_pay",
                    requirement_type="skill",
                    requirement_value={"skill": "cool", "level": 6}
                )
            ]
        )

        manager.add_node(node)
        manager.start_conversation("negotiation")

        # Get available options for player with low Cool
        available = manager.get_available_options({"cool": 3})

        # Should only see normal option
        assert len(available) == 1
        assert available[0].option_id == "normal"

    def test_one_time_dialogue(self):
        """Test dialogue that can only be seen once."""
        from dialogue import DialogueManager, DialogueNode

        manager = DialogueManager()

        node = DialogueNode(
            node_id="first_meeting",
            speaker="Character",
            text="First time we meet.",
            options=[],
            one_time=True
        )

        manager.add_node(node)

        # First time
        manager.start_conversation("first_meeting")
        assert manager.current_node.node_id == "first_meeting"

        manager.end_conversation()

        # Mark as seen
        manager.mark_dialogue_seen("first_meeting")

        # Try again (should be blocked or show alternate)
        assert manager.has_seen_dialogue("first_meeting")


class TestDialogueIntegration:
    """Test integration with other systems."""

    def test_apply_faction_consequence(self):
        """Test applying faction reputation consequence."""
        from dialogue import DialogueManager, DialogueOption

        manager = DialogueManager()

        option = DialogueOption(
            option_id="help",
            text="I'll help.",
            next_node="thanks",
            consequences=[
                {"type": "faction_rep", "faction": "militech", "amount": 25}
            ]
        )

        consequences = manager.get_consequences(option)

        assert len(consequences) == 1
        assert consequences[0]["faction"] == "militech"

    def test_apply_quest_consequence(self):
        """Test applying quest progress consequence."""
        from dialogue import DialogueManager, DialogueOption

        manager = DialogueManager()

        option = DialogueOption(
            option_id="accept",
            text="I accept.",
            next_node="briefing",
            consequences=[
                {"type": "quest_progress", "quest_id": "heist_1", "action": "activate"}
            ]
        )

        consequences = manager.get_consequences(option)

        assert consequences[0]["quest_id"] == "heist_1"

    def test_check_inventory_requirement(self):
        """Test checking if player has required item."""
        from dialogue import DialogueManager, DialogueOption

        manager = DialogueManager()

        option = DialogueOption(
            option_id="show_pass",
            text="[Show Pass]",
            next_node="enter",
            requirement_type="item",
            requirement_value={"item_id": "vip_pass"}
        )

        # Player has pass
        inventory = {"vip_pass": 1}
        assert manager.check_item_requirement(option, inventory) is True

        # Player doesn't have pass
        empty_inventory = {}
        assert manager.check_item_requirement(option, empty_inventory) is False


class TestDialogueVariables:
    """Test dialogue with dynamic variables."""

    def test_dialogue_with_player_name(self):
        """Test inserting player name into dialogue."""
        from dialogue import DialogueNode

        node = DialogueNode(
            node_id="greeting",
            speaker="Friend",
            text="Hey {player_name}, good to see you!",
            options=[]
        )

        # Replace variable
        formatted = node.text.replace("{player_name}", "V")

        assert formatted == "Hey V, good to see you!"

    def test_dialogue_with_multiple_variables(self):
        """Test multiple variable replacements."""
        from dialogue import DialogueNode

        node = DialogueNode(
            node_id="status",
            speaker="Quest Giver",
            text="You need {credits_needed} more credits and {rep_needed} more rep.",
            options=[]
        )

        formatted = node.text.replace("{credits_needed}", "500").replace("{rep_needed}", "25")

        assert "500" in formatted
        assert "25" in formatted


class TestSerialization:
    """Test dialogue system serialization."""

    def test_dialogue_node_to_dict(self):
        """Test converting dialogue node to dictionary."""
        from dialogue import DialogueNode, DialogueOption

        node = DialogueNode(
            node_id="test",
            speaker="NPC",
            text="Hello.",
            options=[DialogueOption("opt1", "Hi", next_node="response")]
        )

        data = node.to_dict()

        assert data["node_id"] == "test"
        assert data["speaker"] == "NPC"
        assert len(data["options"]) == 1

    def test_dialogue_node_from_dict(self):
        """Test loading dialogue node from dictionary."""
        from dialogue import DialogueNode

        data = {
            "node_id": "loaded",
            "speaker": "Vendor",
            "text": "What do you need?",
            "options": [
                {"option_id": "buy", "text": "Show me goods.", "next_node": "shop"}
            ]
        }

        node = DialogueNode.from_dict(data)

        assert node.node_id == "loaded"
        assert len(node.options) == 1

    def test_dialogue_manager_to_dict(self):
        """Test converting dialogue manager state to dictionary."""
        from dialogue import DialogueManager, DialogueNode

        manager = DialogueManager()

        node = DialogueNode("test", "NPC", "Test.", [])
        manager.add_node(node)
        manager.start_conversation("test")

        data = manager.to_dict()

        assert "current_node_id" in data
        assert data["current_node_id"] == "test"

    def test_dialogue_manager_from_dict(self):
        """Test loading dialogue manager from dictionary."""
        from dialogue import DialogueManager

        data = {
            "current_node_id": "greeting",
            "conversation_history": ["greeting"],
            "seen_dialogues": ["intro"]
        }

        manager = DialogueManager.from_dict(data)

        assert manager.current_node_id == "greeting"
        assert "intro" in manager.seen_dialogues


class TestEdgeCases:
    """Test edge cases."""

    def test_select_invalid_option(self):
        """Test selecting option that doesn't exist."""
        from dialogue import DialogueManager, DialogueNode

        manager = DialogueManager()

        node = DialogueNode("test", "NPC", "Hello.", [])
        manager.add_node(node)
        manager.start_conversation("test")

        # Try to select nonexistent option
        result = manager.select_option("nonexistent")

        assert result is False

    def test_navigate_to_missing_node(self):
        """Test navigating to node that doesn't exist."""
        from dialogue import DialogueManager, DialogueNode, DialogueOption

        manager = DialogueManager()

        node = DialogueNode(
            "test",
            "NPC",
            "Test.",
            [DialogueOption("bad", "Go", next_node="missing")]
        )

        manager.add_node(node)
        manager.start_conversation("test")

        # Try to navigate to missing node
        result = manager.select_option("bad")

        # Should fail gracefully
        assert result is False

    def test_empty_dialogue_tree(self):
        """Test manager with no nodes."""
        from dialogue import DialogueManager

        manager = DialogueManager()

        # Try to start conversation with no nodes
        result = manager.start_conversation("anything")

        assert result is False

    def test_circular_dialogue(self):
        """Test dialogue that loops back to itself."""
        from dialogue import DialogueManager, DialogueNode, DialogueOption

        manager = DialogueManager()

        # Create loop
        node = DialogueNode(
            "loop",
            "NPC",
            "Again?",
            [DialogueOption("again", "Say it again.", next_node="loop")]
        )

        manager.add_node(node)
        manager.start_conversation("loop")

        # Loop several times
        for _ in range(5):
            manager.select_option("again")

        # Should still be at loop node
        assert manager.current_node.node_id == "loop"
