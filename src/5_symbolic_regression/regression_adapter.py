"""
Adaptador para usar el sistema de regresión simbólica adaptado
con datos multidimensionales (múltiples parámetros)
"""
import os
import sys
import numpy as np
from typing import List, Dict, Any

# Importar del sistema adaptado en esta misma carpeta
from symbolic_regression import iterative_symbolic_regression

# Asegurar que src/ esté en el path para importar el config unificado
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from config import EPSILON, K, NITERATIONS, MIN_POINTS


def run_symbolic_regression_for_branch(branch_data: Dict[str, np.ndarray],
                                       param_names: List[str],
                                       branch_index: int,
                                       epsilon: float = EPSILON,
                                       k: float = K,
                                       niterations: int = NITERATIONS,
                                       min_points: int = MIN_POINTS) -> List[Dict[str, Any]]:
    """
    Ejecuta regresión simbólica para una rama de raíces.
    La lógica iterativa y criterios de parada están dentro de iterative_symbolic_regression.

    Args:
        branch_data: Diccionario con 'X' (parámetros) e 'y' (raíces) de una rama
        param_names: Lista de nombres de parámetros
        branch_index: Índice de la rama para trazabilidad en logs
        epsilon: Tolerancia de matcheo
        k: Pendiente para la loss sigmoidal (si está activa)
        niterations: Iteraciones internas de PySR por corrida
        min_points: Mínimo de puntos para continuar la búsqueda iterativa

    Returns:
        results: Lista de ecuaciones/iteraciones aceptadas para esa rama
    """
    X = branch_data['X']
    y = branch_data['y']

    print(f"\n{'='*60}")
    print(f"REGRESIÓN SIMBÓLICA - RAMA {branch_index + 1}")
    print(f"{'='*60}")
    print(f"Datos: {len(y)} puntos, {X.shape[1]} parámetros")
    print(f"Parámetros: {param_names}")

    results = iterative_symbolic_regression(
        X, y,
        param_names=param_names,
        epsilon=epsilon,
        k=k,
        niterations=niterations,
        min_points=min_points
    )

    return results


def run_for_all_branches(branches: List[Dict[str, np.ndarray]],
                        param_names: List[str],
                        epsilon: float = EPSILON,
                        k: float = K,
                        niterations: int = NITERATIONS,
                        min_points: int = MIN_POINTS) -> List[List[Dict[str, Any]]]:
    """
    Ejecuta regresión simbólica para todas las ramas.

    Args:
        branches: Lista de datasets por rama, cada uno con 'X' e 'y'
        param_names: Lista de nombres de parámetros
        epsilon: Tolerancia de matcheo
        k: Pendiente para la loss sigmoidal (si está activa)
        niterations: Iteraciones internas de PySR por corrida
        min_points: Mínimo de puntos para continuar la búsqueda iterativa

    Returns:
        all_results: Lista con resultados por rama
    """
    all_results = []

    for i, branch in enumerate(branches):
        results = run_symbolic_regression_for_branch(
            branch, param_names, i,
            epsilon, k, niterations, min_points
        )
        all_results.append(results)

    return all_results


def run_combined_symbolic_regression(combined_data: Dict[str, np.ndarray],
                                      param_names: List[str],
                                      epsilon: float = EPSILON,
                                      k: float = K,
                                      niterations: int = NITERATIONS,
                                      min_points: int = MIN_POINTS,
                                      max_iterations: int = None) -> List[Dict[str, Any]]:
    """
    Ejecuta regresión simbólica sobre TODAS las raíces combinadas.

    En lugar de separar por ramas primero, el algoritmo iterativo
    descubre las ecuaciones una por una a partir del conjunto completo.
    Cada ecuación encontrada debería corresponder a una rama.

    Args:
        combined_data: Dict con 'X' (parámetros) e 'y' (raíces combinadas)
        param_names: Lista de nombres de parámetros
        epsilon: Tolerancia para matcheo
        k: Parámetro de suavidad para loss sigmoidal
        niterations: Iteraciones de PySR por intento
        min_points: Mínimo de puntos para continuar
        max_iterations: Máximo de iteraciones (None = usar default de config)

    Returns:
        Lista de ecuaciones encontradas (cada una representa una "rama" descubierta)
    """
    X = combined_data['X']
    y = combined_data['y']

    print(f"\n{'='*60}")
    print(f"REGRESIÓN SIMBÓLICA - MODO COMBINADO")
    print(f"{'='*60}")
    print(f"Datos: {len(y)} tuplas (params → root)")
    print(f"Dimensiones: {X.shape[1]} parámetros")
    print(f"Parámetros: {param_names}")
    print(f"\nEl algoritmo iterativo descubrirá las ecuaciones (ramas)")
    print(f"una por una, quitando puntos matcheados en cada paso.")

    kwargs = dict(
        param_names=param_names,
        epsilon=epsilon,
        k=k,
        niterations=niterations,
        min_points=min_points
    )
    if max_iterations is not None:
        kwargs['max_iterations'] = max_iterations

    results = iterative_symbolic_regression(X, y, **kwargs)

    # Resumen de ecuaciones encontradas
    print(f"\n{'='*60}")
    print(f"RESUMEN: {len(results)} ECUACIONES DESCUBIERTAS")
    print(f"{'='*60}")
    for i, res in enumerate(results):
        print(f"  {i+1}. {res['equation']} ({res['num_matched']} puntos)")

    return results
