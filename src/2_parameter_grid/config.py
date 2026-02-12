"""
Configuración para la generación del grid de parámetros
"""

# Rangos para cada parámetro
# Formato: {nombre_parametro: (min, max, num_puntos)}
PARAMETER_RANGES = {
    "a": (0.5, 2, 10),   # a entre 0.5 y 2, con 10 puntos (evitar a=0)
    "b": (-2, 2, 10),    # b entre -2 y 2, con 10 puntos
    "c": (-1, 1, 10),    # c entre -1 y 1, con 10 puntos
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
