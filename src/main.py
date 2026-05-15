"""
Pipeline principal para descubrir expresiones analíticas de SISTEMAS DE ECUACIONES
mediante regresión simbólica con estrategia de anclaje.

Pipeline:
1. Parsear sistema de ecuaciones F(x; θ) = 0
2. Generar grid de parámetros
3. Resolver el sistema para cada tupla de parámetros (múltiples soluciones)
4. Combinar todas las soluciones vectoriales
5. Aplicar regresión simbólica con anclaje (descubre ramas)
6. Validar y reportar funciones encontradas
"""

import os
import sys
import json
from datetime import datetime
import numpy as np
import sympy as sp

# ── Añadir src/ al path para que config sea importable ──
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# ── Configuración unificada para sistemas de ecuaciones ──
from config import (
    OUTPUT_DIR, VERBOSE, SAVE_INTERMEDIATE, EXPERIMENT_NAME,
    EQUATIONS, VARIABLES, PARAMETERS,
    PARAMETER_RANGES,
    SYSTEM_SOLVER_METHOD, NUM_INITIAL_GUESSES, GUESS_RANGES,
    DISTANCE_TOLERANCE, SOLVER_RESIDUE_TOL,
    ANCHOR_COORDINATE, VALIDATION_TOL, MAX_ANCHOR_ITERATIONS,
    EPSILON, K, NITERATIONS, MIN_POINTS,
)

# ── Añadir subdirectorios al path para importar módulos ──
for subdir in ['1_equation_definition', '2_parameter_grid', '3_zero_finding',
               '4_data_preparation', '5_symbolic_regression']:
    _p = os.path.join(base_dir, subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Importar módulos del pipeline ──
from equation_parser import parse_system
from grid_generator import generate_grid
from solver import solve_for_all_parameter_tuples
from root_grouping import combine_all_solutions
from regression_adapter import run_anchored_symbolic_regression


def print_section(title, symbol="="):
    """Imprime una sección del pipeline con borde"""
    print(f"\n{symbol * 75}")
    print(f" {title}")
    print(f"{symbol * 75}")


def main():
    """Ejecuta el pipeline completo de descubrimiento de sistemas de ecuaciones."""
    
    print_section("🔬 PIPELINE DE REGRESIÓN SIMBÓLICA PARA SISTEMAS DE ECUACIONES", "═")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ════════════════════════════════════════════════════════════════════════════
    # PASO 1: Parsear el sistema de ecuaciones
    # ════════════════════════════════════════════════════════════════════════════
    print_section("PASO 1: Parsear Sistema de Ecuaciones", "─")
    
    print(f"📋 Sistema:")
    for i, eq in enumerate(EQUATIONS):
        print(f"   [{i+1}] {eq} = 0")
    
    print(f"\n📌 Variables (incógnitas): {VARIABLES}")
    print(f"🔧 Parámetros: {PARAMETERS}")
    
    try:
        equations_sympy, symbols_dict = parse_system(EQUATIONS, VARIABLES, PARAMETERS)
        var_symbols = [symbols_dict[v] for v in VARIABLES]
        param_symbols = {p: symbols_dict[p] for p in PARAMETERS}
        print(f"✓ Sistema parseado correctamente ({len(equations_sympy)} ecuaciones)")
    except Exception as e:
        print(f"✗ Error al parsear el sistema: {e}")
        return
    
    # ════════════════════════════════════════════════════════════════════════════
    # PASO 2: Generar grid de parámetros
    # ════════════════════════════════════════════════════════════════════════════
    print_section("PASO 2: Generar Grid de Parámetros", "─")
    
    print(f"📊 Rangos de parámetros:")
    for p, (min_val, max_val, n_points) in PARAMETER_RANGES.items():
        print(f"   {p}: [{min_val}, {max_val}] × {n_points} puntos")
    
    try:
        grid, grid_param_names = generate_grid(PARAMETER_RANGES)
        if grid_param_names != PARAMETERS:
            print(f"⚠ Orden de parámetros en grid ({grid_param_names}) difiere de PARAMETERS ({PARAMETERS})")
        print(f"✓ Grid generado: {len(grid)} tuplas (producto cartesiano)")
        if len(grid) <= 10:
            for i, t in enumerate(grid):
                print(f"   [{i+1}] {dict(zip(PARAMETERS, t))}")
    except Exception as e:
        print(f"✗ Error al generar grid: {e}")
        return
    
    # ════════════════════════════════════════════════════════════════════════════
    # PASO 3: Resolver el sistema para cada tupla de parámetros
    # ════════════════════════════════════════════════════════════════════════════
    print_section("PASO 3: Resolver Sistema para Cada Tupla de Parámetros", "─")
    
    print(f"🔧 Configuración del solver:")
    print(f"   Método: {SYSTEM_SOLVER_METHOD}")
    print(f"   Intentos por tupla: {NUM_INITIAL_GUESSES}")
    print(f"   Tolerancia de distancia: {DISTANCE_TOLERANCE}")
    print(f"   Tolerancia de residuo: {SOLVER_RESIDUE_TOL}")
    
    try:
        results = solve_for_all_parameter_tuples(
            equations_sympy, var_symbols, PARAMETERS, param_symbols, grid,
            method=SYSTEM_SOLVER_METHOD,
            num_guesses=NUM_INITIAL_GUESSES,
            guess_ranges=GUESS_RANGES,
            dist_tol=DISTANCE_TOLERANCE,
            residue_tol=SOLVER_RESIDUE_TOL
        )
        
        # Estadísticas
        total_solutions = sum(r['num_roots'] for r in results)
        avg_solutions = total_solutions / len(results) if len(results) > 0 else 0
        max_solutions = max((r['num_roots'] for r in results), default=0)
        
        print(f"✓ Resolución completada:")
        print(f"   Tuplas con soluciones: {len(results)}/{len(grid)}")
        print(f"   Total de soluciones: {total_solutions}")
        print(f"   Promedio por tupla: {avg_solutions:.2f}")
        print(f"   Máximo por tupla: {max_solutions}")
        
        # Mostrar primeras soluciones
        if len(results) > 0:
            print(f"\n📍 Ejemplo de primeras tuplas:")
            for i, res in enumerate(results[:3]):
                print(f"\n   Tupla {i+1}: {res['parameters']}")
                for j, root in enumerate(res['roots']):
                    print(f"      Solución {j+1}: {root}")
    
    except Exception as e:
        print(f"✗ Error durante resolución: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ════════════════════════════════════════════════════════════════════════════
    # PASO 4: Combinar todas las soluciones
    # ════════════════════════════════════════════════════════════════════════════
    print_section("PASO 4: Combinar Soluciones Vectoriales", "─")
    
    try:
        combined_data = combine_all_solutions(results, PARAMETERS)
        print(f"✓ Datos combinados:")
        print(f"   Dimensión X (parámetros): {combined_data['X'].shape}")
        print(f"   Dimensión Y (soluciones): {combined_data['Y'].shape}")
        print(f"   Variables: {combined_data['num_variables']}")
    
    except Exception as e:
        print(f"✗ Error al combinar soluciones: {e}")
        return
    
    # ════════════════════════════════════════════════════════════════════════════
    # PASO 5: Regresión simbólica con anclaje
    # ════════════════════════════════════════════════════════════════════════════
    print_section("PASO 5: Regresión Simbólica Multidimensional", "─")
    
    print(f"⚙️  Configuración:")
    print(f"   Variable ancla: {VARIABLES[ANCHOR_COORDINATE]} (índice {ANCHOR_COORDINATE})")
    print(f"   Máximo de iteraciones: {MAX_ANCHOR_ITERATIONS}")
    print(f"   Tolerancia de validación: {VALIDATION_TOL}")
    print(f"   EPSILON: {EPSILON}, K: {K}, NITERATIONS: {NITERATIONS}")
    
    try:
        sr_results = run_anchored_symbolic_regression(
            combined_data, PARAMETERS,
            equations=equations_sympy,
            variables=var_symbols,
            anchor_coord=ANCHOR_COORDINATE,
            epsilon=EPSILON,
            k=K,
            niterations=NITERATIONS,
            min_points=MIN_POINTS,
            max_iterations=MAX_ANCHOR_ITERATIONS,
            validation_tol=VALIDATION_TOL
        )
    
    except Exception as e:
        print(f"✗ Error durante regresión simbólica: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ════════════════════════════════════════════════════════════════════════════
    # PASO 6: Reporte final
    # ════════════════════════════════════════════════════════════════════════════
    print_section("PASO 6: Reporte Final de Resultados", "─")
    
    if len(sr_results) == 0:
        print("⚠️  No se encontraron ramas válidas.")
    else:
        print(f"✓ Se encontraron {len(sr_results)} ramas válidas:\n")
        
        for branch_idx, branch in enumerate(sr_results):
            print(f"{'─'*75}")
            print(f"RAMA {branch_idx + 1}")
            print(f"{'─'*75}")
            
            print(f"Expresiones encontradas (para {len(branch['expressions'])} variables):")
            for var_idx, var in enumerate(var_symbols):
                expr = branch['expressions'][var_idx]
                print(f"  {var} = {expr}")
            
            print(f"\nEstadísticas:")
            print(f"  Puntos matcheados: {branch['num_matched']}")
            print(f"  Iteración: {branch['iteration']}")
            print()
    
    # ════════════════════════════════════════════════════════════════════════════
    # Guardar resultados
    # ════════════════════════════════════════════════════════════════════════════
    print_section("Guardando Resultados", "─")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(OUTPUT_DIR, f"{timestamp}_system_results")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Guardar configuración
        config_data = {
            'equations': EQUATIONS,
            'variables': VARIABLES,
            'parameters': PARAMETERS,
            'parameter_ranges': {k: list(v) for k, v in PARAMETER_RANGES.items()},
            'solver_method': SYSTEM_SOLVER_METHOD,
            'anchor_coordinate': ANCHOR_COORDINATE,
            'timestamp': datetime.now().isoformat(),
            'num_branches_found': len(sr_results)
        }
        
        with open(os.path.join(output_dir, 'config.json'), 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Guardar resultados
        results_data = {
            'num_branches': len(sr_results),
            'branches': []
        }
        
        for i, branch in enumerate(sr_results):
            branch_info = {
                'branch_index': i + 1,
                'expressions': {
                    str(var): expr
                    for var, expr in zip(var_symbols, branch['expressions'])
                },
                'num_matched': branch['num_matched'],
                'iteration': branch['iteration']
            }
            results_data['branches'].append(branch_info)
        
        with open(os.path.join(output_dir, 'results.json'), 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"✓ Resultados guardados en: {output_dir}")
        print(f"  - config.json: Configuración del experimento")
        print(f"  - results.json: Ramas encontradas")
    
    except Exception as e:
        print(f"✗ Error al guardar resultados: {e}")
    
    print_section("✓ PIPELINE COMPLETADO", "═")
    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
