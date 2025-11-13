"""
Neon Collapse - Dialogue & Choice System
Manages conversations, branching dialogue trees, and choice consequences
"""

from typing import Dict, List, Any, Optional


# ============================================================================
# DIALOGUE OPTION CLASS
# ============================================================================

class DialogueOption:
    """Represents a single dialogue option/choice."""

    def __init__(
        self,
        option_id: str,
        text: str,
        next_node: str,
        requirement_type: Optional[str] = None,
        requirement_value: Optional[Dict[str, Any]] = None,
        consequences: Optional[List[Dict[str, Any]]] = None
    ):
        self.option_id = option_id
        self.text = text
        self.next_node = next_node
        self.requirement_type = requirement_type  # skill, attribute, item, faction, multiple
        self.requirement_value = requirement_value or {}
        self.consequences = consequences or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "option_id": self.option_id,
            "text": self.text,
            "next_node": self.next_node,
            "requirement_type": self.requirement_type,
            "requirement_value": self.requirement_value,
            "consequences": self.consequences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueOption':
        """Load from dictionary."""
        return cls(
            option_id=data["option_id"],
            text=data["text"],
            next_node=data["next_node"],
            requirement_type=data.get("requirement_type"),
            requirement_value=data.get("requirement_value"),
            consequences=data.get("consequences", [])
        )


# ============================================================================
# DIALOGUE NODE CLASS
# ============================================================================

class DialogueNode:
    """Represents a single node in a dialogue tree."""

    def __init__(
        self,
        node_id: str,
        speaker: str,
        text: str,
        options: List[DialogueOption],
        one_time: bool = False
    ):
        self.node_id = node_id
        self.speaker = speaker
        self.text = text
        self.options = options
        self.one_time = one_time  # Can only be seen once

    def is_terminal(self) -> bool:
        """Check if this node ends the conversation."""
        return len(self.options) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "speaker": self.speaker,
            "text": self.text,
            "options": [opt.to_dict() for opt in self.options],
            "one_time": self.one_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueNode':
        """Load from dictionary."""
        options = [DialogueOption.from_dict(opt_data) for opt_data in data.get("options", [])]

        return cls(
            node_id=data["node_id"],
            speaker=data["speaker"],
            text=data["text"],
            options=options,
            one_time=data.get("one_time", False)
        )


# ============================================================================
# DIALOGUE MANAGER CLASS
# ============================================================================

class DialogueManager:
    """Manages dialogue trees and conversation state."""

    def __init__(self):
        self.nodes: Dict[str, DialogueNode] = {}
        self.current_node: Optional[DialogueNode] = None
        self.current_node_id: Optional[str] = None
        self.conversation_history: List[str] = []
        self.seen_dialogues: List[str] = []

    def add_node(self, node: DialogueNode):
        """Add a dialogue node to the tree."""
        self.nodes[node.node_id] = node

    def start_conversation(self, start_node_id: str) -> bool:
        """
        Start a conversation at specified node.

        Args:
            start_node_id: ID of starting node

        Returns:
            True if started successfully, False if node not found
        """
        if start_node_id not in self.nodes:
            return False

        self.current_node = self.nodes[start_node_id]
        self.current_node_id = start_node_id
        self.conversation_history = [start_node_id]

        return True

    def select_option(self, option_id: str) -> bool:
        """
        Select a dialogue option and navigate to next node.

        Args:
            option_id: ID of option to select

        Returns:
            True if navigation successful, False otherwise
        """
        if not self.current_node:
            return False

        # Find selected option
        selected_option = None
        for option in self.current_node.options:
            if option.option_id == option_id:
                selected_option = option
                break

        if not selected_option:
            return False

        # Navigate to next node
        next_node_id = selected_option.next_node

        if next_node_id not in self.nodes:
            return False

        self.current_node = self.nodes[next_node_id]
        self.current_node_id = next_node_id
        self.conversation_history.append(next_node_id)

        return True

    def end_conversation(self):
        """End the current conversation."""
        if self.current_node and self.current_node.one_time:
            self.mark_dialogue_seen(self.current_node.node_id)

        self.current_node = None
        self.current_node_id = None

    def get_conversation_history(self) -> List[str]:
        """Get list of node IDs visited in current conversation."""
        return self.conversation_history.copy()

    def mark_dialogue_seen(self, node_id: str):
        """Mark a dialogue node as seen (for one-time dialogues)."""
        if node_id not in self.seen_dialogues:
            self.seen_dialogues.append(node_id)

    def has_seen_dialogue(self, node_id: str) -> bool:
        """Check if player has seen a dialogue before."""
        return node_id in self.seen_dialogues

    def _check_skill_requirement(self, requirement_value: Dict, player_stats: Dict[str, int]) -> bool:
        """Check if player meets skill requirement."""
        skill = requirement_value.get("skill")
        if skill is None:
            return False
        required_level = requirement_value.get("level", 0)
        player_level = player_stats.get(skill, 0)
        return player_level >= required_level

    def _check_attribute_requirement(self, requirement_value: Dict, player_stats: Dict[str, int]) -> bool:
        """Check if player meets attribute requirement."""
        attribute = requirement_value.get("attribute")
        if attribute is None:
            return False
        required_level = requirement_value.get("level", 0)
        player_level = player_stats.get(attribute, 0)
        return player_level >= required_level

    def _check_item_requirement(self, requirement_value: Dict, player_inventory: Optional[Dict[str, int]]) -> bool:
        """Check if player has required item."""
        if player_inventory is None:
            return False
        item_id = requirement_value.get("item_id")
        if item_id is None:
            return False
        return item_id in player_inventory and player_inventory[item_id] > 0

    def _check_faction_requirement(self, requirement_value: Dict, faction_reps: Optional[Dict[str, int]]) -> bool:
        """Check if player meets faction reputation requirement."""
        if faction_reps is None:
            return False
        faction = requirement_value.get("faction")
        if faction is None:
            return False
        min_rep = requirement_value.get("min_rep", 0)
        player_rep = faction_reps.get(faction, 0)
        return player_rep >= min_rep

    def _check_multiple_requirements(self, requirement_value: Dict, player_stats: Dict[str, int]) -> bool:
        """Check if player meets all requirements in a multiple requirement."""
        requirements = requirement_value.get("requirements", [])
        for req in requirements:
            req_type = req.get("type")
            if req_type == "attribute":
                if not self._check_attribute_requirement(req, player_stats):
                    return False
            elif req_type == "skill":
                if not self._check_skill_requirement(req, player_stats):
                    return False
        return True

    def check_option_available(
        self,
        option: DialogueOption,
        player_stats: Dict[str, int],
        player_inventory: Optional[Dict[str, int]] = None,
        faction_reps: Optional[Dict[str, int]] = None
    ) -> bool:
        """
        Check if dialogue option is available to player.

        Args:
            option: Dialogue option to check
            player_stats: Player attributes/skills
            player_inventory: Player inventory
            faction_reps: Faction reputations

        Returns:
            True if option is available
        """
        if not option.requirement_type:
            return True  # No requirements

        requirement_checks = {
            "skill": lambda: self._check_skill_requirement(option.requirement_value, player_stats),
            "attribute": lambda: self._check_attribute_requirement(option.requirement_value, player_stats),
            "item": lambda: self._check_item_requirement(option.requirement_value, player_inventory),
            "faction": lambda: self._check_faction_requirement(option.requirement_value, faction_reps),
            "multiple": lambda: self._check_multiple_requirements(option.requirement_value, player_stats)
        }

        check_func = requirement_checks.get(option.requirement_type)
        if check_func:
            return check_func()

        return False

    def check_item_requirement(
        self,
        option: DialogueOption,
        inventory: Dict[str, int]
    ) -> bool:
        """
        Check if player has required item.

        Args:
            option: Dialogue option
            inventory: Player inventory

        Returns:
            True if requirement met
        """
        if option.requirement_type != "item":
            return True

        item_id = option.requirement_value.get("item_id")
        return item_id in inventory and inventory[item_id] > 0

    def get_available_options(
        self,
        player_stats: Dict[str, int],
        player_inventory: Optional[Dict[str, int]] = None,
        faction_reps: Optional[Dict[str, int]] = None
    ) -> List[DialogueOption]:
        """
        Get list of options available to player at current node.

        Args:
            player_stats: Player attributes
            player_inventory: Player inventory
            faction_reps: Faction reputations

        Returns:
            List of available options
        """
        if not self.current_node:
            return []

        available = []
        for option in self.current_node.options:
            if self.check_option_available(option, player_stats, player_inventory, faction_reps):
                available.append(option)

        return available

    def get_consequences(self, option: DialogueOption) -> List[Dict[str, Any]]:
        """
        Get consequences of selecting an option.

        Args:
            option: Selected dialogue option

        Returns:
            List of consequences
        """
        return option.consequences.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_node_id": self.current_node_id,
            "conversation_history": self.conversation_history.copy(),
            "seen_dialogues": self.seen_dialogues.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueManager':
        """Load from dictionary."""
        manager = cls()

        manager.current_node_id = data.get("current_node_id")
        manager.conversation_history = data.get("conversation_history", [])
        manager.seen_dialogues = data.get("seen_dialogues", [])

        return manager
