from dataclasses import dataclass
import json

@dataclass
class AgentConfig:
    """Configuration for the AI agent."""
    name: str
    system_prompt: str
    inputs: list[str]
    outputs: list[str]

def load_agent_config() -> AgentConfig:
    """Load agent configuration from config.json."""
    with open("config.json") as f:
        config = json.load(f)
        agent_config = config["agent"]
        return AgentConfig(
            name=agent_config["name"],
            system_prompt=agent_config["systemPrompt"],
            inputs=agent_config["inputs"],
            outputs=agent_config["outputs"]
        ) 