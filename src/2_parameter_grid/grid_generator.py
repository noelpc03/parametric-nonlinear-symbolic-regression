"""
Generación de grids de parámetros mediante producto cartesiano.

Para cada parámetro se discretiza su rango en puntos equiespaciados
y se generan todas las combinaciones posibles (producto cartesiano).
"""
import numpy as np
from itertools import product
from typing import Dict, Tuple, List


def generate_grid(parameter_ranges: Dict[str, Tuple[float, float, int]]) -> Tuple[np.ndarray, List[str]]:
    """
    Genera grid de parámetros mediante producto cartesiano.

    Para cada parámetro divide el intervalo [min, max] en (num_points - 1)
    partes iguales, tomando los extremos y los puntos de corte.
    Luego genera todas las combinaciones posibles entre parámetros.

    Args:
        parameter_ranges: Diccionario {param_name: (min, max, num_points)}

    Returns:
        grid: Array (N, num_params) con las tuplas de parámetros
        param_names: Lista con nombres de parámetros en orden
    """
    param_names = list(parameter_ranges.keys())

    # Discretizar cada parámetro en puntos equiespaciados
    ranges = []
    for param in param_names:
        min_val, max_val, num_points = parameter_ranges[param]
        ranges.append(np.linspace(min_val, max_val, num_points))

    # Producto cartesiano de todos los rangos
    grid_points = list(product(*ranges))
    grid = np.array(grid_points)

    print(f"Grid generado: {len(grid)} tuplas (producto cartesiano)")

    return grid, param_names


if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from config import PARAMETER_RANGES

    grid, names = generate_grid(PARAMETER_RANGES)
    
    print("=" * 60)
    print("GRID DE PARÁMETROS")
    print("=" * 60)
    print(f"Parámetros: {names}")
    print(f"Dimensiones del grid: {grid.shape}")
    print(f"Primeras 5 tuplas:")
    for i in range(min(5, len(grid))):
        print(f"  {dict(zip(names, grid[i]))}")
