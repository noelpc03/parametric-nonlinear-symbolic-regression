"""
Funciones de pérdida para regresión simbólica
"""
import numpy as np


def sigmoid_loss(y_true, y_pred, epsilon=0.1, k=10):
    """
    Pérdida suave basada en una sigmoide.
    Cuanto más cerca está el punto (|y - f(x)| <= ε), menor penalización.
    
    Args:
        y_true: Valores verdaderos
        y_pred: Valores predichos
        epsilon: Umbral de tolerancia
        k: Pendiente de la transición sigmoidal
    
    Returns:
        loss: Valor de pérdida (entre 0 y 1)
    """
    diff = np.abs(y_true - y_pred)
    penalties = 1 / (1 + np.exp(-k * (epsilon - diff)))
    return 1 - np.mean(penalties)


def get_julia_loss_function(epsilon, k):
    """
    Genera la función de pérdida en sintaxis Julia para PySR.
    
    Args:
        epsilon: Umbral de tolerancia
        k: Pendiente de la transición sigmoidal
    
    Returns:
        str: Función de pérdida en Julia
    """
    return f"sigmoid_loss(prediction, target) = 1 / (1 + exp(-{k} * (abs(target - prediction) - {epsilon})))"
