# Tesis

Metodologia para descubrir expresiones analiticas de ceros de ecuaciones no lineales usando regresion simbolica con PySR.

## 1. Requisitos

- Python 3.12 o superior
- Julia (recomendado 1.10 o superior)
- Git (opcional, para clonar el repo)

## 2. Instalacion portable (cualquier computadora)

### 2.1 Clonar y entrar al proyecto

```bash
git clone <URL_DEL_REPO>
cd Tesis
```

### 2.2 Crear y activar entorno virtual

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

Windows CMD:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

### 2.3 Instalar Julia (necesario para PySR)

1. Instalar Julia desde su instalador oficial.
2. Verificar que el comando julia quede en PATH.

```bash
julia --version
```

3. Verificar integracion Python + PySR:

```bash
python -c "import pysr; print('PySR OK')"
```

Notas:
- En la primera corrida PySR puede demorar bastante porque Julia compila y descarga dependencias.
- Si julia no se reconoce, cerrar y abrir la terminal luego de instalar Julia.

## 3. Configuracion del pipeline principal

Editar src/config.py y ajustar, como minimo:

```python
EQUATION_STRING = "(x - a) * (x + a)"
VARIABLES = ["x"]
PARAMETERS = ["a"]

PARAMETER_RANGES = {
        "a": (0.1, 5, 50),
}
```

Opciones clave de ejecucion:

- SR_INPUT_MODE:
    - "combined": usa todos los pares (params, root) juntos y descubre ecuaciones iterativamente.
    - "branches": separa por ramas antes de la regresion simbolica.
- Modo de perdida:
    - MSE: USE_SIGMOID_LOSS=False y USE_MATCH_COUNT_LOSS=False
    - Match count: USE_MATCH_COUNT_LOSS=True
    - Sigmoid: USE_SIGMOID_LOSS=True

Regla importante:
- USE_SIGMOID_LOSS y USE_MATCH_COUNT_LOSS no pueden ser True al mismo tiempo.

## 4. Ejecutar un caso normal con main

Desde la raiz del proyecto:

```bash
python src/main.py
```

Comportamiento actual:
- src/main.py respeta SR_INPUT_MODE definido en src/config.py.
- Imprime el modo activo al inicio: Modo de entrada SR: combined o branches.

Salida:
- Se guarda en OUTPUT_DIR/<EXPERIMENT_NAME>_<timestamp>
- Por default: outputs_analytical/<experimento_timestamp>

Archivos generados tipicos:
- config.json
- results_summary.json
- final_expressions.txt

### 4.1 Ejecutar el mismo caso en los 3 modos de perdida

Para cada corrida, cambia estas banderas en src/config.py y vuelve a ejecutar:

```bash
python src/main.py
```

MSE:
- USE_SIGMOID_LOSS=False
- USE_MATCH_COUNT_LOSS=False

Match count:
- USE_SIGMOID_LOSS=False
- USE_MATCH_COUNT_LOSS=True

Sigmoid:
- USE_SIGMOID_LOSS=True
- USE_MATCH_COUNT_LOSS=False

## 5. Benchmarks (todas las formas de ejecucion)

Script principal:

```bash
python src/benchmark/run_benchmark.py
```

Nota:
- El benchmark usa SR_INPUT_MODE desde src/config.py (igual que main).

### 5.1 Ejecutar todo el benchmark

```bash
python src/benchmark/run_benchmark.py
```

### 5.2 Filtrar por categoria

Categorias validas: linear, quadratic, cubic, quartic, quintic, special

```bash
python src/benchmark/run_benchmark.py --category linear
python src/benchmark/run_benchmark.py --category quadratic
python src/benchmark/run_benchmark.py --category cubic
python src/benchmark/run_benchmark.py --category quartic
python src/benchmark/run_benchmark.py --category quintic
python src/benchmark/run_benchmark.py --category special
```

### 5.3 Filtrar por dificultad

Dificultades validas: easy, medium, hard

```bash
python src/benchmark/run_benchmark.py --difficulty easy
python src/benchmark/run_benchmark.py --difficulty medium
python src/benchmark/run_benchmark.py --difficulty hard
```

### 5.4 Combinar filtros

```bash
python src/benchmark/run_benchmark.py --category quadratic --difficulty hard
python src/benchmark/run_benchmark.py --category linear --difficulty easy
```

### 5.5 Ejecutar por nombre de caso

Busqueda parcial por nombre:

```bash
python src/benchmark/run_benchmark.py --case linear_01
python src/benchmark/run_benchmark.py --case quadratic
```

### 5.6 Limitar cantidad de casos

```bash
python src/benchmark/run_benchmark.py --max 5
python src/benchmark/run_benchmark.py --category quadratic --max 3
```

### 5.7 Dry run (solo listar)

```bash
python src/benchmark/run_benchmark.py --dry-run
python src/benchmark/run_benchmark.py --category cubic --dry-run
```

### 5.8 Ejecutar por rango de indices

Los indices son 0-based e incluyen from-index, excluyen to-index.

```bash
python src/benchmark/run_benchmark.py --from-index 0 --to-index 10
python src/benchmark/run_benchmark.py --from-index 10 --to-index 20
```

### 5.9 Cambiar directorio de salida

```bash
python src/benchmark/run_benchmark.py --output ./mis_resultados
python src/benchmark/run_benchmark.py --category linear --output ./mis_resultados/linear
```

### 5.10 Override de iteraciones PySR

```bash
python src/benchmark/run_benchmark.py --niterations 1000
```

### 5.11 Ejecutar por batches (recomendado para RAM limitada)

Linux/macOS (bash):

```bash
cd src/benchmark
bash run_batches.sh
```

Esto ejecuta batches en procesos separados para liberar RAM entre tandas y al final combina resultados.

### 5.12 Combinar resultados de ejecuciones previas

```bash
python src/benchmark/run_benchmark.py --merge src/benchmark_results/batches_*/batch_* --output ./benchmark_merge
```

### 5.13 Ver catalogo de casos

```bash
python src/benchmark/test_cases.py
```

## 6. Resultados del benchmark

Por default se guardan en src/benchmark_results/benchmark_<timestamp>/

Archivos principales:
- raw_results.json
- evaluations.json
- metrics.json
- report.txt

## 7. Estructura del proyecto

```text
src/
|- 1_equation_definition/
|- 2_parameter_grid/
|- 3_zero_finding/
|- 4_data_preparation/
|- 5_symbolic_regression/
|- 6_expression_builder/
|- benchmark/
|  |- run_benchmark.py
|  |- runner.py
|  |- metrics.py
|  |- test_cases.py
|  |- run_batches.sh
|- config.py
|- main.py
|- requirements.txt
```

## 8. Problemas comunes y soluciones

### 8.1 Se queda en Compiling Julia backend...

Es normal en la primera ejecucion. Esperar a que termine la compilacion inicial.

### 8.2 Error: julia command not found

- Verificar instalacion de Julia.
- Confirmar julia --version en la misma terminal donde correras Python.
- Reabrir terminal para refrescar PATH.

### 8.3 Error: No module named pysr

- Verificar que el entorno virtual este activado.
- Reinstalar dependencias con pip install -r src/requirements.txt.

### 8.4 Codigo de salida 130

Significa que la ejecucion fue interrumpida manualmente (Ctrl+C o Stop del IDE).

### 8.5 Alto uso de RAM

- Ejecutar benchmark por batches con src/benchmark/run_batches.sh.
- Reducir NITERATIONS, POPULATIONS o MAXSIZE en src/config.py.

## 9. Recomendaciones para reproducibilidad

- Ejecutar siempre desde la raiz del repo.
- Usar un entorno virtual limpio por maquina.
- Mantener Python y Julia en versiones compatibles entre equipos.
- Guardar junto a resultados el commit de git y los parametros usados en src/config.py.
