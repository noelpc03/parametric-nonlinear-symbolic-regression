"""
Adaptador para usar el sistema de regresión simbólica adaptado
con datos multidimensionales (múltiples parámetros)
"""
import os
import sys
import numpy as np
import sympy as sp
from typing import List, Dict, Any

# Importar del sistema adaptado en esta misma carpeta
from symbolic_regression import iterative_symbolic_regression, train_symbolic_model, _evaluate_hall_of_fame
from utils import find_matched_points

# Asegurar que src/ esté en el path para importar el config unificado
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from config import EPSILON, K, NITERATIONS, MIN_POINTS


def run_symbolic_regression_for_branch(branch_data: Dict[str, np.ndarray],
                                       param_names: List[str],
                                       branch_index: int,
                                       epsilon: float = EPSILON,
                                       k: float = K,
                                       niterations: int = NITERATIONS,
                                       min_points: int = MIN_POINTS) -> List[Dict[str, Any]]:
    """
    Ejecuta regresión simbólica para una rama de raíces.
    La lógica iterativa y criterios de parada están dentro de iterative_symbolic_regression.

    Args:
        branch_data: Diccionario con 'X' (parámetros) e 'y' (raíces) de una rama
        param_names: Lista de nombres de parámetros
        branch_index: Índice de la rama para trazabilidad en logs
        epsilon: Tolerancia de matcheo
        k: Pendiente para la loss sigmoidal (si está activa)
        niterations: Iteraciones internas de PySR por corrida
        min_points: Mínimo de puntos para continuar la búsqueda iterativa

    Returns:
        results: Lista de ecuaciones/iteraciones aceptadas para esa rama
    """
    X = branch_data['X']
    y = branch_data['y']

    print(f"\n{'='*60}")
    print(f"REGRESIÓN SIMBÓLICA - RAMA {branch_index + 1}")
    print(f"{'='*60}")
    print(f"Datos: {len(y)} puntos, {X.shape[1]} parámetros")
    print(f"Parámetros: {param_names}")

    results = iterative_symbolic_regression(
        X, y,
        param_names=param_names,
        epsilon=epsilon,
        k=k,
        niterations=niterations,
        min_points=min_points
    )

    return results


def run_for_all_branches(branches: List[Dict[str, np.ndarray]],
                        param_names: List[str],
                        epsilon: float = EPSILON,
                        k: float = K,
                        niterations: int = NITERATIONS,
                        min_points: int = MIN_POINTS) -> List[List[Dict[str, Any]]]:
    """
    Ejecuta regresión simbólica para todas las ramas.

    Args:
        branches: Lista de datasets por rama, cada uno con 'X' e 'y'
        param_names: Lista de nombres de parámetros
        epsilon: Tolerancia de matcheo
        k: Pendiente para la loss sigmoidal (si está activa)
        niterations: Iteraciones internas de PySR por corrida
        min_points: Mínimo de puntos para continuar la búsqueda iterativa

    Returns:
        all_results: Lista con resultados por rama
    """
    all_results = []

    for i, branch in enumerate(branches):
        results = run_symbolic_regression_for_branch(
            branch, param_names, i,
            epsilon, k, niterations, min_points
        )
        all_results.append(results)

    return all_results


def run_combined_symbolic_regression(combined_data: Dict[str, np.ndarray],
                                      param_names: List[str],
                                      epsilon: float = EPSILON,
                                      k: float = K,
                                      niterations: int = NITERATIONS,
                                      min_points: int = MIN_POINTS,
                                      max_iterations: int = None) -> List[Dict[str, Any]]:
    """
    Ejecuta regresión simbólica sobre TODAS las raíces combinadas.

    En lugar de separar por ramas primero, el algoritmo iterativo
    descubre las ecuaciones una por una a partir del conjunto completo.
    Cada ecuación encontrada debería corresponder a una rama.

    Args:
        combined_data: Dict con 'X' (parámetros) e 'y' (raíces combinadas)
        param_names: Lista de nombres de parámetros
        epsilon: Tolerancia para matcheo
        k: Parámetro de suavidad para loss sigmoidal
        niterations: Iteraciones de PySR por intento
        min_points: Mínimo de puntos para continuar
        max_iterations: Máximo de iteraciones (None = usar default de config)

    Returns:
        Lista de ecuaciones encontradas (cada una representa una "rama" descubierta)
    """
    X = combined_data['X']
    y = combined_data['y']

    print(f"\n{'='*60}")
    print(f"REGRESIÓN SIMBÓLICA - MODO COMBINADO")
    print(f"{'='*60}")
    print(f"Datos: {len(y)} tuplas (params → root)")
    print(f"Dimensiones: {X.shape[1]} parámetros")
    print(f"Parámetros: {param_names}")
    print(f"\nEl algoritmo iterativo descubrirá las ecuaciones (ramas)")
    print(f"una por una, quitando puntos matcheados en cada paso.")

    kwargs = dict(
        param_names=param_names,
        epsilon=epsilon,
        k=k,
        niterations=niterations,
        min_points=min_points
    )
    if max_iterations is not None:
        kwargs['max_iterations'] = max_iterations

    results = iterative_symbolic_regression(X, y, **kwargs)

    # Resumen de ecuaciones encontradas
    print(f"\n{'='*60}")
    print(f"RESUMEN: {len(results)} ECUACIONES DESCUBIERTAS")
    print(f"{'='*60}")
    for i, res in enumerate(results):
        print(f"  {i+1}. {res['equation']} ({res['num_matched']} puntos)")

    return results


def validate_branch(expressions: List[str],
                    param_names: List[str],
                    X: np.ndarray,
                    Y: np.ndarray,
                    equations: List[sp.Expr],
                    variables: List[sp.Symbol],
                    tol: float = 1e-4) -> bool:
    """
    Valida que una rama completa (sistema de expresiones para cada variable)
    satisface el sistema original F(x; θ) = 0.
    
    Args:
        expressions: Lista de strings con expresiones para cada variable
        param_names: Lista de nombres de parámetros
        X: Array (M, num_params) con los puntos de parámetros
        Y: Array (M, num_vars) con las soluciones esperadas
        equations: Lista de expresiones SymPy del sistema
        variables: Lista de símbolos SymPy de variables
        tol: Tolerancia del residuo ||F(x; θ)||
    
    Returns:
        True si la rama es válida, False en caso contrario
    """
    try:
        # Crear diccionario de símbolo->expresión para sustitución
        expr_subs = {}
        for var, expr_str in zip(variables, expressions):
            # Parsear la expresión string a expresión SymPy
            param_syms = [sp.Symbol(p) for p in param_names]
            expr = sp.sympify(expr_str, locals={p: sp.Symbol(p) for p in param_names})
            expr_subs[var] = expr
        
        # Crear funciones evaluables para el sistema
        total_residue = 0.0
        num_points = len(X)
        
        for i in range(num_points):
            # Crear diccionario de valor de parámetros para este punto
            param_vals = {sp.Symbol(p): X[i, j] for j, p in enumerate(param_names)}
            # Sustituir primero variables por expresiones y luego parámetros por valores
            # para evitar reintroducir símbolos al hacer la segunda sustitución.
            eqs_eval = [eq.subs(expr_subs).subs(param_vals) for eq in equations]
            
            # Evaluar cada ecuación
            for eq in eqs_eval:
                val = float(eq)
                total_residue += val ** 2
        
        mean_residue = np.sqrt(total_residue / (num_points * len(equations)))
        
        if mean_residue < tol:
            print(f"✓ Rama validada (residuo medio: {mean_residue:.2e})")
            return True
        else:
            print(f"✗ Rama rechazada (residuo medio: {mean_residue:.2e} > {tol:.2e})")
            return False
    
    except Exception as e:
        print(f"✗ Error al validar rama: {e}")
        return False


def run_anchored_symbolic_regression(combined_data: Dict[str, Any],
                                     param_names: List[str],
                                     equations: List[sp.Expr],
                                     variables: List[sp.Symbol],
                                     anchor_coord: int = 0,
                                     epsilon: float = EPSILON,
                                     k: float = K,
                                     niterations: int = NITERATIONS,
                                     min_points: int = MIN_POINTS,
                                     max_iterations: int = None,
                                     validation_tol: float = 1e-4) -> List[Dict[str, Any]]:
    """
    Ejecuta regresión simbólica multidimensional usando la estrategia de ANCLAJE.
    
    Algoritmo:
      1. Usar coordinate[anchor_coord] para hacer SR iterativa (descubre ramas)
      2. Para cada rama, hacer SR simple en las otras coordenadas
      3. Validar que la rama completa satisface el sistema original
      4. Si válida, guardarla y quitar los puntos; si no, descartar
      5. Repetir hasta que no haya suficientes puntos
    
    Args:
        combined_data: Dict con 'X' (params), 'Y' (solutions), 'tuple_id', 'solution_id'
        param_names: Nombres de los parámetros
        equations: Expresiones SymPy del sistema
        variables: Símbolos SymPy de variables
        anchor_coord: Índice de la variable usada como ancla (default: 0 → x1)
        epsilon: Tolerancia para matcheo en SR
        k: Parámetro de suavidad para la loss sigmoidal
        niterations: Iteraciones internas de PySR
        min_points: Mínimo de puntos para continuar
        max_iterations: Máximo de iteraciones (None = sin límite)
        validation_tol: Tolerancia de validación del residuo
    
    Returns:
        Lista de ramas válidas encontradas, cada una con:
        {
            'expressions': [expr1, expr2, ...],  # Una por variable
            'matched_indices': array de índices globales,
            'num_matched': cantidad de puntos matcheados,
            'residue': residuo de validación
        }
    """
    X = combined_data['X']
    Y = combined_data['Y']
    num_vars = Y.shape[1]
    
    print(f"\n{'='*70}")
    print(f"REGRESIÓN SIMBÓLICA MULTIDIMENSIONAL CON ANCLAJE")
    print(f"{'='*70}")
    print(f"Variable ancla: {variables[anchor_coord]} (índice {anchor_coord})")
    print(f"Datos totales: {len(Y)} puntos, {num_vars} variables")
    print(f"Parámetros: {param_names}\n")
    
    results = []
    remaining_mask = np.ones(len(X), dtype=bool)
    all_indices = np.arange(len(X))
    iteration = 0
    
    while np.sum(remaining_mask) >= min_points:
        iteration += 1
        
        if max_iterations is not None and iteration > max_iterations:
            print(f"\n⚠️  Se alcanzó el máximo de iteraciones ({max_iterations})")
            break
        
        print(f"\n{'─'*70}")
        print(f"ITERACIÓN {iteration}: {np.sum(remaining_mask)} puntos restantes")
        print(f"{'─'*70}")
        
        # Extraer datos restantes
        X_cur = X[remaining_mask]
        Y_cur = Y[remaining_mask]
        cur_indices = all_indices[remaining_mask]
        y_anchor = Y_cur[:, anchor_coord]
        
        # ════════════════════════════════════════════════════════════════
        # FASE 1: SR iterativa sobre la variable ancla
        # ════════════════════════════════════════════════════════════════
        print(f"\n📌 Fase 1: SR iterativa sobre variable ancla ({variables[anchor_coord]})")
        
        anchor_results = iterative_symbolic_regression(
            X_cur, y_anchor, param_names,
            epsilon=epsilon, k=k, niterations=niterations,
            min_points=1, max_iterations=1
        )
        
        if len(anchor_results) == 0 or anchor_results[0]['num_matched'] == 0:
            print(f"✗ No se encontró ecuación para el ancla. Deteniendo.")
            break
        
        best_anchor = anchor_results[0]
        matched_local = best_anchor['matched_indices']
        matched_global = cur_indices[matched_local]
        
        print(f"✓ Ecuación ancla encontrada: {best_anchor['equation']}")
        print(f"  Matchea: {len(matched_local)}/{len(X_cur)} puntos")
        
        # ════════════════════════════════════════════════════════════════
        # FASE 2: SR simple para cada otra variable
        # ════════════════════════════════════════════════════════════════
        print(f"\n📝 Fase 2: SR para variables restantes")
        
        branch_exprs = [None] * num_vars
        branch_exprs[anchor_coord] = best_anchor['equation']
        
        for coord in range(num_vars):
            if coord == anchor_coord:
                continue
            
            y_sub = Y[matched_global, coord]
            
            # Si todos los valores son casi idénticos, usar la constante
            if np.allclose(y_sub, y_sub[0], rtol=1e-5):
                branch_exprs[coord] = str(float(y_sub[0]))
                print(f"  {variables[coord]}: constante = {y_sub[0]:.6g}")
                continue
            
            # Hacer SR para esta variable
            try:
                model = train_symbolic_model(
                    X[matched_global], y_sub, param_names,
                    k=k, epsilon=epsilon, niterations=niterations
                )
                
                # Evaluar hall of fame y obtener la mejor expresión
                best = _evaluate_hall_of_fame(
                    model, X[matched_global], y_sub, epsilon=epsilon
                )
                
                if best is not None:
                    branch_exprs[coord] = best['equation_str']
                    print(f"  {variables[coord]}: {best['equation_str']}")
                else:
                    branch_exprs[coord] = "?"
                    print(f"  {variables[coord]}: no se encontró expresión")
            
            except Exception as e:
                print(f"  {variables[coord]}: error durante SR ({str(e)[:50]}...)")
                branch_exprs[coord] = "?"
        
        # ════════════════════════════════════════════════════════════════
        # FASE 3: Validación de la rama completa
        # ════════════════════════════════════════════════════════════════
        print(f"\n✔️  Fase 3: Validación de la rama completa")
        
        is_valid = validate_branch(
            branch_exprs, param_names,
            X[matched_global], Y[matched_global],
            equations, variables,
            tol=validation_tol
        )
        
        if is_valid:
            # Guardar rama y remover puntos
            results.append({
                'expressions': branch_exprs,
                'matched_indices': matched_global,
                'num_matched': len(matched_global),
                'iteration': iteration
            })
            remaining_mask[matched_global] = False
            print(f"✓ Rama {len(results)} aceptada y guardada.")
        else:
            # Descartar rama
            remaining_mask[matched_global] = False
            print(f"✗ Rama rechazada. Los puntos se descartan.")
    
    # ════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ════════════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"✓ ALGORITMO COMPLETADO")
    print(f"{'='*70}")
    print(f"Ramas encontradas: {len(results)}")
    for i, res in enumerate(results):
        print(f"\nRama {i+1}:")
        for j, expr in enumerate(res['expressions']):
            print(f"  {variables[j]} = {expr}")
        print(f"  Puntos matcheados: {res['num_matched']}")
    
    return results
