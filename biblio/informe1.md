Análisis Avanzado de la Regresión Simbólica: Fundamentos Bibliográficos y Estrategias de Optimización Basadas en la Coincidencia de Puntos
La regresión simbólica representa uno de los desafíos más profundos y gratificantes dentro del aprendizaje automático contemporáneo, situándose en la intersección de la inteligencia artificial, la optimización combinatoria y el descubrimiento científico. A diferencia de las técnicas de regresión convencionales, que se limitan a ajustar parámetros dentro de una estructura de modelo predefinida (como ocurre en la regresión lineal o las redes neuronales), la regresión simbólica asume la tarea más ambiciosa de descubrir simultáneamente tanto la forma funcional de la ecuación como sus coeficientes numéricos.[1, 2] Este paradigma busca identificar expresiones matemáticas que no solo se ajusten a los datos observacionales, sino que también revelen los principios subyacentes de los sistemas complejos, proporcionando modelos que son intrínsecamente interpretables y capaces de generalizar más allá del dominio de entrenamiento.[3, 4]
La motivación para utilizar la regresión simbólica nace de la necesidad de transparencia en campos donde las "cajas negras" son insuficientes, como la física, la biología de sistemas y la ingeniería.[4, 5] Sin embargo, la búsqueda en el espacio de todas las combinaciones posibles de operadores, variables y constantes es un problema de una complejidad computacional inmensa, recientemente clasificado como NP-duro.[6, 7] Para navegar este espacio, la comunidad de investigación ha recurrido tradicionalmente a la programación genética, un motor evolutivo que mimetiza la selección natural para refinar poblaciones de expresiones matemáticas.[8, 9] En los últimos años, han surgido nuevas preocupaciones sobre las métricas tradicionales de éxito, específicamente la excesiva dependencia del error cuadrático medio (MSE), lo que ha dado lugar a técnicas innovadoras que priorizan la "coincidencia de puntos" o "hits", garantizando que el modelo capture la estructura esencial del fenómeno incluso en presencia de ruido o valores atípicos.[10, 11, 12]
El Legado de la Programación Genética y la Bibliografía Fundamental
El estudio de la regresión simbólica es inseparable de la evolución de la programación genética como disciplina. Para cualquier investigador o profesional que desee profundizar en este tema, es fundamental trazar la línea del tiempo bibliográfica que comienza con los trabajos pioneros de John R. Koza en la década de 1990.
Las Piedras Angulares de John R. Koza
La obra fundacional por excelencia es Genetic Programming: On the Programming of Computers by Means of Natural Selection (1992). En este volumen, Koza presenta la programación genética no solo como una técnica de optimización, sino como un nuevo paradigma de computación donde las poblaciones de programas de computadora (típicamente representados como estructuras de árbol en lenguajes como LISP) se crían genéticamente utilizando principios darwinianos.[8, 9, 13] Koza ilustra la regresión simbólica mediante ejemplos clásicos, como la recuperación de ecuaciones econométricas a partir de datos empíricos ruidosos, estableciendo los fundamentos de los operadores de cruce y mutación aplicados a árboles de sintaxis.[8, 14]
La evolución de estas ideas continuó con Genetic Programming III: Darwinian Invention and Problem Solving (1999), donde Koza y su equipo demuestran que la programación genética puede producir soluciones competitivas con el ingenio humano, incluyendo el redescubrimiento de invenciones patentadas en el diseño de circuitos analógicos y sistemas de control.[15] Este texto es crucial para entender la transición de la regresión simbólica desde un ejercicio académico hacia una herramienta de ingeniería capaz de manejar problemas de alta dimensionalidad y restricciones físicas.[15, 16]
Literatura de Soporte y Teórica
Para complementar la visión de Koza, es esencial recurrir a textos que aborden la teoría de los algoritmos genéticos y las estructuras de datos evolutivas. La obra de David Goldberg, Genetic Algorithms in Search, Optimization and Machine Learning (1988), proporciona el marco matemático necesario para comprender la dinámica de las poblaciones y los teoremas de los esquemas que subyacen a la búsqueda simbólica.[9] Asimismo, Zbigniew Michalewicz, en su libro Genetic Algorithms + Data Structures = Evolution Programs (1996), ofrece una perspectiva técnica sobre cómo la representación de los individuos afecta la eficiencia del algoritmo, un tema vital cuando se trabaja con expresiones matemáticas complejas que van más allá de los árboles simples.[9]
En el ámbito hispanohablante, la obra Computación Evolutiva (2019), editada por Carlos Artemio Coello Coello, representa uno de los recursos más actualizados y rigurosos.[17] Este libro, que cuenta con la colaboración de la Academia Mexicana de Computación, desglosa los conceptos fundamentales de los algoritmos evolutivos, la optimización multiobjetivo y su aplicación en problemas de regresión, siendo una referencia obligada para investigadores que buscan bibliografía de alta calidad en español.[17]
Obra Referencial
	
Autor(es)
	
Año
	
Enfoque Principal
Genetic Programming
	
John R. Koza
	
1992
	
Introducción al paradigma y regresión simbólica inicial [8]
Genetic Programming III
	
John R. Koza et al.
	
1999
	
Invención automática y aplicaciones en ingeniería [15]
Genetic Algorithms in Search
	
David Goldberg
	
1988
	
Bases teóricas de la computación evolutiva [9]
Evolutionary Algorithms for SR
	
Gabriel Kronberger
	
2024
	
Guía moderna para profesionales y aplicaciones industriales [2]
Computación Evolutiva
	
Coello Coello (Ed.)
	
2019
	
Panorama exhaustivo de técnicas evolutivas en español [17]
Limitaciones del Error Cuadrático Medio (MSE) en la Regresión Simbólica
El Error Cuadrático Medio (MSE) ha sido durante mucho tiempo la métrica por defecto en la regresión debido a su conveniencia matemática. Definido como el promedio de los cuadrados de las diferencias entre los valores predichos y los reales, el MSE es una función convexa y diferenciable que facilita el uso de métodos basados en el gradiente.[18, 19] Sin embargo, en la regresión simbólica, el uso exclusivo del MSE puede ser contraproducente.
El principal problema del MSE es su extrema sensibilidad a los valores atípicos o ruidosos. Al elevar los errores al cuadrado, una pequeña cantidad de puntos con desviaciones grandes puede dominar completamente la función de aptitud, obligando al algoritmo genético a "desperdiciar" complejidad en la expresión para intentar ajustarse a datos erróneos.[19] Esto resulta en el fenómeno del sobreajuste, donde el modelo pierde su capacidad de generalización y produce ecuaciones innecesariamente largas y difíciles de interpretar.[20]
Desde una perspectiva estadística, minimizar el MSE equivale a realizar una estimación de la media. En muchos problemas de descubrimiento científico, lo que se busca no es la media de los datos ruidosos, sino la tendencia central o la forma funcional correcta que describe la mayoría de los puntos.[21, 22] Esto sugiere que las métricas que miden la "coincidencia de puntos" (cuántos puntos caen dentro de un margen de error aceptable) pueden ser mucho más informativas para identificar la estructura verdadera de un fenómeno que una métrica que promedia todas las discrepancias cuadráticas.[11]
Técnicas para Priorizar la Coincidencia de Puntos y el Conteo de "Hits"
La necesidad de priorizar la precisión local sobre el error agregado ha llevado al desarrollo de varias técnicas dentro de la programación genética que se alejan del MSE. La más intuitiva de estas es el concepto de "hits" o aciertos.
El Sistema de Conteo de Hits y Bonificaciones de Aptitud
En las implementaciones clásicas de programación genética, un "hit" se registra para un caso de entrenamiento si el valor predicho por el modelo está dentro de una tolerancia definida (τ) respecto al valor objetivo.[10, 16] Esta técnica es fundamental en la síntesis de programas y el descubrimiento de algoritmos, donde un error pequeño puede significar un fracaso total de la lógica.
Una técnica efectiva para integrar este concepto en la regresión simbólica es el uso de una función de aptitud híbrida. Por ejemplo, el sistema G-PEA define la aptitud de un individuo basándose en el error promedio, pero aplica una bonificación significativa por cada acierto logrado.[10] Un esquema documentado ofrece una reducción del 0.5% en la puntuación de error por cada 1% de aciertos totales en el conjunto de entrenamiento.[10] Esto crea una presión de selección que favorece a los individuos que "resuelven" correctamente gran parte del problema, incluso si fallan estrepitosamente en unos pocos puntos difíciles, lo que a menudo ayuda al algoritmo a saltar de mínimos locales hacia la forma funcional correcta.[10]
Precisión Basada en Tolerancia (Accτ​) y Robustez
En la investigación moderna, especialmente en el contexto de los modelos de lenguaje aplicados a la regresión simbólica (como Symbolic-R1 o SymbolicChat), se ha estandarizado la métrica de precisión basada en tolerancia (Accτ​).[11, 23] Esta métrica calcula el porcentaje de puntos de datos donde el error relativo es menor que un umbral específico (por ejemplo, 10−3).
El uso de Accτ​ es una respuesta directa a la debilidad de las métricas numéricas convencionales como el R2 o el MSE. Se ha observado que algunas ecuaciones con formas matemáticas completamente erróneas pueden lograr un MSE bajo mediante la optimización excesiva de sus constantes numéricas, lo que enmascara la discrepancia estructural.[11, 23] Al evaluar el éxito mediante el conteo de puntos que caen dentro de una tolerancia estricta, los investigadores pueden distinguir mejor entre modelos que simplemente "promedian" los datos y aquellos que han descubierto el esqueleto simbólico correcto.[23]
Técnica
	
Mecanismo
	
Ventaja en Regresión Simbólica
Hit Count Bonus
	
Aplica descuentos en la penalización por cada punto "exacto".[10]
	
Incentiva la resolución de casos difíciles sin penalizar excesivamente fallos aislados.
Tolerance Accuracy (Accτ​)
	
Mide el porcentaje de puntos con error relativo inferior a un umbral τ.[11]
	
Proporciona una medida clara de la fidelidad del modelo a la estructura de los datos.
Success Rate
	
Evalúa la probabilidad de encontrar la expresión exacta en múltiples ejecuciones.[24]
	
Permite comparar la eficiencia de búsqueda entre algoritmos genéticos y búsqueda aleatoria.
Selección de Lexicase: El Especialista sobre el Promedio
Una de las innovaciones más importantes en la teoría de la selección para la programación genética es la Selección de Lexicase.[25, 26] Mientras que los métodos tradicionales como la selección por torneo agregan el desempeño de un individuo en todos los casos de prueba en una sola puntuación (como el MSE total), la selección de Lexicase trata cada punto de datos como una barrera de filtrado independiente.[26, 27]
Mecanismo de Selección de Lexicase
El proceso de selección de Lexicase es estocástico y dinámico:

    Se toma el conjunto total de puntos de datos y se baraja su orden de manera aleatoria para cada evento de selección.
    Se selecciona el primer punto de datos de la lista barajada.
    Se eliminan de la consideración a todos los individuos de la población cuyo error en ese punto específico sea peor que el mejor error encontrado en la población actual para ese mismo punto.
    Si queda más de un individuo, se repite el proceso con el siguiente punto de datos de la lista.[16, 26, 27]

Este método tiene un efecto profundo: permite la supervivencia de "especialistas". Un individuo puede tener un error global mediocre (un MSE alto), pero si es el mejor de la población en resolver un grupo específico de puntos de datos difíciles, tendrá una alta probabilidad de ser seleccionado como padre.[26] En la regresión simbólica, esto preserva la diversidad genética y evita que la población converja prematuramente hacia soluciones simplistas que solo se ajustan a la parte fácil del conjunto de datos.[25, 28]
Epsilon-Lexicase (ϵ-Lexicase) y EPLEX
Para la regresión de valores continuos, la selección de Lexicase estándar es a menudo demasiado estricta, ya que requiere que un individuo sea exactamente el mejor en un punto para sobrevivir. Para solucionar esto, se desarrolló la variante ϵ-Lexicase, también conocida como EPLEX.[12, 16] En esta versión, se define un umbral ϵ para cada punto de datos. Un individuo sobrevive al filtrado si su error en ese punto está dentro de una distancia ϵ del error del mejor individuo.[12, 27]
Este umbral ϵ no es estático; se calcula automáticamente basándose en la distribución de errores de la población actual (usando a menudo la desviación absoluta mediana), lo que permite que el algoritmo se adapte a la dificultad de los datos en tiempo real.[12] Los experimentos en el benchmark SRBench han demostrado que EPLEX es uno de los métodos de selección más robustos, superando sistemáticamente a la selección por torneo y a la optimización multiobjetivo en la recuperación de ecuaciones en presencia de ruido.[12, 27, 28]
Funciones de Pérdida Robustas y la Pérdida Epsilon-Insensible
Otra estrategia fundamental para priorizar la coincidencia de puntos proviene del campo de la regresión de vectores de soporte (SVR): la función de pérdida epsilon-insensible (Lϵ​).[21, 29]
La Geometría de la Pérdida Epsilon-Insensible
A diferencia del MSE, que penaliza cualquier desviación del objetivo, la pérdida epsilon-insensible define un "tubo" de ancho 2ϵ alrededor de los valores reales. Si la predicción cae dentro de este tubo, la pérdida es exactamente cero.[29] Matemáticamente: Lϵ​(y,f(x))=max(0,∣y−f(x)∣−ϵ) Este enfoque cambia radicalmente la dinámica de la evolución. Al no penalizar los errores pequeños, el algoritmo genético deja de obsesionarse con el ajuste fino de los residuos de bajo nivel y se concentra en mover la estructura de la ecuación para que la mayor cantidad posible de puntos de datos caigan dentro del margen aceptable.[21, 29]
Esta técnica es particularmente útil cuando se sabe que los datos contienen ruido de medición con una magnitud conocida. Si ϵ se ajusta para reflejar el nivel de ruido, el algoritmo ignorará las fluctuaciones aleatorias y se centrará en capturar la señal subyacente.[21] Además, el uso de esta pérdida tiende a producir modelos más simples (parsimoniosos), ya que no hay incentivo para añadir términos complejos solo para reducir errores que ya están dentro de la banda de tolerancia.[29]
Comparación de Funciones de Pérdida en Regresión Simbólica
Función de Pérdida
	
Sensibilidad a Outliers
	
Comportamiento con Ruido
	
Priorización de Puntos
MSE (L2​)
	
Muy Alta
	
Intenta promediar el ruido, causando sobreajuste.[19]
	
Baja (se enfoca en la magnitud total).
MAE (L1​)
	
Moderada
	
Más robusta que MSE; estima la mediana.[30]
	
Media (penaliza linealmente).
Huber Loss
	
Baja
	
Híbrida; lineal para errores grandes y cuadrática para pequeños.[31]
	
Moderada (balanceada).
Epsilon-Insensible
	
Muy Baja
	
Ignora el ruido dentro de la banda ϵ.[29]
	
Alta (maximiza puntos dentro del tubo).
Cauchy Loss
	
Mínima
	
Penalización logarítmica; casi ignora los outliers extremos.[19]
	
Media (se enfoca en la estabilidad central).
Frameworks y Herramientas para Implementar Técnicas Avanzadas
El ecosistema de software para la regresión simbólica ha madurado significativamente, permitiendo a los investigadores aplicar estas técnicas sin necesidad de programar los motores evolutivos desde cero.
PySR y el Poder de Julia
PySR es una biblioteca de Python que actúa como interfaz para un motor de búsqueda extremadamente optimizado escrito en Julia (SymbolicRegression.jl).[5, 32] Una de sus características más potentes es la capacidad de definir funciones de pérdida personalizadas a nivel de elemento utilizando cadenas de texto con sintaxis de Julia.[5, 31]
Esto permite implementar directamente técnicas de coincidencia de puntos. Por ejemplo, se puede definir una pérdida epsilon-insensible o una pérdida que use pesos personalizados para priorizar regiones específicas del espacio de datos.[31] PySR ya integra de forma nativa opciones como L1EpsilonInsLoss(ϵ) y L2EpsilonInsLoss(ϵ), facilitando la transición desde el MSE hacia enfoques más robustos.[31] Además, su arquitectura de "islas" evolutivas permite que diferentes subpoblaciones exploren distintas regiones del frente de Pareto de precisión-complejidad de manera paralela y asíncrona.[5]
gplearn y Fitness Personalizado
Para usuarios que prefieren mantenerse dentro del ecosistema puro de scikit-learn, gplearn ofrece una implementación accesible de programación genética.[33, 34] Aunque sus métricas por defecto son MSE y MAE, permite la definición de medidas de aptitud personalizadas a través de la función fitness.make_fitness().[33]
Para implementar una técnica de coincidencia de puntos en gplearn, el usuario puede crear una función que cuente cuántas predicciones están dentro de una tolerancia dada y devolver este conteo como la puntuación de aptitud. Al configurar greater_is_better=True, el algoritmo evolucionará las expresiones para maximizar el número de "hits".[33] Es crucial, en este caso, considerar la presión de parsimonia para evitar que el algoritmo genere expresiones gigantescas que "memoricen" los puntos mediante una complejidad excesiva.[33]
Operon y el Estado del Arte
Operon es un framework de regresión simbólica escrito en C++ que destaca por su velocidad y por implementar técnicas avanzadas como el cruce semántico y la selección de Lexicase.[6, 16] En comparaciones independientes realizadas en SRBench, Operon ha demostrado ser uno de los algoritmos más rápidos y precisos para descubrir modelos en conjuntos de datos ruidosos del mundo real, gracias a su eficiente manejo de la diversidad poblacional y su capacidad para optimizar constantes numéricas mediante algoritmos de optimización local como el método de Levenberg-Marquardt o BFGS.[6, 16]
El Benchmark SRBench: Estándares de Evaluación Modernos
La evaluación de la regresión simbólica ha pasado de ser anecdótica a ser sistemática gracias a iniciativas como SRBench.[4, 35] Este proyecto mantiene un repositorio de cientos de conjuntos de datos con "verdad terrenal" (ground truth), donde la fórmula original que generó los datos es conocida.[4, 16]
SRBench utiliza métricas de evaluación que van mucho más allá del simple error de ajuste. Se analizan la tasa de recuperación simbólica (qué tan a menudo el algoritmo encuentra la ecuación exacta), la tasa de éxito de precisión (R2>0.999) y la complejidad del modelo final.[16, 36] Los estudios realizados con SRBench han confirmado que los métodos que incorporan mecanismos de selección basados en puntos individuales (como ϵ-Lexicase) y optimización local de constantes superan drásticamente a los métodos de programación genética "clásicos" de la era de Koza.[6, 16]
Algoritmo
	
Optimización de Constantes
	
Selección Destacada
	
Rendimiento en SRBench
Operon
	
BFGS / SGD [35]
	
Lexicase / Torneo
	
Líder en precisión y velocidad.[6]
PySR
	
BFGS (Optim.jl) [5]
	
Multiobjetivo (Pareto)
	
Excelente en interpretabilidad científica.[32]
GP-GOMEA
	
Gradiente Local [6]
	
Elitismo Semántico
	
Mejor balance entre simplicidad y precisión.[6]
EPLEX
	
No nativa (solo selección)
	
ϵ-Lexicase [12]
	
Muy robusto frente al ruido en los datos.[12]
gplearn
	
No nativa [35]
	
Torneo
	
Referencia base de rendimiento.[6]
Nuevas Fronteras: TaylorGP y Modelos de Lenguaje
El campo no ha dejado de innovar, y recientemente han surgido dos tendencias que prometen transformar la manera en que se prioriza la estructura matemática sobre el simple ajuste numérico.
TaylorGP y el Guía por Derivadas
TaylorGP es un enfoque novedoso que utiliza polinomios de Taylor para guiar la búsqueda simbólica.[37] Al aproximar los datos localmente mediante una serie de Taylor, el algoritmo puede identificar características estructurales como la monotonicidad, la paridad y la separabilidad de variables antes de comenzar la evolución genética.[37] Esto permite que el motor de búsqueda priorice expresiones que "se comporten" como la función verdadera en sus derivadas, lo cual es una forma mucho más profunda de coincidencia de puntos que el simple ajuste de valores de salida.[37]
Regresión Simbólica Basada en Transformers (NSR)
Inspirado por el éxito de los modelos de lenguaje, el campo de la Regresión Simbólica Neuronal (NSR) trata el descubrimiento de ecuaciones como una tarea de traducción de "secuencia a secuencia".[1, 38] Estos modelos, como TPSR o SymbolicChat, son pre-entrenados en millones de ecuaciones sintácticas para aprender la "gramática" de las leyes físicas.[11, 38]
Lo fascinante de estos modelos es que pueden integrar retroalimentación de verificación de ecuaciones no diferenciable durante el proceso de generación.[38] Por ejemplo, se pueden utilizar técnicas de aprendizaje por refuerzo para recompensar al modelo cuando genera ecuaciones que maximizan el conteo de puntos dentro de una tolerancia (Accτ​), permitiendo que el conocimiento previo del LLM sobre la estructura de las fórmulas se combine con la necesidad de precisión numérica en los puntos observados.[11, 38]
Conclusiones y Recomendaciones Técnicas
La regresión simbólica ha madurado desde ser una extensión de los algoritmos genéticos hasta convertirse en una disciplina sofisticada de descubrimiento de conocimiento. Para los profesionales que buscan alejarse del error cuadrático medio y priorizar modelos que capturen la esencia de sus datos, se pueden extraer las siguientes conclusiones fundamentales:
En primer lugar, la bibliografía clásica de John R. Koza sigue siendo indispensable para comprender la mecánica del árbol de sintaxis y los operadores genéticos, pero debe complementarse con literatura moderna sobre optimización multiobjetivo y parsimonia.[8, 15, 17] Para una base sólida en español, el texto editado por Coello Coello proporciona el rigor académico necesario para entender los mecanismos de selección avanzada.[17]
En segundo lugar, para priorizar la coincidencia de puntos, la técnica más robusta disponible actualmente es la selección ϵ-Lexicase (EPLEX).[12, 27] Al evaluar el desempeño en cada punto de datos de forma independiente y permitir la supervivencia de especialistas, EPLEX evita las trampas de los mínimos locales del MSE y permite que el algoritmo descubra la estructura correcta incluso en conjuntos de datos ruidosos o incompletos.[12, 26]
Finalmente, el uso de funciones de pérdida alternativas, como la pérdida epsilon-insensible, ofrece una vía directa para mejorar la robustez.[21, 29] Al definir un margen de error aceptable, el investigador comunica al algoritmo que la precisión extrema en los residuos es menos importante que el descubrimiento de la forma funcional general. Herramientas modernas como PySR facilitan enormemente esta personalización, permitiendo integrar estas funciones de pérdida y restricciones físicas directamente en el núcleo del motor evolutivo.[31]
La regresión simbólica no es simplemente una técnica de ajuste de curvas; es una búsqueda de la verdad matemática en los datos. Al adoptar métricas basadas en aciertos y mecanismos de selección que valoran la especialización local, los científicos y científicos de datos pueden obtener modelos que no solo son precisos, sino que también cuentan una historia coherente y comprensible sobre el mundo.
--------------------------------------------------------------------------------

    Parsing the Language of Expression: Enhancing Symbolic Regression with Domain-Aware Symbolic Priors - arXiv, https://arxiv.org/html/2503.09592v1
    (PDF) Symbolic Regression - ResearchGate, https://www.researchgate.net/publication/382152886_Symbolic_Regression
    Prior-Guided Symbolic Regression: Towards Scientific Consistency in Equation Discovery, https://arxiv.org/html/2602.13021v1
    Contemporary Symbolic Regression Methods and their Relative Performance - PMC, https://pmc.ncbi.nlm.nih.gov/articles/PMC11074949/
    GSR: A Generalized Symbolic Regression Approach - Mitsubishi Electric Research Laboratories, https://www.merl.com/publications/docs/TR2023-002.pdf
    Have your spaghetti and eat it too: Evolutionary algorithmics and post-evolutionary analysis, https://www.researchgate.net/publication/220285940_Have_your_spaghetti_and_eat_it_too_Evolutionary_algorithmics_and_post-evolutionary_analysis
    Finetuning Large Language Model as an Effective Symbolic Regressor - arXiv, https://arxiv.org/html/2508.09897v2
    
    Epsilon-Lexicase Selection for Regression | Request PDF - ResearchGate, https://www.researchgate.net/publication/305685736_Epsilon-Lexicase_Selection_for_Regression
    
    
    
    Controlling overfitting in symbolic regression based on a bias/variance error decomposition - SciSpace, https://scispace.com/pdf/controlling-overfitting-in-symbolic-regression-based-on-a-hry49hibkj.pdf
    
    Multi-View Symbolic Regression - arXiv.org, https://arxiv.org/pdf/2402.04298
    
    The Inefficiency of Genetic Programming for Symbolic Regression – Extended Version - arXiv.org, https://arxiv.org/html/2404.17292v1
    [PDF] Population Diversity Leads to Short Running Times of Lexicase Selection, https://www.semanticscholar.org/paper/Population-Diversity-Leads-to-Short-Running-Times-Helmuth-Lengler/036ab1a71e248f8659d2942301a1a4024e6e0ae3
    
    A Performance Analysis of Lexicase-Based and Traditional Selection Methods in GP for Symbolic Regression - arXiv.org, https://arxiv.org/html/2407.21632v2
    Down-Sampled Epsilon-Lexicase Selection for Real-World Symbolic Regression Problems - arXiv, https://arxiv.org/pdf/2302.04301
    
    For regression, what loss functions do people actually use besides MSE and MAE? - Reddit, https://www.reddit.com/r/MLQuestions/comments/1q18u5d/for_regression_what_loss_functions_do_people/
    MilesCranmer/PySR: High-Performance Symbolic ... - GitHub, https://github.com/MilesCranmer/PySR
    Interpretable Machine Learning for Science with PySR and ... - arXiv, https://arxiv.org/pdf/2305.01582
    Introduction to GP — gplearn 0.4.3 documentation, https://gplearn.readthedocs.io/en/stable/intro.html
    API reference Symbolic Regressor - gplearn's documentation! - Read the Docs, https://gplearn.readthedocs.io/en/stable/reference.html
    Call for Action: Towards the Next Generation of Symbolic Regression Benchmark - arXiv.org, https://arxiv.org/html/2505.03977v1
    parfam – (neural guided) symbolic regression - arXiv.org, https://arxiv.org/pdf/2310.05537
    Taylor Genetic Programming for Symbolic Regression, https://minds.wisconsin.edu/bitstream/handle/1793/90504/3512290.3528757.pdf?sequence=1&isAllowed=y
    Transformer-based Planning for Symbolic Regression - Chandan Reddy, https://creddy.net/papers/NeurIPS23a.pdf