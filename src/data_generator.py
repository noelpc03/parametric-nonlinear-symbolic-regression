"""
Generación de datos para el proyecto de regresión simbólica
"""
import numpy as np
from config import DATA_SEED, X_MIN, X_MAX, NUM_POINTS


def generate_random_data(seed=DATA_SEED, x_min=X_MIN, x_max=X_MAX, num_points=NUM_POINTS):
    """
    Genera datos de ejemplo con ruido aleatorio.
    
    Args:
        seed: Semilla para reproducibilidad
        x_min: Valor mínimo de X
        x_max: Valor máximo de X
        num_points: Número de puntos a generar
    
    Returns:
        X: array de shape (num_points, 1) con valores de x
        y: array de shape (num_points,) con valores de y (ruido aleatorio)
    """
    np.random.seed(seed)
    X = np.linspace(x_min, x_max, num_points).reshape(-1, 1)
    y = np.random.randn(len(X))
    return X, y


def generate_data_from_functions(functions, x_min=X_MIN, x_max=X_MAX, num_points=NUM_POINTS, noise=0.0):
    """
    Genera datos a partir de una lista de funciones.
    
    Args:
        functions: Lista de funciones que toman X y devuelven y
        x_min: Valor mínimo de X
        x_max: Valor máximo de X
        num_points: Número de puntos a generar por función
        noise: Nivel de ruido a agregar (desviación estándar)
    
    Returns:
        X: array con valores de x
        y: array con valores de y
    """
    X_list = []
    y_list = []
    
    for func in functions:
        X_func = np.linspace(x_min, x_max, num_points).reshape(-1, 1)
        y_func = func(X_func.flatten())
        
        if noise > 0:
            y_func += np.random.randn(len(y_func)) * noise
        
        X_list.append(X_func)
        y_list.append(y_func)
    
    X = np.vstack(X_list)
    y = np.concatenate(y_list)
    
    return X, y
