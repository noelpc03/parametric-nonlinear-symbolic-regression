# Guía de Parámetros de PySR (Regresión Simbólica)

Esta guía tiene dos objetivos:

1. Documentar qué parámetros de PySR se usan actualmente en este proyecto.
2. Explicar valores posibles y efecto práctico de cada parámetro para justificar decisiones en la tesis.

---

## 1. Configuración actual usada en el proyecto

Fuente de verdad:

- `src/config.py`
- `src/5_symbolic_regression/symbolic_regression.py`

### 1.1 Parámetros de búsqueda evolutiva

| Parámetro | Definición formal | Valor actual | Dónde se define | Decisión y motivo |
|---|---|---:|---|---|
| `niterations` | $n_{iter} \in \mathbb{N}^{+}$: número de iteraciones globales de evolución/migración. | `500` | `config.py` | Búsqueda profunda para casos difíciles (ej. raíces cerradas complejas). |
| `populations` | $P \in \mathbb{N}^{+}$: número de poblaciones (islas) en paralelo. | `30` | `config.py` | Más islas evolutivas para diversidad sin subir demasiado memoria por individuo. |
| `population_size` | $N_{pop} \in \mathbb{N}^{+}$: individuos por población. | `50` | `config.py` | Compromiso diversidad/tiempo por ciclo. |
| `ncycles_per_iteration` | $C \in \mathbb{N}^{+}$: ciclos evolutivos internos por iteración global. | `550` | `config.py` | Mayor exploración local antes de migración. |
| `maxsize` | $s_{max} \in \mathbb{N}^{+}$: cota superior de nodos del árbol simbólico. | `25` | `config.py` | Permite expresiones medianas-largas sin explotar tamaño del árbol. |
| `model_selection` | Función de selección $\hat f = \operatorname*{argmin}_{f \in \mathcal{H}} J(f)$ sobre Hall of Fame. | `"best"` | `symbolic_regression.py` | Balancea error y complejidad en el frente de Pareto. |
| `parsimony` | $\lambda \ge 0$: coeficiente de penalización por complejidad en el objetivo. | `0.0` | `config.py` | No se penaliza globalmente porque ya hay penalización por operador. |

### 1.2 Operadores y restricciones

| Parámetro | Definición formal | Valor actual | Decisión y motivo |
|---|---|---|---|
| `unary_operators` | Conjunto $\mathcal{U}$ de operadores unarios permitidos en la gramática de árboles. | `neg` + `safe_sqrt`, `safe_cbrt`, `safe_root4` ... `safe_root10` | Inyectar conocimiento de dominio para raíces n-ésimas reales y estabilidad numérica. |
| `binary_operators` | Conjunto $\mathcal{B}$ de operadores binarios permitidos. | `+`, `-`, `*`, `/`, `safe_pow` | `safe_pow` conserva signo y evita NaN para potencias fraccionarias. |
| `complexity_of_operators` | Mapa $c: \mathcal{O} \to \mathbb{R}_{+}$ (costo por operador). | `+,-,*:1`, `/:2`, raíces:2, `safe_pow:4` | Penalizar `safe_pow` para preferir raíces específicas más interpretables. |
| `constraints` | Restricciones de factibilidad $\mathcal{A}_o$ sobre argumentos de cada operador $o$. | `{"safe_pow": (9, 1)}` | Limita complejidad de argumentos de `safe_pow` para evitar árboles degenerados. |
| `nested_constraints` | Relación de anidamiento permitido/prohibido $R(o_{ext}, o_{int})$. | raíces no se anidan entre sí; `safe_pow` no anida `safe_pow` | Control explícito de explosión combinatoria y expresiones poco físicas. |

### 1.3 Pérdidas (loss)

| Modo | Definición formal | Flag | Descripción |
|---|---|---|---|
| MSE por defecto | $L_{MSE}=\frac{1}{N}\sum_{i=1}^{N}(\hat y_i-y_i)^2$ | `USE_SIGMOID_LOSS=False`, `USE_MATCH_COUNT_LOSS=False` | Usa pérdida por defecto de SymbolicRegression.jl (error cuadrático). |
| Sigmoidal | $L_{sig}=\sigma(k(|\hat y-y|-\varepsilon))$ por punto (promediada en dataset). | `USE_SIGMOID_LOSS=True` | Suaviza transición alrededor de un umbral `epsilon`. |
| Conteo duro (nuevo) | $L_{hard}=\frac{1}{N}\sum_{i=1}^{N}\mathbf{1}(|\hat y_i-y_i|\ge\varepsilon_{mc})$ | `USE_MATCH_COUNT_LOSS=True`, `MATCH_COUNT_EPSILON=1e-4` | Optimiza fracción de no-matches: 0 si `|y-ŷ|<1e-4`, 1 si no. |

### 1.4 Rendimiento y sistema

| Parámetro | Definición formal | Valor actual | Decisión y motivo |
|---|---|---:|---|
| `procs` | $p \in \mathbb{N}_{0}$: número de procesos de Julia para evaluación. | `0` | Configurado para evitar paralelismo de procesos (prioriza estabilidad de RAM en este entorno). |
| `turbo` | Indicador binario de activación de rutas SIMD/optimizadas. | `True` | Acelera evaluación numérica en CPU compatible (LoopVectorization). |
| `temp_equation_file` | Variable booleana de persistencia temporal de ecuaciones intermedias. | `True` | Mantener rastreo temporal de ecuaciones durante corrida. |
| `delete_tempfiles` | Variable booleana de limpieza automática de temporales. | `True` | Limpiar temporales automáticamente al finalizar. |

### 1.5 Parámetros del wrapper iterativo (no son de PySR puro)

Estos parámetros están en el algoritmo iterativo del proyecto y explican gran parte del tiempo total:

| Parámetro | Definición formal | Valor actual | Papel |
|---|---|---:|---|
| `NUM_ATTEMPTS` | $A \in \mathbb{N}^{+}$: ejecuciones independientes de PySR por iteración del wrapper. | `3` | Repite PySR por iteración y escoge el mejor hallazgo. |
| `MAX_ITERATIONS` | $I_{max} \in \mathbb{N}^{+} \cup \{\infty\}$: máximo de iteraciones externas del algoritmo iterativo. | `None` (sin límite) | Permite descubrir todas las ramas cuando el problema tiene más de 5 funciones objetivo. |
| `MIN_MATCH_FRACTION` | $\rho_{min} \in [0,1]$: fracción mínima de puntos matcheados para aceptar ecuación. | `0.05` | Umbral mínimo para aceptar una ecuación en la iteración actual. |
| `MAX_CONSECUTIVE_NO_MATCH` | $S_{max} \in \mathbb{N}_{0}$: límite de iteraciones consecutivas sin mejora. | `3` | Criterio de corte por estancamiento, con mayor tolerancia a oscilaciones estocásticas. |
| `MIN_POINTS` | $N_{min} \in \mathbb{N}^{+}$: mínimo de puntos para continuar iterando. | `5` | No sigue si quedan muy pocos puntos. |
| `EPSILON` | $\varepsilon_{rel}>0$: umbral relativo de match, $|y-\hat y|<\varepsilon_{rel}(1+|y|)$. | `0.005` | Umbral relativo de match post-entrenamiento (modos no duros). |

### 1.6 Justificación bibliográfica de cada valor elegido

Esta subsección responde a la pregunta metodológica central de tesis: por qué se eligió cada valor concreto usado hoy en el proyecto, y qué evidencia lo respalda.

#### 1.6.1 Búsqueda evolutiva

| Parámetro (valor) | Por qué se usa este valor en este proyecto | Evidencia/fuente |
|---|---|---|
| `niterations = 500` | Se prioriza exploración profunda por tratarse de descubrimiento de fórmulas analíticas (no simple ajuste numérico). `500` da presupuesto suficiente sin llegar al costo extremo de configuraciones tipo timeout de horas. | [PARAMSLM-1], [CRANMER-2023], [LACAVA-2021] |
| `populations = 30` | Implementa estrategia multi-isla para sostener diversidad estructural entre candidatos. Se alinea con la recomendación de usar múltiples islas para evitar convergencia prematura. | [PARAMSLM-1], [PARAMSLM-2], [KOZA-1992] |
| `population_size = 50` | Valor intermedio: mayor cobertura que defaults pequeños, pero con costo de memoria/tiempo manejable en entorno local. | [PARAMSLM-1], [PARAMSLM-2] |
| `ncycles_per_iteration = 550` | Se favorece refinamiento local dentro de cada isla antes de mezclar información, reduciendo homogenización prematura. | [PARAMSLM-1], [PARAMSLM-2] |
| `maxsize = 25` | Permite expresiones de complejidad media-alta (raíces anidadas, términos racionales) sin abrir demasiado el espacio de búsqueda y sin bloat excesivo. | [PARAMSLM-2], [LACAVA-2021] |
| `model_selection = "best"` | Se busca equilibrio precisión-complejidad (frente de Pareto) para priorizar ecuaciones interpretables en tesis, no solo mínima pérdida puntual. | [PARAMSLM-6], [PARAMSLM-7], [CRANMER-2023] |
| `parsimony = 0.0` (con penalización por operador) | No se agrega penalización global porque ya existe control de complejidad explícito en `complexity_of_operators`, restricciones y anidamiento. Evita doble penalización. | [PARAMSLM-2], [PARAMSLM-6], [SOTA-ESTADO-ARTE] |

#### 1.6.2 Operadores, restricciones y sesgo físico

| Parámetro (valor) | Por qué se usa este valor en este proyecto | Evidencia/fuente |
|---|---|---|
| `unary_operators = [neg + safe_root*]` | Inyecta conocimiento de dominio para raíces reales (pares e impares) y mejora estabilidad numérica en datos con signos mixtos. | [PARAMSLM-2], [CRANMER-2023] |
| `binary_operators = +,-,*,/,safe_pow` | Conserva gramática base interpretable y agrega `safe_pow` para generalizar potencias fraccionarias sin NaN por base negativa. | [PARAMSLM-2], [PARAMSLM-8] |
| `complexity_of_operators` con `safe_pow:4` | Penalización mayor a operador demasiado flexible para favorecer formas específicas (raíces dedicadas) más explicables en contexto científico. | [PARAMSLM-2], [PARAMSLM-6], [LACAVA-2021] |
| `constraints = {"safe_pow": (9,1)}` | Limita complejidad del exponente para forzar potencias simples/físicamente interpretables y reducir explosión combinatoria. | [PARAMSLM-2], [PARAMSLM-8] |
| `nested_constraints` (sin anidamiento entre raíces / sin `safe_pow` sobre `safe_pow`) | Evita construcciones simbólicas patológicas y reduce búsqueda en regiones poco plausibles. | [PARAMSLM-2], [CRANMER-2023], [KOZA-1992] |

#### 1.6.3 Pérdidas y criterio de match

| Parámetro (valor) | Por qué se usa este valor en este proyecto | Evidencia/fuente |
|---|---|---|
| Modo base `MSE` | Provee baseline estándar en literatura para comparación A/B y análisis de deltas. | [LACAVA-2021], [CRANMER-2023] |
| `MATCH_COUNT_EPSILON = 1e-4` | Umbral estricto para objetivo discreto de cobertura exacta de puntos, alineado con objetivo de tesis de “pasar por los puntos”. | [SOTA-ESTADO-ARTE], [PARAMSLM-5] |
| `USE_MATCH_COUNT_LOSS` (activación experimental) | Permite comparar directamente una pérdida orientada a matches contra MSE en el mismo pipeline. | [PARAMSLM-5], [KARTELJ-2023], [SU-2024] |
| `EPSILON = 0.005` (match relativo post-entrenamiento) | Estabiliza decisión de match en distintos órdenes de magnitud de $y$ mediante tolerancia relativa. | [PARAMSLM-5], [CRANMER-2023] |

#### 1.6.4 Rendimiento y recursos

| Parámetro (valor) | Por qué se usa este valor en este proyecto | Evidencia/fuente |
|---|---|---|
| `procs = 0` | Prioriza estabilidad de RAM en hardware local y evita sobrecoste de multiproceso para este entorno de tesis. | [PARAMSLM-4], [PARAMSLM-9] |
| `turbo = True` | Aprovecha optimizaciones SIMD de backend Julia para reducir costo de evaluación por expresión. | [PARAMSLM-4], [CRANMER-2023] |

#### 1.6.5 Wrapper iterativo (orquestación del pipeline)

| Parámetro (valor) | Por qué se usa este valor en este proyecto | Evidencia/fuente |
|---|---|---|
| `NUM_ATTEMPTS = 3` | Mitiga estocasticidad de una sola corrida de PySR por iteración externa y mejora robustez de selección de ecuación. | [PARAMSLM-1], [PARAMSLM-3] |
| `MAX_ITERATIONS = None` | El número de ramas no es fijo a priori; sin límite rígido se evita truncar casos con más funciones objetivo que el umbral anterior. | [SOTA-ESTADO-ARTE], [CRANMER-2023] |
| `MIN_MATCH_FRACTION = 0.05` | Evita aceptar ecuaciones espurias que expliquen una fracción mínima irrelevante de los puntos restantes. | [PARAMSLM-5], [LACAVA-2021] |
| `MAX_CONSECUTIVE_NO_MATCH = 3` | Criterio de paro por estancamiento con tolerancia suficiente a variación estocástica entre intentos. | [PARAMSLM-3], [KOZA-1992] |
| `MIN_POINTS = 5` | Impide sobre-optimizar sobre subconjuntos demasiado pequeños con baja confiabilidad estadística. | [PARAMSLM-5], [LACAVA-2021] |

---

## 2. Diccionario base de parámetros (qué es cada uno)

Esta sección preserva la explicación conceptual de cada parámetro (qué representa dentro de PySR), y además añade valores posibles y comportamiento esperado al cambiarlo.

## 2.1 Control de la búsqueda

| Parámetro | Qué es | Definición formal | Valores posibles / comunes | Qué pasa al subirlo o bajarlo |
|---|---|---|---|---|
| `niterations` | Número de iteraciones principales (ciclos de migración entre poblaciones). | $n_{iter} \in \mathbb{N}^{+}$. | Entero positivo (`10` a `2000+` en práctica). | Bajo: rápido pero menos exploración. Alto: más chance de encontrar fórmula correcta, con mayor tiempo. |
| `populations` | Número de poblaciones independientes (islas evolutivas). | $P \in \mathbb{N}^{+}$. | Entero positivo (`1` a `100+`). | Bajo: menor diversidad. Alto: mayor diversidad y más costo computacional. |
| `population_size` | Tamaño de cada población. | $N_{pop} \in \mathbb{N}^{+}$. | Entero positivo (`10` a `200+`). | Bajo: menos candidatos por generación. Alto: más cobertura del espacio de expresiones y más costo por ciclo. |
| `ncycles_per_iteration` | Ciclos evolutivos internos antes de migrar individuos entre poblaciones. | $C \in \mathbb{N}^{+}$. | Entero positivo (`10` a `1000+`). | Bajo: migración frecuente, menos refinamiento local. Alto: más refinamiento local, más tiempo por iteración. |
| `maxsize` | Número máximo de nodos del árbol simbólico (operadores, variables, constantes). | $s_{max} \in \mathbb{N}^{+}$. | Entero positivo (`5` a `50+`). | Bajo: fuerza expresiones simples. Alto: permite expresiones complejas pero aumenta riesgo de bloat. |
| `maxdepth` | Profundidad máxima del árbol simbólico. | $d_{max} \in \mathbb{N}^{+}$. | Entero positivo (`3` a `20+` típico). | Bajo: árboles compactos, menos expresividad. Alto: expresividad mayor y riesgo de estructuras inestables. |
| `model_selection` | Criterio para escoger ecuación final del Hall of Fame. | $\hat f = \arg\min_{f \in \mathcal{H}} J(f)$ según el criterio seleccionado. | `"accuracy"`, `"best"` (según versión). | `accuracy`: privilegia menor error. `best`: balance error-complejidad (más interpretable). |

## 2.2 Operadores y complejidad

| Parámetro | Qué es | Definición formal | Valores posibles / comunes | Qué pasa al subirlo o bajarlo |
|---|---|---|---|---|
| `unary_operators` | Lista de funciones unarias permitidas en expresiones. | Conjunto $\mathcal{U}$ de operadores aridad-1. | Lista de strings Julia (`"sin"`, `"log"`, `"neg"`, funciones `safe_*`). | Más operadores: más expresividad, más espacio de búsqueda y tiempo. |
| `binary_operators` | Lista de operadores binarios permitidos. | Conjunto $\mathcal{B}$ de operadores aridad-2. | Lista (`"+"`, `"-"`, `"*"`, `"/"`, `"pow"`, funciones custom). | Operadores más potentes facilitan ajuste, pero pueden inducir sobreajuste/simbolismo espurio. |
| `complexity_of_operators` | Peso de complejidad por operador. | Función de costo $c: \mathcal{O} \to \mathbb{R}_{+}$. | Diccionario operador->costo (int/float positivo). | Costo alto desalienta operador; costo bajo lo vuelve más frecuente. |
| `complexity_of_constants` | Costo de usar constantes numéricas. | Escalar $c_{const} \in \mathbb{R}_{+}$. | Entero/float positivo (default suele ser `1`). | Alto: menos constantes libres. Bajo: mayor ajuste numérico (riesgo de sobreajuste). |
| `complexity_of_variables` | Costo de usar variables de entrada. | Escalar/vector $c_{var} \in \mathbb{R}_{+}$. | Entero/float positivo. | Alto: reduce dependencia de variables. Bajo: facilita uso de más variables. |
| `constraints` | Restricciones de complejidad para argumentos de operadores concretos. | Conjunto factible $\mathcal{A}_o$ para cada operador $o$. | Dict (formato depende del operador y versión). | Restringir más: reduce explosión combinatoria; restringir menos: mayor libertad, más costo. |
| `nested_constraints` | Reglas para impedir anidamientos específicos. | Relación $R(o_{ext}, o_{int})$ de anidamiento permitido. | Dict de operador externo vs internos permitidos/prohibidos. | Más restricciones: expresiones más estables e interpretables. Menos restricciones: mayor expresividad, más riesgo de fórmulas patológicas. |

## 2.3 Optimización de constantes

| Parámetro | Qué es | Definición formal | Valores posibles / comunes | Qué pasa al subirlo o bajarlo |
|---|---|---|---|---|
| `should_optimize_constants` | Activa refinamiento numérico de constantes. | Variable binaria $z_{opt}\in\{0,1\}$. | Booleano. | `False`: más rápido pero constantes menos precisas. `True`: mejor ajuste local con más tiempo. |
| `optimizer_algorithm` | Algoritmo de optimización local de constantes. | Selección $\mathcal{A}_{opt}$ del método de optimización. | `"BFGS"`, `"L-BFGS"` (según versión). | Algoritmos más robustos suelen mejorar ajuste, pero pueden costar más CPU. |
| `optimizer_nrestarts` | Número de reinicios del optimizador. | $r \in \mathbb{N}_{0}$. | Entero no negativo. | Más reinicios: menor riesgo de mínimo local; más tiempo. |
| `optimizer_iterations` | Iteraciones internas del optimizador de constantes. | $t_{opt} \in \mathbb{N}^{+}$. | Entero positivo. | Más iteraciones: mayor refinamiento, mayor costo. |
| `optimizer_probability` | Probabilidad de aplicar optimización a un individuo. | $p_{opt} \in [0,1]$. | Float en `[0,1]`. | Baja: más rápido. Alta: más ajuste fino, más costo global. |

## 2.4 Rendimiento y paralelismo

| Parámetro | Qué es | Definición formal | Valores posibles / comunes | Qué pasa al subirlo o bajarlo |
|---|---|---|---|---|
| `procs` | Número de procesos de Julia para paralelismo. | $p \in \mathbb{N}_{0}$. | `0` o entero positivo (depende versión/entorno). | Más procesos: más throughput y más RAM. Menos: más estable en hardware limitado. |
| `multithreading` | Uso de hilos en lugar de procesos. | Variable binaria $z_{mt}\in\{0,1\}$. | Booleano. | Puede reducir costo de comunicación en memoria compartida; depende del hardware. |
| `batching` | Entrenamiento por lotes de datos. | Variable binaria $z_{batch}\in\{0,1\}$. | Booleano. | `True`: menor costo por evaluación en datasets grandes; más ruido estocástico. |
| `batch_size` | Tamaño de lote cuando `batching=True`. | $B \in \mathbb{N}^{+}$ muestras por batch. | Entero positivo. | Lote pequeño: rápido y ruidoso. Lote grande: más estable y más costoso. |
| `turbo` | Activación de optimizaciones de bajo nivel en Julia. | Variable binaria $z_{turbo}\in\{0,1\}$. | Booleano. | `True`: puede acelerar bastante en CPU compatible. |

## 2.5 Parámetros técnicos e interfaz

| Parámetro | Qué es | Definición formal | Valores posibles / comunes | Qué pasa al subirlo o bajarlo |
|---|---|---|---|---|
| Operadores personalizados | Funciones definidas directamente en sintaxis Julia dentro de listas de operadores. | Conjunto $\mathcal{O}_{custom}$ añadido a la gramática. | Strings con definición Julia válida. | Aumenta capacidad de modelar dominio específico; exige mapping correcto a SymPy. |
| `extra_sympy_mappings` | Traducción de operadores Julia a SymPy en Python. | Función de mapeo $\phi: \mathcal{O}_{julia} \to \mathcal{O}_{sympy}$. | Dict nombre_operador->lambda SymPy. | Mapping incorrecto rompe evaluación y comparación de expresiones. |
| `temp_equation_file` | Genera archivo temporal de ecuaciones durante entrenamiento. | Variable binaria $z_{tmp}\in\{0,1\}$. | Booleano. | Útil para trazabilidad/debug. |
| `delete_tempfiles` | Borra temporales al terminar. | Variable binaria $z_{clean}\in\{0,1\}$. | Booleano. | `True`: workspace limpio. `False`: conserva artefactos para auditoría. |
| `verbosity` | Nivel de detalle de logs. | $v \in \mathbb{N}_{0}$. | Entero (`0` mínimo). | Más verbosity: mejor diagnóstico, más ruido en consola. |
| `progress` | Barra de progreso visual. | Variable binaria $z_{prog}\in\{0,1\}$. | Booleano. | Mejora observabilidad, sin impacto fuerte en calidad. |
| `random_state` | Semilla para reproducibilidad. | $s \in \mathbb{Z}$ o `None`. | Entero o `None`. | Fija semilla para comparaciones justas entre corridas. |
| `denoise` | Preproceso de denoising en los datos. | Variable binaria $z_{denoise}\in\{0,1\}$. | Booleano. | Útil con ruido real; puede introducir sesgo si los datos ya son limpios/sintéticos. |

---

## 3. Parámetros posibles y efecto según valor

Esta sección resume rangos prácticos y qué ocurre al subir/bajar cada parámetro.

## 3.1 Control de búsqueda

| Parámetro | Definición formal | Valores posibles (prácticos) | Si es bajo | Si es alto |
|---|---|---|---|---|
| `niterations` | $n_{iter}\in\mathbb{N}^{+}$. | `10` a `2000+` | Rápido, riesgo de subajuste estructural | Mayor chance de hallar fórmula correcta, pero tiempo mucho mayor |
| `populations` | $P\in\mathbb{N}^{+}$. | `1` a `100+` | Menos diversidad entre islas | Más diversidad, mayor costo computacional |
| `population_size` | $N_{pop}\in\mathbb{N}^{+}$. | `10` a `200+` | Menor cobertura del espacio de expresiones | Más cobertura y más costo por ciclo |
| `ncycles_per_iteration` | $C\in\mathbb{N}^{+}$. | `10` a `1000+` | Migración frecuente, menor refinamiento local | Más refinamiento local, iteraciones más lentas |
| `maxsize` | $s_{max}\in\mathbb{N}^{+}$. | `5` a `50+` | Ecuaciones demasiado simples | Puede capturar estructuras complejas, pero riesgo de bloat |
| `model_selection` | Regla $\hat f = \arg\min_{f\in\mathcal{H}}J(f)$. | `"accuracy"`, `"best"` | `accuracy`: favorece error mínimo | `best`: favorece equilibrio error-complejidad |

## 3.2 Operadores, complejidad y restricciones

| Parámetro | Definición formal | Valores posibles | Efecto |
|---|---|---|---|
| `unary_operators` | Conjunto $\mathcal{U}$ de operadores unarios permitidos. | Lista de funciones Julia válidas | Más operadores = mayor expresividad y mayor espacio de búsqueda |
| `binary_operators` | Conjunto $\mathcal{B}$ de operadores binarios permitidos. | Lista de operadores binarios | Igual que arriba; operadores potentes aceleran ajuste pero aumentan ambigüedad |
| `complexity_of_operators` | Función de costo $c: \mathcal{O}\to\mathbb{R}_{+}$. | Enteros/floats positivos | Penalización alta reduce uso del operador; baja lo favorece |
| `constraints` | Conjunto factible $\mathcal{A}_o$ para argumentos de cada operador. | Dict por operador (p. ej. tupla en binarios) | Limita complejidad de argumentos para controlar explosión |
| `nested_constraints` | Relación de anidamiento $R(o_{ext},o_{int})$. | Dict de anidamiento permitido/no permitido | Evita composiciones patológicas (ej. raíz de raíz de raíz) |

## 3.3 Loss y criterio de match

| Parámetro | Definición formal | Valores posibles | Efecto |
|---|---|---|---|
| `USE_SIGMOID_LOSS` | Indicador binario $z_{sig}\in\{0,1\}$. | `True/False` | Activa pérdida suave alrededor de umbral |
| `USE_MATCH_COUNT_LOSS` | Indicador binario $z_{hard}\in\{0,1\}$. | `True/False` | Activa objetivo discreto de maximizar matches |
| `MATCH_COUNT_EPSILON` | $\varepsilon_{mc}>0$ en $\mathbf{1}(|y-\hat y|<\varepsilon_{mc})$. | `1e-6` a `1e-2` típico | Umbral bajo: más estricto, menos matches; umbral alto: más permisivo |
| `EPSILON` (post-match) | $\varepsilon_{rel}>0$ en $|y-\hat y|<\varepsilon_{rel}(1+|y|)$. | `1e-4` a `1e-1` típico | Controla tolerancia relativa al evaluar cobertura en wrapper |

Regla importante:

- No activar simultáneamente `USE_SIGMOID_LOSS=True` y `USE_MATCH_COUNT_LOSS=True`.

## 3.4 Rendimiento y paralelismo

| Parámetro | Definición formal | Valores posibles | Efecto |
|---|---|---|---|
| `procs` | $p\in\mathbb{N}_{0}$. | `0` o entero positivo (según versión) | Más procesos acelera, pero consume más RAM |
| `turbo` | Indicador binario $z_{turbo}\in\{0,1\}$. | `True/False` | `True` puede mejorar rendimiento en CPU compatible |
| `batching` | Indicador binario $z_{batch}\in\{0,1\}$. | `True/False` | Reduce costo por paso en datasets grandes, aumenta ruido estocástico |
| `batch_size` | $B\in\mathbb{N}^{+}$ (muestras por batch). | entero positivo | Batch chico: rápido/ruidoso; grande: más estable/costoso |

## 3.5 Optimización de constantes

Según versión de PySR/SymbolicRegression.jl, se pueden controlar parámetros del optimizador (BFGS/L-BFGS, reinicios, iteraciones). En general:

- Más optimización de constantes: mejor ajuste local, más tiempo.
- Menos optimización: más velocidad, peor refinamiento numérico.

---

## 4. Justificación técnica de las decisiones actuales

1. La justificación completa parámetro-por-parámetro está en la sección 1.6.
2. El principio general de diseño fue: maximizar descubrimiento de estructura analítica bajo restricciones reales de cómputo y trazabilidad para tesis.
3. Se aplicó sesgo físico explícito (operadores seguros + restricciones) para mejorar interpretabilidad y estabilidad.
4. La comparación A/B de pérdidas se mantuvo sobre el mismo pipeline para aislar el efecto del criterio de pérdida.
5. La configuración final balancea exploración evolutiva, control de complejidad y robustez operativa.

---

## 5. Bibliografía y fuentes

### 5.1 Referencias externas

- [CRANMER-2023] Cranmer, M. et al. *Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl*. arXiv:2305.01582.
- [LACAVA-2021] La Cava, W. et al. *Contemporary Symbolic Regression Methods and their Relative Performance (SRBench)*. arXiv:2107.14351.
- [KOZA-1992] Koza, J. *Genetic Programming*. MIT Press.
- [KARTELJ-2023] Kartelj, A. et al. *RILS-ROLS: A Robust Iterated Local Search Method for Symbolic Regression*.
- [SU-2024] Su, F. et al. *Smooth Sigmoid Surrogate: A Differentiable Alternative to Greedy Search in Trees*.

### 5.2 Fuentes internas usadas para esta guía

- [PARAMSLM-1] `docs/paramsLM.md` (sección de island model, `niterations`, `populations`, `population_size`, `ncycles_per_iteration`).
- [PARAMSLM-2] `docs/paramsLM.md` (sección de operadores, complejidad, `constraints`, `nested_constraints`).
- [PARAMSLM-3] `docs/paramsLM.md` (sección de estocasticidad, replacement/evolution, ajuste de estabilidad de búsqueda).
- [PARAMSLM-4] `docs/paramsLM.md` (sección de rendimiento: `procs`, `multithreading`, `turbo`, despliegue HPC).
- [PARAMSLM-5] `docs/paramsLM.md` (sección de pérdidas, robustez, criterio de evaluación de matches y ruido).
- [PARAMSLM-6] `docs/paramsLM.md` (sección de selección de modelo y frente de Pareto).
- [PARAMSLM-7] `docs/paramsLM.md` (discusión de score/parsimony jump en selección `best`).
- [PARAMSLM-8] `docs/paramsLM.md` (restricción de potencias tipo `pow: (9,1)` y sesgo estructural).
- [PARAMSLM-9] `docs/paramsLM.md` (trade-off de cómputo en entornos limitados vs HPC).
- [SOTA-ESTADO-ARTE] `SOTA/estadoDelArte.tex` (estado del arte, bibliografía consolidada de SR para tesis y justificación de pérdidas suaves/no-MSE).