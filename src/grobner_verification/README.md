# Verificación con Bases de Gröbner

Herramienta **independiente** del pipeline principal para verificar algebraicamente
que las expresiones descubiertas por regresión simbólica son raíces válidas de la
ecuación original.

## Uso

```bash
python verify.py <directorio_resultados>
```

### Ejemplo

```bash
python verify.py ../outputs_analytical/quadratic_test_20260213_152345
```

## Métodos de verificación

1. **Algebraica directa**: Sustituye x = g(params) en F(x) y simplifica.
2. **Bases de Gröbner**: Para expresiones con radicales (sqrt), introduce variables
   auxiliares s² = h(params) y reduce F(g) módulo el ideal generado.
3. **Numérica**: Evalúa en puntos aleatorios como fallback.

## Teoría

Para una ecuación polinómica F(x, a, b, c) = 0 y candidata x = g(a, b, c):

- Si g es polinómica: verificar F(g) = 0 directamente
- Si g contiene √h: introducir s con s² = h, verificar F(g(s)) ≡ 0 mod (s² - h)
  usando bases de Gröbner en el anillo k[s, a, b, c]

## Nota

Este módulo **no** forma parte del pipeline automático. Es una herramienta
de comprobación manual para cuando se quiera verificar algebraicamente
que las soluciones encontradas son correctas.
