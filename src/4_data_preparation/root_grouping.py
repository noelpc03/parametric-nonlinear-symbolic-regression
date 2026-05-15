"""
Agrupación de raíces por rama para regresión simbólica
"""
import numpy as np
from typing import List, Dict, Any


def expand_tuples(results: List[Dict[str, Any]],
                  param_names: List[str]) -> np.ndarray:
    """
    Expande los resultados de resolución en tuplas (params, root).

    Args:
        results: Lista de diccionarios con 'parameters' y 'roots'
        param_names: Lista de nombres de parámetros

    Returns:
        expanded: Array (M, num_params + 1) donde cada fila es (a1, a2, ..., x_i)
    """
    expanded_tuples = []

    for result in results:
        params = [result['parameters'][p] for p in param_names]
        roots = result['roots']

        # Crear una fila por cada raíz
        for root in roots:
            row = params + [root]
            expanded_tuples.append(row)

    return np.array(expanded_tuples)


def combine_all_roots(results: List[Dict[str, Any]],
                      param_names: List[str]) -> Dict[str, np.ndarray]:
    """
    Combina TODAS las raíces en un único dataset sin separar por ramas.

    Para cada tupla de parámetros con múltiples raíces, crea múltiples filas
    (una por cada raíz). El algoritmo de regresión simbólica iterativo será
    el encargado de descubrir las diferentes ecuaciones (ramas) a partir
    de este conjunto combinado.

    Args:
        results: Lista de diccionarios con 'parameters' y 'roots'
        param_names: Lista de nombres de parámetros

    Returns:
        Dict con:
            'X': Array (M, num_params) con los parámetros
            'y': Array (M,) con las raíces correspondientes
    """
    all_params = []
    all_roots = []

    for result in results:
        params = [result['parameters'][p] for p in param_names]
        roots = result['roots']

        # Crear una entrada por cada raíz (sin agrupar por índice de rama)
        for root in roots:
            all_params.append(params)
            all_roots.append(root)

    X = np.array(all_params)
    y = np.array(all_roots)

    # Conteo de información
    num_roots_dist = {}
    for result in results:
        n = result['num_roots']
        num_roots_dist[n] = num_roots_dist.get(n, 0) + 1

    print(f"Datos combinados: {len(y)} tuplas (params → root)")
    print(f"  Tuplas de parámetros originales: {len(results)}")
    print(f"  Distribución de raíces por tupla: {num_roots_dist}")

    return {'X': X, 'y': y}


def combine_all_solutions(results: List[Dict[str, Any]],
                          param_names: List[str]) -> Dict[str, Any]:
    """
    Combina TODAS las soluciones (vectores multidimensionales) en un dataset unificado.
    
    Para sistemas de ecuaciones, cada "solución" es un vector (x1, x2, ..., xn).
    Esta función prepara los datos para la regresión simbólica con anclaje.
    
    Args:
        results: Lista de diccionarios con:
                 - 'parameters': dict con valores de parámetros
                 - 'roots': lista de arrays numpy (vectores solución)
                 - 'num_roots': cantidad de soluciones para esta tupla
        param_names: Lista de nombres de parámetros
    
    Returns:
        Dict con:
            'X': Array (M, num_params) con valores de parámetros
            'Y': Array (M, num_variables) con soluciones vectoriales
            'tuple_id': Array (M,) índice de tupla origen de cada solución
            'solution_id': Array (M,) índice de solución dentro de su tupla
            'num_variables': int, cantidad de variables en cada solución
    """
    all_params = []
    all_solutions = []
    tuple_ids = []
    solution_ids = []
    
    for t_idx, result in enumerate(results):
        params = [result['parameters'][p] for p in param_names]
        roots = result['roots']  # Lista de arrays (cada uno es una solución)
        
        # Crear una fila por cada solución
        for s_idx, sol_vec in enumerate(roots):
            all_params.append(params)
            all_solutions.append(sol_vec)
            tuple_ids.append(t_idx)
            solution_ids.append(s_idx)
    
    X = np.array(all_params)  # Shape: (M, num_params)
    Y = np.array(all_solutions)  # Shape: (M, num_variables)
    
    # Conteo de información
    num_roots_dist = {}
    for result in results:
        n = result['num_roots']
        num_roots_dist[n] = num_roots_dist.get(n, 0) + 1
    
    print(f"\n📊 Datos combinados (sistema de ecuaciones):")
    print(f"  Puntos totales: {len(Y)}")
    print(f"  Tuplas de parámetros: {len(results)}")
    print(f"  Variables por solución: {Y.shape[1]}")
    print(f"  Dimensión X: {X.shape}")
    print(f"  Dimensión Y: {Y.shape}")
    print(f"  Distribución de soluciones por tupla: {num_roots_dist}\n")
    
    return {
        'X': X,
        'Y': Y,
        'tuple_id': np.array(tuple_ids),
        'solution_id': np.array(solution_ids),
        'num_variables': Y.shape[1] if len(Y) > 0 else 0
    }


def group_by_root_branch(results: List[Dict[str, Any]], 
                        param_names: List[str]) -> List[Dict[str, np.ndarray]]:
    """
    Agrupa raíces por "rama" (primera raíz, segunda raíz, etc.).
    
    Args:
        results: Lista de diccionarios con 'parameters' y 'roots'
        param_names: Lista de nombres de parámetros
    
    Returns:
        branches: Lista de diccionarios {'X': params, 'y': roots} por rama
    """
    # Determinar número máximo de raíces
    max_roots = max(result['num_roots'] for result in results)
    
    # Crear un grupo por cada rama
    branches = [{'params': [], 'roots': []} for _ in range(max_roots)]
    
    for result in results:
        params = [result['parameters'][p] for p in param_names]
        roots = result['roots']
        
        # Asignar cada raíz a su rama correspondiente
        for i, root in enumerate(roots):
            branches[i]['params'].append(params)
            branches[i]['roots'].append(root)
    
    # Convertir a numpy arrays
    for i, branch in enumerate(branches):
        branch['X'] = np.array(branch['params'])
        branch['y'] = np.array(branch['roots'])
        del branch['params']
        del branch['roots']
    
    # Filtrar ramas vacías
    branches = [b for b in branches if len(b['y']) > 0]
    
    print(f"Raíces agrupadas en {len(branches)} ramas:")
    for i, branch in enumerate(branches):
        print(f"  Rama {i+1}: {len(branch['y'])} puntos")
    
    return branches


if __name__ == "__main__":
    import os, sys
    _src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, _src)
    sys.path.insert(0, os.path.join(_src, '1_equation_definition'))
    sys.path.insert(0, os.path.join(_src, '2_parameter_grid'))
    sys.path.insert(0, os.path.join(_src, '3_zero_finding'))

    from config import (EQUATION_STRING, VARIABLES, PARAMETERS, PARAMETER_RANGES,
                        SOLVER_METHOD, FILTER_COMPLEX, COMPLEX_TOLERANCE, SORT_ROOTS)
    from equation_parser import parse_equation
    from grid_generator import generate_grid
    from solver import solve_for_all_parameter_tuples

    # Pipeline completo hasta este punto
    equation, symbols = parse_equation(EQUATION_STRING, VARIABLES, PARAMETERS)
    grid, param_names = generate_grid(PARAMETER_RANGES)

    # Usar subset para prueba
    grid_test = grid[:100]

    var_symbols = [symbols[v] for v in VARIABLES]
    param_symbols = {p: symbols[p] for p in PARAMETERS}

    results = solve_for_all_parameter_tuples(
        equation, var_symbols, param_names, param_symbols, grid_test,
        SOLVER_METHOD, FILTER_COMPLEX, COMPLEX_TOLERANCE, SORT_ROOTS
    )
    
    # Expandir y agrupar
    print("\n" + "=" * 60)
    print("EXPANSIÓN DE TUPLAS")
    print("=" * 60)
    expanded = expand_tuples(results, param_names)
    print(f"Tuplas expandidas: {expanded.shape}")
    print("Primeras 5 tuplas:")
    print(expanded[:5])
    
    print("\n" + "=" * 60)
    print("AGRUPACIÓN POR RAMA")
    print("=" * 60)
    branches = group_by_root_branch(results, param_names)
    
    for i, branch in enumerate(branches):
        print(f"\nRama {i+1}:")
        print(f"  X (params): {branch['X'].shape}")
        print(f"  y (roots): {branch['y'].shape}")
        print(f"  Primeros 3 puntos:")
        for j in range(min(3, len(branch['y']))):
            print(f"    Params: {branch['X'][j]} → Root: {branch['y'][j]:.4f}")
