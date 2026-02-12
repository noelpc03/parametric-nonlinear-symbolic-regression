"""
Configuración para la definición de ecuaciones
"""

# Ejemplo de ecuación a resolver: ax^2 + bx + c = 0
# Se puede cambiar por cualquier ecuación

EQUATION_STRING = "a*x**2 + b*x + c"  # Expresión simbólica
VARIABLES = ["x"]  # Variables a resolver (incógnitas)
PARAMETERS = ["a", "b", "c"]  # Parámetros

# Para ecuaciones con múltiples variables, por ejemplo:
# EQUATION_STRING = "(x - a**2) * (y - a*b)"
# VARIABLES = ["x", "y"]
# PARAMETERS = ["a", "b"]
