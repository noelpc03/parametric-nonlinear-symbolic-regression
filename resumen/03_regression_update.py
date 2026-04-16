import numpy as np
import graphviz
import pandas as pd

from s_symbolic_regressor import SymbolicRegressorWrapper

Parametros_del_modelos = 1

archivo_csv = "datosFR2.csv"
df = pd.read_csv(archivo_csv, header=0)

parametros = df.iloc[:, :Parametros_del_modelos].values.tolist()
soluciones = df.iloc[:, Parametros_del_modelos:].values.tolist()

parametros = np.array(parametros)
soluciones = np.array(soluciones).T

def define_fitness():
    # error = 0.03 da exacto
    error = 0.01  # "bastante bien" :D

    def fitness(y, y_pred, w):
        suma = 0

        for i in range(len(y)):
            if abs(y[i] - y_pred[i]) <= error:
                suma += 1
        return suma

    return fitness

modelos = []

cubic_gp = SymbolicRegressorWrapper(
    population_size=100,
    generations=30,
    stopping_criteria=23,
    p_crossover=0.7,
    p_subtree_mutation=0.1,
    p_hoist_mutation=0.05,
    p_point_mutation=0.1,
    max_samples=0.9,
    verbose=1,
    parsimony_coefficient=0.5,
    random_state=0,
)

cubic_gp.define_metric_function(define_fitness(), is_maximize=True)

i = 0

cubic_gp.fit(parametros, soluciones[i])

modelos.append(cubic_gp)

new_parameters =  []
new_solutions = []

for i in range(len(parametros)):
    if (abs(cubic_gp.predict(parametros[i].reshape(1,-1))) - soluciones[0][i]) < 0.03:
        # no hacemos nada
        continue
    else:
        # agregamos a la lista nueva
        new_parameters.append(parametros[i])
        new_solutions.append(soluciones[0][i])

cubic_gp = SymbolicRegressorWrapper(
    population_size=100,
    generations=30,
    stopping_criteria=23,
    p_crossover=0.7,
    p_subtree_mutation=0.1,
    p_hoist_mutation=0.05,
    p_point_mutation=0.1,
    max_samples=0.9,
    verbose=1,
    parsimony_coefficient=0.5,
    random_state=0,
)

cubic_gp.define_metric_function(define_fitness(), is_maximize=True)

cubic_gp.fit(new_parameters, new_solutions)

modelos.append(cubic_gp)

new_parameters2 =  []
new_solutions2 = []

for i in range(len(new_parameters2)):
    if (abs(cubic_gp.predict(new_parameters2[i].reshape(1,-1))) - new_solutions2[0][i]) < 0.03:
        # no hacemos nada
        continue
    else:
        # agregamos a la lista nueva
        new_parameters2.append(parametros[i])
        new_solutions2.append(soluciones[0][i])
