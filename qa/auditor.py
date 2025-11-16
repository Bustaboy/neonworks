"""
The Auditor (QA) Agent

This agent is responsible for automated testing of the game by "seeing" the screen
and "playing" the game to verify that quests and other mechanics are working correctly.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pyautogui
import pygame
from PIL import Image

from core.director import Director
from data.config_loader import GameDataLoader

# Configure logging for the Auditor
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("qa/auditor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class Auditor:
    """
    The Auditor agent, a QA tester that can "see" the screen and "play" the game.
    """

    def __init__(self, screen: pygame.Surface, game_data_loader: GameDataLoader):
        """
        Initializes the Auditor agent.

        Args:
            screen: The main Pygame display surface to capture screenshots from.
            game_data_loader: The data loader for accessing game data like quest objectives.
        """
        self.screen = screen
        self.bible = game_data_loader
        self.bug_reports: list[str] = []

    def _get_screen_state(self) -> Image.Image:
        """
        Captures the current state of the Pygame window and returns it as a PIL Image.

        Returns:
            A PIL Image object of the current screen.
        """
        logger.info("Capturing screen state...")
        view = pygame.surfarray.array3d(self.screen)
        # Pygame uses (width, height, channels), PIL uses (height, width, channels)
        # Also, pygame's default is RGB, which is fine.
        view = view.transpose([1, 0, 2])
        image = Image.fromarray(view)
        logger.info("Screen state captured.")
        return image

    def _send_input(self, action: str):
        """
        Sends a keyboard input to the game window.

        Args:
            action: The key to press (e.g., "w", "space", "enter").
        """
        logger.info(f"Sending input: '{action}'")
        pyautogui.press(action)
        # Add a small delay to allow the game to process the input
        time.sleep(0.5)

    def run_test(self, director: Director, test_quest_id: str, max_steps: int = 20):
        """
        Runs an automated test for a given quest.

        The Auditor will loop, getting the quest objective, capturing the screen,
        and using the multimodal 'Auditor' AI to decide the next action.

        Args:
            director: The Director instance to run AI tasks.
            test_quest_id: The ID of the quest to test.
            max_steps: The maximum number of steps to attempt before failing the test.
        """
        logger.info(f"--- Starting test for Quest ID: {test_quest_id} ---")
        self.bug_reports = []

        # 1. Get quest objective from the bible
        quest_objective = "Objective not found."
        try:
            # Assuming quest definitions are in a file specified in project settings
            project = self.bible.project
            if project and project.config and project.config.settings.quest_definitions:
                quest_data = self.bible.load_data(project.config.settings.quest_definitions)
                if "quests" in quest_data and test_quest_id in quest_data["quests"]:
                    quest_details = quest_data["quests"][test_quest_id]
                    quest_objective = quest_details.get("objective", quest_objective)
            logger.info(f"Quest Objective: {quest_objective}")
        except Exception as e:
            self._log_bug(f"Failed to retrieve quest objective for {test_quest_id}: {e}")
            return

        for step in range(max_steps):
            logger.info(f"--- Test Step {step + 1}/{max_steps} ---")

            # 2. Get a screenshot
            screenshot = self._get_screen_state()
            screenshot_path = Path(f"qa/screenshots/step_{step+1}.png")
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot.save(screenshot_path)
            logger.info(f"Saved screenshot to {screenshot_path}")

            # 3. Call director.run_task('Auditor', ...)
            prompt = f"""
            As the Auditor, your task is to test the game to ensure the quest is completable.
            Current Quest Objective: {quest_objective}
            Analyze the attached screenshot and decide the single best keyboard input to perform next.
            Your response should be a single, lowercase key or action word (e.g., 'w', 'a', 's', 'd', 'space', 'enter').
            If you believe the objective is complete, respond with 'objective_complete'.
            If you are stuck or see a bug, respond with 'bug_detected'.
            """

            try:
                # Note: The Director and its `run_task` would need to be updated
                # to handle multimodal prompts (text + image).
                # This is a conceptual implementation.
                # For now, we'll mock a response.
                # In a real implementation, you would pass the image to the director.
                # next_action = director.run_task("Auditor", prompt, image=screenshot)

                # Mocking the response for now
                mock_actions = ["w", "w", "a", "space", "d", "d", "enter", "objective_complete"]
                next_action = mock_actions[step] if step < len(mock_actions) else "bug_detected"
                logger.info(f"AI decision: '{next_action}'")

                if next_action == "objective_complete":
                    logger.info("AI determined the objective is complete. Test successful.")
                    break
                elif next_action == "bug_detected":
                    self._log_bug(f"AI detected a bug or got stuck at step {step + 1}.")
                    break
                else:
                    # 4. Send the decided input
                    self._send_input(next_action)

            except Exception as e:
                self._log_bug(f"An error occurred during AI task execution at step {step + 1}: {e}")
                break
        else:
            self._log_bug(
                f"Test failed: Reached maximum steps ({max_steps}) without completing the objective."
            )

        logger.info(f"--- Test for Quest ID: {test_quest_id} concluded. ---")
        if self.bug_reports:
            logger.warning("--- Bug Reports ---")
            for report in self.bug_reports:
                logger.warning(report)
        else:
            logger.info("No bugs reported.")

    def _log_bug(self, description: str):
        """
        Logs a bug report.

        Args:
            description: A description of the bug.
        """
        logger.error(f"BUG: {description}")
        self.bug_reports.append(description)
