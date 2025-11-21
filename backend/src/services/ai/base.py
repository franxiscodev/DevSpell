"""
Interface base para providers de IA.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AIProvider(ABC):
    """Interface base para providers de IA."""

    @abstractmethod
    async def generate_suggestions(self, code: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Genera sugerencias de mejora para el código analizado.

        Args:
            code: Código fuente a analizar
            analysis: Resultados del análisis estático (complejidad, métricas, etc.)

        Returns:
            Lista de sugerencias de mejora
        """
        pass

    @abstractmethod
    async def explain_function(self, function_code: str, function_name: str) -> str:
        """
        Explica qué hace una función específica.

        Args:
            function_code: Código de la función
            function_name: Nombre de la función

        Returns:
            Explicación detallada de la función
        """
        pass

    @abstractmethod
    async def optimize_code(self, code: str) -> str:
        """
        Optimiza el código reduciendo complejidad.

        Args:
            code: Código fuente a optimizar

        Returns:
            Código optimizado con comentarios explicando mejoras
        """
        pass
