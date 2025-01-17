"""Model handler for managing different LLM providers."""

from typing import Any, Dict, Optional
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

class ModelHandler:
    """Handler class for managing different LLM providers."""
    
    SUPPORTED_PROVIDERS = {
        "groq": ChatGroq,
        "anthropic": ChatAnthropic,
        "ollama": ChatOllama
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the model handler with configuration.
        
        Args:
            config: Dictionary containing model configuration with keys:
                - provider: The model provider (e.g., "groq", "anthropic")
                - name: The model name
                - options: Additional model options
        """
        self.config = config
        self._model: Optional[BaseChatModel] = None
        
    def get_model(self) -> BaseChatModel:
        """Get or create the language model instance.
        
        Returns:
            BaseChatModel: The configured language model instance
        
        Raises:
            ValueError: If the provider is not supported
        """
        if self._model is None:
            provider = self.config["provider"].lower()
            if provider not in self.SUPPORTED_PROVIDERS:
                raise ValueError(f"Unsupported model provider: {provider}. "
                              f"Supported providers are: {list(self.SUPPORTED_PROVIDERS.keys())}")
            
            model_class = self.SUPPORTED_PROVIDERS[provider]
            model_kwargs = {
                "model": self.config["name"]
            }
            
            # Add any additional options from config
            if "options" in self.config:
                model_kwargs.update(self.config["options"])
                
            self._model = model_class(**model_kwargs)
            
        return self._model
