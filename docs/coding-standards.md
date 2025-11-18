# Coding Standards - DevSpell

## Python
- ✅ Type hints obligatorios
- ✅ Docstrings en funciones públicas
- ✅ f-strings para formateo
- ✅ Usar pathlib en vez de os.path
- ✅ Manejo explícito de errores

## Estructura
```python
def function_name(param: str) -> dict:
    """Brief description.
    
    Args:
        param: Description
        
    Returns:
        Description
    """
    pass
```

## Tests
- Pytest para unit tests
- Coverage mínimo: 80%
- Tests antes de commit

## Git
- Commits en español
- Formato: `feat: descripción` o `fix: descripción`
- Branch: feature/nombre-feature

## Naming
- Variables/funciones: snake_case
- Clases: PascalCase
- Constantes: UPPER_SNAKE_CASE