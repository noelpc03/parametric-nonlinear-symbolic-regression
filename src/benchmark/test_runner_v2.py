"""
Test runner v2: Ejecuta casos múltiples veces con estadísticas consolidadas.

Características:
  - Carga casos desde JSON
  - Ejecuta cada caso N veces (configurable)
  - Consolida resultados (promedio, desv. est., min, max)
  - Genera reporte con tablas y estadísticas
  - Soporta ejecución por ID, nombre, o todos

Comandos disponibles:

    # Ejecutar todos los 35 casos 5 veces cada uno
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json

  # Ejecutar solo caso ID 1
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --id 1

  # Ejecutar solo caso ID 1, 3 veces cada uno
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --id 1 --runs 3

    # Ejecutar multiples IDs en una sola corrida
    python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --ids 14 20 25 --runs 3

  # Ejecutar caso por nombre específico
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --name system_linear_01

  # Ejecutar solo los primeros 5 casos
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --max-cases 5

  # Ejecutar todos 10 veces cada uno
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --runs 10

  # Solo listar casos sin ejecutar (dry-run)
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --dry-run

  # Ejecutar y guardar resultados en carpeta específica
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --output-dir my_results

  # Combinar opciones: casos 1-5, 7 ejecuciones cada uno, guardar resultados
  python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --id 1 --runs 7 --output-dir results_caso1
"""

import os
import sys
import json
import argparse
import time
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add src/ to path (go up one level from benchmark/)
_benchmark_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.dirname(_benchmark_dir)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Add subdirectories from src/
for subdir in ['1_equation_definition', '2_parameter_grid', '3_zero_finding', 
               '4_data_preparation', '5_symbolic_regression', '6_expression_builder']:
    _p = os.path.join(_src_dir, subdir)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Import from current package (benchmark)
try:
    from . import data_loader
    from .runner import run_single_case
    from .metrics import evaluate_case
except ImportError:
    # Fallback for direct script execution
    import data_loader
    from runner import run_single_case
    from metrics import evaluate_case


def run_test_case_multiple_times(case: Dict[str, Any], 
                                  num_runs: int = 5, 
                                  sr_config: Dict = None,
                                  progress_callback=None) -> Dict[str, Any]:
    """
    Execute a test case multiple times and consolidate results.
    
    Args:
        case: Test case from JSON
        num_runs: Number of times to run
        sr_config: SR configuration override
    
    Returns:
        Consolidated result dict with statistics
    """
    if sr_config is None:
        sr_config = {}
    
    # Convert case format for runner; keep equations list for system parsing.
    all_equations = case["equations"]
    runner_case = {
        "id": case["id"],
        "name": case["name"],
        "equation": " ; ".join(all_equations),
        "equations": all_equations,
        "variables": case["variables"],
        "parameters": case["parameters"],
        "parameter_ranges": {p: tuple(case["parameter_ranges"][p]) 
                            for p in case["parameters"]},
        "expected_roots": [f"{v}={sol.get(v, '?')}" 
                          for sol in case["expected_solutions"]
                          for v in case["variables"]],
    }
    
    results = []
    evaluations = []
    
    print(f"\n  Ejecutando {case['name']} {num_runs} veces...")
    
    for run_idx in range(num_runs):
        print(f"    Run {run_idx + 1}/{num_runs}...", end="", flush=True)
        
        try:
            result = run_single_case(runner_case, sr_config=sr_config)
            evaluation = {
                "success": result.get("status") == "success",
                "roots_matched": 0,
                "roots_expected": len(case["expected_solutions"]),
                "coverage": 0.0,
                "time": result.get("total_time_seconds", 0),
            }
            
            # Debug: print result status
            if result.get("status") != "success":
                print(f" [Status: {result.get('status')}, Error: {result.get('error_message')}]", end="")
            
            # Calculate coverage from branch results
            if result.get("branch_results"):
                total_coverage = 0
                num_branches = len(result["branch_results"])
                for branch in result["branch_results"]:
                    total_coverage += branch.get("coverage", 0)
                evaluation["coverage"] = total_coverage / num_branches if num_branches > 0 else 0
            
            # Count discovered roots
            if result.get("discovered_roots"):
                evaluation["roots_matched"] = len(result["discovered_roots"])
            
            results.append(result)
            evaluations.append(evaluation)
            print(" ✓")
            
        except Exception as e:
            print(f" ✗ Error: {e}")
            evaluations.append({
                "success": False,
                "roots_matched": 0,
                "roots_expected": len(case["expected_solutions"]),
                "coverage": 0.0,
                "time": 0,
                "error": str(e)
            })
    
        if progress_callback is not None:
            progress_callback(_build_consolidated(case, evaluations, num_runs))

    return _build_consolidated(case, evaluations, num_runs)


def _build_consolidated(case: Dict[str, Any], evaluations: List[Dict[str, Any]], num_runs: int) -> Dict[str, Any]:
    runs_completed = len(evaluations)
    successes = sum(1 for e in evaluations if e["success"])
    success_rate = successes / runs_completed if runs_completed > 0 else 0.0

    roots_matched = [e["roots_matched"] for e in evaluations]
    roots_expected = evaluations[0]["roots_expected"] if evaluations else 0
    coverage = [e["coverage"] for e in evaluations]
    times = [e["time"] for e in evaluations]

    roots_stats = {
        "mean": float(np.mean(roots_matched)) if roots_matched else 0.0,
        "std": float(np.std(roots_matched)) if roots_matched else 0.0,
        "min": int(np.min(roots_matched)) if roots_matched else 0,
        "max": int(np.max(roots_matched)) if roots_matched else 0,
    }
    coverage_stats = {
        "mean": float(np.mean(coverage)) if coverage else 0.0,
        "std": float(np.std(coverage)) if coverage else 0.0,
        "min": float(np.min(coverage)) if coverage else 0.0,
        "max": float(np.max(coverage)) if coverage else 0.0,
    }
    time_stats = {
        "mean": float(np.mean(times)) if times else 0.0,
        "std": float(np.std(times)) if times else 0.0,
        "min": float(np.min(times)) if times else 0.0,
        "max": float(np.max(times)) if times else 0.0,
    }

    return {
        "case_id": case["id"],
        "case_name": case["name"],
        "num_runs": num_runs,
        "num_runs_completed": runs_completed,
        "success_rate": success_rate,
        "statistics": {
            "roots_matched": roots_stats,
            "roots_expected": roots_expected,
            "coverage": coverage_stats,
            "time_seconds": time_stats,
        },
        "individual_runs": evaluations,
    }


def run_benchmark_suite(test_cases: List[Dict[str, Any]], 
                        num_runs: int = 5, 
                        sr_config: Dict = None,
                        dry_run: bool = False,
                        output_dir: str = None) -> Tuple[List[Dict], Dict]:
    """
    Run multiple test cases and generate consolidated report.
    
    Args:
        test_cases: List of test cases
        num_runs: Number of runs per test
        sr_config: SR configuration
        dry_run: Only list cases, don't execute
    
    Returns:
        (consolidated_results, global_statistics)
    """
    print("\n" + "="*70)
    print("  TEST RUNNER V2: BENCHMARK CON MÚLTIPLES EJECUCIONES")
    print("="*70)
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Casos: {len(test_cases)}")
    print(f"  Runs por caso: {num_runs}")
    
    if dry_run:
        print(f"\n  [DRY RUN] No se ejecutarán los casos.\n")
        print("  Casos a ejecutar:")
        for case in test_cases:
            print(f"    [{case['id']:2d}] {case['name']:30s}")
        return [], {}
    
    print(f"\n  Casos a ejecutar:")
    for case in test_cases:
        print(f"    [{case['id']:2d}] {case['name']:30s}")
    
    # Execute
    all_results = []
    total_start = time.time()

    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        initial_stats = _compute_global_stats([], 0.0, num_runs)
        _write_json_results(all_results, initial_stats, output_dir)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'#'*70}")
        print(f"  CASO {i}/{len(test_cases)}: [{case['id']}] {case['name']}")
        print(f"  Ecuaciones: {', '.join(case['equations'][:2])}{'...' if len(case['equations']) > 2 else ''}")
        print(f"  Variables: {', '.join(case['variables'])}")
        print(f"  Parámetros: {', '.join(case['parameters'])}")
        print(f"{'#'*70}")
        
        progress_callback = None
        if output_dir is not None:
            def progress_callback(partial_consolidated, results=all_results):
                partial_results = results + [partial_consolidated]
                partial_stats = _compute_global_stats(
                    partial_results,
                    time.time() - total_start,
                    num_runs,
                )
                _write_json_results(partial_results, partial_stats, output_dir)

        consolidated = run_test_case_multiple_times(
            case,
            num_runs=num_runs,
            sr_config=sr_config,
            progress_callback=progress_callback,
        )
        all_results.append(consolidated)

        if output_dir is not None:
            partial_stats = _compute_global_stats(
                all_results,
                time.time() - total_start,
                num_runs,
            )
            _write_json_results(all_results, partial_stats, output_dir)
    
    total_time = time.time() - total_start
    
    # Global statistics
    global_stats = _compute_global_stats(all_results, total_time, num_runs)
    
    return all_results, global_stats


def _compute_global_stats(all_results: List[Dict], total_time: float, num_runs: int) -> Dict:
    executed_cases = len(all_results)
    avg_time = (total_time / executed_cases) if executed_cases > 0 else 0
    avg_success = np.mean([r["success_rate"] for r in all_results]) if all_results else 0
    avg_coverage = np.mean([r["statistics"]["coverage"]["mean"] for r in all_results]) if all_results else 0

    return {
        "total_cases": executed_cases,
        "total_runs": executed_cases * num_runs,
        "total_time_seconds": total_time,
        "avg_time_per_case": avg_time,
        "avg_success_rate": avg_success,
        "avg_coverage": avg_coverage,
    }


def _write_json_results(all_results: List[Dict], global_stats: Dict, output_dir: str) -> None:
    consolidated_path = os.path.join(output_dir, "consolidated_results.json")
    stats_path = os.path.join(output_dir, "global_statistics.json")

    with open(consolidated_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())

    with open(stats_path, "w") as f:
        json.dump(global_stats, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())


def print_report(all_results: List[Dict], global_stats: Dict):
    """
    Print formatted report.
    """
    print("\n" + "="*70)
    print("  REPORTE CONSOLIDADO")
    print("="*70)
    
    print(f"\nResumen global:")
    print(f"  Total de casos: {global_stats['total_cases']}")
    print(f"  Total de ejecuciones: {global_stats['total_runs']}")
    print(f"  Tiempo total: {global_stats['total_time_seconds']:.1f}s")
    print(f"  Tasa de éxito promedio: {global_stats['avg_success_rate']*100:.1f}%")
    print(f"  Cobertura promedio: {global_stats['avg_coverage']*100:.1f}%")
    
    # Table header
    print(f"\n{'ID':>3} {'Nombre':30s} {'Éxito %':>8} {'Cob. Med':>8} {'Raíces':>8} {'Tiempo':>8}")
    print("-" * 70)
    
    # Sort by ID
    sorted_results = sorted(all_results, key=lambda x: x["case_id"])
    
    for result in sorted_results:
        success_pct = result["success_rate"] * 100
        coverage = result["statistics"]["coverage"]["mean"] * 100
        roots_matched = result["statistics"]["roots_matched"]["mean"]
        time_mean = result["statistics"]["time_seconds"]["mean"]
        
        print(f"{result['case_id']:3d} {result['case_name']:30s} "
              f"{success_pct:7.1f}% {coverage:7.1f}% {roots_matched:7.1f}s {time_mean:7.1f}s")
    
    # Rank: Best cases (by success rate then coverage)
    print(f"\n{'='*70}")
    print(f"  TOP 5 CASOS MEJORES")
    print(f"{'='*70}")
    
    sorted_by_perf = sorted(all_results, 
                           key=lambda x: (x["success_rate"], x["statistics"]["coverage"]["mean"]),
                           reverse=True)
    
    for i, result in enumerate(sorted_by_perf[:5], 1):
        success_pct = result["success_rate"] * 100
        coverage = result["statistics"]["coverage"]["mean"] * 100
        print(f"  {i}. [{result['case_id']}] {result['case_name']}: "
              f"{success_pct:.0f}% éxito, {coverage:.0f}% cobertura")
    
    # Rank: Worst cases
    print(f"\n{'='*70}")
    print(f"  TOP 5 CASOS CON MÁS DIFICULTAD")
    print(f"{'='*70}")
    
    sorted_by_diff = sorted(all_results, 
                           key=lambda x: (x["success_rate"], x["statistics"]["coverage"]["mean"]))
    
    for i, result in enumerate(sorted_by_diff[:5], 1):
        success_pct = result["success_rate"] * 100
        coverage = result["statistics"]["coverage"]["mean"] * 100
        print(f"  {i}. [{result['case_id']}] {result['case_name']}: "
              f"{success_pct:.0f}% éxito, {coverage:.0f}% cobertura")


def save_results(all_results: List[Dict], global_stats: Dict, output_dir: str = None):
    """
    Save results to JSON.
    """
    output_dir = _resolve_output_dir(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    
    _write_json_results(all_results, global_stats, output_dir)
    
    # Save text report
    with open(os.path.join(output_dir, "report.txt"), 'w', encoding='utf-8') as f:
        f.write(f"TEST RUNNER V2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Total de casos: {global_stats['total_cases']}\n")
        f.write(f"Total de ejecuciones: {global_stats['total_runs']}\n")
        f.write(f"Tiempo total: {global_stats['total_time_seconds']:.1f}s\n")
        f.write(f"Tasa de exito promedio: {global_stats['avg_success_rate']*100:.1f}%\n")
        f.write(f"Cobertura promedio: {global_stats['avg_coverage']*100:.1f}%\n\n")
        
        f.write(f"{'ID':>3} {'Nombre':30s} {'Exito %':>8} {'Cob. %':>8}\n")
        f.write("-" * 70 + "\n")
        
        for result in sorted(all_results, key=lambda x: x["case_id"]):
            success_pct = result["success_rate"] * 100
            coverage = result["statistics"]["coverage"]["mean"] * 100
            f.write(f"{result['case_id']:3d} {result['case_name']:30s} "
                   f"{success_pct:7.1f}% {coverage:7.1f}%\n")
    
    print(f"\n✓ Resultados guardados en: {output_dir}")
    return output_dir


def _resolve_output_dir(output_dir: str = None) -> str:
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(os.path.dirname(__file__), "results",
                            f"test_runner_v2_{timestamp}")
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Test runner v2 con múltiples ejecuciones por caso"
    )
    parser.add_argument("--cases", required=True, 
                       help="Ruta al JSON de casos (ej: src/benchmark/data/test_cases_sistemas.json)")
    parser.add_argument("--id", type=int, default=None,
                       help="Ejecutar solo caso con ID específico (1-35)")
    parser.add_argument("--ids", type=int, nargs="+", default=None,
                       help="Ejecutar multiples casos por ID (ej: --ids 14 20 25)")
    parser.add_argument("--name", type=str, default=None,
                       help="Ejecutar solo caso con nombre específico")
    parser.add_argument("--runs", type=int, default=5,
                       help="Número de ejecuciones por caso (default: 5)")
    parser.add_argument("--max-cases", type=int, default=None,
                       help="Máximo número de casos a ejecutar")
    parser.add_argument("--dry-run", action="store_true",
                       help="Solo listar casos, no ejecutar")
    parser.add_argument("--output-dir", type=str, default=None,
                       help="Directorio para guardar resultados")
    
    args = parser.parse_args()
    
    # Load test cases
    try:
        cases = data_loader.load_test_cases(args.cases)
    except Exception as e:
        print(f"Error al cargar casos: {e}")
        sys.exit(1)
    
    # Validate and filter
    print(f"Cargados {len(cases)} casos")
    
    # Filter by ID(s)
    selected_ids = []
    if args.id is not None:
        selected_ids.append(args.id)
    if args.ids:
        selected_ids.extend(args.ids)

    if selected_ids:
        seen = set()
        unique_ids = []
        for case_id in selected_ids:
            if case_id not in seen:
                seen.add(case_id)
                unique_ids.append(case_id)

        cases_by_id = {case["id"]: case for case in cases}
        missing = [case_id for case_id in unique_ids if case_id not in cases_by_id]
        if missing:
            missing_str = ", ".join(str(case_id) for case_id in missing)
            print(f"Error: Caso(s) con ID {missing_str} no encontrado(s)")
            sys.exit(1)

        cases = [cases_by_id[case_id] for case_id in unique_ids]
    
    # Filter by name
    if args.name is not None:
        case = data_loader.get_test_case_by_name(cases, args.name)
        if case:
            cases = [case]
        else:
            print(f"Error: Caso con nombre '{args.name}' no encontrado")
            sys.exit(1)
    
    # Limit number of cases
    if args.max_cases is not None:
        cases = cases[:args.max_cases]
    
    if not cases:
        print("Error: No hay casos que cumplan los filtros")
        sys.exit(1)
    
    output_dir = None
    if not args.dry_run:
        output_dir = _resolve_output_dir(args.output_dir)

    # Run benchmark
    all_results, global_stats = run_benchmark_suite(
        cases,
        num_runs=args.runs,
        dry_run=args.dry_run,
        output_dir=output_dir,
    )
    
    if args.dry_run:
        return
    
    # Print report
    print_report(all_results, global_stats)
    
    # Save results
    save_results(all_results, global_stats, output_dir)


if __name__ == "__main__":
    main()
