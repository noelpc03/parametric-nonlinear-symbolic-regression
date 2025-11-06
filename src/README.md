# Regresión Simbólica Iterativa

Proyecto de regresión simbólica que encuentra múltiples funciones para matchear diferentes subconjuntos de puntos de forma iterativa.

## 📁 Estructura del Proyecto

```
src/
├── main.py                    # Archivo principal para ejecutar el algoritmo
├── config.py                  # Configuración y parámetros
├── data_generator.py          # Generación de datos de ejemplo
├── loss_functions.py          # Funciones de pérdida personalizadas
├── symbolic_regression.py     # Algoritmo iterativo y entrenamiento
├── visualization.py           # Visualización de resultados
├── save_results.py            # Guardado de resultados y gráficas
├── utils.py                   # Funciones auxiliares
├── sigmoid_old.py             # Versión antigua (respaldo)
└── outputs/                   # Resultados guardados por timestamp
    └── 20251106_131149/
        ├── results.json
        ├── equations.txt
        ├── matched_points.csv
        ├── summary.txt
        ├── config_used.json
        ├── plots_combined.png
        ├── plot_all_functions.png
        └── plot_iterations.png
```

## 🚀 Uso

### Ejecución básica:

```bash
python main.py
```

### Personalización:

Modifica los parámetros en `config.py`:

- **Datos**: `NUM_POINTS`, `X_MIN`, `X_MAX`
- **Pérdida**: `EPSILON`, `K`
- **Modelo**: `NITERATIONS`, `POPULATIONS`, operadores
- **Algoritmo**: `MIN_POINTS`, `MAX_ITERATIONS`

## 📦 Módulos

### `config.py`
Contiene todos los parámetros configurables del proyecto.

### `data_generator.py`
- `generate_random_data()`: Genera datos con ruido aleatorio
- `generate_data_from_functions()`: Genera datos a partir de funciones conocidas

### `loss_functions.py`
- `sigmoid_loss()`: Función de pérdida sigmoidal en Python
- `get_julia_loss_function()`: Genera la función de pérdida para Julia/PySR

### `symbolic_regression.py`
- `train_symbolic_model()`: Entrena un modelo PySR individual
- `iterative_symbolic_regression()`: Algoritmo principal iterativo

### `visualization.py`
- `visualize_results()`: Visualización completa con dos gráficos
- `plot_all_functions()`: Gráfico de todas las funciones
- `plot_iteration_progress()`: Gráfico del progreso por iteración
- `plot_single_iteration()`: Gráfico de una iteración individual

### `save_results.py`
- `save_all_results()`: Guarda todos los resultados en un directorio con timestamp
- `save_results_json()`: Guarda resultados en formato JSON
- `save_equations_txt()`: Guarda ecuaciones en texto legible
- `save_matched_points_csv()`: Guarda tabla de puntos matcheados
- `save_summary_txt()`: Guarda resumen del experimento
- `save_config_json()`: Guarda la configuración utilizada
- `save_plots()`: Guarda las gráficas en PNG

### `utils.py`
Funciones auxiliares para identificación de puntos y formateo de salida.

## 🔄 Algoritmo

1. **Generación de datos**: Crea conjunto inicial de puntos
2. **Iteración**:
   - Entrena modelo de regresión simbólica
   - Identifica puntos matcheados (|y - ŷ| < ε)
   - Guarda función y puntos matcheados
   - Elimina puntos matcheados del conjunto
3. **Repetición**: Continúa hasta que no queden puntos o no se puedan matchear más
4. **Visualización**: Muestra todas las funciones encontradas y sus puntos

## 📊 Salida

El algoritmo genera automáticamente un directorio con timestamp en `outputs/` que contiene:

### Archivos generados:
- **`results.json`**: Todas las funciones encontradas con sus metadatos en formato JSON
- **`equations.txt`**: Lista legible de todas las ecuaciones encontradas
- **`matched_points.csv`**: Tabla con todos los puntos y qué función los matcheó
- **`summary.txt`**: Resumen estadístico del experimento (puntos matcheados, iteraciones, etc.)
- **`config_used.json`**: Configuración de parámetros utilizada en esta ejecución
- **`plots_combined.png`**: Ambas gráficas en una sola imagen
- **`plot_all_functions.png`**: Todas las funciones superpuestas con puntos matcheados
- **`plot_iterations.png`**: Distribución de puntos por iteración

### Visualización interactiva:
- Muestra las gráficas en ventanas de matplotlib para análisis en tiempo real
- Imprime progreso de cada iteración en consola
- Resume total de funciones y puntos matcheados
