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
EXPERIMENT_NAME = "test_1"

# ============================================================
# 2. DEFINICIÓN DE LA ECUACIÓN
# ============================================================

# Ecuación a resolver: f(x; params) = 0
# Caso quadratic_13_factored
# (x - a) * (x + a) = 0  -> raíces esperadas: -a y a
EQUATION_STRING = "(x - a) * (x + a)"
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
  "a": (0.1, 5, 50),
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
NITERATIONS = 500 
POPULATIONS = 30  
UNARY_OPERATORS = ["neg"]
BINARY_OPERATORS = ["+", "-", "*", "/"]

# Operadores custom para PySR (fuente única de verdad).
# Se expresan en sintaxis Julia porque PySR los evalúa del lado de Julia.
CUSTOM_UNARY_OPERATOR_DEFINITIONS = [
  "safe_sqrt(x) = sqrt(abs(x))",                                    # raíz 2
  "safe_cbrt(x) = cbrt(x)",                                         # raíz 3 (preserva signo)
  "safe_root4(x) = sqrt(sqrt(abs(x)))",                             # raíz 4
  "safe_root5(x) = copysign(abs(x)^(one(x)/typeof(x)(5)), x)",      # raíz 5
  "safe_root6(x) = cbrt(sqrt(abs(x)))",                             # raíz 6
  "safe_root7(x) = copysign(abs(x)^(one(x)/typeof(x)(7)), x)",      # raíz 7
  "safe_root8(x) = sqrt(sqrt(sqrt(abs(x))))",                       # raíz 8
  "safe_root9(x) = cbrt(cbrt(x))",                                  # raíz 9
  "safe_root10(x) = sqrt(sqrt(abs(x))) * sqrt(abs(x))^(one(x)/typeof(x)(5))",  # raíz 10
]

CUSTOM_BINARY_OPERATOR_DEFINITIONS = [
  # Preserva el signo (crucial para raíces impares) y evita NaN en bases negativas.
  "safe_pow(x, y) = copysign(abs(x)^y, x)",
]

USE_SIGMOID_LOSS = False  # False = usar MSE estándar

# Nueva pérdida por conteo duro de matches:
# Un punto matchea si |y - y_pred| < MATCH_COUNT_EPSILON.
# La optimización minimiza la fracción de no-matches (equivale a maximizar matches).
USE_MATCH_COUNT_LOSS = False
MATCH_COUNT_EPSILON = 1e-4

# ── Parámetros del algoritmo iterativo ──
MIN_POINTS = 5  # Mínimo de puntos para continuar
MAX_ITERATIONS = None  # Sin límite de iteraciones
MAX_CONSECUTIVE_NO_MATCH = 3  # Corte global: parar tras N iteraciones consecutivas sin matches

# Modo de entrada para la regresión simbólica:
#   - 'combined': usa todas las tuplas (params -> root) juntas
#                 y el algoritmo iterativo descubre ecuaciones secuencialmente.
#   - 'branches': separa por rama antes de SR (modo legacy).
SR_INPUT_MODE = 'combined'

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
