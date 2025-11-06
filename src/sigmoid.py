import numpy as np
from pysr import PySRRegressor
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import copy

# ----------------------------
# 1. Generamos datos de ejemplo
# ----------------------------
np.random.seed(0)
X_original = np.linspace(-3, 3, 100).reshape(-1, 1)

# Generamos y como ruido puro (sin ninguna función subyacente)
y_original = np.random.randn(len(X_original))

# ---------------------------------
# 2. Definimos la pérdida sigmoidal
# ---------------------------------
def sigmoid_loss(y_true, y_pred, epsilon=0.1, k=10):
    """
    Pérdida suave basada en una sigmoide.
    Cuanto más cerca está el punto (|y - f(x)| <= ε), menor penalización.
    """
    diff = np.abs(y_true - y_pred)
    penalties = 1 / (1 + np.exp(-k * (epsilon - diff)))
    return 1 - np.mean(penalties)

# -----------------------------------------
# 3. Función para identificar puntos matcheados
# -----------------------------------------
def find_matched_points(X, y, y_pred, epsilon=0.05):
    """
    Identifica los índices de los puntos que son matcheados por la función.
    Un punto es matcheado si |y - y_pred| < epsilon
    """
    diff = np.abs(y - y_pred)
    matched_indices = np.where(diff < epsilon)[0]
    return matched_indices

# -----------------------------------------
# 4. Función para entrenar un modelo de regresión simbólica
# -----------------------------------------
def train_symbolic_model(X, y, k=10, epsilon=0.05, niterations=100):
    """
    Entrena un modelo de regresión simbólica con la función de pérdida sigmoidal
    """
    loss_function = f"sigmoid_loss(prediction, target) = 1 / (1 + exp(-{k} * (abs(target - prediction) - {epsilon})))"
    
    model = PySRRegressor(
        niterations=niterations,
        populations=4,
        elementwise_loss=loss_function,
        model_selection="best",
        variable_names=["x"],
        unary_operators=["sin", "cos", "exp", "log"],
        binary_operators=["+", "-", "*", "/"],
    )
    
    model.fit(X, y)
    return model

# -----------------------------------------
# 5. Algoritmo iterativo principal
# -----------------------------------------
def iterative_symbolic_regression(X, y, epsilon=0.05, k=10, niterations=100, min_points=1, max_iterations=None):
    """
    Algoritmo iterativo de regresión simbólica:
    1. Encuentra una función que matchee la mayor cantidad de puntos
    2. Elimina esos puntos del conjunto
    3. Repite hasta que no queden puntos o no se puedan matchear más
    
    Args:
        X: datos de entrada (shape: (n, 1))
        y: datos de salida (shape: (n,))
        epsilon: tolerancia para considerar un punto como "matcheado"
        k: pendiente de la sigmoide
        niterations: número de iteraciones para cada modelo
        min_points: número mínimo de puntos para continuar el proceso (default: 1, procesa hasta el último punto)
        max_iterations: número máximo de iteraciones del algoritmo completo (None = sin límite)
    
    Returns:
        List[Dict]: Lista de diccionarios, cada uno con:
            - 'model': el modelo entrenado
            - 'equation': la ecuación simbólica
            - 'matched_indices': índices de los puntos matcheados (en el conjunto original)
            - 'X_matched': coordenadas X de los puntos matcheados
            - 'y_matched': coordenadas y de los puntos matcheados
            - 'num_matched': número de puntos matcheados
    """
    results = []
    
    # Creamos una copia de los datos para ir eliminando puntos
    X_remaining = X.copy()
    y_remaining = y.copy()
    
    # Mantenemos un mapeo de índices al conjunto original
    original_indices = np.arange(len(X))
    
    iteration = 0
    consecutive_no_match = 0  # Contador de iteraciones sin matcheos
    max_consecutive_no_match = 3  # Máximo de intentos sin matchear antes de detenerse
    
    print("=" * 60)
    print("Iniciando algoritmo iterativo de regresión simbólica")
    print("=" * 60)
    
    while len(X_remaining) >= min_points:
        iteration += 1
        
        # Verificar si alcanzamos el máximo de iteraciones
        if max_iterations is not None and iteration > max_iterations:
            print(f"\n⚠️  Se alcanzó el número máximo de iteraciones ({max_iterations})")
            break
        
        print(f"\n--- Iteración {iteration} ---")
        print(f"Puntos restantes: {len(X_remaining)}")
        
        # Entrenar modelo con los puntos restantes
        model = train_symbolic_model(X_remaining, y_remaining, k=k, epsilon=epsilon, niterations=niterations)
        
        # Obtener predicciones
        y_pred = model.predict(X_remaining)
        
        # Identificar puntos matcheados
        matched_indices_local = find_matched_points(X_remaining, y_remaining, y_pred, epsilon=epsilon)
        
        if len(matched_indices_local) == 0:
            consecutive_no_match += 1
            print(f"⚠️  No se encontraron puntos matcheados en la iteración {iteration}")
            
            if consecutive_no_match >= max_consecutive_no_match:
                print(f"⚠️  No se encontraron puntos matcheados en {max_consecutive_no_match} iteraciones consecutivas.")
                print("Deteniendo el algoritmo.")
                break
            else:
                print(f"Reintentando... ({consecutive_no_match}/{max_consecutive_no_match})")
                continue
        
        # Reiniciar contador si hubo matcheo
        consecutive_no_match = 0
        
        # Mapear índices locales a índices originales
        matched_indices_original = original_indices[matched_indices_local]
        
        # Obtener la ecuación
        equation = model.get_best()
        
        # Guardar resultados
        result = {
            'iteration': iteration,
            'model': model,
            'equation': str(equation),
            'matched_indices': matched_indices_original,
            'X_matched': X[matched_indices_original],
            'y_matched': y[matched_indices_original],
            'num_matched': len(matched_indices_original)
        }
        results.append(result)
        
        print(f"✓ Ecuación encontrada: {equation}")
        print(f"✓ Puntos matcheados: {len(matched_indices_original)}")
        
        # Eliminar puntos matcheados del conjunto restante
        mask = np.ones(len(X_remaining), dtype=bool)
        mask[matched_indices_local] = False
        
        X_remaining = X_remaining[mask]
        y_remaining = y_remaining[mask]
        original_indices = original_indices[mask]
    
    # Mensaje final
    if len(X_remaining) > 0:
        print(f"\n⚠️  Quedan {len(X_remaining)} puntos sin matchear")
        print(f"Índices de puntos sin matchear: {original_indices}")
    else:
        print(f"\n✓ ¡Todos los puntos han sido matcheados!")
    
    print("\n" + "=" * 60)
    print(f"Proceso completado: {len(results)} funciones encontradas")
    print(f"Total de puntos matcheados: {sum(r['num_matched'] for r in results)}/{len(X)}")
    print("=" * 60)
    
    return results

# -----------------------------------------
# 6. Función de visualización
# -----------------------------------------
def visualize_results(X_original, y_original, results, epsilon=0.05):
    """
    Visualiza los resultados del algoritmo iterativo
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfico 1: Todos los puntos y todas las funciones
    ax1 = axes[0]
    ax1.scatter(X_original, y_original, s=30, alpha=0.5, c='gray', label='Todos los puntos')
    
    colors = plt.cm.rainbow(np.linspace(0, 1, len(results)))
    
    for i, result in enumerate(results):
        # Graficar la función
        X_plot = np.linspace(X_original.min(), X_original.max(), 500).reshape(-1, 1)
        y_plot = result['model'].predict(X_plot)
        ax1.plot(X_plot, y_plot, color=colors[i], lw=2, label=f"Función {i+1}")
        
        # Marcar los puntos matcheados
        ax1.scatter(result['X_matched'], result['y_matched'], 
                   s=100, color=colors[i], edgecolors='black', linewidths=1.5, 
                   marker='o', zorder=5)
    
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_title('Todas las funciones y sus puntos matcheados')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Iteración por iteración
    ax2 = axes[1]
    
    # Puntos no matcheados todavía
    all_matched = np.concatenate([r['matched_indices'] for r in results])
    unmached_mask = np.ones(len(X_original), dtype=bool)
    unmached_mask[all_matched] = False
    
    if np.any(unmached_mask):
        ax2.scatter(X_original[unmached_mask], y_original[unmached_mask], 
                   s=50, c='red', marker='x', label='Sin matchear', zorder=10)
    
    for i, result in enumerate(results):
        ax2.scatter(result['X_matched'], result['y_matched'], 
                   s=100, color=colors[i], edgecolors='black', linewidths=1.5,
                   label=f"Iter {i+1}: {result['num_matched']} pts", zorder=5)
    
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.set_title('Puntos matcheados por iteración')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    for i, result in enumerate(results):
        print(f"\nIteración {i+1}:")
        print(f"  Ecuación: {result['equation']}")
        print(f"  Puntos matcheados: {result['num_matched']}")
        print(f"  Índices: {result['matched_indices'][:10]}..." if len(result['matched_indices']) > 10 else f"  Índices: {result['matched_indices']}")

# -----------------------------------------
# 7. Ejecutar el algoritmo
# -----------------------------------------
if __name__ == "__main__":
    # Parámetros
    epsilon = 0.05  # Tolerancia para matcheo
    k = 10  # Pendiente de la sigmoide
    niterations = 50  # Iteraciones por modelo (reducido para hacer pruebas más rápidas)
    min_points = 1  # Mínimo de puntos para continuar (1 = procesa hasta el último punto)
    
    # Ejecutar algoritmo iterativo
    results = iterative_symbolic_regression(
        X_original, 
        y_original, 
        epsilon=epsilon, 
        k=k, 
        niterations=niterations,
        min_points=min_points
    )
    
    # Visualizar resultados
    visualize_results(X_original, y_original, results, epsilon=epsilon)
