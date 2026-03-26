# Guía de Parámetros de PySR (Regresión Simbólica)

Esta guía detalla los parámetros disponibles para configurar el regresor de PySR, organizados por su función dentro del proceso de búsqueda evolutiva.

---

## 1. Parámetros de Control de la Búsqueda
Estos definen qué tan profundo y qué tan exhaustivamente buscará el algoritmo la solución óptima.

* **`niterations`**: Número de veces que las poblaciones se mezclan (migración). Es el ciclo principal de entrenamiento.
* **`populations`**: Número de poblaciones separadas que evolucionan de forma independiente.
* **`population_size`**: Tamaño de cada población. Un tamaño mayor incrementa la diversidad pero ralentiza cada iteración.
* **`ncycles_per_iteration`**: Cuántos ciclos de evolución ocurren dentro de una sola iteración antes de que las poblaciones intercambien sus mejores individuos.
* **`maxsize`**: El número máximo de nodos en un árbol (suma de operadores, constantes y variables). Por defecto es 20.
* **`maxdepth`**: La profundidad máxima permitida para el árbol de la ecuación.
* **`model_selection`**: Define el criterio para elegir la "mejor" ecuación al finalizar.
    * `"accuracy"`: Selecciona la que tiene el mínimo error.
    * `"best"`: Busca un balance entre error y complejidad (salto de parsimonia).

---

## 2. Operadores y Complejidad
Define las reglas matemáticas y el "costo" de usar ciertos elementos en las fórmulas.

* **`unary_operators`**: Lista de funciones de un solo argumento (ej. `["sin", "cos", "exp", "log", "neg"]`).
* **`binary_operators`**: Operadores de dos argumentos (ej. `["+", "-", "*", "/", "pow"]`).
* **`complexity_of_operators`**: Diccionario para asignar pesos específicos a los operadores. Permite penalizar funciones complejas.
* **`complexity_of_constants`**: Complejidad asignada a cada constante numérica (por defecto 1).
* **`complexity_of_variables`**: Complejidad asignada a cada variable de entrada (por defecto 1).
* **`constraints`**: Diccionario para limitar la complejidad de los argumentos de un operador específico.
* **`nested_constraints`**: Evita que ciertos operadores se aniden dentro de sí mismos para prevenir estructuras excesivamente complejas.

---

## 3. Optimización de Constantes
Controla cómo se ajustan los valores numéricos una vez que se encuentra una estructura de ecuación prometedora.

* **`should_optimize_constants`**: Booleano que indica si se deben refinar las constantes mediante optimización numérica (BFGS).
* **`optimizer_algorithm`**: Algoritmo utilizado para el ajuste de constantes (por defecto `"BFGS"` o `"L-BFGS"`).
* **`optimizer_nrestarts`**: Cuántas veces reiniciar la optimización desde puntos aleatorios para evitar mínimos locales.
* **`optimizer_iterations`**: Número de iteraciones internas del optimizador.
* **`optimizer_probability`**: Probabilidad de que un individuo sea sometido a optimización de constantes durante la evolución.

---

## 4. Rendimiento y Paralelismo
Configuraciones para aprovechar el hardware disponible.

* **`procs`**: Número de procesos de Julia a lanzar para el cálculo paralelo.
* **`multithreading`**: Booleano. Si es `True`, utiliza hilos de ejecución en lugar de procesos independientes (ideal para sistemas con memoria compartida).
* **`batching`**: Si se debe entrenar utilizando subconjuntos de datos (necesario para datasets muy grandes).
* **`batch_size`**: Tamaño de la muestra aleatoria para cada paso de evaluación cuando el batching está activo.
* **`turbo`**: Utiliza `LoopVectorization.jl` en Julia para acelerar drásticamente los cálculos en CPUs compatibles.

---

## 5. Parámetros Técnicos y de Interfaz
Configuraciones de sistema, comunicación entre lenguajes y utilidades.

* **Operadores con lógica propia**: Permite definir funciones personalizadas directamente en sintaxis de Julia dentro de las listas de operadores.
* **`extra_sympy_mappings`**: Diccionario para mapear operadores personalizados de Julia a funciones de SymPy en Python.
* **`temp_equation_file`**: Indica si se debe generar un archivo `.csv` temporal con el registro de las ecuaciones encontradas.
* **`delete_tempfiles`**: Si se deben borrar automáticamente los archivos temporales al cerrar la sesión.
* **`verbosity`**: Nivel de detalle de los mensajes en consola (0 para silencio).
* **`progress`**: Booleano que habilita la barra de progreso visual en tiempo real.
* **`random_state`**: Semilla para garantizar la reproducibilidad de los resultados.
* **`denoise`**: Booleano. Aplica un proceso gaussiano para intentar filtrar el ruido de los datos antes de iniciar la búsqueda simbólica.