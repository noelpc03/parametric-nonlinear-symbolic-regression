"""
Configuración para regresión simbólica adaptada a descubrimiento de expresiones analíticas
"""

# Parámetros de la función de pérdida sigmoidal
EPSILON = 0.05  # Tolerancia para considerar un punto como "matcheado"
K = 10  # Pendiente de la transición sigmoidal (qué tan suave es la transición)

# Parámetros del modelo PySR
NITERATIONS = 50  # Número de iteraciones evolutivas por modelo
POPULATIONS = 10  # Número de poblaciones
UNARY_OPERATORS = ["sin", "cos", "exp", "log", "sqrt", "abs", "neg"]
BINARY_OPERATORS = ["+", "-", "*", "/", "^"]

# Parámetros del algoritmo iterativo
MIN_POINTS = 5  # Mínimo de puntos para continuar 
MAX_ITERATIONS = 20  # Número máximo de iteraciones del algoritmo (None = sin límite)
MAX_CONSECUTIVE_NO_MATCH = 3  # Máximo de intentos consecutivos sin matchear antes de detenerse

# Parámetros avanzados de PySR
PARSIMONY = 0.005  # Penalización por complejidad (favorece funciones simples)
POPULATION_SIZE = 50  # Tamaño de cada población
NCYCLES_PER_ITERATION = 800  # Ciclos evolutivos por iteración
MAXSIZE = 30  # Complejidad máxima permitida
TURBO = True  # Optimizaciones agresivas
