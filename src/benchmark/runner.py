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

from equation_parser import parse_equation
from grid_generator import generate_grid
from solver import solve_for_all_parameter_tuples
from root_grouping import group_by_root_branch, combine_all_roots
from regression_adapter import run_for_all_branches, run_combined_symbolic_regression


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
        "category": test_case["category"],
        "difficulty": test_case["difficulty"],
        "equation": test_case["equation"],
        "expected_roots": test_case["expected_roots"],
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
        equation, symbols = parse_equation(
            test_case["equation"],
            test_case["variables"],
            test_case["parameters"]
        )
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
            equation, var_symbols, param_names, param_symbols, grid,
            method='solve',
            filter_complex=True,
            complex_tol=1e-10,
            sort_roots=True
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

        if input_mode == "combined":
            combined_data = combine_all_roots(solver_results, param_names)
            result["num_combined_tuples"] = len(combined_data["y"])
            # Se define más adelante como el número de ecuaciones descubiertas.
            result["num_branches_found"] = 0
        else:
            branches = group_by_root_branch(solver_results, param_names)
            result["num_branches_found"] = len(branches)

        result["stages_timing"]["grouping"] = time.time() - t0
        
        # ── Etapa 5: Regresión simbólica ──
        t0 = time.time()

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
