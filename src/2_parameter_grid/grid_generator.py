"""
Generación de grids de parámetros
"""
import numpy as np
from itertools import product
from typing import Dict, Tuple, List
from scipy.stats import qmc


def generate_grid(parameter_ranges: Dict[str, Tuple[float, float, int]], 
                  method: str = 'grid',
                  num_samples: int = 10000,
                  random_seed: int = 42) -> Tuple[np.ndarray, List[str]]:
    """
    Genera grid de parámetros.
    
    Args:
        parameter_ranges: Diccionario {param_name: (min, max, num_points)}
        method: 'grid', 'random', o 'lhs'
        num_samples: Número de muestras (para random/lhs)
        random_seed: Semilla aleatoria
    
    Returns:
        grid: Array (N, num_params) con las tuplas de parámetros
        param_names: Lista con nombres de parámetros en orden
    """
    np.random.seed(random_seed)
    
    param_names = list(parameter_ranges.keys())
    num_params = len(param_names)
    
    if method == 'grid':
        # Grid completo (producto cartesiano)
        ranges = []
        for param in param_names:
            min_val, max_val, num_points = parameter_ranges[param]
            ranges.append(np.linspace(min_val, max_val, num_points))
        
        # Producto cartesiano
        grid_points = list(product(*ranges))
        grid = np.array(grid_points)
        
        print(f"Grid completo generado: {len(grid)} tuplas")
        
    elif method == 'random':
        # Muestreo aleatorio uniforme
        grid = np.zeros((num_samples, num_params))
        for i, param in enumerate(param_names):
            min_val, max_val, _ = parameter_ranges[param]
            grid[:, i] = np.random.uniform(min_val, max_val, num_samples)
        
        print(f"Muestreo aleatorio: {num_samples} tuplas")
        
    elif method == 'lhs':
        # Latin Hypercube Sampling
        sampler = qmc.LatinHypercube(d=num_params, seed=random_seed)
        sample = sampler.random(n=num_samples)
        
        # Escalar a los rangos
        grid = np.zeros((num_samples, num_params))
        for i, param in enumerate(param_names):
            min_val, max_val, _ = parameter_ranges[param]
            grid[:, i] = min_val + sample[:, i] * (max_val - min_val)
        
        print(f"Latin Hypercube Sampling: {num_samples} tuplas")
    
    else:
        raise ValueError(f"Método desconocido: {method}")
    
    return grid, param_names


if __name__ == "__main__":
    from config import PARAMETER_RANGES, SAMPLING_METHOD, NUM_SAMPLES, RANDOM_SEED
    
    grid, names = generate_grid(
        PARAMETER_RANGES, 
        method=SAMPLING_METHOD,
        num_samples=NUM_SAMPLES,
        random_seed=RANDOM_SEED
    )
    
    print("=" * 60)
    print("GRID DE PARÁMETROS")
    print("=" * 60)
    print(f"Parámetros: {names}")
    print(f"Dimensiones del grid: {grid.shape}")
    print(f"Primeras 5 tuplas:")
    for i in range(min(5, len(grid))):
        print(f"  {dict(zip(names, grid[i]))}")
