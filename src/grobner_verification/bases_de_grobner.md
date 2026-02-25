# Bases de Gröbner — Explicación formal con ejemplos paso a paso

## 1. Contexto: ¿Qué problema resuelven?

Cuando tenemos un sistema de ecuaciones polinómicas, queremos saber:
- ¿El sistema tiene solución?
- ¿Una expresión dada pertenece a las consecuencias del sistema?
- ¿Podemos simplificar o "resolver" el sistema eliminando variables?

Las Bases de Gröbner son una herramienta algebraica que responde estas preguntas de forma **algorítmica**. Son el equivalente polinomial multivariable de lo que el algoritmo de Euclides es para polinomios de una sola variable, o lo que la eliminación gaussiana es para sistemas lineales.

---

## 2. Conceptos previos

### 2.1 Anillo de polinomios

Trabajamos en $\mathbb{Q}[x_1, x_2, \ldots, x_n]$, que es el conjunto de todos los polinomios en las variables $x_1, x_2, \ldots, x_n$ con coeficientes racionales.

Cada polinomio es una suma finita de **monomios**. Un monomio tiene la forma:

$$c \cdot x_1^{\alpha_1} x_2^{\alpha_2} \cdots x_n^{\alpha_n}$$

donde:
- $c \in \mathbb{Q}$ es el **coeficiente** (un número racional, como $3$, $-\frac{1}{2}$, etc.)
- $\alpha_i \in \mathbb{N}_0$ son los **exponentes** (enteros no negativos: $0, 1, 2, \ldots$)
- $x_1^{\alpha_1} x_2^{\alpha_2} \cdots x_n^{\alpha_n}$ es la **parte monomial** (sin el coeficiente)

**Ejemplo:** En $\mathbb{Q}[x, y]$, el polinomio $3x^2y - 2xy^2 + 5$ tiene tres monomios:
- $3 \cdot x^2 y^1$ (coeficiente $c = 3$, exponentes $\alpha_x = 2$, $\alpha_y = 1$)
- $-2 \cdot x^1 y^2$ (coeficiente $c = -2$, exponentes $\alpha_x = 1$, $\alpha_y = 2$)
- $5 \cdot x^0 y^0$ (coeficiente $c = 5$, exponentes $\alpha_x = 0$, $\alpha_y = 0$)

### 2.2 Orden monomial

Para trabajar con polinomios multivariables necesitamos decidir cuál monomio es "más grande" que otro. Un **orden monomial** $\prec$ es una regla que ordena las partes monomiales de manera consistente.

Dado un monomio, representamos sus exponentes como una tupla $\alpha = (\alpha_1, \alpha_2, \ldots, \alpha_n)$. El **grado total** es $|\alpha| = \alpha_1 + \alpha_2 + \cdots + \alpha_n$.

Los órdenes más comunes son:

#### Orden lexicográfico (lex)

Se comparan los exponentes de izquierda a derecha (como en un diccionario). Dados dos monomios con exponentes $\alpha = (\alpha_1, \ldots, \alpha_n)$ y $\beta = (\beta_1, \ldots, \beta_n)$:

$$\alpha >_{\text{lex}} \beta \iff \text{la primera coordenada } i \text{ donde difieren cumple } \alpha_i > \beta_i$$

**Ejemplo** con variables $x > y > z$:
- $x^2y$ vs $xy^3$: exponentes $(2,1,0)$ vs $(1,3,0)$. Primera diferencia: $2 > 1$ → $x^2y >_{\text{lex}} xy^3$
- $xy^2$ vs $xy$: exponentes $(1,2,0)$ vs $(1,1,0)$. Primera diferencia (en $y$): $2 > 1$ → $xy^2 >_{\text{lex}} xy$

#### Orden grado-lexicográfico reverso (grevlex)

Primero compara el grado total. Si empatan, usa lexicográfico reverso (compara de derecha a izquierda, pero al revés):

$$\alpha >_{\text{grevlex}} \beta \iff |\alpha| > |\beta|, \text{ o } |\alpha| = |\beta| \text{ y la última coordenada donde difieren cumple } \alpha_i < \beta_i$$

**¿Por qué importa?** El orden determina cuál es el "término líder" de un polinomio, y eso controla cómo funciona el algoritmo de división.

### 2.3 Términos de un polinomio

Dado un polinomio $f$ y un orden monomial $\prec$ fijo, definimos:

- $\text{LT}(f)$ = **término líder**: el monomio con coeficiente más grande según el orden. Es el "término dominante" del polinomio.
- $\text{LM}(f)$ = **monomio líder**: la parte monomial de $\text{LT}(f)$ (sin el coeficiente).
- $\text{LC}(f)$ = **coeficiente líder**: el coeficiente de $\text{LT}(f)$.

**Ejemplo:** Sea $f = 3x^2y + 2xy^2 - y^3 + 1$ con orden lex ($x > y$):
- Los exponentes son: $(2,1), (1,2), (0,3), (0,0)$
- En lex, el mayor es $(2,1)$ → $\text{LT}(f) = 3x^2y$
- $\text{LM}(f) = x^2y$
- $\text{LC}(f) = 3$

### 2.4 Ideal

Un **ideal** $I$ en $\mathbb{Q}[x_1, \ldots, x_n]$ es un conjunto de polinomios con dos propiedades:
1. Si $f, g \in I$, entonces $f + g \in I$ (cerrado bajo suma)
2. Si $f \in I$ y $h$ es cualquier polinomio, entonces $h \cdot f \in I$ (cerrado bajo multiplicación por cualquier polinomio)

El ideal **generado** por los polinomios $f_1, f_2, \ldots, f_m$ se escribe:

$$I = \langle f_1, f_2, \ldots, f_m \rangle = \left\{ \sum_{i=1}^{m} h_i \cdot f_i \ : \ h_i \in \mathbb{Q}[x_1, \ldots, x_n] \right\}$$

donde:
- $f_1, \ldots, f_m$ son los **generadores** del ideal
- $h_1, \ldots, h_m$ son polinomios **arbitrarios** (los "coeficientes" de la combinación)
- Cada elemento de $I$ es una combinación de los generadores multiplicados por polinomios cualesquiera

**Intuición:** El ideal $\langle f_1, \ldots, f_m \rangle$ representa todas las "consecuencias algebraicas" del sistema $f_1 = 0, f_2 = 0, \ldots, f_m = 0$. Si $g \in I$, entonces $g = 0$ en cualquier solución del sistema.

**Ejemplo:** $I = \langle x^2 - 1, x - 1 \rangle$ en $\mathbb{Q}[x]$.
- $x^2 - 1 = (x+1)(x-1) \in I$ ✓
- $x + 1 = \frac{x^2 - 1}{x - 1} = 1 \cdot (x^2 - 1) + (-1)(x^2 - x) $... En realidad, $(x^2-1) - x(x-1) = x^2 - 1 - x^2 + x = x - 1$, y $(x^2-1) - (x+1)(x-1) = 0$. Veámoslo más claro: $x + 1 = 1 \cdot (x^2 - 1) + (-x) \cdot (x - 1) = x^2 - 1 - x^2 + x = x - 1$... no, así no sale. Lo correcto: $x + 1 = 1 \cdot (x^2 - 1) - (x - 1)(x - 1) + \ldots$. Simplemente: como $x - 1 \in I$, cualquier múltiplo de $(x-1)$ está en $I$, y como $x^2 - 1 = (x-1)(x+1)$ también está en $I$, podemos obtener $x + 1 = \frac{x^2 - 1}{x - 1}$ que aunque no se pueda escribir trivialmente como combinación con coeficientes polinómicos, sí se puede: $(x+1) = 1 \cdot (x^2 - 1) + (1 - x) \cdot (x - 1) = x^2 - 1 + x - 1 - x^2 + x = 2x - 2$... Esto muestra que el cálculo manual de pertenencia a un ideal no es trivial. **Exactamente para esto sirven las bases de Gröbner**: para hacer este tipo de verificación de forma sistemática.

### 2.5 División de polinomios multivariable

En una variable, dividir $f$ entre $g$ da cociente $q$ y residuo $r$: $f = qg + r$ con $\deg(r) < \deg(g)$.

En varias variables, dividimos $f$ entre un **conjunto** de polinomios $F = \{f_1, \ldots, f_m\}$:

$$f = q_1 f_1 + q_2 f_2 + \cdots + q_m f_m + r$$

donde:
- $q_i$ son los cocientes (polinomios)
- $r$ es el **residuo** (lo que no se pudo dividir por ningún $f_i$)

**Algoritmo de división multivariable:**

```
Entrada: f (polinomio a dividir), F = (f₁, ..., fₘ) (divisores)
Salida: q₁, ..., qₘ (cocientes), r (residuo)

r ← 0
p ← f
Mientras p ≠ 0:
    dividió ← False
    Para i = 1, ..., m:
        Si LT(fᵢ) divide a LT(p):
            qᵢ ← qᵢ + LT(p)/LT(fᵢ)
            p ← p - (LT(p)/LT(fᵢ)) · fᵢ
            dividió ← True
            Salir del For (volver al While)
    Si no dividió:
        r ← r + LT(p)
        p ← p - LT(p)
Retornar q₁, ..., qₘ, r
```

**Problema clave:** A diferencia de una variable, el residuo $r$ **depende del orden** en que listamos los $f_i$. Mismos generadores, diferente orden → diferente residuo. Esto hace que la pertenencia a un ideal no se pueda determinar solo con división ordinaria.

---

## 3. Definición formal de Base de Gröbner

### 3.1 Ideal de términos líderes

Dado un ideal $I$, definimos el **ideal de términos líderes**:

$$\text{LT}(I) = \langle \text{LT}(f) : f \in I, f \neq 0 \rangle$$

Este es el ideal generado por los términos líderes de **todos** los polinomios en $I$ (no solo de los generadores).

### 3.2 Definición

Un conjunto finito $G = \{g_1, \ldots, g_t\} \subset I$ es una **Base de Gröbner** del ideal $I$ si:

$$\langle \text{LT}(g_1), \text{LT}(g_2), \ldots, \text{LT}(g_t) \rangle = \text{LT}(I)$$

En palabras: los términos líderes de los elementos de $G$ generan **todos** los posibles términos líderes de elementos de $I$.

### 3.3 ¿Por qué importa?

**Propiedad fundamental:** Si $G$ es una Base de Gröbner de $I$, entonces al dividir cualquier polinomio $f$ entre $G$, el residuo $r$ es **único** (no depende del orden de los $g_i$). Además:

$$f \in I \iff r = 0$$

Esto convierte la pregunta "¿pertenece $f$ al ideal $I$?" en un cálculo mecánico: dividir y ver si el residuo es cero.

---

## 4. Algoritmo de Buchberger

### 4.1 S-polinomio

El ingrediente clave es el **S-polinomio** (de "syzygy"). Dados dos polinomios $f$ y $g$, se define:

$$S(f, g) = \frac{x^\gamma}{\text{LT}(f)} \cdot f - \frac{x^\gamma}{\text{LT}(g)} \cdot g$$

donde:
- $x^\gamma = \text{lcm}(\text{LM}(f), \text{LM}(g))$ es el **mínimo común múltiplo** de los monomios líderes
- $\text{lcm}(x^{\alpha}, x^{\beta}) = x^{(\max(\alpha_1, \beta_1), \ldots, \max(\alpha_n, \beta_n))}$
- $\frac{x^\gamma}{\text{LT}(f)}$ multiplica a $f$ para "elevar" su término líder al mcm
- La resta cancela los términos líderes, revelando posibles nuevas relaciones

**Intuición:** El S-polinomio prueba si los términos líderes de $f$ y $g$ pueden producir cancelaciones que generen nuevos polinomios que deberían estar en la base.

### 4.2 Algoritmo

```
Entrada: F = {f₁, ..., fₘ} (generadores del ideal I)
Salida: G (Base de Gröbner de I)

G ← F
Repetir:
    G' ← G
    Para cada par {p, q} ⊂ G' con p ≠ q:
        Calcular S(p, q)
        Dividir S(p, q) entre G' → residuo r
        Si r ≠ 0:
            G ← G ∪ {r}
Hasta que G = G'
Retornar G
```

En cada paso:
1. Tomamos un par de polinomios de $G$
2. Calculamos su S-polinomio
3. Lo dividimos entre $G$ actual
4. Si el residuo no es cero, lo agregamos a $G$ (es un nuevo generador necesario)
5. Repetimos hasta que no aparezcan residuos nuevos

**El algoritmo siempre termina** (esto se demuestra por el Lema de Dickson: toda cadena ascendente de ideales monomiales se estabiliza).

---

## 5. Ejemplo 1 — Sistema lineal simple

### Problema

Verificar si $f = x + y$ pertenece al ideal $I = \langle f_1, f_2 \rangle$ donde:

$$f_1 = x + y + z, \quad f_2 = x + y - z$$

Usamos orden **lex** con $x > y > z$.

### Paso 1: Términos líderes

| Polinomio | $\text{LT}$ | $\text{LM}$ | $\text{LC}$ |
|-----------|-------------|-------------|-------------|
| $f_1 = x + y + z$ | $x$ | $x$ | $1$ |
| $f_2 = x + y - z$ | $x$ | $x$ | $1$ |

### Paso 2: S-polinomio

$$\text{LM}(f_1) = x, \quad \text{LM}(f_2) = x$$
$$x^\gamma = \text{lcm}(x, x) = x$$

$$S(f_1, f_2) = \frac{x}{x} \cdot f_1 - \frac{x}{x} \cdot f_2 = f_1 - f_2$$

$$= (x + y + z) - (x + y - z) = 2z$$

### Paso 3: Dividir $S(f_1, f_2) = 2z$ entre $G = \{f_1, f_2\}$

- $\text{LT}(2z) = 2z$
- ¿$\text{LT}(f_1) = x$ divide a $2z$? No ($x \nmid z$)
- ¿$\text{LT}(f_2) = x$ divide a $2z$? No
- Ninguno divide → residuo $r = 2z \neq 0$

### Paso 4: Agregar al conjunto

$$G = \{f_1, f_2, g_3\} = \{x + y + z, \; x + y - z, \; 2z\}$$

### Paso 5: Nuevos S-polinomios

**$S(f_1, g_3)$:**
- $\text{LM}(f_1) = x$, $\text{LM}(g_3) = z$, $\text{lcm}(x, z) = xz$

$$S(f_1, g_3) = \frac{xz}{x} \cdot f_1 - \frac{xz}{2z} \cdot g_3 = z(x + y + z) - \frac{x}{2}(2z)$$

$$= xz + yz + z^2 - xz = yz + z^2$$

Dividimos $yz + z^2$ entre $G = \{f_1, f_2, g_3\}$:
- $\text{LT}(yz + z^2) = yz$. ¿$x$ divide a $yz$? No. ¿$x$ divide? No. ¿$2z$ divide a $yz$? Sí: $yz / z = y$.

$$yz + z^2 - y \cdot \frac{g_3}{2} = yz + z^2 - y \cdot z = z^2$$

- $\text{LT}(z^2) = z^2$. ¿$2z$ divide a $z^2$? Sí: $z^2/z = z$.

$$z^2 - z \cdot \frac{g_3}{2} = z^2 - z^2 = 0$$

Residuo $= 0$ ✓ (no hay que agregar nada)

**$S(f_2, g_3)$:** Por simetría similar, también da residuo $0$.

### Paso 6: No hay más residuos nuevos

$$G = \{x + y + z, \; x + y - z, \; 2z\}$$

Esta es la **Base de Gröbner** de $I$. Podemos simplificarla. Notemos que $g_3 = 2z$ implica $z = 0$ (en las soluciones del ideal). Sustituyendo en $f_1$: $x + y + 0 = x + y$. Entonces una base reducida sería $\{x + y, \; z\}$.

### Paso 7: ¿Pertenece $f = x + y$ a $I$?

Dividimos $f = x + y$ entre $G = \{x + y + z, \; x + y - z, \; 2z\}$:

- $\text{LT}(x + y) = x$. ¿$\text{LT}(f_1) = x$ divide a $x$? Sí.

$$(x + y) - 1 \cdot (x + y + z) = -z$$

- $\text{LT}(-z) = -z$. ¿$2z$ divide a $-z$? Sí: $-z / 2z = -1/2$.

$$-z - (-\tfrac{1}{2}) \cdot 2z = -z + z = 0$$

**Residuo $= 0$** → $f = x + y \in I$ ✓

Esto significa que $x + y = 0$ es una consecuencia del sistema $\{x+y+z=0, \; x+y-z=0\}$. Y tiene sentido: restando las ecuaciones obtenemos $2z = 0$, luego $z = 0$, luego $x + y = 0$.

---

## 6. Ejemplo 2 — Verificar una raíz cuadrática

### Problema

Tenemos la ecuación $f = ax^2 + bx + c = 0$ y queremos verificar que la candidata:

$$x = \frac{-b + \sqrt{b^2 - 4ac}}{2a}$$

es efectivamente una raíz. Este es exactamente el tipo de verificación que hace `verify.py`.

### Paso 1: Eliminar la raíz cuadrada

Introducimos una variable auxiliar $s$ que reemplaza a $\sqrt{b^2 - 4ac}$:

$$s = \sqrt{b^2 - 4ac} \quad \Longleftrightarrow \quad s^2 = b^2 - 4ac \quad \Longleftrightarrow \quad s^2 - b^2 + 4ac = 0$$

La candidata sin radical queda: $x = \frac{-b + s}{2a}$

### Paso 2: Sustituir en la ecuación

Reemplazamos $x = \frac{-b + s}{2a}$ en $f = ax^2 + bx + c$:

$$f\!\left(\frac{-b+s}{2a}\right) = a \cdot \frac{(-b+s)^2}{4a^2} + b \cdot \frac{-b+s}{2a} + c$$

Expandimos $(-b + s)^2 = b^2 - 2bs + s^2$:

$$= \frac{b^2 - 2bs + s^2}{4a} + \frac{-b^2 + bs}{2a} + c$$

Multiplicamos todo por $4a$ (el denominador común) para obtener un **polinomio puro** (sin fracciones):

$$4a \cdot f(g) = (b^2 - 2bs + s^2) + 2(-b^2 + bs) + 4ac$$

$$= b^2 - 2bs + s^2 - 2b^2 + 2bs + 4ac$$

$$= s^2 - b^2 + 4ac$$

### Paso 3: El ideal y la reducción de Gröbner

Tenemos:
- **Polinomio a reducir:** $P = s^2 - b^2 + 4ac$ (el numerador de $f(g)$)
- **Relación auxiliar:** $R = s^2 - b^2 + 4ac$ (la definición de $s$)

¡Observá que $P$ y $R$ son **idénticos**! Esto significa que:

$$P = 1 \cdot R + 0$$

El residuo de dividir $P$ entre $\{R\}$ es $\mathbf{0}$.

### Paso 4: Interpretar

Que el residuo sea $0$ significa que $P \in \langle R \rangle$, es decir:

$$s^2 - b^2 + 4ac \equiv 0 \pmod{s^2 = b^2 - 4ac}$$

Como $P$ era $4a \cdot f(g)$ y $a \neq 0$ (estamos en una cuadrática), entonces $f(g) = 0$.

**Conclusión:** La fórmula cuadrática es una raíz válida ✓

> **Nota:** En la implementación de `verify.py`, este caso es tan directo que la función detecta que el numerador es idéntico a la relación auxiliar y reporta "Numerador directamente 0" sin necesidad de calcular la base de Gröbner completa.

---

## 7. Ejemplo 3 — Base de Gröbner no trivial

### Problema

Encontrar la Base de Gröbner de $I = \langle f_1, f_2 \rangle$ donde:

$$f_1 = x^2 + y - 1, \quad f_2 = x + y^2 - 1$$

Usamos orden **lex** con $x > y$. Este ejemplo muestra cómo las bases de Gröbner **eliminan variables**, similar a la eliminación gaussiana.

### Paso 1: Términos líderes

| Polinomio | $\text{LT}$ (lex, $x > y$) | $\text{LM}$ | $\text{LC}$ |
|-----------|---------------------------|-------------|-------------|
| $f_1 = x^2 + y - 1$ | $x^2$ | $x^2$ | $1$ |
| $f_2 = x + y^2 - 1$ | $x$ | $x$ | $1$ |

### Paso 2: S-polinomio $S(f_1, f_2)$

$$\text{LM}(f_1) = x^2, \quad \text{LM}(f_2) = x$$
$$x^\gamma = \text{lcm}(x^2, x) = x^2$$

$$S(f_1, f_2) = \frac{x^2}{x^2} \cdot f_1 - \frac{x^2}{x} \cdot f_2 = f_1 - x \cdot f_2$$

$$= (x^2 + y - 1) - x(x + y^2 - 1) = x^2 + y - 1 - x^2 - xy^2 + x$$

$$= -xy^2 + x + y - 1$$

### Paso 3: Dividir $-xy^2 + x + y - 1$ entre $G = \{f_1, f_2\}$

Llamemos $p = -xy^2 + x + y - 1$.

- $\text{LT}(p) = -xy^2$. ¿$x^2$ divide a $xy^2$? No ($x$ en $xy^2$ tiene exponente 1, pero $x^2$ necesita 2). ¿$x$ divide a $xy^2$? Sí: $xy^2 / x = y^2$.

$$p - (-y^2) \cdot f_2 = (-xy^2 + x + y - 1) + y^2(x + y^2 - 1)$$

$$= -xy^2 + x + y - 1 + xy^2 + y^4 - y^2 = y^4 - y^2 + y + x - 1$$

Ahora tenemos $p' = y^4 - y^2 + y + x - 1$.

- $\text{LT}(p') = x$ (en lex con $x > y$, el término $x$ tiene monomio $x^1y^0$ que es mayor que $y^4 = x^0y^4$). ¿$x^2$ divide a $x$? No. ¿$x$ divide a $x$? Sí: $x/x = 1$.

$$p' - 1 \cdot f_2 = (y^4 - y^2 + y + x - 1) - (x + y^2 - 1) = y^4 - 2y^2 + y$$

Ahora tenemos $p'' = y^4 - 2y^2 + y$.

- $\text{LT}(p'') = y^4$. ¿$x^2$ divide a $y^4$? No. ¿$x$ divide a $y^4$? No.
- Ningún LT divide → pasamos $y^4$ al residuo. $r = y^4$. Continuamos con $p''' = -2y^2 + y$.
- $\text{LT}(-2y^2 + y) = -2y^2$. Ninguno divide → al residuo. $r = y^4 - 2y^2$. Queda $p'''' = y$.
- $\text{LT}(y) = y$. Ninguno divide → al residuo. $r = y^4 - 2y^2 + y$. Queda $0$.

**Residuo** $r = y^4 - 2y^2 + y \neq 0$

### Paso 4: Agregar nuevo generador

$$g_3 = y^4 - 2y^2 + y$$
$$G = \{x^2 + y - 1, \; x + y^2 - 1, \; y^4 - 2y^2 + y\}$$

Observá algo crucial: **$g_3$ solo tiene la variable $y$**. La variable $x$ fue **eliminada**. Esto es análogo a la eliminación gaussiana.

### Paso 5: Nuevos S-polinomios

Ahora necesitamos los S-polinomios de los nuevos pares.

**$S(f_2, g_3)$:**
- $\text{LM}(f_2) = x$, $\text{LM}(g_3) = y^4$, $\text{lcm}(x, y^4) = xy^4$

$$S(f_2, g_3) = y^4 \cdot f_2 - x \cdot g_3 = y^4(x + y^2 - 1) - x(y^4 - 2y^2 + y)$$

$$= xy^4 + y^6 - y^4 - xy^4 + 2xy^2 - xy = y^6 - y^4 + 2xy^2 - xy$$

Dividiendo entre $G$: el término $2xy^2$ se reduce con $f_2$ (que tiene LT $= x$), y tras varias reducciones, el residuo final resulta $0$.

**$S(f_1, g_3)$:** De manera similar, el residuo es $0$.

### Paso 6: No hay más residuos nuevos → Base de Gröbner encontrada

$$G = \{x^2 + y - 1, \quad x + y^2 - 1, \quad y^4 - 2y^2 + y\}$$

### Paso 7: Interpretar la base

La base tiene una estructura reveladora:

1. $y^4 - 2y^2 + y = 0$ → ecuación **solo en $y$**: $y(y^3 - 2y + 1) = 0$, que factoriza como $y(y-1)(y^2+y-1) = 0$, dando $y = 0$, $y = 1$, $y = \frac{-1 \pm \sqrt{5}}{2}$.
2. $x + y^2 - 1 = 0$ → una vez conocido $y$, obtenemos $x = 1 - y^2$.
3. $x^2 + y - 1 = 0$ → relación redundante (ya contenida en las otras dos).

La base de Gröbner **triangularizó** el sistema: primero resolvemos $y$ solo, luego despejamos $x$ en función de $y$. Esto es exactamente lo que hace la eliminación gaussiana, pero para sistemas **no lineales**.

### Soluciones

| $y$ | $x = 1 - y^2$ |
|-----|----------------|
| $0$ | $1$ |
| $1$ | $0$ |
| $\frac{-1+\sqrt{5}}{2}$ | $\frac{-1+\sqrt{5}}{2}$ |
| $\frac{-1-\sqrt{5}}{2}$ | $\frac{-1-\sqrt{5}}{2}$ |

---

## 8. Conexión con tu pipeline

En `verify.py`, las bases de Gröbner se usan para verificar que las expresiones que PySR descubrió son raíces **exactas** de la ecuación original. El flujo es:

1. PySR descubre (por ejemplo) `(-x1 + safe_sqrt(x1**2 - 4*x0*x2)) / (2*x0)` para $ax^2 + bx + c = 0$
2. Se racionaliza: constantes como $-4.0000005$ pasan a $-4$
3. Se introduce variable auxiliar: $s^2 = b^2 - 4ac$
4. Se sustituye en $F$ y se multiplica por denominadores → polinomio $P$
5. Se calcula la base de Gröbner de la relación $\{s^2 - b^2 + 4ac\}$ y se reduce $P$ módulo esa base
6. Si el residuo es $0$: la expresión es una raíz algebraicamente exacta ✓

Esto da una **prueba formal** de que la expresión descubierta numéricamente es correcta, no solo una buena aproximación.
