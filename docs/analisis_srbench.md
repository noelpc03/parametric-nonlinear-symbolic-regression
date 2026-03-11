# Análisis de SRBench: Configuraciones de Referencia para Regresión Simbólica

## 1. ¿Qué es SRBench?

SRBench (Symbolic Regression Benchmark) es el benchmark estándar de la comunidad para comparar métodos de regresión simbólica. Fue presentado en NeurIPS 2022 por La Cava, Orzechowski, Cava et al. Incluye:

- **14 algoritmos** de regresión simbólica (PySR, Operon, gplearn, FEAT, GP-GOMEA, Bingo, etc.)
- **252 datasets** de regresión (122 "black-box" de PMLB + 130 "ground-truth" de Feynman/Strogatz)
- Un framework de evaluación unificado con métricas de precisión, simplicidad y equivalencia simbólica

La configuración oficial de PySR en SRBench fue escrita por **Miles Cranmer** (autor de PySR), lo que la convierte en la referencia más autorizada para el tuning del algoritmo.

---

## 2. Diferencia Fundamental: Nuestro Problema vs. SRBench

Antes de comparar configuraciones, es crucial entender que **resolvemos problemas fundamentalmente diferentes**:

| Aspecto | **SRBench** | **Nuestro pipeline** |
|---|---|---|
| **Objetivo** | Regresión: dado $(X, y)$, encontrar $\hat{f}$ que minimice el error de predicción | Descubrimiento de raíces: dada $F(x; \boldsymbol{\alpha})=0$, encontrar las expresiones $g_i(\boldsymbol{\alpha})$ tales que $F(g_i, \boldsymbol{\alpha}) \equiv 0$ |
| **Datos** | Observaciones experimentales o simuladas con **ruido** ($\sigma = 0, 0.001, 0.01, 0.1$) | Pares $(\boldsymbol{\alpha}, x)$ obtenidos resolviendo $F=0$ numéricamente — **sin ruido** (precisión de punto flotante, $\sim 10^{-15}$) |
| **Fórmula objetivo** | Desconocida a priori (el benchmark evalúa si se recuperó) | Existe una expresión analítica exacta con loss $\approx 0$. No buscamos una "buena aproximación" |
| **Criterio de éxito** | $R^2$ en test set, simplicidad, equivalencia simbólica | $\varepsilon$-matching: $\|y - \hat{y}\| < \varepsilon(1+\|y\|)$ con $\varepsilon = 0.005$ punto por punto |
| **Operadores** | Estándar: $+, -, \times, \div, \sin, \exp, \log, \sqrt{\,}$ | Específicos: $+, -, \times, \div, \text{neg}, \text{safe\_pow}(x,y) = \text{sign}(x) \cdot |x|^y$ |
| **Complejidad típica** | Variable (desde $y = x_1$ hasta fórmulas de Feynman con ~20 nodos) | Alta: la fórmula cuadrática tiene ~19 nodos; las cúbicas pueden tener más |
| **Tiempo disponible** | 2 horas por dataset | ~5–10 minutos por rama (con 3 intentos) |
| **Recursos** | Clusters con muchos cores y RAM | Laptop o PC con RAM limitada (por eso `procs=0`) |

### Consecuencias de estas diferencias

1. **No necesitamos generalización.** SRBench evalúa con train/test split (75/25) porque los datos tienen ruido. Nosotros tenemos datos exactos: la fórmula que matchea el training set es **la misma** que matchearía cualquier test set, porque provienen de una relación matemática determinista.

2. **El parsimony adaptativo no es tan relevante.** SRBench usa `adaptive_parsimony_scaling=1000` para evitar que PySR produzca fórmulas sobreajustadas al ruido. En nuestro caso, no hay ruido que sobreajustar: una expresión de complejidad 19 que tenga loss $10^{-13}$ **es** la fórmula correcta, no un sobreajuste.

3. **Nuestros cambios de diversidad sí son necesarios.** SRBench no modifica `tournament_selection_p` ni `fraction_replaced` porque tiene 2 horas para ejecutar y usa todos los cores. Con nuestro presupuesto computacional menor (~5 min por intento, un solo proceso Julia), la convergencia prematura es un riesgo real — por eso reducimos la presión selectiva.

4. **`safe_pow` no existe en SRBench.** Ningún algoritmo del benchmark usa un operador binario de potencia generalizada. Usan `sqrt` como unario dedicado, lo cual no escala a raíces cúbicas o cuartas. Nuestro `safe_pow` + constraints es una contribución original.

---

## 3. Configuración de PySR en SRBench (por Miles Cranmer)

```python
est = PySRRegressor(
    niterations=1_000_000_000,             # Infinitas iteraciones (usa timeout)
    ncyclesperiteration=2_500,             # 4.5× más que nuestro 550
    population_size=100,                   # 2× más que nuestro 50
    populations=max(15, cpu_count()*2),    # Escala con cores disponibles
    timeout_in_seconds=2*60*60 - 10*60,    # 1h50min (2h menos 10min de compilación)
    maxsize=30,                            # 20% más que nuestro 25
    maxdepth=20,                           # Explícito (nosotros usamos default)
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["sin", "exp", "log", "sqrt"],
    constraints={
        "sin": 9, "exp": 9, "log": 9, "sqrt": 9,
        "/": (-1, 9),                      # Denominador limitado a complejidad 9
    },
    nested_constraints={
        "sin":  {"sin": 0, "exp": 1, "log": 1, "sqrt": 1},
        "exp":  {"exp": 0, "log": 0},     # Prohíbe exp(log(x)) y exp(exp(x))
        "log":  {"exp": 0, "log": 0},     # Prohíbe log(exp(x)) y log(log(x))
        "sqrt": {"sqrt": 0},              # Prohíbe sqrt(sqrt(x))
    },
    procs=cpu_count(),                     # Usa todos los cores
    multithreading=False,
    batching=True,
    batch_size=50,                         # 4× más pequeño que nuestro 200
    turbo=True,
    weight_optimize=0.001,                 # Optimización de constantes como mutación
    adaptive_parsimony_scaling=1_000.0,    # 50× el default (20.0)
    parsimony=0.0,                         # Sin parsimony estático (como nosotros)
)
```

### Comparación detallada

| Parámetro | SRBench (Cranmer) | Nuestro config | Análisis |
|---|---|---|---|
| `niterations` | 10⁹ (usa timeout) | 500 | SRBench depende del timeout; nosotros de iteraciones fijas. Ambos son válidos para sus contextos |
| `ncyclesperiteration` | 2,500 | 550 | Con nuestro `niterations=500`, el esfuerzo total es $500 \times 550 = 275\text{k}$ ciclos. Suficiente para nuestros problemas |
| `population_size` | 100 | 50 | Poblaciones más pequeñas ahorran RAM. Con `procs=0`, no podemos permitir 100 |
| `populations` | ~32 (16 cores) | 30 | Similar |
| `maxsize` | 30 | 25 | La cuadrática cabe en 25; podría necesitarse más para ecuaciones más complejas |
| `batch_size` | **50** | 200 | **Diferencia notable.** Batches más pequeños añaden más ruido estocástico al fitness. En SRBench esto ayuda con datos ruidosos; en nuestro caso (datos exactos) el beneficio sería diferente: más varianza en la evaluación podría ayudar a escapar de óptimos locales |
| `procs` | cpu_count() | 0 | Nosotros priorizamos RAM sobre velocidad. Válido para laptops |
| `adaptive_parsimony_scaling` | 1,000 | default (20) | En SRBench evita sobreajuste a ruido. En nuestro caso no hay ruido; una expresión exacta nunca es "sobreajuste" |
| `weight_optimize` | 0.001 | no seteado | Podría ayudar a que BFGS ajuste constantes de `safe_pow(expr, 0.5)` más rápidamente |
| `constraints` | Unarios ≤ 9, `/` denom ≤ 9 | `safe_pow` exp ≤ 1 | Nuestro constraint es más restrictivo en el exponente de `safe_pow`, lo cual está justificado: queremos $0.5$ o $0.333$, no expresiones complejas en el exponente |
| `nested_constraints` | Prohíbe composiciones que se cancelan (exp∘log, log∘exp) | `safe_pow∘safe_pow=0` | Ambos eliminan composiciones inútiles |
| **Diversidad** | Defaults de PySR | 6 parámetros modificados | Cranmer tiene 2h + todos los cores. Nosotros compensamos menor presupuesto con mayor diversidad |

---

## 4. Patrones de Otros Algoritmos en SRBench

### Operon (multi-objetivo)

```python
objectives = ['r2', 'length']  # Optimización Pareto: precisión vs. simplicidad
tournament_size = 3             # Muy bajo → máxima diversidad
population_size = 100–1000      # Tuneado con Optuna (50 trials)
max_length = 10–50              # Tuneado
time_limit = 900                # 15 minutos por run
```

**Relevancia para nosotros:** El tournament size de 3 es aún más bajo que nuestro 8. Confirma que la tendencia en la comunidad es **reducir la presión selectiva** para mejorar la exploración. La optimización multi-objetivo (Pareto) no aplica directamente a nuestro caso porque queremos la expresión exacta, no un trade-off.

### gplearn (crossover-heavy)

```python
tournament_size = 20            # Presión altísima
p_crossover = 0.7               # 70% crossover (vs. nuestro 6.6%)
p_subtree_mutation = 0.01       # Mutación mínima
parsimony_coefficient = 0.001   # Parsimony explícito
metric = 'mae'                  # MAE en vez de MSE
```

**Relevancia para nosotros:** gplearn representa la **filosofía opuesta** a la nuestra: presión selectiva alta + mucho crossover. Funciona cuando las expresiones objetivo son simples. Para expresiones complejas como la cuadrática (~19 nodos), esta estrategia falla — como demostramos con V1.

### FEAT (operadores de potencia)

```python
functions = ["+", "-", "*", "/", "sqrt", "sin", "cos", "exp", "log",
             "^2", "^3", "1/", "tanh", "logit"]  # Potencias explícitas
max_depth = 6
batch_size = 100
```

**Relevancia para nosotros:** FEAT incluye `^2` y `^3` como operadores explícitos — el enfoque de "hardcodear cada potencia" que rechazamos en favor de `safe_pow` generalizado. Su `max_depth=6` es muy restrictivo; la cuadrática requeriría más profundidad.

### GP-GOMEA (fine-tuning de constantes)

```python
pop_size = 1024
evaluations = 500_000           # 499,500 búsqueda + 500 fine-tuning
max_features = 20
```

**Relevancia para nosotros:** GP-GOMEA reserva **500 evaluaciones exclusivas** para optimizar constantes post-búsqueda. En PySR, BFGS hace esto automáticamente. Nuestro `weight_optimize` no está seteado; podría ser beneficioso activarlo.

### Bingo (Age-Fitness)

```python
fitness_algorithm = AgeFitnessEA()  # Individuos viejos se reemplazan primero
crossover_rate = 0.4
mutation_rate = 0.45                # Más mutación que crossover
stack_size = 24–32
```

**Relevancia para nosotros:** Bingo usa **Age-Fitness**, un mecanismo de diversidad completamente diferente: en vez de reducir la presión selectiva (como nosotros), reemplaza individuos viejos independientemente de su fitness. Su ratio mutación/crossover (0.45/0.4) es similar a nuestra filosofía de priorizar mutaciones sobre cruces.

---

## 5. Cómo Evalúa SRBench la Calidad

### Métricas predictivas

- **R²** (coeficiente de determinación) — métrica principal de ranking
- **MSE** (error cuadrático medio)
- **MAE** (error absoluto medio)

Evaluadas en train (75%) y test (25%).

### Métrica de simplicidad

$$\text{simplicity} = -\frac{\log(\text{num\_components})}{\log(5)}$$

donde `num_components` es el número de nodos en el árbol SymPy simplificado.

### Equivalencia simbólica (ground-truth)

Para datasets con fórmula conocida (Feynman, Strogatz):

1. Solo se evalúa si $R^2 > 0.5$ en test.
2. Se calcula `simplify(true_model - predicted_model)`.
3. Clasificación:
   - **Exacta:** la diferencia simplifica a 0
   - **Aditiva:** la diferencia es una constante
   - **Multiplicativa:** el cociente es una constante
4. Cualquiera de las tres se considera "solución simbólica".

### Contraste con nuestra evaluación

| SRBench | Nuestro pipeline |
|---|---|
| R² en test set (con ruido) | $\varepsilon$-matching punto por punto (sin ruido) |
| Equivalencia simbólica post-hoc | Verificación algebraica con Bases de Gröbner |
| Acepta "off by a constant" | Requiere matcheo exacto ($\varepsilon = 0.005$ relativo) |
| 10 semillas aleatorias por dataset | 3 intentos por iteración, early stopping al 100% |

---

## 6. Parámetros a Considerar Experimentar

Basándonos en el análisis de SRBench, estos son parámetros que **podrían** beneficiar nuestro pipeline, con la advertencia de que nuestro problema es diferente:

### Candidatos prometedores

| Parámetro | Valor actual | Valor SRBench | Motivo para probar |
|---|---|---|---|
| `batch_size` | 200 | **50** | Más estocasticidad podría ayudar a escapar de los patrones `safe_pow(const, variable)` que observamos |
| `weight_optimize` | no seteado | **0.001** | Activar optimización de constantes como mutación; podría acelerar convergencia de coeficientes en `safe_pow(expr, 0.5)` |
| `constraints["/"]` | no seteado | **(-1, 9)** | Limitar complejidad del denominador para evitar divisiones demasiado elaboradas |

### Candidatos con reservas

| Parámetro | Valor SRBench | Por qué NO es directamente aplicable |
|---|---|---|
| `adaptive_parsimony_scaling=1000` | Evita sobreajuste a ruido | No tenemos ruido. Una expresión exacta de complejidad 19 **es** la solución, no un sobreajuste. Activar esto podría penalizar la fórmula correcta |
| `niterations=∞ + timeout` | SRBench tiene 2 horas | Nuestro presupuesto es ~5–10 min. Nuestro enfoque de 500 iteraciones + 3 intentos ya funciona |
| `population_size=100` | Más diversidad intra-isla | Duplicaría el consumo de RAM con `procs=0` |
| `maxsize=30` | Expresiones más grandes | 25 es suficiente para cuadráticas/cúbicas. Para ecuaciones más complejas habría que revisarlo |

---

## 7. Conclusión

SRBench confirma que nuestra configuración está alineada con las mejores prácticas de la comunidad en los aspectos estructurales (`parsimony=0.0`, `turbo=True`, `batching=True`, constraints de anidamiento). Las diferencias principales (`procs=0`, diversidad V2, `safe_pow` con constraints) están **justificadas por nuestro problema específico**: presupuesto computacional limitado, datos sin ruido, necesidad de fórmulas exactas, y un operador de potencia generalizado que no existe en SRBench.

El hallazgo más relevante de SRBench para nuestro trabajo es la confirmación de que **ningún otro método en el benchmark usa un operador de potencia binario generalizado** como `safe_pow`. Todos usan operadores unarios dedicados (`sqrt`, `^2`, `^3`) o simplemente no incluyen raíces. Nuestro enfoque de `safe_pow(x, y) = sign(x) * |x|^y` con `constraints=(-1, 1)` es una contribución original que permite descubrir raíces de cualquier orden sin hardcodear operadores.
