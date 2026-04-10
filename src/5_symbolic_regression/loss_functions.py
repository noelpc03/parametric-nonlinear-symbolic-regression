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


def match_count_loss(y_true, y_pred, epsilon=1e-4):
    """
    Pérdida dura por conteo de matches.

    Un punto matchea si |y_true - y_pred| < epsilon.
    La pérdida es la fracción de puntos que NO matchean:

        loss = 1 - (#matches / N)

    Minimizar esta pérdida equivale a maximizar la cantidad de puntos matcheados.

    Args:
        y_true: Valores verdaderos
        y_pred: Valores predichos
        epsilon: Umbral absoluto de match

    Returns:
        loss: Fracción de no-matches en [0, 1]
    """
    diff = np.abs(y_true - y_pred)
    matched = diff < epsilon
    return 1.0 - np.mean(matched)


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


def get_julia_match_count_loss_function(epsilon=1e-4):
    """
    Genera la pérdida de conteo duro en sintaxis Julia para PySR.

    Para cada punto:
        - 0.0 si matchea (|target - prediction| < epsilon)
        - 1.0 si no matchea

    El promedio sobre el dataset equivale a la fracción de puntos no matcheados.

    Args:
        epsilon: Umbral absoluto de match

    Returns:
        str: Función de pérdida en Julia
    """
    return f"match_count_loss(prediction, target) = ifelse(abs(target - prediction) < {epsilon}, 0.0, 1.0)"
