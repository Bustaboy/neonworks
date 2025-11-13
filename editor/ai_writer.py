"""
AI Creative Writing Assistant

Intelligent assistance for dialog, quest writing, and narrative design.
Helps game designers create compelling stories, branching dialogs, and engaging quests.
"""

import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional


class DialogTone(Enum):
    """Dialog tone options"""

    FRIENDLY = auto()
    HOSTILE = auto()
    NEUTRAL = auto()
    MYSTERIOUS = auto()
    HUMOROUS = auto()
    SERIOUS = auto()
    DESPERATE = auto()
    CONFIDENT = auto()


class QuestType(Enum):
    """Quest type categories"""

    MAIN_STORY = auto()
    SIDE_QUEST = auto()
    FETCH_QUEST = auto()
    COMBAT_QUEST = auto()
    EXPLORATION = auto()
    ESCORT = auto()
    PUZZLE = auto()
    CRAFTING = auto()


@dataclass
class DialogLine:
    """A single line of dialog"""

    speaker: str
    text: str
    tone: DialogTone
    choices: List["DialogChoice"] = None

    def __post_init__(self):
        if self.choices is None:
            self.choices = []


@dataclass
class DialogChoice:
    """A player choice in dialog"""

    text: str
    leads_to: str  # ID of next dialog node
    requirements: Dict[str, any] = None  # Skill checks, items needed, etc.

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}


@dataclass
class QuestTemplate:
    """Generated quest template"""

    title: str
    description: str
    quest_type: QuestType
    objectives: List[str]
    rewards: Dict[str, any]
    dialog_intro: str
    dialog_completion: str
    suggested_location: str
    difficulty: str  # Easy, Medium, Hard


class AIWritingAssistant:
    """
    AI assistant for creative writing in games.

    Features:
    - Dialog generation with consistent character voices
    - Quest template creation
    - Branching narrative suggestions
    - Character development assistance
    - Tone and style consistency checking
    """

    def __init__(self, game_theme: str = "cyberpunk"):
        self.game_theme = game_theme
        self.character_voices = {}  # Character name -> personality traits

        # Thematic word banks for different game themes
        self.theme_vocabulary = {
            "cyberpunk": {
                "adjectives": [
                    "neon",
                    "cyber",
                    "digital",
                    "corporate",
                    "augmented",
                    "neural",
                    "chrome",
                    "encrypted",
                ],
                "nouns": [
                    "netrunner",
                    "hacker",
                    "corp",
                    "data",
                    "implant",
                    "grid",
                    "matrix",
                    "sector",
                ],
                "verbs": [
                    "hack",
                    "jack in",
                    "upload",
                    "decrypt",
                    "augment",
                    "interface",
                ],
                "locations": [
                    "downtown sector",
                    "corporate district",
                    "undercity",
                    "data haven",
                    "net cafe",
                ],
            },
            "fantasy": {
                "adjectives": [
                    "ancient",
                    "mystical",
                    "enchanted",
                    "cursed",
                    "legendary",
                    "sacred",
                ],
                "nouns": [
                    "wizard",
                    "warrior",
                    "artifact",
                    "spell",
                    "dungeon",
                    "kingdom",
                ],
                "verbs": ["cast", "enchant", "quest", "battle", "explore"],
                "locations": ["castle", "forest", "cave", "village", "temple"],
            },
            "scifi": {
                "adjectives": [
                    "advanced",
                    "alien",
                    "quantum",
                    "stellar",
                    "interstellar",
                    "plasma",
                ],
                "nouns": [
                    "station",
                    "colony",
                    "alien",
                    "ship",
                    "technology",
                    "star system",
                ],
                "verbs": ["scan", "transmit", "terraform", "explore", "research"],
                "locations": [
                    "space station",
                    "colony",
                    "planet",
                    "asteroid field",
                    "research facility",
                ],
            },
        }

        self.vocab = self.theme_vocabulary.get(
            game_theme, self.theme_vocabulary["cyberpunk"]
        )

    def generate_quest(
        self, quest_type: QuestType, difficulty: str = "Medium", player_level: int = 1
    ) -> QuestTemplate:
        """
        Generate a complete quest template with AI assistance.

        The AI creates:
        - Thematically appropriate title and description
        - Balanced objectives
        - Appropriate rewards
        - Introductory and completion dialog
        """
        print(f"🤖 AI Writer: Crafting a {difficulty} {quest_type.name} quest...")

        if quest_type == QuestType.FETCH_QUEST:
            return self._generate_fetch_quest(difficulty, player_level)
        elif quest_type == QuestType.COMBAT_QUEST:
            return self._generate_combat_quest(difficulty, player_level)
        elif quest_type == QuestType.EXPLORATION:
            return self._generate_exploration_quest(difficulty, player_level)
        elif quest_type == QuestType.MAIN_STORY:
            return self._generate_story_quest(difficulty, player_level)
        else:
            return self._generate_generic_quest(quest_type, difficulty, player_level)

    def _generate_fetch_quest(
        self, difficulty: str, player_level: int
    ) -> QuestTemplate:
        """Generate a fetch quest"""
        items = [
            "data chip",
            "medical supplies",
            "encrypted files",
            "rare component",
            "prototype device",
        ]
        item = random.choice(items)

        adjective = random.choice(self.vocab["adjectives"])
        location = random.choice(self.vocab["locations"])

        title = f"Recovery: {adjective.capitalize()} {item.capitalize()}"

        description = (
            f"A client needs you to retrieve a {adjective} {item} from the {location}. "
            f"The area is dangerous, but the pay is good. Exercise caution."
        )

        num_objectives = (
            2 if difficulty == "Easy" else 3 if difficulty == "Medium" else 4
        )

        objectives = [
            f"Travel to the {location}",
            f"Locate the {adjective} {item}",
        ]

        if num_objectives >= 3:
            objectives.append(f"Avoid or eliminate hostile forces")

        if num_objectives >= 4:
            objectives.append(f"Deliver the {item} without damage")

        rewards = self._calculate_rewards(difficulty, player_level)

        dialog_intro = (
            f"Listen up. I need someone capable to recover a {item} from the {location}. "
            f"It's {adjective} tech, worth a fortune. You interested?"
        )

        dialog_completion = (
            f"Good work. The {item} is exactly what I needed. "
            f"Here's your payment. Pleasure doing business."
        )

        return QuestTemplate(
            title=title,
            description=description,
            quest_type=QuestType.FETCH_QUEST,
            objectives=objectives,
            rewards=rewards,
            dialog_intro=dialog_intro,
            dialog_completion=dialog_completion,
            suggested_location=location,
            difficulty=difficulty,
        )

    def _generate_combat_quest(
        self, difficulty: str, player_level: int
    ) -> QuestTemplate:
        """Generate a combat quest"""
        enemies = [
            "raiders",
            "corporate mercenaries",
            "rogue AI units",
            "gang members",
            "corrupted drones",
        ]
        enemy = random.choice(enemies)

        location = random.choice(self.vocab["locations"])
        adjective = random.choice(self.vocab["adjectives"])

        title = f"Elimination: {adjective.capitalize()} {enemy.capitalize()}"

        description = (
            f"A group of {enemy} has taken over the {location}. "
            f"They're causing trouble and need to be dealt with. "
            f"Eliminate the threat and restore order."
        )

        num_enemies = (
            5 if difficulty == "Easy" else 10 if difficulty == "Medium" else 15
        )

        objectives = [
            f"Locate the {enemy} at the {location}",
            f"Eliminate {num_enemies} {enemy}",
            f"Clear the area of all hostiles",
        ]

        if difficulty == "Hard":
            objectives.append(f"Neutralize the {enemy} leader")

        rewards = self._calculate_rewards(difficulty, player_level, combat_bonus=True)

        dialog_intro = (
            f"We've got a problem. {enemy.capitalize()} have moved into the {location}. "
            f"They're {adjective} and dangerous. Think you can handle them?"
        )

        dialog_completion = (
            f"The {location} is clear. You did good work out there. "
            f"Here's your combat pay. We'll call you if we need you again."
        )

        return QuestTemplate(
            title=title,
            description=description,
            quest_type=QuestType.COMBAT_QUEST,
            objectives=objectives,
            rewards=rewards,
            dialog_intro=dialog_intro,
            dialog_completion=dialog_completion,
            suggested_location=location,
            difficulty=difficulty,
        )

    def _generate_exploration_quest(
        self, difficulty: str, player_level: int
    ) -> QuestTemplate:
        """Generate an exploration quest"""
        discoveries = [
            "ancient facility",
            "hidden cache",
            "abandoned outpost",
            "secret lab",
            "lost colony",
        ]
        discovery = random.choice(discoveries)

        adjective = random.choice(self.vocab["adjectives"])
        location = random.choice(self.vocab["locations"])

        title = f"Discovery: The {adjective.capitalize()} {discovery.capitalize()}"

        description = (
            f"Rumors speak of a {adjective} {discovery} in the {location}. "
            f"Scout the area and report what you find. There could be valuable tech or intel."
        )

        objectives = [
            f"Travel to the {location}",
            f"Locate the {adjective} {discovery}",
            "Explore and document findings",
        ]

        if difficulty in ["Medium", "Hard"]:
            objectives.append("Retrieve any valuable data or items")

        if difficulty == "Hard":
            objectives.append("Map the entire area")

        rewards = self._calculate_rewards(difficulty, player_level)

        dialog_intro = (
            f"I've heard whispers about a {discovery} somewhere in the {location}. "
            f"It's supposed to be {adjective}. Want to check it out? Could be profitable."
        )

        dialog_completion = (
            f"Excellent work on the reconnaissance. This information is valuable. "
            f"Take this as compensation. Who knows what else is out there?"
        )

        return QuestTemplate(
            title=title,
            description=description,
            quest_type=QuestType.EXPLORATION,
            objectives=objectives,
            rewards=rewards,
            dialog_intro=dialog_intro,
            dialog_completion=dialog_completion,
            suggested_location=location,
            difficulty=difficulty,
        )

    def _generate_story_quest(
        self, difficulty: str, player_level: int
    ) -> QuestTemplate:
        """Generate a main story quest"""
        events = ["conspiracy", "power play", "invasion", "revolution", "awakening"]
        event = random.choice(events)

        adjective = random.choice(self.vocab["adjectives"])
        noun = random.choice(self.vocab["nouns"])

        title = f"The {adjective.capitalize()} {event.capitalize()}"

        description = (
            f"Something big is happening. A {adjective} {event} threatens everything we've built. "
            f"This isn't just another job - this is about survival. "
            f"The fate of the {noun} hangs in the balance."
        )

        objectives = [
            f"Investigate the {event}",
            f"Gather intelligence on the {adjective} threat",
            f"Confront those responsible",
            "Make a critical decision",
            "Deal with the consequences",
        ]

        rewards = self._calculate_rewards(difficulty, player_level, story_bonus=True)
        rewards["story_progress"] = True

        dialog_intro = (
            f"I wouldn't normally involve you in this, but we're out of options. "
            f"This {event}... it's bigger than any of us. "
            f"The {adjective} forces at play here... they won't stop until they get what they want. "
            f"Are you ready for this?"
        )

        dialog_completion = (
            f"It's over. For now. What you did... it changed everything. "
            f"The {event} has been dealt with, but this is just the beginning. "
            f"There's more to this story. Much more."
        )

        return QuestTemplate(
            title=title,
            description=description,
            quest_type=QuestType.MAIN_STORY,
            objectives=objectives,
            rewards=rewards,
            dialog_intro=dialog_intro,
            dialog_completion=dialog_completion,
            suggested_location="multiple",
            difficulty=difficulty,
        )

    def _generate_generic_quest(
        self, quest_type: QuestType, difficulty: str, player_level: int
    ) -> QuestTemplate:
        """Generate a generic quest"""
        adjective = random.choice(self.vocab["adjectives"])
        noun = random.choice(self.vocab["nouns"])
        location = random.choice(self.vocab["locations"])

        return QuestTemplate(
            title=f"The {adjective.capitalize()} {noun.capitalize()}",
            description=f"A {quest_type.name.lower().replace('_', ' ')} involving {adjective} {noun}.",
            quest_type=quest_type,
            objectives=["Complete the objective", "Return for reward"],
            rewards=self._calculate_rewards(difficulty, player_level),
            dialog_intro=f"I have a job for you involving {adjective} {noun}. Interested?",
            dialog_completion="Good work. Here's your payment.",
            suggested_location=location,
            difficulty=difficulty,
        )

    def generate_dialog_tree(
        self, npc_name: str, situation: str, tone: DialogTone
    ) -> List[DialogLine]:
        """
        Generate a branching dialog tree for an NPC.

        The AI creates natural-sounding conversation with appropriate choices.
        """
        print(f"🤖 AI Writer: Crafting dialog for {npc_name} ({tone.name})...")

        # Opening line based on tone
        opening_lines = {
            DialogTone.FRIENDLY: [
                f"Hey there! Good to see a friendly face in this {self.vocab['adjectives'][0]} place.",
                "Welcome! What brings you around these parts?",
                "Always happy to help out. What do you need?",
            ],
            DialogTone.HOSTILE: [
                "What do you want? Make it quick.",
                "You've got nerve coming here. State your business.",
                "I don't have time for this. Speak or leave.",
            ],
            DialogTone.NEUTRAL: [
                f"You need something? I deal in {self.vocab['nouns'][0]}s if you're buying.",
                "What can I do for you?",
                "Talk. I'm listening.",
            ],
            DialogTone.MYSTERIOUS: [
                "Interesting... I've been expecting someone like you.",
                "Fate has a curious way of bringing people together, doesn't it?",
                "You seek answers. Perhaps I have some... for a price.",
            ],
        }

        opening = random.choice(
            opening_lines.get(tone, opening_lines[DialogTone.NEUTRAL])
        )

        # Generate player choices
        choices = [
            DialogChoice("Tell me about this situation.", "info_node"),
            DialogChoice("What can you offer me?", "trade_node"),
            DialogChoice("I'll be going now.", "end_node"),
        ]

        if tone == DialogTone.HOSTILE:
            choices.insert(
                1,
                DialogChoice(
                    "[Intimidate] You'll cooperate or else.",
                    "intimidate_node",
                    {"skill": "intimidation", "level": 3},
                ),
            )
        elif tone == DialogTone.MYSTERIOUS:
            choices.append(
                DialogChoice(
                    "[Investigate] Something doesn't add up here.",
                    "investigate_node",
                    {"skill": "perception", "level": 2},
                )
            )

        dialog_tree = [
            DialogLine(speaker=npc_name, text=opening, tone=tone, choices=choices)
        ]

        return dialog_tree

    def suggest_dialog_improvements(self, dialog_text: str) -> List[str]:
        """
        Analyze dialog and suggest improvements.

        Checks for:
        - Tone consistency
        - Character voice
        - Pacing
        - Player agency
        """
        suggestions = []

        # Check length
        if len(dialog_text) > 300:
            suggestions.append(
                "💡 Dialog is lengthy. Consider breaking into multiple nodes for better pacing."
            )

        # Check for questions (player agency)
        if "?" not in dialog_text:
            suggestions.append(
                "💡 Add a question or choice to increase player engagement."
            )

        # Check for theme words
        theme_words_found = sum(
            1
            for word in self.vocab["adjectives"] + self.vocab["nouns"]
            if word in dialog_text.lower()
        )

        if theme_words_found == 0:
            suggestions.append(
                f"💡 Consider adding {self.game_theme} thematic vocabulary for immersion."
            )

        # Check for emotional words
        emotional_words = [
            "angry",
            "happy",
            "sad",
            "excited",
            "worried",
            "calm",
            "terrified",
        ]
        if not any(word in dialog_text.lower() for word in emotional_words):
            suggestions.append(
                "💡 Add emotional depth to make the character more relatable."
            )

        if not suggestions:
            suggestions.append(
                "✅ Dialog looks great! Good pacing and character voice."
            )

        return suggestions

    def _calculate_rewards(
        self,
        difficulty: str,
        player_level: int,
        combat_bonus: bool = False,
        story_bonus: bool = False,
    ) -> Dict[str, any]:
        """Calculate appropriate quest rewards"""
        base_xp = 100 * player_level
        base_credits = 50 * player_level

        multipliers = {"Easy": 0.8, "Medium": 1.0, "Hard": 1.5}

        multiplier = multipliers.get(difficulty, 1.0)

        if combat_bonus:
            multiplier *= 1.2
        if story_bonus:
            multiplier *= 1.5

        rewards = {
            "xp": int(base_xp * multiplier),
            "credits": int(base_credits * multiplier),
            "reputation": 10 * multipliers.get(difficulty, 1.0),
        }

        # Add items for harder quests
        if difficulty == "Hard":
            rewards["items"] = ["rare_component", "medical_supplies"]
        elif difficulty == "Medium":
            rewards["items"] = ["medical_supplies"]

        return rewards

    def create_character_profile(
        self, name: str, role: str, personality_traits: List[str]
    ) -> Dict[str, any]:
        """
        Create a character profile to maintain consistent dialog voice.
        """
        self.character_voices[name] = {
            "role": role,
            "personality": personality_traits,
            "speech_patterns": self._generate_speech_patterns(personality_traits),
        }

        print(f"✅ Created character profile for {name} ({role})")
        print(f"   Personality: {', '.join(personality_traits)}")

        return self.character_voices[name]

    def _generate_speech_patterns(self, personality_traits: List[str]) -> List[str]:
        """Generate speech patterns based on personality"""
        patterns = []

        if "gruff" in personality_traits:
            patterns.extend(["short sentences", "direct", "no pleasantries"])
        if "cheerful" in personality_traits:
            patterns.extend(["exclamations", "positive language", "helpful tone"])
        if "intelligent" in personality_traits:
            patterns.extend(["technical terms", "complex sentences", "analytical"])
        if "mysterious" in personality_traits:
            patterns.extend(["vague references", "metaphors", "cryptic hints"])

        return patterns or ["neutral tone"]


def demo_ai_writer():
    """Demo the AI writing assistant"""
    print("=" * 60)
    print("AI CREATIVE WRITING ASSISTANT DEMO")
    print("=" * 60)

    writer = AIWritingAssistant(game_theme="cyberpunk")

    # Generate quests
    print("\n📝 QUEST GENERATION:\n")
    quest1 = writer.generate_quest(QuestType.FETCH_QUEST, "Medium", player_level=5)
    print(f"Title: {quest1.title}")
    print(f"Description: {quest1.description}")
    print(f"Objectives: {', '.join(quest1.objectives)}")
    print(f"Rewards: {quest1.rewards}")

    print("\n" + "=" * 60 + "\n")

    quest2 = writer.generate_quest(QuestType.MAIN_STORY, "Hard", player_level=10)
    print(f"Title: {quest2.title}")
    print(f"Description: {quest2.description}")
    print(f"Dialog Intro: {quest2.dialog_intro}")

    # Generate dialog
    print("\n" + "=" * 60)
    print("\n💬 DIALOG GENERATION:\n")

    dialog = writer.generate_dialog_tree("Raven", "meeting", DialogTone.MYSTERIOUS)
    print(f"Speaker: {dialog[0].speaker}")
    print(f"Text: {dialog[0].text}")
    print(f"Player choices:")
    for choice in dialog[0].choices:
        print(f"  - {choice.text}")

    # Character profile
    print("\n" + "=" * 60)
    print("\n👤 CHARACTER PROFILE:\n")

    profile = writer.create_character_profile(
        "Raven", "Information Broker", ["mysterious", "intelligent", "cautious"]
    )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo_ai_writer()
