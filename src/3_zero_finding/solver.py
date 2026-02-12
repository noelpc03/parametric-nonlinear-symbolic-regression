"""
Resolución de ecuaciones para encontrar ceros
"""
import numpy as np
import sympy as sp
from typing import List, Dict, Any
from tqdm import tqdm


def solve_equation_for_parameters(equation: sp.Expr, 
                                  variable: sp.Symbol,
                                  param_symbols: Dict[str, sp.Symbol],
                                  param_values: Dict[str, float],
                                  method: str = 'solve',
                                  filter_complex: bool = True,
                                  complex_tol: float = 1e-10,
                                  sort_roots: bool = True) -> List[float]:
    """
    Resuelve f(x; params) = 0 para una tupla específica de parámetros.
    
    Args:
        equation: Expresión SymPy de la ecuación
        variable: Variable a resolver
        param_symbols: Diccionario {nombre: símbolo} de parámetros
        param_values: Diccionario {nombre: valor} con valores numéricos
        method: 'solve' o 'nsolve'
        filter_complex: Si True, filtra raíces complejas
        complex_tol: Tolerancia para considerar una raíz como real
        sort_roots: Si True, ordena las raíces numéricamente
    
    Returns:
        roots: Lista de raíces reales
    """
    # Sustituir parámetros en la ecuación
    eq_substituted = equation.subs(param_values)
    
    try:
        if method == 'solve':
            # Resolver simbólicamente
            solutions = sp.solve(eq_substituted, variable)
        elif method == 'nsolve':
            # Resolver numéricamente (requiere implementación más sofisticada)
            solutions = sp.solve(eq_substituted, variable)
        else:
            raise ValueError(f"Método desconocido: {method}")
        
        # Convertir a valores numéricos
        roots = []
        for sol in solutions:
            try:
                # Evaluar la solución
                val = complex(sol.evalf())
                
                # Filtrar complejas si se requiere
                if filter_complex:
                    if abs(val.imag) < complex_tol:
                        roots.append(val.real)
                else:
                    roots.append(val)
            except:
                # Si no se puede evaluar, ignorar
                continue
        
        # Ordenar raíces
        if sort_roots and len(roots) > 0:
            roots = sorted(roots)
        
        return roots
    
    except Exception as e:
        # Si falla la resolución, devolver lista vacía
        return []


def solve_for_all_parameter_tuples(equation: sp.Expr,
                                   variables: List[sp.Symbol],
                                   param_names: List[str],
                                   param_symbols: Dict[str, sp.Symbol],
                                   parameter_grid: np.ndarray,
                                   method: str = 'solve',
                                   filter_complex: bool = True,
                                   complex_tol: float = 1e-10,
                                   sort_roots: bool = True) -> List[Dict[str, Any]]:
    """
    Resuelve la ecuación para todas las tuplas de parámetros.
    
    Args:
        equation: Ecuación a resolver
        variables: Lista de variables a resolver
        param_names: Lista de nombres de parámetros
        param_symbols: Diccionario de símbolos de parámetros
        parameter_grid: Array (N, num_params) con tuplas de parámetros
        ... (otros parámetros igual que solve_equation_for_parameters)
    
    Returns:
        results: Lista de diccionarios con resultados por tupla
    """
    results = []
    
    # Solo soportamos una variable por ahora
    if len(variables) > 1:
        raise NotImplementedError("Por ahora solo se soporta una variable")
    
    variable = variables[0]
    
    print(f"Resolviendo ecuación para {len(parameter_grid)} tuplas de parámetros...")
    
    for param_tuple in tqdm(parameter_grid):
        # Crear diccionario de valores de parámetros
        param_values = {param_symbols[name]: val 
                       for name, val in zip(param_names, param_tuple)}
        
        # Resolver ecuación
        roots = solve_equation_for_parameters(
            equation, variable, param_symbols, param_values,
            method=method, filter_complex=filter_complex,
            complex_tol=complex_tol, sort_roots=sort_roots
        )
        
        # Guardar resultados
        if len(roots) > 0:
            results.append({
                'parameters': dict(zip(param_names, param_tuple)),
                'roots': roots,
                'num_roots': len(roots)
            })
    
    print(f"Completado. {len(results)} tuplas con raíces válidas.")
    return results


if __name__ == "__main__":
    from config import SOLVER_METHOD, FILTER_COMPLEX, COMPLEX_TOLERANCE, SORT_ROOTS
    import sys
    sys.path.append('..')
    
    from equation_definition.equation_parser import parse_equation
    from equation_definition.config import EQUATION_STRING, VARIABLES, PARAMETERS
    from parameter_grid.grid_generator import generate_grid
    from parameter_grid.config import PARAMETER_RANGES, SAMPLING_METHOD, NUM_SAMPLES, RANDOM_SEED
    
    # Parsear ecuación
    equation, symbols = parse_equation(EQUATION_STRING, VARIABLES, PARAMETERS)
    
    # Generar grid
    grid, param_names = generate_grid(
        PARAMETER_RANGES, SAMPLING_METHOD, NUM_SAMPLES, RANDOM_SEED
    )
    
    # Usar solo primeras 10 tuplas para prueba
    grid_test = grid[:10]
    
    # Resolver
    var_symbols = [symbols[v] for v in VARIABLES]
    param_symbols = {p: symbols[p] for p in PARAMETERS}
    
    results = solve_for_all_parameter_tuples(
        equation, var_symbols, param_names, param_symbols, grid_test,
        method=SOLVER_METHOD, filter_complex=FILTER_COMPLEX,
        complex_tol=COMPLEX_TOLERANCE, sort_roots=SORT_ROOTS
    )
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("RESULTADOS DE RESOLUCIÓN")
    print("=" * 60)
    for i, result in enumerate(results[:5]):
        print(f"\nTupla {i+1}: {result['parameters']}")
        print(f"  Raíces: {result['roots']}")
