"""
Orquestador principal del benchmark.

Ejecuta todos los casos de prueba (o un subconjunto filtrado),
recopila resultados, calcula métricas y genera reporte.

Uso:
    python run_benchmark.py                    # Todos los casos
    python run_benchmark.py --category linear  # Solo lineales
    python run_benchmark.py --difficulty easy   # Solo fáciles
    python run_benchmark.py --case linear_01   # Un caso específico
    python run_benchmark.py --max 5            # Solo los primeros 5
    python run_benchmark.py --dry-run          # Solo listar, no ejecutar
Ejecución por batches (para evitar llenado de RAM):
    python run_benchmark.py --from-index 0 --to-index 10   # Casos 1-10
    python run_benchmark.py --from-index 10 --to-index 20  # Casos 11-20
    ...

Combinar resultados de batches:
    python run_benchmark.py --merge benchmark_results/batch_*"""

import os
import sys
import json
import glob
import argparse
import time
from datetime import datetime

# Asegurar paths
_benchmark_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_benchmark_dir, '..')
if _benchmark_dir not in sys.path:
    sys.path.insert(0, _benchmark_dir)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from test_cases import TEST_CASES, get_test_cases, print_catalog_summary
from runner import run_single_case
from metrics import evaluate_case, compute_global_metrics, print_metrics_report


def run_benchmark(cases=None, category=None, difficulty=None, 
                  case_name=None, max_cases=None, sr_config=None,
                  output_dir=None, dry_run=False,
                  from_index=None, to_index=None):
    """
    Ejecuta el benchmark completo.
    
    Args:
        cases: lista de casos (si None, usa TEST_CASES con filtros)
        category: filtrar por categoría
        difficulty: filtrar por dificultad
        case_name: ejecutar solo un caso por nombre (parcial)
        max_cases: máximo de casos a ejecutar
        sr_config: override de config de SR
        output_dir: directorio para guardar resultados
        dry_run: solo listar, no ejecutar
        from_index: índice inicial (inclusive, 0-based)
        to_index: índice final (exclusive, 0-based)
    
    Returns:
        (evaluations, metrics) si no es dry_run
    """
    # Seleccionar casos
    if cases is None:
        cases = get_test_cases(category=category, difficulty=difficulty, 
                               max_cases=max_cases)
    
    # Filtrar por nombre
    if case_name is not None:
        cases = [c for c in cases if case_name.lower() in c["name"].lower()]
    
    if max_cases is not None:
        cases = cases[:max_cases]
    
    # Filtrar por rango de índices (para ejecución por batches)
    if from_index is not None or to_index is not None:
        fi = from_index if from_index is not None else 0
        ti = to_index if to_index is not None else len(cases)
        cases = cases[fi:ti]
    
    print("\n" + "=" * 70)
    print("  BENCHMARK DEL PIPELINE DE DESCUBRIMIENTO DE RAÍCES")
    print("=" * 70)
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Casos seleccionados: {len(cases)}")
    
    if len(cases) == 0:
        print("  ⚠ No hay casos que coincidan con los filtros")
        return [], {}
    
    print(f"\n  Casos a ejecutar:")
    for i, tc in enumerate(cases):
        roots_str = ", ".join(tc["expected_roots"])
        print(f"    {i+1:2d}. [{tc['difficulty']:6s}] {tc['name']:35s} "
              f"({tc['equation']} = 0) → [{roots_str}]")
    
    if dry_run:
        print("\n  [DRY RUN] No se ejecutarán los casos.")
        return [], {}
    
    # ── Ejecutar casos ──
    all_results = []
    evaluations = []
    
    total_start = time.time()
    
    for i, tc in enumerate(cases):
        print(f"\n\n{'#' * 70}")
        print(f"  CASO {i+1}/{len(cases)}: {tc['name']}")
        print(f"  Ecuación: {tc['equation']} = 0")
        print(f"  Parámetros: {tc['parameters']}")
        print(f"  Raíces esperadas: {tc['expected_roots']}")
        print(f"{'#' * 70}")
        
        case_result = run_single_case(tc, sr_config=sr_config)
        all_results.append(case_result)
        
        evaluation = evaluate_case(case_result, tc)
        evaluations.append(evaluation)
        
        # Resumen rápido del caso
        status_icon = "✓" if evaluation["root_match_rate"] == 1.0 else "✗"
        print(f"\n  {status_icon} Resultado: {evaluation['roots_matched']}/{evaluation['roots_expected']} raíces, "
              f"cobertura {evaluation['average_coverage']*100:.0f}%, "
              f"tiempo {evaluation['time_seconds']:.1f}s")
        
        if case_result.get("discovered_roots"):
            for j, root in enumerate(case_result["discovered_roots"]):
                print(f"    Rama {j+1}: {root}")
    
    total_time = time.time() - total_start
    
    # ── Calcular métricas ──
    metrics = compute_global_metrics(evaluations)
    
    # ── Imprimir reporte ──
    print_metrics_report(metrics, evaluations)
    
    # ── Guardar resultados ──
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(_src_dir, "benchmark_results", f"benchmark_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar resultados crudos
    serializable_results = []
    for r in all_results:
        sr = {k: v for k, v in r.items() if k != "traceback"}
        serializable_results.append(sr)
    
    with open(os.path.join(output_dir, "raw_results.json"), 'w') as f:
        json.dump(serializable_results, f, indent=2, default=str)
    
    # Guardar evaluaciones
    with open(os.path.join(output_dir, "evaluations.json"), 'w') as f:
        json.dump(evaluations, f, indent=2, default=str)
    
    # Guardar métricas
    with open(os.path.join(output_dir, "metrics.json"), 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    # Guardar reporte de texto
    with open(os.path.join(output_dir, "report.txt"), 'w') as f:
        f.write(f"BENCHMARK DEL PIPELINE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Casos ejecutados: {len(cases)}\n")
        f.write(f"Tiempo total: {total_time:.1f}s\n\n")
        f.write(f"Tasa de éxito (pipeline): {metrics['success_rate']*100:.1f}%\n")
        f.write(f"Raíces descubiertas:      {metrics['root_discovery_rate']*100:.1f}%\n")
        f.write(f"Casos perfectos:          {metrics['perfect_cases']}/{metrics['total_cases']} ({metrics['perfect_rate']*100:.1f}%)\n")
        f.write(f"Cobertura promedio:       {metrics['average_coverage']*100:.1f}%\n\n")
        
        f.write(f"{'='*70}\n")
        f.write(f"DETALLE POR CASO\n")
        f.write(f"{'='*70}\n\n")
        
        for e in evaluations:
            status = "✓ PERFECTO" if e["root_match_rate"] == 1.0 else (
                f"~ PARCIAL ({e['roots_matched']}/{e['roots_expected']})" if e["roots_matched"] > 0 else
                "✗ FALLIDO"
            )
            f.write(f"{e['name']} [{e['category']}/{e['difficulty']}]: {status} ({e['time_seconds']:.1f}s)\n")
            for md in e.get("match_details", []):
                icon = "✓" if md["matched"] else "✗"
                f.write(f"  {icon} esperada: {md['expected']}\n")
                if md["matched"]:
                    f.write(f"    descubierta: {md['discovered']}\n")
                else:
                    closest = md.get("closest_discovered")
                    if closest:
                        frac = md.get("closest_fraction", 0)
                        err = md.get("closest_error", float('inf'))
                        f.write(f"    descubierta: (no matcheó)\n")
                        f.write(f"    más cercana: {closest}  [coincidencia={frac*100:.1f}%, error={err:.4f}]\n")
                    else:
                        f.write(f"    descubierta: (rama no encontrada por el pipeline)\n")
            # Mostrar raíces descubiertas que no matchearon con ninguna esperada
            unmatched = e.get("unmatched_discovered", [])
            if unmatched:
                f.write(f"  ⚠ Raíces descubiertas sin match con esperadas:\n")
                for ur in unmatched:
                    f.write(f"    → {ur}\n")
            f.write("\n")
    
    print(f"\n  Resultados guardados en: {output_dir}")
    
    return evaluations, metrics


def merge_batch_results(batch_dirs, output_dir=None):
    """
    Combina resultados de múltiples ejecuciones por batch en un reporte unificado.
    
    Args:
        batch_dirs: lista de directorios con resultados de batches
        output_dir: directorio de salida para resultados combinados
    """
    all_evaluations = []
    all_raw_results = []
    total_time = 0
    
    for bd in sorted(batch_dirs):
        eval_path = os.path.join(bd, "evaluations.json")
        raw_path = os.path.join(bd, "raw_results.json")
        
        if not os.path.exists(eval_path):
            print(f"  ⚠ No se encontró {eval_path}, saltando...")
            continue
        
        with open(eval_path, 'r') as f:
            evals = json.load(f)
        all_evaluations.extend(evals)
        
        if os.path.exists(raw_path):
            with open(raw_path, 'r') as f:
                raws = json.load(f)
            all_raw_results.extend(raws)
        
        # Sumar tiempos
        metrics_path = os.path.join(bd, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                m = json.load(f)
            total_time += m.get("total_time_seconds", 0)
        
        print(f"  ✓ {bd}: {len(evals)} casos cargados")
    
    if len(all_evaluations) == 0:
        print("  ✗ No se encontraron resultados para combinar")
        return
    
    # Recalcular métricas globales
    metrics = compute_global_metrics(all_evaluations)
    metrics["total_time_seconds"] = total_time
    
    # Imprimir reporte
    print(f"\n{'='*70}")
    print(f"  RESULTADOS COMBINADOS DE {len(batch_dirs)} BATCHES")
    print(f"{'='*70}")
    print_metrics_report(metrics, all_evaluations)
    
    # Guardar
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(_src_dir, "benchmark_results", f"merged_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "evaluations.json"), 'w') as f:
        json.dump(all_evaluations, f, indent=2, default=str)
    
    with open(os.path.join(output_dir, "raw_results.json"), 'w') as f:
        json.dump(all_raw_results, f, indent=2, default=str)
    
    with open(os.path.join(output_dir, "metrics.json"), 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    # Reporte de texto
    with open(os.path.join(output_dir, "report.txt"), 'w') as f:
        f.write(f"BENCHMARK COMBINADO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Batches combinados: {len(batch_dirs)}\n")
        f.write(f"Casos totales: {len(all_evaluations)}\n")
        f.write(f"Tiempo total: {total_time:.1f}s\n\n")
        f.write(f"Tasa de éxito (pipeline): {metrics['success_rate']*100:.1f}%\n")
        f.write(f"Raíces descubiertas:      {metrics['root_discovery_rate']*100:.1f}%\n")
        f.write(f"Casos perfectos:          {metrics['perfect_cases']}/{metrics['total_cases']} ({metrics['perfect_rate']*100:.1f}%)\n")
        f.write(f"Cobertura promedio:       {metrics['average_coverage']*100:.1f}%\n\n")
        
        f.write(f"{'='*70}\n")
        f.write(f"DETALLE POR CASO\n")
        f.write(f"{'='*70}\n\n")
        
        for e in all_evaluations:
            status = "✓ PERFECTO" if e["root_match_rate"] == 1.0 else (
                f"~ PARCIAL ({e['roots_matched']}/{e['roots_expected']})" if e["roots_matched"] > 0 else
                "✗ FALLIDO"
            )
            f.write(f"{e['name']} [{e['category']}/{e['difficulty']}]: {status} ({e['time_seconds']:.1f}s)\n")
            for md in e.get("match_details", []):
                icon = "✓" if md["matched"] else "✗"
                f.write(f"  {icon} esperada: {md['expected']}\n")
                if md["matched"]:
                    f.write(f"    descubierta: {md['discovered']}\n")
                else:
                    closest = md.get("closest_discovered")
                    if closest:
                        frac = md.get("closest_fraction", 0)
                        err = md.get("closest_error", float('inf'))
                        f.write(f"    descubierta: (no matcheó)\n")
                        f.write(f"    más cercana: {closest}  [coincidencia={frac*100:.1f}%, error={err:.4f}]\n")
                    else:
                        f.write(f"    descubierta: (rama no encontrada por el pipeline)\n")
            unmatched = e.get("unmatched_discovered", [])
            if unmatched:
                f.write(f"  ⚠ Raíces descubiertas sin match con esperadas:\n")
                for ur in unmatched:
                    f.write(f"    → {ur}\n")
            f.write("\n")
    
    print(f"\n  Resultados combinados guardados en: {output_dir}")
    return all_evaluations, metrics


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark del pipeline de descubrimiento de raíces"
    )
    parser.add_argument("--category", "-c", 
                        choices=["linear", "quadratic", "cubic", "quartic", "quintic", "special"],
                        help="Filtrar por categoría")
    parser.add_argument("--difficulty", "-d",
                        choices=["easy", "medium", "hard"],
                        help="Filtrar por dificultad")
    parser.add_argument("--case", "-n",
                        help="Ejecutar solo casos cuyo nombre contenga este texto")
    parser.add_argument("--max", "-m", type=int,
                        help="Máximo número de casos a ejecutar")
    parser.add_argument("--from-index", type=int, default=None,
                        help="Índice inicial de casos (0-based, inclusive)")
    parser.add_argument("--to-index", type=int, default=None,
                        help="Índice final de casos (0-based, exclusive)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo listar casos, no ejecutar")
    parser.add_argument("--niterations", type=int, default=None,
                        help="Override NITERATIONS de PySR")
    parser.add_argument("--output", "-o",
                        help="Directorio de salida")
    parser.add_argument("--merge", nargs='+', metavar='DIR',
                        help="Combinar resultados de múltiples batches")
    
    args = parser.parse_args()
    
    # Modo merge: combinar resultados existentes
    if args.merge:
        # Expandir globs
        dirs = []
        for pattern in args.merge:
            expanded = glob.glob(pattern)
            dirs.extend(expanded)
        dirs = [d for d in dirs if os.path.isdir(d)]
        if not dirs:
            print("  ✗ No se encontraron directorios válidos")
            return
        print(f"\n  Combinando {len(dirs)} batches...")
        merge_batch_results(dirs, output_dir=args.output)
        return
    
    sr_config = {}
    if args.niterations is not None:
        sr_config["niterations"] = args.niterations
    
    run_benchmark(
        category=args.category,
        difficulty=args.difficulty,
        case_name=args.case,
        max_cases=args.max,
        sr_config=sr_config if sr_config else None,
        output_dir=args.output,
        dry_run=args.dry_run,
        from_index=args.from_index,
        to_index=args.to_index,
    )


if __name__ == "__main__":
    main()
