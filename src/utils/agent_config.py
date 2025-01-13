from dataclasses import dataclass
import json
import logging
from typing import Optional, Dict

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    verbose: bool
    log_file: Optional[str]
    levels: Dict[str, str]

@dataclass
class AgentConfig:
    """Configuration for the AI agent."""
    name: str
    system_prompt: str
    logging: LoggingConfig

def configure_logging(config: LoggingConfig) -> None:
    """Configure logging based on settings."""
    # Base logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure handlers
    handlers = []
    if config.log_file:
        handlers.append(logging.FileHandler(config.log_file))
    handlers.append(logging.StreamHandler())
    
    # Set logging level based on verbose flag
    base_level = logging.DEBUG if config.verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=base_level,
        format=log_format,
        handlers=handlers
    )
    
    # Configure specific loggers
    for logger_name, level in config.levels.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))

def load_agent_config() -> AgentConfig:
    """Load agent configuration from config.json."""
    with open("config.json") as f:
        config = json.load(f)
        agent_config = config["agent"]
        logging_config = LoggingConfig(
            verbose=config["logging"]["verbose"],
            log_file=config["logging"]["logFile"],
            levels=config["logging"]["levels"]
        )
        
        # Configure logging
        configure_logging(logging_config)
        
        return AgentConfig(
            name=agent_config["name"],
            system_prompt=agent_config["systemPrompt"],
            logging=logging_config
        ) 