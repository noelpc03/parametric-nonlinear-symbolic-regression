# Sistema de Descubrimiento de Expresiones Analíticas

Sistema modular para descubrir expresiones analíticas de ceros de ecuaciones mediante regresión simbólica.

## Descripción

Este sistema toma una ecuación con parámetros, genera un grid de valores de parámetros, encuentra los ceros de la ecuación para cada combinación, y luego usa regresión simbólica para descubrir las expresiones analíticas de esas raíces en función de los parámetros.

## Pipeline

```
1. Definir ecuación f(x; a₁, a₂, ...) = 0
         ↓
2. Generar grid de parámetros (a₁, a₂, ...)
         ↓
3. Resolver f = 0 para cada tupla → obtener raíces x_i
         ↓
4. Agrupar raíces por rama (x₁, x₂, ...)
         ↓
5. Regresión simbólica: encontrar x_i = g(a₁, a₂, ...)
         ↓
6. Construir expresiones finales (Piecewise si necesario)
```

## Estructura del Proyecto

```
src/
├── main.py                          # Orquestador principal
├── config.py                        # Configuración global
├── requirements.txt                 # Dependencias
│
├── 1_equation_definition/           # Paso 1: Definir ecuación
│   ├── config.py                    # Ecuación, variables, parámetros
│   └── equation_parser.py           # Parser con SymPy
│
├── 2_parameter_grid/                # Paso 2: Generar grid
│   ├── config.py                    # Rangos y método de muestreo
│   └── grid_generator.py            # Generador de grids
│
├── 3_zero_finding/                  # Paso 3: Encontrar raíces
│   ├── config.py                    # Método de resolución
│   └── solver.py                    # Solver con SymPy
│
├── 4_data_preparation/              # Paso 4: Preparar datos
│   └── root_grouping.py             # Agrupación por rama
│
├── 5_symbolic_regression/           # Paso 5: Regresión
│   └── regression_adapter.py        # Adaptador para sistema existente
│
├── 6_expression_builder/            # Paso 6: Construir expresiones
│   └── piecewise_builder.py         # Constructor de Piecewise
│
└── symbolic_regression/             # Sistema de regresión (existente)
    ├── config.py
    ├── main.py
    ├── symbolic_regression.py
    ├── loss_functions.py
    ├── visualization.py
    └── ...
```

## Configuración

### 1. Definir la ecuación (1_equation_definition/config.py)

```python
EQUATION_STRING = "a*x**2 + b*x + c"  # Ecuación a resolver
VARIABLES = ["x"]                      # Variables (incógnitas)
PARAMETERS = ["a", "b", "c"]          # Parámetros
```

### 2. Configurar rangos de parámetros (2_parameter_grid/config.py)

```python
PARAMETER_RANGES = {
    "a": (-2, 2, 30),   # (min, max, num_puntos)
    "b": (-3, 3, 30),
    "c": (-1, 1, 30),
}

SAMPLING_METHOD = 'grid'  # 'grid', 'random', o 'lhs'
```

### 3. Configurar método de resolución (3_zero_finding/config.py)

```python
SOLVER_METHOD = 'solve'        # 'solve' o 'nsolve'
FILTER_COMPLEX = True          # Filtrar raíces complejas
SORT_ROOTS = True              # Ordenar raíces numéricamente
```

### 4. Configurar regresión simbólica (symbolic_regression/config.py)

```python
EPSILON = 0.05                 # Tolerancia para matcheo
K = 10                         # Pendiente sigmoidal
NITERATIONS = 50              # Iteraciones evolutivas
POPULATIONS = 10               # Poblaciones paralelas
```

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar pipeline completo
python main.py
```

Los resultados se guardan en `outputs_analytical/[experiment_name]_[timestamp]/`:
- `config.json`: Configuración usada
- `results_summary.json`: Resumen detallado
- `final_expressions.txt`: Expresiones descubiertas en texto legible

## Ejemplo: Ecuación Cuadrática

Para la ecuación $ax^2 + bx + c = 0$, el sistema debería descubrir las dos fórmulas de las raíces:

**Rama 1:**
```
x₁ = (-b - √(b² - 4ac)) / (2a)
```

**Rama 2:**
```
x₂ = (-b + √(b² - 4ac)) / (2a)
```

## Funciones Piecewise

Cuando el algoritmo iterativo de regresión simbólica encuentra múltiples funciones para una misma rama, el sistema construye expresiones Piecewise que unifican las funciones según las regiones del espacio de parámetros donde aplican.

## Documentación Adicional

- Ver `docs/sigmoide_vs_mse.md` para entender la función de pérdida sigmoidal
- Ver `symbolic_regression/README.md` para detalles del sistema de regresión

## Autor

Noel PC - Tesis de grado
