"""
Funciones auxiliares para el proyecto
"""
import numpy as np


def find_matched_points(X, y, y_pred, epsilon=0.05):
    """
    Identifica los índices de los puntos que son matcheados por la función.
    Un punto es matcheado si |y - y_pred| < epsilon
    
    Args:
        X: Valores de entrada (no usado, pero se mantiene por consistencia)
        y: Valores verdaderos
        y_pred: Valores predichos
        epsilon: Tolerancia para matcheo
    
    Returns:
        matched_indices: Array con los índices de los puntos matcheados
    """
    diff = np.abs(y - y_pred)
    matched_indices = np.where(diff < epsilon)[0]
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
        print(f"\n✓ ¡Todos los puntos han sido matcheados!")
    
    print("\n" + "=" * 60)
    print(f"Proceso completado: {num_results} funciones encontradas")
    print(f"Total de puntos matcheados: {total_matched}/{total_points}")
    print("=" * 60)


def print_results_summary(results):
    """Imprime un resumen detallado de los resultados"""
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    for i, result in enumerate(results):
        print(f"\nIteración {i+1}:")
        print(f"  Ecuación: {result['equation']}")
        print(f"  Puntos matcheados: {result['num_matched']}")
        if len(result['matched_indices']) > 10:
            print(f"  Índices: {result['matched_indices'][:10]}...")
        else:
            print(f"  Índices: {result['matched_indices']}")
