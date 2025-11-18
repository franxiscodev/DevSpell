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
