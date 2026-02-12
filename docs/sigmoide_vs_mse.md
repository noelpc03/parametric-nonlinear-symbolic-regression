# Por qué una pérdida sigmoidal favorece el “matcheo” de puntos (vs. Error Cuadrático Medio)

Este documento explica, con intuición y soporte matemático, por qué usar una pérdida basada en una sigmoide es un enfoque adecuado cuando el objetivo es “matchear” (cubrir) la mayor cantidad de puntos dentro de una tolerancia ε, en contraposición al clásico Error Cuadrático Medio (MSE).

## Objetivo del proyecto

En este trabajo buscamos, de manera iterativa, encontrar funciones simbólicas que pasen por la mayor cantidad de puntos posibles dentro de una tolerancia $\varepsilon$ y, una vez encontrados, retirar esos puntos y repetir el proceso. Es decir, nuestro objetivo real se parece al siguiente indicador tipo 0–1:

$$
\text{match}(r) = \begin{cases}
1, & \text{si } |r| \le \varepsilon, \\
0, & \text{si } |r| > \varepsilon,
\end{cases}
$$

donde $r = y - f(x)$ es el residual.

Este objetivo es discontinuo y no derivable. En optimización (y en búsqueda evolutiva), es beneficioso usar una función objetivo suave que aproxime a ese indicador y provea una señal de mejora continua.

## MSE no se alinea con “contar puntos dentro de ε”

El Error Cuadrático Medio (MSE) minimiza $\frac{1}{n} \sum_i (y_i - f(x_i))^2$. Esto persigue “promediar” errores pequeños en todos los puntos, en lugar de maximizar la cantidad de puntos dentro de un umbral. Consecuencias:

- Un solo outlier con residual grande domina el MSE, empujando la solución a “compensar” en vez de cubrir bien un grupo denso de puntos.
- MSE no distingue entre un punto con error 0.06 y otro con 0.6: ambos están fuera de $\varepsilon$, pero el segundo pesa 100× más; la métrica no premia acercarse al umbral para convertir “casi” en “sí”.
- Nuestro objetivo real es más cercano a “maximizar el conteo de puntos admitidos”, no a minimizar el error promedio global.

## Pérdida sigmoidal: un surrogate suave del indicador 0–1

Usamos la forma logística sobre el residual:

$$
\sigma_k(\varepsilon - |r|) = \frac{1}{1 + e^{-k\,(\varepsilon - |r|)}}.
$$

- Si $|r| \ll \varepsilon$ (muy dentro): $\sigma \approx 1$.
- Si $|r| \approx \varepsilon$ (en el borde): $\sigma \approx 0.5$.
- Si $|r| \gg \varepsilon$ (muy fuera): $\sigma \approx 0$.

En Python, promediamos esta “afinidad de match” y la convertimos en pérdida:

$$
\mathcal{L} \,=\, 1 - \frac{1}{n} \sum_{i=1}^n \sigma_k\big(\varepsilon - |r_i|\big).
$$

En Julia (PySR) definimos directamente la versión elemento a elemento a minimizar:

$$
\ell(r) \,=\, \frac{1}{1 + e^{-k\,(|r| - \varepsilon)}} \;=\; 1 - \sigma_k\big(\varepsilon - |r|\big),
$$

y PySR promedia $\ell(r_i)$ internamente.

### Interpretación

- Dentro de $\varepsilon$: la pérdida es baja y decrece cuanto más “dentro” esté el punto.
- Fuera de $\varepsilon$: la pérdida crece suavemente cuanto más lejos esté.
- En el límite $k\to\infty$, $\sigma$ aproxima una función escalón y recuperamos el comportamiento tipo 0–1.

## ¿Por qué este enfoque favorece “matchear” puntos?

- Señal suave y útil: cerca del umbral, una pequeña mejora del residual produce una mejora visible en la pérdida. Esto incentiva convertir “casi” en “sí”. Con MSE, esas pequeñas mejoras pueden quedar diluidas.
- Robustez a outliers: puntos muy lejanos no “secuestran” la optimización; su contribución se satura (no crece cuadráticamente como en MSE).
- Alineación con el objetivo: maximizar $\sigma$ (o minimizar $1-\sigma$) es un surrogate directo para “estar dentro de $\varepsilon$”.
- Mejor exploración evolutiva: las funciones que aciertan a un grupo de puntos reciben una ventaja clara; el algoritmo evolutivo puede conservar y recombinar estos “aciertos” en generaciones siguientes.

## Efecto de los hiperparámetros $(\varepsilon, k)$

- $\varepsilon$ (tolerancia): determina qué consideramos “admitido”. Debe reflejar la escala del ruido o tolerancia del problema. Si es demasiado pequeño, casi nada entra; si es muy grande, todo entra y se pierde selectividad.
- $k$ (pendiente): controla la “dureza” de la transición.
  - $k$ grande → transición más brusca (más cercano a 0–1). Puede dificultar la optimización si es excesivo.
  - $k$ pequeño → transición suave. Demasiado pequeño hace la señal poco informativa (todos los puntos cerca de 0.5).

Una regla práctica es empezar con un $k$ que haga que $\sigma(0) \approx 0.7$–$0.9$ y ajustar según el comportamiento.

## Ejemplos numéricos (con $\varepsilon=0.05$, $k=10$)

| Residual $|r|$ | Estado | $\ell(r)$ (PySR) | Interpretación |
|---:|:--:|---:|:--|
| 0.00 | ✅ dentro | $\approx 0.38$ | pérdida baja |
| 0.03 | ✅ dentro | $\approx 0.45$ | casi en borde |
| 0.05 | 🔸 borde  | $0.50$ | punto de inflexión |
| 0.10 | ❌ fuera  | $\approx 0.62$ | pérdida media–alta |
| 0.50 | ❌ fuera  | $\approx 0.99$ | pérdida casi máxima |

(Recordatorio: en Python reportamos $1 - \text{media}(\sigma)$; en PySR minimizamos directamente $\ell = 1-\sigma$.)

## Integración con PySR

- En Python definimos la cadena Julia a través de `get_julia_loss_function(epsilon, k)` y la pasamos como `elementwise_loss` a `PySRRegressor`.
- PySR (en Julia) evalúa millones de ecuaciones candidatas, calcula $\ell(r)$ por punto y minimiza el promedio.
- Nuestro bucle iterativo elimina los puntos ya cubiertos (con $|r| \le \varepsilon$) y repite la búsqueda sobre los restantes.

## Alternativas y notas

- Otras pérdidas robustas: Huber, Tukey, ramp loss. La logística es especialmente conveniente por su suavidad y control vía $k$.
- Parsimonia (penalización de complejidad) complementa esta idea: entre dos funciones con el mismo conteo efectivo, preferimos la más simple.

## Conclusión

La pérdida sigmoidal actúa como un **surrogate suave** del objetivo real “contar puntos dentro de $\varepsilon$”, proporcionando una señal de optimización informativa, robusta a outliers y bien alineada con la meta de cubrir el máximo de puntos. Por eso es un enfoque adecuado (y práctico) para guiar la regresión simbólica evolutiva en este proyecto.
