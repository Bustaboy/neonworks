"""
Character Generator UI

Visual interface for AI-powered character generation with sprite preview.

Hotkey: Ctrl+G
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

import pygame

from neonworks.ui.ui_system import (
    Panel,
    Button,
    Label,
    TextInput,
    Dropdown,
    Checkbox,
    ScrollPanel,
)


class CharacterGeneratorUI:
    """
    Visual character generator with AI assistance.

    Features:
    - Text-based character description input
    - AI-powered character generation (if available)
    - Manual stat configuration
    - Sprite/portrait assignment
    - Character preview
    - Export to database
    - Archetype templates
    """

    # Character archetypes
    ARCHETYPES = [
        "Warrior",
        "Mage",
        "Rogue",
        "Cleric",
        "Paladin",
        "Ranger",
        "Barbarian",
        "Monk",
        "Bard",
        "Custom",
    ]

    # Character classes
    CLASSES = ["hero", "enemy", "npc", "boss"]

    def __init__(self, world, renderer, project_path: Optional[str] = None):
        """Initialize character generator UI."""
        self.world = world
        self.renderer = renderer
        self.visible = False
        self.project_path = project_path or ""

        # Generated character state
        self.character = self._default_character()
        self.ai_available = self._check_ai_available()

        # UI elements
        self._create_ui()

    def _check_ai_available(self) -> bool:
        """Check if AI character generator is available."""
        try:
            from neonworks.editor.ai_character_generator import AICharacterGenerator

            return True
        except ImportError:
            return False

    def _default_character(self) -> Dict[str, Any]:
        """Create a default character template."""
        return {
            "id": "new_character",
            "name": "New Character",
            "description": "",
            "level": 1,
            "class": "hero",
            "stats": {
                "hp": 100,
                "max_hp": 100,
                "mp": 50,
                "max_mp": 50,
                "attack": 10,
                "defense": 10,
                "magic_attack": 5,
                "magic_defense": 5,
                "speed": 10,
                "luck": 5,
            },
            "sprite": "",
            "portrait": "",
            "skills": [],
            "equipment": {},
        }

    def _create_ui(self):
        """Create UI elements."""
        screen_width = 1280
        screen_height = 720

        # Main panel
        self.main_panel = Panel(
            x=50,
            y=50,
            width=screen_width - 100,
            height=screen_height - 100,
            color=(40, 40, 50),
        )

        # Title
        self.title_label = Label(
            text="Character Generator (Ctrl+G)",
            x=70,
            y=70,
            font_size=24,
            color=(255, 255, 255),
        )

        # Left panel - Input
        self.input_panel = Panel(x=70, y=120, width=550, height=500, color=(50, 50, 60))

        self.input_label = Label(
            text="Character Input:", x=80, y=130, font_size=16, color=(200, 200, 200)
        )

        # Archetype selector
        self.archetype_label = Label(text="Archetype:", x=80, y=170, font_size=14)
        self.archetype_dropdown = Dropdown(
            x=180, y=165, width=150, height=30, options=self.ARCHETYPES
        )

        # Class selector
        self.class_label = Label(text="Class:", x=350, y=170, font_size=14)
        self.class_dropdown = Dropdown(
            x=420, y=165, width=120, height=30, options=self.CLASSES
        )

        # Character ID
        self.id_label = Label(text="ID:", x=80, y=210, font_size=14)
        self.id_input = TextInput(x=180, y=205, width=360, height=30)

        # Character name
        self.name_label = Label(text="Name:", x=80, y=250, font_size=14)
        self.name_input = TextInput(x=180, y=245, width=360, height=30)

        # Description (AI input)
        self.desc_label = Label(text="Description:", x=80, y=290, font_size=14)
        self.desc_help = Label(
            text="Describe your character for AI generation",
            x=80,
            y=315,
            font_size=10,
            color=(150, 150, 150),
        )
        self.desc_input = TextInput(x=80, y=335, width=520, height=80, multiline=True)

        # Stats section
        self.stats_label = Label(text="Base Stats:", x=80, y=430, font_size=14)

        # HP
        self.hp_label = Label(text="HP:", x=80, y=460, font_size=12)
        self.hp_input = TextInput(x=150, y=455, width=80, height=25)

        # MP
        self.mp_label = Label(text="MP:", x=250, y=460, font_size=12)
        self.mp_input = TextInput(x=300, y=455, width=80, height=25)

        # Attack
        self.atk_label = Label(text="ATK:", x=400, y=460, font_size=12)
        self.atk_input = TextInput(x=460, y=455, width=80, height=25)

        # Defense
        self.def_label = Label(text="DEF:", x=80, y=495, font_size=12)
        self.def_input = TextInput(x=150, y=490, width=80, height=25)

        # Magic Attack
        self.matk_label = Label(text="M.ATK:", x=250, y=495, font_size=12)
        self.matk_input = TextInput(x=315, y=490, width=65, height=25)

        # Magic Defense
        self.mdef_label = Label(text="M.DEF:", x=400, y=495, font_size=12)
        self.mdef_input = TextInput(x=465, y=490, width=75, height=25)

        # Speed
        self.spd_label = Label(text="SPD:", x=80, y=530, font_size=12)
        self.spd_input = TextInput(x=150, y=525, width=80, height=25)

        # Luck
        self.luck_label = Label(text="LUCK:", x=250, y=530, font_size=12)
        self.luck_input = TextInput(x=315, y=525, width=65, height=25)

        # Level
        self.level_label = Label(text="LVL:", x=400, y=530, font_size=12)
        self.level_input = TextInput(x=450, y=525, width=90, height=25)

        # Right panel - Preview & Output
        self.preview_panel = Panel(x=650, y=120, width=500, height=500, color=(50, 50, 60))

        self.preview_label = Label(
            text="Character Preview:", x=660, y=130, font_size=16, color=(200, 200, 200)
        )

        # Character preview area (sprite/portrait would go here)
        self.preview_bg = Panel(x=660, y=170, width=200, height=200, color=(30, 30, 40))

        # Output JSON preview
        self.output_label = Label(
            text="Generated Data:", x=660, y=390, font_size=14, color=(200, 200, 200)
        )

        self.output_scroll = ScrollPanel(x=660, y=420, width=470, height=180, color=(30, 30, 40))

        # Buttons
        if self.ai_available:
            self.generate_button = Button(
                text="AI Generate",
                x=70,
                y=640,
                width=150,
                height=35,
                on_click=self.ai_generate,
            )
        else:
            self.generate_button = Button(
                text="AI Unavailable",
                x=70,
                y=640,
                width=150,
                height=35,
                enabled=False,
            )

        self.apply_archetype_button = Button(
            text="Apply Archetype",
            x=230,
            y=640,
            width=150,
            height=35,
            on_click=self.apply_archetype,
        )

        self.randomize_button = Button(
            text="Randomize Stats",
            x=390,
            y=640,
            width=150,
            height=35,
            on_click=self.randomize_stats,
        )

        self.export_button = Button(
            text="Export to DB",
            x=900,
            y=640,
            width=120,
            height=35,
            on_click=self.export_character,
        )

        self.clear_button = Button(
            text="Clear", x=1030, y=640, width=70, height=35, on_click=self.clear_character
        )

        self.close_button = Button(
            text="Close", x=1110, y=640, width=70, height=35, on_click=self.close
        )

    def apply_archetype(self):
        """Apply selected archetype template."""
        archetype = self.archetype_dropdown.selected

        # Archetype stat templates
        templates = {
            "Warrior": {
                "hp": 120,
                "mp": 20,
                "attack": 15,
                "defense": 12,
                "magic_attack": 3,
                "magic_defense": 5,
                "speed": 8,
                "luck": 5,
            },
            "Mage": {
                "hp": 70,
                "mp": 100,
                "attack": 5,
                "defense": 6,
                "magic_attack": 20,
                "magic_defense": 15,
                "speed": 7,
                "luck": 7,
            },
            "Rogue": {
                "hp": 90,
                "mp": 30,
                "attack": 12,
                "defense": 8,
                "magic_attack": 5,
                "magic_defense": 7,
                "speed": 16,
                "luck": 12,
            },
            "Cleric": {
                "hp": 85,
                "mp": 80,
                "attack": 6,
                "defense": 10,
                "magic_attack": 15,
                "magic_defense": 18,
                "speed": 9,
                "luck": 8,
            },
            "Paladin": {
                "hp": 110,
                "mp": 50,
                "attack": 13,
                "defense": 14,
                "magic_attack": 8,
                "magic_defense": 12,
                "speed": 7,
                "luck": 6,
            },
            "Ranger": {
                "hp": 95,
                "mp": 40,
                "attack": 14,
                "defense": 9,
                "magic_attack": 7,
                "magic_defense": 8,
                "speed": 13,
                "luck": 10,
            },
            "Barbarian": {
                "hp": 130,
                "mp": 10,
                "attack": 18,
                "defense": 11,
                "magic_attack": 2,
                "magic_defense": 4,
                "speed": 6,
                "luck": 4,
            },
            "Monk": {
                "hp": 100,
                "mp": 60,
                "attack": 11,
                "defense": 10,
                "magic_attack": 10,
                "magic_defense": 10,
                "speed": 14,
                "luck": 9,
            },
            "Bard": {
                "hp": 80,
                "mp": 70,
                "attack": 7,
                "defense": 7,
                "magic_attack": 12,
                "magic_defense": 10,
                "speed": 11,
                "luck": 15,
            },
        }

        if archetype in templates:
            stats = templates[archetype]
            self.character["stats"]["hp"] = stats["hp"]
            self.character["stats"]["max_hp"] = stats["hp"]
            self.character["stats"]["mp"] = stats["mp"]
            self.character["stats"]["max_mp"] = stats["mp"]
            self.character["stats"]["attack"] = stats["attack"]
            self.character["stats"]["defense"] = stats["defense"]
            self.character["stats"]["magic_attack"] = stats["magic_attack"]
            self.character["stats"]["magic_defense"] = stats["magic_defense"]
            self.character["stats"]["speed"] = stats["speed"]
            self.character["stats"]["luck"] = stats["luck"]

            # Update UI
            self._load_character_to_ui()

    def randomize_stats(self):
        """Randomize character stats."""
        import random

        self.character["stats"]["hp"] = random.randint(60, 150)
        self.character["stats"]["max_hp"] = self.character["stats"]["hp"]
        self.character["stats"]["mp"] = random.randint(10, 100)
        self.character["stats"]["max_mp"] = self.character["stats"]["mp"]
        self.character["stats"]["attack"] = random.randint(5, 20)
        self.character["stats"]["defense"] = random.randint(5, 20)
        self.character["stats"]["magic_attack"] = random.randint(2, 25)
        self.character["stats"]["magic_defense"] = random.randint(3, 20)
        self.character["stats"]["speed"] = random.randint(5, 18)
        self.character["stats"]["luck"] = random.randint(3, 15)

        self._load_character_to_ui()

    def ai_generate(self):
        """Generate character using AI."""
        if not self.ai_available:
            print("AI character generator not available")
            return

        description = self.desc_input.text
        if not description:
            print("Please enter a character description")
            return

        try:
            from neonworks.editor.ai_character_generator import AICharacterGenerator

            generator = AICharacterGenerator()

            # Generate character from description
            # Note: This is a simplified version - full implementation would use AI
            archetype = self.archetype_dropdown.selected
            char_name = self.name_input.text or "Generated Character"

            print(f"Generating {archetype} character: {char_name}")
            print(f"Description: {description}")

            # Apply archetype stats as base
            self.apply_archetype()

            # Update description
            self.character["description"] = description
            self.character["name"] = char_name

            print("Character generated successfully!")

        except Exception as e:
            print(f"Error generating character: {e}")

    def export_character(self):
        """Export character to database."""
        if not self.project_path:
            print("No project loaded. Set project path first.")
            return

        # Save current UI state to character
        self._save_ui_to_character()

        # Load existing characters
        char_file = Path(self.project_path) / "config" / "characters.json"

        try:
            if char_file.exists():
                with open(char_file, "r") as f:
                    data = json.load(f)
            else:
                data = {"characters": []}

            # Add/update character
            characters = data.get("characters", [])

            # Check if character already exists
            existing = None
            for i, char in enumerate(characters):
                if char.get("id") == self.character["id"]:
                    existing = i
                    break

            if existing is not None:
                characters[existing] = self.character
                print(f"Updated character: {self.character['id']}")
            else:
                characters.append(self.character)
                print(f"Added new character: {self.character['id']}")

            data["characters"] = characters

            # Save file
            char_file.parent.mkdir(parents=True, exist_ok=True)
            with open(char_file, "w") as f:
                json.dump(data, f, indent=2)

            print(f"Character exported to {char_file}")

        except Exception as e:
            print(f"Error exporting character: {e}")

    def clear_character(self):
        """Clear current character and reset to default."""
        self.character = self._default_character()
        self._load_character_to_ui()

    def _save_ui_to_character(self):
        """Save UI input to character object."""
        self.character["id"] = self.id_input.text
        self.character["name"] = self.name_input.text
        self.character["description"] = self.desc_input.text
        self.character["class"] = self.class_dropdown.selected

        # Parse numeric inputs
        try:
            self.character["level"] = int(self.level_input.text or "1")
            self.character["stats"]["hp"] = int(self.hp_input.text or "100")
            self.character["stats"]["max_hp"] = self.character["stats"]["hp"]
            self.character["stats"]["mp"] = int(self.mp_input.text or "50")
            self.character["stats"]["max_mp"] = self.character["stats"]["mp"]
            self.character["stats"]["attack"] = int(self.atk_input.text or "10")
            self.character["stats"]["defense"] = int(self.def_input.text or "10")
            self.character["stats"]["magic_attack"] = int(self.matk_input.text or "5")
            self.character["stats"]["magic_defense"] = int(self.mdef_input.text or "5")
            self.character["stats"]["speed"] = int(self.spd_input.text or "10")
            self.character["stats"]["luck"] = int(self.luck_input.text or "5")
        except ValueError as e:
            print(f"Invalid numeric input: {e}")

    def _load_character_to_ui(self):
        """Load character data to UI inputs."""
        self.id_input.text = self.character.get("id", "")
        self.name_input.text = self.character.get("name", "")
        self.desc_input.text = self.character.get("description", "")
        self.class_dropdown.selected = self.character.get("class", "hero")
        self.level_input.text = str(self.character.get("level", 1))

        stats = self.character.get("stats", {})
        self.hp_input.text = str(stats.get("hp", 100))
        self.mp_input.text = str(stats.get("mp", 50))
        self.atk_input.text = str(stats.get("attack", 10))
        self.def_input.text = str(stats.get("defense", 10))
        self.matk_input.text = str(stats.get("magic_attack", 5))
        self.mdef_input.text = str(stats.get("magic_defense", 5))
        self.spd_input.text = str(stats.get("speed", 10))
        self.luck_input.text = str(stats.get("luck", 5))

    def update(self, dt: float):
        """Update character generator."""
        if not self.visible:
            return

        # Update UI elements
        self.main_panel.update(dt)
        self.archetype_dropdown.update(dt)
        self.class_dropdown.update(dt)
        self.id_input.update(dt)
        self.name_input.update(dt)
        self.desc_input.update(dt)

        # Update stat inputs
        self.hp_input.update(dt)
        self.mp_input.update(dt)
        self.atk_input.update(dt)
        self.def_input.update(dt)
        self.matk_input.update(dt)
        self.mdef_input.update(dt)
        self.spd_input.update(dt)
        self.luck_input.update(dt)
        self.level_input.update(dt)

        # Update buttons
        self.generate_button.update(dt)
        self.apply_archetype_button.update(dt)
        self.randomize_button.update(dt)
        self.export_button.update(dt)
        self.clear_button.update(dt)
        self.close_button.update(dt)

        # Save UI to character periodically
        self._save_ui_to_character()

    def render(self, screen: pygame.Surface):
        """Render character generator UI."""
        if not self.visible:
            return

        # Render panels
        self.main_panel.render(screen)
        self.title_label.render(screen)

        # Render input panel
        self.input_panel.render(screen)
        self.input_label.render(screen)
        self.archetype_label.render(screen)
        self.archetype_dropdown.render(screen)
        self.class_label.render(screen)
        self.class_dropdown.render(screen)
        self.id_label.render(screen)
        self.id_input.render(screen)
        self.name_label.render(screen)
        self.name_input.render(screen)
        self.desc_label.render(screen)
        self.desc_help.render(screen)
        self.desc_input.render(screen)

        # Render stats section
        self.stats_label.render(screen)
        self.hp_label.render(screen)
        self.hp_input.render(screen)
        self.mp_label.render(screen)
        self.mp_input.render(screen)
        self.atk_label.render(screen)
        self.atk_input.render(screen)
        self.def_label.render(screen)
        self.def_input.render(screen)
        self.matk_label.render(screen)
        self.matk_input.render(screen)
        self.mdef_label.render(screen)
        self.mdef_input.render(screen)
        self.spd_label.render(screen)
        self.spd_input.render(screen)
        self.luck_label.render(screen)
        self.luck_input.render(screen)
        self.level_label.render(screen)
        self.level_input.render(screen)

        # Render preview panel
        self.preview_panel.render(screen)
        self.preview_label.render(screen)
        self.preview_bg.render(screen)

        # Character name preview
        char_name = self.character.get("name", "Unknown")
        name_preview = Label(
            text=char_name, x=680, y=250, font_size=18, color=(255, 255, 100)
        )
        name_preview.render(screen)

        # Character class preview
        char_class = self.character.get("class", "hero").upper()
        class_preview = Label(text=char_class, x=680, y=280, font_size=14, color=(150, 150, 255))
        class_preview.render(screen)

        # Level preview
        level = self.character.get("level", 1)
        level_preview = Label(text=f"Level {level}", x=680, y=310, font_size=14)
        level_preview.render(screen)

        # Stats summary
        stats = self.character.get("stats", {})
        stats_text = f"HP: {stats.get('hp', 0)}  MP: {stats.get('mp', 0)}  ATK: {stats.get('attack', 0)}"
        stats_preview = Label(text=stats_text, x=680, y=340, font_size=12, color=(200, 200, 200))
        stats_preview.render(screen)

        # Render output
        self.output_label.render(screen)
        self.output_scroll.render(screen)

        # Render character JSON
        char_json = json.dumps(self.character, indent=2)
        lines = char_json.split("\n")

        y_offset = 430
        for line in lines[:10]:  # Show first 10 lines
            if len(line) > 60:
                line = line[:57] + "..."

            line_label = Label(text=line, x=670, y=y_offset, font_size=10, color=(220, 220, 220))
            line_label.render(screen)
            y_offset += 16

        # Render buttons
        self.generate_button.render(screen)
        self.apply_archetype_button.render(screen)
        self.randomize_button.render(screen)
        self.export_button.render(screen)
        self.clear_button.render(screen)
        self.close_button.render(screen)

    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if not self.visible:
            return

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return

            # Ctrl+G to toggle
            if event.key == pygame.K_g and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.toggle()
                return

        # Handle UI events
        self.archetype_dropdown.handle_event(event)
        self.class_dropdown.handle_event(event)
        self.id_input.handle_event(event)
        self.name_input.handle_event(event)
        self.desc_input.handle_event(event)

        # Handle stat inputs
        self.hp_input.handle_event(event)
        self.mp_input.handle_event(event)
        self.atk_input.handle_event(event)
        self.def_input.handle_event(event)
        self.matk_input.handle_event(event)
        self.mdef_input.handle_event(event)
        self.spd_input.handle_event(event)
        self.luck_input.handle_event(event)
        self.level_input.handle_event(event)

        # Handle buttons
        self.generate_button.handle_event(event)
        self.apply_archetype_button.handle_event(event)
        self.randomize_button.handle_event(event)
        self.export_button.handle_event(event)
        self.clear_button.handle_event(event)
        self.close_button.handle_event(event)

    def set_project_path(self, path: str):
        """Set project path for export."""
        self.project_path = path

    def toggle(self):
        """Toggle character generator visibility."""
        self.visible = not self.visible
        if self.visible:
            self._load_character_to_ui()

    def close(self):
        """Close character generator."""
        self.visible = False


def get_character_generator(world, renderer, project_path: Optional[str] = None):
    """Get or create character generator instance."""
    if not hasattr(get_character_generator, "_instance"):
        get_character_generator._instance = CharacterGeneratorUI(world, renderer, project_path)
    return get_character_generator._instance
