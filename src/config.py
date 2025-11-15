"""
Configuración y parámetros del proyecto de regresión simbólica iterativa
"""

# Parámetros de generación de datos
DATA_SEED = 0
X_MIN = -3
X_MAX = 3
NUM_POINTS = 100

# Parámetros de la función de pérdida sigmoidal
EPSILON = 0.05  # Tolerancia para considerar un punto como "matcheado"
K = 10  # Pendiente de la transición sigmoidal (qué tan suave es la transición)

# Parámetros del modelo PySR
NITERATIONS = 20  # Número de iteraciones evolutivas por modelo
POPULATIONS = 6  # Número de poblaciones
UNARY_OPERATORS = ["sin", "cos", "tan", "exp", "log", "abs", "sign", "tan", "asin", "acos", "atan"]
BINARY_OPERATORS = ["+", "-", "*", "/", "^"]

# Parámetros del algoritmo iterativo
MIN_POINTS = 1  # Mínimo de puntos para continuar 
MAX_ITERATIONS = 100  # Número máximo de iteraciones del algoritmo (None = sin límite, limitado para pruebas)
MAX_CONSECUTIVE_NO_MATCH = 3  # Máximo de intentos consecutivos sin matchear antes de detenerse

# Parámetros de visualización
FIGURE_SIZE = (16, 6)
POINT_SIZE_SCATTER = 30
POINT_SIZE_MATCHED = 100
POINT_SIZE_UNMATCHED = 50
LINE_WIDTH = 2
