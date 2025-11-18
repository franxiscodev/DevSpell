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
    # Validar que el código no esté vacío
    if not code.strip():
        raise CodeAnalysisError("El código no puede estar vacío")

    analyzer = CodeAnalyzer(code)
    return analyzer.analyze()
