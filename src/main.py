"""
Pipeline principal para descubrir expresiones analíticas de ceros de ecuaciones
mediante regresión simbólica

Pipeline:
1. Definir ecuación f(x; params) = 0
2. Generar grid de parámetros
3. Resolver f = 0 para cada tupla de parámetros
4. Agrupar raíces por rama
5. Aplicar regresión simbólica a cada rama
6. Construir expresiones finales (Piecewise si es necesario)
"""

import os
import sys
import json
import importlib.util
from datetime import datetime
import numpy as np


def _load_config(config_path, module_name):
    """Carga un config.py desde una ruta específica con un nombre de módulo único."""
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base_dir = os.path.dirname(os.path.abspath(__file__))

# ── Configuración global ──
_global_cfg = _load_config(os.path.join(base_dir, 'config.py'), 'global_config')
OUTPUT_DIR = _global_cfg.OUTPUT_DIR
VERBOSE = _global_cfg.VERBOSE
SAVE_INTERMEDIATE = _global_cfg.SAVE_INTERMEDIATE
EXPERIMENT_NAME = _global_cfg.EXPERIMENT_NAME

# ── Configuración de ecuación ──
_eq_cfg = _load_config(os.path.join(base_dir, '1_equation_definition', 'config.py'), 'eq_config')
EQUATION_STRING = _eq_cfg.EQUATION_STRING
VARIABLES = _eq_cfg.VARIABLES
PARAMETERS = _eq_cfg.PARAMETERS

# ── Configuración de grid ──
_grid_cfg = _load_config(os.path.join(base_dir, '2_parameter_grid', 'config.py'), 'grid_config')
PARAMETER_RANGES = _grid_cfg.PARAMETER_RANGES
SAMPLING_METHOD = _grid_cfg.SAMPLING_METHOD
NUM_SAMPLES = _grid_cfg.NUM_SAMPLES
RANDOM_SEED = _grid_cfg.RANDOM_SEED

# ── Configuración del solver ──
_solver_cfg = _load_config(os.path.join(base_dir, '3_zero_finding', 'config.py'), 'solver_config')
SOLVER_METHOD = _solver_cfg.SOLVER_METHOD
FILTER_COMPLEX = _solver_cfg.FILTER_COMPLEX
COMPLEX_TOLERANCE = _solver_cfg.COMPLEX_TOLERANCE
SORT_ROOTS = _solver_cfg.SORT_ROOTS

# ── Configuración de regresión simbólica ──
_reg_cfg = _load_config(os.path.join(base_dir, '5_symbolic_regression', 'config.py'), 'regression_config')
EPSILON = _reg_cfg.EPSILON
K = _reg_cfg.K
NITERATIONS = _reg_cfg.NITERATIONS
MIN_POINTS = _reg_cfg.MIN_POINTS

# ── Añadir subdirectorios al path para importar módulos ──
for subdir in ['1_equation_definition', '2_parameter_grid', '3_zero_finding',
               '4_data_preparation', '5_symbolic_regression', '6_expression_builder']:
    _p = os.path.join(base_dir, subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Importar módulos del pipeline ──
from equation_parser import parse_equation
from grid_generator import generate_grid
from solver import solve_for_all_parameter_tuples
from root_grouping import group_by_root_branch
from regression_adapter import run_for_all_branches
from piecewise_builder import (
    build_piecewise_expression,
    find_region_boundaries,
    simplify_to_single_expression
)


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
        'sampling_method': SAMPLING_METHOD,
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
                
                # Intentar simplificar
                simplified = simplify_to_single_expression(branch_results)
                f.write(f"\n  Expresión simplificada (más puntos):\n")
                f.write(f"    {VARIABLES[0]} = {simplified}\n")
    
    print(f"\nResultados guardados en: {output_dir}")


def main():
    """Ejecuta el pipeline completo"""
    
    print("\n" + "="*70)
    print(" DESCUBRIMIENTO DE EXPRESIONES ANALÍTICAS")
    print(" Pipeline de Regresión Simbólica para Ceros de Ecuaciones")
    print("="*70)
    
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
    
    grid, param_names = generate_grid(
        PARAMETER_RANGES, 
        method=SAMPLING_METHOD,
        num_samples=NUM_SAMPLES,
        random_seed=RANDOM_SEED
    )
    
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
    # PASO 4: Agrupar raíces por rama
    # ============================================================
    print_section("PASO 4: Agrupación de raíces")
    
    branches = group_by_root_branch(results, param_names)
    
    print(f"Ramas identificadas: {len(branches)}")
    for i, branch in enumerate(branches):
        print(f"  Rama {i+1}: {len(branch['y'])} puntos")
    
    # ============================================================
    # PASO 5: Regresión simbólica por rama
    # ============================================================
    print_section("PASO 5: Regresión simbólica")
    
    all_results = run_for_all_branches(
        branches, param_names,
        epsilon=EPSILON, k=K, 
        niterations=NITERATIONS, min_points=MIN_POINTS
    )
    
    # ============================================================
    # PASO 6: Construir expresiones finales
    # ============================================================
    print_section("PASO 6: Expresiones finales")
    
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
            
            # Analizar regiones
            boundaries = find_region_boundaries(
                [f['X_matched'] for f in branch_results],
                param_names
            )
            print(f"  Regiones detectadas: {len(boundaries)}")
    
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
