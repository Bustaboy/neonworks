"""
Character Bio Generator

Generates character biographies with varying detail levels based on importance.
Supports AI generation, template-based generation, and manual override.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import random


class CharacterImportance(Enum):
    """Character importance levels determining bio length and detail."""
    NPC = "npc"              # 1-2 sentences, basic description
    SUPPORTING = "supporting"  # 2-4 sentences, moderate detail
    MAIN = "main"            # 4-8 sentences, rich backstory


@dataclass
class BioTemplate:
    """Template for generating character bios."""
    importance: CharacterImportance
    intro_patterns: List[str]
    trait_patterns: List[str]
    background_patterns: List[str]
    motivation_patterns: Optional[List[str]] = None


class CharacterBioGenerator:
    """
    Generates character biographies based on appearance and importance level.

    Bio Length Guidelines:
    - NPC: 40-80 words (1-2 sentences)
    - Supporting: 80-150 words (2-4 sentences)
    - Main: 150-300 words (4-8 sentences)
    """

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, BioTemplate]:
        """Initialize bio templates for different character archetypes."""
        return {
            "warrior": BioTemplate(
                importance=CharacterImportance.NPC,
                intro_patterns=[
                    "A {adjective} warrior clad in {armor_type}",
                    "A battle-hardened fighter wearing {armor_type}",
                    "A skilled combatant armored in {armor_type}",
                ],
                trait_patterns=[
                    "Known for {trait} and unwavering courage",
                    "Renowned for {trait} in battle",
                    "Feared for {trait} on the battlefield",
                ],
                background_patterns=[
                    "Trained in the art of combat from a young age",
                    "Forged through countless battles",
                    "Honed skills through years of military service",
                ],
                motivation_patterns=[
                    "Seeks to protect the innocent",
                    "Driven by a desire for glory",
                    "Motivated by loyalty to their comrades",
                ]
            ),
            "mage": BioTemplate(
                importance=CharacterImportance.NPC,
                intro_patterns=[
                    "A {adjective} spellcaster versed in {magic_type}",
                    "A scholarly mage studying {magic_type}",
                    "A powerful wizard mastering {magic_type}",
                ],
                trait_patterns=[
                    "Known for {trait} and arcane wisdom",
                    "Renowned for {trait} and mystical prowess",
                    "Feared for {trait} and magical power",
                ],
                background_patterns=[
                    "Spent years studying ancient tomes",
                    "Trained at a prestigious magic academy",
                    "Self-taught through dangerous experimentation",
                ],
                motivation_patterns=[
                    "Seeks to unlock forbidden knowledge",
                    "Driven by curiosity about the arcane",
                    "Motivated by a thirst for power",
                ]
            ),
            "thief": BioTemplate(
                importance=CharacterImportance.NPC,
                intro_patterns=[
                    "A {adjective} rogue skilled in {specialty}",
                    "A nimble thief excelling at {specialty}",
                    "A shadowy figure known for {specialty}",
                ],
                trait_patterns=[
                    "Known for {trait} and quick reflexes",
                    "Renowned for {trait} and stealth",
                    "Feared for {trait} in the criminal underworld",
                ],
                background_patterns=[
                    "Grew up on the streets learning to survive",
                    "Former member of the thieves' guild",
                    "Turned to thievery after losing everything",
                ],
                motivation_patterns=[
                    "Seeks wealth to escape poverty",
                    "Driven by the thrill of the heist",
                    "Motivated by a desire for freedom",
                ]
            ),
            "cleric": BioTemplate(
                importance=CharacterImportance.NPC,
                intro_patterns=[
                    "A {adjective} priest devoted to {deity}",
                    "A holy cleric serving {deity}",
                    "A faithful servant of {deity}",
                ],
                trait_patterns=[
                    "Known for {trait} and unwavering faith",
                    "Renowned for {trait} and divine power",
                    "Blessed with {trait} and holy grace",
                ],
                background_patterns=[
                    "Trained in the sacred halls of the temple",
                    "Answered the divine calling at a young age",
                    "Found purpose through spiritual awakening",
                ],
                motivation_patterns=[
                    "Seeks to spread their faith",
                    "Driven by a mission to heal the suffering",
                    "Motivated by divine visions",
                ]
            ),
        }

    def generate_bio(
        self,
        character_name: str,
        character_type: str,
        layers: List[Dict],
        importance: CharacterImportance = CharacterImportance.NPC,
        use_ai: bool = True,
    ) -> Dict[str, str]:
        """
        Generate character bio with appropriate length for importance level.

        Args:
            character_name: Name of the character
            character_type: Type/class (warrior, mage, etc.)
            layers: Character layer data for appearance analysis
            importance: Character importance level
            use_ai: Whether to use AI generation (if False, uses templates)

        Returns:
            Dict with 'description' (short) and 'note' (full bio)
        """
        if use_ai:
            return self._generate_ai_bio(character_name, character_type, layers, importance)
        else:
            return self._generate_template_bio(character_name, character_type, layers, importance)

    def _generate_ai_bio(
        self,
        character_name: str,
        character_type: str,
        layers: List[Dict],
        importance: CharacterImportance,
    ) -> Dict[str, str]:
        """Generate bio using AI-style generation (simulated for now)."""
        # Analyze character appearance
        appearance = self._analyze_appearance(layers)

        # Generate bio based on importance level
        if importance == CharacterImportance.NPC:
            bio = self._generate_npc_bio(character_name, character_type, appearance)
        elif importance == CharacterImportance.SUPPORTING:
            bio = self._generate_supporting_bio(character_name, character_type, appearance)
        else:  # MAIN
            bio = self._generate_main_bio(character_name, character_type, appearance)

        return bio

    def _analyze_appearance(self, layers: List[Dict]) -> Dict[str, str]:
        """Analyze character layers to describe appearance."""
        appearance = {
            "armor_type": "unknown armor",
            "weapon": "unarmed",
            "accessories": [],
            "colors": [],
            "overall_style": "mysterious",
        }

        # Analyze layers
        for layer in layers:
            layer_type = layer.get("layer_type", "")
            component_id = layer.get("component_id", "")

            # Armor detection
            if "armor" in component_id.lower() or layer_type == "TORSO":
                if "plate" in component_id.lower():
                    appearance["armor_type"] = "heavy plate armor"
                elif "leather" in component_id.lower():
                    appearance["armor_type"] = "studded leather armor"
                elif "robe" in component_id.lower():
                    appearance["armor_type"] = "flowing robes"
                else:
                    appearance["armor_type"] = "sturdy armor"

            # Weapon detection
            if layer_type == "WEAPON" or layer_type == "WEAPON_BACK":
                if "sword" in component_id.lower():
                    appearance["weapon"] = "a longsword"
                elif "staff" in component_id.lower():
                    appearance["weapon"] = "a mystical staff"
                elif "bow" in component_id.lower():
                    appearance["weapon"] = "a recurve bow"
                elif "dagger" in component_id.lower():
                    appearance["weapon"] = "twin daggers"
                elif "mace" in component_id.lower():
                    appearance["weapon"] = "a holy mace"

            # Accessory detection
            if layer_type in ["CAPE", "HEAD", "ACCESSORY"]:
                appearance["accessories"].append(component_id.replace("_", " "))

        return appearance

    def _generate_npc_bio(
        self,
        name: str,
        char_type: str,
        appearance: Dict[str, str],
    ) -> Dict[str, str]:
        """Generate short bio for NPCs (1-2 sentences, 40-80 words)."""

        # Templates for different character types
        npc_templates = {
            "warrior": [
                f"{name} is a battle-hardened warrior clad in {appearance['armor_type']}, wielding {appearance['weapon']} with practiced ease.",
                f"A seasoned fighter, {name} wears {appearance['armor_type']} and carries {appearance['weapon']}.",
                f"{name} stands ready in {appearance['armor_type']}, {appearance['weapon']} at the ready.",
            ],
            "mage": [
                f"{name} is a studious mage dressed in {appearance['armor_type']}, {appearance['weapon']} crackling with arcane energy.",
                f"A scholarly spellcaster, {name} wields {appearance['weapon']} and wears {appearance['armor_type']}.",
                f"{name} channels mystical forces through {appearance['weapon']}, clad in {appearance['armor_type']}.",
            ],
            "thief": [
                f"{name} is a nimble rogue garbed in {appearance['armor_type']}, {appearance['weapon']} concealed and ready.",
                f"A shadow in the night, {name} moves silently in {appearance['armor_type']} with {appearance['weapon']}.",
                f"{name} operates from the darkness, equipped with {appearance['armor_type']} and {appearance['weapon']}.",
            ],
            "cleric": [
                f"{name} is a devoted cleric wearing {appearance['armor_type']}, {appearance['weapon']} blessed by divine power.",
                f"A faithful servant of the divine, {name} carries {appearance['weapon']} and wears {appearance['armor_type']}.",
                f"{name} channels holy energy through {appearance['weapon']}, dressed in {appearance['armor_type']}.",
            ],
            "archer": [
                f"{name} is a skilled archer in {appearance['armor_type']}, {appearance['weapon']} strung and ready.",
                f"A precise marksman, {name} wears {appearance['armor_type']} and wields {appearance['weapon']}.",
                f"{name} never misses a shot with {appearance['weapon']}, protected by {appearance['armor_type']}.",
            ],
            "knight": [
                f"{name} is a noble knight resplendent in {appearance['armor_type']}, {appearance['weapon']} gleaming.",
                f"A paragon of chivalry, {name} stands proud in {appearance['armor_type']} with {appearance['weapon']}.",
                f"{name} embodies honor and valor, clad in {appearance['armor_type']} and wielding {appearance['weapon']}.",
            ],
        }

        # Get template for character type or use generic
        templates = npc_templates.get(char_type, npc_templates["warrior"])
        description = random.choice(templates)

        return {
            "description": description,
            "note": f"NPC: {description}",
        }

    def _generate_supporting_bio(
        self,
        name: str,
        char_type: str,
        appearance: Dict[str, str],
    ) -> Dict[str, str]:
        """Generate medium bio for supporting characters (2-4 sentences, 80-150 words)."""

        # Intro sentence
        intros = {
            "warrior": f"{name} is a veteran warrior whose {appearance['armor_type']} bears the scars of countless battles.",
            "mage": f"{name} is a learned spellcaster whose {appearance['armor_type']} shimmer with protective enchantments.",
            "thief": f"{name} is a cunning rogue whose {appearance['armor_type']} allows for silent movement through shadows.",
            "cleric": f"{name} is a devoted priest whose {appearance['armor_type']} radiate with holy light.",
            "archer": f"{name} is a skilled archer whose {appearance['armor_type']} provide mobility without sacrificing protection.",
            "knight": f"{name} is a noble knight whose {appearance['armor_type']} symbolize honor and duty.",
            "paladin": f"{name} is a holy warrior whose {appearance['armor_type']} shine with divine blessing.",
            "assassin": f"{name} is a deadly assassin whose {appearance['armor_type']} blend seamlessly with darkness.",
            "bard": f"{name} is a charismatic bard whose {appearance['armor_type']} are as colorful as their tales.",
            "monk": f"{name} is a disciplined monk whose {appearance['armor_type']} reflect a life of simplicity.",
        }

        intro = intros.get(char_type, f"{name} is a skilled {char_type} wearing {appearance['armor_type']}.")

        # Weapon detail
        weapon_detail = f"Wielding {appearance['weapon']}, they have proven their worth time and again."

        # Background hint
        backgrounds = [
            "Their past remains shrouded in mystery, known only through reputation.",
            "Rumors speak of a difficult past that forged them into who they are today.",
            "They earned their skills through years of dedicated training.",
            "A tragic event in their youth set them on this path.",
        ]
        background = random.choice(backgrounds)

        # Personality/trait
        traits = [
            "Those who know them speak of unwavering determination.",
            "They are known for their calm demeanor even in chaos.",
            "Their loyalty to their cause is unquestioned.",
            "They possess a sharp wit that catches many off guard.",
        ]
        trait = random.choice(traits)

        full_bio = f"{intro} {weapon_detail} {background} {trait}"

        # Create shorter description (first 2 sentences)
        description = f"{intro} {weapon_detail}"

        return {
            "description": description,
            "note": f"Supporting Character:\n\n{full_bio}",
        }

    def _generate_main_bio(
        self,
        name: str,
        char_type: str,
        appearance: Dict[str, str],
    ) -> Dict[str, str]:
        """Generate detailed bio for main characters (4-8 sentences, 150-300 words)."""

        # Opening paragraph (2-3 sentences)
        openings = {
            "warrior": f"{name} stands as a legendary warrior, their {appearance['armor_type']} bearing witness to a lifetime of battle. Every dent and scratch tells a story of survival against impossible odds. {appearance['weapon'].capitalize()} in hand, they have become a symbol of strength to allies and a harbinger of doom to enemies.",

            "mage": f"{name} has dedicated their life to mastering the arcane arts, their {appearance['armor_type']} woven with protective enchantments accumulated over decades of study. The power channeled through {appearance['weapon']} represents years of dangerous experimentation and forbidden research. Their name is whispered in both awe and fear across magical circles.",

            "thief": f"{name} rose from the gutter streets to become a master of stealth and deception. Their {appearance['armor_type']} have been carefully selected for absolute silence, while {appearance['weapon']} have ended many lives before victims realized danger was near. The thieves' guild speaks of them in hushed, respectful tones.",

            "cleric": f"{name} received a divine calling that changed their life forever. Clad in {appearance['armor_type']} that seem to glow with inner light, they wield {appearance['weapon']} blessed by the gods themselves. Their faith has moved mountains and turned the tide of holy wars.",

            "knight": f"{name} embodies the ideals of chivalry and honor that many have forgotten. Their {appearance['armor_type']} shine not just from polish, but from the righteousness of their cause. {appearance['weapon'].capitalize()} held high, they charge into battle not for glory, but for those who cannot fight for themselves.",

            "paladin": f"{name} walks the sacred path between warrior and priest, their {appearance['armor_type']} radiating divine energy. {appearance['weapon'].capitalize()} serves as both sword and holy symbol, smiting evil wherever it appears. The gods themselves have marked them as a champion of light.",
        }

        opening = openings.get(char_type, f"{name} is a renowned {char_type} whose {appearance['armor_type']} and {appearance['weapon']} are known throughout the land.")

        # Background paragraph (2-3 sentences)
        background = f"Born into humble circumstances, {name} discovered their calling during a moment of crisis that would have broken lesser souls. Through trials that tested both body and spirit, they emerged transformed—no longer the person they once were, but something greater. The path chosen was not easy, marked by loss, sacrifice, and hard-won victories that shaped them into a force to be reckoned with."

        # Personality/motivation (2-3 sentences)
        personality = f"{name} carries themselves with quiet confidence born from countless battles and challenges overcome. Behind their battle-hardened exterior lies a complex person driven by deeply personal motivations that few truly understand. Those fortunate enough to earn their trust discover a fierce loyalty and unwavering dedication that makes them an invaluable ally."

        full_bio = f"{opening}\n\n{background}\n\n{personality}"

        # Create medium-length description (first paragraph)
        return {
            "description": opening,
            "note": f"Main Character:\n\n{full_bio}",
        }

    def _generate_template_bio(
        self,
        character_name: str,
        character_type: str,
        layers: List[Dict],
        importance: CharacterImportance,
    ) -> Dict[str, str]:
        """Generate bio using templates as fallback."""
        appearance = self._analyze_appearance(layers)

        # Use simpler template system
        template = self.templates.get(character_type)
        if not template:
            # Generic fallback
            return {
                "description": f"{character_name} is a {character_type} wearing {appearance['armor_type']}.",
                "note": f"A {character_type} who wields {appearance['weapon']}.",
            }

        # Build bio from template
        intro = random.choice(template.intro_patterns)
        trait = random.choice(template.trait_patterns)

        # Fill in placeholders
        intro = intro.format(
            adjective=random.choice(["skilled", "seasoned", "experienced", "formidable"]),
            armor_type=appearance["armor_type"],
        )
        trait = trait.format(
            trait=random.choice(["exceptional skill", "tactical brilliance", "relentless determination", "unwavering focus"]),
        )

        if importance == CharacterImportance.NPC:
            description = f"{character_name} is {intro}."
            note = f"{description} {trait}."
        elif importance == CharacterImportance.SUPPORTING:
            background = random.choice(template.background_patterns)
            description = f"{character_name} is {intro}. {trait}."
            note = f"{description} {background}."
        else:  # MAIN
            background = random.choice(template.background_patterns)
            motivation = random.choice(template.motivation_patterns or ["Driven by unknown forces."])
            description = f"{character_name} is {intro}. {trait}."
            note = f"{description} {background} {motivation}."

        return {
            "description": description,
            "note": note,
        }


# Convenience function
def generate_character_bio(
    character_name: str,
    character_type: str,
    layers: List[Dict],
    importance: str = "npc",
    use_ai: bool = True,
) -> Dict[str, str]:
    """
    Generate a character bio.

    Args:
        character_name: Name of the character
        character_type: Type/class (warrior, mage, etc.)
        layers: Character layer data
        importance: "npc", "supporting", or "main"
        use_ai: Whether to use AI generation

    Returns:
        Dict with 'description' and 'note' fields
    """
    generator = CharacterBioGenerator()
    importance_level = CharacterImportance(importance.lower())
    return generator.generate_bio(character_name, character_type, layers, importance_level, use_ai)
