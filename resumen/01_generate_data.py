from scipy.optimize import root
import pandas as pd
import numpy as np
from random import uniform, randint

def function1 (x,p):
    x1 = x[0]
    x2 = x[1]
    a = p[0]
    b = p[1]
    f = [(x1- a)*(x2 - a*b), x1*x2 - a*b*b]
    return f

print(function1([1,2],[3,4]))
print("El siguiente debe ser (0,0)")
print(function1([4,8], [2,4]))
print(function1([2,8], [2,4]))

cantidad_de_valores_para_parametro = 3
cantidad_de_puntos_iniciales_por_parametro = 5

cota_inferior_para_a = 0
cota_superior_para_a = 10

cota_inferior_para_b = 0
cota_superior_para_b = 10

cota_inferior_para_x0 = 0
cota_superior_para_x0 = 1000

cota_inferior_para_x1 = 0
cota_superior_para_x1 = 1000

vector_de_parametros_aleatorios = []
vector_de_puntos_iniciales = []

# we start with the values for parameter a
for i in range (cantidad_de_valores_para_parametro):
    # first we generate an initial value for the parameter
    a = uniform(cota_inferior_para_a, cota_superior_para_a)
    # once we have the value of a, generate the corresponding
    # values for b.
    for k in range (cantidad_de_valores_para_parametro):
        b = uniform(cota_inferior_para_b, cota_superior_para_b)
        # now the initial points
        for j in range(cantidad_de_puntos_iniciales_por_parametro):
            # first, we add the value of [a,b] to the vector of parameters
            vector_de_parametros_aleatorios.append([a, b])
            # now we create the initial points 
            x0 = uniform(cota_inferior_para_x0, cota_superior_para_x0)
            x1 = uniform(cota_inferior_para_x1, cota_superior_para_x1)
            # and then we add it to the vector
            vector_de_puntos_iniciales.append([x0, x1])

for i in range(len(vector_de_parametros_aleatorios)):
    print(vector_de_parametros_aleatorios[i], vector_de_puntos_iniciales[i])

def find_zeros(f, params_vector, initial_values_vector):
    found_solutions = []
    print ("iter", "success", "parameters", "solution", "function value")
    for i in range(len(params_vector)):
        current_solution = root(f, initial_values_vector[i], params_vector[i])
        # let's store the data
        found_solutions.append([current_solution.x, current_solution.fun, current_solution.success])
        print (i+1, current_solution.success, params_vector[i], current_solution.x, current_solution.fun)
    return found_solutions

found_zeros1 = find_zeros(function1, vector_de_parametros_aleatorios, vector_de_puntos_iniciales)

# the following line is to print the results
# print(found_zeros1)

def create_csv_con_problemas(params, found_zeros):
    # the first thing is to create a new list
    list_with_all_the_solutions = []
    for i in range(len(params)):
        # if we found a zero (check position 2 of found_zeros)
        if (found_zeros[2]):
            # then we store the parameters and the zero found
            # the zero found is position 0 of the the current element
            # of found_zeros
            list_with_all_the_solutions.append([params[i], found_zeros[i][0]])
    # finally, we create the csv using pandas
    df = pd.DataFrame(list_with_all_the_solutions)
    df.to_csv('datosFR3.csv', index=False)
    return list_with_all_the_solutions

l = create_csv(vector_de_parametros_aleatorios, found_zeros1)

for e in l:
    print(e)

def create_csv(params, found_zeros):
    # the first thing is to create a new list
    list_with_all_the_solutions = []
    for i in range(len(params)):
        # now we create a new list to "unpack" the arrays in parameters and zeros
        current_row = []
        # if we found a zero (check position 2 of found_zeros)
        if (found_zeros[2]):
            # then we store the parameters and the zero found
            # BUT, we are going to split the parameters, the current_row
            # does not contain any array.
            # fist let's add all the parameters
            for param in params[i]:
                current_row.append(param)
            # now let's add the zeros found:
            for zero in found_zeros[i][0]:
                current_row.append(zero)
            #finally, we add the current_row to the list_with_all_the_solutions
            list_with_all_the_solutions.append(current_row)
    # finally, we create the csv using pandas
    df = pd.DataFrame(list_with_all_the_solutions)
    df.to_csv('datosFR2.csv', index=False)
    return list_with_all_the_solutions

l = create_csv(vector_de_parametros_aleatorios, found_zeros1)

for e in l:
    print(e)
