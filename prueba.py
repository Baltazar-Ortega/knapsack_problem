# Asegurarse de tener instalado el paquete PuLP
# Si no se tiene: $ pip install PuLP
import pulp 

# # Ejemplo de: https://benalexkeen.com/linear-programming-with-python-and-pulp-part-2/
# my_lp_problem = pulp.LpProblem('My_LP_Problem', pulp.LpMaximize)

# x = pulp.LpVariable('x', lowBound=0, cat='Continuous')
# y = pulp.LpVariable('y', lowBound=2, cat='Continuous')

# my_lp_problem += 4 * x + 3 * y, 'z'

# my_lp_problem += 2 * y <= 25 - x
# my_lp_problem += 4 * y >= 2 * x - 8
# my_lp_problem += y <= 2 * x - 5

# print(my_lp_problem)

# my_lp_problem.solve()

# print(pulp.LpStatus[my_lp_problem.status])

# for variable in my_lp_problem.variables():
#         print(variable.name, "=", variable.varValue)

# print(pulp.value(my_lp_problem.objective))

# print("\n\n\n\n")

print("\n\n\n\n\t Mochila con resultados NO enteros \n\n\n")

# Resultado optimo con variables no enteras (decimales)
problema_mochila = pulp.LpProblem('Problema_Mochila_6.3', pulp.LpMaximize)

x = pulp.LpVariable('x', lowBound=0, cat='Continuous')
y = pulp.LpVariable('y', lowBound=0, cat='Continuous')
z = pulp.LpVariable('z', lowBound=0, cat='Continuous')

problema_mochila += 11 * x + 7 * y + 12 * z, 'z'

problema_mochila +=  4 * x + 3 * y + 5 * z <= 10

print(problema_mochila)

problema_mochila.solve()

print(pulp.LpStatus[problema_mochila.status])

for variable in problema_mochila.variables():
        print(variable.name, "=", variable.varValue)

print(pulp.value(problema_mochila.objective))


print("\n\n\n\n\t Mochila con resultados NO enteros. Se usan listas \n\n\n")

# Resultado optimo con variables no enteras (decimales)
problema_mochila_enteros = pulp.LpProblem('Problema_Mochila_Enteros_6.3', pulp.LpMaximize)

costos = {'x': 11, 'y': 7, 'z': 12}
pesos = {'x': 4, 'y': 3, 'z': 5}

xs = ['x', 'y', 'z']
x_vars = pulp.LpVariable.dicts("Xs", xs, 0) # Prefijo Xs_

problema_mochila_enteros += pulp.lpSum([costos[i] * x_vars[i] for i in xs]), 'z'  # 11*Xs_x + 7*Xs_y + 12*Xs_z + 0

problema_mochila_enteros += pulp.lpSum([pesos[i] * x_vars[i] for i in xs]) <= 10


print(problema_mochila_enteros)

problema_mochila_enteros.solve()

print("Estatus: ", pulp.LpStatus[problema_mochila_enteros.status]) # Optimal

for variable in problema_mochila_enteros.variables():
        print(variable.name, "=", variable.varValue)

print(pulp.value(problema_mochila_enteros.objective)) # 27.5






