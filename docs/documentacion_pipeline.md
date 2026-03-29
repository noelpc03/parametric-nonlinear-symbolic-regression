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
12. [Resultados del Benchmark](#12-resultados-del-benchmark)
13. [Limitaciones y Trabajo Futuro](#13-limitaciones-y-trabajo-futuro)

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

> **Nota:** En `config.py`, `UNARY_OPERATORS` se define como `["neg"]` y `BINARY_OPERATORS` como `["+", "-", "*", "/"]`. El operador de potencia generalizado `safe_pow(x, y) = sign(x) * abs(x)^y` se agrega como operador binario inline en `symbolic_regression.py` (ver §7.3.1).

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

### 6.4 Cuándo Funciona el Ordenamiento

**Condición de corrección:** El ordenamiento por posición funciona si y solo si las ramas **no se cruzan** para ningún valor de los parámetros en el rango de interés:

$$g_1(\boldsymbol{\alpha}) < g_2(\boldsymbol{\alpha}) < \ldots < g_n(\boldsymbol{\alpha}) \quad \forall\, \boldsymbol{\alpha} \in \mathcal{D}$$

**Ejemplo canónico — $x^2 - a = 0$ con $a > 0$:**

Raíces exactas: $x_1 = -\sqrt{a}$, $x_2 = \sqrt{a}$.

| $a$ | Raíces ordenadas | Rama 1 | Rama 2 |
|-----|-----------------|--------|--------|
| 1   | $[-1,\; 1]$     | $-1$   | $1$    |
| 4   | $[-2,\; 2]$     | $-2$   | $2$    |
| 9   | $[-3,\; 3]$     | $-3$   | $3$    |
| 16  | $[-4,\; 4]$     | $-4$   | $4$    |

Las ramas nunca se cruzan ($-\sqrt{a} < \sqrt{a}$ para todo $a > 0$). El ordenamiento las separa limpiamente y PySR descubre $-\sqrt{a}$ y $\sqrt{a}$ sin confusión.

### 6.5 Cuándo Falla: Cruce de Ramas y Cambio en el Número de Raíces

#### Caso 1: Raíces independientes que se cruzan — $(x-a)(x-b) = 0$

Raíces exactas: $x = a$ y $x = b$, con $a$ y $b$ variando independientemente.

| $a$ | $b$ | Ordenadas   | Rama 1     | Rama 2     |
|-----|-----|-------------|------------|------------|
| 1   | 3   | $[1,\; 3]$  | $a$        | $b$        |
| 2   | 3   | $[2,\; 3]$  | $a$        | $b$        |
| 4   | 3   | $[3,\; 4]$  | $b$ ⚠️     | $a$ ⚠️     |
| 5   | 3   | $[3,\; 5]$  | $b$ ⚠️     | $a$ ⚠️     |

Cuando $a > b$ las ramas se **intercambian**. El dataset de la Rama 1 contiene $\min(a, b)$, que no es una expresión algebraica estándar. PySR no puede expresar $\min(a, b)$ con $+, -, \times, \div, \sqrt{\,}$, aunque la fórmula de cada raíz individual ($x = a$ o $x = b$) sea trivial.

#### Caso 2: Número de raíces variable — $x^3 - 3x + a = 0$ con $a \in [-3, 3]$

Esta cúbica tiene **3 raíces reales** para $|a| < 2$ y **1 raíz real** para $|a| > 2$:

| $a$    | Raíces reales (ordenadas)        | Rama 1 | Rama 2 | Rama 3 |
|--------|----------------------------------|--------|--------|--------|
| $-3$   | $[\approx 2.10]$                 | 2.10   | —      | —      |
| $-1.5$ | $[-1.82,\; 0.35,\; 1.47]$       | −1.82  | 0.35   | 1.47   |
| $0$    | $[-1.73,\; 0,\; 1.73]$           | −1.73  | 0      | 1.73   |
| $1.5$  | $[-1.47,\; {-0.35},\; 1.82]$    | −1.47  | −0.35  | 1.82   |
| $3$    | $[\approx -2.10]$                | −2.10  | —      | —      |

La **Rama 1 mezcla datos de fórmulas analíticas distintas**: para $|a| < 2$ sigue la fórmula trigonométrica de Vieta; para $|a| > 2$ sigue la fórmula de Cardano. No existe ninguna expresión analítica continua que cubra todos esos puntos.

```
   raíces
    ↑
  2 |          ·····                    ← raíz única (a < -2)
    |       ···     ···
  1 |   ···    ╱╱╱╱╱╱╱ ···             ← rama 3 (|a| < 2)
    |  ·      ╱╱╱╱╱╱╱╱╱   ···
  0 |--------╱╱╱╱╱╱╱╱╱╱---------→ a   ← rama 2 (|a| < 2)
    |  ····  ╲╲╲╲╲╲╲╲╲   ·
 -1 |     ··· ╲╲╲╲╲╲╲ ···              ← rama 1 (|a| < 2)
    |        ···     ···
 -2 |           ·····                   ← raíz única (a > 2)
    +----+----+----+----+----→
        -3   -1    1    3     a
```

La Rama 1 salta entre la curva de abajo ($|a| < 2$) y las curvas de raíz única ($|a| > 2$), produciendo una función con **discontinuidades** en $a = \pm 2$.

### 6.6 Resumen: Condiciones de Aplicabilidad

| Condición | ¿Funciona? | Ejemplo |
|-----------|:----------:|---------|
| Ramas no se cruzan para todo $\boldsymbol{\alpha} \in \mathcal{D}$ | ✅ | $x^2 - a = 0$, $ax^2+bx+c=0$ |
| Raíces simétricas tipo $\pm f(\boldsymbol{\alpha})$ | ✅ | $x^2 - a = 0$, $x^2 - a^2 = 0$ |
| Número de raíces constante en $\mathcal{D}$ | ✅ | Cuadrática con $\Delta > 0$ siempre |
| Ramas se cruzan ($g_i(\boldsymbol{\alpha}_0) = g_j(\boldsymbol{\alpha}_0)$ para algún $\boldsymbol{\alpha}_0$) | ❌ | $(x-a)(x-b)=0$ |
| Número de raíces varía con los parámetros | ❌ | $x^3 - 3x + a = 0$ |
| Raíces confluentes (raíz doble) cerca del borde del dominio | ⚠️ | Discriminante $\to 0$ |

> **Nota:** Los 43 casos del benchmark actual están diseñados para satisfacer las condiciones de aplicabilidad: la mayoría tiene un solo parámetro positivo con raíces que no se cruzan. El caso `special_39` es la excepción conocida donde el cruce de ramas impide el descubrimiento.

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

#### Versión 1 (configuración base histórica)

La configuración V1 original utilizaba `safe_sqrt(x) = sqrt(abs(x))` como operador **unario** dedicado para raíces cuadradas. Esta versión fue reemplazada por el operador generalizado `safe_pow` (ver §7.3.1).

```python
# ── Configuración V1 (HISTÓRICA — ya no se usa) ──
model = PySRRegressor(
    niterations=500,
    populations=30,
    population_size=50,
    ncycles_per_iteration=550,
    maxsize=25,
    parsimony=0.0,
    turbo=True,
    procs=0,
    model_selection="accuracy",
    batching=True,
    batch_size=200,
    unary_operators=["safe_sqrt(x) = sqrt(abs(x))", "neg"],
    binary_operators=["+", "-", "*", "/"],
    extra_sympy_mappings={"safe_sqrt": lambda x: sympy.sqrt(sympy.Abs(x))},
    nested_constraints={"safe_sqrt": {"safe_sqrt": 0}},
    complexity_of_operators={
        "+": 1, "-": 1, "*": 1, "/": 2,
        "safe_sqrt": 2, "neg": 1
    },
    temp_equation_file=True,
    delete_tempfiles=True,
)
```

#### Configuración actual (Versión 3)

La configuración actual del modelo tal como aparece en `symbolic_regression.py`. Esta versión incorpora **operadores unarios de raíces n-ésimas** (2 a 10) para resolver el problema de ambigüedad exponencial/raíz detectado en versiones anteriores (ver §7.3.14):

```python
# ── Operadores unarios de raíces (Julia) ──
root_operators = [
    "safe_sqrt(x) = sqrt(abs(x))",                      # Raíz 2
    "safe_cbrt(x) = cbrt(x)",                           # Raíz 3
    "safe_root4(x) = sqrt(sqrt(abs(x)))",               # Raíz 4
    "safe_root5(x) = sign(x) * sqrt(sqrt(abs(x))) * abs(x)^0.05",  # Raíz 5
    "safe_root6(x) = cbrt(sqrt(abs(x)))",               # Raíz 6
    "safe_root7(x) = sign(x) * abs(x)^(1.0/7.0)",       # Raíz 7
    "safe_root8(x) = sqrt(sqrt(sqrt(abs(x))))",         # Raíz 8
    "safe_root9(x) = cbrt(cbrt(x))",                    # Raíz 9
    "safe_root10(x) = sqrt(sqrt(sqrt(abs(x)))) * abs(x)^0.025",  # Raíz 10
]

model = PySRRegressor(
    niterations=500,              # Iteraciones evolutivas
    populations=30,               # Poblaciones paralelas (islas)
    population_size=50,           # Individuos por población
    ncycles_per_iteration=550,    # Ciclos genéticos por iteración interna
    maxsize=25,                   # Máximo de nodos por árbol de expresión
    parsimony=0.0,                # Sin penalización por complejidad
    turbo=True,                   # Optimizaciones SIMD en Julia
    procs=0,                      # Un solo proceso Julia (ahorra RAM)
    model_selection="best",       # Salto de parsimonia (ver §7.3.14)

    # ── Operadores ──
    unary_operators=["neg"] + root_operators,
    binary_operators=["+", "-", "*", "/", "safe_pow(x, y) = sign(x) * abs(x)^y"],

    # ── Mappings y constraints ──
    extra_sympy_mappings=root_sympy_mappings,   # Ver §7.3.14
    nested_constraints=root_nested_constraints,  # Prohibir anidamiento de raíces
    constraints={"safe_pow": (9, 1)},           # Base compleja, exponente simple

    complexity_of_operators={
        "+": 1, "-": 1, "*": 1, "/": 2, "neg": 1,
        "safe_sqrt": 2, "safe_cbrt": 2,
        "safe_root4": 2, "safe_root5": 2, "safe_root6": 2,
        "safe_root7": 2, "safe_root8": 2, "safe_root9": 2, "safe_root10": 2,
        "safe_pow": 4,  # Penalizado para preferir raíces específicas
    },

    temp_equation_file=True,      # Archivos temporales para ecuaciones
    delete_tempfiles=True,        # Limpiar archivos temporales al terminar
)
```

> **Nota:** Los parámetros de diversidad evolutiva (V2) se han comentado temporalmente en `config.py` mientras se evalúa el impacto de los nuevos operadores de raíces. Ver §7.3.13 para la documentación completa de estos parámetros.

A continuación se justifica cada decisión de diseño:

#### 7.3.1 De `safe_sqrt` a `safe_pow`: La Evolución del Operador de Potencia

##### Versión 1: `safe_sqrt` (operador unario dedicado)

**Problema original:** La fórmula cuadrática contiene $\sqrt{b^2 - 4ac}$. Para que PySR pueda descubrir esta expresión, necesita un operador de raíz cuadrada. Sin embargo, durante la evolución genética se generan expresiones intermedias como $\sqrt{-7.3}$ que producen `NaN`, envenenan la población y destruyen las ramas evolutivas prometedoras.

**Solución rechazada — `bumper=True`:** PySR ofrece un mecanismo llamado `bumper` que reemplaza `NaN` por valores grandes. Sin embargo, esto **mata las expresiones con sqrt** porque les asigna un loss enorme, eliminándolas de la evolución antes de que puedan componerse en $\sqrt{b^2 - 4ac}$.

**Solución V1 — `safe_sqrt`:** Se definió un operador unario personalizado en Julia:

```julia
safe_sqrt(x) = sqrt(abs(x))
```

Esta solución funcionó para la cuadrática (ver §10), pero presentaba una **limitación fundamental**: solo permitía raíces cuadradas. Para ecuaciones cúbicas (que requieren $\sqrt[3]{\cdot}$) u otras raíces fraccionarias, habría que agregar operadores dedicados como `safe_cbrt`, `safe_4throot`, etc. — un enfoque que no escala.

##### Versión 3: `safe_pow` (operador binario generalizado)

**Motivación:** El benchmark V2 (43 casos) confirmó que `safe_sqrt` no podía resolver ecuaciones cúbicas (ej: `cubic_25`) porque PySR no tenía forma de expresar $a^{1/3}$. En lugar de agregar operadores hardcodeados para cada tipo de raíz, se reemplazó `safe_sqrt` por un **operador binario de potencia generalizada**:

```julia
safe_pow(x, y) = sign(x) * abs(x)^y
```

Con correspondencia en SymPy:

```python
extra_sympy_mappings = {"safe_pow": lambda x, y: sympy.sign(x) * sympy.Pow(sympy.Abs(x), y)}
```

**¿Por qué `sign(x) * abs(x)^y` y no `abs(x)^y`?**

La primera implementación usaba `abs(x)^y`, pero esto **destruye el signo para raíces impares**. Ejemplo:

$$(-8)^{1/3} = -2 \quad \text{pero} \quad |{-8}|^{1/3} = 8^{1/3} = +2$$

Al usar `sign(x) * abs(x)^y`:

$$\text{sign}(-8) \cdot |{-8}|^{1/3} = (-1) \cdot 2 = -2 \quad \checkmark$$

Esto preserva el signo correcto para raíces de cualquier orden, lo cual es crucial para ecuaciones cúbicas y otras con raíces impares.

**Generalización:** `safe_pow` subsume todos los operadores de raíz posibles:

| Operación | Expresión con `safe_pow` | Exponente |
|---|---|---|
| $\sqrt{x}$ | `safe_pow(x, 0.5)` | $0.5$ |
| $\sqrt[3]{x}$ | `safe_pow(x, 0.3333)` | $\approx 1/3$ |
| $\sqrt[4]{x}$ | `safe_pow(x, 0.25)` | $0.25$ |
| $x^n$ (cualquier potencia) | `safe_pow(x, n)` | $n$ |

PySR descubre tanto la base como el exponente durante la evolución, eliminando la necesidad de anticipar qué raíces serán necesarias.

##### El problema de convergencia de `safe_pow` y la solución con constraints

**Problema detectado:** Al ser un operador **binario**, `safe_pow(x, y)` tiene un espacio de búsqueda mucho mayor que `safe_sqrt(x)` (unario). PySR debe descubrir simultáneamente qué poner en la base **y** qué poner en el exponente. En la práctica, PySR tendía a descubrir patrones exponenciales como `safe_pow(-1.5, b)` (base constante, exponente variable) en lugar de `safe_pow(expr, 0.5)` (base expresión, exponente constante).

En el caso de la cuadrática completa (3 parámetros: $ax^2+bx+c=0$), V1 con `safe_sqrt` encontraba ambas raíces en ~1181s, mientras que V2 con `safe_pow` sin constraints encontraba solo 1 de 2 raíces en ~5275s.

**Solución — `constraints` de PySR** (referencia: [Tuning Guide de Miles Cranmer](https://astroautomata.com/PySR/tuning/)):

```python
constraints = {"safe_pow": (-1, 1)}
```

Este parámetro limita la **complejidad** de cada argumento del operador:
- Primer argumento (base): complejidad $\leq -1$ (sin límite, indicado por valor negativo)
- Segundo argumento (exponente): complejidad $\leq 1$ (solo una constante o una variable)

Esto **guía a PySR hacia `safe_pow(expresión_compleja, constante)`** en lugar de `safe_pow(constante, expresión_compleja)`. El exponente queda restringido a valores simples como `0.5`, `0.333`, etc., que PySR puede optimizar con BFGS. La base, sin restricción, puede contener la expresión arbitrariamente compleja que se necesite (ej: `b*b - 4*a*c`).

**Resultado:** Con este constraint, PySR redescubrió la fórmula cuadrática exacta en el Attempt 3 de la Rama 1, y en el Attempt 1 de la Rama 2 (ver §10.3).

**Restricción de anidamiento:** Se prohíbe `safe_pow` dentro de `safe_pow` para evitar expresiones como `safe_pow(safe_pow(x, 0.5), 0.3)` que aumentan complejidad sin utilidad:

```python
nested_constraints = {"safe_pow": {"safe_pow": 0}}
```

#### 7.3.2 ¿Por qué `square` no está como operador?

Inicialmente se incluyó el operador `square(x) = x²`. Sin embargo, PySR trataba `square` como un operador atómico y no descubría que $b^2 = b \cdot b$. Al removerlo, PySR usa `b * b` con el operador `*`, lo que le permite llegar a `safe_sqrt(b*b - 4*a*c)` componiendo sub-expresiones existentes.

#### 7.3.3 `parsimony = 0.0` y `model_selection`

La fórmula cuadrática tiene **complejidad ~18** (18 nodos en el árbol de expresión). Si se penaliza la complejidad (`parsimony > 0`), PySR prefiere expresiones simples pero inexactas. Al eliminar la penalización, se permite que la evolución explore expresiones complejas hasta alcanzar la fórmula exacta.

**Evolución de `model_selection`:**

- **V1/V2:** `model_selection = "accuracy"` — selecciona la ecuación con menor loss del Hall of Fame, independientemente de la complejidad.

- **V3:** `model_selection = "best"` — usa el **salto de parsimonia** (máxima curvatura del frente Pareto complejidad-error) para balancear precisión y simplicidad. Con los operadores unarios de raíces (§7.3.14), la ecuación cuadrática correcta tiene complejidad ~15-18 nodos y MSE ~0. Una aproximación exponencial incorrecta podría tener MSE marginalmente menor pero complejidad ~23-25 nodos. El criterio `"best"` selecciona la ecuación correcta porque es más parsimoniosa.

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

#### 7.3.7 `batching` (V1/V2) — Eliminado en V3

**Problema de RAM (V1/V2):** Con 1056 puntos de datos, 30 poblaciones y 50 individuos cada una, PySR evaluaba $30 \times 50 \times 1056 = 1{,}584{,}000$ predicciones por ciclo evolutivo, consumiendo RAM excesiva.

**Solución V1/V2:** `batching=True` hace que cada ciclo evalúe un **mini-batch aleatorio** de 200 puntos en lugar de los 1056 completos. Esto reduce el consumo de memoria por un factor de $\sim$5.

**Efecto secundario positivo — regularización estocástica:** Al igual que el mini-batch en deep learning, evaluar diferentes subconjuntos aleatorios en cada ciclo evita que PySR se sobreajuste a un subconjunto particular de puntos.

**Eliminación en V3:** Se eliminó el batching porque introducía **varianza estocástica** en el fitness: una expresión que matchea bien los 200 puntos del batch actual podría tener peor fitness con el siguiente batch. Con `procs=0` y datasets de ~512 puntos, el consumo de RAM es manejable (~4-6 GB). Al evaluar sobre **todos los puntos** en cada ciclo, el fitness es determinístico y la selección evolutiva es más estable. Ver §7.3.14 para detalles.

#### 7.3.8 `procs=0`: Un Solo Proceso Julia

PySR puede lanzar múltiples procesos Julia para evolución paralela. Sin embargo, cada proceso duplica el runtime de Julia en memoria. Con `procs=0`, toda la evolución ocurre en un único proceso, ahorrando centenares de MB de RAM a costa de velocidad.

#### 7.3.9 `turbo=True`: Optimizaciones en Julia

`turbo=True` activa optimizaciones agresivas en el backend de Julia, incluyendo operaciones SIMD (Single Instruction, Multiple Data) y evaluación vectorizada. Esto **acelera la evaluación de expresiones ~2-3 veces** sin afectar la calidad de los resultados. Dado el alto esfuerzo computacional configurado (275,000 ciclos), esta aceleración es importante para mantener los tiempos de ejecución en el rango de minutos y no de horas por rama.

#### 7.3.10 `complexity_of_operators`: Costos de Complejidad

El diccionario de costos asigna a cada operador un peso que contribuye al conteo de nodos del árbol.

**Configuración V1/V2:**

```python
complexity_of_operators = {
    "+": 1, "-": 1, "*": 1,     # Operaciones básicas: 1 nodo
    "/": 2,                       # División: 2 nodos (más costosa)
    "safe_pow": 2,                # Potencia generalizada: 2 nodos
    "neg": 1                      # Negación: 1 nodo
}
```

**Configuración V3 (con operadores de raíces):**

```python
complexity_of_operators = {
    "+": 1, "-": 1, "*": 1, "/": 2, "neg": 1,
    # Operadores de raíces: costo moderado (2)
    "safe_sqrt": 2, "safe_cbrt": 2,
    "safe_root4": 2, "safe_root5": 2, "safe_root6": 2,
    "safe_root7": 2, "safe_root8": 2, "safe_root9": 2, "safe_root10": 2,
    # safe_pow: penalizado (4) para preferir raíces específicas
    "safe_pow": 4,
}
```

**Justificación de la penalización de `safe_pow`:**

Con `maxsize=25` y `safe_pow` a complejidad 4, una expresión puede usar ~6 instancias de `safe_pow` o ~12 operadores de raíces específicos. Esto **guía a PySR hacia los operadores unarios de raíces** cuando son suficientes (raíces de orden 2-10), reservando `safe_pow` para casos donde realmente se necesita un exponente arbitrario. Ver §7.3.14 para detalles de la estrategia de desambiguación.

> **Nota histórica:** En V2, `safe_pow` tenía costo 2. Esto era apropiado cuando era el único operador de raíces disponible. Al agregar operadores unarios específicos en V3, se aumentó a 4 para crear una preferencia evolutiva hacia las raíces dedicadas.

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

#### 7.3.13 Versión 2: Parámetros de Diversidad Evolutiva

> **Estado:** Validada. El benchmark V2 (43 casos) alcanzó **96.1% de raíces descubiertas** y **41/43 casos perfectos**, frente al 77.6% y 28/43 de la V1 (ver §12).

##### Diagnóstico del problema (identificado en V1)

El benchmark de la Versión 1 (43 casos de prueba) arrojó una **tasa de descubrimiento de raíces del 77.6%** con un patrón de fallo dominante: PySR descubría consistentemente las raíces positivas (por ejemplo, $\sqrt{a}$, $a$, $2a$) pero no sus variantes negativas ($-\sqrt{a}$, $-a$, $-2a$). El análisis reveló que el problema no es de representabilidad — PySR dispone del operador `neg` — sino de **convergencia prematura** de la búsqueda evolutiva.

##### Análisis teórico: la presión selectiva del Tournament Selection

PySR utiliza **tournament selection** como mecanismo de selección de padres. En cada evento de selección, se eligen $n$ individuos al azar de la población y se selecciona al mejor con probabilidad $p$, al segundo mejor con probabilidad $p(1-p)$, y así sucesivamente. La probabilidad de seleccionar al individuo de ranking $k$ en un torneo de tamaño $n$ es:

$$P(\text{seleccionar ranking } k) = p \cdot (1-p)^{k-1}, \quad k = 1, 2, \ldots, n$$

Con los valores por defecto de PySR ($p = 0.982$, $n = 15$):

| Ranking | Probabilidad | Interpretación |
|---------|-------------|----------------|
| 1° (mejor) | $0.982$ | 98.2% |
| 2° | $0.982 \times 0.018 = 0.0177$ | 1.77% |
| 3° | $0.982 \times 0.018^2 \approx 0.0003$ | 0.03% |
| 4° en adelante | $\approx 0$ | ~0% |

Esto constituye **de facto una selección por truncamiento** (truncation selection): solo el mejor individuo se reproduce. Goldberg y Deb (1991) demostraron que la velocidad de convergencia de una población depende directamente de la presión selectiva: cuanto mayor es la probabilidad de seleccionar al mejor individuo, más rápido la población entera converge a clones de dicho individuo.

Blickle y Thiele (1996) formalizaron la **intensidad de selección** del tournament selection y demostraron que torneos grandes con alta probabilidad de selección producen rápida pérdida de diversidad genética ("genetic drift"). Con $p = 0.982$ y $n = 15$, la población de 50 individuos converge esencialmente a clones del mejor individuo en pocas decenas de generaciones.

##### Consecuencia concreta

Cuando PySR busca una expresión para datos donde $y = -\sqrt{a}$, la convergencia prematura impide el descubrimiento de la forma exacta. La secuencia típica es:

1. **Generaciones 1–5:** Las expresiones son aleatorias. Algunas usan `safe_sqrt(a)` (que siempre retorna $\geq 0$).
2. **Generación ~10:** Una expresión como `safe_sqrt(a) * C₁` con $C_1 \approx -0.8$ (optimizada por BFGS) obtiene un MSE decente — no perfecto, pero mucho mejor que las expresiones aleatorias iniciales.
3. **Generaciones 15–20:** Como esta expresión es la mejor, y la probabilidad de seleccionarla es 98.2%, casi todos los hijos se generan a partir de ella. La población entera se llena de variantes de `safe_sqrt(a) * C` con $C$ cercano a $-0.8$.
4. **Generaciones 30+:** La expresión correcta `neg(safe_sqrt(a))` requiere **componer** dos operadores (`neg` + `safe_sqrt`). Para descubrirla, un individuo con estructura diferente (que use `neg(...)`) necesitaría sobrevivir y reproducirse — pero la presión selectiva los eliminó hace decenas de generaciones.
5. **Estado final:** BFGS optimiza la constante hasta $C \approx -0.9998$, produciendo un MSE muy bajo ($\sim 10^{-6}$) pero no exactamente $0$. PySR queda atascado en este óptimo local y nunca alcanza `neg(safe_sqrt(a))`, cuyo MSE sería $= 0$.

##### Segundo problema: migración inexistente

El parámetro `fraction_replaced` controla qué fracción de cada población se reemplaza con migrantes de otras poblaciones en cada generación. Con el valor por defecto de PySR:

$$\text{migrantes/generación} = \text{population\_size} \times \text{fraction\_replaced} = 50 \times 0.00036 = 0.018$$

Es decir, **cero individuos** migran por generación. Las 30 poblaciones (islas) evolucionan en **completo aislamiento**, desperdiciando la arquitectura multi-isla de PySR. Whitley, Rana y Heckendorn (1999) establecieron que tasas de migración del 1-10% de la población son óptimas para el modelo de islas; por debajo de eso, las islas degeneran en ejecuciones independientes sin intercambio genético.

##### Configuración Versión 2

Se modificaron 6 parámetros del algoritmo evolutivo de PySR para preservar la diversidad poblacional:

```python
model = PySRRegressor(
    # ... (todos los parámetros de la Versión 1 se mantienen) ...
    
    # ── Parámetros de diversidad (Versión 2) ──
    tournament_selection_p=0.75,         # (default PySR: 0.982)
    tournament_selection_n=8,            # (default PySR: 15)
    probability_negate_constant=0.05,    # (default PySR: 0.00743)
    fraction_replaced=0.05,              # (default PySR: 0.00036)
    crossover_probability=0.066,         # (default PySR: 0.0259)
    weight_mutate_operator=0.5,          # (default PySR: 0.293)
)
```

##### Justificación detallada de cada parámetro

**1. `tournament_selection_p`: 0.982 → 0.75**

Con $p = 0.75$ y $n = 8$, la distribución de selección cambia cualitativamente:

| Ranking | Antes ($p=0.982$, $n=15$) | Después ($p=0.75$, $n=8$) |
|---------|--------------------------|---------------------------|
| 1° | 98.2% | **75.0%** |
| 2° | 1.77% | **18.75%** |
| 3° | 0.03% | **4.69%** |
| 4° | ~0% | **1.17%** |

Ahora el segundo y tercer mejor individuo tienen probabilidades **reales** de reproducirse. Esto permite que expresiones alternativas (como `neg(safe_sqrt(a))` frente a `safe_sqrt(a) * C`) coexistan y compitan en la población durante más generaciones antes de que una domine.

- **Referencia:** Goldberg, D. E. & Deb, K. (1991). "A comparative analysis of selection schemes used in genetic algorithms." *Foundations of Genetic Algorithms*, 1, 69-93.
- **Referencia:** Luke, S. & Panait, L. (2002). "Is the perfect the enemy of the good?" *Proceedings of GECCO 2002*, pp. 820-828. (Demostración experimental de que menor presión selectiva mejora exploración en GP.)

**2. `tournament_selection_n`: 15 → 8**

El tamaño del torneo determina la **granularidad** de la presión selectiva. Blickle y Thiele (1996) mostraron que la intensidad de selección crece con $\sqrt{\ln(n)}$. Reducir de 15 a 8 disminuye la presión selectiva un ~15% adicional, complementando la reducción de $p$.

- **Referencia:** Blickle, T. & Thiele, L. (1996). "A comparison of selection schemes used in evolutionary algorithms." *Evolutionary Computation*, 4(4), 361-394.

**3. `probability_negate_constant`: 0.00743 → 0.05**

Este parámetro controla la probabilidad de que, durante una mutación, PySR niegue una constante numérica en la expresión. Con el valor por defecto (0.743%), esta mutación ocurre aproximadamente **una vez cada 135 mutaciones**. Al subir a 5%, ocurre **una vez cada 20 mutaciones** — un aumento de ~7×.

Esta mutación es directamente relevante para el patrón de fallo observado: si PySR tiene una expresión `safe_sqrt(a) * 1.0`, negar la constante produce `safe_sqrt(a) * (-1.0)`, que es equivalente a `neg(safe_sqrt(a))`. Con el valor por defecto, esta mutación es demasiado rara para competir con la convergencia prematura.

**4. `fraction_replaced`: 0.00036 → 0.05**

Con $0.05$, el número de migrantes por generación es:

$$50 \times 0.05 = 2.5 \text{ individuos/generación}$$

Esto activa efectivamente el modelo de islas de PySR: si una isla descubre `neg(safe_sqrt(a))` mientras otra convergió a `safe_sqrt(a)`, la expresión negada puede **migrar** a otras islas y propagarse. Sin migración, un descubrimiento en una isla muere en esa isla.

- **Referencia:** Whitley, D., Rana, S. & Heckendorn, R. B. (1999). "The island model genetic algorithm: On separability, population size and convergence." *Journal of Computing and Information Technology*, 7(1), 33-47.

**5. `crossover_probability`: 0.0259 → 0.066**

El cruzamiento (crossover) toma subárboles de dos individuos diferentes y los intercambia. Si un individuo contiene `safe_sqrt(a)` y otro contiene `neg(...)`, un cruce puede producir `neg(safe_sqrt(a))` directamente. Al aumentar la probabilidad de cruce de 2.6% a 6.6% (~2.5×), se facilita la composición de subexpresiones provenientes de individuos distintos.

El valor de 0.066 se eligió moderadamente para no desestabilizar la búsqueda: en programación genética, cruzamientos demasiado frecuentes pueden ser destructivos (Koza, 1992), ya que intercambiar subárboles aleatorios a menudo produce expresiones inválidas o con peor fitness.

- **Referencia:** Koza, J. R. (1992). *Genetic Programming: On the Programming of Computers by Means of Natural Selection.* MIT Press. (Capítulo 6: análisis de la probabilidad de crossover y su efecto en la convergencia.)

**6. `weight_mutate_operator`: 0.293 → 0.5**

Este peso relativo controla con qué frecuencia PySR muta un operador por otro (por ejemplo, cambia `+` por `-`, o `safe_sqrt` por `neg`). Al aumentar de 0.293 a 0.5, PySR realiza ~70% más mutaciones de tipo "cambio de operador".

Esta mutación es estructuralmente relevante: permite que PySR explore variantes topológicas del árbol de expresión sin cambiar su forma. Una expresión `safe_sqrt(a + b)` podría mutar a `neg(a + b)` mediante un solo cambio de operador. Esto complementa el crossover al ofrecer un mecanismo **local** de diversificación estructural.

##### Resumen de cambios y su efecto combinado

| Parámetro | Default PySR | V1 (base) | V2 (diversidad) | Efecto |
|-----------|-------------|-----------|-----------------|--------|
| `tournament_selection_p` | 0.982 | 0.982 (default) | **0.75** | P(2°) de 1.8% → 18.8% |
| `tournament_selection_n` | 15 | 15 (default) | **8** | Torneo más pequeño → menos presión |
| `probability_negate_constant` | 0.00743 | 0.00743 (default) | **0.05** | 7× más negaciones de constantes |
| `fraction_replaced` | 0.00036 | 0.00036 (default) | **0.05** | 0 → 2.5 migrantes/generación |
| `crossover_probability` | 0.0259 | 0.0259 (default) | **0.066** | 2.5× más cruces entre individuos |
| `weight_mutate_operator` | 0.293 | 0.293 (default) | **0.5** | 70% más cambios de operador |

Los 6 cambios actúan de forma sinérgica:
- Parámetros 1-2 **preservan diversidad** al reducir la presión selectiva.
- Parámetro 4 **propaga diversidad** entre islas mediante migración.
- Parámetros 3, 5, 6 **generan diversidad** al ampliar el repertorio de mutaciones y cruces.

##### Principio teórico unificador

Estos cambios implementan, con las herramientas disponibles en PySR, el mismo principio que la **ε-lexicase selection** (La Cava et al., 2016; Orzechowski et al., 2022): preservar diversidad poblacional para que la búsqueda evolutiva explore múltiples nichos del espacio de expresiones simultáneamente, en lugar de converger prematuramente a un solo nicho.

La diferencia es que ε-lexicase logra esto cambiando el mecanismo de selección completo (de tournament a lexicase), mientras que aquí se logra un efecto análogo reduciendo la presión selectiva del tournament existente y compensando con mayor migración y diversidad mutacional.

- **Referencia:** La Cava, W., Helmuth, T., Spector, L. & Moore, J. H. (2019). "A probabilistic and multi-objective analysis of lexicase selection and ε-lexicase selection." *Evolutionary Computation*, 27(3), 377-402.
- **Referencia:** Orzechowski, P., La Cava, W. & Moore, J. H. (2022). "Where are we now? A large benchmark study of recent symbolic regression methods." *Proceedings of NeurIPS 2022.*

#### 7.3.14 Versión 3: Operadores Unarios de Raíces n-ésimas

> **Estado:** Validada. El caso `quadratic_19_full_abc` ($ax^2 + bx + c = 0$) pasó de 45.5% de cobertura (V2 con solo `safe_pow`) a **100% de cobertura** (V3 con operadores unarios de raíces).

##### Diagnóstico del problema (identificado en V2)

El benchmark V2 mostró que el caso más complejo del catálogo — la ecuación cuadrática completa con tres parámetros libres ($ax^2 + bx + c = 0$) — no lograba descubrirse correctamente. Mientras que versiones anteriores con `safe_sqrt` unario encontraban ambas raíces, V2 con solo `safe_pow` binario producía expresiones erróneas con **cobertura del 45.5%**.

**Análisis del Hall of Fame de V2:** Las ecuaciones descubiertas tenían patrones como:

```
safe_pow(1.4931327, c) - (safe_pow(-1.2609383, c) / (a * 1.4765537))
safe_pow(-1.4893247, b) / a
```

En lugar del patrón correcto:

```
safe_pow(b*b - 4*a*c, 0.5)  →  √(b² - 4ac)
```

##### El problema: ambigüedad exponencial/raíz de `safe_pow`

El operador binario `safe_pow(x, y)` puede expresar **dos familias de funciones** completamente diferentes:

| Patrón | Ejemplo | Función matemática |
|--------|---------|-------------------|
| `safe_pow(constante, variable)` | `safe_pow(2.0, b)` | $2^b$ (exponencial) |
| `safe_pow(expresión, constante)` | `safe_pow(x, 0.5)` | $\sqrt{x}$ (raíz) |

El constraint `(-1, 1)` intenta restringir el segundo argumento (exponente) a complejidad 1, pero **no elimina la ambigüedad**: tanto `safe_pow(2.0, b)` como `safe_pow(b*b - 4*a*c, 0.5)` satisfacen el constraint.

**¿Por qué PySR prefiere exponenciales?**

La evolución genética tiende hacia exponenciales porque son **numéricamente más fáciles de optimizar**:

1. **Gradiente más suave:** $\frac{\partial}{\partial c}(2^b)$ es continuo y suave para todo $b$, mientras que $\frac{\partial}{\partial x}(\sqrt{x})$ tiene una singularidad en $x=0$.

2. **BFGS converge más rápido:** El optimizador de constantes de PySR (BFGS) puede ajustar la base de una exponencial más eficientemente que optimizar expresiones bajo una raíz.

3. **Fitness parcial temprano:** Una exponencial como `safe_pow(1.5, b)` produce valores finitos para todo $b$, obteniendo un MSE moderado desde la primera generación. En cambio, `safe_pow(b*b - 4*a*c, 0.5)` requiere que PySR **descubra primero** la expresión completa del discriminante antes de obtener buen fitness.

Este fenómeno constituye un **atractor evolutivo**: la presión selectiva arrastra a PySR hacia exponenciales porque producen fitness inicial más alto, aunque la expresión objetivo (raíz cuadrada) tenga fitness final perfecto.

##### La solución: operadores unarios de raíces específicas

La solución es **desambiguar** las raíces de las exponenciales mediante operadores **unarios** dedicados. Un operador unario `safe_sqrt(x)` solo puede expresar raíces — es **imposible** escribir una exponencial con él.

Se implementaron 9 operadores unarios para raíces de orden 2 a 10:

```julia
# Raíces con Julia nativo (sintaxis directa)
safe_sqrt(x) = sqrt(abs(x))              # Raíz 2: √|x|
safe_cbrt(x) = cbrt(x)                   # Raíz 3: ∛x (cbrt maneja negativos)

# Raíces por composición (evita errores de sintaxis en Julia)
safe_root4(x) = sqrt(sqrt(abs(x)))       # Raíz 4: √√|x|
safe_root6(x) = cbrt(sqrt(abs(x)))       # Raíz 6: ∛√|x|
safe_root8(x) = sqrt(sqrt(sqrt(abs(x)))) # Raíz 8: √√√|x|
safe_root9(x) = cbrt(cbrt(x))            # Raíz 9: ∛∛x

# Raíces con exponenciación explícita
safe_root5(x) = sign(x) * sqrt(sqrt(abs(x))) * abs(x)^0.05   # Raíz 5: x^0.2
safe_root7(x) = sign(x) * abs(x)^(1.0/7.0)                   # Raíz 7: x^(1/7)
safe_root10(x) = sqrt(sqrt(sqrt(abs(x)))) * abs(x)^0.025     # Raíz 10: x^0.1
```

**Diseño de cada operador:**

- **Raíces pares (2, 4, 6, 8, 10):** Usan `abs(x)` porque la raíz par de un negativo no es real. PySR debe descubrir que el argumento es positivo (ej: $b^2 - 4ac \geq 0$ cuando hay raíces reales).

- **Raíces impares (3, 5, 7, 9):** Usan `sign(x) * abs(x)^(1/n)` para preservar el signo. Ejemplo: $\sqrt[3]{-8} = -2$.

- **Composición vs. exponenciación:** Cuando es posible, se prefiere composición (`sqrt(sqrt(x))` para raíz 4) porque evita potencias fraccionarias explícitas que pueden causar errores numéricos en Julia. Solo cuando no hay composición exacta (raíces 5, 7, 10) se usa exponenciación.

**Mappings a SymPy:**

```python
root_sympy_mappings = {
    "safe_sqrt": lambda x: sympy.sqrt(sympy.Abs(x)),
    "safe_cbrt": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 3)),
    "safe_root4": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 4)),
    "safe_root5": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 5)),
    "safe_root6": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 6)),
    "safe_root7": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 7)),
    "safe_root8": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 8)),
    "safe_root9": lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 9)),
    "safe_root10": lambda x: sympy.Pow(sympy.Abs(x), sympy.Rational(1, 10)),
    "safe_pow": lambda x, y: sympy.sign(x) * sympy.Pow(sympy.Abs(x), y),
}
```

##### Constraints de anidamiento entre raíces

Para evitar expresiones redundantes como `safe_sqrt(safe_sqrt(x))` (equivalente a `safe_root4(x)`) o `safe_sqrt(safe_cbrt(x))` (equivalente a `safe_root6(x)`), se prohíbe el anidamiento de operadores de raíces entre sí:

```python
root_names = ["safe_sqrt", "safe_cbrt", "safe_root4", "safe_root5", "safe_root6",
              "safe_root7", "safe_root8", "safe_root9", "safe_root10"]

nested_constraints = {name: {n: 0 for n in root_names} for name in root_names}
nested_constraints["safe_pow"] = {"safe_pow": 0}
```

Esto genera una matriz de restricciones $9 \times 9$ donde ningún operador de raíz puede contener a otro como hijo directo.

##### Penalización de `safe_pow` con `complexity_of_operators`

Se mantiene `safe_pow` como operador disponible para expresiones no estándar (potencias arbitrarias), pero se **penaliza** su uso asignándole complejidad 4 frente a complejidad 2 de los operadores de raíces:

```python
complexity_of_operators = {
    "+": 1, "-": 1, "*": 1, "/": 2, "neg": 1,
    "safe_sqrt": 2, "safe_cbrt": 2,
    "safe_root4": 2, "safe_root5": 2, "safe_root6": 2,
    "safe_root7": 2, "safe_root8": 2, "safe_root9": 2, "safe_root10": 2,
    "safe_pow": 4,  # Penalizado para preferir raíces específicas
}
```

Dado que `maxsize=25`, una expresión puede usar ~12 raíces específicas o ~6 instancias de `safe_pow`. Esto **guía a PySR hacia los operadores de raíces** cuando son suficientes, reservando `safe_pow` para casos donde realmente se necesita un exponente no entero.

##### Cambio a `model_selection="best"` (salto de parsimonia)

Se modificó `model_selection` de `"accuracy"` a `"best"`:

```python
model_selection = "best"  # (antes: "accuracy")
```

**¿Por qué?**

- `"accuracy"` selecciona la ecuación con menor MSE del Hall of Fame, independientemente de la complejidad. Esto puede devolver expresiones de 25 nodos que sobreajustan cuando existe una expresión de 10 nodos igualmente precisa.

- `"best"` busca el **salto de parsimonia**: la ecuación que ofrece la mayor reducción de error relativa a su aumento de complejidad. Formalmente, selecciona el punto de máxima curvatura en el frente de Pareto complejidad-error.

Con los operadores de raíces unarios, la ecuación cuadrática correcta tiene complejidad ~15-18 nodos y MSE ~0. Una aproximación exponencial incorrecta podría tener MSE marginalmente menor (por sobreajuste) pero complejidad ~23-25 nodos. El criterio `"best"` selecciona la ecuación cuadrática correcta porque es más parsimoniosa.

- **Referencia:** Cranmer, M. (2023). "Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl." *arXiv:2305.01582*. Sección 3.2: "Pareto-optimal model selection."

##### Eliminación de `batching`

Se eliminó el batching del modelo:

```python
# ANTES (V2):
batching = True
batch_size = 200

# AHORA (V3):
# (sin batching — se eliminan ambas líneas)
```

**Justificación:**

El batching evaluaba cada expresión candidata sobre 200 puntos aleatorios por ciclo evolutivo, reduciendo consumo de RAM. Sin embargo, introducía **varianza estocástica** en el fitness: una expresión que matchea bien los 200 puntos del batch actual podría tener peor fitness con el siguiente batch.

Con `procs=0` (un solo proceso Julia) y los constraints implementados, el consumo de RAM es manejable (~4-6 GB para 512-1000 puntos). Al evaluar sobre **todos los puntos** en cada ciclo, el fitness es determinístico y la selección evolutiva es más estable.

##### Configuración completa V3

```python
model = PySRRegressor(
    niterations=500,
    populations=30,
    population_size=50,
    ncycles_per_iteration=550,
    maxsize=25,
    parsimony=0.0,
    turbo=True,
    procs=0,
    model_selection="best",  # Salto de parsimonia

    # ── Operadores unarios: raíces específicas ──
    unary_operators=[
        "neg",
        "safe_sqrt(x) = sqrt(abs(x))",
        "safe_cbrt(x) = cbrt(x)",
        "safe_root4(x) = sqrt(sqrt(abs(x)))",
        "safe_root5(x) = sign(x) * sqrt(sqrt(abs(x))) * abs(x)^0.05",
        "safe_root6(x) = cbrt(sqrt(abs(x)))",
        "safe_root7(x) = sign(x) * abs(x)^(1.0/7.0)",
        "safe_root8(x) = sqrt(sqrt(sqrt(abs(x))))",
        "safe_root9(x) = cbrt(cbrt(x))",
        "safe_root10(x) = sqrt(sqrt(sqrt(abs(x)))) * abs(x)^0.025",
    ],

    # ── Operadores binarios: aritmética + potencia generalizada ──
    binary_operators=["+", "-", "*", "/", "safe_pow(x, y) = sign(x) * abs(x)^y"],

    extra_sympy_mappings=root_sympy_mappings,  # Ver arriba
    nested_constraints=root_nested_constraints,  # Prohibir anidamiento de raíces
    constraints={"safe_pow": (9, 1)},  # Base compleja, exponente simple

    complexity_of_operators={
        "+": 1, "-": 1, "*": 1, "/": 2, "neg": 1,
        "safe_sqrt": 2, "safe_cbrt": 2,
        "safe_root4": 2, "safe_root5": 2, "safe_root6": 2,
        "safe_root7": 2, "safe_root8": 2, "safe_root9": 2, "safe_root10": 2,
        "safe_pow": 4,
    },

    temp_equation_file=True,
    delete_tempfiles=True,
)
```

##### Resultado: caso `quadratic_19_full_abc`

Con la configuración V3, PySR redescubrió ambas raíces de la ecuación cuadrática:

**Rama 1 (raíz negativa):**
```
neg(((b * 0.5) + safe_sqrt((a * c) - ((b * b) * 0.25))) / a)
```
Equivalente a: $x_1 = \frac{-b - \sqrt{b^2 - 4ac}}{2a}$

**Rama 2 (raíz positiva):**
```
((b * -0.5) + safe_sqrt((-1 * (c * a)) + ((b * b) * 0.25))) / a
```
Equivalente a: $x_2 = \frac{-b + \sqrt{b^2 - 4ac}}{2a}$

Ambas ecuaciones matchean el 100% de los puntos de datos con tolerancia $\varepsilon = 0.005$.

##### Resumen de la evolución V1 → V2 → V3

| Versión | Operador de raíces | Problema | Solución |
|---------|-------------------|----------|----------|
| V1 | `safe_sqrt` (unario) | Solo raíces cuadradas | Funciona para cuadrática |
| V2 | `safe_pow` (binario) | Ambigüedad exponencial/raíz | Agregar diversidad evolutiva |
| V3 | Raíces 2-10 (unarios) + `safe_pow` | Exponenciales dominaban | Desambiguar con operadores específicos |

**Principio general:** Cuando un operador generalizado (como `safe_pow`) tiene múltiples interpretaciones semánticas, la evolución genética tiende hacia la interpretación numéricamente más fácil. Para forzar la interpretación deseada (raíces), se deben agregar operadores específicos que **solo** puedan expresar esa interpretación.

- **Referencia:** Koza, J. R. (1992). *Genetic Programming*. MIT Press. Capítulo 7: "Choice of function and terminal sets" — discusión de cómo la elección de operadores afecta la trayectoria evolutiva.
- **Referencia:** Cranmer, M. (2023). "PySR Tuning Guide." https://astroautomata.com/PySR/tuning/ — recomendaciones sobre diseño de operadores personalizados.

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

#### 9.3.3 Ambigüedad de Signo por `safe_pow` / `safe_sqrt`

PySR usa `safe_pow(h, y) = sign(h) * |h|^y` (o en V1, `safe_sqrt(h) = sqrt(|h|)`). Para potencias fraccionarias como $y = 0.5$, esto se reduce algebraicamente a una raíz cuadrada con ambigüedad de signo: `safe_pow(h, 0.5)` puede representar $\sqrt{h}$ o $-\sqrt{-h}$ dependiendo del signo de $h$.

Para la verificación, se introducen variables auxiliares y se prueban ambas variantes:

- Variante 1: $s^2 = h$ (argumento directo)
- Variante 2: $s^2 = -h$ (argumento negado)

Si alguna de las dos produce residuo 0, la expresión es válida.

> **Retrocompatibilidad:** El módulo `verify.py` maneja tanto expresiones con `safe_pow` como con el antiguo `safe_sqrt`, aplicando las transformaciones de parsing correspondientes a cada formato.

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

#### V1 (con `safe_sqrt`)

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

#### V3 (con `safe_pow` + constraints)

Tras reemplazar `safe_sqrt` por `safe_pow` y añadir `constraints={"safe_pow": (-1, 1)}`, PySR redescubrió la fórmula cuadrática usando el operador generalizado.

**Rama 1** (raíz menor, $x_2$):

PySR encontró en el intento 3, con complejidad 19 y loss $2.65 \times 10^{-13}$:

$$x_2 = \frac{\text{safe\_pow}\bigl((a \cdot c) + (b \cdot b) \cdot (-0.25),\; 0.5\bigr) + b \cdot (-0.5)}{a}$$

que se racionaliza a:

$$x_2 = \frac{\sqrt{ac - b^2/4} - b/2}{a}$$

Dado que para datos con discriminante $\geq 0$ se tiene $ac - b^2/4 \leq 0$, y `safe_pow` aplica `sign(x) * abs(x)^y`:

$$\text{safe\_pow}(ac - b^2/4,\; 0.5) = \text{sign}(ac - b^2/4) \cdot |ac - b^2/4|^{0.5} = -\sqrt{b^2/4 - ac} = -\frac{\sqrt{b^2 - 4ac}}{2}$$

Por lo tanto:

$$x_2 = \frac{-\sqrt{b^2 - 4ac}/2 - b/2}{a} = \frac{-b - \sqrt{b^2 - 4ac}}{2a} \quad \checkmark$$

Cobertura: **512/512 puntos (100%)**.

**Rama 2** (raíz mayor, $x_1$):

PySR encontró en el intento 1 (!), con complejidad 19 y loss $8.09 \times 10^{-15}$:

$$x_1 = \bigl(\text{safe\_pow}\bigl(b \cdot b - (c \cdot 4) \cdot a,\; 0.5\bigr) - b\bigr) \cdot \frac{0.5}{a}$$

que se racionaliza directamente a la forma clásica:

$$x_1 = \frac{\sqrt{b^2 - 4ac} - b}{2a} = \frac{-b + \sqrt{b^2 - 4ac}}{2a} \quad \checkmark$$

Cobertura: **512/512 puntos (100%)**. Tiempo total: **1261.5 segundos** (~21 minutos).

> **Observación:** La Rama 2 logró una precisión mayor (loss $8 \times 10^{-15}$ vs $2.6 \times 10^{-13}$) y convergió en el primer intento. Esto se debe a que PySR expresó el discriminante directamente como $b^2 - 4ac$ (positivo en los datos), evitando la indirección de `sign()` que introduce ruido numérico adicional.

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

Ambas versiones (V1 con `safe_sqrt` y V3 con `safe_pow`) producen expresiones algebraicamente equivalentes:

| Rama | Expresión Racionalizada | Algebraica | Gröbner | Estado |
|------|-------------------------|:----------:|:-------:|:------:|
| 1 | $\frac{-b - \sqrt{b^2-4ac}}{2a}$ | ✓ | ✓ | **VÁLIDA** |
| 2 | $\frac{-b + \sqrt{b^2-4ac}}{2a}$ | — | ✓ | **VÁLIDA** |

La verificación con Gröbner es idéntica en ambos casos: independientemente de si PySR usó `safe_sqrt(b²-4ac)` o `safe_pow(b²-4ac, 0.5)`, la variable auxiliar $s$ y la relación $s^2 = b^2 - 4ac$ son las mismas.

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
| 21 | `tournament_selection_p = 0.75` (V2) | Default PySR: 0.982 | Con $p=0.982$ el mejor individuo se selecciona 98.2% de las veces → convergencia prematura (Goldberg & Deb, 1991). Con $p=0.75$: P(2°)=18.8%, P(3°)=4.7% → diversidad real |
| 22 | `tournament_selection_n = 8` (V2) | Default PySR: 15 | Torneos más pequeños reducen la intensidad de selección ~15% adicional (Blickle & Thiele, 1996) |
| 23 | `probability_negate_constant = 0.05` (V2) | Default PySR: 0.00743 | 7× más probable que PySR niegue constantes durante mutación. Directamente relevante para el patrón de fallo de raíces negativas |
| 24 | `fraction_replaced = 0.05` (V2) | Default PySR: 0.00036 | 50×0.05=2.5 migrantes/gen, activando el modelo de islas. Con 0.00036, cero migrantes → islas aisladas (Whitley et al., 1999) |
| 25 | `crossover_probability = 0.066` (V2) | Default PySR: 0.0259 | 2.5× más cruces facilita composición de subexpresiones de diferentes individuos (Koza, 1992) |
| 26 | `weight_mutate_operator = 0.5` (V2) | Default PySR: 0.293 | 70% más mutaciones de operador → mayor exploración estructural del espacio de expresiones |
| 27 | `safe_pow(x,y) = sign(x)*abs(x)^y` (V3) | `safe_sqrt(x) = sqrt(abs(x))` (V1) | Operador binario generalizado: subsume sqrt, cbrt, y cualquier potencia fraccionaria. Elimina la necesidad de hardcodear operadores por tipo de raíz |
| 28 | `sign(x)*abs(x)^y` en vez de `abs(x)^y` | `abs(x)^y` (implementación inicial de safe_pow) | `abs(x)^y` destruye el signo para raíces impares: $(-8)^{1/3}=−2$ pero $\|{-8}\|^{1/3}=+2$. Con `sign(x)` se preserva el signo |
| 29 | `constraints={"safe_pow": (-1, 1)}` (V3) | Sin constraints | Restringe el exponente a complejidad 1 (constante o variable simple). Guía a PySR hacia `safe_pow(expr, 0.5)` en vez de `safe_pow(const, variable)` (Cranmer, Tuning Guide) |
| 30 | `complexity_of_operators: safe_pow=2` (V3) | `safe_pow=3` (inicial) | Con costo 3, PySR no lograba alcanzar la fórmula cuadrática dentro del `maxsize=25`. Al reducir a 2 (igual que `/` y `safe_sqrt` en V1), se restauró la capacidad de descubrimiento |

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
9. **Versión 2 — Parámetros de diversidad (validada):** Benchmark de 43 casos reveló convergencia prematura como causa dominante de fallo (77.6% de raíces descubiertas). Se reconfiguraron 6 parámetros evolutivos de PySR para reducir presión selectiva, activar migración entre islas, y aumentar diversidad mutacional, basándose en Goldberg & Deb (1991), Blickle & Thiele (1996), Whitley et al. (1999) y Koza (1992). **Resultado:** 96.1% raíces descubiertas, 41/43 casos perfectos.
10. **Corrección del bug de `neg()` en métricas:** Durante la evaluación del benchmark V2, se descubrió que `metrics.py` no parseaba correctamente el operador `neg()` de PySR, produciendo errores de evaluación que subestimaban los resultados reales. La corrección consistió en añadir `_neg = lambda x: -x` al diccionario local de `sympify`. Tras la corrección, los resultados V2 mejoraron significativamente.
11. **Reemplazo de `safe_sqrt` por `safe_pow`:** El benchmark V2 demostró que `safe_sqrt` no podía resolver ecuaciones cúbicas (ej: `cubic_25` requiere $a^{1/3}$). Se reemplazó por `safe_pow(x,y) = sign(x) * abs(x)^y`, un operador binario que generaliza todas las potencias fraccionarias.
12. **Corrección de signo en `safe_pow`:** La implementación inicial `abs(x)^y` destruía el signo para raíces impares ($(-8)^{1/3}$ daba $+2$ en vez de $-2$). Se corrigió a `sign(x) * abs(x)^y`.
13. **Constraints para `safe_pow`:** Al ser binario, `safe_pow` tenía un espacio de búsqueda mucho mayor que `safe_sqrt`. Se añadió `constraints={"safe_pow": (-1, 1)}` para restringir el exponente a complejidad 1, y se redujo `complexity_of_operators["safe_pow"]` de 3 a 2. Con estos dos cambios, PySR redescubrió la fórmula cuadrática exacta (§10.3).

---

## 12. Resultados del Benchmark

El pipeline se evaluó mediante un benchmark de **43 casos de prueba** organizados en 6 categorías (linear, quadratic, cubic, radical, special, multi_param) y 3 niveles de dificultad (easy, medium, hard).

### 12.1 Versión 1 (V1): Configuración Base con `safe_sqrt`

| Métrica | Resultado |
|---|---|
| Pipeline completado sin error | 100% (43/43) |
| Raíces descubiertas (global) | **77.6%** |
| Casos perfectos (100% raíces) | **28/43** (65.1%) |
| Cobertura promedio por rama | 93.2% |

**Patrón de fallo dominante:** PySR descubría las raíces positivas ($\sqrt{a}$, $a$) pero no las negativas ($-\sqrt{a}$, $-a$). Diagnóstico: convergencia prematura del tournament selection con parámetros por defecto de PySR (ver §7.3.13).

### 12.2 Versión 2 (V2): Parámetros de Diversidad + `safe_sqrt`

| Métrica | V1 | V2 | Mejora |
|---|---|---|---|
| Raíces descubiertas | 77.6% | **96.1%** | +18.5pp |
| Casos perfectos | 28/43 | **41/43** | +13 |
| Cobertura promedio | 93.2% | **99.4%** | +6.2pp |

**Casos fallidos en V2:**
- `cubic_25` (0/2 raíces): Requiere $a^{1/3}$ — imposible con `safe_sqrt` como único operador de raíz.
- `special_39` (0/2 raíces): Limitación estructural por cruce de ramas en el ordenamiento por valor.

**Corrección de bug de `neg()`:** Durante la evaluación V2, se descubrió que `metrics.py` no incluía `neg` en el diccionario local de `sympify`, causando errores de parsing silenciosos. La corrección (`_neg = lambda x: -x`) mejoró las métricas reportadas de V2.

### 12.3 Versión 3 (V3): Operador Generalizado `safe_pow` + Constraints

Cambios respecto a V2:
- `safe_sqrt(x) = sqrt(abs(x))` → `safe_pow(x, y) = sign(x) * abs(x)^y`
- `constraints={"safe_pow": (-1, 1)}` — exponente restringido a complejidad 1
- `complexity_of_operators["safe_pow"] = 2` (reducido desde 3)

**Test de validación — `quadratic_19_full_abc`** ($ax^2+bx+c=0$, 3 parámetros):

| Rama | Intento | Complejidad | Loss | Fórmula Descubierta | Puntos |
|---|---|---|---|---|---|
| 1 ($x_2$) | 3 de 3 | 19 | $2.65 \times 10^{-13}$ | `(safe_pow((a*c) + ((b*b)*-0.25), 0.5) + (b*-0.5)) / a` | 512/512 |
| 2 ($x_1$) | 1 de 3 | 19 | $8.09 \times 10^{-15}$ | `((safe_pow((b*b) - ((c*4)*a), 0.5) - b) * 0.5) / a` | 512/512 |

**Resultado:** 2/2 raíces, 100% cobertura, 1261.5 segundos.

Las fórmulas descubiertas son algebraicamente equivalentes a la fórmula cuadrática clásica:

$$x_{1,2} = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

**Impacto de `safe_pow` en el benchmark:**
- `cubic_25`: **RESUELTO** — PySR descubrió `safe_pow(a, 0.3333)` = $a^{1/3}$ ✓
- `quadratic_19`: **RESUELTO** — Ambas raíces encontradas con fórmula exacta ✓
- `special_39`: Sin cambio — limitación estructural, no del operador.

### 12.4 Evolución Comparativa

| Métrica | V1 | V2 | V3 (test) |
|---|---|---|---|
| Operador de potencia | `safe_sqrt` (unario) | `safe_sqrt` (unario) | `safe_pow` (binario) |
| Diversidad evolutiva | Defaults PySR | 6 parámetros tuneados | 6 parámetros tuneados |
| Constraints | — | — | `(-1, 1)` en exponente |
| `cubic_25` | ✗ | ✗ | **✓** |
| `quadratic_19` (3 params) | ✓ (2/2, 1181s) | ✗ (1/2, 5275s) | **✓** (2/2, 1261s) |
| `special_39` | ✗ | ✗ | ✗ (limitación estructural) |

> **Nota:** Los resultados V3 mostrados corresponden al test unitario de `quadratic_19`. El benchmark completo de 43 casos con V3 está pendiente de ejecución.

---

## 13. Limitaciones y Trabajo Futuro

### 13.1 Limitaciones Actuales

- **Variable única:** El pipeline actualmente soporta ecuaciones con una sola incógnita. La extensión a sistemas de ecuaciones requiere reorganizar el Paso 3 y la agrupación por rama.
- **Determinación de regiones Piecewise:** La construcción automática de las condiciones de las regiones es simplificada. Un sistema robusto requeriría clasificación espacial o árboles de decisión.
- **Escalabilidad:** Para ecuaciones con muchos parámetros ($n > 5$), el grid regular $m^n$ crece exponencialmente. Sería necesario LHS o muestreo adaptativo.
- **Ecuaciones trascendentes:** La verificación con Gröbner solo aplica a ecuaciones polinómicas. Para ecuaciones trascendentes, la verificación numérica es el único método disponible.
- **Cruce de ramas (`special_39`):** Cuando las ramas de raíces se cruzan en el espacio de parámetros (la raíz "menor" en una región se vuelve la "mayor" en otra), el agrupamiento por posición ordinal mezcla datos de ramas distintas. PySR no puede encontrar una expresión que ajuste datos de dos funciones mezcladas.

### 13.2 Trabajo Futuro

- Ejecutar benchmark V3 completo (43 casos) para obtener métricas definitivas.
- Integrar la verificación de Gröbner de forma opcional en el pipeline.
- Implementar detección automática de regiones para expresiones Piecewise.
- Explorar operadores adicionales (trigonométricos, exponenciales) para ecuaciones trascendentes.
- Paralelizar los intentos de PySR en máquinas con RAM suficiente.
- Implementar un mecanismo de *warm start* donde intentos posteriores hereden las mejores expresiones de intentos anteriores.
- **Métodos alternativos de agrupación de ramas** (para resolver el problema de cruce descrito en §6.5):
  - *Tracking por continuidad:* en lugar de ordenar por valor, seguir cada raíz como curva continua conforme varía el parámetro. Si la raíz $i$ en el punto $\boldsymbol{\alpha}^{(k)}$ era $r$, en $\boldsymbol{\alpha}^{(k+1)}$ asignarla a la raíz más cercana a $r$. Resuelve el cruce de ramas sin requerir información algebraica.
  - *Clustering:* usar K-means o DBSCAN sobre los pares $(\boldsymbol{\alpha}, x)$ para agrupar raíces en clusters que correspondan a ramas continuas.
  - *Separación por regiones:* detectar automáticamente las regiones del dominio donde el número de raíces es constante y tratar cada región por separado.
  - *Homotopy continuation:* métodos numéricos que siguen las raíces como curvas paramétricas, garantizando no perder ninguna ni mezclarlas.

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
