"""
Construcción de expresiones Piecewise cuando hay múltiples funciones por rama
"""
import sympy as sp
import numpy as np
from typing import List, Dict, Any


def build_piecewise_expression(functions: List[Dict[str, Any]],
                               param_names: List[str],
                               param_symbols: Dict[str, sp.Symbol]) -> sp.Piecewise:
    """
    Construye una expresión Piecewise para funciones múltiples de una rama.
    
    Args:
        functions: Lista de funciones encontradas (de iterative_symbolic_regression)
        param_names: Lista de nombres de parámetros
        param_symbols: Diccionario de símbolos SymPy de parámetros
    
    Returns:
        piecewise_expr: Expresión Piecewise de SymPy
    """
    if len(functions) == 1:
        # Si solo hay una función, no hace falta Piecewise
        return sp.sympify(functions[0]['equation'])
    
    # Para cada función, necesitamos definir la condición que determina
    # cuándo se aplica. Esto requiere análisis de los puntos matcheados.
    
    # Por ahora, implementamos una versión simple:
    # cada función se aplica en la región donde matchea puntos
    
    pieces = []
    
    for i, func in enumerate(functions):
        equation_str = func['equation']
        X_matched = func['X_matched']
        
        # Convertir ecuación a SymPy
        # Necesitamos mapear los nombres de variables del modelo
        # Por ahora asumimos que PySR usa x0, x1, x2, ... para los parámetros
        expr = sp.sympify(equation_str)
        
        # Reemplazar x0, x1, ... por los nombres reales de parámetros
        for j, param_name in enumerate(param_names):
            expr = expr.subs(f'x{j}', param_symbols[param_name])
        
        # Definir condición (región donde aplica)
        # Esto es complejo y requiere clustering o análisis de regiones
        # Por ahora, usamos una condición simbólica genérica
        
        if i < len(functions) - 1:
            # Para todas menos la última, definir una condición
            # Ejemplo simple: basado en rango de primer parámetro
            if len(X_matched) > 0:
                min_val = np.min(X_matched[:, 0])
                max_val = np.max(X_matched[:, 0])
                first_param = param_symbols[param_names[0]]
                
                condition = sp.And(first_param >= min_val, first_param <= max_val)
                pieces.append((expr, condition))
            else:
                # Sin puntos matcheados, skip
                continue
        else:
            # La última función es el "else" (True)
            pieces.append((expr, True))
    
    return sp.Piecewise(*pieces)


def find_region_boundaries(X_matched_list: List[np.ndarray],
                          param_names: List[str]) -> List[Dict]:
    """
    Encuentra las fronteras de las regiones donde aplica cada función.
    
    Esta es una función auxiliar para determinar automáticamente
    las condiciones de las expresiones Piecewise.
    
    Args:
        X_matched_list: Lista de arrays X_matched para cada función
        param_names: Nombres de parámetros
    
    Returns:
        boundaries: Lista de diccionarios con info de fronteras
    """
    # Implementación simplificada
    # En un sistema real, esto requeriría clustering o análisis espacial
    
    boundaries = []
    
    for X_matched in X_matched_list:
        if len(X_matched) == 0:
            boundaries.append({})
            continue
        
        # Calcular rangos para cada parámetro
        ranges = {}
        for i, param in enumerate(param_names):
            ranges[param] = {
                'min': float(np.min(X_matched[:, i])),
                'max': float(np.max(X_matched[:, i])),
                'mean': float(np.mean(X_matched[:, i])),
                'std': float(np.std(X_matched[:, i]))
            }
        
        boundaries.append(ranges)
    
    return boundaries


def simplify_to_single_expression(functions: List[Dict[str, Any]]) -> str:
    """
    Si las funciones son equivalentes o muy similares, devuelve una sola.
    
    Args:
        functions: Lista de funciones
    
    Returns:
        simplified: Expresión simplificada (string)
    """
    if len(functions) == 1:
        return functions[0]['equation']
    
    # Comparar ecuaciones
    equations = [f['equation'] for f in functions]
    unique_equations = list(set(equations))
    
    if len(unique_equations) == 1:
        # Todas las funciones son iguales
        return unique_equations[0]
    
    # Si son diferentes, devolver la que matchea más puntos
    best_func = max(functions, key=lambda f: f['num_matched'])
    return best_func['equation']


if __name__ == "__main__":
    # Ejemplo de uso
    print("Módulo de construcción de expresiones Piecewise")
    print("Este módulo se usa cuando el algoritmo iterativo encuentra")
    print("múltiples funciones para una misma rama de raíces.")
    
    # Crear símbolos de ejemplo
    a, b, c = sp.symbols('a b c')
    param_symbols = {'a': a, 'b': b, 'c': c}
    param_names = ['a', 'b', 'c']
    
    # Simulación de funciones encontradas
    functions_example = [
        {
            'equation': '(-x1 + (x1**2 - 4*x0*x2)**0.5) / (2*x0)',
            'X_matched': np.array([[1, 2, -1], [1.5, 2.5, -0.5]]),
            'num_matched': 50
        },
        {
            'equation': '(-x1 - (x1**2 - 4*x0*x2)**0.5) / (2*x0)',
            'X_matched': np.array([[1, 2, 1], [1.5, 2.5, 1.5]]),
            'num_matched': 45
        }
    ]
    
    print("\n" + "=" * 60)
    print("EJEMPLO DE CONSTRUCCIÓN PIECEWISE")
    print("=" * 60)
    
    boundaries = find_region_boundaries(
        [f['X_matched'] for f in functions_example],
        param_names
    )
    
    print("\nFronteras detectadas:")
    for i, boundary in enumerate(boundaries):
        print(f"\nFunción {i+1}:")
        for param, ranges in boundary.items():
            print(f"  {param}: [{ranges['min']:.2f}, {ranges['max']:.2f}]")
