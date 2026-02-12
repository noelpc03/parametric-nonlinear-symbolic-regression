"""
Módulo de regresión simbólica iterativa
"""
import numpy as np
from pysr import PySRRegressor
from typing import List, Dict

from config import (
    EPSILON, K, NITERATIONS, POPULATIONS, MIN_POINTS, 
    MAX_ITERATIONS, MAX_CONSECUTIVE_NO_MATCH,
    UNARY_OPERATORS, BINARY_OPERATORS
)
from loss_functions import get_julia_loss_function
from utils import (
    find_matched_points, print_iteration_header, print_iteration_info,
    print_iteration_result, print_final_summary
)


def train_symbolic_model(X, y, k=K, epsilon=EPSILON, niterations=NITERATIONS):
    """
    Entrena un modelo de regresión simbólica con la función de pérdida sigmoidal.
    
    Args:
        X: Datos de entrada (shape: (n, 1))
        y: Datos de salida (shape: (n,))
        k: Pendiente de la sigmoide
        epsilon: Tolerancia para matcheo
        niterations: Número de iteraciones evolutivas
    
    Returns:
        model: Modelo PySRRegressor entrenado
    """
    loss_function = get_julia_loss_function(epsilon, k)
    
    model = PySRRegressor(
        niterations=niterations,
        populations=POPULATIONS,
        elementwise_loss=loss_function,
        model_selection="best",
        variable_names=["x"],
        unary_operators=UNARY_OPERATORS,
        binary_operators=BINARY_OPERATORS,
        temp_equation_file=True,   # Usar archivos temporales en lugar de outputs/
        delete_tempfiles=True,     # Borrar archivos temporales al finalizar
    )
    
    model.fit(X, y)
    return model


def iterative_symbolic_regression(
    X, y, 
    epsilon=EPSILON, 
    k=K, 
    niterations=NITERATIONS, 
    min_points=MIN_POINTS, 
    max_iterations=MAX_ITERATIONS
):
    """
    Algoritmo iterativo de regresión simbólica:
    1. Encuentra una función que matchee la mayor cantidad de puntos
    2. Elimina esos puntos del conjunto
    3. Repite hasta que no queden puntos o no se puedan matchear más
    
    Args:
        X: datos de entrada (shape: (n, 1))
        y: datos de salida (shape: (n,))
        epsilon: tolerancia para considerar un punto como "matcheado"
        k: pendiente de la sigmoide
        niterations: número de iteraciones para cada modelo
        min_points: número mínimo de puntos para continuar el proceso
        max_iterations: número máximo de iteraciones del algoritmo completo (None = sin límite)
    
    Returns:
        List[Dict]: Lista de diccionarios, cada uno con:
            - 'iteration': número de iteración
            - 'model': el modelo entrenado
            - 'equation': la ecuación simbólica
            - 'matched_indices': índices de los puntos matcheados (en el conjunto original)
            - 'X_matched': coordenadas X de los puntos matcheados
            - 'y_matched': coordenadas y de los puntos matcheados
            - 'num_matched': número de puntos matcheados
    """
    results = []
    
    # Creamos una copia de los datos para ir eliminando puntos
    X_remaining = X.copy()
    y_remaining = y.copy()
    
    # Mantenemos un mapeo de índices al conjunto original
    original_indices = np.arange(len(X))
    
    iteration = 0
    consecutive_no_match = 0  # Contador de iteraciones sin matcheos
    
    print_iteration_header()
    
    while len(X_remaining) >= min_points:
        iteration += 1
        
        # Verificar si alcanzamos el máximo de iteraciones
        if max_iterations is not None and iteration > max_iterations:
            print(f"\n⚠️  Se alcanzó el número máximo de iteraciones ({max_iterations})")
            break
        
        print_iteration_info(iteration, len(X_remaining))
        
        # Entrenar modelo con los puntos restantes
        model = train_symbolic_model(X_remaining, y_remaining, k=k, epsilon=epsilon, niterations=niterations)
        
        # Obtener predicciones
        y_pred = model.predict(X_remaining)
        
        # Identificar puntos matcheados
        matched_indices_local = find_matched_points(X_remaining, y_remaining, y_pred, epsilon=epsilon)
        
        if len(matched_indices_local) == 0:
            consecutive_no_match += 1
            print(f"⚠️  No se encontraron puntos matcheados en la iteración {iteration}")
            
            if consecutive_no_match >= MAX_CONSECUTIVE_NO_MATCH:
                print(f"⚠️  No se encontraron puntos matcheados en {MAX_CONSECUTIVE_NO_MATCH} iteraciones consecutivas.")
                print("Deteniendo el algoritmo.")
                break
            else:
                print(f"Reintentando... ({consecutive_no_match}/{MAX_CONSECUTIVE_NO_MATCH})")
                continue
        
        # Reiniciar contador si hubo matcheo
        consecutive_no_match = 0
        
        # Mapear índices locales a índices originales
        matched_indices_original = original_indices[matched_indices_local]
        
        # Obtener la ecuación y extraer información
        equation_series = model.get_best()
        
        # Extraer la ecuación en formato legible (sympy_format si está disponible)
        if hasattr(equation_series, 'get'):
            equation_str = equation_series.get('sympy_format', str(equation_series.get('equation', equation_series)))
        else:
            equation_str = str(equation_series)
        
        # Guardar resultados
        result = {
            'iteration': iteration,
            'model': model,
            'equation': equation_str,  # Guardar como string limpio
            'equation_series': equation_series,  # Guardar el objeto completo por si se necesita
            'matched_indices': matched_indices_original,
            'X_matched': X[matched_indices_original],
            'y_matched': y[matched_indices_original],
            'num_matched': len(matched_indices_original)
        }
        results.append(result)
        
        print_iteration_result(equation_str, len(matched_indices_original))
        
        # Eliminar puntos matcheados del conjunto restante
        mask = np.ones(len(X_remaining), dtype=bool)
        mask[matched_indices_local] = False
        
        X_remaining = X_remaining[mask]
        y_remaining = y_remaining[mask]
        original_indices = original_indices[mask]
    
    # Resumen final
    total_matched = sum(r['num_matched'] for r in results)
    print_final_summary(len(X_remaining), original_indices, len(results), total_matched, len(X))
    
    return results
