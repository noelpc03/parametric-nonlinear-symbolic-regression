"""
Resolución de ecuaciones para encontrar ceros.

Dos métodos disponibles:
  - 'solve':  resolución simbólica (SymPy solve) — exacta, encuentra todas las raíces
  - 'nsolve': resolución numérica (SymPy nsolve) — aproximada, útil cuando solve falla
"""
import numpy as np
import sympy as sp
from typing import List, Dict, Any
from tqdm import tqdm


def _nsolve_multiple(equation, variable, guesses, complex_tol=1e-10, root_tol=1e-8):
    """
    Ejecuta sp.nsolve con múltiples puntos iniciales para encontrar
    varias raíces de la ecuación.

    nsolve solo encuentra UNA raíz por vez (la más cercana al guess),
    así que probamos con muchos guesses y eliminamos duplicados.

    Args:
        equation:    expresión SymPy ya sustituida (sin parámetros, solo con x)
        variable:    símbolo de la incógnita
        guesses:     lista de puntos iniciales a probar
        complex_tol: tolerancia para considerar una raíz como real
        root_tol:    tolerancia para considerar dos raíces como la misma

    Returns:
        roots: lista de raíces reales únicas encontradas
    """
    found_roots = []

    for guess in guesses:
        try:
            sol = sp.nsolve(equation, variable, guess)
            val = complex(sol)

            # Descartar raíces complejas
            if abs(val.imag) > complex_tol:
                continue

            real_val = val.real

            # Verificar que no sea duplicada de una ya encontrada
            is_duplicate = any(abs(real_val - r) < root_tol for r in found_roots)
            if not is_duplicate:
                found_roots.append(real_val)

        except (sp.calculus.util.AccumBounds, ValueError, ZeroDivisionError):
            # nsolve no convergió desde este guess — ignorar
            continue
        except Exception:
            continue

    return found_roots


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
        method: 'solve' (simbólico, exacto) o 'nsolve' (numérico, aproximado)
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
            # Resolver simbólicamente — encuentra TODAS las raíces exactas
            solutions = sp.solve(eq_substituted, variable)

            # Convertir a valores numéricos
            roots = []
            for sol in solutions:
                try:
                    val = complex(sol.evalf())

                    if filter_complex:
                        if abs(val.imag) < complex_tol:
                            roots.append(val.real)
                    else:
                        roots.append(val)
                except Exception:
                    continue

        elif method == 'nsolve':
            # Resolver numéricamente — prueba múltiples guesses
            guesses = np.linspace(-10, 10, 41)  # 41 puntos de -10 a 10
            roots = _nsolve_multiple(
                eq_substituted, variable, guesses, complex_tol=complex_tol
            )

        else:
            raise ValueError(f"Método desconocido: {method}")
        
        # Ordenar raíces
        if sort_roots and len(roots) > 0:
            roots = sorted(roots)
        
        return roots
    
    except Exception:
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
        variables: Lista de variables incógnita a resolver
        param_names: Lista de nombres de parámetros en el orden del grid
        param_symbols: Diccionario {nombre: símbolo} de parámetros
        parameter_grid: Array (N, num_params) con tuplas de parámetros
        method: Método de resolución ('solve' o 'nsolve')
        filter_complex: Si True, filtra raíces complejas
        complex_tol: Tolerancia para considerar una raíz como real
        sort_roots: Si True, ordena las raíces numéricamente
    
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
    import os, sys
    _parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, _parent)
    from config import (SOLVER_METHOD, FILTER_COMPLEX, COMPLEX_TOLERANCE, SORT_ROOTS,
                        EQUATION_STRING, VARIABLES, PARAMETERS,
                        PARAMETER_RANGES)

    # Añadir carpetas hermanas al path
    sys.path.insert(0, os.path.join(_parent, '1_equation_definition'))
    sys.path.insert(0, os.path.join(_parent, '2_parameter_grid'))

    from equation_parser import parse_equation
    from grid_generator import generate_grid
    
    # Parsear ecuación
    equation, symbols = parse_equation(EQUATION_STRING, VARIABLES, PARAMETERS)
    
    # Generar grid
    grid, param_names = generate_grid(PARAMETER_RANGES)
    
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
