# Tesis

Desarrollar y validar una metodología basada en regresión simbólica para determinar las expresiones analíticas de ecuaciones no lineales.

## Instalación

### Requisitos previos
- Python 3.12+
- Julia (requerido por PySR)

### Instalación de dependencias

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r src/requirements.txt
```

## Ejecución del Pipeline Principal

El pipeline descubre expresiones analíticas de ceros de ecuaciones mediante regresión simbólica.

### Configuración

Antes de ejecutar, edita `src/config.py` para definir:

```python
# Ecuación a resolver
EQUATION_STRING = "x + a - 2"  # f(x; params) = 0
VARIABLES = ["x"]
PARAMETERS = ["a"]

# Rangos de parámetros
PARAMETER_RANGES = {
    "a": (-5, 5, 50),  # (min, max, num_puntos)
}
```

### Ejecutar el pipeline

```bash
python src/main.py
```

Los resultados se guardan en `src/outputs_analytical/`.

## Benchmarks

El sistema incluye un conjunto de 43 casos de prueba organizados por categorías.

### Categorías disponibles

| Categoría | Casos | Descripción |
|-----------|-------|-------------|
| `linear` | 1-10 | Ecuaciones lineales |
| `quadratic` | 11-24 | Ecuaciones cuadráticas |
| `cubic` | 25-30 | Ecuaciones cúbicas |
| `quartic` | 31-34 | Ecuaciones cuárticas |
| `quintic` | 34 | Ecuaciones quínticas |
| `special` | 36-43 | Formas especiales |

### Dificultades

- `easy`: Casos simples
- `medium`: Complejidad intermedia
- `hard`: Casos complejos

### Comandos de Benchmark

#### Ejecutar todos los tests

```bash
python src/benchmark/run_benchmark.py
```

#### Ejecutar por categoría (grupo)

```bash
# Lineales
python src/benchmark/run_benchmark.py --category linear

# Cuadráticas
python src/benchmark/run_benchmark.py --category quadratic

# Cúbicas
python src/benchmark/run_benchmark.py --category cubic

# Cuárticas
python src/benchmark/run_benchmark.py --category quartic

# Quínticas
python src/benchmark/run_benchmark.py --category quintic

# Especiales
python src/benchmark/run_benchmark.py --category special
```

#### Ejecutar por dificultad

```bash
python src/benchmark/run_benchmark.py --difficulty easy
python src/benchmark/run_benchmark.py --difficulty medium
python src/benchmark/run_benchmark.py --difficulty hard
```

#### Combinar filtros

```bash
# Cuadráticas difíciles
python src/benchmark/run_benchmark.py --category quadratic --difficulty hard

# Lineales fáciles
python src/benchmark/run_benchmark.py --category linear --difficulty easy
```

#### Ejecutar caso específico

```bash
# Por nombre (búsqueda parcial)
python src/benchmark/run_benchmark.py --case linear_01
python src/benchmark/run_benchmark.py --case quadratic
```

#### Limitar número de casos

```bash
# Solo los primeros 5 casos
python src/benchmark/run_benchmark.py --max 5

# Primeros 3 casos cuadráticos
python src/benchmark/run_benchmark.py --category quadratic --max 3
```

#### Modo dry-run (ver sin ejecutar)

```bash
# Ver qué casos se ejecutarían
python src/benchmark/run_benchmark.py --category cubic --dry-run
```

#### Ejecutar por rango de índices (batches)

```bash
# Casos 1-10 (índices 0-9)
python src/benchmark/run_benchmark.py --from-index 0 --to-index 10

# Casos 11-20 (índices 10-19)
python src/benchmark/run_benchmark.py --from-index 10 --to-index 20
```

#### Especificar directorio de salida

```bash
python src/benchmark/run_benchmark.py --category linear --output ./mis_resultados
```

#### Ajustar iteraciones de PySR

```bash
python src/benchmark/run_benchmark.py --niterations 1000
```

### Ejecución por Batches (recomendado para RAM limitada)

Ejecuta el benchmark completo en procesos separados para liberar RAM entre batches:

```bash
cd src/benchmark
bash run_batches.sh
```

Este script:
1. Ejecuta cada categoría en un proceso independiente
2. Libera la RAM de Julia/PySR entre batches
3. Combina todos los resultados al final

### Combinar resultados de múltiples ejecuciones

```bash
python src/benchmark/run_benchmark.py --merge benchmark_results/batch_*
```

### Ver catálogo de casos

```bash
python src/benchmark/test_cases.py
```

## Estructura del Proyecto

```
src/
├── 1_equation_definition/   # Parsing de ecuaciones
├── 2_parameter_grid/        # Generación de grid de parámetros
├── 3_zero_finding/          # Resolución numérica/simbólica
├── 4_data_preparation/      # Agrupación de raíces por rama
├── 5_symbolic_regression/   # Regresión simbólica con PySR
├── 6_expression_builder/    # Construcción de expresiones finales
├── benchmark/               # Sistema de benchmarking
│   ├── run_benchmark.py     # Orquestador principal
│   ├── test_cases.py        # Catálogo de 43 casos de prueba
│   ├── runner.py            # Ejecutor de casos individuales
│   ├── metrics.py           # Cálculo de métricas
│   └── run_batches.sh       # Script para ejecución por batches
├── benchmark_results/       # Resultados de benchmarks
├── config.py                # Configuración del pipeline
├── main.py                  # Entrada principal
└── requirements.txt         # Dependencias
```

## Resultados

Los resultados de los benchmarks se guardan en `src/benchmark_results/` con:

- `raw_results.json` - Resultados crudos
- `evaluations.json` - Evaluaciones por caso
- `metrics.json` - Métricas globales
- `report.txt` - Reporte legible

## Opciones de Configuración

Las principales opciones en `src/config.py`:

| Opción | Descripción | Default |
|--------|-------------|---------|
| `NITERATIONS` | Iteraciones de PySR | 500 |
| `EPSILON` | Tolerancia de matcheo | 0.005 |
| `MIN_POINTS` | Mínimo puntos por rama | 5 |
| `SOLVER_METHOD` | Método de resolución | `'solve'` |
| `FILTER_COMPLEX` | Filtrar raíces complejas | `True` |
