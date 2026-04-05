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
    """Imprime el encabezado del algoritmo iterativo"""
    print("=" * 60)
    print("Iniciando algoritmo iterativo de regresión simbólica")
    print("=" * 60)


def print_iteration_info(iteration, num_remaining):
    """Imprime información de la iteración actual"""
    print(f"\n--- Iteración {iteration} ---")
    print(f"Puntos restantes: {num_remaining}")


def print_iteration_result(equation, num_matched):
    """Imprime el resultado de una iteración"""
    print(f"✓ Ecuación encontrada: {equation}")
    print(f"✓ Puntos matcheados: {num_matched}")


def print_final_summary(num_remaining, original_indices, num_results, total_matched, total_points):
    """Imprime el resumen final del algoritmo"""
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
