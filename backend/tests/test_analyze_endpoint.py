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
