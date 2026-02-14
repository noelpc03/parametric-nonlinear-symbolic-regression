"""
Parseo y definición de ecuaciones simbólicas
"""
import os
import sympy as sp
from typing import List, Tuple


def parse_equation(equation_str: str, variables: List[str], parameters: List[str]) -> Tuple[sp.Expr, dict]:
    """
    Parsea una ecuación string y la convierte en expresión SymPy.
    
    Args:
        equation_str: String con la ecuación (ej: "a*x**2 + b*x + c")
        variables: Lista de nombres de variables (incógnitas)
        parameters: Lista de nombres de parámetros
    
    Returns:
        equation: Expresión SymPy
        symbols_dict: Diccionario con todos los símbolos {nombre: símbolo}
    """
    # Crear símbolos SymPy
    var_symbols = sp.symbols(variables)
    param_symbols = sp.symbols(parameters)
    
    # Crear diccionario de símbolos
    if isinstance(var_symbols, sp.Symbol):
        var_symbols = [var_symbols]
    if isinstance(param_symbols, sp.Symbol):
        param_symbols = [param_symbols]
    
    symbols_dict = {}
    for name, symbol in zip(variables, var_symbols):
        symbols_dict[name] = symbol
    for name, symbol in zip(parameters, param_symbols):
        symbols_dict[name] = symbol
    
    # Parsear la ecuación
    equation = sp.sympify(equation_str, locals=symbols_dict)
    
    return equation, symbols_dict


def get_equation_info(equation: sp.Expr, symbols_dict: dict) -> dict:
    """
    Obtiene información sobre la ecuación.
    
    Returns:
        info: Diccionario con información de la ecuación
    """
    return {
        'equation': equation,
        'latex': sp.latex(equation),
        'complexity': len(str(equation)),
        'symbols': symbols_dict
    }


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from config import EQUATION_STRING, VARIABLES, PARAMETERS
    
    equation, symbols = parse_equation(EQUATION_STRING, VARIABLES, PARAMETERS)
    info = get_equation_info(equation, symbols)
    
    print("=" * 60)
    print("ECUACIÓN PARSEADA")
    print("=" * 60)
    print(f"Expresión: {equation}")
    print(f"LaTeX: {info['latex']}")
    print(f"Variables: {VARIABLES}")
    print(f"Parámetros: {PARAMETERS}")
