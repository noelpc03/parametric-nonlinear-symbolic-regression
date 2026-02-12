"""
Archivo principal para ejecutar el algoritmo de regresión simbólica iterativa
"""
from data_generator import generate_random_data
from symbolic_regression import iterative_symbolic_regression
from visualization import visualize_results
from save_results import save_all_results
from config import EPSILON, K, NITERATIONS, MIN_POINTS, MAX_ITERATIONS


def main():
    """
    Función principal que ejecuta el algoritmo completo.
    """
    # 1. Generar datos
    print("Generando datos...")
    X, y = generate_random_data()
    print(f"Datos generados: {len(X)} puntos\n")
    
    # 2. Ejecutar algoritmo iterativo de regresión simbólica
    results = iterative_symbolic_regression(
        X, y,
        epsilon=EPSILON,
        k=K,
        niterations=NITERATIONS,
        min_points=MIN_POINTS,
        max_iterations=MAX_ITERATIONS
    )
    
    # 3. Guardar resultados
    if len(results) > 0:
        output_dir = save_all_results(results, X, y)
        
        # 4. Visualizar resultados (mostrar gráficas interactivas)
        print("\nGenerando visualizaciones interactivas...")
        visualize_results(X, y, results, epsilon=EPSILON)
    else:
        print("\nNo se encontraron funciones. No hay nada que visualizar.")


if __name__ == "__main__":
    main()
