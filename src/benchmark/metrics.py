"""
Módulo de métricas y comparación para el benchmark.

Compara las expresiones descubiertas por PySR contra las esperadas.
Calcula métricas globales y por categoría.
"""

import numpy as np
import sympy as sp
from sympy import symbols, sympify, sqrt, Abs, simplify, nsimplify, expand
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict


def _parse_expr(expr_str, param_names):
    """Parsea una expresión string a SymPy, manejando safe_sqrt."""
    clean = expr_str.replace("safe_sqrt", "sqrt")
    param_syms = {p: symbols(p) for p in param_names}
    local_dict = {**param_syms, 'sqrt': sp.sqrt}
    try:
        expr = sympify(clean, locals=local_dict)
        return expr
    except Exception:
        return None


def _rationalize(expr, tol=1e-3):
    """Racionaliza constantes numéricas."""
    try:
        return nsimplify(expr, rational=True, tolerance=tol)
    except Exception:
        return expr


def _expressions_equivalent(discovered_str, expected_str, param_names, 
                             num_tests=200, tol=1e-4):
    """
    Verifica si dos expresiones son equivalentes numéricamente.
    
    Evalúa ambas en muchos puntos aleatorios y compara.
    
    Args:
        discovered_str: expresión descubierta (puede tener safe_sqrt)
        expected_str: expresión esperada
        param_names: nombres de parámetros
        num_tests: número de puntos de prueba
        tol: tolerancia relativa para equivalencia
    
    Returns:
        (is_equivalent, match_fraction, mean_relative_error)
    """
    discovered = _parse_expr(discovered_str, param_names)
    expected = _parse_expr(expected_str, param_names)
    
    if discovered is None or expected is None:
        return False, 0.0, float('inf')
    
    # Intentar primero simplificación simbólica
    try:
        discovered_rat = _rationalize(discovered)
        diff = simplify(expand(discovered_rat - expected))
        if diff == 0:
            return True, 1.0, 0.0
    except Exception:
        pass
    
    # Fallback: comparación numérica
    param_syms = [symbols(p) for p in param_names]
    
    def safe_sqrt_np(x):
        return np.sqrt(np.abs(x))
    
    try:
        f_discovered = sp.lambdify(
            param_syms, discovered,
            modules=[{'sqrt': safe_sqrt_np, 'Abs': np.abs}, 'numpy']
        )
        f_expected = sp.lambdify(
            param_syms, expected,
            modules=[{'sqrt': np.sqrt, 'Abs': np.abs}, 'numpy']
        )
    except Exception:
        return False, 0.0, float('inf')
    
    np.random.seed(42)
    matches = 0
    errors = []
    valid = 0
    
    for _ in range(num_tests):
        vals = np.random.uniform(0.1, 3.0, size=len(param_names))
        try:
            v_disc = float(f_discovered(*vals))
            v_exp = float(f_expected(*vals))
            
            if np.isnan(v_disc) or np.isnan(v_exp) or np.isinf(v_disc) or np.isinf(v_exp):
                continue
            
            valid += 1
            rel_err = abs(v_disc - v_exp) / (1.0 + abs(v_exp))
            errors.append(rel_err)
            
            if rel_err < tol:
                matches += 1
        except Exception:
            continue
    
    if valid == 0:
        return False, 0.0, float('inf')
    
    match_fraction = matches / valid
    mean_error = np.mean(errors) if errors else float('inf')
    is_equiv = match_fraction > 0.95
    
    return is_equiv, match_fraction, mean_error


def evaluate_case(case_result, test_case):
    """
    Evalúa un resultado individual comparando con las raíces esperadas.
    
    Args:
        case_result: dict retornado por run_single_case
        test_case: dict del catálogo de test_cases
    
    Returns:
        evaluation: dict con métricas del caso:
            - roots_matched: cuántas raíces esperadas se encontraron
            - roots_expected: cuántas raíces se esperaban
            - root_match_rate: fracción de raíces encontradas
            - branch_count_correct: si encontró el # correcto de ramas
            - average_coverage: cobertura promedio de puntos por rama
            - match_details: detalle de qué raíz matcheó con qué
            - expression_exact: si las expresiones son simbólicamente idénticas
            - status: del caso
            - time: tiempo total
    """
    evaluation = {
        "name": case_result["name"],
        "category": case_result["category"],
        "difficulty": case_result["difficulty"],
        "status": case_result["status"],
        "time_seconds": case_result["total_time_seconds"],
        "roots_expected": len(test_case["expected_roots"]),
        "roots_matched": 0,
        "root_match_rate": 0.0,
        "branch_count_correct": False,
        "average_coverage": 0.0,
        "match_details": [],
        "any_error": case_result.get("error_message"),
    }
    
    if case_result["status"] not in ("success", "no_sr_results"):
        return evaluation
    
    # Verificar número de ramas
    expected_branches = len(test_case["expected_roots"])
    found_branches = case_result["num_branches_found"]
    evaluation["branch_count_correct"] = (found_branches == expected_branches)
    evaluation["num_branches_found"] = found_branches
    
    # Cobertura promedio
    coverages = [br["coverage"] for br in case_result["branch_results"]]
    evaluation["average_coverage"] = np.mean(coverages) if coverages else 0.0
    
    # Comparar raíces descubiertas vs esperadas
    param_names = test_case["parameters"]
    discovered = case_result["discovered_roots"]
    expected = test_case["expected_roots"]
    
    # Para cada raíz esperada, buscar la mejor coincidencia entre las descubiertas
    matched_expected = set()
    matched_discovered = set()
    
    # Primera pasada: encontrar matches exactos (equivalentes)
    for i, exp_root in enumerate(expected):
        best_match = None
        best_fraction = 0.0
        
        for j, disc_root in enumerate(discovered):
            if j in matched_discovered:
                continue
            
            is_equiv, fraction, mean_err = _expressions_equivalent(
                disc_root, exp_root, param_names
            )
            
            if is_equiv and fraction > best_fraction:
                best_match = j
                best_fraction = fraction
        
        if best_match is not None:
            matched_expected.add(i)
            matched_discovered.add(best_match)
            evaluation["match_details"].append({
                "expected": exp_root,
                "discovered": discovered[best_match],
                "match_fraction": best_fraction,
                "matched": True,
            })
        else:
            # No se encontró equivalencia exacta.
            # Buscar la raíz descubierta más cercana (no matcheada) para contexto.
            closest_disc = None
            closest_fraction = 0.0
            closest_error = float('inf')
            for j, disc_root in enumerate(discovered):
                if j in matched_discovered:
                    continue
                _, fraction, mean_err = _expressions_equivalent(
                    disc_root, exp_root, param_names
                )
                if fraction > closest_fraction or (fraction == closest_fraction and mean_err < closest_error):
                    closest_disc = disc_root
                    closest_fraction = fraction
                    closest_error = mean_err
            
            evaluation["match_details"].append({
                "expected": exp_root,
                "discovered": None,
                "match_fraction": 0.0,
                "matched": False,
                "closest_discovered": closest_disc,
                "closest_fraction": closest_fraction,
                "closest_error": closest_error,
            })
    
    # Registrar raíces descubiertas que no matchearon con ninguna esperada
    unmatched_discovered = [discovered[j] for j in range(len(discovered)) if j not in matched_discovered]
    evaluation["unmatched_discovered"] = unmatched_discovered
    
    evaluation["roots_matched"] = len(matched_expected)
    evaluation["root_match_rate"] = len(matched_expected) / len(expected) if expected else 0.0
    
    return evaluation


def compute_global_metrics(evaluations: List[Dict]) -> Dict:
    """
    Calcula métricas globales del benchmark.
    
    Args:
        evaluations: lista de dicts de evaluate_case
    
    Returns:
        metrics: dict con métricas globales
    """
    n = len(evaluations)
    if n == 0:
        return {"error": "No hay evaluaciones"}
    
    # ── Métricas globales ──
    statuses = Counter(e["status"] for e in evaluations)
    
    successful = [e for e in evaluations if e["status"] == "success"]
    n_success = len(successful)
    
    # Tasa de éxito (pipeline completa sin errores)
    success_rate = n_success / n
    
    # Tasa de raíces encontradas (sobre todos los casos exitosos)
    total_expected = sum(e["roots_expected"] for e in successful)
    total_matched = sum(e["roots_matched"] for e in successful)
    root_discovery_rate = total_matched / total_expected if total_expected > 0 else 0.0
    
    # Casos perfectos (todas las raíces encontradas)
    perfect = sum(1 for e in successful if e["root_match_rate"] == 1.0)
    perfect_rate = perfect / n
    
    # Cobertura promedio
    avg_coverage = np.mean([e["average_coverage"] for e in successful]) if successful else 0.0
    
    # Tiempo
    total_time = sum(e["time_seconds"] for e in evaluations)
    avg_time = np.mean([e["time_seconds"] for e in evaluations])
    
    # Ramas correctas
    branch_correct = sum(1 for e in successful if e["branch_count_correct"])
    branch_rate = branch_correct / n_success if n_success > 0 else 0.0
    
    metrics = {
        "total_cases": n,
        "status_distribution": dict(statuses),
        "success_rate": success_rate,
        "root_discovery_rate": root_discovery_rate,
        "perfect_cases": perfect,
        "perfect_rate": perfect_rate,
        "average_coverage": avg_coverage,
        "branch_count_accuracy": branch_rate,
        "total_time_seconds": total_time,
        "average_time_seconds": avg_time,
    }
    
    # ── Métricas por categoría ──
    categories = defaultdict(list)
    for e in evaluations:
        categories[e["category"]].append(e)
    
    metrics["by_category"] = {}
    for cat, cat_evals in sorted(categories.items()):
        cat_success = [e for e in cat_evals if e["status"] == "success"]
        cat_total_exp = sum(e["roots_expected"] for e in cat_success)
        cat_total_match = sum(e["roots_matched"] for e in cat_success)
        cat_perfect = sum(1 for e in cat_success if e["root_match_rate"] == 1.0)
        
        metrics["by_category"][cat] = {
            "total": len(cat_evals),
            "success": len(cat_success),
            "root_discovery_rate": cat_total_match / cat_total_exp if cat_total_exp > 0 else 0.0,
            "perfect_cases": cat_perfect,
            "perfect_rate": cat_perfect / len(cat_evals) if cat_evals else 0.0,
            "avg_time": np.mean([e["time_seconds"] for e in cat_evals]),
        }
    
    # ── Métricas por dificultad ──
    difficulties = defaultdict(list)
    for e in evaluations:
        difficulties[e["difficulty"]].append(e)
    
    metrics["by_difficulty"] = {}
    for diff, diff_evals in sorted(difficulties.items()):
        diff_success = [e for e in diff_evals if e["status"] == "success"]
        diff_total_exp = sum(e["roots_expected"] for e in diff_success)
        diff_total_match = sum(e["roots_matched"] for e in diff_success)
        diff_perfect = sum(1 for e in diff_success if e["root_match_rate"] == 1.0)
        
        metrics["by_difficulty"][diff] = {
            "total": len(diff_evals),
            "success": len(diff_success),
            "root_discovery_rate": diff_total_match / diff_total_exp if diff_total_exp > 0 else 0.0,
            "perfect_cases": diff_perfect,
            "perfect_rate": diff_perfect / len(diff_evals) if diff_evals else 0.0,
            "avg_time": np.mean([e["time_seconds"] for e in diff_evals]),
        }
    
    return metrics


def print_metrics_report(metrics: Dict, evaluations: List[Dict]):
    """Imprime un reporte legible de las métricas."""
    
    print("\n" + "=" * 70)
    print("  REPORTE DE BENCHMARK — MÉTRICAS GLOBALES")
    print("=" * 70)
    
    print(f"\n  Casos totales: {metrics['total_cases']}")
    print(f"  Status: {metrics['status_distribution']}")
    print(f"\n  ── Tasas de éxito ──")
    print(f"  Pipeline completado sin error:  {metrics['success_rate']*100:.1f}%")
    print(f"  Raíces descubiertas (global):   {metrics['root_discovery_rate']*100:.1f}%")
    print(f"  Casos perfectos (100% raíces):  {metrics['perfect_cases']}/{metrics['total_cases']} ({metrics['perfect_rate']*100:.1f}%)")
    print(f"  # Ramas correcto:              {metrics['branch_count_accuracy']*100:.1f}%")
    print(f"  Cobertura promedio por rama:    {metrics['average_coverage']*100:.1f}%")
    
    print(f"\n  ── Tiempos ──")
    print(f"  Tiempo total:    {metrics['total_time_seconds']:.1f}s")
    print(f"  Tiempo promedio: {metrics['average_time_seconds']:.1f}s/caso")
    
    # Por categoría
    print(f"\n  ── Por categoría ──")
    print(f"  {'Categoría':12s} {'Total':>5s} {'OK':>4s} {'Raíces%':>8s} {'Perfect':>8s} {'T(s)':>7s}")
    print(f"  {'-'*12} {'-'*5} {'-'*4} {'-'*8} {'-'*8} {'-'*7}")
    for cat, cm in sorted(metrics["by_category"].items()):
        print(f"  {cat:12s} {cm['total']:5d} {cm['success']:4d} "
              f"{cm['root_discovery_rate']*100:7.1f}% "
              f"{cm['perfect_cases']:3d}/{cm['total']:<3d} "
              f"{cm['avg_time']:7.1f}")
    
    # Por dificultad
    print(f"\n  ── Por dificultad ──")
    print(f"  {'Dificultad':12s} {'Total':>5s} {'OK':>4s} {'Raíces%':>8s} {'Perfect':>8s} {'T(s)':>7s}")
    print(f"  {'-'*12} {'-'*5} {'-'*4} {'-'*8} {'-'*8} {'-'*7}")
    for diff in ["easy", "medium", "hard"]:
        if diff in metrics["by_difficulty"]:
            dm = metrics["by_difficulty"][diff]
            print(f"  {diff:12s} {dm['total']:5d} {dm['success']:4d} "
                  f"{dm['root_discovery_rate']*100:7.1f}% "
                  f"{dm['perfect_cases']:3d}/{dm['total']:<3d} "
                  f"{dm['avg_time']:7.1f}")
    
    # Detalle por caso
    print(f"\n  ── Detalle por caso ──")
    print(f"  {'Caso':35s} {'Status':>10s} {'Raíces':>10s} {'Coverag':>8s} {'T(s)':>7s}")
    print(f"  {'-'*35} {'-'*10} {'-'*10} {'-'*8} {'-'*7}")
    
    for e in evaluations:
        status_icon = {
            "success": "✓",
            "error": "✗",
            "no_roots": "∅",
            "no_sr_results": "~"
        }.get(e["status"], "?")
        
        roots_str = f"{e['roots_matched']}/{e['roots_expected']}"
        cov_str = f"{e['average_coverage']*100:.0f}%" if e["status"] == "success" else "-"
        
        print(f"  {status_icon} {e['name']:33s} {e['status']:>9s} {roots_str:>10s} {cov_str:>8s} {e['time_seconds']:7.1f}")
    
    # Casos fallidos
    failed = [e for e in evaluations if e["status"] != "success" or e["root_match_rate"] < 1.0]
    if failed:
        print(f"\n  ── Casos no perfectos ──")
        for e in failed:
            print(f"\n  {e['name']} [{e['status']}]:")
            if e.get("any_error"):
                print(f"    Error: {e['any_error'][:100]}")
            for md in e.get("match_details", []):
                icon = "✓" if md["matched"] else "✗"
                print(f"    {icon} Esperada: {md['expected']}")
                if md["matched"]:
                    print(f"      Descubierta: {md['discovered']}")
                else:
                    closest = md.get("closest_discovered")
                    if closest:
                        frac = md.get("closest_fraction", 0)
                        err = md.get("closest_error", float('inf'))
                        print(f"      Descubierta: (no matcheó)")
                        print(f"      Más cercana: {closest}  [coincidencia={frac*100:.1f}%, error={err:.4f}]")
                    else:
                        print(f"      Descubierta: (rama no encontrada por el pipeline)")
            unmatched = e.get("unmatched_discovered", [])
            if unmatched:
                print(f"    ⚠ Raíces descubiertas sin match:")
                for ur in unmatched:
                    print(f"      → {ur}")
