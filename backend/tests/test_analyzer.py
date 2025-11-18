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
