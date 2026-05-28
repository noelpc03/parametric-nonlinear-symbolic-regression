# Benchmark Testing System

Sistema completo de pruebas para evaluar el pipeline de descubrimiento de raíces simbólicas. Ejecuta múltiples casos parametrizados de sistemas de ecuaciones, con soporte para múltiples ejecuciones por caso y estadísticas consolidadas.

## Estructura de carpetas

```
src/benchmark/
├── README.md                           # Este archivo
├── __init__.py                         # Inicializador del paquete Python
├── test_runner_v2.py                   # Orquestador principal (punto de entrada)
├── data_loader.py                      # Carga y valida casos desde JSON
├── runner.py                           # Ejecutor de un caso individual
├── metrics.py                          # Evaluador de resultados
├── data/
│   └── test_cases_sistemas.json        # 35 test cases (fuente de datos)
└── results/                            # Resultados de ejecuciones
    ├── test_runner_v2_20260515_143022/
    │   ├── consolidated_results.json
    │   ├── global_statistics.json
    │   └── report.txt
    └── ... (más carpetas de resultados)
```

## Archivos principales

### `test_runner_v2.py`
**Propósito:** Orquestador principal del benchmark.

**Características:**
- Carga casos desde JSON
- Ejecuta cada caso N veces configurables
- Consolida estadísticas (media, desv. est., min, max)
- Genera reportes con tablas formateadas
- Soporta filtros por ID o nombre
- Modo dry-run para previsualizar

**Uso:**
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json [OPTIONS]
```

### `data_loader.py`
**Propósito:** Carga, valida y gestiona los casos de prueba desde JSON.

**Funciones principales:**
- `load_test_cases(json_file)` - Carga todos los casos desde JSON
- `validate_test_case(case)` - Valida estructura de un caso
- `get_test_case_by_id(cases, id)` - Busca caso por ID (1-35)
- `get_test_case_by_name(cases, name)` - Busca caso por nombre
- `filter_by_id_range(cases, min_id, max_id)` - Filtra por rango de IDs
- `export_to_runner_format(case)` - Convierte a formato compatible con runner
- `get_statistics(cases)` - Genera estadísticas sobre casos

### `runner.py`
**Propósito:** Ejecuta el pipeline completo para un caso individual.

**Función principal:**
- `run_single_case(test_case, sr_config)` - Ejecuta caso a través de las 6 etapas del pipeline

**Pipeline (6 etapas):**
1. Parsear ecuaciones (SymPy)
2. Generar grid de parámetros
3. Resolver sistema para cada tupla de parámetros (scipy)
4. Agrupar soluciones por rama
5. Regresión simbólica (PySR - basado en Julia)
6. Comparar raíces descubiertas vs esperadas

### `metrics.py`
**Propósito:** Evalúa y compara resultados de ejecución.

**Funciones principales:**
- `_parse_expr()` - Parsea expresiones simbólicas
- `_expressions_equivalent()` - Verifica equivalencia numérica entre expresiones
- `evaluate_case()` - Compara resultado descubierto vs esperado

### `data/test_cases_sistemas.json`
**Propósito:** Base de datos de 35 casos de prueba.

**Estructura de cada caso:**
```json
{
  "id": 1,
  "name": "system_linear_01",
  "type": "system",
  "description": "2x2 linear system",
  "equations": ["x + y - a", "x - y - b"],
  "variables": ["x", "y"],
  "parameters": ["a", "b"],
  "parameter_ranges": {
    "a": [0.1, 3, 10],
    "b": [0.1, 3, 10]
  },
  "expected_solutions": [
    {
      "branch": 1,
      "x": "(a + b) / 2",
      "y": "(a - b) / 2"
    }
  ]
}
```

**Casos disponibles:**
- **IDs 1-5:** Sistemas lineales (easy, easy, easy, easy, medium)
- **IDs 6-15:** Sistemas cuadráticos (mixed difficulty)
- **IDs 16-20:** Sistemas cúbicos (mixed difficulty)
- **IDs 21-30:** Sistemas especiales (mixed difficulty)
- **IDs 31-35:** Sistemas trigonometricos/exp/mixed

## Comandos de uso

### 1. Ejecutar todos los 35 casos (5 ejecuciones cada uno - DEFAULT)
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json
```

### 2. Ejecutar un caso específico por ID
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --id 1
```

### 3. Ejecutar caso con número de ejecuciones personalizado
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --id 5 --runs 10
```

### 4. Ejecutar caso por nombre
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --name system_linear_01
```

### 5. Limitar a N primeros casos
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --max-cases 5
```

### 6. Aumentar número de ejecuciones globalmente
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --runs 20
```

### 7. Modo dry-run (solo listar sin ejecutar)
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --dry-run
```

### 8. Guardar en directorio específico
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json --output-dir mi_resultados
```

### 9. Combinaciones complejas
```bash
# ID 1, 7 ejecuciones, guardar resultados
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json \
  --id 1 --runs 7 --output-dir caso_1_resultados

# Primeros 10 casos, 3 ejecuciones cada uno
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json \
  --max-cases 10 --runs 3

# Casos 1-5 con dry-run
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json \
  --id 1 --max-cases 5 --dry-run
```

### 10. Ejecutar multiples IDs en una sola corrida
```bash
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json \
  --ids 14 20 25 --runs 3
```

## Argumentos disponibles

| Argumento | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `--cases` | str | (requerido) | Ruta al JSON de test cases |
| `--id` | int | None | Ejecutar solo caso con ID específico (1-35) |
| `--ids` | int | None | Ejecutar multiples IDs (ej: `--ids 14 20 25`) |
| `--name` | str | None | Ejecutar solo caso con nombre específico |
| `--runs` | int | 5 | Número de ejecuciones por caso |
| `--max-cases` | int | None | Máximo número de casos a ejecutar |
| `--dry-run` | flag | False | Solo listar, no ejecutar |
| `--output-dir` | str | (auto) | Directorio para guardar resultados |

## Formato de resultados

### Estructura de salida
```
results/test_runner_v2_YYYYMMDD_HHMMSS/
├── consolidated_results.json    # Todos los resultados consolidados
├── global_statistics.json       # Estadísticas globales del benchmark
└── report.txt                   # Reporte en formato texto
```

Nota: mientras el benchmark esta corriendo, el runner va actualizando
`consolidated_results.json` y `global_statistics.json` despues de cada corrida
individual y al finalizar cada caso.

### consolidated_results.json
Contiene por cada caso:
```json
{
  "case_id": 1,
  "case_name": "system_linear_01",
  "num_runs": 5,
  "success_rate": 0.8,
  "statistics": {
    "roots_matched": {
      "mean": 2.0,
      "std": 0.0,
      "min": 2,
      "max": 2
    },
    "coverage": {
      "mean": 0.95,
      "std": 0.02,
      "min": 0.93,
      "max": 0.97
    },
    "time_seconds": {
      "mean": 12.5,
      "std": 1.2,
      "min": 11.3,
      "max": 14.1
    }
  },
  "individual_runs": [ ... ]
}
```

### global_statistics.json
```json
{
  "total_cases": 5,
  "total_runs": 25,
  "total_time_seconds": 312.5,
  "avg_time_per_case": 62.5,
  "avg_success_rate": 0.82,
  "avg_coverage": 0.92
}
```

### report.txt
Formato legible:
```
TEST RUNNER V2 — 2026-05-15 16:30:45
======================================================================

Total de casos: 5
Total de ejecuciones: 25
Tiempo total: 312.5s
Tasa de éxito promedio: 82.0%
Cobertura promedio: 92.0%

 ID Nombre                           Éxito %  Cob. Med    Raíces    Tiempo
----------------------------------------------------------------------
  1 system_linear_01                  80.0%   95.0%   2.0s    12.5s
  2 system_linear_02                  80.0%   94.0%   2.0s    13.1s
  ...
```

## Flujo de ejecución

```
test_runner_v2.py (punto de entrada)
    ↓
parse_arguments() - procesa argumentos CLI
    ↓
data_loader.load_test_cases() - carga JSON
    ↓
apply_filters() - aplica --id, --name, --max-cases
    ↓
run_benchmark_suite() - orquestador
    ├─→ para cada caso:
    │   └─→ run_test_case_multiple_times()
    │       ├─→ N veces: runner.run_single_case()
    │       │   ├─→ equation_parser.parse_equation()
    │       │   ├─→ grid_generator.generate_grid()
    │       │   ├─→ solver.solve_for_all_parameter_tuples()
    │       │   ├─→ root_grouping.group_by_root_branch()
    │       │   ├─→ regression_adapter.run_for_all_branches()
    │       │   └─→ metrics.evaluate_case()
    │       └─→ consolida resultados (media, std, min, max)
    ├─→ calcula estadísticas globales
    └─→ retorna (all_results, global_stats)
    ↓
print_report() - imprime tablas en consola
    ↓
save_results() - guarda JSON + TXT
```

## Ejemplos prácticos

### Ejecutar primer caso 3 veces
```bash
python src/benchmark/test_runner_v2.py \
  --cases src/benchmark/data/test_cases_sistemas.json \
  --id 1 --runs 3
```

### Ejecutar primeros 5 casos 10 veces cada uno y guardar
```bash
python src/benchmark/test_runner_v2.py \
  --cases src/benchmark/data/test_cases_sistemas.json \
  --max-cases 5 --runs 10 \
  --output-dir resultados_inicio
```

### Previsualizar qué casos se ejecutarían (dry-run)
```bash
python src/benchmark/test_runner_v2.py \
  --cases src/benchmark/data/test_cases_sistemas.json \
  --max-cases 10 --dry-run
```

### Ejecutar caso específico por nombre
```bash
python src/benchmark/test_runner_v2.py \
  --cases src/benchmark/data/test_cases_sistemas.json \
  --name system_quadratic_05 --runs 5
```

## Archivos de datos

### test_cases_sistemas.json
- **Fuente:** Convertido de `casos_sistemas.txt` (raíz del proyecto)
- **Formatos de ecuaciones:** Compatibles con SymPy
  - Operadores: `+`, `-`, `*`, `/`, `**` (potencia)
  - Ejemplos: `x + y - a`, `x**2 - y**2 - (a - b)`
- **35 casos totales** distribuidos en categorías:
  - Lineales: IDs 1-5
  - Cuadráticos: IDs 6-15
  - Cúbicos: IDs 16-20
  - Especiales: IDs 21-30
  - Trig/Exp/Mixed: IDs 31-35

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'tqdm'`
**Solución:** Instala las dependencias del proyecto
```bash
pip install tqdm numpy scipy sympy
```

### Error: `FileNotFoundError: JSON file not found`
**Solución:** Verifica que uses la ruta correcta
```bash
# Incorrecto
python src/benchmark/test_runner_v2.py --cases data/test_cases_sistemas.json

# Correcto
python src/benchmark/test_runner_v2.py --cases src/benchmark/data/test_cases_sistemas.json
```

### Error: `Caso con ID X no encontrado`
**Solución:** Los IDs válidos son 1-35. Verifica el ID ingresado.

### Tiempo muy largo de ejecución
**Sugerencias:**
- Usa `--max-cases N` para limitar la cantidad
- Usa `--runs 1` para una sola ejecución por caso
- Usa `--dry-run` para verificar qué se ejecutará

## Desarrollo y extensión

### Agregar un nuevo caso
1. Edita `data/test_cases_sistemas.json`
2. Añade objeto en array `test_cases` con estructura correcta
3. Actualiza `metadata.total_cases`
4. Reinicia test_runner_v2

### Personalizar configuración de SR
Modifica `sr_config` en `test_runner_v2.py` antes de llamar `run_benchmark_suite()`.

### Integrar nuevas métricas
- Edita `metrics.py` para agregar funciones de evaluación
- Actualiza `run_single_case()` en `runner.py` para usar nuevas métricas

## Licencia y atribución

Parte del pipeline de tesis en Descubrimiento de Raíces Simbólicas.

---

**Última actualización:** Mayo 15, 2026
