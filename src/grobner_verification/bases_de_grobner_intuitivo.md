# Bases de Gröbner — Explicación intuitiva con ejemplos

## La idea en una frase

Las bases de Gröbner son una forma de **simplificar sistemas de ecuaciones polinómicas** hasta que sea obvio qué se puede deducir de ellos. Es como la eliminación gaussiana que usás en álgebra lineal, pero funciona también cuando las ecuaciones **no son lineales**.

---

## Empecemos con lo que ya sabés: eliminación gaussiana

Si tenés el sistema lineal:

$$x + y + z = 0$$
$$x + y - z = 0$$

Lo resolvés restando una ecuación de la otra:

$$(x + y + z) - (x + y - z) = 0 \implies 2z = 0 \implies z = 0$$

Y sustituyendo atrás: $x + y = 0$.

Eso que acabás de hacer — combinar ecuaciones para eliminar variables y obtener ecuaciones más simples — es **exactamente** lo que hacen las bases de Gröbner, pero de forma general para cualquier sistema polinómico.

---

## Ejemplo 1: Verificar una consecuencia de un sistema

### El problema

Tenemos dos ecuaciones:

$$f_1: \quad x + y + z = 0$$
$$f_2: \quad x + y - z = 0$$

Pregunta: ¿es $x + y = 0$ una consecuencia de este sistema? Es decir, ¿en cualquier solución del sistema se cumple que $x + y = 0$?

### La intuición

Si podés obtener $x + y$ combinando $f_1$ y $f_2$ (sumando, restando, multiplicando por algo), entonces sí es consecuencia.

A ojo es fácil: restamos y obtenemos $2z = 0$, luego sustituimos y listo. Pero, ¿cómo lo haría un algoritmo que no tiene "intuición"?

### Lo que hace Gröbner (paso a paso)

**Paso 1 — Combinación canceladora.** El algoritmo toma $f_1$ y $f_2$ y calcula su "S-polinomio", que no es más que una resta diseñada para cancelar el término más grande:

$$S(f_1, f_2) = f_1 - f_2 = (x + y + z) - (x + y - z) = 2z$$

Los dos $x$ se cancelaron. Obtuvimos algo nuevo: $2z$.

**Paso 2 — ¿$2z$ se puede simplificar más?** El algoritmo intenta "dividir" $2z$ entre las ecuaciones que ya tiene ($f_1$ y $f_2$). Pero $f_1$ empieza con $x$ y $f_2$ empieza con $x$, y $2z$ no tiene $x$, así que **no se puede simplificar**. Entonces $2z$ es información nueva y la agregamos al sistema:

$$\text{Sistema ampliado:} \quad \{x + y + z, \quad x + y - z, \quad 2z\}$$

**Paso 3 — ¿Hay más combinaciones nuevas?** El algoritmo repite: toma nuevos pares, calcula S-polinomios, divide. Todas las combinaciones nuevas dan residuo 0. No hay más información que extraer.

**Resultado:** La base de Gröbner es $\{x + y + z, \; x + y - z, \; 2z\}$.

### Ahora verificamos la pregunta

¿$x + y$ es consecuencia del sistema? Dividimos $x + y$ entre la base:

1. $x + y$ empieza con $x$. La ecuación $f_1 = x + y + z$ también empieza con $x$. Dividimos: $(x + y) - 1 \cdot (x + y + z) = -z$
2. $-z$ empieza con $z$. La ecuación $2z$ también empieza con $z$. Dividimos: $-z - (-\frac{1}{2}) \cdot 2z = 0$

**Residuo = 0** → Sí, $x + y = 0$ es consecuencia del sistema ✓

### ¿Qué pasó realmente?

La base de Gröbner descubrió que el sistema original es equivalente a decir "$z = 0$ y $x + y = 0$". Al dividir $x + y$ entre la base, el residuo 0 confirma que esa información ya estaba contenida en el sistema.

---

## Ejemplo 2: Verificar la fórmula cuadrática

### El problema

Tenemos la ecuación cuadrática $ax^2 + bx + c = 0$ y alguien nos dice que una raíz es:

$$x = \frac{-b + \sqrt{b^2 - 4ac}}{2a}$$

¿Cómo verificamos que esto es correcto, **algebraicamente**, sin sustituir números?

### El obstáculo: la raíz cuadrada

La raíz cuadrada $\sqrt{b^2 - 4ac}$ no es un polinomio. Las bases de Gröbner solo trabajan con polinomios. Entonces hacemos un truco: **le ponemos nombre** a la raíz cuadrada.

Definimos $s = \sqrt{b^2 - 4ac}$. Esto es lo mismo que decir:

$$s^2 = b^2 - 4ac$$

o equivalentemente:

$$s^2 - b^2 + 4ac = 0 \quad \text{(llamémosla la "regla de } s \text{")}$$

Ahora la candidata sin raíz cuadrada es: $x = \frac{-b + s}{2a}$

### Sustituir en la ecuación

Reemplazamos $x = \frac{-b + s}{2a}$ en $ax^2 + bx + c$:

$$a \cdot \frac{(-b+s)^2}{4a^2} + b \cdot \frac{-b+s}{2a} + c$$

Expandimos $(-b + s)^2 = b^2 - 2bs + s^2$:

$$= \frac{b^2 - 2bs + s^2}{4a} + \frac{-b^2 + bs}{2a} + c$$

Para eliminar los denominadores, multiplicamos todo por $4a$:

$$= (b^2 - 2bs + s^2) + 2(-b^2 + bs) + 4ac$$

$$= b^2 - 2bs + s^2 - 2b^2 + 2bs + 4ac$$

$$= s^2 - b^2 + 4ac$$

### El momento clave

Obtuvimos que $4a \cdot f(x) = s^2 - b^2 + 4ac$.

Pero la "regla de $s$" dice que $s^2 - b^2 + 4ac = 0$.

¡Son exactamente lo mismo! Entonces:

$$4a \cdot f(x) = 0 \quad \implies \quad f(x) = 0 \quad \text{(porque } a \neq 0\text{)}$$

### ¿Dónde entran las bases de Gröbner?

Lo que hicimos a mano fue: dividir el resultado entre la regla de $s$ y ver que el residuo es 0. Eso ES una reducción de Gröbner:

- **Polinomio a reducir:** $P = s^2 - b^2 + 4ac$
- **Base (las reglas):** $\{s^2 - b^2 + 4ac\}$
- **Residuo:** $P - 1 \cdot (s^2 - b^2 + 4ac) = 0$ ✓

En este caso la base de Gröbner tiene un solo elemento y la reducción es trivial. Pero el mecanismo es el mismo que para casos complicados: reducir módulo las relaciones y ver si queda 0.

### ¿Y qué pasa con `safe_sqrt`?

En tu pipeline, PySR usa `safe_sqrt(h) = sqrt(|h|)` en vez de `sqrt(h)`. El valor absoluto $|h|$ significa que el argumento real podría ser $h$ o $-h$. Por eso `verify.py` prueba **ambas variantes de signo**: si con $s^2 = h$ no da 0, prueba con $s^2 = -h$. Alguna de las dos tiene que funcionar si la expresión es correcta.

---

## Ejemplo 3: Eliminar variables en un sistema no lineal

### El problema

Tenemos el sistema:

$$f_1: \quad x^2 + y = 1$$
$$f_2: \quad x + y^2 = 1$$

Dos ecuaciones, dos incógnitas, pero **no son lineales**. No podés usar eliminación gaussiana directamente. ¿Cómo encontramos las soluciones?

### Lo que hace Gröbner

**Paso 1 — S-polinomio.** El algoritmo mira los términos más grandes: $f_1$ empieza con $x^2$ y $f_2$ empieza con $x$. Calcula la combinación que cancela esos términos:

$$S(f_1, f_2) = f_1 - x \cdot f_2 = (x^2 + y - 1) - x(x + y^2 - 1)$$

$$= x^2 + y - 1 - x^2 - xy^2 + x = -xy^2 + x + y - 1$$

**Paso 2 — Dividir entre el sistema actual.** Tomamos $-xy^2 + x + y - 1$ e intentamos simplificarlo usando $f_1$ y $f_2$:

- El término $-xy^2$ tiene una $x$, y $f_2$ empieza con $x$, así que podemos usar $f_2$ para eliminarla. Hacemos la división y luego seguimos reduciendo.
- Tras varias reducciones, llegamos a algo que ya no se puede simplificar más:

$$g_3 = y^4 - 2y^2 + y$$

Este residuo no es 0, así que es **información nueva**. Lo agregamos.

**Paso 3 — Repetir.** El algoritmo sigue tomando pares y calculando S-polinomios. Todos los nuevos dan residuo 0. No hay más información.

**Base de Gröbner final:**

$$G = \{x^2 + y - 1, \quad x + y^2 - 1, \quad y^4 - 2y^2 + y\}$$

### ¿Qué ganamos?

Mirá la tercera ecuación: $y^4 - 2y^2 + y = 0$. **Solo tiene $y$**. La variable $x$ desapareció.

El algoritmo eliminó $x$ automáticamente, igual que la eliminación gaussiana elimina variables en sistemas lineales. Ahora podemos resolver:

$$y(y^3 - 2y + 1) = 0$$
$$y(y - 1)(y^2 + y - 1) = 0$$

Las soluciones para $y$ son:

$$y = 0, \quad y = 1, \quad y = \frac{-1 + \sqrt{5}}{2}, \quad y = \frac{-1 - \sqrt{5}}{2}$$

Y para cada $y$, la segunda ecuación de la base nos da $x$:

$$x + y^2 - 1 = 0 \implies x = 1 - y^2$$

| $y$ | $x = 1 - y^2$ |
|-----|----------------|
| $0$ | $1$ |
| $1$ | $0$ |
| $\frac{-1+\sqrt{5}}{2} \approx 0.618$ | $\frac{-1+\sqrt{5}}{2} \approx 0.618$ |
| $\frac{-1-\sqrt{5}}{2} \approx -1.618$ | $\frac{-1-\sqrt{5}}{2} \approx -1.618$ |

Dos de las soluciones tienen $x = y$ (son los puntos donde las curvas se cruzan sobre la diagonal). Todo esto salió automáticamente del algoritmo.

### La analogía con eliminación gaussiana

| Eliminación gaussiana | Bases de Gröbner |
|----------------------|------------------|
| Sistemas lineales | Sistemas polinómicos (cualquier grado) |
| Resta filas para eliminar variables | Calcula S-polinomios para eliminar términos |
| Llega a forma escalonada | Llega a una base con ecuaciones en menos variables |
| La última fila tiene 1 variable | El último polinomio de la base tiene las menos variables |
| Sustitución hacia atrás | Resolver la ecuación simple y sustituir atrás |

---

## Resumen: ¿Qué hacen las bases de Gröbner?

1. **Toman** un conjunto de ecuaciones polinómicas
2. **Combinan** las ecuaciones (S-polinomios) para encontrar consecuencias nuevas
3. **Simplifican** cada consecuencia dividiéndola entre lo que ya tienen
4. **Agregan** lo que no se simplifica a 0 (porque es información nueva)
5. **Repiten** hasta que no hay más información nueva
6. El resultado es un sistema equivalente al original pero **más fácil de trabajar**

Y la propiedad mágica: si querés saber si algo es consecuencia del sistema, dividís entre la base de Gröbner. **Si el residuo es 0, sí es consecuencia. Si no es 0, no lo es.** Sin ambigüedad.

---

## ¿Para qué lo usás en tu tesis?

Tu pipeline:
1. **PySR descubre** una expresión candidata (ej: $\frac{-b + \sqrt{b^2 - 4ac}}{2a}$)
2. Querés **demostrar** que esa expresión es realmente una raíz de la ecuación original
3. Sustituís la candidata en la ecuación → obtenés un polinomio $P$
4. Reducís $P$ módulo las relaciones auxiliares (como $s^2 = b^2 - 4ac$) usando Gröbner
5. **Residuo 0** → la expresión es algebraicamente exacta, no solo una aproximación numérica

Es la diferencia entre decir "le probé 1000 puntos y funciona" (verificación numérica) y decir "es algebraicamente imposible que no funcione" (verificación con Gröbner).
