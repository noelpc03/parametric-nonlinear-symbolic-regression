"""
Módulo de visualización de resultados
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict

from config import (
    FIGURE_SIZE, POINT_SIZE_SCATTER, POINT_SIZE_MATCHED, 
    POINT_SIZE_UNMATCHED, LINE_WIDTH
)
from utils import print_results_summary


def visualize_results(X_original, y_original, results, epsilon=0.05):
    """
    Visualiza los resultados del algoritmo iterativo con dos gráficos:
    1. Todas las funciones y sus puntos matcheados
    2. Puntos matcheados por iteración
    
    Args:
        X_original: Datos originales X
        y_original: Datos originales y
        results: Lista de diccionarios con los resultados de cada iteración
        epsilon: Tolerancia utilizada (solo para referencia)
    """
    if len(results) == 0:
        print("No hay resultados para visualizar")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=FIGURE_SIZE)
    
    # Gráfico 1: Todos los puntos y todas las funciones
    plot_all_functions(axes[0], X_original, y_original, results)
    
    # Gráfico 2: Iteración por iteración
    plot_iteration_progress(axes[1], X_original, y_original, results)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir resumen
    print_results_summary(results)


def plot_all_functions(ax, X_original, y_original, results):
    """
    Grafica todas las funciones encontradas con sus puntos matcheados.
    
    Args:
        ax: Axes de matplotlib
        X_original: Datos originales X
        y_original: Datos originales y
        results: Lista de resultados
    """
    ax.scatter(X_original, y_original, s=POINT_SIZE_SCATTER, alpha=0.5, 
               c='gray', label='Todos los puntos')
    
    colors = plt.cm.rainbow(np.linspace(0, 1, len(results)))
    
    for i, result in enumerate(results):
        # Graficar la función
        X_plot = np.linspace(X_original.min(), X_original.max(), 500).reshape(-1, 1)
        y_plot = result['model'].predict(X_plot)
        ax.plot(X_plot, y_plot, color=colors[i], lw=LINE_WIDTH, 
                label=f"Función {i+1}")
        
        # Marcar los puntos matcheados
        ax.scatter(result['X_matched'], result['y_matched'], 
                  s=POINT_SIZE_MATCHED, color=colors[i], edgecolors='black', 
                  linewidths=1.5, marker='o', zorder=5)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Todas las funciones y sus puntos matcheados')
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_iteration_progress(ax, X_original, y_original, results):
    """
    Grafica el progreso del algoritmo iteración por iteración.
    
    Args:
        ax: Axes de matplotlib
        X_original: Datos originales X
        y_original: Datos originales y
        results: Lista de resultados
    """
    colors = plt.cm.rainbow(np.linspace(0, 1, len(results)))
    
    # Puntos no matcheados
    all_matched = np.concatenate([r['matched_indices'] for r in results])
    unmatched_mask = np.ones(len(X_original), dtype=bool)
    unmatched_mask[all_matched] = False
    
    if np.any(unmatched_mask):
        ax.scatter(X_original[unmatched_mask], y_original[unmatched_mask], 
                  s=POINT_SIZE_UNMATCHED, c='red', marker='x', 
                  label='Sin matchear', zorder=10)
    
    for i, result in enumerate(results):
        ax.scatter(result['X_matched'], result['y_matched'], 
                  s=POINT_SIZE_MATCHED, color=colors[i], edgecolors='black', 
                  linewidths=1.5, label=f"Iter {i+1}: {result['num_matched']} pts", 
                  zorder=5)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Puntos matcheados por iteración')
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_single_iteration(X, y, model, matched_indices, title="Resultado de iteración"):
    """
    Visualiza el resultado de una sola iteración.
    
    Args:
        X: Datos X
        y: Datos y
        model: Modelo entrenado
        matched_indices: Índices de puntos matcheados
        title: Título del gráfico
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Todos los puntos
    ax.scatter(X, y, s=30, alpha=0.5, c='gray', label='Todos los puntos')
    
    # Función encontrada
    X_plot = np.linspace(X.min(), X.max(), 500).reshape(-1, 1)
    y_plot = model.predict(X_plot)
    ax.plot(X_plot, y_plot, color='blue', lw=2, label='Función encontrada')
    
    # Puntos matcheados
    ax.scatter(X[matched_indices], y[matched_indices], 
              s=100, color='green', edgecolors='black', linewidths=1.5,
              marker='o', label=f'Matcheados ({len(matched_indices)})', zorder=5)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
