"""
Módulo de regresión simbólica iterativa adaptado para múltiples parámetros.

Arquitectura:
  - Proceso iterativo: encuentra funciones, quita puntos, repite
  - Dentro de cada iteración: múltiples intentos de PySR (NUM_ATTEMPTS)
  - Dentro de cada intento: evalúa todo el Hall of Fame
  - Se queda con la ecuación que matchea más puntos entre todos los intentos
"""
import os
import sys
import numpy as np
from pysr import PySRRegressor
from typing import List, Dict
import sympy

# Asegurar que src/ esté en el path para importar el config unificado
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from config import (
    EPSILON, K, NITERATIONS, POPULATIONS, MIN_POINTS,
    MAX_ITERATIONS, MAX_CONSECUTIVE_NO_MATCH,
    UNARY_OPERATORS, BINARY_OPERATORS,
    PARSIMONY, POPULATION_SIZE, NCYCLES_PER_ITERATION,
    MAXSIZE, TURBO, PROCS, NUM_ATTEMPTS,
    MIN_MATCH_FRACTION, USE_SIGMOID_LOSS,
    TOURNAMENT_SELECTION_P, TOURNAMENT_SELECTION_N,
    PROBABILITY_NEGATE_CONSTANT, FRACTION_REPLACED,
    CROSSOVER_PROBABILITY, WEIGHT_MUTATE_OPERATOR,
)

from loss_functions import get_julia_loss_function
from utils import (
    find_matched_points, print_iteration_header, print_iteration_info,
    print_iteration_result, print_final_summary
)


def train_symbolic_model(X, y, param_names, k=K, epsilon=EPSILON, niterations=NITERATIONS):
    """
    Entrena un modelo de regresión simbólica.
    """
    model_kwargs = dict(
        niterations=niterations,
        populations=POPULATIONS,
        population_size=POPULATION_SIZE,
        ncycles_per_iteration=NCYCLES_PER_ITERATION,
        maxsize=MAXSIZE,
        parsimony=PARSIMONY,
        turbo=TURBO,
        procs=PROCS,
        model_selection="accuracy",
        batching=True,
        batch_size=200,
        unary_operators=["neg"],
        binary_operators=BINARY_OPERATORS + ["safe_pow(x, y) = sign(x) * abs(x)^y"],
        extra_sympy_mappings={"safe_pow": lambda x, y: sympy.sign(x) * sympy.Pow(sympy.Abs(x), y)},
        nested_constraints={"safe_pow": {"safe_pow": 0}},
        constraints={"safe_pow": (-1, 1)},
        complexity_of_operators={"+": 1, "-": 1, "*": 1, "/": 2, "safe_pow": 2, "neg": 1},
        tournament_selection_p=TOURNAMENT_SELECTION_P,
        tournament_selection_n=TOURNAMENT_SELECTION_N,
        probability_negate_constant=PROBABILITY_NEGATE_CONSTANT,
        fraction_replaced=FRACTION_REPLACED,
        crossover_probability=CROSSOVER_PROBABILITY,
        weight_mutate_operator=WEIGHT_MUTATE_OPERATOR,
        temp_equation_file=True,
        delete_tempfiles=True,
    )

    if USE_SIGMOID_LOSS:
        loss_function = get_julia_loss_function(epsilon, k)
        model_kwargs['elementwise_loss'] = loss_function

    model = PySRRegressor(**model_kwargs)
    model.fit(X, y, variable_names=param_names)
    return model


def _evaluate_hall_of_fame(model, X, y, epsilon):
    """
    Evalúa TODAS las ecuaciones del Hall of Fame de un modelo PySR.
    Retorna la mejor ecuación (la que matchea más puntos) como un dict con:
      - 'eq_idx': índice en el Hall of Fame
      - 'equation_str': texto de la ecuación
      - 'matched_indices': array de índices matcheados
      - 'num_matched': cantidad de puntos matcheados
      - 'model': referencia al modelo
    
    Retorna None si no matchea ningún punto.
    """
    best = None

    try:
        hof = model.equations_
    except Exception:
        # Fallback: usar predict directo
        y_pred = model.predict(X)
        matched = find_matched_points(X, y, y_pred, epsilon=epsilon)
        if len(matched) == 0:
            return None
        eq_series = model.get_best()
        eq_str = str(eq_series.get('equation', eq_series)) if hasattr(eq_series, 'get') else str(eq_series)
        return {
            'eq_idx': 0,
            'equation_str': eq_str,
            'matched_indices': matched,
            'num_matched': len(matched),
            'model': model,
        }

    for eq_idx in range(len(hof)):
        try:
            y_pred = model.predict(X, index=eq_idx)
            matched = find_matched_points(X, y, y_pred, epsilon=epsilon)

            if best is None or len(matched) > best['num_matched']:
                complexity = hof.iloc[eq_idx].get('complexity', '?')
                loss = hof.iloc[eq_idx].get('loss', '?')
                eq_text = str(hof.iloc[eq_idx].get('equation', '?'))

                best = {
                    'eq_idx': eq_idx,
                    'equation_str': eq_text,
                    'matched_indices': matched,
                    'num_matched': len(matched),
                    'model': model,
                    'complexity': complexity,
                    'loss': loss,
                }
                print(f"    ★ Ecuación #{eq_idx} matchea {len(matched)} pts "
                      f"(complejidad={complexity}, loss={loss}): {eq_text}")
        except Exception:
            continue

    return best


def _run_attempts(X, y, param_names, num_attempts, epsilon, k, niterations):
    """
    Ejecuta PySR num_attempts veces sobre los mismos datos.
    En cada intento evalúa todo el Hall of Fame.
    Retorna la mejor ecuación encontrada entre todos los intentos.

    Retorna None si ningún intento matchea puntos.
    Si algún intento matchea el 100% de los puntos, para inmediatamente.
    """
    best_overall = None
    total_points = len(y)

    for attempt in range(1, num_attempts + 1):
        if num_attempts > 1:
            print(f"\n    ── Intento {attempt}/{num_attempts} ──")

        model = train_symbolic_model(X, y, param_names, k=k, epsilon=epsilon, niterations=niterations)
        candidate = _evaluate_hall_of_fame(model, X, y, epsilon)

        if candidate is None:
            print(f"    Intento {attempt}: sin matcheo")
            continue

        if num_attempts > 1:
            print(f"    Intento {attempt}: mejor ecuación matchea {candidate['num_matched']}/{total_points} pts")

        if best_overall is None or candidate['num_matched'] > best_overall['num_matched']:
            best_overall = candidate
            if num_attempts > 1:
                print(f"    ★ Nuevo mejor global!")

        # Early stop: si cubrimos todos los puntos, no necesitamos más intentos
        if best_overall['num_matched'] >= total_points:
            if num_attempts > 1 and attempt < num_attempts:
                print(f"    ✓ ¡100% de cobertura! Saltando intentos restantes.")
            break

    return best_overall


def iterative_symbolic_regression(
    X, y,
    param_names,
    epsilon=EPSILON,
    k=K,
    niterations=NITERATIONS,
    min_points=MIN_POINTS,
    max_iterations=MAX_ITERATIONS
):
    """
    Algoritmo iterativo de regresión simbólica con múltiples intentos:

    Para cada iteración:
      1. Ejecuta PySR NUM_ATTEMPTS veces sobre los puntos restantes
      2. Evalúa todo el Hall of Fame de cada intento
      3. Elige la ecuación que matchea más puntos entre todos los intentos
      4. Si supera MIN_MATCH_FRACTION, acepta la ecuación y quita los puntos
      5. Repite con los puntos restantes

    Esto permite:
      - Ecuaciones simples: se encuentran en 1 iteración (100% en un solo paso)
      - Ecuaciones complejas/Piecewise: se descubren en varias iteraciones
      - Robustez: múltiples intentos compensan la estocasticidad de PySR

    Returns:
        List[Dict]: Lista de funciones encontradas, cada una con:
            - 'iteration', 'model', 'equation', 'equation_series',
            - 'matched_indices', 'X_matched', 'y_matched', 'num_matched'
    """
    results = []
    X_remaining = X.copy()
    y_remaining = y.copy()
    original_indices = np.arange(len(X))

    iteration = 0
    consecutive_no_match = 0

    print_iteration_header()

    while len(X_remaining) >= min_points:
        iteration += 1

        if max_iterations is not None and iteration > max_iterations:
            print(f"\n⚠️  Se alcanzó el máximo de iteraciones ({max_iterations})")
            break

        print_iteration_info(iteration, len(X_remaining))

        # ── Múltiples intentos para esta iteración ──
        best = _run_attempts(
            X_remaining, y_remaining, param_names,
            num_attempts=NUM_ATTEMPTS,
            epsilon=epsilon, k=k, niterations=niterations
        )

        # ── Verificar si se encontró algo útil ──
        if best is None or best['num_matched'] == 0:
            consecutive_no_match += 1
            print(f"⚠️  Ningún intento matcheó puntos en la iteración {iteration}")
            if consecutive_no_match >= MAX_CONSECUTIVE_NO_MATCH:
                print(f"⚠️  {MAX_CONSECUTIVE_NO_MATCH} iteraciones sin matcheo. Deteniendo.")
                break
            print(f"Reintentando... ({consecutive_no_match}/{MAX_CONSECUTIVE_NO_MATCH})")
            continue

        # ── Verificar fracción mínima ──
        match_fraction = best['num_matched'] / len(X_remaining)
        if match_fraction < MIN_MATCH_FRACTION:
            consecutive_no_match += 1
            print(f"⚠️  Mejor ecuación matchea solo {best['num_matched']}/{len(X_remaining)} "
                  f"({100*match_fraction:.1f}%) — bajo el umbral de {100*MIN_MATCH_FRACTION:.0f}%")
            if consecutive_no_match >= MAX_CONSECUTIVE_NO_MATCH:
                print(f"⚠️  {MAX_CONSECUTIVE_NO_MATCH} iteraciones bajo umbral. Deteniendo.")
                break
            print(f"Reintentando... ({consecutive_no_match}/{MAX_CONSECUTIVE_NO_MATCH})")
            continue

        # ── Aceptar resultado ──
        consecutive_no_match = 0
        matched_local = best['matched_indices']
        matched_original = original_indices[matched_local]

        result = {
            'iteration': iteration,
            'model': best['model'],
            'equation': best['equation_str'],
            'equation_series': None,
            'matched_indices': matched_original,
            'X_matched': X[matched_original],
            'y_matched': y[matched_original],
            'num_matched': len(matched_original)
        }
        results.append(result)

        print_iteration_result(best['equation_str'], len(matched_original))

        # ── Quitar puntos matcheados ──
        mask = np.ones(len(X_remaining), dtype=bool)
        mask[matched_local] = False
        X_remaining = X_remaining[mask]
        y_remaining = y_remaining[mask]
        original_indices = original_indices[mask]

    # Resumen final
    total_matched = sum(r['num_matched'] for r in results)
    print_final_summary(len(X_remaining), original_indices, len(results), total_matched, len(X))
    
    return results
