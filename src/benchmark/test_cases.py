"""
Catálogo de casos de prueba para el benchmark del pipeline.

Cada caso define:
  - name: nombre identificador del caso
  - equation: string de la ecuación f(x; params) = 0
  - variables: lista de variables (incógnitas)
  - parameters: lista de parámetros
  - parameter_ranges: dict {param: (min, max, num_points)}
  - expected_roots: lista de expresiones SymPy esperadas (strings)
                    una por rama, en orden (raíz más pequeña primero)
  - category: categoría del caso (linear, quadratic, cubic, etc.)
  - difficulty: 'easy', 'medium', 'hard'
  - notes: notas opcionales
"""

TEST_CASES = [
    # ================================================================
    # LINEALES CON 1 PARÁMETRO (casos 1-5)
    # ================================================================
    {
        "name": "linear_01_basic",
        "equation": "x + a - 2",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["2 - a"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Caso más simple posible"
    },
    {
        "name": "linear_02_scaled",
        "equation": "2*x - a",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["a / 2"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Coeficiente 2 delante de x"
    },
    {
        "name": "linear_03_offset",
        "equation": "x - 3*a + 5",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["3*a - 5"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Coeficiente 3 en parámetro + constante"
    },
    {
        "name": "linear_04_fraction",
        "equation": "3*x + a - 6",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-6, 6, 50)},
        "expected_roots": ["(6 - a) / 3"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Resultado con fracción"
    },
    {
        "name": "linear_05_negative",
        "equation": "-x + a + 1",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["a + 1"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Coeficiente negativo en x"
    },

    # ================================================================
    # LINEALES CON 2 PARÁMETROS (casos 6-10)
    # ================================================================
    {
        "name": "linear_06_two_params",
        "equation": "x - a - b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (-3, 3, 15), "b": (-3, 3, 15)},
        "expected_roots": ["a + b"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Suma de dos parámetros"
    },
    {
        "name": "linear_07_scaled_params",
        "equation": "x - 2*a + 3*b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (-3, 3, 15), "b": (-3, 3, 15)},
        "expected_roots": ["2*a - 3*b"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "Combinación lineal con coeficientes"
    },
    {
        "name": "linear_08_product_param",
        "equation": "x - a*b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (-3, 3, 15), "b": (-3, 3, 15)},
        "expected_roots": ["a*b"],
        "category": "linear",
        "difficulty": "medium",
        "notes": "Producto de parámetros (no lineal en params)"
    },
    {
        "name": "linear_09_division",
        "equation": "a*x - b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.5, 3, 15), "b": (-3, 3, 15)},
        "expected_roots": ["b / a"],
        "category": "linear",
        "difficulty": "medium",
        "notes": "División de parámetros; a > 0 para evitar divisor 0"
    },
    {
        "name": "linear_10_three_params",
        "equation": "x - a - b - c",
        "variables": ["x"],
        "parameters": ["a", "b", "c"],
        "parameter_ranges": {"a": (-2, 2, 8), "b": (-2, 2, 8), "c": (-2, 2, 8)},
        "expected_roots": ["a + b + c"],
        "category": "linear",
        "difficulty": "easy",
        "notes": "3 parámetros, suma simple"
    },

    # ================================================================
    # CUADRÁTICAS CON 1 PARÁMETRO (casos 11-17)
    # ================================================================
    {
        "name": "quadratic_11_simple",
        "equation": "x**2 - a",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 10, 50)},
        "expected_roots": ["-sqrt(a)", "sqrt(a)"],
        "category": "quadratic",
        "difficulty": "easy",
        "notes": "sqrt puro; a > 0 para raíces reales"
    },
    {
        "name": "quadratic_12_shifted",
        "equation": "x**2 - 2*a*x + a**2",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["a"],
        "category": "quadratic",
        "difficulty": "easy",
        "notes": "(x - a)² = 0 → raíz doble x = a"
    },
    {
        "name": "quadratic_13_factored",
        "equation": "(x - a) * (x + a)",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["-a", "a"],
        "category": "quadratic",
        "difficulty": "easy",
        "notes": "x² - a² = 0; raíces ±a"
    },
    {
        "name": "quadratic_14_linear_coeff",
        "equation": "x**2 + a*x",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["-a", "0"],
        "category": "quadratic",
        "difficulty": "easy",
        "notes": "x(x + a) = 0; una raíz es siempre 0"
    },
    {
        "name": "quadratic_15_full",
        "equation": "x**2 - 3*a*x + 2*a**2",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["a", "2*a"],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "(x-a)(x-2a) = 0"
    },
    {
        "name": "quadratic_16_irrational",
        "equation": "x**2 - 2*x - a",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0, 10, 50)},
        "expected_roots": ["1 - sqrt(1 + a)", "1 + sqrt(1 + a)"],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "Fórmula cuadrática con sqrt(1+a)"
    },
    {
        "name": "quadratic_17_param_coeff",
        "equation": "a*x**2 - 1",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["-1/sqrt(a)", "1/sqrt(a)"],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "x = ±1/√a"
    },

    # ================================================================
    # CUADRÁTICAS CON 2-3 PARÁMETROS (casos 18-24)
    # ================================================================
    {
        "name": "quadratic_18_two_params",
        "equation": "x**2 - a*x - b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (-3, 3, 15), "b": (0, 5, 15)},
        "expected_roots": [
            "(a - sqrt(a**2 + 4*b)) / 2",
            "(a + sqrt(a**2 + 4*b)) / 2"
        ],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "Fórmula cuadrática con 2 parámetros"
    },
    {
        "name": "quadratic_19_full_abc",
        "equation": "a*x**2 + b*x + c",
        "variables": ["x"],
        "parameters": ["a", "b", "c"],
        "parameter_ranges": {"a": (0.5, 3, 8), "b": (-3, 3, 8), "c": (-3, 0, 8)},
        "expected_roots": [
            "(-b - sqrt(b**2 - 4*a*c)) / (2*a)",
            "(-b + sqrt(b**2 - 4*a*c)) / (2*a)"
        ],
        "category": "quadratic",
        "difficulty": "hard",
        "notes": "Fórmula cuadrática completa; c <= 0 ayuda a tener disc >= 0"
    },
    {
        "name": "quadratic_20_factored_two",
        "equation": "(x - a) * (x - b)",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 5, 15), "b": (-5, -0.1, 15)},
        "expected_roots": ["b", "a"],
        "category": "quadratic",
        "difficulty": "easy",
        "notes": "Raíces son directamente los parámetros; a>0, b<0 para orden"
    },
    {
        "name": "quadratic_21_sum_product",
        "equation": "x**2 - (a + b)*x + a*b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 5, 15), "b": (-5, -0.1, 15)},
        "expected_roots": ["b", "a"],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "Vieta: suma=a+b, producto=a*b"
    },
    {
        "name": "quadratic_22_symmetric",
        "equation": "x**2 - a**2 - b**2",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0, 3, 12), "b": (0, 3, 12)},
        "expected_roots": ["-sqrt(a**2 + b**2)", "sqrt(a**2 + b**2)"],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "Raíz involucra norma euclidiana de (a,b)"
    },
    {
        "name": "quadratic_23_nested",
        "equation": "x**2 - 4*a*b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 3, 12), "b": (0.1, 3, 12)},
        "expected_roots": ["-2*sqrt(a*b)", "2*sqrt(a*b)"],
        "category": "quadratic",
        "difficulty": "medium",
        "notes": "sqrt de producto de parámetros"
    },
    {
        "name": "quadratic_24_depressed",
        "equation": "x**2 + a*x + a**2/4",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["-a/2"],
        "category": "quadratic",
        "difficulty": "easy",
        "notes": "(x + a/2)² = 0, raíz doble"
    },

    # ================================================================
    # CÚBICAS (casos 25-30)
    # ================================================================
    {
        "name": "cubic_25_one_root",
        "equation": "x**3 - a",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 10, 50)},
        "expected_roots": ["a**(1/3)"],
        "category": "cubic",
        "difficulty": "medium",
        "notes": "Raíz cúbica; solo 1 raíz real para a > 0"
    },
    {
        "name": "cubic_26_factored",
        "equation": "x * (x - a) * (x + a)",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["-a", "0", "a"],
        "category": "cubic",
        "difficulty": "easy",
        "notes": "x(x²-a²) = 0; tres raíces explícitas"
    },
    {
        "name": "cubic_27_quadratic_factor",
        "equation": "(x - a) * (x**2 + 1)",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["a"],
        "category": "cubic",
        "difficulty": "easy",
        "notes": "Solo 1 raíz real; x²+1 > 0 siempre"
    },
    {
        "name": "cubic_28_depressed",
        "equation": "x**3 - 3*a*x + 2*a**(3/2)",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["-2*sqrt(a)", "sqrt(a)"],
        "category": "cubic",
        "difficulty": "hard",
        "notes": "Cúbica deprimida factorizable: (x-√a)²(x+2√a)=0 → 2 raíces reales distintas"
    },
    {
        "name": "cubic_29_two_params",
        "equation": "x**3 - a*b*x",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 3, 12), "b": (0.1, 3, 12)},
        "expected_roots": ["-sqrt(a*b)", "0", "sqrt(a*b)"],
        "category": "cubic",
        "difficulty": "medium",
        "notes": "x(x² - ab) = 0"
    },
    {
        "name": "cubic_30_triple",
        "equation": "(x - a)**3",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (-5, 5, 50)},
        "expected_roots": ["a"],
        "category": "cubic",
        "difficulty": "easy",
        "notes": "Raíz triple x = a"
    },

    # ================================================================
    # CUÁRTICAS Y GRADO SUPERIOR (casos 31-35)
    # ================================================================
    {
        "name": "quartic_31_biquadratic",
        "equation": "x**4 - a**2",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["-sqrt(a)", "sqrt(a)"],
        "category": "quartic",
        "difficulty": "medium",
        "notes": "x⁴ = a² → x² = |a| → x = ±√|a|; 2 raíces reales"
    },
    {
        "name": "quartic_32_factored",
        "equation": "(x - a) * (x + a) * (x - 2*a) * (x + 2*a)",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 3, 50)},
        "expected_roots": ["-2*a", "-a", "a", "2*a"],
        "category": "quartic",
        "difficulty": "hard",
        "notes": "4 raíces lineales en a"
    },
    {
        "name": "quartic_33_double_quadratic",
        "equation": "(x**2 - a) * (x**2 - b)",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 3, 10), "b": (4, 8, 10)},
        "expected_roots": ["-sqrt(b)", "-sqrt(a)", "sqrt(a)", "sqrt(b)"],
        "category": "quartic",
        "difficulty": "hard",
        "notes": "4 raíces con sqrt; b > a > 0 para orden"
    },
    {
        "name": "quintic_34_factored",
        "equation": "x * (x - a) * (x + a) * (x - 2*a) * (x + 2*a)",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 3, 50)},
        "expected_roots": ["-2*a", "-a", "0", "a", "2*a"],
        "category": "quintic",
        "difficulty": "hard",
        "notes": "5 raíces, todas lineales en a"
    },
    {
        "name": "quartic_35_repeated",
        "equation": "(x - a)**2 * (x + a)**2",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["-a", "a"],
        "category": "quartic",
        "difficulty": "medium",
        "notes": "Raíces dobles ±a"
    },

    # ================================================================
    # FORMAS ESPECIALES (casos 36-43)
    # ================================================================
    {
        "name": "special_36_reciprocal",
        "equation": "a*x - 1",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.5, 5, 50)},
        "expected_roots": ["1/a"],
        "category": "special",
        "difficulty": "easy",
        "notes": "x = 1/a"
    },
    {
        "name": "special_37_ratio",
        "equation": "a*x - b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.5, 3, 15), "b": (-3, 3, 15)},
        "expected_roots": ["b/a"],
        "category": "special",
        "difficulty": "easy",
        "notes": "x = b/a"
    },
    {
        "name": "special_38_quadratic_ratio",
        "equation": "x**2 - a/b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 5, 12), "b": (0.5, 3, 12)},
        "expected_roots": ["-sqrt(a/b)", "sqrt(a/b)"],
        "category": "special",
        "difficulty": "medium",
        "notes": "sqrt de ratio de parámetros"
    },
    {
        "name": "special_39_difference_of_squares",
        "equation": "x**2 - (a - b)**2",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (1, 5, 12), "b": (-2, 2, 12)},
        "expected_roots": ["-(a - b)", "a - b"],
        "category": "special",
        "difficulty": "medium",
        "notes": "x = ±(a-b)"
    },
    {
        "name": "special_40_linear_three_params",
        "equation": "a*x + b*x - c",
        "variables": ["x"],
        "parameters": ["a", "b", "c"],
        "parameter_ranges": {"a": (0.5, 3, 7), "b": (0.5, 3, 7), "c": (-3, 3, 7)},
        "expected_roots": ["c / (a + b)"],
        "category": "special",
        "difficulty": "medium",
        "notes": "(a+b)x = c → x = c/(a+b)"
    },
    {
        "name": "special_41_square_root_form",
        "equation": "x**2 - (a + b)**2",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0, 3, 12), "b": (0, 3, 12)},
        "expected_roots": ["-(a + b)", "a + b"],
        "category": "special",
        "difficulty": "medium",
        "notes": "x = ±(a+b)"
    },
    {
        "name": "special_42_cubic_simple",
        "equation": "x**3 - a**3",
        "variables": ["x"],
        "parameters": ["a"],
        "parameter_ranges": {"a": (0.1, 5, 50)},
        "expected_roots": ["a"],
        "category": "special",
        "difficulty": "medium",
        "notes": "x³ - a³ = (x-a)(x²+ax+a²); solo x=a es real"
    },
    {
        "name": "special_43_mixed",
        "equation": "x**2 - a*x - b*x + a*b",
        "variables": ["x"],
        "parameters": ["a", "b"],
        "parameter_ranges": {"a": (0.1, 5, 15), "b": (-5, -0.1, 15)},
        "expected_roots": ["b", "a"],
        "category": "special",
        "difficulty": "medium",
        "notes": "(x-a)(x-b) = 0 expandido"
    },
]


def get_test_cases(category=None, difficulty=None, max_cases=None):
    """
    Filtra y retorna casos de prueba.
    
    Args:
        category: 'linear', 'quadratic', 'cubic', 'quartic', 'quintic', 'special' o None (todos)
        difficulty: 'easy', 'medium', 'hard' o None (todos)
        max_cases: máximo número de casos a retornar
    
    Returns:
        Lista de casos de prueba filtrados
    """
    cases = TEST_CASES
    
    if category is not None:
        cases = [c for c in cases if c["category"] == category]
    
    if difficulty is not None:
        cases = [c for c in cases if c["difficulty"] == difficulty]
    
    if max_cases is not None:
        cases = cases[:max_cases]
    
    return cases


def print_catalog_summary():
    """Imprime un resumen del catálogo de casos."""
    from collections import Counter
    
    cats = Counter(c["category"] for c in TEST_CASES)
    diffs = Counter(c["difficulty"] for c in TEST_CASES)
    params = Counter(len(c["parameters"]) for c in TEST_CASES)
    roots = Counter(len(c["expected_roots"]) for c in TEST_CASES)
    
    print(f"\n{'='*60}")
    print(f"  CATÁLOGO DE CASOS DE PRUEBA")
    print(f"{'='*60}")
    print(f"  Total: {len(TEST_CASES)} casos\n")
    
    print(f"  Por categoría:")
    for cat, count in sorted(cats.items()):
        print(f"    {cat:12s}: {count}")
    
    print(f"\n  Por dificultad:")
    for diff, count in sorted(diffs.items()):
        print(f"    {diff:12s}: {count}")
    
    print(f"\n  Por # parámetros:")
    for np_, count in sorted(params.items()):
        print(f"    {np_} parámetro(s): {count}")
    
    print(f"\n  Por # raíces esperadas:")
    for nr, count in sorted(roots.items()):
        print(f"    {nr} raíz/raíces: {count}")


if __name__ == "__main__":
    print_catalog_summary()
    print("\nPrimeros 5 casos:")
    for tc in TEST_CASES[:5]:
        print(f"  {tc['name']}: {tc['equation']} = 0 → {tc['expected_roots']}")
