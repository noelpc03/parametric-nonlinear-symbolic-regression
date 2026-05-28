"""
Ejecutor de un caso de prueba individual.

Ejecuta el pipeline completo para un caso de prueba:
  1. Parsear ecuación
  2. Generar grid
  3. Resolver
    4. Preparar datos para SR (modo combinado o por ramas)
    5. Regresión simbólica iterativa
  6. Comparar con respuesta esperada

Diseñado para ser llamado desde el orquestador de benchmark.
"""

import os
import sys
import time
import traceback
import numpy as np
import json
from datetime import datetime

# Asegurar que src/ esté en el path
_src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Añadir subdirectorios al path
for subdir in ['1_equation_definition', '2_parameter_grid', '3_zero_finding',
               '4_data_preparation', '5_symbolic_regression', '6_expression_builder']:
    _p = os.path.join(_src_dir, subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from equation_parser import parse_equation, parse_system
from grid_generator import generate_grid
from solver import solve_for_all_parameter_tuples
from root_grouping import group_by_root_branch, combine_all_roots, combine_all_solutions
from regression_adapter import (
    run_for_all_branches,
    run_combined_symbolic_regression,
    run_anchored_symbolic_regression,
)


def run_single_case(test_case, sr_config=None):
    """
    Ejecuta el pipeline completo para un caso de prueba.
    
    Args:
        test_case: dict con la definición del caso (de test_cases.py)
        sr_config: dict con configuración de regresión simbólica (override).
                   Si es None, usa los defaults del config.py unificado.
    
    Returns:
        result: dict con toda la información del resultado:
            - name, category, difficulty: del caso
            - equation: string de la ecuación
            - expected_roots: raíces esperadas
            - discovered_roots: raíces descubiertas por PySR
            - num_branches_expected: ramas esperadas
            - num_branches_found: ramas encontradas
            - branch_results: detalle por rama
            - total_time_seconds: tiempo total
            - status: 'success', 'error', 'no_roots', 'no_sr_results'
            - error_message: mensaje de error (si aplica)
            - stages_timing: tiempos por etapa
    """
    result = {
        "name": test_case["name"],
        "category": test_case.get("category", "N/A"),
        "difficulty": test_case.get("difficulty", "N/A"),
        "equation": test_case.get("equation", ""),
        "expected_roots": test_case.get("expected_roots", []),
        "num_branches_expected": len(test_case["expected_roots"]),
        "discovered_roots": [],
        "num_branches_found": 0,
        "branch_results": [],
        "total_time_seconds": 0,
        "status": "error",
        "error_message": None,
        "stages_timing": {},
    }
    
    # Cargar config defaults de SR
    from config import (
        EPSILON, K, NITERATIONS, POPULATIONS, MIN_POINTS,
        MAX_ITERATIONS, MAX_CONSECUTIVE_NO_MATCH,
        NUM_ATTEMPTS, PARSIMONY, POPULATION_SIZE,
        NCYCLES_PER_ITERATION, MAXSIZE, TURBO, PROCS,
        SR_INPUT_MODE,
        SYSTEM_SOLVER_METHOD, NUM_INITIAL_GUESSES, GUESS_RANGES,
        DISTANCE_TOLERANCE, SOLVER_RESIDUE_TOL,
        ANCHOR_COORDINATE, VALIDATION_TOL, MAX_ANCHOR_ITERATIONS,
    )
    
    # Override con config personalizada si se provee
    if sr_config is None:
        sr_config = {}
    
    epsilon = sr_config.get("epsilon", EPSILON)
    k = sr_config.get("k", K)
    niterations = sr_config.get("niterations", NITERATIONS)
    min_points = sr_config.get("min_points", MIN_POINTS)
    input_mode = str(sr_config.get("sr_input_mode", SR_INPUT_MODE)).strip().lower()

    if input_mode not in ("combined", "branches"):
        raise ValueError(
            f"sr_input_mode inválido: {input_mode}. Usa 'combined' o 'branches'."
        )
    
    total_start = time.time()
    
    try:
        # ── Etapa 1: Parsear ecuación ──
        t0 = time.time()
        equations_input = test_case.get("equations")
        if equations_input:
            equations, symbols = parse_system(
                equations_input,
                test_case["variables"],
                test_case["parameters"],
            )
            result["equation"] = " ; ".join(equations_input)
            is_system = len(equations_input) > 1 or len(test_case["variables"]) > 1
        else:
            equation, symbols = parse_equation(
                test_case["equation"],
                test_case["variables"],
                test_case["parameters"],
            )
            equations = [equation]
            is_system = len(test_case["variables"]) > 1
        result["stages_timing"]["parse"] = time.time() - t0
        
        # ── Etapa 2: Generar grid ──
        t0 = time.time()
        grid, param_names = generate_grid(test_case["parameter_ranges"])
        result["stages_timing"]["grid"] = time.time() - t0
        result["num_grid_points"] = len(grid)
        
        # ── Etapa 3: Resolver ecuación ──
        t0 = time.time()
        var_symbols = [symbols[v] for v in test_case["variables"]]
        param_symbols = {p: symbols[p] for p in test_case["parameters"]}
        
        solver_results = solve_for_all_parameter_tuples(
            equations, var_symbols, param_names, param_symbols, grid,
            method=SYSTEM_SOLVER_METHOD,
            num_guesses=NUM_INITIAL_GUESSES,
            guess_ranges=GUESS_RANGES,
            dist_tol=DISTANCE_TOLERANCE,
            residue_tol=SOLVER_RESIDUE_TOL,
        )
        result["stages_timing"]["solve"] = time.time() - t0
        result["num_solved"] = len(solver_results)
        
        if len(solver_results) == 0:
            result["status"] = "no_roots"
            result["error_message"] = "No se encontraron raíces reales"
            result["total_time_seconds"] = time.time() - total_start
            return result
        
        # ── Etapa 4: Preparar datos para SR ──
        t0 = time.time()

        branches = None
        combined_data = None
        anchored_results = None

        if is_system:
            combined_data = combine_all_solutions(solver_results, param_names)
            result["num_combined_tuples"] = len(combined_data["Y"])
            # Se define mas adelante como el numero de ramas encontradas.
            result["num_branches_found"] = 0
        else:
            if input_mode == "combined":
                combined_data = combine_all_roots(solver_results, param_names)
                result["num_combined_tuples"] = len(combined_data["y"])
                # Se define mas adelante como el numero de ecuaciones descubiertas.
                result["num_branches_found"] = 0
            else:
                branches = group_by_root_branch(solver_results, param_names)
                result["num_branches_found"] = len(branches)

        result["stages_timing"]["grouping"] = time.time() - t0
        
        # ── Etapa 5: Regresión simbólica ──
        t0 = time.time()

        if is_system:
            anchored_results = run_anchored_symbolic_regression(
                combined_data,
                param_names,
                equations,
                var_symbols,
                anchor_coord=ANCHOR_COORDINATE,
                epsilon=epsilon,
                k=k,
                niterations=niterations,
                min_points=min_points,
                max_iterations=MAX_ANCHOR_ITERATIONS,
                validation_tol=VALIDATION_TOL,
            )
            combined_sr_results = None
            all_sr_results = None
        else:
            if input_mode == "combined":
                combined_sr_results = run_combined_symbolic_regression(
                    combined_data,
                    param_names,
                    epsilon=epsilon,
                    k=k,
                    niterations=niterations,
                    min_points=min_points,
                    max_iterations=MAX_ITERATIONS,
                )
                all_sr_results = None
            else:
                all_sr_results = run_for_all_branches(
                    branches, param_names,
                    epsilon=epsilon, k=k,
                    niterations=niterations, min_points=min_points
                )
                combined_sr_results = None

        result["stages_timing"]["symbolic_regression"] = time.time() - t0

        # ── Procesar resultados ──
        if is_system:
            total_points = len(combined_data["Y"]) if combined_data is not None else 0

            for branch_idx, branch in enumerate(anchored_results or []):
                expressions = branch.get("expressions", [])
                num_matched = int(branch.get("num_matched", 0))
                coverage = (num_matched / total_points) if total_points > 0 else 0.0

                functions_found = []
                for var, expr in zip(test_case["variables"], expressions):
                    functions_found.append({
                        "equation": f"{var}={expr}",
                        "num_matched": num_matched,
                    })

                result["branch_results"].append({
                    "branch_index": branch_idx,
                    "num_data_points": num_matched,
                    "functions_found": functions_found,
                    "total_points_matched": num_matched,
                    "coverage": coverage,
                })

                if expressions:
                    joined = "; ".join(
                        f"{var}={expr}" for var, expr in zip(test_case["variables"], expressions)
                    )
                    result["discovered_roots"].append(joined)

            result["num_branches_found"] = len(result["discovered_roots"])
        else:
            if input_mode == "combined":
                total_points = len(combined_data["y"]) if combined_data is not None else 0
                total_matched = 0
                functions_found = []

                for func in combined_sr_results:
                    eq = str(func["equation"])
                    num_matched = int(func["num_matched"])

                    functions_found.append({
                        "equation": eq,
                        "num_matched": num_matched,
                    })
                    total_matched += num_matched
                    result["discovered_roots"].append(eq)

                coverage = (total_matched / total_points) if total_points > 0 else 0.0
                result["branch_results"].append({
                    "branch_index": 0,
                    "num_data_points": total_points,
                    "functions_found": functions_found,
                    "total_points_matched": total_matched,
                    "coverage": coverage,
                })
                result["num_branches_found"] = len(result["discovered_roots"])
            else:
                for branch_idx, branch_results in enumerate(all_sr_results):
                    branch_info = {
                        "branch_index": branch_idx,
                        "num_data_points": len(branches[branch_idx]['y']),
                        "functions_found": [],
                        "total_points_matched": 0,
                    }

                    for func in branch_results:
                        func_info = {
                            "equation": str(func['equation']),
                            "num_matched": int(func['num_matched']),
                        }
                        branch_info["functions_found"].append(func_info)
                        branch_info["total_points_matched"] += func['num_matched']
                        result["discovered_roots"].append(str(func['equation']))

                    # Cobertura de esta rama
                    if branch_info["num_data_points"] > 0:
                        branch_info["coverage"] = branch_info["total_points_matched"] / branch_info["num_data_points"]
                    else:
                        branch_info["coverage"] = 0.0

                    result["branch_results"].append(branch_info)
        
        if len(result["discovered_roots"]) == 0:
            result["status"] = "no_sr_results"
            result["error_message"] = "SR no encontró expresiones"
        else:
            result["status"] = "success"
    
    except Exception as e:
        result["status"] = "error"
        result["error_message"] = f"{type(e).__name__}: {str(e)}"
        result["traceback"] = traceback.format_exc()
    
    result["total_time_seconds"] = time.time() - total_start
    return result
