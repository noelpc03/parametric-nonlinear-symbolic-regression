"""
Configuración unificada del sistema de descubrimiento de expresiones analíticas.

Todas las configuraciones del pipeline se definen aquí:
  1. Opciones globales
  2. Definición de la ecuación
  3. Grid de parámetros
  4. Resolución (zero-finding)
  5. Regresión simbólica
"""

# ============================================================
# 1. OPCIONES GLOBALES
# ============================================================

# Directorio de salida para resultados
OUTPUT_DIR = "outputs_analytical"

# Verbose: imprimir información detallada
VERBOSE = True

# Guardar resultados intermedios
SAVE_INTERMEDIATE = True

# Nombre del experimento (para organizar outputs)
EXPERIMENT_NAME = "linear_test"

# ============================================================
# 2. DEFINICIÓN DE LA ECUACIÓN
# ============================================================

# Ecuación a resolver: f(x; params) = 0
# Ejemplo: x + a - 2 = 0  →  x = 2 - a
EQUATION_STRING = "x + a - 2"
VARIABLES = ["x"]
PARAMETERS = ["a"]

# Para ecuaciones con múltiples variables, por ejemplo:
# EQUATION_STRING = "(x - a**2) * (y - a*b)"
# VARIABLES = ["x", "y"]
# PARAMETERS = ["a", "b"]

# ============================================================
# 3. GRID DE PARÁMETROS
# ============================================================

# Rangos para cada parámetro
# Formato: {nombre_parametro: (min, max, num_puntos)}
PARAMETER_RANGES = {
    "a": (-5, 5, 50),
}

# Método: producto cartesiano (grid regular)
# Para cada parámetro se divide [min, max] en (num_points - 1) partes iguales,
# tomando los extremos y los puntos de corte. Luego se generan todas las
# combinaciones posibles.

# ============================================================
# 4. RESOLUCIÓN (ZERO-FINDING)
# ============================================================

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

# ============================================================
# 5. REGRESIÓN SIMBÓLICA
# ============================================================

# ── Parámetros del matcheo post-entrenamiento ──
EPSILON = 0.005  # Tolerancia relativa para considerar un punto como "matcheado"
# Un punto matchea si |y - y_pred| < EPSILON * (1 + |y|)
# Esto adapta la tolerancia al orden de magnitud de los valores
K = 100  # No se usa con MSE loss, solo para matcheo

# ── Parámetros del modelo PySR ──
NITERATIONS = 500  # Más iteraciones: con batching la RAM no crece
POPULATIONS = 30  # Más poblaciones con batching (solo evalúa 200 pts/batch, no todos)
UNARY_OPERATORS = ["neg"]
BINARY_OPERATORS = ["+", "-", "*", "/"]
# safe_pow(x, y) = sign(x) * abs(x)^y se agrega como operador inline en symbolic_regression.py
# Preserva el signo (crucial para raíces impares: (-8)^(1/3) = -2)
# y protege contra NaN (abs() evita bases negativas en potencias fraccionarias).
USE_SIGMOID_LOSS = False  # False = usar MSE estándar

# ── Parámetros del algoritmo iterativo ──
MIN_POINTS = 5  # Mínimo de puntos para continuar
MAX_ITERATIONS = 5  # Máximo de iteraciones del proceso iterativo
MAX_CONSECUTIVE_NO_MATCH = 2

# ── Estrategia multi-intento por iteración ──
# En cada iteración del proceso iterativo, PySR se ejecuta NUM_ATTEMPTS veces.
# Se evalúa el Hall of Fame completo de cada intento y se elige la ecuación
# que matchee la mayor cantidad de puntos.
# Si un intento logra 100% de los puntos restantes, se detiene.
NUM_ATTEMPTS = 3

# Fracción mínima de puntos restantes que debe matchear una ecuación
# para ser aceptada. Si ningún intento supera este umbral, la iteración
# se considera fallida.
MIN_MATCH_FRACTION = 0.05  # Al menos 5% de los puntos restantes

# ── Parámetros avanzados de PySR ──
PARSIMONY = 0.0  # No penalizar complejidad
POPULATION_SIZE = 50  # Equilibrio entre diversidad y memoria
NCYCLES_PER_ITERATION = 550  # Ciclos evolutivos por iteración
MAXSIZE = 25  # La cuadrática tiene ~15 nodos, 25 da margen
TURBO = True  # Optimizaciones agresivas
PROCS = 0  # Sin multiproceso: usa UN solo proceso Julia (ahorra mucha RAM)

# # ── Parámetros de diversidad evolutiva ──
# # Reducir presión selectiva para evitar convergencia prematura.
# # Defaults de PySR: tournament_selection_p=0.982, tournament_selection_n=15
# # Con p=0.982 el mejor individuo se elige 98.2% de las veces → la población
# # converge a clones en pocas generaciones (Goldberg & Deb, 1991).
# # Con p=0.75, n=8: P(2°)=18.8%, P(3°)=4.7% → diversidad real.
# TOURNAMENT_SELECTION_P = 0.75   # Prob. de elegir al mejor en torneo (default: 0.982)
# TOURNAMENT_SELECTION_N = 8      # Tamaño del torneo (default: 15)
# PROBABILITY_NEGATE_CONSTANT = 0.05  # Prob. de negar constante en mutación (default: 0.00743)
# FRACTION_REPLACED = 0.05       # Migración entre islas: 50*0.05=2.5 ind/gen (default: 0.00036≈0)
# CROSSOVER_PROBABILITY = 0.066  # Prob. de cruce vs mutación (default: 0.0259)
# WEIGHT_MUTATE_OPERATOR = 0.5   # Peso relativo de mutar operador (default: 0.293)
