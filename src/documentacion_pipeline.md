# Descubrimiento de Expresiones Analíticas de Raíces de Ecuaciones mediante Regresión Simbólica

## Índice

1. [Introducción y Planteamiento del Problema](#1-introducción-y-planteamiento-del-problema)
2. [Arquitectura General del Sistema](#2-arquitectura-general-del-sistema)
3. [Paso 1: Definición de la Ecuación](#3-paso-1-definición-de-la-ecuación)
4. [Paso 2: Generación del Grid de Parámetros](#4-paso-2-generación-del-grid-de-parámetros)
5. [Paso 3: Resolución Numérica de Ceros](#5-paso-3-resolución-numérica-de-ceros)
6. [Paso 4: Agrupación de Raíces por Rama](#6-paso-4-agrupación-de-raíces-por-rama)
7. [Paso 5: Regresión Simbólica](#7-paso-5-regresión-simbólica)
8. [Paso 6: Construcción de Expresiones Finales](#8-paso-6-construcción-de-expresiones-finales)
9. [Comprobación con Bases de Gröbner](#9-comprobación-con-bases-de-gröbner)
10. [Caso de Estudio: La Ecuación Cuadrática](#10-caso-de-estudio-la-ecuación-cuadrática)
11. [Decisiones de Diseño y Justificaciones](#11-decisiones-de-diseño-y-justificaciones)
12. [Limitaciones y Trabajo Futuro](#12-limitaciones-y-trabajo-futuro)

---

## 1. Introducción y Planteamiento del Problema

### 1.1 Motivación

En numerosas aplicaciones científicas y de ingeniería se requiere resolver ecuaciones de la forma

$$F(x;\, \alpha_1, \alpha_2, \ldots, \alpha_n) = 0$$

donde $x$ es la incógnita y $\alpha_1, \ldots, \alpha_n$ son parámetros. Cuando la ecuación admite una **solución analítica cerrada** — es decir, una función $x = g(\alpha_1, \ldots, \alpha_n)$ expresable en términos de operaciones elementales — dicha fórmula resulta invaluable: permite evaluar la solución instantáneamente para cualquier combinación de parámetros, facilita el análisis de sensibilidad, y proporciona comprensión cualitativa del comportamiento del sistema.

Sin embargo, obtener tales fórmulas manualmente es difícil o imposible para ecuaciones no lineales complejas. Mientras que las fórmulas para polinomios de grado $\leq 4$ son conocidas desde hace siglos (Cardano, Ferrari), para ecuaciones trascendentes o de grado superior no existen métodos algebraicos generales (Abel–Ruffini).

### 1.2 Propuesta

Este trabajo presenta un **pipeline computacional** que, dada una ecuación paramétrica $F(x; \boldsymbol{\alpha}) = 0$, descubre automáticamente las expresiones analíticas de sus raíces $x = g_i(\boldsymbol{\alpha})$ utilizando **regresión simbólica** (PySR).

La idea central es:

1. Generar un conjunto amplio de tuplas de parámetros $\{(\alpha_1^{(k)}, \ldots, \alpha_n^{(k)})\}_{k=1}^{N}$.
2. Para cada tupla, resolver numéricamente $F(x; \boldsymbol{\alpha}^{(k)}) = 0$ y obtener las raíces $x_1^{(k)}, x_2^{(k)}, \ldots$
3. Tratar los pares $(\boldsymbol{\alpha}^{(k)}, x_i^{(k)})$ como un **dataset de regresión**: los parámetros son las variables de entrada y la raíz es la variable de salida.
4. Aplicar **regresión simbólica** para descubrir la expresión $g_i(\boldsymbol{\alpha})$ que reproduce los datos.

### 1.3 Definición Formal

**Entrada:** Una ecuación $F(x;\, \alpha_1, \ldots, \alpha_n) = 0$, con $x \in \mathbb{R}$ incógnita y $\boldsymbol{\alpha} \in \mathbb{R}^n$ parámetros.

**Salida:** Un conjunto de expresiones $\{g_i\}_{i=1}^{r}$ tales que para cada rama de raíces:

$$F\bigl(g_i(\boldsymbol{\alpha});\, \boldsymbol{\alpha}\bigr) = 0 \quad \forall\, \boldsymbol{\alpha} \in \mathcal{D}$$

donde $\mathcal{D} \subset \mathbb{R}^n$ es el dominio de parámetros donde la rama $i$ existe.

---

## 2. Arquitectura General del Sistema

El sistema se organiza como un pipeline de 6 etapas secuenciales, más un módulo de comprobación independiente:

```
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline Principal                        │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 1. Definición│───▶│ 2. Grid de   │───▶│ 3. Resolución│  │
│  │    Ecuación   │    │  Parámetros  │    │    de Ceros   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                       │           │
│         ▼                                       ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 6. Expresión │◀───│ 5. Regresión │◀───│ 4. Agrupación│  │
│  │    Final      │    │   Simbólica  │    │   por Rama   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Comprobación con Bases de Gröbner (módulo independiente)    │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Estructura de Directorios

```
src/
├── main.py                          # Orquestador del pipeline
├── config.py                        # Configuración unificada (todas las etapas)
├── 1_equation_definition/           # Paso 1
│   └── equation_parser.py
├── 2_parameter_grid/                # Paso 2
│   └── grid_generator.py
├── 3_zero_finding/                  # Paso 3
│   └── solver.py
├── 4_data_preparation/              # Paso 4
│   └── root_grouping.py
├── 5_symbolic_regression/           # Paso 5
│   ├── symbolic_regression.py
│   ├── regression_adapter.py
│   ├── loss_functions.py
│   └── utils.py
├── 6_expression_builder/            # Paso 6
│   └── piecewise_builder.py
├── grobner_verification/            # Comprobación
│   └── verify.py
└── benchmark/                       # Sistema de benchmarking
    ├── test_cases.py                # Catálogo de 43 casos de prueba
    ├── runner.py                    # Ejecutor de casos individuales
    ├── metrics.py                   # Comparación y métricas
    └── run_benchmark.py             # Orquestador con CLI
```

### 2.2 Configuración Unificada

Toda la configuración del pipeline se centraliza en un único archivo `config.py` en la raíz de `src/`, organizado en 5 secciones:

1. **Opciones globales:** directorio de salida, nombre del experimento
2. **Definición de la ecuación:** string, variables, parámetros
3. **Grid de parámetros:** rangos y número de puntos por parámetro
4. **Resolución:** método del solver, filtrado de raíces complejas
5. **Regresión simbólica:** parámetros de PySR, tolerancias, estrategia iterativa

Los módulos de cada subcarpeta importan directamente desde este `config.py` añadiendo `src/` al `sys.path`.

> **Nota:** En `config.py`, `UNARY_OPERATORS` se define como `["sqrt", "neg"]` por legibilidad. Sin embargo, `symbolic_regression.py` transforma `sqrt` en la definición inline `safe_sqrt(x) = sqrt(abs(x))` al construir el modelo PySR (ver §7.3.1).

---

## 3. Paso 1: Definición de la Ecuación

### 3.1 Descripción

El usuario especifica la ecuación a resolver en `config.py`:

```python
EQUATION_STRING = "a*x**2 + b*x + c"   # F(x; a,b,c) = ax² + bx + c
VARIABLES = ["x"]                       # Incógnitas
PARAMETERS = ["a", "b", "c"]            # Parámetros
```

### 3.2 Parsing Simbólico

El módulo `equation_parser.py` convierte la cadena en una expresión de **SymPy**:

$$F(x; a, b, c) = ax^2 + bx + c$$

El parser:
1. Crea símbolos SymPy para cada variable y parámetro.
2. Usa `sympy.sympify()` con un diccionario `locals` que asocia cada nombre a su símbolo.
3. Retorna la expresión SymPy y un diccionario `symbols_dict` que mapea nombres a símbolos.

### 3.3 Generalidad

El sistema soporta cualquier ecuación expresable en SymPy:
- Polinomios de cualquier grado
- Ecuaciones trascendentes (trigonométricas, exponenciales)
- Sistemas con múltiples variables (preparado pero no implementado completamente)

---

## 4. Paso 2: Generación del Grid de Parámetros

### 4.1 Objetivo

Generar un conjunto $\mathcal{G} = \{(\alpha_1^{(k)}, \ldots, \alpha_n^{(k)})\}_{k=1}^{N}$ de tuplas de parámetros que cubran densamente el dominio de interés.

### 4.2 Método de Generación

Se utiliza un **grid regular (producto cartesiano)**:

Para cada parámetro $\alpha_i$ se define un rango $[\alpha_i^{\min}, \alpha_i^{\max}]$ que se divide en $m_i - 1$ partes iguales, generando $m_i$ puntos equiespaciados (incluidos ambos extremos). El grid completo es el producto cartesiano:

$$\mathcal{G} = \{(\alpha_1^{(j_1)}, \ldots, \alpha_n^{(j_n)}) : j_i = 1, \ldots, m_i\}$$

con $N = \prod_{i=1}^{n} m_i$ puntos totales.

Este método garantiza cobertura uniforme, es determinista y reproducible.

### 4.3 Configuración para el Caso de Estudio

Para la ecuación cuadrática $ax^2 + bx + c = 0$:

```python
PARAMETER_RANGES = {
    "a": (1, 3, 12),     # a ∈ [1, 3], 12 puntos
    "b": (-3, 3, 12),    # b ∈ [-3, 3], 12 puntos
    "c": (-2, 2, 12),    # c ∈ [-2, 2], 12 puntos
}
```

Esto produce $N = 12 \times 12 \times 12 = 1728$ tuplas de parámetros.

### 4.4 Decisión: ¿Por qué grid regular?

Se eligió grid regular porque:
- Garantiza cobertura uniforme del espacio de parámetros.
- Es determinista y reproducible.
- $12^3 = 1728$ es manejable en memoria y tiempo de cómputo.

---

## 5. Paso 3: Resolución Numérica de Ceros

### 5.1 Objetivo

Para cada tupla $\boldsymbol{\alpha}^{(k)} \in \mathcal{G}$, resolver

$$F(x;\, \boldsymbol{\alpha}^{(k)}) = 0$$

y obtener todas las raíces reales $x_1^{(k)}, x_2^{(k)}, \ldots, x_{r_k}^{(k)}$.

### 5.2 Método de Resolución

Se utiliza `sympy.solve()` (resolución simbólica). El proceso para cada tupla es:

1. **Sustitución:** Reemplazar los parámetros por sus valores numéricos en la expresión SymPy.
2. **Resolución:** Aplicar `sp.solve(eq_substituted, x)` para obtener las soluciones.
3. **Evaluación:** Convertir cada solución a valor numérico con `complex(sol.evalf())`.
4. **Filtrado:** Descartar raíces complejas (parte imaginaria $|\\text{Im}(x)| > 10^{-10}$).
5. **Ordenamiento:** Ordenar raíces de menor a mayor.

### 5.3 Filtrado de Raíces Complejas

Se filtra una raíz $z = a + bi$ como real si y solo si:

$$|b| < \varepsilon_{\text{complex}} = 10^{-10}$$

En ese caso se toma $x = \text{Re}(z) = a$.

### 5.4 Resultado

Para la ecuación cuadrática con $a > 0$, el discriminante $\Delta = b^2 - 4ac$ determina:
- $\Delta > 0$: dos raíces reales distintas → $r_k = 2$
- $\Delta = 0$: una raíz doble → $r_k = 1$
- $\Delta < 0$: ninguna raíz real → la tupla se descarta

De las 1728 tuplas, las que tienen $\Delta \geq 0$ producen raíces reales. Tras el filtrado se obtuvieron **1056 tuplas con exactamente 2 raíces reales**.

---

## 6. Paso 4: Agrupación de Raíces por Rama

### 6.1 Motivación

Una ecuación de grado $n$ puede tener hasta $n$ raíces. Para buscar una expresión analítica de cada raíz, necesitamos **agrupar las raíces por su posición ordinal**: la primera raíz más pequeña forma la "Rama 1", la segunda la "Rama 2", etc.

### 6.2 Método de Agrupación

Dado que las raíces se ordenan por valor en el Paso 3 ($x_1^{(k)} \leq x_2^{(k)} \leq \ldots$), la agrupación es directa:

$$\text{Rama } i = \{(\boldsymbol{\alpha}^{(k)}, x_i^{(k)}) : k = 1, \ldots, N,\; r_k \geq i\}$$

### 6.3 Estructura de Datos

Cada rama se almacena como un diccionario:
```python
{
    'X': np.ndarray de shape (M, n),   # Parámetros (entradas)
    'y': np.ndarray de shape (M,)       # Raíces (salidas)
}
```

Para la cuadrática, se obtienen 2 ramas con 1056 puntos cada una:
- **Rama 1:** La raíz menor → $x_1 = \frac{-b - \sqrt{b^2 - 4ac}}{2a}$
- **Rama 2:** La raíz mayor → $x_2 = \frac{-b + \sqrt{b^2 - 4ac}}{2a}$

---

## 7. Paso 5: Regresión Simbólica

Este es el paso central y más complejo del pipeline. Utiliza **PySR** (PySRRegressor), una librería de regresión simbólica basada en programación genética que se ejecuta sobre Julia.

### 7.1 Fundamento Teórico

La **regresión simbólica** busca, dentro de un espacio de expresiones matemáticas, la función $\hat{f}$ que minimiza una métrica de error sobre los datos:

$$\hat{f} = \arg\min_{f \in \mathcal{F}} \mathcal{L}(f) = \arg\min_{f \in \mathcal{F}} \frac{1}{N} \sum_{k=1}^{N} \ell\bigl(y^{(k)}, f(\mathbf{x}^{(k)})\bigr)$$

donde $\mathcal{F}$ es el espacio de expresiones construibles con un conjunto dado de operadores, y $\ell$ es una función de pérdida (en nuestro caso, MSE).

A diferencia de la regresión clásica (que fija la forma funcional y ajusta parámetros), la regresión simbólica **descubre la forma funcional** misma.

### 7.2 PySR y Programación Genética

PySR implementa un algoritmo de **programación genética multi-población** donde:

1. Cada individuo es un **árbol de expresión** (AST).
2. Las **operaciones genéticas** incluyen mutación, cruzamiento, simplificación algebraica.
3. Múltiples poblaciones evolucionan en paralelo con **migración** periódica.
4. El **Hall of Fame** almacena la mejor expresión encontrada para cada nivel de complejidad (número de nodos del árbol).

### 7.3 Configuración de PySR

A continuación se muestra la configuración exacta del modelo tal como aparece en el código (`symbolic_regression.py`):

```python
model = PySRRegressor(
    niterations=500,              # Iteraciones evolutivas
    populations=30,               # Poblaciones paralelas (islas)
    population_size=50,           # Individuos por población
    ncycles_per_iteration=550,    # Ciclos genéticos por iteración interna
    maxsize=25,                   # Máximo de nodos por árbol de expresión
    parsimony=0.0,                # Sin penalización por complejidad
    turbo=True,                   # Optimizaciones SIMD en Julia
    procs=0,                      # Un solo proceso Julia (ahorra RAM)
    model_selection="accuracy",   # Seleccionar por precisión pura
    batching=True,                # Evaluación por mini-batches
    batch_size=200,               # 200 puntos por batch
    unary_operators=["safe_sqrt(x) = sqrt(abs(x))", "neg"],
    binary_operators=["+", "-", "*", "/"],
    extra_sympy_mappings={"safe_sqrt": lambda x: sympy.sqrt(sympy.Abs(x))},
    nested_constraints={"safe_sqrt": {"safe_sqrt": 0}},
    complexity_of_operators={
        "+": 1, "-": 1, "*": 1, "/": 2,
        "safe_sqrt": 2, "neg": 1
    },
    temp_equation_file=True,      # Archivos temporales para ecuaciones
    delete_tempfiles=True,        # Limpiar archivos temporales al terminar
)
```

A continuación se justifica cada decisión de diseño:

#### 7.3.1 `safe_sqrt`: La Decisión Crítica

**Problema:** La fórmula cuadrática contiene $\sqrt{b^2 - 4ac}$. Para que PySR pueda descubrir esta expresión, necesita el operador `sqrt`. Sin embargo, durante la evolución genética se generan expresiones intermedias como $\sqrt{-7.3}$ que producen `NaN`, envenenan la población y destruyen las ramas evolutivas prometedoras.

**Solución rechazada — `bumper=True`:** PySR ofrece un mecanismo llamado `bumper` que reemplaza `NaN` por valores grandes. Sin embargo, esto **mata las expresiones con sqrt** porque les asigna un loss enorme, eliminándolas de la evolución antes de que puedan componerse en $\sqrt{b^2 - 4ac}$.

**Solución adoptada — `safe_sqrt`:** Se define un operador personalizado en Julia:

```julia
safe_sqrt(x) = sqrt(abs(x))
```

Con correspondencia en SymPy:

```python
extra_sympy_mappings = {"safe_sqrt": lambda x: sympy.sqrt(sympy.Abs(x))}
```

**¿Por qué funciona?** Durante la evolución, cualquier expresión con `safe_sqrt` produce un valor real finito, permitiendo que PySR componga gradualmente `safe_sqrt(b*b - 4*a*c)`. La función `abs()` no altera el resultado cuando el argumento es no negativo (que es exactamente el caso para datos con discriminante $\geq 0$, ya que filtramos las raíces complejas).

**Restricción de anidamiento:** Se prohíbe `safe_sqrt` dentro de `safe_sqrt` para evitar expresiones como $\sqrt{|\sqrt{|x|}|}$ que aumentan complejidad sin utilidad:

```python
nested_constraints = {"safe_sqrt": {"safe_sqrt": 0}}
```

#### 7.3.2 ¿Por qué `square` no está como operador?

Inicialmente se incluyó el operador `square(x) = x²`. Sin embargo, PySR trataba `square` como un operador atómico y no descubría que $b^2 = b \cdot b$. Al removerlo, PySR usa `b * b` con el operador `*`, lo que le permite llegar a `safe_sqrt(b*b - 4*a*c)` componiendo sub-expresiones existentes.

#### 7.3.3 `parsimony = 0.0` y `model_selection = "accuracy"`

La fórmula cuadrática tiene **complejidad ~18** (18 nodos en el árbol de expresión). Si se penaliza la complejidad (`parsimony > 0`), PySR prefiere expresiones simples pero inexactas. Al eliminar la penalización, se permite que la evolución explore expresiones complejas hasta alcanzar la fórmula exacta.

`model_selection = "accuracy"` instruye a PySR a devolver la ecuación con menor loss del Hall of Fame, independientemente de su complejidad. La alternativa `"best"` usa un balance entre complejidad y loss (similar al criterio de información de Akaike), que descartaría la fórmula exacta en favor de aproximaciones más simples.

#### 7.3.4 `niterations=500` y `ncycles_per_iteration=550`: Esfuerzo Computacional

Estos dos parámetros multiplicados determinan el **esfuerzo total de búsqueda**:

$$\text{Ciclos totales} = 500 \times 550 = 275{,}000$$

En cada ciclo, PySR aplica operaciones genéticas (mutación, cruzamiento, simplificación algebraica) a cada individuo de cada población. Para contexto, los valores por defecto de PySR son `niterations=40` y `ncycles_per_iteration=55`, lo que da $40 \times 55 = 2{,}200$ ciclos. Nuestra configuración usa **~125 veces más esfuerzo computacional** que el default.

Este esfuerzo es necesario porque:
- La fórmula cuadrática requiere descubrir una composición de 15-18 nodos — una expresión rara en un espacio combinatoriamente vasto.
- Con `batching=True`, la RAM no crece con más iteraciones (solo el tiempo), por lo que es rentable explorar más.
- Expresiones complejas como $\frac{-b + \sqrt{b^2 - 4ac}}{2a}$ necesitan muchas generaciones para ensamblarse pieza a pieza.

#### 7.3.5 `populations=30` y `population_size=50`: Diversidad Evolutiva

PySR implementa un modelo de **islas** (multi-población):

- **30 poblaciones (islas):** Cada isla evoluciona de forma independiente, explorando una zona diferente del espacio de expresiones. Periódicamente, las mejores expresiones migran entre islas.
- **50 individuos por isla:** Suficiente variedad genética dentro de cada isla para evitar convergencia prematura.

En total, $30 \times 50 = 1{,}500$ expresiones candidatas evolucionan simultáneamente. Esto maximiza la diversidad de la búsqueda: mientras una isla puede explorar expresiones lineales, otra puede estar construyendo composiciones con `safe_sqrt`, y una tercera puede estar optimizando fracciones con `/`.

#### 7.3.6 `maxsize=25`: Tamaño Máximo del Árbol

Cada expresión en PySR es un **árbol de sintaxis abstracta** (AST) donde cada operador y cada variable/constante es un nodo. El parámetro `maxsize` limita el número máximo de nodos.

Referencia de complejidades:

| Expresión | Nodos |
|---|---|
| `a` | 1 |
| `a + b` | 3 |
| `sqrt(a)` | 2 |
| `a * b + c` | 5 |
| `(-b + sqrt(b*b - 4*a*c)) / (2*a)` | ~15-18 |

Con `maxsize=25` hay margen para que PySR represente la fórmula cuadrática incluso en formas no simplificadas (por ejemplo, `((b + safe_sqrt((b * b) + (a * (c * -4.0)))) / a) * -0.5` tiene ~20 nodos). Si se usara `maxsize=10`, sería imposible representar la fórmula cuadrática y PySR nunca la encontraría.

#### 7.3.7 `batching=True` y `batch_size=200`

**Problema de RAM:** Con 1056 puntos de datos, 30 poblaciones y 50 individuos cada una, PySR evaluaba $30 \times 50 \times 1056 = 1{,}584{,}000$ predicciones por ciclo evolutivo, consumiendo RAM excesiva.

**Solución:** `batching=True` hace que cada ciclo evalúe un **mini-batch aleatorio** de 200 puntos en lugar de los 1056 completos. Esto reduce el consumo de memoria por un factor de $\sim$5.

**Efecto secundario positivo — regularización estocástica:** Al igual que el mini-batch en deep learning, evaluar diferentes subconjuntos aleatorios en cada ciclo evita que PySR se sobreajuste a un subconjunto particular de puntos. La expresión debe ser correcta en *todo* el dominio, no solo en un grupo de puntos favorables. Esto **mejora la generalización** de las expresiones descubiertas.

#### 7.3.8 `procs=0`: Un Solo Proceso Julia

PySR puede lanzar múltiples procesos Julia para evolución paralela. Sin embargo, cada proceso duplica el runtime de Julia en memoria. Con `procs=0`, toda la evolución ocurre en un único proceso, ahorrando centenares de MB de RAM a costa de velocidad.

#### 7.3.9 `turbo=True`: Optimizaciones en Julia

`turbo=True` activa optimizaciones agresivas en el backend de Julia, incluyendo operaciones SIMD (Single Instruction, Multiple Data) y evaluación vectorizada. Esto **acelera la evaluación de expresiones ~2-3 veces** sin afectar la calidad de los resultados. Dado el alto esfuerzo computacional configurado (275,000 ciclos), esta aceleración es importante para mantener los tiempos de ejecución en el rango de minutos y no de horas por rama.

#### 7.3.10 `complexity_of_operators`: Costos de Complejidad

El diccionario de costos asigna a cada operador un peso que contribuye al conteo de nodos del árbol:

```python
complexity_of_operators = {
    "+": 1, "-": 1, "*": 1,     # Operaciones básicas: 1 nodo
    "/": 2,                       # División: 2 nodos (más costosa)
    "safe_sqrt": 2,               # Raíz cuadrada: 2 nodos
    "neg": 1                      # Negación: 1 nodo
}
```

Asignar costo 2 a `/` y `safe_sqrt` refleja que son operaciones más "caras" conceptualmente. Esto influye en cuándo PySR alcanza `maxsize`: una expresión con muchas divisiones y raíces consumirá su presupuesto de nodos más rápido, guiando la evolución a usarlas solo cuando realmente reducen el error.

#### 7.3.11 `temp_equation_file=True` y `delete_tempfiles=True`

PySR comunica las ecuaciones del Hall of Fame entre Julia y Python mediante archivos temporales. `temp_equation_file=True` crea estos archivos en un directorio temporal del sistema en lugar del directorio de trabajo, evitando ensuciar el proyecto. `delete_tempfiles=True` los borra al finalizar.

#### 7.3.12 Función de Pérdida: MSE vs. Sigmoide

Se implementaron dos funciones de pérdida:

**Sigmoide (descartada, `USE_SIGMOID_LOSS=False`):**

$$\ell_{\sigma}(y, \hat{y}) = \frac{1}{1 + e^{-k(|y - \hat{y}| - \varepsilon)}}$$

Diseñada para producir un corte abrupto en $\varepsilon$: si $|y - \hat{y}| < \varepsilon$, la pérdida $\approx 0$; si $|y - \hat{y}| > \varepsilon$, la pérdida $\approx 1$.

**¿Por qué se descartó la sigmoide?** El problema fundamental es que la sigmoide **no distingue entre estar lejos y estar muy lejos** de un punto. Si una expresión candidata falla un punto por 0.5 o por 500, la pérdida es la misma ($\approx 1$). Esto elimina el gradiente informativo para los puntos no matcheados y crea un incentivo perverso: a PySR le resulta igualmente "rentable" matchear perfectamente una **región** del espacio de parámetros (por ejemplo, solo donde $a > 0$ y $b < 1$) que buscar la fórmula global. En la práctica, PySR encontraba constantes o expresiones simples que cubrían subconjuntos locales, fragmentando la búsqueda en lugar de descubrir $\frac{-b + \sqrt{b^2 - 4ac}}{2a}$.

En términos de optimización: la superficie de pérdida sigmoide tiene grandes **mesetas planas** (gradiente $\approx 0$) lejos de $\varepsilon$, lo que impide que la evolución genética y BFGS "vean" la dirección hacia la expresión correcta. El MSE, en cambio, tiene un gradiente proporcional al error, lo que siempre indica la dirección de mejora.

**MSE (adoptada):**

$$\mathcal{L}_{\text{MSE}} = \frac{1}{N} \sum_{k=1}^{N} (y^{(k)} - \hat{y}^{(k)})^2$$

La pérdida estándar guía a PySR hacia la expresión globalmente más precisa. Se complementa con matcheo post-entrenamiento usando tolerancia relativa para evaluar la calidad.

#### ¿Por qué MSE no produce expresiones "promedio" que no pasen por ningún punto?

Un riesgo teórico del MSE es que minimice el error global mediante una expresión "media" que no pase exactamente por ningún dato — un problema habitual en regresión clásica con datos ruidosos. En nuestro sistema este riesgo no se materializa, por cuatro razones que se complementan:

1. **Los datos no tienen ruido.** Los pares $(\boldsymbol{\alpha}^{(k)}, x^{(k)})$ provienen de resolver $F(x; \boldsymbol{\alpha}) = 0$ numéricamente. Son relaciones matemáticas exactas, no mediciones experimentales. Esto implica que **existe** una expresión con $\mathcal{L}_{\text{MSE}} \approx 0$ (del orden de $10^{-15}$ por precisión de punto flotante). Cualquier expresión "promedio" que no pase por los puntos tendría $\mathcal{L}_{\text{MSE}} \gg 0$, por lo que la presión evolutiva la descarta en favor de la expresión exacta.

2. **BFGS ajusta las constantes hacia la solución exacta.** PySR no solo evoluciona la estructura del árbol de expresión — para cada candidata, aplica el optimizador **BFGS** (método cuasi-Newton) para ajustar las constantes numéricas minimizando el MSE. Por ejemplo, si la evolución genética descubre la estructura `(b + sqrt(b*b + a*c*C₁)) / (a * C₂)`, BFGS ajusta $C_1$ y $C_2$ y, dado que los datos son exactos, converge a $C_1 \approx -4.0$ y $C_2 \approx -2.0$. Una estructura incorrecta nunca puede alcanzar $\mathcal{L}_{\text{MSE}} \approx 0$ por mucho que BFGS optimice sus constantes.

3. **La selección final usa $\varepsilon$-matching, no MSE.** Tras entrenar PySR, no se selecciona la ecuación con menor MSE sino la que **matchea más puntos** con la tolerancia relativa $|y - \hat{y}| < \varepsilon(1 + |y|)$ (ver §7.4). Esto actúa como red de seguridad: incluso si el Hall of Fame contiene una expresión "media" con MSE moderado, nunca será seleccionada porque matchea pocos puntos comparada con la expresión exacta.

4. **El proceso iterativo maneja la dispersión.** Si los datos de una rama son dispersos (una raíz con comportamiento diferente en distintas regiones), el proceso iterativo (§7.6) lo resuelve: en la iteración 1, PySR encuentra una expresión que cubre una porción de los puntos; en las siguientes iteraciones, descubre las expresiones restantes. El umbral `MIN_MATCH_FRACTION = 0.05` garantiza que cada expresión aceptada cubre al menos el 5% de los puntos restantes, rechazando expresiones que no pasan por casi ningún dato.

En resumen, MSE actúa como **motor de búsqueda** durante la evolución: guía a PySR hacia el vecindario de la expresión correcta. La **decisión final** la toma el $\varepsilon$-matching punto a punto, que verifica que la expresión pasa efectivamente por los datos.

### 7.4 Evaluación del Hall of Fame

Tras ejecutar PySR, el **Hall of Fame** contiene la mejor ecuación para cada nivel de complejidad (1 nodo, 2 nodos, ..., 25 nodos). En lugar de tomar solo la ecuación "mejor" según el modelo, **evaluamos todas las ecuaciones del Hall of Fame** y seleccionamos la que matchea más puntos.

El matcheo usa **tolerancia relativa**:

$$|y^{(k)} - \hat{y}^{(k)}| < \varepsilon \cdot (1 + |y^{(k)}|)$$

con $\varepsilon = 0.005$. La tolerancia relativa es preferible a la absoluta porque adapta el umbral al orden de magnitud de $y$: un error de $0.01$ es despreciable para $y = 100$ pero no para $y = 0.001$.

### 7.5 Estrategia Multi-Intento

PySR es un algoritmo **estocástico**: distintas ejecuciones sobre los mismos datos pueden encontrar expresiones diferentes. En nuestras pruebas, una ejecución encontraba la fórmula exacta con 100% de cobertura mientras otra solo lograba 15%.

**Solución:** En cada iteración del proceso iterativo, se ejecuta PySR `NUM_ATTEMPTS = 3` veces. Se evalúa el Hall of Fame completo de cada intento y se selecciona la ecuación que matchea el mayor número de puntos entre todos los intentos. Si algún intento logra 100% de cobertura, se interrumpen los intentos restantes (*early stopping*).

### 7.6 Algoritmo Iterativo

Para ecuaciones cuyas raíces se comportan como una función definida a trozos, es necesario un **proceso iterativo** que descubra cada pieza:

```
Algoritmo: Regresión Simbólica Iterativa con Multi-Intento
──────────────────────────────────────────────────────────
Entrada: X ∈ ℝ^{N×n}, y ∈ ℝ^N, parámetros de configuración
Salida:  Lista de funciones {(gⱼ, Iⱼ)}

1.  X_rem ← X, y_rem ← y, idx ← {1,...,N}
2.  Para iteración t = 1, 2, ..., MAX_ITERATIONS:
3.      Si |X_rem| < MIN_POINTS: terminar
4.      mejor ← ∅
5.      Para intento a = 1, ..., NUM_ATTEMPTS:
6.          modelo ← PySR.fit(X_rem, y_rem)
7.          Para cada ecuación e en Hall_of_Fame(modelo):
8.              ŷ ← e.predict(X_rem)
9.              M ← {k : |y_rem[k] - ŷ[k]| < ε(1+|y_rem[k]|)}
10.             Si |M| > |mejor.M|: mejor ← (e, M)
11.         Si |mejor.M| = |X_rem|: break (early stop)
12.     Si |mejor.M| / |X_rem| < MIN_MATCH_FRACTION: continuar
13.     Registrar gₜ ← mejor.e, Iₜ ← idx[mejor.M]
14.     X_rem ← X_rem \ mejor.M
15.     y_rem ← y_rem \ mejor.M
16.     idx ← idx \ mejor.M
17. Retornar {(gₜ, Iₜ)}ₜ
```

**Ejemplo de uso del proceso iterativo:** Una función definida a trozos

$$x(\alpha) = \begin{cases} \alpha^2 & \text{si } \alpha < 0 \\ \sin(\alpha) & \text{si } \alpha \geq 0 \end{cases}$$

En la iteración 1, PySR descubre $\alpha^2$ y matchea los puntos con $\alpha < 0$. En la iteración 2, con los puntos restantes ($\alpha \geq 0$), descubre $\sin(\alpha)$.

### 7.7 Control de Calidad

- **`MIN_MATCH_FRACTION = 0.05`**: Una ecuación debe matchear al menos el 5% de los puntos restantes para ser aceptada. Esto evita aceptar expresiones espurias que solo ajustan ruido.
- **`MAX_CONSECUTIVE_NO_MATCH = 2`**: Si dos iteraciones consecutivas no producen un matcheo aceptable, el proceso se detiene.

---

## 8. Paso 6: Construcción de Expresiones Finales

### 8.1 Caso Simple: Expresión Única

Si una rama se resuelve en una sola iteración (una función matchea todos los puntos), la salida es directamente esa expresión.

### 8.2 Caso Complejo: Expresión Piecewise

Si el proceso iterativo encuentra múltiples funciones $g_1, g_2, \ldots$ para una rama, se construye una expresión **Piecewise**:

$$x(\boldsymbol{\alpha}) = \begin{cases} g_1(\boldsymbol{\alpha}) & \text{si } \boldsymbol{\alpha} \in \mathcal{R}_1 \\ g_2(\boldsymbol{\alpha}) & \text{si } \boldsymbol{\alpha} \in \mathcal{R}_2 \\ \vdots \end{cases}$$

donde las regiones $\mathcal{R}_i$ se determinan a partir de los puntos matcheados por cada función.

---

## 9. Comprobación con Bases de Gröbner

### 9.1 Motivación

La regresión simbólica produce expresiones que ajustan bien los datos numéricos, pero ¿son **algebraicamente correctas**? ¿Es $g(\boldsymbol{\alpha})$ realmente una raíz de $F$? PySR puede encontrar expresiones con constantes ligeramente aproximadas (por ejemplo, `−4.0000005` en vez de `−4`), o formas equivalentes pero no obvias.

Para ecuaciones polinómicas, la **teoría de bases de Gröbner** proporciona un método algorítmico de verificación exacta.

### 9.2 Fundamento Teórico

#### 9.2.1 Ideales y Anillos Polinómicos

Sea $k[\alpha_1, \ldots, \alpha_n]$ el anillo de polinomios sobre un cuerpo $k$. Un **ideal** $I \subset k[\alpha_1, \ldots, \alpha_n]$ es un subconjunto cerrado bajo suma y multiplicación por elementos del anillo.

Un ideal finitamente generado es $I = \langle f_1, \ldots, f_s \rangle = \{h_1 f_1 + \cdots + h_s f_s : h_i \in k[\alpha_1, \ldots, \alpha_n]\}$.

#### 9.2.2 Bases de Gröbner

Una **base de Gröbner** $G$ de un ideal $I$ (respecto a un ordenamiento monomial) es un conjunto generador de $I$ con la propiedad de que todo polinomio tiene un **residuo único** al dividirlo por $G$.

Propiedad fundamental: $f \in I \iff \text{rem}(f, G) = 0$.

Esto permite decidir algorítmicamente si un polinomio pertenece a un ideal.

#### 9.2.3 Algoritmo de Buchberger

El cálculo de bases de Gröbner se realiza mediante el **algoritmo de Buchberger** (o variantes optimizadas como Faugère F4/F5), que reduce iterativamente los **S-polinomios** de pares de generadores hasta que todos se reducen a cero.

### 9.3 Verificación de Raíces

#### 9.3.1 Caso sin Radicales

Si $g(\boldsymbol{\alpha})$ es una expresión racional (sin raíces cuadradas), verificar que es raíz de $F$ equivale a comprobar:

$$F\bigl(g(\boldsymbol{\alpha});\, \boldsymbol{\alpha}\bigr) \equiv 0$$

Esto se verifica directamente sustituyendo y simplificando algebraicamente.

#### 9.3.2 Caso con Radicales: Variable Auxiliar

Si $g$ contiene $\sqrt{h(\boldsymbol{\alpha})}$, introducimos una **variable auxiliar** $s$ con la relación:

$$s^2 = h(\boldsymbol{\alpha}) \quad \Leftrightarrow \quad s^2 - h(\boldsymbol{\alpha}) = 0$$

Sea $g_{\text{poly}}(\boldsymbol{\alpha}, s)$ la expresión resultante de reemplazar $\sqrt{h}$ por $s$ en $g$. Entonces $g$ es raíz de $F$ si y solo si:

$$F\bigl(g_{\text{poly}}(\boldsymbol{\alpha}, s);\, \boldsymbol{\alpha}\bigr) \equiv 0 \pmod{s^2 - h(\boldsymbol{\alpha})}$$

Es decir, si el polinomio $F(g_{\text{poly}})$ pertenece al ideal $\langle s^2 - h(\boldsymbol{\alpha}) \rangle$.

**Procedimiento algorítmico:**

1. Sustituir $x = g_{\text{poly}}(\boldsymbol{\alpha}, s)$ en $F$ para obtener $P = F(g_{\text{poly}}, \boldsymbol{\alpha})$.
2. Limpiar denominadores: si $P = N/D$, trabajar con $N$.
3. Calcular la base de Gröbner de $\{s^2 - h(\boldsymbol{\alpha})\}$.
4. Reducir $N$ módulo la base de Gröbner.
5. Si el residuo es $0$, entonces $g$ es una raíz válida de $F$.

#### 9.3.3 Ambigüedad de Signo por `safe_sqrt`

PySR usa `safe_sqrt(h) = sqrt(|h|)`. Algebraicamente, $|h|$ es $h$ o $-h$ dependiendo del signo de $h$. Para la verificación, se prueban ambas variantes:

- Variante 1: $s^2 = h$ (argumento directo)
- Variante 2: $s^2 = -h$ (argumento negado)

Si alguna de las dos produce residuo 0, la expresión es válida.

### 9.4 Racionalización de Constantes

PySR produce constantes numéricas aproximadas (por ejemplo, `−4.0000005` en lugar de `−4`, o `0.5` en lugar de `1/2`). Para la verificación algebraica exacta, se usa **`nsimplify`** de SymPy con tolerancia $10^{-4}$:

$$-4.0000005 \longrightarrow -4, \qquad 0.499999825 \longrightarrow \frac{1}{2}, \qquad -2.0000007 \longrightarrow -2$$

Esto convierte las expresiones en racionales exactos, permitiendo cancelaciones algebraicas perfectas.

### 9.5 Eliminación de Denominadores

Las expresiones de PySR suelen contener fracciones como $\frac{-b + s}{2a}$. Al sustituir en $F$, el resultado tiene denominadores (ej: $c + \frac{s^2 - b^2}{4a}$). Las bases de Gröbner operan sobre **anillos polinómicos** y no manejan $1/a$.

**Solución:** Se utiliza `sympy.together()` para combinar fracciones y `sympy.fraction()` para extraer numerador y denominador. La verificación se hace sobre el **numerador** (el denominador no puede ser idénticamente cero bajo nuestras restricciones de parámetros).

### 9.6 Niveles de Verificación

El módulo aplica tres niveles en cascada:

1. **Algebraica Directa:** Sustituir y simplificar con SymPy. Funciona cuando la expresión racionalizada cancela exactamente.

2. **Bases de Gröbner:** Para expresiones con radicales donde la simplificación directa no basta. Se introduce la variable auxiliar $s$ y se reduce módulo $s^2 - h$.

3. **Numérica:** Evaluar $F(g(\boldsymbol{\alpha}), \boldsymbol{\alpha})$ en 100 puntos aleatorios y verificar que $|F| < 10^{-8}$. Sirve como fallback cuando las verificaciones algebraicas no aplican (ej: ecuaciones trascendentes).

---

## 10. Caso de Estudio: La Ecuación Cuadrática

### 10.1 Ecuación

$$F(x; a, b, c) = ax^2 + bx + c = 0$$

Solución analítica conocida:

$$x_{1,2} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

### 10.2 Configuración

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| $a \in [1, 3]$ | 12 puntos | Se evita $a = 0$ (ecuación degenerada) |
| $b \in [-3, 3]$ | 12 puntos | Rango moderado simétrico |
| $c \in [-2, 2]$ | 12 puntos | Rango moderado simétrico |
| Total tuplas | 1728 | $12^3$ |
| Tuplas con $\Delta \geq 0$ | 1056 | Filtro por raíces reales |

### 10.3 Resultados de la Regresión Simbólica

**Rama 1** (raíz menor, $x_1$):

PySR encontró en el intento 1, con complejidad 18 y loss $6.7 \times 10^{-15}$:

$$x_1 = \frac{b + \text{safe\_sqrt}(b \cdot b + c \cdot (-4.0000005) \cdot a)}{a \cdot (-2.0000007)}$$

que, tras racionalización, se convierte en:

$$x_1 = \frac{-(b + \sqrt{b^2 - 4ac})}{2a} = \frac{-b - \sqrt{b^2 - 4ac}}{2a} \quad \checkmark$$

Cobertura: **1056/1056 puntos (100%)**.

**Rama 2** (raíz mayor, $x_2$):

PySR encontró con complejidad 18 y loss $6.7 \times 10^{-15}$:

$$x_2 = \bigl(\text{safe\_sqrt}(a \cdot c \cdot 4 - b \cdot b) - b\bigr) \cdot \frac{0.5}{a}$$

que se racionaliza a:

$$x_2 = \frac{-b + \sqrt{4ac - b^2}}{2a}$$

Nótese que PySR escribió el discriminante como $4ac - b^2$ en lugar de $b^2 - 4ac$. Esto es válido porque `safe_sqrt` aplica `abs()`, y $|4ac - b^2| = |b^2 - 4ac|$, por lo que $\sqrt{|4ac - b^2|} = \sqrt{b^2 - 4ac}$.

Cobertura: **1056/1056 puntos (100%)**.

### 10.4 Verificación con Bases de Gröbner

#### Rama 1

**Verificación algebraica directa:** Tras racionalizar $g_1 = -(b + \sqrt{b^2 - 4ac})/(2a)$, SymPy calculó:

$$F(g_1) = \text{expand}\left(a \cdot g_1^2 + b \cdot g_1 + c\right) = 0 \quad \checkmark$$

**Verificación con Gröbner:** Se introdujo $s_0$ con $s_0^2 = b^2 - 4ac$. El numerador de $F(g_1)$ resulta ser:

$$N = 4ac - b^2 + s_0^2$$

La base de Gröbner del ideal $\langle s_0^2 - (b^2 - 4ac) \rangle = \langle s_0^2 - b^2 + 4ac \rangle$ es el propio generador. Reduciendo $N$:

$$\text{rem}(4ac - b^2 + s_0^2, \;\{s_0^2 - b^2 + 4ac\}) = 0 \quad \checkmark$$

#### Rama 2

**Verificación algebraica directa:** No simplificó a 0 directamente porque SymPy no resolvió la relación $\sqrt{4ac - b^2}$ vs $\sqrt{b^2 - 4ac}$.

**Verificación con Gröbner (Variante 2 de signo):** Se probó $s_0^2 = -(4ac - b^2) = b^2 - 4ac$, es decir, el ideal $\langle s_0^2 - b^2 + 4ac \rangle$. El numerador de $F(g_2)$ resultó:

$$N = 4ac - b^2 + s_0^2$$

$$\text{rem}(N, \;\{s_0^2 - b^2 + 4ac\}) = 0 \quad \checkmark$$

La verificación con variante de signo negado demostró que `safe_sqrt(4ac - b²)` es algebraicamente equivalente a `sqrt(b² - 4ac)`.

### 10.5 Resumen de Verificación

| Rama | Expresión Racionalizada | Algebraica | Gröbner | Estado |
|------|-------------------------|:----------:|:-------:|:------:|
| 1 | $\frac{-b - \sqrt{b^2-4ac}}{2a}$ | ✓ | ✓ | **VÁLIDA** |
| 2 | $\frac{-b + \sqrt{b^2-4ac}}{2a}$ | — | ✓ | **VÁLIDA** |

---

## 11. Decisiones de Diseño y Justificaciones

### 11.1 Tabla de Decisiones

| # | Decisión | Alternativa considerada | Motivo de elección |
|---|----------|------------------------|-------------------|
| 1 | `safe_sqrt(x) = sqrt(abs(x))` | `sqrt` con `bumper=True` | `bumper` mata las expresiones intermedias con $\sqrt{(\text{negativo})}$ antes de que puedan componerse. `safe_sqrt` siempre produce valores finitos |
| 2 | Remover operador `square` | Incluir `square(x) = x²` | PySR trata `square` como atómico y no descubre que $b^2 = b \cdot b$ dentro de $\sqrt{b^2 - 4ac}$ |
| 3 | MSE loss | Sigmoide loss | Sigmoide fragmenta el espacio de parámetros en regiones, encontrando fórmulas locales en vez de la global |
| 4 | `parsimony = 0.0` | `parsimony > 0` | La fórmula cuadrática tiene ~18 nodos. La penalización de complejidad impide que PySR la explore |
| 5 | `model_selection = "accuracy"` | `"best"` (balance complejidad/loss) | Queremos la expresión más precisa del Hall of Fame, no la más simple |
| 6 | `batching=True, batch_size=200` | Evaluar todos los puntos | Controla RAM (factor ~5), y además actúa como regularización estocástica (mini-batch) que mejora generalización |
| 7 | `procs=0` | Multiprocessing | Cada proceso Julia duplica el consumo de RAM. Un solo proceso ahorra centenares de MB |
| 8 | Tolerancia relativa $\varepsilon(1+\|y\|)$ | Tolerancia absoluta $\varepsilon$ | Adaptación al orden de magnitud: un error de 0.01 es despreciable para $y=100$ pero significativo para $y=0.001$ |
| 9 | Multi-intento por iteración | Single-shot | PySR es estocástico: una ejecución logra 100%, otra solo 15%. Con 3 intentos se toma el mejor |
| 10 | Iterativo + Multi-intento | Multi-intento envolvente | El proceso iterativo descubre funciones Piecewise; el multi-intento da robustez. Combinados: máxima flexibilidad |
| 11 | Evaluación de todo el Hall of Fame | Solo `model.predict()` (la "mejor") | PySR selecciona por loss MSE, pero una ecuación con loss ligeramente mayor puede matchear exactamente más puntos |
| 12 | Grid regular (producto cartesiano) | LHS o Random | Determinista, reproducible, cobertura uniforme garantizada. Se descartaron las alternativas por innecesarias |
| 13 | `nsimplify` con tolerancia $10^{-4}$ | Usar constantes float directamente | Las constantes de PySR son aproximadas; racionalizar permite cancelaciones algebraicas exactas en la verificación |
| 14 | Variables auxiliares + Gröbner | Simplificación directa con SymPy | SymPy no siempre simplifica expresiones con $\sqrt{|h|}$; Gröbner decide algorítmicamente la pertenencia al ideal |
| 15 | `niterations=500` × `ncycles=550` | Defaults de PySR (40 × 55) | ~275,000 ciclos totales (~125x más que default). Necesario para descubrir expresiones complejas de 15-18 nodos |
| 16 | `populations=30`, `population_size=50` | Menos poblaciones | 30 islas × 50 individuos = 1,500 candidatas simultáneas. Maximiza diversidad con modelo de islas y migración |
| 17 | `maxsize=25` | Default (20) | La fórmula cuadrática tiene ~15-18 nodos; formas no simplificadas de PySR pueden alcanzar ~20. 25 da margen suficiente |
| 18 | `turbo=True` | `turbo=False` | Activa SIMD y evaluación vectorizada en Julia, ~2-3x más rápido. Esencial para hacer viables 275,000 ciclos |
| 19 | `complexity_of_operators`: `/`=2, `safe_sqrt`=2 | Costo uniforme (todo=1) | Refleja que `sqrt` y `/` son más costosas; guía a PySR a usarlas solo cuando reducen el error significativamente |
| 20 | `nested_constraints`: prohibir sqrt-en-sqrt | Sin restricción | Evita expresiones inútiles como $\sqrt{|\sqrt{|x|}|}$ que consumen nodos sin aportar precisión |

### 11.2 Evolución del Diseño

El diseño final se alcanzó tras múltiples iteraciones:

1. **Intento con `sqrt` directo:** Fracasó — PySR no encontraba raíces cuadradas.
2. **Intento con `bumper=True`:** Fracasó — las expresiones con `sqrt` eran eliminadas de la evolución.
3. **Intento con sigmoide loss:** Fragmentaba las expresiones, encontrando fórmulas locales.
4. **Intento con `square` como operador:** Impedía la composición $\sqrt{b^2 - 4ac}$.
5. **Descubrimiento de `safe_sqrt`:** Permite la evolución de expresiones con raíces cuadradas sin producir NaN.
6. **Adición de batching:** Resolvió el problema de consumo excesivo de RAM.
7. **Multi-intento:** Compensó la estocasticidad de PySR.
8. **Evaluación del Hall of Fame completo:** Encontró la fórmula exacta que no era la seleccionada por defecto.

---

## 12. Limitaciones y Trabajo Futuro

### 12.1 Limitaciones Actuales

- **Variable única:** El pipeline actualmente soporta ecuaciones con una sola incógnita. La extensión a sistemas de ecuaciones requiere reorganizar el Paso 3 y la agrupación por rama.
- **Determinación de regiones Piecewise:** La construcción automática de las condiciones de las regiones es simplificada. Un sistema robusto requeriría clasificación espacial o árboles de decisión.
- **Escalabilidad:** Para ecuaciones con muchos parámetros ($n > 5$), el grid regular $m^n$ crece exponencialmente. Sería necesario LHS o muestreo adaptativo.
- **Ecuaciones trascendentes:** La verificación con Gröbner solo aplica a ecuaciones polinómicas. Para ecuaciones trascendentes, la verificación numérica es el único método disponible.

### 12.2 Trabajo Futuro

- Integrar la verificación de Gröbner de forma opcional en el pipeline.
- Implementar detección automática de regiones para expresiones Piecewise.
- Explorar operadores adicionales (trigonométricos, exponenciales) para ecuaciones trascendentes.
- Paralelizar los intentos de PySR en máquinas con RAM suficiente.
- Implementar un mecanismo de *warm start* donde intentos posteriores hereden las mejores expresiones de intentos anteriores.

---

## Apéndice A: Dependencias

| Paquete | Versión | Uso |
|---------|---------|-----|
| PySR | 1.5.9 | Regresión simbólica |
| SymPy | 1.14.0 | Álgebra simbólica, parsing, Gröbner |
| NumPy | 2.3.3 | Arrays numéricos |
| Pandas | 2.3.2 | Hall of Fame de PySR |
| scikit-learn | 1.7.2 | Dependencia de PySR |
| juliacall | 0.9.26 | Puente Python ↔ Julia |

## Apéndice B: Reproducción del Experimento

```bash
# 1. Activar entorno virtual
source .venv/bin/activate

# 2. Ejecutar pipeline completo
cd src
python3 main.py

# 3. Verificar resultados con Gröbner
cd grobner_verification
python verify.py ../outputs_analytical/quadratic_test_<timestamp>
```
