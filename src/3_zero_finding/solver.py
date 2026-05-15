"""
Resolución de sistemas de ecuaciones no lineales paramétricas.

Usa scipy.optimize.root con múltiples puntos iniciales para encontrar
todas las soluciones de un sistema F(x; θ) = 0.

Métodos:
  - 'scipy': scipy.optimize.root con método híbrido (Broyden + line search)
"""
import numpy as np
import sympy as sp
import warnings
from typing import List, Dict, Any, Tuple
from scipy.optimize import root
from tqdm import tqdm


def solve_system_scipy(equations: List[sp.Expr],
                       variables: List[sp.Symbol],
                       param_values: Dict[sp.Symbol, float],
                       guess_ranges: Dict[str, Tuple[float, float]],
                       num_guesses: int = 20,
                       dist_tol: float = 1e-3,
                       residue_tol: float = 1e-6) -> List[np.ndarray]:
    """
    Resuelve un sistema de ecuaciones F(x; θ) = 0 para una tupla de parámetros fija.
    
    Usa scipy.optimize.root con múltiples puntos iniciales aleatorios y filtra
    soluciones duplicadas usando distancia euclidiana.
    
    Args:
        equations: Lista de expresiones SymPy (el sistema)
        variables: Lista de símbolos SymPy (las incógnitas x1, x2, ...)
        param_values: Dict {símbolo: valor numérico} con los parámetros fijos
        guess_ranges: Dict {nombre_variable: (min, max)} para generar puntos iniciales
        num_guesses: Número de puntos iniciales aleatorios a probar
        dist_tol: Tolerancia euclidiana para considerar dos soluciones como iguales
        residue_tol: Tolerancia del residuo ||F(x; θ)|| < tol para aceptar
    
    Returns:
        unique_solutions: Lista de arrays numpy (vectores solución únicos)
    """
    # Sustituir parámetros en las ecuaciones
    eqs_sub = [eq.subs(param_values) for eq in equations]
    
    # Crear función evaluable usando lambdify
    # lambdify devuelve una función que toma los valores de las variables en orden
    eval_func = sp.lambdify(variables, eqs_sub, modules='numpy')
    
    def system_func(vec):
        """Wrapper que evalúa el sistema en el punto vec."""
        try:
            result = eval_func(*vec)
            # Si hay una sola ecuación, lambdify devuelve un escalar; convertir a array
            if np.isscalar(result):
                return np.array([result])
            return np.asarray(result).flatten()
        except Exception:
            # Si hay error de evaluación, retornar residuo grande
            return np.full(len(equations), 1e10)
    
    found_solutions = []
    
    # Probar múltiples puntos iniciales
    for _ in range(num_guesses):
        # Generar punto inicial aleatorio
        guess = []
        for var in variables:
            var_name = str(var)
            if var_name in guess_ranges:
                min_val, max_val = guess_ranges[var_name]
            else:
                # Si no está en guess_ranges, usar rango por defecto
                min_val, max_val = -10.0, 10.0
            
            guess.append(np.random.uniform(min_val, max_val))
        
        guess = np.array(guess)
        
        try:
            # Suprimir warnings de scipy
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Resolver con scipy.optimize.root (método híbrido por defecto)
                sol = root(system_func, guess, method='hybr', tol=1e-8)
            
            # Verificar si convergió y el residuo es aceptable
            if sol.success and np.linalg.norm(sol.fun) < residue_tol:
                found_solutions.append(sol.x.real)
        
        except Exception:
            # Ignorar excepciones en esta iteración
            continue
    
    # Filtrar soluciones duplicadas por distancia euclidiana
    unique_solutions = []
    for sol in found_solutions:
        is_duplicate = False
        for unique_sol in unique_solutions:
            if np.linalg.norm(np.array(sol) - np.array(unique_sol)) < dist_tol:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_solutions.append(sol)
    
    return unique_solutions


def solve_for_all_parameter_tuples(equations: List[sp.Expr],
                                   variables: List[sp.Symbol],
                                   param_names: List[str],
                                   param_symbols: Dict[str, sp.Symbol],
                                   parameter_grid: np.ndarray,
                                   method: str = 'scipy',
                                   **scipy_kwargs) -> List[Dict[str, Any]]:
    """
    Resuelve el sistema para todas las tuplas de parámetros en el grid.
    
    Args:
        equations: Lista de expresiones SymPy del sistema
        variables: Lista de símbolos SymPy (las incógnitas)
        param_names: Nombres de los parámetros (para mapping en results)
        param_symbols: Dict {nombre: símbolo} de los parámetros
        parameter_grid: Array (N, num_params) con tuplas de parámetros
        method: Método de resolución (solo 'scipy' por ahora)
        **scipy_kwargs: Argumentos adicionales para solve_system_scipy
                       (num_guesses, dist_tol, residue_tol, guess_ranges)
    
    Returns:
        results: Lista de dicts con estructura:
                 {
                   'parameters': {param_name: value, ...},
                   'roots': [array1, array2, ...],
                   'num_roots': int
                 }
    """
    if method != 'scipy':
        raise ValueError(f"Método desconocido: {method}")
    
    results = []
    
    print(f"\nResolviendo sistema para {len(parameter_grid)} tuplas de parámetros...")
    
    for param_tuple in tqdm(parameter_grid):
        # Crear diccionario de valores de parámetros
        param_values = {}
        for name, val in zip(param_names, param_tuple):
            if name in param_symbols:
                param_values[param_symbols[name]] = val
        
        # Resolver sistema
        roots = solve_system_scipy(equations, variables, param_values, **scipy_kwargs)
        
        # Guardar resultados solo si hay soluciones
        if len(roots) > 0:
            results.append({
                'parameters': dict(zip(param_names, param_tuple)),
                'roots': roots,
                'num_roots': len(roots)
            })
    
    print(f"Completado. {len(results)}/{len(parameter_grid)} tuplas con soluciones válidas.\n")
    return results


if __name__ == "__main__":
    import os, sys
    _parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, _parent)
    from config import (
        EQUATIONS, VARIABLES, PARAMETERS, PARAMETER_RANGES,
        SYSTEM_SOLVER_METHOD, NUM_INITIAL_GUESSES, GUESS_RANGES,
        DISTANCE_TOLERANCE, SOLVER_RESIDUE_TOL
    )

    # Añadir carpetas hermanas al path
    sys.path.insert(0, os.path.join(_parent, '1_equation_definition'))
    sys.path.insert(0, os.path.join(_parent, '2_parameter_grid'))

    from equation_parser import parse_system
    from grid_generator import generate_grid
    
    # Parsear sistema de ecuaciones
    equations_sympy, symbols_dict = parse_system(EQUATIONS, VARIABLES, PARAMETERS)
    var_symbols = [symbols_dict[v] for v in VARIABLES]
    param_symbols = {p: symbols_dict[p] for p in PARAMETERS}
    
    # Generar grid de parámetros
    grid, _ = generate_grid(PARAMETER_RANGES)
    
    # Resolver sistema
    results = solve_for_all_parameter_tuples(
        equations_sympy, var_symbols, PARAMETERS, param_symbols, grid,
        method=SYSTEM_SOLVER_METHOD,
        num_guesses=NUM_INITIAL_GUESSES,
        guess_ranges=GUESS_RANGES,
        dist_tol=DISTANCE_TOLERANCE,
        residue_tol=SOLVER_RESIDUE_TOL
    )
    
    # Mostrar resultados
    print(f"\nTotal de tuplas con soluciones: {len(results)}")
    if len(results) > 0:
        print(f"Primera tupla: {results[0]['parameters']}")
        print(f"  Soluciones encontradas: {results[0]['num_roots']}")
        for i, root_vec in enumerate(results[0]['roots']):
            print(f"    Raíz {i+1}: {root_vec}")
