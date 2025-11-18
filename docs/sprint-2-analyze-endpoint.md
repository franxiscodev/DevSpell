# Sprint 2: Endpoint de Análisis de Código

## Objetivo
Crear endpoint POST /api/v1/analyze que recibe código Python y retorna métricas de calidad

## ¿Qué vamos a construir?

Un sistema que analiza código Python usando AST (Abstract Syntax Tree) y calcula:
- Número de líneas totales
- Número de líneas de código (sin comentarios ni vacías)
- Complejidad ciclomática (McCabe)
- Número de funciones definidas
- Número de clases definidas
- Número de imports
- Lista de funciones con sus líneas

---

## Arquitectura
```
Cliente
  ↓ POST /api/v1/analyze { "code": "..." }
  ↓
FastAPI Router (analyze.py)
  ↓
Analyzer Service (code_analyzer.py)
  ↓ ast.parse()
  ↓
AST Visitor (ast_visitor.py)
  ↓
Métricas calculadas
  ↓
Response JSON
```

---

## ARCHIVO 1: backend/src/models/analyze.py

### ¿Qué es?
Modelos Pydantic que definen:
- Request: lo que el cliente envía
- Response: lo que la API retorna

### Código completo:
```python
"""
Modelos Pydantic para el endpoint de análisis.
"""
from pydantic import BaseModel, Field, field_validator


class FunctionInfo(BaseModel):
    """Información de una función detectada."""
    name: str = Field(..., description="Nombre de la función")
    line_start: int = Field(..., description="Línea donde comienza")
    line_end: int = Field(..., description="Línea donde termina")
    complexity: int = Field(default=1, description="Complejidad ciclomática")


class AnalyzeRequest(BaseModel):
    """Request para analizar código."""
    code: str = Field(..., description="Código Python a analizar", min_length=1)
    
    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        """Valida que el código no esté vacío después de strip."""
        if not v.strip():
            raise ValueError("El código no puede estar vacío")
        return v


class AnalyzeResponse(BaseModel):
    """Response con métricas del código analizado."""
    total_lines: int = Field(..., description="Líneas totales incluyendo vacías")
    code_lines: int = Field(..., description="Líneas de código (sin comentarios ni vacías)")
    complexity: int = Field(..., description="Complejidad ciclomática total")
    num_functions: int = Field(..., description="Número de funciones definidas")
    num_classes: int = Field(..., description="Número de clases definidas")
    num_imports: int = Field(..., description="Número de imports")
    functions: list[FunctionInfo] = Field(default_factory=list, description="Lista de funciones detectadas")
```

### ¿Por qué este código?
- `FunctionInfo`: Estructura para cada función encontrada
- `AnalyzeRequest`: Valida que el código no esté vacío
- `AnalyzeResponse`: Define exactamente qué retorna la API
- `Field(...)`: Documentación automática en Swagger

---

## ARCHIVO 2: backend/src/services/ast_visitor.py

### ¿Qué es?
Visitor que recorre el AST (árbol sintáctico) y calcula complejidad ciclomática

### Código completo:
```python
"""
AST Visitor para calcular complejidad ciclomática.
"""
import ast
from typing import Any


class ComplexityVisitor(ast.NodeVisitor):
    """
    Visitor que calcula complejidad ciclomática de código Python.
    
    La complejidad ciclomática mide el número de caminos independientes
    en el código. Comienza en 1 y se incrementa por:
    - if, elif
    - for, while
    - except
    - and, or (operadores lógicos)
    - list/dict/set comprehensions
    """
    
    def __init__(self) -> None:
        """Inicializa el visitor con complejidad 1."""
        self.complexity = 1
    
    def visit_If(self, node: ast.If) -> Any:
        """Incrementa por cada if/elif."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> Any:
        """Incrementa por cada for."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> Any:
        """Incrementa por cada while."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
        """Incrementa por cada except."""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        """Incrementa por cada operador lógico (and/or)."""
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_comprehension(self, node: ast.comprehension) -> Any:
        """Incrementa por comprehensions."""
        self.complexity += 1
        self.generic_visit(node)


def calculate_complexity(code: str) -> int:
    """
    Calcula la complejidad ciclomática de un código.
    
    Args:
        code: Código Python como string
        
    Returns:
        Complejidad ciclomática (mínimo 1)
        
    Raises:
        SyntaxError: Si el código tiene errores de sintaxis
    """
    try:
        tree = ast.parse(code)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity
    except SyntaxError:
        raise
```

### ¿Por qué este código?
- `ComplexityVisitor`: Hereda de `ast.NodeVisitor` para recorrer el AST
- Cada `visit_*`: Se llama automáticamente cuando encuentra ese tipo de nodo
- `complexity`: Comienza en 1 y aumenta con cada decisión (if, for, etc.)
- McCabe Complexity: Métrica estándar de calidad de código

---

## ARCHIVO 3: backend/src/services/code_analyzer.py

### ¿Qué es?
Servicio principal que analiza el código y extrae todas las métricas

### Código completo:
```python
"""
Servicio de análisis de código Python usando AST.
"""
import ast
from typing import Any

from src.models.analyze import FunctionInfo
from src.services.ast_visitor import calculate_complexity


class CodeAnalysisError(Exception):
    """Error durante el análisis de código."""
    pass


class CodeAnalyzer:
    """Analiza código Python y extrae métricas."""
    
    def __init__(self, code: str) -> None:
        """
        Inicializa el analizador con código.
        
        Args:
            code: Código Python a analizar
        """
        self.code = code
        self.lines = code.splitlines()
    
    def count_total_lines(self) -> int:
        """
        Cuenta líneas totales incluyendo vacías.
        
        Returns:
            Número total de líneas
        """
        return len(self.lines)
    
    def count_code_lines(self) -> int:
        """
        Cuenta líneas de código (excluye vacías y comentarios).
        
        Returns:
            Número de líneas de código
        """
        code_lines = 0
        for line in self.lines:
            stripped = line.strip()
            # Ignorar líneas vacías y comentarios
            if stripped and not stripped.startswith("#"):
                code_lines += 1
        return code_lines
    
    def parse_ast(self) -> ast.Module:
        """
        Parsea el código a AST.
        
        Returns:
            AST del código
            
        Raises:
            CodeAnalysisError: Si hay error de sintaxis
        """
        try:
            return ast.parse(self.code)
        except SyntaxError as e:
            raise CodeAnalysisError(f"Error de sintaxis en línea {e.lineno}: {e.msg}")
    
    def extract_functions(self, tree: ast.Module) -> list[FunctionInfo]:
        """
        Extrae información de todas las funciones.
        
        Args:
            tree: AST del código
            
        Returns:
            Lista de información de funciones
        """
        functions: list[FunctionInfo] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calcular complejidad de la función
                func_code = ast.get_source_segment(self.code, node)
                func_complexity = 1  # Por defecto
                
                if func_code:
                    try:
                        func_complexity = calculate_complexity(func_code)
                    except:
                        pass  # Si falla, dejar en 1
                
                functions.append(FunctionInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    complexity=func_complexity,
                ))
        
        return functions
    
    def count_classes(self, tree: ast.Module) -> int:
        """
        Cuenta el número de clases definidas.
        
        Args:
            tree: AST del código
            
        Returns:
            Número de clases
        """
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    
    def count_imports(self, tree: ast.Module) -> int:
        """
        Cuenta el número de imports (import e import from).
        
        Args:
            tree: AST del código
            
        Returns:
            Número de imports
        """
        imports = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
        return imports
    
    def analyze(self) -> dict[str, Any]:
        """
        Analiza el código y retorna todas las métricas.
        
        Returns:
            Diccionario con métricas del código
            
        Raises:
            CodeAnalysisError: Si hay error al analizar
        """
        # Parsear AST
        tree = self.parse_ast()
        
        # Calcular complejidad total
        try:
            total_complexity = calculate_complexity(self.code)
        except SyntaxError:
            raise CodeAnalysisError("Error al calcular complejidad")
        
        # Extraer métricas
        functions = self.extract_functions(tree)
        
        return {
            "total_lines": self.count_total_lines(),
            "code_lines": self.count_code_lines(),
            "complexity": total_complexity,
            "num_functions": len(functions),
            "num_classes": self.count_classes(tree),
            "num_imports": self.count_imports(tree),
            "functions": functions,
        }


def analyze_code(code: str) -> dict[str, Any]:
    """
    Función helper para analizar código.
    
    Args:
        code: Código Python a analizar
        
    Returns:
        Diccionario con métricas
        
    Raises:
        CodeAnalysisError: Si hay error al analizar
    """
    analyzer = CodeAnalyzer(code)
    return analyzer.analyze()
```

### ¿Por qué este código?
- `CodeAnalyzer`: Clase que encapsula toda la lógica de análisis
- `count_*`: Métodos que calculan cada métrica
- `parse_ast()`: Convierte código a árbol sintáctico
- `analyze()`: Método principal que orquesta todo
- Usa `ast.walk()`: Recorre todos los nodos del árbol
- Manejo de errores específico con `CodeAnalysisError`

---

## ARCHIVO 4: backend/src/api/routes/analyze.py

### ¿Qué es?
Endpoint FastAPI que expone el servicio de análisis

### Código completo:
```python
"""
Endpoint para análisis de código.
"""
from fastapi import APIRouter, HTTPException, status

from src.models.analyze import AnalyzeRequest, AnalyzeResponse
from src.services.code_analyzer import analyze_code, CodeAnalysisError
from src.core.logger import logger


router = APIRouter(tags=["Analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analizar código Python",
    description="""
    Analiza código Python y retorna métricas de calidad.
    
    **Métricas calculadas:**
    - Líneas totales y líneas de código
    - Complejidad ciclomática (McCabe)
    - Número de funciones, clases e imports
    - Detalle de cada función con su complejidad
    
    **Validaciones:**
    - El código no puede estar vacío
    - Debe ser Python sintácticamente válido
    """,
)
async def analyze_python_code(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analiza código Python y retorna métricas.
    
    Args:
        request: Código Python a analizar
        
    Returns:
        Métricas del código
        
    Raises:
        HTTPException 400: Si el código tiene errores de sintaxis
        HTTPException 500: Si hay error interno al analizar
    """
    try:
        logger.info(f"Analizando código de {len(request.code)} caracteres")
        
        # Analizar código
        metrics = analyze_code(request.code)
        
        logger.info(
            f"Análisis completado: {metrics['code_lines']} líneas, "
            f"complejidad {metrics['complexity']}"
        )
        
        return AnalyzeResponse(**metrics)
        
    except CodeAnalysisError as e:
        logger.error(f"Error al analizar código: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error inesperado al analizar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al analizar el código",
        )
```

### ¿Por qué este código?
- `@router.post`: Define el endpoint POST
- `response_model`: FastAPI valida la respuesta automáticamente
- `summary` y `description`: Aparecen en Swagger
- `HTTPException`: Manejo de errores HTTP apropiado
- `logger`: Registra cada análisis para debugging
- Código de estado 400 para errores del cliente, 500 para errores del servidor

---

## ARCHIVO 5: backend/src/main.py (ACTUALIZACIÓN)

### ¿Qué cambia?
Agregar el router de analyze

### Código actualizado (solo la parte que cambia):
```python
# ... (todo el código anterior igual)

from src.api.routes import health, analyze  # <-- AGREGAR analyze


def create_app() -> FastAPI:
    """..."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(analyze.router, prefix="/api/v1")  # <-- AGREGAR ESTA LÍNEA
    
    return app
```

---

## ARCHIVO 6: backend/tests/test_analyzer.py

### ¿Qué es?
Tests completos para el servicio de análisis

### Código completo:
```python
"""
Tests para el servicio de análisis de código.
"""
import pytest

from src.services.code_analyzer import CodeAnalyzer, analyze_code, CodeAnalysisError


def test_count_total_lines():
    """Debe contar líneas totales correctamente."""
    code = """def hello():
    print("hello")
    
# comentario
"""
    analyzer = CodeAnalyzer(code)
    assert analyzer.count_total_lines() == 4


def test_count_code_lines():
    """Debe contar solo líneas de código (sin vacías ni comentarios)."""
    code = """def hello():
    print("hello")
    
# comentario
    return True
"""
    analyzer = CodeAnalyzer(code)
    assert analyzer.count_code_lines() == 3  # def, print, return


def test_parse_valid_code():
    """Debe parsear código válido sin errores."""
    code = "x = 1 + 2"
    analyzer = CodeAnalyzer(code)
    tree = analyzer.parse_ast()
    assert tree is not None


def test_parse_invalid_code():
    """Debe lanzar error con código inválido."""
    code = "def hello("  # Sintaxis inválida
    analyzer = CodeAnalyzer(code)
    
    with pytest.raises(CodeAnalysisError):
        analyzer.parse_ast()


def test_extract_functions():
    """Debe extraer información de funciones."""
    code = """def function1():
    pass

def function2(x, y):
    return x + y
"""
    analyzer = CodeAnalyzer(code)
    tree = analyzer.parse_ast()
    functions = analyzer.extract_functions(tree)
    
    assert len(functions) == 2
    assert functions[0].name == "function1"
    assert functions[1].name == "function2"
    assert functions[0].line_start == 1
    assert functions[1].line_start == 4


def test_count_classes():
    """Debe contar clases correctamente."""
    code = """class MyClass:
    pass

class AnotherClass:
    def method(self):
        pass
"""
    analyzer = CodeAnalyzer(code)
    tree = analyzer.parse_ast()
    assert analyzer.count_classes(tree) == 2


def test_count_imports():
    """Debe contar imports correctamente."""
    code = """import os
import sys
from pathlib import Path
"""
    analyzer = CodeAnalyzer(code)
    tree = analyzer.parse_ast()
    assert analyzer.count_imports(tree) == 3


def test_analyze_simple_code():
    """Debe analizar código simple correctamente."""
    code = """import os

def hello(name):
    if name:
        print(f"Hello {name}")
    return True
"""
    result = analyze_code(code)
    
    assert result["total_lines"] == 6
    assert result["code_lines"] == 5
    assert result["num_functions"] == 1
    assert result["num_imports"] == 1
    assert result["complexity"] >= 2  # if aumenta complejidad


def test_analyze_complex_code():
    """Debe analizar código complejo con múltiples estructuras."""
    code = """import sys
from typing import List

class Calculator:
    def add(self, a, b):
        return a + b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

def process_numbers(numbers: List[int]):
    result = []
    for num in numbers:
        if num > 0:
            result.append(num * 2)
        elif num < 0:
            result.append(abs(num))
    return result
"""
    result = analyze_code(code)
    
    assert result["num_classes"] == 1
    assert result["num_functions"] == 3  # add, divide, process_numbers
    assert result["num_imports"] == 2
    assert result["complexity"] > 1  # Múltiples if/for
    assert len(result["functions"]) == 3


def test_analyze_empty_code_raises_error():
    """Debe fallar con código vacío."""
    with pytest.raises(CodeAnalysisError):
        analyze_code("")
```

---

## ARCHIVO 7: backend/tests/test_analyze_endpoint.py

### ¿Qué es?
Tests de integración para el endpoint

### Código completo:
```python
"""
Tests para el endpoint de análisis.
"""
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_analyze_endpoint_exists():
    """El endpoint debe existir y aceptar POST."""
    response = client.post("/api/v1/analyze", json={"code": "x = 1"})
    assert response.status_code == 200


def test_analyze_simple_code():
    """Debe analizar código simple correctamente."""
    code = """def hello():
    print("Hello")
    return True
"""
    response = client.post("/api/v1/analyze", json={"code": code})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_lines" in data
    assert "code_lines" in data
    assert "complexity" in data
    assert "num_functions" in data
    assert data["num_functions"] == 1


def test_analyze_invalid_syntax():
    """Debe retornar error 400 con sintaxis inválida."""
    code = "def hello("
    response = client.post("/api/v1/analyze", json={"code": code})
    
    assert response.status_code == 400
    assert "detail" in response.json()


def test_analyze_empty_code():
    """Debe retornar error con código vacío."""
    response = client.post("/api/v1/analyze", json={"code": ""})
    assert response.status_code == 422  # Validation error


def test_analyze_response_structure():
    """La respuesta debe tener la estructura correcta."""
    code = "x = 1"
    response = client.post("/api/v1/analyze", json={"code": code})
    
    data = response.json()
    
    # Verificar campos requeridos
    assert "total_lines" in data
    assert "code_lines" in data
    assert "complexity" in data
    assert "num_functions" in data
    assert "num_classes" in data
    assert "num_imports" in data
    assert "functions" in data
    
    # Verificar tipos
    assert isinstance(data["total_lines"], int)
    assert isinstance(data["code_lines"], int)
    assert isinstance(data["complexity"], int)
    assert isinstance(data["functions"], list)


def test_analyze_with_functions():
    """Debe detectar funciones y su información."""
    code = """def function1():
    pass

def function2():
    if True:
        pass
"""
    response = client.post("/api/v1/analyze", json={"code": code})
    data = response.json()
    
    assert data["num_functions"] == 2
    assert len(data["functions"]) == 2
    assert data["functions"][0]["name"] == "function1"
    assert data["functions"][1]["name"] == "function2"
```

---

## Orden de Creación

1. ✅ models/analyze.py (modelos de datos)
2. ✅ services/ast_visitor.py (cálculo de complejidad)
3. ✅ services/code_analyzer.py (servicio principal)
4. ✅ api/routes/analyze.py (endpoint)
5. ✅ main.py (agregar router)
6. ✅ tests/test_analyzer.py (tests del servicio)
7. ✅ tests/test_analyze_endpoint.py (tests del endpoint)

## Validación Final

- ✅ Tests pasan: `uv run pytest tests/ -v`
- ✅ Servidor arranca sin errores
- ✅ http://localhost:8000/docs muestra el nuevo endpoint
- ✅ POST /api/v1/analyze funciona correctamente
- ✅ Manejo de errores apropiado

## Ejemplo de Uso
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello():\n    print(\"hello\")\n    return True"}'
```

Response:
```json
{
  "total_lines": 3,
  "code_lines": 3,
  "complexity": 1,
  "num_functions": 1,
  "num_classes": 0,
  "num_imports": 0,
  "functions": [
    {
      "name": "hello",
      "line_start": 1,
      "line_end": 3,
      "complexity": 1
    }
  ]
}
```