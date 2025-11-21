"""
Provider de IA usando Ollama (local).
"""
import aiohttp
from typing import List, Dict, Any
from src.core.config import settings
from src.core.logger import logger
from .base import AIProvider
from .prompts import SUGGESTION_PROMPT, EXPLAIN_PROMPT, OPTIMIZE_PROMPT


class OllamaProvider(AIProvider):
    """Provider de IA usando Ollama local."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        logger.info(f"🤖 OllamaProvider initialized: {self.model} at {self.base_url}")

    async def _generate(self, prompt: str) -> str:
        """
        Llamada interna a Ollama API.

        Args:
            prompt: Prompt a enviar al modelo

        Returns:
            Respuesta generada por el modelo

        Raises:
            Exception: Si hay error en la comunicación con Ollama
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 500,  # Máximo tokens de respuesta
            }
        }

        try:
            logger.debug(f"Calling Ollama: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        generated_text = result.get("response", "")
                        logger.debug(f"Ollama response: {len(generated_text)} chars")
                        return generated_text
                    else:
                        error = await response.text()
                        logger.error(f"Ollama error: {error}")
                        raise Exception(f"Ollama returned status {response.status}: {error}")
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to Ollama: {e}")
            raise Exception(f"Failed to connect to Ollama: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            raise

    async def generate_suggestions(self, code: str, analysis: Dict[str, Any]) -> List[str]:
        """Genera sugerencias de mejora para el código."""
        prompt = SUGGESTION_PROMPT.format(
            code=code,
            complexity=analysis.get("complexity", "N/A"),
            num_functions=analysis.get("num_functions", 0),
            code_lines=analysis.get("code_lines", 0)
        )

        try:
            response = await self._generate(prompt)

            # Parsear respuesta: buscar líneas numeradas
            suggestions = []
            for line in response.split("\n"):
                line = line.strip()
                # Buscar líneas que empiecen con número seguido de punto o paréntesis
                if line and len(line) > 2:
                    if line[0].isdigit() and line[1] in ('.', ')', ':'):
                        # Remover el número inicial y limpiar
                        suggestion = line[2:].strip()
                        if suggestion:
                            suggestions.append(suggestion)

            # Si no encontramos formato numerado, dividir por saltos de línea dobles
            if not suggestions:
                suggestions = [s.strip() for s in response.split("\n\n") if s.strip()]

            # Limitar a 5 sugerencias
            return suggestions[:5] if suggestions else ["No suggestions generated"]

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return [f"Error generating suggestions: {str(e)}"]

    async def explain_function(self, function_code: str, function_name: str) -> str:
        """Explica qué hace una función específica."""
        prompt = EXPLAIN_PROMPT.format(
            function_name=function_name,
            function_code=function_code
        )

        try:
            return await self._generate(prompt)
        except Exception as e:
            logger.error(f"Error explaining function: {e}")
            return f"Error generating explanation: {str(e)}"

    async def optimize_code(self, code: str) -> str:
        """Optimiza el código reduciendo complejidad."""
        prompt = OPTIMIZE_PROMPT.format(code=code)

        try:
            return await self._generate(prompt)
        except Exception as e:
            logger.error(f"Error optimizing code: {e}")
            return f"Error generating optimization: {str(e)}"
