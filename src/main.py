"""
Pipeline principal para descubrir expresiones analíticas de ceros de ecuaciones
mediante regresión simbólica

Pipeline:
1. Definir ecuación f(x; params) = 0
2. Generar grid de parámetros
3. Resolver f = 0 para cada tupla de parámetros
4. Agrupar raíces por rama
5. Aplicar regresión simbólica a cada rama
6. Reportar funciones encontradas por rama
"""

import os
import sys
import json
from datetime import datetime
import numpy as np

# ── Añadir src/ al path para que config sea importable ──
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# ── Configuración unificada ──
from config import (
    OUTPUT_DIR, VERBOSE, SAVE_INTERMEDIATE, EXPERIMENT_NAME,
    EQUATION_STRING, VARIABLES, PARAMETERS,
    PARAMETER_RANGES,
    SOLVER_METHOD, FILTER_COMPLEX, COMPLEX_TOLERANCE, SORT_ROOTS,
    EPSILON, K, NITERATIONS, MIN_POINTS,
    MAX_ITERATIONS, SR_INPUT_MODE,
)

# ── Añadir subdirectorios al path para importar módulos ──
for subdir in ['1_equation_definition', '2_parameter_grid', '3_zero_finding',
               '4_data_preparation', '5_symbolic_regression']:
    _p = os.path.join(base_dir, subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Importar módulos del pipeline ──
from equation_parser import parse_equation
from grid_generator import generate_grid
from solver import solve_for_all_parameter_tuples
from root_grouping import group_by_root_branch, combine_all_roots
from regression_adapter import run_for_all_branches, run_combined_symbolic_regression


def print_section(title):
    """Imprime una sección del pipeline"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def save_results(output_dir, equation_info, branches, all_results, param_names):
    """Guarda todos los resultados del pipeline"""
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar configuración
    config_data = {
        'equation': str(equation_info['equation']),
        'equation_latex': equation_info['latex'],
        'variables': VARIABLES,
        'parameters': PARAMETERS,
        'parameter_ranges': {k: list(v) for k, v in PARAMETER_RANGES.items()},
        'sampling_method': 'grid',
        'solver_method': SOLVER_METHOD,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(os.path.join(output_dir, 'config.json'), 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Guardar resultados por rama
    summary = []
    
    for branch_idx, branch_results in enumerate(all_results):
        branch_info = {
            'branch_index': branch_idx + 1,
            'num_data_points': len(branches[branch_idx]['y']),
            'num_functions_found': len(branch_results),
            'functions': []
        }
        
        for func_idx, func in enumerate(branch_results):
            func_info = {
                'function_index': func_idx + 1,
                'equation': str(func['equation']),
                'points_matched': int(func['num_matched']),
                'matched_indices': func['matched_indices'].tolist() if hasattr(func['matched_indices'], 'tolist') else list(func['matched_indices'])
            }
            branch_info['functions'].append(func_info)
        
        summary.append(branch_info)
    
    # Guardar resumen
    with open(os.path.join(output_dir, 'results_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Guardar expresiones finales en texto legible
    with open(os.path.join(output_dir, 'final_expressions.txt'), 'w') as f:
        f.write("EXPRESIONES ANALÍTICAS DESCUBIERTAS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Ecuación original: {equation_info['equation']} = 0\n")
        f.write(f"Variables: {VARIABLES}\n")
        f.write(f"Parámetros: {PARAMETERS}\n\n")
        
        for branch_idx, branch_results in enumerate(all_results):
            f.write(f"\nRAMA {branch_idx + 1} (raíz #{branch_idx + 1}):\n")
            f.write("-"*70 + "\n")
            
            if len(branch_results) == 1:
                f.write(f"Expresión única:\n")
                f.write(f"  {VARIABLES[0]} = {branch_results[0]['equation']}\n")
                f.write(f"  Puntos cubiertos: {branch_results[0]['num_matched']}\n")
            else:
                f.write(f"Múltiples funciones encontradas ({len(branch_results)}):\n")
                for func_idx, func in enumerate(branch_results):
                    f.write(f"\n  Función {func_idx + 1}:\n")
                    f.write(f"    {VARIABLES[0]} = {func['equation']}\n")
                    f.write(f"    Puntos cubiertos: {func['num_matched']}\n")
    
    print(f"\nResultados guardados en: {output_dir}")


def main():
    """Ejecuta el pipeline completo"""
    
    print("\n" + "="*70)
    print(" DESCUBRIMIENTO DE EXPRESIONES ANALÍTICAS")
    print(" Pipeline de Regresión Simbólica para Ceros de Ecuaciones")
    print("="*70)

    input_mode = str(SR_INPUT_MODE).strip().lower()
    if input_mode not in ("combined", "branches"):
        raise ValueError(
            f"SR_INPUT_MODE inválido: {SR_INPUT_MODE}. Usa 'combined' o 'branches'."
        )

    print(f"Modo de entrada SR: {input_mode}")
    
    # ============================================================
    # PASO 1: Definir ecuación
    # ============================================================
    print_section("PASO 1: Definición de ecuación")
    
    equation, symbols = parse_equation(EQUATION_STRING, VARIABLES, PARAMETERS)
    
    print(f"Ecuación: {equation} = 0")
    print(f"Variables (incógnitas): {VARIABLES}")
    print(f"Parámetros: {PARAMETERS}")
    
    # ============================================================
    # PASO 2: Generar grid de parámetros
    # ============================================================
    print_section("PASO 2: Generación de grid de parámetros")
    
    grid, param_names = generate_grid(PARAMETER_RANGES)
    
    print(f"Grid generado: {grid.shape[0]} tuplas de parámetros")
    print(f"Dimensiones: {grid.shape[1]} parámetros")
    
    # ============================================================
    # PASO 3: Resolver ecuación para cada tupla
    # ============================================================
    print_section("PASO 3: Resolución de ecuación")
    
    var_symbols = [symbols[v] for v in VARIABLES]
    param_symbols = {p: symbols[p] for p in PARAMETERS}
    
    results = solve_for_all_parameter_tuples(
        equation, var_symbols, param_names, param_symbols, grid,
        method=SOLVER_METHOD, 
        filter_complex=FILTER_COMPLEX,
        complex_tol=COMPLEX_TOLERANCE, 
        sort_roots=SORT_ROOTS
    )
    
    print(f"Tuplas con raíces válidas: {len(results)}")
    if len(results) > 0:
        num_roots_dist = {}
        for r in results:
            n = r['num_roots']
            num_roots_dist[n] = num_roots_dist.get(n, 0) + 1
        print(f"Distribución de número de raíces: {num_roots_dist}")
    
    # ============================================================
    # PASO 4: Preparar datos para regresión simbólica
    # ============================================================
    print_section("PASO 4: Preparación de datos para SR")

    if input_mode == "combined":
        combined_data = combine_all_roots(results, param_names)
        branches = [{"X": combined_data["X"], "y": combined_data["y"]}]
        print(f"Tuplas combinadas para SR: {len(combined_data['y'])}")
    else:
        combined_data = None
        branches = group_by_root_branch(results, param_names)
        print(f"Ramas identificadas: {len(branches)}")
        for i, branch in enumerate(branches):
            print(f"  Rama {i+1}: {len(branch['y'])} puntos")
    
    # ============================================================
    # PASO 5: Regresión simbólica por rama
    # ============================================================
    print_section("PASO 5: Regresión simbólica")

    if input_mode == "combined":
        combined_results = run_combined_symbolic_regression(
            combined_data,
            param_names,
            epsilon=EPSILON,
            k=K,
            niterations=NITERATIONS,
            min_points=MIN_POINTS,
            max_iterations=MAX_ITERATIONS,
        )
        all_results = [combined_results]
    else:
        all_results = run_for_all_branches(
            branches, param_names,
            epsilon=EPSILON, k=K,
            niterations=NITERATIONS, min_points=MIN_POINTS
        )
    
    # ============================================================
    # PASO 6: Reportar funciones encontradas
    # ============================================================
    print_section("PASO 6: Funciones encontradas")
    
    for branch_idx, branch_results in enumerate(all_results):
        print(f"\nRama {branch_idx + 1}:")
        
        if len(branch_results) == 0:
            print("  No se encontraron funciones")
        elif len(branch_results) == 1:
            print(f"  Expresión única: {branch_results[0]['equation']}")
            print(f"  Puntos matcheados: {branch_results[0]['num_matched']}")
        else:
            print(f"  Múltiples funciones ({len(branch_results)}):")
            for i, func in enumerate(branch_results):
                print(f"    {i+1}. {func['equation']} ({func['num_matched']} puntos)")
    
    # ============================================================
    # Guardar resultados
    # ============================================================
    print_section("Guardando resultados")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(OUTPUT_DIR, f"{EXPERIMENT_NAME}_{timestamp}")
    
    equation_info = {
        'equation': equation,
        'latex': symbols  # Ajustar según necesidad
    }
    
    save_results(output_dir, {'equation': equation, 'latex': str(equation)}, 
                branches, all_results, param_names)
    
    print_section("PIPELINE COMPLETADO")
    print(f"Resultados en: {output_dir}")


if __name__ == "__main__":
    main()
