"""
Configuración para encontrar ceros de ecuaciones
"""

# Método de resolución
# 'solve': SymPy solve (simbólico, puede ser lento)
# 'nsolve': SymPy nsolve (numérico, más rápido pero requiere guess)
# 'roots': numpy.roots (solo para polinomios)
SOLVER_METHOD = 'solve'

# Para nsolve: punto inicial
INITIAL_GUESS = 0.0

# Filtrar raíces complejas (quedarse solo con reales)
FILTER_COMPLEX = True

# Tolerancia para considerar una raíz como real (parte imaginaria < tol)
COMPLEX_TOLERANCE = 1e-10

# Ordenar raíces por valor (True) o por orden de aparición (False)
SORT_ROOTS = True

# Timeout por tupla de parámetros (segundos, None = sin límite)
TIMEOUT_PER_TUPLE = 5.0
