# Documentacion Formal del Notebook de Benchmark A/B

## 1. Proposito del documento

Este documento describe de manera formal y detallada el notebook de evaluacion comparativa A/B ubicado en:

- `src/benchmark/notebooks/test_nb.ipynb`

El objetivo es dejar trazabilidad metodologica para tesis sobre:

1. Que problema experimental se resuelve.
2. Que definiciones matematicas se usan.
3. Como se ejecuta el pipeline del proyecto sin sobrescribir parametros.
4. Como se comparan dos sistemas de perdida (A y B).
5. Que tests se usan y como se interpretan los resultados.

Este texto se redacta como anexo metodologico y de reproducibilidad.

---

## 2. Alcance experimental

El notebook implementa una evaluacion A/B de dos sistemas de perdida sobre el mismo pipeline de descubrimiento simbolico de raices:

- Sistema A: `mse`.
- Sistema B: `match_count`.

La evaluacion se ejecuta de forma secuencial para todos los casos del catalogo de benchmark (`TEST_CASES`) y genera un reporte estadistico con comparacion pareada.

No se aplican overrides de configuracion de regresion simbolica: el notebook utiliza los parametros definidos en `src/config.py`.

---

## 3. Definiciones formales

### 3.1 Ecuacion parametrica

Se trabaja con ecuaciones de la forma:

$$
F(x; \theta) = 0,
$$

con:

- $x$: variable de interes (raiz).
- $\theta = (\theta_1, \ldots, \theta_p)$: vector de parametros.

### 3.2 Rama de raices

Una rama es una funcion analitica $g_j(\theta)$ tal que:

$$
F(g_j(\theta); \theta) = 0,
$$

en una region del espacio de parametros donde esa rama existe como raiz real.

### 3.3 Cobertura

Para una rama descubierta, la cobertura se define como:

$$
\text{coverage} = \frac{\#\text{puntos matcheados}}{\#\text{puntos totales de la rama}}.
$$

### 3.4 Root match rate por caso

Si un caso tiene $R$ raices esperadas y se matchean $M$:

$$
\text{root\_match\_rate} = \frac{M}{R}.
$$

### 3.5 Perdida `match_count`

La perdida dura por conteo se define sobre un umbral absoluto $\varepsilon$:

$$
\ell_i =
\begin{cases}
0, & |y_i - \hat{y}_i| < \varepsilon \\
1, & \text{en otro caso}
\end{cases}
$$

$$
\mathcal{L}_{\text{match\_count}} = \frac{1}{N}\sum_{i=1}^{N}\ell_i
= 1 - \frac{\#\text{matches}}{N}.
$$

Minimizar esta perdida equivale a maximizar el numero de matches.

---

## 4. Estructura del notebook (seccion por seccion)

El notebook esta organizado en 11 bloques principales:

1. Configuracion de entorno y dependencias.
2. Carga de datos de referencia y corridas previas.
3. Normalizacion y validacion de formato.
4. Definicion de funciones de ejecucion y agregacion.
5. Evaluacion de Sistema A (`mse`).
6. Evaluacion de Sistema B (`match_count`).
7. Comparacion de metricas lado a lado.
8. Pruebas estadisticas pareadas.
9. Visualizaciones.
10. Analisis de errores por caso.
11. Exportacion de reporte final.

Esta estructura separa de forma explicita:

- Ejecucion del experimento.
- Analitica estadistica.
- Trazabilidad de artefactos.

---

## 5. Integracion con el codigo fuente del proyecto

El notebook no reimplementa el pipeline matematico; delega la logica en `src`.

### 5.1 Flujo de llamadas

Para cada caso:

1. El notebook llama `run_single_case(...)` desde `src/benchmark/runner.py`.
2. El runner ejecuta parseo, grid, solver, agrupacion y regresion simbolica.
3. El notebook llama `evaluate_case(...)` desde `src/benchmark/metrics.py` para evaluar calidad del resultado.

### 5.2 Ventaja metodologica

Esta decision asegura:

1. Consistencia entre benchmark por script y benchmark por notebook.
2. Menor riesgo de divergencia por duplicacion de logica.
3. Reproducibilidad de tesis sobre un unico codigo operativo.

---

## 6. Configuracion experimental utilizada

La configuracion efectiva se toma de `src/config.py`.

### 6.1 Parametros clave de regresion simbolica

Valores vigentes:

- `NITERATIONS = 500`
- `POPULATIONS = 30`
- `POPULATION_SIZE = 50`
- `NCYCLES_PER_ITERATION = 550`
- `MAXSIZE = 25`
- `TURBO = True`
- `PROCS = 0`
- `NUM_ATTEMPTS = 3`
- `MIN_POINTS = 5`
- `MAX_ITERATIONS = None` (sin limite)
- `MAX_CONSECUTIVE_NO_MATCH = 3`
- `MIN_MATCH_FRACTION = 0.05`
- `EPSILON = 0.005` (matcheo relativo post-entrenamiento)
- `MATCH_COUNT_EPSILON = 1e-4` (umbral absoluto para loss dura)

### 6.2 Politica de no override

El notebook define explicitamente que utiliza defaults de `src/config.py` y no sobreescribe parametros de SR para la comparacion A/B.

---

## 7. Definicion de los sistemas comparados

## 7.1 Sistema A (`mse`)

Corresponde a la funcion de perdida por defecto de regresion (error cuadratico medio):

$$
\mathcal{L}_{\text{MSE}} = \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2.
$$

Interpretacion: prioriza minimizacion de error promedio continuo.

## 7.2 Sistema B (`match_count`)

Usa la perdida dura por conteo de matches con umbral absoluto.

Interpretacion: prioriza el numero de puntos exactos dentro de tolerancia.

## 7.3 Regla de conmutacion en notebook

Antes de ejecutar cada caso:

1. Se fuerza `USE_SIGMOID_LOSS = False`.
2. Se activa `USE_MATCH_COUNT_LOSS = (loss_mode == 'match_count')`.

Con esto se compara exclusivamente `mse` vs `match_count`.

---

## 8. Catalogo de tests usados en el benchmark

Fuente:

- `src/benchmark/test_cases.py`

Total de casos:

- 43

### 8.1 Distribucion por categoria

| Categoria | Casos |
|---|---:|
| linear | 10 |
| quadratic | 14 |
| cubic | 6 |
| quartic | 4 |
| quintic | 1 |
| special | 8 |

### 8.2 Distribucion por dificultad

| Dificultad | Casos |
|---|---:|
| easy | 19 |
| medium | 19 |
| hard | 5 |

### 8.3 Distribucion cruzada categoria-dificultad

| Categoria | easy | medium | hard |
|---|---:|---:|---:|
| linear | 8 | 2 | 0 |
| quadratic | 6 | 7 | 1 |
| cubic | 3 | 2 | 1 |
| quartic | 0 | 2 | 2 |
| quintic | 0 | 0 | 1 |
| special | 2 | 6 | 0 |

### 8.4 Lista completa de casos por categoria

#### linear

- `linear_01_basic` (easy, 1 raiz esperada)
- `linear_02_scaled` (easy, 1 raiz esperada)
- `linear_03_offset` (easy, 1 raiz esperada)
- `linear_04_fraction` (easy, 1 raiz esperada)
- `linear_05_negative` (easy, 1 raiz esperada)
- `linear_06_two_params` (easy, 1 raiz esperada)
- `linear_07_scaled_params` (easy, 1 raiz esperada)
- `linear_08_product_param` (medium, 1 raiz esperada)
- `linear_09_division` (medium, 1 raiz esperada)
- `linear_10_three_params` (easy, 1 raiz esperada)

#### quadratic

- `quadratic_11_simple` (easy, 2 raices esperadas)
- `quadratic_12_shifted` (easy, 1 raiz esperada)
- `quadratic_13_factored` (easy, 2 raices esperadas)
- `quadratic_14_linear_coeff` (easy, 2 raices esperadas)
- `quadratic_15_full` (medium, 2 raices esperadas)
- `quadratic_16_irrational` (medium, 2 raices esperadas)
- `quadratic_17_param_coeff` (medium, 2 raices esperadas)
- `quadratic_18_two_params` (medium, 2 raices esperadas)
- `quadratic_19_full_abc` (hard, 2 raices esperadas)
- `quadratic_20_factored_two` (easy, 2 raices esperadas)
- `quadratic_21_sum_product` (medium, 2 raices esperadas)
- `quadratic_22_symmetric` (medium, 2 raices esperadas)
- `quadratic_23_nested` (medium, 2 raices esperadas)
- `quadratic_24_depressed` (easy, 1 raiz esperada)

#### cubic

- `cubic_25_one_root` (medium, 1 raiz esperada)
- `cubic_26_factored` (easy, 3 raices esperadas)
- `cubic_27_quadratic_factor` (easy, 1 raiz esperada)
- `cubic_28_depressed` (hard, 2 raices esperadas)
- `cubic_29_two_params` (medium, 3 raices esperadas)
- `cubic_30_triple` (easy, 1 raiz esperada)

#### quartic

- `quartic_31_biquadratic` (medium, 2 raices esperadas)
- `quartic_32_factored` (hard, 4 raices esperadas)
- `quartic_33_double_quadratic` (hard, 4 raices esperadas)
- `quartic_35_repeated` (medium, 2 raices esperadas)

#### quintic

- `quintic_34_factored` (hard, 5 raices esperadas)

#### special

- `special_36_reciprocal` (easy, 1 raiz esperada)
- `special_37_ratio` (easy, 1 raiz esperada)
- `special_38_quadratic_ratio` (medium, 2 raices esperadas)
- `special_39_difference_of_squares` (medium, 2 raices esperadas)
- `special_40_linear_three_params` (medium, 1 raiz esperada)
- `special_41_square_root_form` (medium, 2 raices esperadas)
- `special_42_cubic_simple` (medium, 1 raiz esperada)
- `special_43_mixed` (medium, 2 raices esperadas)

---

## 9. Metricas reportadas

El notebook reporta metricas por corrida, por sistema y por comparacion pareada.

### 9.1 Metricas por registro

- `status`: estado de ejecucion del caso.
- `time_seconds`: tiempo total por caso.
- `roots_expected`: numero de raices esperadas.
- `roots_matched`: numero de raices matcheadas.
- `root_match_rate`: fraccion de raices encontradas.
- `coverage_combined`: cobertura promedio por ramas encontradas.
- `num_functions_found`: numero de expresiones descubiertas.

### 9.2 Metricas agregadas

Para cada sistema (`A`, `B`):

1. `n_runs`, `n_cases`.
2. `success_rate`.
3. `mean_root_match_rate`.
4. `mean_coverage`.
5. `median_time_seconds`.

### 9.3 Deltas A/B

Se calcula, por caso y repeticion:

$$
\Delta_{\text{match}} = \text{root\_match\_rate}_B - \text{root\_match\_rate}_A,
$$

$$
\Delta_{\text{cov}} = \text{coverage}_B - \text{coverage}_A,
$$

$$
\Delta_{\text{time}} = \text{time}_B - \text{time}_A.
$$

---

## 10. Pruebas estadisticas empleadas

### 10.1 Wilcoxon signed-rank pareado

Esta prueba se aplica sobre diferencias pareadas por caso entre Sistema B y Sistema A.

Para cada caso/repeticion $i$ se define:

$$
d_i^{match} = \text{root\_match\_rate}_{B,i} - \text{root\_match\_rate}_{A,i},
$$

$$
d_i^{cov} = \text{coverage}_{B,i} - \text{coverage}_{A,i},
$$

$$
d_i^{time} = \text{time}_{B,i} - \text{time}_{A,i}.
$$

La prueba de Wilcoxon signed-rank no usa la media ni requiere normalidad; evalua si la mediana de las diferencias es 0 (o mayor/menor segun la alternativa).

Procedimiento conceptual:

1. Se toman las diferencias no nulas.
2. Se ordenan por magnitud absoluta $|d_i|$.
3. Se asignan rangos y se reinyecta el signo de cada diferencia.
4. Se compara la suma de rangos positivos y negativos.

Hipotesis usadas en el notebook:

1. Para `delta_root_match_rate` (alternativa `greater`):
	- $H_0$: mediana$(d^{match}) = 0$.
	- $H_1$: mediana$(d^{match}) > 0$ (B supera a A).
2. Para `delta_coverage` (alternativa `greater`):
	- $H_0$: mediana$(d^{cov}) = 0$.
	- $H_1$: mediana$(d^{cov}) > 0$.
3. Para `delta_time_seconds` (alternativa `two-sided`):
	- $H_0$: mediana$(d^{time}) = 0$.
	- $H_1$: mediana$(d^{time}) \neq 0$.

Interpretacion:

1. Si el p-valor de `delta_root_match_rate` es pequeno y la mediana de $d^{match}$ es positiva, hay evidencia de mejora de B en recuperacion de raices.
2. Si el p-valor de `delta_coverage` es pequeno y la mediana de $d^{cov}$ es positiva, hay evidencia de mejora de B en cobertura.
3. Si el p-valor de `delta_time_seconds` es pequeno, hay diferencia de tiempo entre sistemas; el signo de la mediana indica que sistema es mas lento/rapido.

Notas de implementacion en el notebook:

1. Si hay menos de 3 observaciones validas, se devuelve `NaN` para evitar inferencias inestables.
2. Si todas las diferencias son 0, se reporta estadistico 0 y p-valor 1.0 (sin evidencia de diferencia).

Razon metodologica:

1. Es una prueba no parametrica apropiada para muestras pareadas.
2. No exige distribucion normal de las diferencias.
3. Respeta el diseno A/B por pares naturales (mismo caso, distinta perdida).

### 10.2 Binomial sobre discordantes

Esta prueba se usa para una salida binaria de interes: exito perfecto por caso.

Se define:

$$
perfect_A = \mathbb{1}(\text{root\_match\_rate}_A = 1.0), \quad
perfect_B = \mathbb{1}(\text{root\_match\_rate}_B = 1.0).
$$

Luego se cuentan solo pares discordantes:

1. `n01`: A falla y B acierta.
2. `n10`: A acierta y B falla.
3. $n_d = n01 + n10$.

Hipotesis del contraste binomial exacto:

1. $H_0$: en pares discordantes, ambos sistemas tienen probabilidad 0.5 de "ganar".
2. $H_1$: esa probabilidad difiere de 0.5.

En implementacion, el notebook calcula:

$$
p\text{-valor} = \text{BinomTest}\left(\min(n01,n10),\; n=n_d,\; p=0.5\right).
$$

Interpretacion:

1. p-valor pequeno y `n01 > n10`: B gana mas casos perfectos que A.
2. p-valor pequeno y `n10 > n01`: A gana mas casos perfectos que B.
3. p-valor alto: no hay evidencia suficiente de asimetria en exito perfecto.

Observacion metodologica:

Esta formulacion es equivalente al analisis exacto de signos sobre pares discordantes (muy proximo, en espiritu, a McNemar exacto para datos pareados binarios).

### 10.3 Criterio de decision estadistica

Para informe de tesis se recomienda explicitar:

1. Nivel de significancia $\alpha$ (tipicamente 0.05).
2. Direccion esperada de efecto para cada metrica (ya codificada en las alternativas del notebook).
3. Magnitud del efecto (mediana/mean de los deltas), no solo p-valores.

Cuando se evalua mas de una metrica a la vez, puede incluirse una correccion por comparaciones multiples (por ejemplo Holm) como analisis de robustez.

---

## 11. Protocolo de ejecucion reproducible

### 11.1 Precondiciones

1. Ejecutar el notebook dentro del repositorio del proyecto.
2. Tener entorno virtual con dependencias instaladas.
3. Verificar que la celda de setup detecta correctamente `PROJECT_ROOT`.

### 11.2 Orden recomendado de ejecucion

1. Celda 3 (setup).
2. Celda 5 (carga de referencia).
3. Celda 7 (validaciones).
4. Celda 9 (funciones de ejecucion).
5. Celda 11 (Sistema A).
6. Celda 13 (Sistema B).
7. Celdas 15, 17, 19, 21, 23 (analisis y exportacion).

### 11.3 Semilla

El notebook fija semilla para `random` y `numpy` por caso y repeticion para reducir ruido en la comparacion A/B.

Observacion: esto mejora comparabilidad, pero no implica determinismo total del motor evolutivo de PySR si no se fija semilla interna del backend.

---

## 12. Artefactos de salida

Por corrida se crea un directorio tipo:

- `src/benchmark_results/ab_notebook_full_YYYYMMDD_HHMMSS/`

Archivos principales:

1. `system_a_mse.csv`
2. `system_b_match_count.csv`
3. `report/all_runs.csv`
4. `report/paired_deltas.csv`
5. `report/comparison_table.csv`
6. `report/stats_report.csv`
7. `report/final_table.csv`
8. `report/figure_*.png`
9. `report/meta.json`

Estos artefactos permiten trazabilidad completa para anexos de tesis y auditoria de resultados.

---

## 13. Criterios de interpretacion para tesis

### 13.1 Resultado favorable para Sistema B

Se considera evidencia favorable para `match_count` si, simultaneamente:

1. Aumenta `root_match_rate` promedio frente a A.
2. Aumenta o mantiene `coverage_combined`.
3. El p-valor de Wilcoxon para `delta_root_match_rate` y/o `delta_coverage` es consistente con mejora (segun nivel de significancia definido en tesis).
4. El costo temporal adicional es aceptable para el objetivo aplicado.

### 13.2 Resultado favorable para Sistema A

Se considera evidencia favorable para `mse` si:

1. No hay mejora estadisticamente sostenida de B en calidad.
2. B incrementa tiempo de forma significativa sin beneficios proporcionales.

### 13.3 Resultado mixto

Si B mejora calidad en casos dificiles pero penaliza tiempo, la conclusion recomendada es condicional por categoria de problema.

---

## 14. Limitaciones metodologicas

1. El benchmark evalua un catalogo finito de expresiones objetivo.
2. La estocasticidad evolutiva puede introducir variacion entre corridas.
3. La comparacion depende de tolerancias numericas y criterio de equivalencia.
4. El costo computacional limita el numero de repeticiones en hardware reducido.

Estas limitaciones deben declararse en la tesis para transparencia metodologica.

---

## 15. Glosario tecnico

- Rama: expresion analitica asociada a una raiz en funcion de parametros.
- Match: punto donde error cae bajo un umbral de tolerancia.
- Cobertura: fraccion de datos explicados por una expresion descubierta.
- Hall of Fame: conjunto de ecuaciones candidatas no dominadas/seleccionadas por PySR.
- Benchmark A/B: experimento comparativo controlado entre dos configuraciones del mismo pipeline.

---

## 16. Referencias internas del proyecto

- `src/benchmark/notebooks/test_nb.ipynb`
- `src/benchmark/test_cases.py`
- `src/benchmark/runner.py`
- `src/benchmark/metrics.py`
- `src/5_symbolic_regression/symbolic_regression.py`
- `src/5_symbolic_regression/loss_functions.py`
- `src/config.py`

---

## 17. Nota de uso academico

Este documento puede citarse en la tesis como especificacion metodologica del experimento A/B y como referencia de reproducibilidad para resultados reportados en capitulos de evaluacion.
