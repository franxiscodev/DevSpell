"""
Templates de prompts para análisis de código con IA.
"""

SUGGESTION_PROMPT = """Eres un experto en análisis de código Python. Analiza este código y proporciona sugerencias de mejora.

CÓDIGO:
{code}

MÉTRICAS:
- Complejidad ciclomática: {complexity}
- Número de funciones: {num_functions}
- Líneas de código: {code_lines}

INSTRUCCIONES:
- Proporciona 2-4 sugerencias concretas y accionables
- Enfócate en: reducir complejidad, mejorar legibilidad, seguir mejores prácticas, optimizar performance
- Responde en ESPAÑOL pero mantén términos técnicos en inglés (ej: "list comprehension", "type hints", "memoization")
- Sé conciso: máximo 2 líneas por sugerencia
- Usa formato numerado simple

EJEMPLO DE FORMATO:
1. Agregar type hints a los parámetros para mejorar la claridad del código
2. Usar memoization con @lru_cache para optimizar la función factorial recursiva
3. Extraer la lógica compleja en funciones separadas para reducir la complejidad

TUS SUGERENCIAS:"""


EXPLAIN_PROMPT = """Explica qué hace esta función Python en términos claros y simples.

NOMBRE DE LA FUNCIÓN: {function_name}

CÓDIGO:
{function_code}

INSTRUCCIONES:
- Responde en ESPAÑOL pero mantén términos técnicos en inglés
- Proporciona una explicación estructurada con:
  1. Propósito: Qué hace la función (1-2 oraciones)
  2. Parámetros: Lista cada parámetro y su propósito
  3. Valor de retorno: Qué devuelve
  4. Notas importantes: Casos especiales, supuestos o comportamiento relevante

Mantén la explicación concisa y enfocada.

TU EXPLICACIÓN:"""


OPTIMIZE_PROMPT = """Optimiza este código Python para reducir complejidad y mejorar el rendimiento manteniendo la funcionalidad.

CÓDIGO ORIGINAL:
{code}

INSTRUCCIONES:
- Responde en ESPAÑOL pero mantén términos técnicos en inglés
- Proporciona:
  1. Versión optimizada del código
  2. Explicación breve (3-4 puntos) de qué se mejoró y por qué

Enfócate en:
- Reducir complejidad ciclomática
- Mejorar eficiencia algorítmica
- Mejor uso de idioms y built-ins de Python
- Nombres de variables más claros

Mantén el código optimizado limpio y bien comentado.

TU OPTIMIZACIÓN:"""
