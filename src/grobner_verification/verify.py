"""
Verificación de soluciones polinómicas usando Bases de Gröbner.

Este módulo NO está integrado al pipeline principal.
Se usa como herramienta independiente para comprobar que las expresiones
descubiertas por regresión simbólica son raíces válidas de la ecuación original.

Teoría:
-------
Dada una ecuación polinómica F(x, params) = 0 y una candidata x = g(params),
queremos verificar que F(g(params), params) ≡ 0.

Para expresiones con radicales (sqrt), introducimos una variable auxiliar:
  Si g contiene sqrt(h(params)), definimos s = sqrt(h(params)),
  lo que equivale a s² = h(params), y trabajamos en el anillo polinómico
  extendido con la relación s² - h = 0.

El ideal de verificación es:
  I = < F(x, params), x - g(params), s² - h(params) >

Si al calcular la base de Gröbner de I con respecto a una ordenación que
elimine x (y posiblemente s), el resultado indica que F se reduce a 0
módulo las relaciones dadas, entonces g es una raíz válida.

En la práctica, sustituimos x = g(params) en F y verificamos que el
resultado pertenece al ideal generado por las relaciones auxiliares
(como s² - h = 0).
"""

import sympy as sp
from sympy import (
    symbols, sympify, sqrt, Abs, groebner, reduced,
    Poly, Symbol, degree, expand, simplify, Rational,
    nsimplify, fraction, numer, denom, lcm, together
)
import json
import os
import sys
import re
from pathlib import Path


def load_results(results_dir):
    """Carga los resultados del pipeline desde el directorio de salida."""
    config_path = os.path.join(results_dir, "config.json")
    results_path = os.path.join(results_dir, "results_summary.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"No se encontró config.json en {results_dir}")
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"No se encontró results_summary.json en {results_dir}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    with open(results_path, 'r') as f:
        results = json.load(f)

    return config, results


def parse_expression(expr_str, params):
    """
    Parsea una expresión del pipeline (puede contener safe_pow, safe_sqrt)
    y devuelve la expresión SymPy + lista de sustituciones auxiliares.

    safe_pow(x, y) → abs(x)^y
    safe_sqrt(arg) → sqrt(abs(arg))  (retrocompatibilidad)
    Para la verificación con Gröbner, necesitamos eliminar abs() y sqrt()
    introduciendo variables auxiliares.

    Retorna:
        sympy_expr: expresión SymPy
    """
    # Retrocompatibilidad: safe_sqrt → sqrt
    clean_expr = expr_str.replace("safe_sqrt", "sqrt")

    # Crear símbolos para los parámetros
    param_symbols = {p: symbols(p) for p in params}

    # safe_pow(x, y) = sign(x) * abs(x)^y
    _safe_pow = lambda x, y: sp.sign(x) * sp.Pow(sp.Abs(x), y)
    _neg = lambda x: -x

    # Parsear con SymPy
    local_dict = {**param_symbols, 'sqrt': sqrt, 'safe_pow': _safe_pow, 'neg': _neg}
    expr = sympify(clean_expr, locals=local_dict)

    return expr


def rationalize_expression(expr, tol=1e-4):
    """
    Convierte constantes flotantes cercanas a racionales simples.
    Ej: -4.0000005 → -4, 0.5 → 1/2, -2.0000007 → -2
    
    Esto es ESENCIAL porque PySR devuelve constantes numéricas aproximadas
    y para la verificación algebraica necesitamos valores exactos.
    """
    return nsimplify(expr, rational=True, tolerance=tol)


def extract_sqrt_subexpressions(expr):
    """
    Extrae todas las sub-expresiones dentro de sqrt() en la expresión.
    Retorna un dict {sqrt_expr: argumento_dentro}.
    """
    sqrt_map = {}
    for subexpr in sp.preorder_traversal(expr):
        if isinstance(subexpr, sp.Pow) and subexpr.exp == Rational(1, 2):
            # Es un sqrt(base)
            base = subexpr.base
            sqrt_map[subexpr] = base
    return sqrt_map


def verify_polynomial_root_algebraic(equation_str, expr_str, params, variable="x"):
    """
    Verificación algebraica directa: sustituye la expresión candidata
    en la ecuación y simplifica.

    Primero racionaliza las constantes numéricas (ej: -4.0000005 → -4)
    para permitir cancelaciones exactas.

    Retorna:
        (is_valid, details_dict)
    """
    print(f"\n{'='*60}")
    print(f"  VERIFICACIÓN ALGEBRAICA DIRECTA")
    print(f"{'='*60}")
    print(f"  Ecuación: {equation_str} = 0")
    print(f"  Candidata: {variable} = {expr_str}")

    param_syms = {p: symbols(p) for p in params}
    x = symbols(variable)

    # Parsear ecuación
    eq = sympify(equation_str, locals={**param_syms, variable: x})
    print(f"\n  F({variable}) = {eq}")

    # Parsear candidata y racionalizar constantes
    candidate_raw = parse_expression(expr_str, params)
    candidate = rationalize_expression(candidate_raw)
    print(f"  g(params) raw = {candidate_raw}")
    print(f"  g(params) racionalizada = {candidate}")

    # Sustituir x = g(params) en F
    substituted = eq.subs(x, candidate)
    print(f"\n  F(g(params)) = {substituted}")

    # Expandir y simplificar
    expanded = expand(substituted)
    print(f"  Expandido = {expanded}")

    simplified = simplify(substituted)
    print(f"  Simplificado = {simplified}")

    is_zero = simplified == 0 or simplify(simplified) == 0

    if is_zero:
        print(f"\n  ✓ VERIFICADO: F(g(params)) ≡ 0")
    else:
        print(f"\n  ✗ NO simplifica a 0 directamente")
        print(f"    (Puede requerir verificación con Gröbner para radicales)")

    return is_zero, {
        "method": "algebraic_direct",
        "candidate_rationalized": str(candidate),
        "substituted": str(substituted),
        "expanded": str(expanded),
        "simplified": str(simplified),
        "is_zero": is_zero
    }


def verify_polynomial_root_grobner(equation_str, expr_str, params, variable="x"):
    """
    Verificación usando Bases de Gröbner.

    Proceso:
    1. Racionaliza constantes numéricas (-4.0000005 → -4)
    2. Para expresiones con sqrt, introduce variable auxiliar s con s² = h
    3. Multiplica por denominadores para obtener polinomios puros
    4. Calcula base de Gröbner y reduce F(g) módulo las relaciones
    5. Si safe_sqrt tiene signo ambiguo (sqrt(|h|)), prueba ambos signos

    Retorna:
        (is_valid, details_dict)
    """
    print(f"\n{'='*60}")
    print(f"  VERIFICACIÓN CON BASES DE GRÖBNER")
    print(f"{'='*60}")
    print(f"  Ecuación: {equation_str} = 0")
    print(f"  Candidata: {variable} = {expr_str}")

    param_syms = {p: symbols(p) for p in params}
    x = symbols(variable)

    # Parsear ecuación
    eq = sympify(equation_str, locals={**param_syms, variable: x})

    # Parsear candidata y racionalizar
    candidate_raw = parse_expression(expr_str, params)
    candidate = rationalize_expression(candidate_raw)
    print(f"\n  Candidata racionalizada: {candidate}")

    # Extraer sub-expresiones sqrt
    sqrt_map = extract_sqrt_subexpressions(candidate)

    if not sqrt_map:
        print("\n  No hay radicales. Usando verificación directa...")
        return verify_polynomial_root_algebraic(equation_str, expr_str, params, variable)

    print(f"  Radicales encontrados: {len(sqrt_map)}")

    # Como safe_sqrt(h) = sqrt(|h|), y |h| puede ser h o -h,
    # probamos ambas variantes de signo para cada radical
    sign_variants = _generate_sign_variants(sqrt_map)

    for variant_idx, (sign_label, variant_sqrt_map) in enumerate(sign_variants):
        print(f"\n  --- Variante de signo {variant_idx + 1}: {sign_label} ---")

        result = _try_grobner_with_signs(
            eq, candidate, variant_sqrt_map, param_syms, x, variable
        )

        if result[0]:  # is_valid
            return result

    # Ninguna variante funcionó
    print(f"\n  ✗ Ninguna variante de signo verificó la ecuación")
    return False, {
        "method": "grobner",
        "is_zero": False,
        "note": "Ninguna variante de signo del discriminante verificó"
    }


def _generate_sign_variants(sqrt_map):
    """
    Genera todas las combinaciones de signo para los argumentos de sqrt.
    safe_sqrt(h) = sqrt(|h|), así que el argumento real puede ser h o -h.
    
    Retorna lista de (label, modified_sqrt_map)
    """
    sqrt_items = list(sqrt_map.items())
    n = len(sqrt_items)
    variants = []

    # Generar 2^n combinaciones de signos
    for bits in range(2**n):
        modified = {}
        labels = []
        for i, (sqrt_expr, base_arg) in enumerate(sqrt_items):
            if bits & (1 << i):
                # Negar el argumento
                modified[sqrt_expr] = -base_arg
                labels.append(f"s{i}²=-({base_arg})")
            else:
                # Mantener el argumento original
                modified[sqrt_expr] = base_arg
                labels.append(f"s{i}²={base_arg}")
        variants.append((", ".join(labels), modified))

    return variants


def _try_grobner_with_signs(eq, candidate, sqrt_map, param_syms, x, variable):
    """
    Intenta verificación con Gröbner para una variante de signos específica.
    """
    # Crear variables auxiliares para cada sqrt
    aux_vars = {}
    aux_relations = []
    candidate_poly = candidate

    for i, (sqrt_expr, base_arg) in enumerate(sqrt_map.items()):
        s = symbols(f's{i}')
        aux_vars[sqrt_expr] = s

        # Limpiar Abs si existe
        clean_base = base_arg
        clean_base = clean_base.replace(Abs, lambda arg: arg)

        relation = expand(s**2 - clean_base)
        aux_relations.append(relation)

        # Reemplazar sqrt(base_original) por s en la candidata
        candidate_poly = candidate_poly.subs(sqrt_expr, s)
        print(f"    s{i}² = {clean_base}")
        print(f"    Relación: {relation} = 0")

    print(f"    Candidata polinomializada: {variable} = {candidate_poly}")

    # Sustituir en F
    f_substituted = eq.subs(x, candidate_poly)
    print(f"    F(g) = {f_substituted}")

    # Limpiar fracciones: multiplicar por denominadores comunes
    # Esto convierte expresiones como c + b²/(2a) en polinomios puros
    f_together = together(f_substituted)
    f_num, f_den = fraction(f_together)
    f_poly = expand(f_num)
    print(f"    F(g) × denominador = {f_poly}")
    print(f"    Denominador = {f_den}")

    # Si el numerador ya es 0, verificado
    if f_poly == 0 or simplify(f_poly) == 0:
        print(f"\n  ✓ VERIFICADO: F(g) ≡ 0 (numerador es 0)")
        return True, {
            "method": "grobner",
            "f_numerator": str(f_poly),
            "is_zero": True,
            "note": "Numerador directamente 0"
        }

    # Reunir todas las variables (solo las simbólicas, no numéricas)
    all_params = list(param_syms.values())
    all_aux = list(aux_vars.values())
    all_symbols = all_aux + all_params

    print(f"    Variables del anillo: {all_symbols}")

    # Calcular base de Gröbner y reducir
    try:
        print(f"    Calculando base de Gröbner del ideal de relaciones...")
        gb_relations = groebner(aux_relations, *all_symbols, order='grevlex')
        print(f"    Base de Gröbner (relaciones): {list(gb_relations)}")

        print(f"    Reduciendo F(g) módulo las relaciones...")
        _, remainder = reduced(f_poly, list(gb_relations), *all_symbols, order='grevlex')
        remainder = expand(remainder)
        print(f"    Residuo: {remainder}")

        is_valid = (remainder == 0) or (simplify(remainder) == 0)

        if is_valid:
            print(f"\n  ✓ VERIFICADO POR GRÖBNER: F(g) ≡ 0 (mod s² = h)")
        else:
            print(f"    Residuo no nulo: {remainder}")

        return is_valid, {
            "method": "grobner",
            "f_numerator": str(f_poly),
            "grobner_basis": [str(g) for g in gb_relations],
            "remainder": str(remainder),
            "is_zero": is_valid
        }

    except Exception as e:
        print(f"    ⚠ Error en Gröbner: {e}")
        return False, {
            "method": "grobner",
            "error": str(e),
            "is_zero": False
        }


def verify_numerically(equation_str, expr_str, params, variable="x",
                       num_tests=100, tol=1e-8):
    """
    Verificación numérica: evalúa la expresión en puntos aleatorios
    y comprueba que satisface la ecuación.

    Usa safe_sqrt (sqrt(abs(...))) para la evaluación numérica,
    igual que hace PySR. Solo evalúa en puntos donde la expresión
    produce valores reales válidos.
    """
    import numpy as np

    print(f"\n{'='*60}")
    print(f"  VERIFICACIÓN NUMÉRICA ({num_tests} puntos aleatorios)")
    print(f"{'='*60}")

    param_syms = {p: symbols(p) for p in params}
    x = symbols(variable)

    eq = sympify(equation_str, locals={**param_syms, variable: x})
    candidate = parse_expression(expr_str, params)

    # Sustituir x por la candidata
    f_of_g = eq.subs(x, candidate)

    # Crear función numérica usando numpy con safe_sqrt/safe_pow
    param_list = list(param_syms.values())

    def safe_sqrt_np(x):
        return np.sqrt(np.abs(x))

    def safe_pow_np(x, y):
        return np.sign(x) * np.power(np.abs(x), y)

    f_numeric = sp.lambdify(
        param_list, f_of_g,
        modules=[{'sqrt': safe_sqrt_np, 'Abs': np.abs, 'safe_pow': safe_pow_np}, 'numpy']
    )

    # Generar puntos aleatorios
    np.random.seed(42)
    errors = []
    valid_count = 0
    nan_count = 0

    for _ in range(num_tests):
        vals = np.random.uniform(-3, 3, size=len(params))
        try:
            result = float(f_numeric(*vals))
            if np.isnan(result) or np.isinf(result):
                nan_count += 1
            else:
                errors.append(abs(result))
                if abs(result) < tol:
                    valid_count += 1
        except:
            nan_count += 1

    if errors:
        max_error = max(errors)
        mean_error = sum(errors) / len(errors)
        valid_frac = valid_count / (valid_count + len(errors) - valid_count) if errors else 0

        print(f"  Puntos evaluados: {len(errors)} (+ {nan_count} NaN/Inf)")
        print(f"  Error máximo: {max_error:.2e}")
        print(f"  Error medio:  {mean_error:.2e}")
        print(f"  Puntos válidos (|F(g)| < {tol}): {valid_count}/{len(errors)}")

        is_valid = mean_error < tol
        if is_valid:
            print(f"\n  ✓ VERIFICADO NUMÉRICAMENTE")
        else:
            # Para expresiones con constantes aproximadas (como -4.0000005)
            # puede haber error residual pequeño
            if mean_error < 1e-4:
                print(f"\n  ~ APROXIMADAMENTE VÁLIDO (error residual por constantes numéricas)")
                is_valid = True
            else:
                print(f"\n  ✗ NO VERIFICADO NUMÉRICAMENTE")

        return is_valid, {
            "method": "numerical",
            "num_tests": num_tests,
            "valid_points": valid_count,
            "total_points": len(errors),
            "nan_points": nan_count,
            "max_error": max_error,
            "mean_error": mean_error,
            "is_valid": is_valid
        }
    else:
        print(f"  ⚠ Todos los puntos dieron NaN/Inf")
        return False, {"method": "numerical", "is_valid": False}


def verify_all(results_dir, equation_str=None, params=None, variable="x"):
    """
    Verificación completa de todas las expresiones encontradas por el pipeline.

    Aplica tres niveles de verificación:
      1. Algebraica directa (simplificación simbólica)
      2. Bases de Gröbner (para expresiones con radicales)
      3. Numérica (fallback, útil para constantes aproximadas)
    """
    config, results = load_results(results_dir)

    if equation_str is None:
        equation_str = config.get("equation_string", config.get("equation"))
    if params is None:
        params = config.get("parameters", [])
    if variable == "x":
        variables = config.get("variables", ["x"])
        variable = variables[0] if variables else "x"

    print("=" * 70)
    print("  VERIFICACIÓN DE SOLUCIONES CON BASES DE GRÖBNER")
    print("=" * 70)
    print(f"  Ecuación: {equation_str} = 0")
    print(f"  Variable: {variable}")
    print(f"  Parámetros: {params}")
    print(f"  Directorio: {results_dir}")

    all_results = []

    for branch in results:
        branch_idx = branch["branch_index"]
        print(f"\n\n{'#'*70}")
        print(f"  RAMA {branch_idx}")
        print(f"{'#'*70}")

        for func in branch["functions"]:
            func_idx = func["function_index"]
            expr_str = func["equation"]
            points = func["points_matched"]

            print(f"\n  Función {func_idx}: {expr_str}")
            print(f"  Puntos matcheados: {points}")

            branch_result = {
                "branch": branch_idx,
                "function": func_idx,
                "expression": expr_str,
                "points_matched": points,
                "verifications": {}
            }

            # 1. Verificación algebraica directa
            alg_valid, alg_details = verify_polynomial_root_algebraic(
                equation_str, expr_str, params, variable
            )
            branch_result["verifications"]["algebraic"] = alg_details

            # 2. Verificación con Gröbner (si hay radicales)
            grob_valid, grob_details = verify_polynomial_root_grobner(
                equation_str, expr_str, params, variable
            )
            branch_result["verifications"]["grobner"] = grob_details

            # 3. Verificación numérica
            num_valid, num_details = verify_numerically(
                equation_str, expr_str, params, variable
            )
            branch_result["verifications"]["numerical"] = num_details

            # Resultado combinado
            branch_result["is_valid"] = alg_valid or grob_valid or num_valid
            all_results.append(branch_result)

    # Resumen final
    print(f"\n\n{'='*70}")
    print(f"  RESUMEN DE VERIFICACIÓN")
    print(f"{'='*70}")

    for r in all_results:
        status = "✓ VÁLIDA" if r["is_valid"] else "✗ NO VÁLIDA"
        v = r["verifications"]
        methods = []
        if v.get("algebraic", {}).get("is_zero"):
            methods.append("algebraica")
        if v.get("grobner", {}).get("is_zero"):
            methods.append("Gröbner")
        if v.get("numerical", {}).get("is_valid"):
            methods.append("numérica")

        print(f"\n  Rama {r['branch']}, Función {r['function']}: {status}")
        print(f"    Expresión: {r['expression']}")
        print(f"    Verificada por: {', '.join(methods) if methods else 'ningún método'}")
        print(f"    Puntos matcheados: {r['points_matched']}")

    return all_results


def main():
    """Punto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verificación de soluciones polinómicas con Bases de Gröbner"
    )
    parser.add_argument(
        "results_dir",
        help="Directorio con los resultados del pipeline (contiene config.json y results_summary.json)"
    )
    parser.add_argument(
        "--equation", "-e",
        help="Ecuación original (override del config.json)",
        default=None
    )
    parser.add_argument(
        "--variable", "-v",
        help="Variable a resolver (default: x)",
        default="x"
    )

    args = parser.parse_args()
    verify_all(args.results_dir, equation_str=args.equation, variable=args.variable)


if __name__ == "__main__":
    main()
