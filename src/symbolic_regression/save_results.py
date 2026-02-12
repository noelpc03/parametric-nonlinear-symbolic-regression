"""
Módulo para guardar los resultados del algoritmo de regresión simbólica iterativa
"""
import os
import json
import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import shutil

from config import *


def create_output_directory(base_dir="outputs"):
    """
    Crea un directorio con timestamp para guardar los resultados.
    
    Args:
        base_dir: Directorio base donde crear la carpeta
    
    Returns:
        str: Ruta completa al directorio creado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def save_results_json(results, output_dir):
    """
    Guarda los resultados en formato JSON con funciones y sus puntos matcheados.
    
    Args:
        results: Lista de diccionarios con los resultados
        output_dir: Directorio donde guardar el archivo
    """
    # Convertir los resultados a un formato serializable con puntos
    serializable_results = []
    
    for result in results:
        # Crear lista de puntos matcheados para esta función
        matched_points = []
        for i in range(len(result['matched_indices'])):
            point = {
                'index': int(result['matched_indices'][i]),
                'x': float(result['X_matched'][i]),
                'y': float(result['y_matched'][i])
            }
            matched_points.append(point)
        
        serializable_result = {
            'iteration': int(result['iteration']),
            'equation': str(result['equation']),  # Asegurar que sea string
            'num_matched': int(result['num_matched']),
            'matched_points': matched_points
        }
        serializable_results.append(serializable_result)
    
    filepath = os.path.join(output_dir, "results.json")
    with open(filepath, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"✓ Resultados guardados en: {filepath}")


def save_equations_txt(results, output_dir):
    """
    Guarda las ecuaciones en un archivo de texto legible con sus puntos.
    
    Args:
        results: Lista de diccionarios con los resultados
        output_dir: Directorio donde guardar el archivo
    """
    filepath = os.path.join(output_dir, "equations.txt")
    
    with open(filepath, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("ECUACIONES ENCONTRADAS CON SUS PUNTOS MATCHEADOS\n")
        f.write("=" * 70 + "\n\n")
        
        for result in results:
            # La ecuación ya viene como string limpio desde symbolic_regression.py
            equation_str = result['equation']
            
            f.write(f"Iteración {result['iteration']}:\n")
            f.write(f"  Ecuación: {equation_str}\n")
            f.write(f"  Puntos matcheados: {result['num_matched']}\n")
            f.write(f"  Índices: {result['matched_indices'].tolist()}\n\n")
            
            # Agregar tabla de puntos matcheados
            f.write(f"  Puntos (x, y):\n")
            for i in range(len(result['matched_indices'])):
                idx = result['matched_indices'][i]
                x_val = result['X_matched'][i].flatten()[0] if result['X_matched'][i].ndim > 0 else result['X_matched'][i]
                y_val = result['y_matched'][i]
                f.write(f"    [{idx:3d}] x={x_val:8.4f}, y={y_val:8.4f}\n")
            
            f.write("\n" + "-" * 70 + "\n\n")
    
    print(f"✓ Ecuaciones guardadas en: {filepath}")


def save_matched_points_csv(results, X_original, y_original, output_dir):
    """
    Guarda una tabla CSV con todos los puntos y qué función los matcheó.
    
    Args:
        results: Lista de diccionarios con los resultados
        X_original: Array con los valores X originales
        y_original: Array con los valores y originales
        output_dir: Directorio donde guardar el archivo
    """
    filepath = os.path.join(output_dir, "matched_points.csv")
    
    # Crear un diccionario que mapea índice de punto -> iteración y ecuación
    point_mapping = {}
    for result in results:
        for idx in result['matched_indices']:
            point_mapping[idx] = {
                'iteration': result['iteration'],
                'equation': result['equation']
            }
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['point_id', 'x', 'y', 'iteration', 'matched', 'equation'])
        
        for i in range(len(X_original)):
            x_val = float(X_original[i])
            y_val = float(y_original[i])
            
            if i in point_mapping:
                iteration = point_mapping[i]['iteration']
                equation = point_mapping[i]['equation']
                matched = 'Yes'
            else:
                iteration = ''
                equation = ''
                matched = 'No'
            
            writer.writerow([i, x_val, y_val, iteration, matched, equation])
    
    print(f"✓ Puntos guardados en: {filepath}")


def save_summary_txt(results, X_original, output_dir, config_params=None):
    """
    Guarda un resumen textual del experimento.
    
    Args:
        results: Lista de diccionarios con los resultados
        X_original: Array con los valores X originales
        output_dir: Directorio donde guardar el archivo
        config_params: Diccionario con los parámetros de configuración usados
    """
    filepath = os.path.join(output_dir, "summary.txt")
    
    total_matched = sum(r['num_matched'] for r in results)
    total_points = len(X_original)
    
    with open(filepath, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("RESUMEN DEL EXPERIMENTO\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("ESTADÍSTICAS:\n")
        f.write(f"  Total de puntos: {total_points}\n")
        f.write(f"  Puntos matcheados: {total_matched}\n")
        f.write(f"  Puntos sin matchear: {total_points - total_matched}\n")
        f.write(f"  Porcentaje matcheado: {100 * total_matched / total_points:.2f}%\n")
        f.write(f"  Número de iteraciones: {len(results)}\n")
        f.write(f"  Número de funciones encontradas: {len(results)}\n\n")
        
        if config_params:
            f.write("PARÁMETROS UTILIZADOS:\n")
            for key, value in config_params.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
        
        f.write("DISTRIBUCIÓN DE PUNTOS POR ITERACIÓN:\n")
        for result in results:
            f.write(f"  Iteración {result['iteration']}: {result['num_matched']} puntos\n")
        f.write("\n")
        
        f.write("=" * 70 + "\n")
    
    print(f"✓ Resumen guardado en: {filepath}")


def save_config_json(output_dir):
    """
    Guarda la configuración utilizada en el experimento.
    
    Args:
        output_dir: Directorio donde guardar el archivo
    """
    config_dict = {
        'DATA_SEED': DATA_SEED,
        'X_MIN': X_MIN,
        'X_MAX': X_MAX,
        'NUM_POINTS': NUM_POINTS,
        'EPSILON': EPSILON,
        'K': K,
        'NITERATIONS': NITERATIONS,
        'POPULATIONS': POPULATIONS,
        'UNARY_OPERATORS': UNARY_OPERATORS,
        'BINARY_OPERATORS': BINARY_OPERATORS,
        'MIN_POINTS': MIN_POINTS,
        'MAX_ITERATIONS': MAX_ITERATIONS,
        'MAX_CONSECUTIVE_NO_MATCH': MAX_CONSECUTIVE_NO_MATCH,
    }
    
    filepath = os.path.join(output_dir, "config_used.json")
    with open(filepath, 'w') as f:
        json.dump(config_dict, f, indent=2)
    
    print(f"✓ Configuración guardada en: {filepath}")


def save_individual_function_plots(results, X_original, y_original, output_dir):
    """
    Guarda una imagen PNG individual para cada función/iteración.
    
    Args:
        results: Lista de diccionarios con los resultados
        X_original: Array con los valores X originales
        y_original: Array con los valores y originales
        output_dir: Directorio donde guardar las imágenes
    """
    # Crear subdirectorio para las funciones individuales
    individual_dir = os.path.join(output_dir, "individual_functions")
    os.makedirs(individual_dir, exist_ok=True)
    
    for result in results:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Todos los puntos originales en gris claro
        ax.scatter(X_original, y_original, s=30, alpha=0.3, c='lightgray', 
                  label='Otros puntos', zorder=1)
        
        # La función encontrada
        X_plot = np.linspace(X_original.min(), X_original.max(), 500).reshape(-1, 1)
        y_plot = result['model'].predict(X_plot)
        ax.plot(X_plot, y_plot, color='blue', lw=2, 
               label=f'Función encontrada', zorder=3)
        
        # Puntos matcheados por esta función
        ax.scatter(result['X_matched'], result['y_matched'], 
                  s=100, color='red', edgecolors='black', linewidths=1.5,
                  marker='o', label=f'Puntos matcheados ({result["num_matched"]})', 
                  zorder=5)
        
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title(f'Iteración {result["iteration"]} - {result["num_matched"]} puntos matcheados\n{result["equation"]}', 
                    fontsize=10, wrap=True)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Guardar figura
        filename = f"function_iter_{result['iteration']:02d}.png"
        filepath = os.path.join(individual_dir, filename)
        plt.savefig(filepath, dpi=200, bbox_inches='tight')
        plt.close(fig)
    
    print(f"✓ {len(results)} gráficas individuales guardadas en: {individual_dir}/")


def save_plots(X_original, y_original, results, output_dir, epsilon=EPSILON):
    """
    Guarda las gráficas en archivos PNG.
    
    Args:
        X_original: Array con los valores X originales
        y_original: Array con los valores y originales
        results: Lista de diccionarios con los resultados
        output_dir: Directorio donde guardar las imágenes
        epsilon: Tolerancia utilizada
    """
    from visualization import plot_all_functions, plot_iteration_progress
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfico 1: Todas las funciones
    plot_all_functions(axes[0], X_original, y_original, results)
    
    # Gráfico 2: Progreso por iteración
    plot_iteration_progress(axes[1], X_original, y_original, results)
    
    plt.tight_layout()
    
    # Guardar la figura combinada
    filepath_combined = os.path.join(output_dir, "plots_combined.png")
    plt.savefig(filepath_combined, dpi=300, bbox_inches='tight')
    print(f"✓ Gráficas combinadas guardadas en: {filepath_combined}")
    
    # Guardar gráficas individuales principales
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    plot_all_functions(ax1, X_original, y_original, results)
    filepath1 = os.path.join(output_dir, "plot_all_functions.png")
    plt.savefig(filepath1, dpi=300, bbox_inches='tight')
    plt.close(fig1)
    print(f"✓ Gráfica 1 guardada en: {filepath1}")
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    plot_iteration_progress(ax2, X_original, y_original, results)
    filepath2 = os.path.join(output_dir, "plot_iterations.png")
    plt.savefig(filepath2, dpi=300, bbox_inches='tight')
    plt.close(fig2)
    print(f"✓ Gráfica 2 guardada en: {filepath2}")
    
    # Cerrar la figura combinada
    plt.close(fig)
    
    # Guardar gráficas individuales por función
    save_individual_function_plots(results, X_original, y_original, output_dir)


def save_all_results(results, X_original, y_original, output_dir=None):
    """
    Guarda todos los resultados del experimento.
    
    Args:
        results: Lista de diccionarios con los resultados
        X_original: Array con los valores X originales
        y_original: Array con los valores y originales
        output_dir: Directorio donde guardar (si None, se crea uno nuevo)
    
    Returns:
        str: Ruta al directorio donde se guardaron los resultados
    """
    if output_dir is None:
        output_dir = create_output_directory()
    
    print("\n" + "=" * 70)
    print("GUARDANDO RESULTADOS")
    print("=" * 70 + "\n")
    
    # Guardar todos los archivos
    save_results_json(results, output_dir)
    save_equations_txt(results, output_dir)
    save_matched_points_csv(results, X_original, y_original, output_dir)
    
    # Preparar parámetros de configuración para el resumen
    config_params = {
        'EPSILON': EPSILON,
        'K': K,
        'NITERATIONS': NITERATIONS,
        'NUM_POINTS': NUM_POINTS,
        'MIN_POINTS': MIN_POINTS,
    }
    save_summary_txt(results, X_original, output_dir, config_params)
    save_config_json(output_dir)
    save_plots(X_original, y_original, results, output_dir)
    
    print("\n" + "=" * 70)
    print(f"✓ TODOS LOS RESULTADOS GUARDADOS EN: {output_dir}")
    print("=" * 70 + "\n")
    
    return output_dir
