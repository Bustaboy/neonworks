from pathlib import Path
from typing import Any, Dict, Optional

from core.director import Director
from core.project import Project, get_current_project
from data.config_loader import GameDataLoader


class GenerativeDialogueManager:
    """
    Manages the generation of dynamic dialogue using an AI agent (Loremaster).
    """

    def __init__(self):
        self._game_data_loader: Optional[GameDataLoader] = None
        self._project: Optional[Project] = None

    def _get_game_data_loader(self) -> Optional[GameDataLoader]:
        """Lazily loads and returns the GameDataLoader."""
        if self._game_data_loader is None:
            self._project = get_current_project()
            if self._project and self._project.root_dir:
                self._game_data_loader = GameDataLoader(self._project.root_dir)
            else:
                print(
                    "Warning: No active project or project root directory found for GameDataLoader."
                )
        return self._game_data_loader

    def get_dialogue(self, director: Director, event_context: Dict[str, Any]) -> str:
        """
        Generates dialogue based on game context using the Loremaster AI agent.

        Args:
            director: The Director instance to run AI tasks.
            event_context: A dictionary containing context for dialogue generation,
                           e.g., {"npc_id": "villager_01", "quest_status": "started_quest_x"}.

        Returns:
            A string containing the generated dialogue.
        """
        game_data_loader = self._get_game_data_loader()
        if not game_data_loader:
            return "Error: Game data loader not initialized. Cannot generate dialogue."

        # Extract context from event_context
        npc_id = event_context.get("npc_id")
        player_quest_status = event_context.get("player_quest_status")
        current_location = event_context.get("current_location")
        time_of_day = event_context.get("time_of_day")

        # Query existing game data for context
        npc_personality = {}
        quest_details = {}

        project = get_current_project()
        if project and project.config and project.config.settings:
            # Load character definitions
            char_def_file = project.config.settings.character_definitions
            if char_def_file:
                try:
                    character_data = game_data_loader.load_data(char_def_file)
                    if (
                        npc_id
                        and "characters" in character_data
                        and npc_id in character_data["characters"]
                    ):
                        npc_personality = character_data["characters"][npc_id]
                except FileNotFoundError:
                    print(f"Warning: Character definitions file '{char_def_file}' not found.")
                except Exception as e:
                    print(f"Error loading character definitions: {e}")

            # Load quest definitions
            quest_def_file = project.config.settings.quest_definitions
            if quest_def_file:
                try:
                    quest_data = game_data_loader.load_data(quest_def_file)
                    if (
                        player_quest_status
                        and "quests" in quest_data
                        and player_quest_status in quest_data["quests"]
                    ):
                        quest_details = quest_data["quests"][player_quest_status]
                except FileNotFoundError:
                    print(f"Warning: Quest definitions file '{quest_def_file}' not found.")
                except Exception as e:
                    print(f"Error loading quest definitions: {e}")

        # Construct a detailed prompt for the Loremaster
        prompt_parts = [
            "Generate a short, engaging dialogue line for an NPC.",
            f"NPC ID: {npc_id}",
            f"Current Location: {current_location}",
            f"Time of Day: {time_of_day}",
        ]

        if npc_personality:
            prompt_parts.append(f"NPC Personality: {npc_personality.get('description', 'N/A')}")
            prompt_parts.append(f"NPC Traits: {', '.join(npc_personality.get('traits', []))}")
            prompt_parts.append(f"NPC Mood: {npc_personality.get('mood', 'neutral')}")

        if player_quest_status:
            prompt_parts.append(f"Player Quest Status: {player_quest_status}")
            if quest_details:
                prompt_parts.append(f"Quest Name: {quest_details.get('name', 'N/A')}")
                prompt_parts.append(f"Quest Objective: {quest_details.get('objective', 'N/A')}")
                prompt_parts.append(f"Quest Stage: {quest_details.get('stage', 'N/A')}")

        final_prompt = "\n".join(prompt_parts)
        print(f"Sending prompt to Loremaster:\n{final_prompt}")

        # Call the Loremaster AI agent
        try:
            dialogue = director.run_task("Loremaster", final_prompt)
            return dialogue
        except Exception as e:
            return f"Error generating dialogue with Loremaster: {e}"
