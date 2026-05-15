"""
Pruebas modulares y livianas para validar cambios del pipeline de sistemas.

Este script evita correr todo el pipeline completo (costoso en recursos)
y permite verificar cada bloque por separado.
"""

import argparse
import os
import sys
from typing import Callable, Dict

import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

for subdir in [
    "1_equation_definition",
    "2_parameter_grid",
    "3_zero_finding",
    "4_data_preparation",
    "5_symbolic_regression",
]:
    path = os.path.join(BASE_DIR, subdir)
    if path not in sys.path:
        sys.path.insert(0, path)

from config import EQUATIONS, VARIABLES, PARAMETERS, PARAMETER_RANGES
from equation_parser import parse_system
from grid_generator import generate_grid
from solver import solve_system_scipy
from root_grouping import combine_all_solutions


def check_parser() -> None:
    equations_sympy, symbols_dict = parse_system(EQUATIONS, VARIABLES, PARAMETERS)

    assert len(equations_sympy) == len(EQUATIONS), "Cantidad de ecuaciones parseadas incorrecta"
    assert all(v in symbols_dict for v in VARIABLES), "Faltan variables en symbols_dict"
    assert all(p in symbols_dict for p in PARAMETERS), "Faltan parametros en symbols_dict"

    print("OK parser: sistema parseado correctamente")


def check_grid() -> None:
    grid, names = generate_grid(PARAMETER_RANGES)

    expected_size = 1
    for _, _, n_points in PARAMETER_RANGES.values():
        expected_size *= n_points

    assert names == list(PARAMETER_RANGES.keys()), "Orden de parametros inesperado"
    assert grid.shape[0] == expected_size, "Tamano del grid incorrecto"
    assert grid.shape[1] == len(PARAMETER_RANGES), "Numero de columnas incorrecto en grid"

    print(f"OK grid: shape={grid.shape}, parametros={names}")


def _system_context():
    equations_sympy, symbols_dict = parse_system(EQUATIONS, VARIABLES, PARAMETERS)
    var_symbols = [symbols_dict[v] for v in VARIABLES]
    return equations_sympy, symbols_dict, var_symbols


def check_solver() -> None:
    equations_sympy, symbols_dict, var_symbols = _system_context()

    # Una sola tupla para test rapido y de bajo costo.
    param_values = {
        symbols_dict["a"]: 1.0,
        symbols_dict["b"]: 2.0,
    }

    np.random.seed(0)
    roots = solve_system_scipy(
        equations=equations_sympy,
        variables=var_symbols,
        param_values=param_values,
        guess_ranges={"x1": (-5.0, 5.0), "x2": (-5.0, 5.0)},
        num_guesses=12,
        dist_tol=1e-3,
        residue_tol=1e-6,
    )

    assert len(roots) >= 1, "El solver no encontro ninguna solucion en el caso de prueba"

    # Verificar que el residuo sea bajo para cada solucion encontrada.
    for root in roots:
        x1, x2 = float(root[0]), float(root[1])
        r1 = (x1 - 1.0) * (x2 - 2.0)
        r2 = x1 * x2 - 4.0
        assert np.sqrt(r1 * r1 + r2 * r2) < 1e-4, "Solucion con residuo alto"

    print(f"OK solver: soluciones encontradas={len(roots)}")


def check_combine() -> None:
    # Dataset sintetico minimo para verificar estructura vectorial Y:(M, n_vars).
    fake_results = [
        {
            "parameters": {"a": 1.0, "b": 2.0},
            "roots": [np.array([2.0, 2.0]), np.array([1.0, 4.0])],
            "num_roots": 2,
        },
        {
            "parameters": {"a": 2.0, "b": 3.0},
            "roots": [np.array([3.0, 6.0])],
            "num_roots": 1,
        },
    ]

    combined = combine_all_solutions(fake_results, ["a", "b"])

    assert combined["X"].shape == (3, 2), "X debe ser (M, n_params)"
    assert combined["Y"].shape == (3, 2), "Y debe ser (M, n_vars)"
    assert combined["tuple_id"].shape == (3,), "tuple_id con shape incorrecto"
    assert combined["solution_id"].shape == (3,), "solution_id con shape incorrecto"
    assert combined["num_variables"] == 2, "num_variables incorrecto"

    print("OK combine: estructura vectorial correcta")


def check_validate() -> None:
    from regression_adapter import validate_branch

    equations_sympy, symbols_dict, var_symbols = _system_context()

    # Parametros de prueba.
    X = np.array(
        [
            [1.0, 2.0],
            [1.5, 2.5],
            [2.0, 3.0],
        ],
        dtype=float,
    )

    # Expresiones validas para una rama del sistema actual:
    # x1 = b, x2 = a*b
    expressions_ok = ["b", "a*b"]

    # Y se usa por compatibilidad de firma; validate_branch no lo explota internamente.
    Y_dummy = np.zeros((X.shape[0], len(var_symbols)), dtype=float)

    valid = validate_branch(
        expressions=expressions_ok,
        param_names=PARAMETERS,
        X=X,
        Y=Y_dummy,
        equations=equations_sympy,
        variables=var_symbols,
        tol=1e-4,
    )
    assert valid, "La rama valida fue rechazada"

    expressions_bad = ["a", "a*b"]
    invalid = validate_branch(
        expressions=expressions_bad,
        param_names=PARAMETERS,
        X=X,
        Y=Y_dummy,
        equations=equations_sympy,
        variables=var_symbols,
        tol=1e-4,
    )
    assert not invalid, "La rama invalida fue aceptada"

    print("OK validate: acepta/rechaza ramas correctamente")


def main() -> int:
    parser = argparse.ArgumentParser(description="Chequeos modulares livianos")
    parser.add_argument(
        "--step",
        choices=["parser", "grid", "solver", "combine", "validate", "all"],
        default="all",
        help="Modulo a verificar",
    )
    args = parser.parse_args()

    checks: Dict[str, Callable[[], None]] = {
        "parser": check_parser,
        "grid": check_grid,
        "solver": check_solver,
        "combine": check_combine,
        "validate": check_validate,
    }

    if args.step == "all":
        order = ["parser", "grid", "solver", "combine", "validate"]
        for name in order:
            print(f"\n--- Ejecutando check: {name} ---")
            checks[name]()
        print("\nTodos los chequeos modulares terminaron correctamente.")
    else:
        print(f"--- Ejecutando check: {args.step} ---")
        checks[args.step]()
        print("Chequeo completado.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
