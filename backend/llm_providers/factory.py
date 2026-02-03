"""
Factory for creating LLM provider instances based on configuration.
"""

from .base import LLMProvider
from .ollama_provider import OllamaProvider
from config import settings


def create_llm_provider() -> LLMProvider:
    """
    Create an LLM provider based on application settings.
    
    Returns:
        Configured LLM provider instance
        
    Raises:
        ValueError: If provider is not supported or not configured
    """
    provider_name = settings.llm_provider.lower()
    
    if provider_name == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model
        )
    
    elif provider_name == "openai":
        # TODO: Implement OpenAI provider
        raise NotImplementedError("OpenAI provider not yet implemented")
    
    elif provider_name == "claude":
        # TODO: Implement Claude provider
        raise NotImplementedError("Claude provider not yet implemented")
    
    elif provider_name == "gemini":
        # TODO: Implement Gemini provider
        raise NotImplementedError("Gemini provider not yet implemented")
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
