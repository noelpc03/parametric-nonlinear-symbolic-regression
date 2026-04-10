"""
Utilidades de salida para funciones descubiertas por regresión simbólica.

Este módulo solo devuelve y resume las funciones encontradas por el
algoritmo iterativo.
"""
from typing import List, Dict, Any


def return_discovered_functions(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Devuelve sin postproceso las funciones encontradas por SR.

    Args:
        functions: Lista de funciones retornadas por iterative_symbolic_regression

    Returns:
        discovered_functions: Copia de la lista de funciones encontradas
    """
    return list(functions)


def summarize_discovered_functions(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Genera un resumen liviano de las funciones encontradas.

    Args:
        functions: Lista de funciones retornadas por iterative_symbolic_regression

    Returns:
        summary: Lista de diccionarios con indice, ecuación y puntos matcheados
    """
    summary = []
    for idx, func in enumerate(functions, start=1):
        summary.append({
            "function_index": idx,
            "equation": str(func.get("equation", "")),
            "num_matched": int(func.get("num_matched", 0)),
        })
    return summary


if __name__ == "__main__":
    example_functions = [
        {"equation": "a + b", "num_matched": 50},
        {"equation": "a - b", "num_matched": 45},
    ]

    print("Funciones encontradas (sin postproceso):")
    for item in summarize_discovered_functions(example_functions):
        print(f"  {item['function_index']}. {item['equation']} ({item['num_matched']} puntos)")
