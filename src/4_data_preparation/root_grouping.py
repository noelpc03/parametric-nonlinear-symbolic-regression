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
    import sys
    sys.path.append('..')
    
    from equation_definition.equation_parser import parse_equation
    from equation_definition.config import EQUATION_STRING, VARIABLES, PARAMETERS
    from parameter_grid.grid_generator import generate_grid
    from parameter_grid.config import PARAMETER_RANGES, SAMPLING_METHOD, NUM_SAMPLES, RANDOM_SEED
    from zero_finding.solver import solve_for_all_parameter_tuples
    from zero_finding.config import SOLVER_METHOD, FILTER_COMPLEX, COMPLEX_TOLERANCE, SORT_ROOTS
    
    # Pipeline completo hasta este punto
    equation, symbols = parse_equation(EQUATION_STRING, VARIABLES, PARAMETERS)
    grid, param_names = generate_grid(PARAMETER_RANGES, SAMPLING_METHOD, NUM_SAMPLES, RANDOM_SEED)
    
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
