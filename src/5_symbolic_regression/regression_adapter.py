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
    La lógica de múltiples intentos está dentro de iterative_symbolic_regression.
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
    """
    all_results = []

    for i, branch in enumerate(branches):
        results = run_symbolic_regression_for_branch(
            branch, param_names, i,
            epsilon, k, niterations, min_points
        )
        all_results.append(results)

    return all_results
