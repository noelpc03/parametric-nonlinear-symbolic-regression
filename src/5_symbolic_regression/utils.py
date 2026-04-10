"""
Funciones auxiliares para regresión simbólica
"""
import numpy as np


def find_matched_points(X, y, y_pred, epsilon=0.05, mode="relative"):
    """
    Identifica los índices de los puntos que son matcheados por la función.

    Modos disponibles:
        - relative: |y - y_pred| < epsilon * (1 + |y|)
        - absolute: |y - y_pred| < epsilon
    
    Args:
        X: Valores de entrada (no usado, pero se mantiene por consistencia)
        y: Valores verdaderos
        y_pred: Valores predichos
        epsilon: Tolerancia de matcheo (interpretada según mode)
        mode: "relative" o "absolute"
    
    Returns:
        matched_indices: Array con los índices de los puntos matcheados
    """
    diff = np.abs(y - y_pred)

    if mode == "absolute":
        threshold = epsilon
    elif mode == "relative":
        threshold = epsilon * (1.0 + np.abs(y))
    else:
        raise ValueError(f"mode desconocido: {mode}. Usa 'relative' o 'absolute'.")

    matched_indices = np.where(diff < threshold)[0]
    return matched_indices


def print_iteration_header():
    """
    Imprime el encabezado del algoritmo iterativo.

    Returns:
        None
    """
    print("=" * 60)
    print("Iniciando algoritmo iterativo de regresión simbólica")
    print("=" * 60)


def print_iteration_info(iteration, num_remaining):
    """
    Imprime información de la iteración actual.

    Args:
        iteration: Número de iteración actual
        num_remaining: Cantidad de puntos restantes por matchear

    Returns:
        None
    """
    print(f"\n--- Iteración {iteration} ---")
    print(f"Puntos restantes: {num_remaining}")


def print_iteration_result(equation, num_matched):
    """
    Imprime el resultado de una iteración.

    Args:
        equation: Ecuación seleccionada en la iteración
        num_matched: Cantidad de puntos matcheados por la ecuación

    Returns:
        None
    """
    print(f"✓ Ecuación encontrada: {equation}")
    print(f"✓ Puntos matcheados: {num_matched}")


def print_final_summary(num_remaining, original_indices, num_results, total_matched, total_points):
    """
    Imprime el resumen final del algoritmo.

    Args:
        num_remaining: Cantidad de puntos que quedaron sin matchear
        original_indices: Índices originales de los puntos no matcheados
        num_results: Cantidad de ecuaciones aceptadas
        total_matched: Total de puntos matcheados en todas las iteraciones
        total_points: Cantidad total de puntos de entrada

    Returns:
        None
    """
    if num_remaining > 0:
        print(f"\n⚠️  Quedan {num_remaining} puntos sin matchear")
        print(f"Índices de puntos sin matchear: {original_indices}")
    else:
        print(f"\n✓ TODOS LOS PUNTOS FUERON MATCHEADOS!")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Total de funciones encontradas: {num_results}")
    print(f"Total de puntos matcheados: {total_matched}/{total_points}")
    print(f"Porcentaje de cobertura: {100*total_matched/total_points:.1f}%")
