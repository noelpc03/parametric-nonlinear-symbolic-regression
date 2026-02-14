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
EXPERIMENT_NAME = "quadratic_test"

# ============================================================
# 2. DEFINICIÓN DE LA ECUACIÓN
# ============================================================

# Ecuación a resolver: f(x; params) = 0
# Ejemplo: ax² + bx + c = 0
EQUATION_STRING = "a*x**2 + b*x + c"
VARIABLES = ["x"]
PARAMETERS = ["a", "b", "c"]

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
    "a": (1, 3, 12),    # a positivo, evitar 0
    "b": (-3, 3, 12),   # b en rango moderado
    "c": (-2, 2, 12),   # c en rango moderado
}

# Método de muestreo
# 'grid': Grid completo (producto cartesiano) - puede ser muy grande
# 'random': Muestreo aleatorio uniforme
# 'lhs': Latin Hypercube Sampling (mejor cobertura que random)
SAMPLING_METHOD = 'grid'

# Número de muestras (solo para 'random' y 'lhs')
NUM_SAMPLES = 10000

# Semilla para reproducibilidad
RANDOM_SEED = 42

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
UNARY_OPERATORS = ["sqrt", "neg"]
BINARY_OPERATORS = ["+", "-", "*", "/"]
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
