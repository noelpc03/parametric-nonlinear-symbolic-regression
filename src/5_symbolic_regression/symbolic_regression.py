"""
Módulo de regresión simbólica iterativa adaptado para múltiples parámetros.

Arquitectura:
  - Proceso iterativo: encuentra funciones, quita puntos, repite
    - Dentro de cada iteración: una corrida de PySR
    - Evalúa todo el Hall of Fame de esa corrida
    - Selecciona la ecuación con más matches y continúa
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
    CUSTOM_UNARY_OPERATOR_DEFINITIONS, CUSTOM_BINARY_OPERATOR_DEFINITIONS,
    PARSIMONY, POPULATION_SIZE, NCYCLES_PER_ITERATION,
    MAXSIZE, TURBO, PROCS,
    MIN_MATCH_FRACTION, USE_SIGMOID_LOSS,
    USE_MATCH_COUNT_LOSS, MATCH_COUNT_EPSILON,
    VERBOSE,
    # TOURNAMENT_SELECTION_P, TOURNAMENT_SELECTION_N,
    # PROBABILITY_NEGATE_CONSTANT, FRACTION_REPLACED,
    # CROSSOVER_PROBABILITY, WEIGHT_MUTATE_OPERATOR,
)

from loss_functions import (
    get_julia_loss_function,
    get_julia_match_count_loss_function,
)
from utils import (
    find_matched_points, print_iteration_header, print_iteration_info,
    print_iteration_result, print_final_summary
)


def _operator_name(op_definition: str) -> str:
    """Extrae el nombre de un operador a partir de su definición Julia."""
    return op_definition.split("(", 1)[0].strip()


def train_symbolic_model(X, y, param_names, k=K, epsilon=EPSILON, niterations=NITERATIONS):
    """
    Entrena un modelo de regresión simbólica.
    """
    if USE_SIGMOID_LOSS and USE_MATCH_COUNT_LOSS:
        raise ValueError("Configuración inválida: USE_SIGMOID_LOSS y USE_MATCH_COUNT_LOSS no pueden ser True a la vez.")

    # Mappings de sympy para las raíces
    root_sympy_mappings = {
        "safe_sqrt": lambda x: sympy.sqrt(sympy.Abs(x)),
        "safe_cbrt": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 3)),
        "safe_root4": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 4)),
        "safe_root5": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 5)),
        "safe_root6": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 6)),
        "safe_root7": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 7)),
        "safe_root8": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 8)),
        "safe_root9": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 9)),
        "safe_root10": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 10)),
        "safe_pow": lambda x, y: sympy.sign(x) * sympy.Pow(sympy.Abs(x), y),
    }

    # Constraints para evitar anidamiento de raíces entre sí
    root_names = [_operator_name(op) for op in CUSTOM_UNARY_OPERATOR_DEFINITIONS]
    custom_binary_names = [_operator_name(op) for op in CUSTOM_BINARY_OPERATOR_DEFINITIONS]
    root_nested_constraints = {name: {n: 0 for n in root_names} for name in root_names}
    if "safe_pow" in custom_binary_names:
        root_nested_constraints["safe_pow"] = {"safe_pow": 0}

    complexity_of_operators = {
        "+": 1,
        "-": 1,
        "*": 1,
        "/": 2,
        "neg": 1,
    }
    for root_name in root_names:
        complexity_of_operators[root_name] = 2
    if "safe_pow" in custom_binary_names:
        complexity_of_operators["safe_pow"] = 4  # Penalizar para preferir raíces específicas

    constraints = {}
    if "safe_pow" in custom_binary_names:
        constraints["safe_pow"] = (9, 1)  # safe_pow: base compleja, exponente simple

    model_kwargs = dict(
        niterations=niterations,
        populations=POPULATIONS,
        population_size=POPULATION_SIZE,
        ncycles_per_iteration=NCYCLES_PER_ITERATION,
        maxsize=MAXSIZE,
        parsimony=PARSIMONY,
        turbo=TURBO,
        procs=PROCS,
        progress=bool(VERBOSE),
        verbosity=1 if VERBOSE else 0,
        model_selection="best",
        unary_operators=UNARY_OPERATORS + CUSTOM_UNARY_OPERATOR_DEFINITIONS,
        binary_operators=BINARY_OPERATORS + CUSTOM_BINARY_OPERATOR_DEFINITIONS,
        extra_sympy_mappings=root_sympy_mappings,
        nested_constraints=root_nested_constraints,
        constraints=constraints,
        complexity_of_operators=complexity_of_operators,
        # tournament_selection_p=TOURNAMENT_SELECTION_P,
        # tournament_selection_n=TOURNAMENT_SELECTION_N,
        # probability_negate_constant=PROBABILITY_NEGATE_CONSTANT,
        # fraction_replaced=FRACTION_REPLACED,
        # crossover_probability=CROSSOVER_PROBABILITY,
        # weight_mutate_operator=WEIGHT_MUTATE_OPERATOR,
        temp_equation_file=True,
        delete_tempfiles=True,
    )

    if USE_MATCH_COUNT_LOSS:
        model_kwargs['elementwise_loss'] = get_julia_match_count_loss_function(MATCH_COUNT_EPSILON)
    elif USE_SIGMOID_LOSS:
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
    match_mode = "absolute" if USE_MATCH_COUNT_LOSS else "relative"
    match_epsilon = MATCH_COUNT_EPSILON if USE_MATCH_COUNT_LOSS else epsilon

    try:
        hof = model.equations_
    except Exception:
        # Fallback: usar predict directo
        y_pred = model.predict(X)
        matched = find_matched_points(
            X, y, y_pred,
            epsilon=match_epsilon,
            mode=match_mode,
        )
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
            matched = find_matched_points(
                X, y, y_pred,
                epsilon=match_epsilon,
                mode=match_mode,
            )

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


def _run_single_search(X, y, param_names, epsilon, k, niterations):
    """
    Ejecuta una sola corrida de PySR sobre los datos actuales y evalúa
    todo su Hall of Fame.

    Retorna la mejor ecuación de la corrida o None si no hubo matches.
    """
    model = train_symbolic_model(X, y, param_names, k=k, epsilon=epsilon, niterations=niterations)
    candidate = _evaluate_hall_of_fame(model, X, y, epsilon)

    if candidate is None or candidate['num_matched'] == 0:
        return None

    return candidate


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
        Algoritmo iterativo de regresión simbólica (una corrida por iteración):

    Para cada iteración:
            1. Ejecuta una corrida de PySR sobre los puntos restantes
            2. Evalúa su Hall of Fame y selecciona la ecuación con más matches
            3. Si supera MIN_MATCH_FRACTION, acepta la ecuación y quita los puntos
            4. Repite con los puntos restantes

    Esto permite:
      - Ecuaciones simples: se encuentran en 1 iteración (100% en un solo paso)
      - Ecuaciones complejas/Piecewise: se descubren en varias iteraciones

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
    # Corte global: detener tras N iteraciones consecutivas con 0 matches.
    consecutive_zero_match = 0
    # Guardarraíl adicional: detener si repetidamente no alcanza MIN_MATCH_FRACTION.
    consecutive_below_threshold = 0

    print_iteration_header()

    while len(X_remaining) >= min_points:
        iteration += 1

        if max_iterations is not None and iteration > max_iterations:
            print(f"\n⚠️  Se alcanzó el máximo de iteraciones ({max_iterations})")
            break

        print_iteration_info(iteration, len(X_remaining))

        # ── Una sola corrida de PySR para esta iteración ──
        best = _run_single_search(
            X_remaining, y_remaining, param_names,
            epsilon=epsilon, k=k, niterations=niterations
        )

        # ── Verificar si se encontró algo útil ──
        if best is None or best['num_matched'] == 0:
            consecutive_zero_match += 1
            print(f"⚠️  Ninguna ecuación matcheó puntos en la iteración {iteration}")
            if consecutive_zero_match >= MAX_CONSECUTIVE_NO_MATCH:
                print(f"⚠️  {MAX_CONSECUTIVE_NO_MATCH} iteraciones sin matcheo. Deteniendo.")
                break
            print(f"Reintentando... (sin match: {consecutive_zero_match}/{MAX_CONSECUTIVE_NO_MATCH})")
            continue

        # Hubo al menos un match: reiniciar contador de sin-match.
        consecutive_zero_match = 0

        # ── Verificar fracción mínima ──
        match_fraction = best['num_matched'] / len(X_remaining)
        if match_fraction < MIN_MATCH_FRACTION:
            consecutive_below_threshold += 1
            print(f"⚠️  Mejor ecuación matchea solo {best['num_matched']}/{len(X_remaining)} "
                  f"({100*match_fraction:.1f}%) — bajo el umbral de {100*MIN_MATCH_FRACTION:.0f}%")
            if consecutive_below_threshold >= MAX_CONSECUTIVE_NO_MATCH:
                print(f"⚠️  {MAX_CONSECUTIVE_NO_MATCH} iteraciones bajo umbral. Deteniendo.")
                break
            print(f"Reintentando... (bajo umbral: {consecutive_below_threshold}/{MAX_CONSECUTIVE_NO_MATCH})")
            continue

        # ── Aceptar resultado ──
        consecutive_below_threshold = 0
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
