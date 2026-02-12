"""
Configuración global del sistema de descubrimiento de expresiones analíticas
"""

# ============================================================
# CONFIGURACIÓN DE LA ECUACIÓN
# ============================================================
# Se define en: 1_equation_definition/config.py

# ============================================================
# CONFIGURACIÓN DEL GRID DE PARÁMETROS
# ============================================================
# Se define en: 2_parameter_grid/config.py

# ============================================================
# CONFIGURACIÓN DE RESOLUCIÓN
# ============================================================
# Se define en: 3_zero_finding/config.py

# ============================================================
# CONFIGURACIÓN DE REGRESIÓN SIMBÓLICA
# ============================================================
# Se define en: symbolic_regression/config.py

# ============================================================
# OPCIONES GLOBALES
# ============================================================

# Directorio de salida para resultados
OUTPUT_DIR = "outputs_analytical"

# Verbose: imprimir información detallada
VERBOSE = True

# Guardar resultados intermedios
SAVE_INTERMEDIATE = True

# Nombre del experimento (para organizar outputs)
EXPERIMENT_NAME = "quadratic_equation"
