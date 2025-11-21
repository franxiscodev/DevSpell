"""
Servicios de IA para análisis de código.
"""
from src.core.config import settings
from .base import AIProvider
from .ollama_provider import OllamaProvider


def get_ai_provider() -> AIProvider:
    """
    Factory para obtener el provider de IA configurado.

    Returns:
        AIProvider: Instancia del provider configurado

    Raises:
        ValueError: Si el provider configurado no es válido
    """
    if settings.ai_provider == "ollama":
        return OllamaProvider()
    # Futuro: elif settings.ai_provider == "gemini": return GeminiProvider()
    else:
        raise ValueError(f"Unknown AI provider: {settings.ai_provider}")


__all__ = ["AIProvider", "OllamaProvider", "get_ai_provider"]
