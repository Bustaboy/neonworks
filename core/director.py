# core/director.py

import gc
from pathlib import Path
from llama_cpp import Llama

class Director:
    """
    The Director agent is the master orchestrator of the multi-agent system.
    It manages the loading and unloading of specialized agents to perform tasks
    while staying within a strict VRAM budget.
    """

    def __init__(self):
        """
        Initializes the Director, setting up the paths and model mappings for all agents.
        """
        self.base_path = Path(__file__).parent.parent  # Root of the neonworks project
        self.models_path = self.base_path / "models"
        self.personas_path = self.base_path / "prompts"

        # Map agent names to their corresponding GGUF model files.
        # This allows for easy swapping and management of different models for different tasks.
        self.agent_model_map = {
            "Loremaster": "nous-hermes-2-solar-10.7b.Q4_K_M.gguf",
            "Auditor": "llava-v1.5-7b-Q4_K.gguf",  # Placeholder for a multimodal vision model
            "Architect": "deepseek-coder-6.7b-instruct.Q4_K_M.gguf",
            # The Director can use a general-purpose model for complex reasoning and planning.
            "Director": "nous-hermes-2-solar-10.7b.Q4_K_M.gguf",
        }

        self.loaded_agent_name = None
        self.loaded_model = None

    def _get_agent_model_path(self, agent_name: str) -> Path:
        """
        Retrieves the full path to an agent's GGUF model file.

        Args:
            agent_name: The name of the agent.

        Returns:
            A Path object to the agent's model file.
        """
        model_filename = self.agent_model_map.get(agent_name)
        if not model_filename:
            raise ValueError(f"No model is configured for agent: {agent_name}")
        
        model_path = self.models_path / model_filename
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found for agent {agent_name}: {model_path}\n"
                f"Please ensure the model is downloaded and placed in the '{self.models_path}' directory."
            )
        return model_path

    def _get_agent_persona(self, agent_name: str) -> str:
        """
        Retrieves the system prompt (persona) for a given agent.

        Args:
            agent_name: The name of the agent.

        Returns:
            The content of the agent's persona file as a string.
        """
        persona_path = self.personas_path / f"{agent_name.lower()}.md"
        if not persona_path.exists():
            raise FileNotFoundError(f"Persona file not found for agent {agent_name}: {persona_path}")
        
        with open(persona_path, "r", encoding="utf-8") as f:
            return f.read()

    def run_task(self, agent_name: str, prompt_text: str) -> str:
        """
        Runs a task by dynamically loading an agent, executing the prompt, and unloading it.
        This "load, execute, unload" cycle is critical for managing VRAM.

        Args:
            agent_name: The name of the specialized agent to use.
            prompt_text: The user prompt describing the task for the agent.

        Returns:
            The text response from the agent.
        """
        print(f"--- Director: Initiating task for agent: {agent_name} ---")
        
        try:
            # 1. Load Agent and Model into VRAM
            print(f"Loading {agent_name} agent and model...")
            model_path = self._get_agent_model_path(agent_name)
            persona_prompt = self._get_agent_persona(agent_name)
            
            self.loaded_model = Llama(
                model_path=str(model_path),
                n_gpu_layers=-1,  # Offload all possible layers to GPU
                verbose=False
            )
            self.loaded_agent_name = agent_name
            print(f"Agent {agent_name} loaded successfully.")

            # 2. Execute the Task
            print("Executing task...")
            messages = [
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": prompt_text},
            ]

            completion = self.loaded_model.create_chat_completion(messages=messages)
            response_text = completion['choices'][0]['message']['content']
            print("Task executed.")

            return response_text

finally:
            # 3. Unload Agent and Model from VRAM
            if self.loaded_model is not None:
                print(f"Unloading {self.loaded_agent_name} agent to free VRAM...")
                self.loaded_model = None
                self.loaded_agent_name = None
                # Force garbage collection to release VRAM immediately
                gc.collect()
                print("Agent unloaded. VRAM freed.")
            print(f"--- Director: Task for agent {agent_name} concluded. ---")

# Example usage:
if __name__ == '__main__':
    # This block demonstrates how the Director would be used.
    # It requires the models and prompts to be in the correct directories.
    
    # Create a dummy model and prompt file for testing purposes
    # In a real scenario, these files would already exist.
    
    # Create dummy directories
    Path("models").mkdir(exist_ok=True)
    Path("prompts").mkdir(exist_ok=True)

    # Create a dummy Loremaster persona
    loremaster_persona_content = """
    # Agent Persona: The Loremaster
    You are a master storyteller. Your task is to write beautiful and engaging fantasy lore.
    """
    with open("prompts/loremaster.md", "w") as f:
        f.write(loremaster_persona_content)

    # To make this example runnable without a real model, we can't create a dummy GGUF.
    # We will catch the FileNotFoundError and print a helpful message.
    
    try:
        director = Director()
        task_prompt = "Write a short description for a mythical sword named 'Starfire'."
        response = director.run_task("Loremaster", task_prompt)
        print("\n--- Response from Loremaster ---")
        print(response)
    except (ValueError, FileNotFoundError) as e:
        print(f"\n[ERROR] Could not run example: {e}")
        print("This is expected if you have not downloaded the required GGUF models.")
