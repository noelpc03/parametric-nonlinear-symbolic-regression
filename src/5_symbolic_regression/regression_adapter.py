"""
Adaptador para usar el sistema de regresión simbólica adaptado
con datos multidimensionales (múltiples parámetros)
"""
import os
import importlib.util
import numpy as np
from typing import List, Dict, Any

# Importar del sistema adaptado en esta misma carpeta
from symbolic_regression import iterative_symbolic_regression

# Cargar config.py de esta misma carpeta explícitamente
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
_spec = importlib.util.spec_from_file_location('sr_config', _cfg_path)
_sr_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sr_config)
EPSILON = _sr_config.EPSILON
K = _sr_config.K
NITERATIONS = _sr_config.NITERATIONS
MIN_POINTS = _sr_config.MIN_POINTS


def run_symbolic_regression_for_branch(branch_data: Dict[str, np.ndarray],
                                       param_names: List[str],
                                       branch_index: int,
                                       epsilon: float = EPSILON,
                                       k: float = K,
                                       niterations: int = NITERATIONS,
                                       min_points: int = MIN_POINTS) -> List[Dict[str, Any]]:
    """
    Ejecuta regresión simbólica para una rama de raíces.
    
    Args:
        branch_data: Diccionario con 'X' (params) y 'y' (roots)
        param_names: Lista de nombres de parámetros
        branch_index: Índice de la rama (para logging)
        epsilon, k, niterations, min_points: Parámetros de regresión
    
    Returns:
        results: Lista de resultados del algoritmo iterativo
    """
    X = branch_data['X']
    y = branch_data['y']
    
    print(f"\n{'='*60}")
    print(f"REGRESIÓN SIMBÓLICA - RAMA {branch_index + 1}")
    print(f"{'='*60}")
    print(f"Datos: {len(y)} puntos, {X.shape[1]} parámetros")
    print(f"Parámetros: {param_names}")
    
    # Ejecutar regresión simbólica iterativa con nombres de parámetros
    results = iterative_symbolic_regression(
        X, y,
        param_names=param_names,  # IMPORTANTE: pasar nombres de parámetros
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
    
    Returns:
        all_results: Lista de resultados por rama
    """
    all_results = []
    
    for i, branch in enumerate(branches):
        results = run_symbolic_regression_for_branch(
            branch, param_names, i,
            epsilon, k, niterations, min_points
        )
        all_results.append(results)
    
    return all_results
