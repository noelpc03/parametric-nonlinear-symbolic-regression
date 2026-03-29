#!/usr/bin/env python3
"""Test simple para verificar que safe_root5 funciona."""

from pysr import PySRRegressor
import numpy as np
import sympy

print("Iniciando test de safe_root5...")

X = np.random.rand(50, 1)
y = np.sqrt(X[:, 0])

model = PySRRegressor(
    niterations=5,
    populations=1,
    unary_operators=[
        'safe_root5(x) = copysign(abs(x)^(one(x)/typeof(x)(5)), x)'
    ],
    extra_sympy_mappings={
        'safe_root5': lambda x: sympy.sign(x) * sympy.Pow(sympy.Abs(x), sympy.Rational(1, 5)),
    },
    temp_equation_file=True,
    delete_tempfiles=True,
    procs=0,
    turbo=False,
)

try:
    model.fit(X, y)
    print('OK - safe_root5 funciona!')
except Exception as e:
    print(f'ERROR: {e}')
