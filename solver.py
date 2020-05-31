from pulp import *
from treelib import Node, Tree
import math
import random

def main():
    tipo = 'LpMaximize'

    problema = LpProblem("Ej2_Branch_and_Bound", LpMaximize)

    coeficientes = {'x1': 2, 'x2': 3}
    # Costos de restricciones
    costosRes1 = {'x1': -3, 'x2': 1}
    costosRes2 = {'x1': 4, 'x2': 2}
    costosRes3 = {'x1': 4, 'x2': -1}
    costosRes4 = {'x1': -1, 'x2': 2}

    xs = ['x1', 'x2']
    x_vars = LpVariable.dicts("v", xs, 0) # v_x1, v_x2

    problema += lpSum([coeficientes[i] * x_vars[i] for i in xs]), 'obj' # funcion objetivo

    problema += lpSum([costosRes1[i] * x_vars[i] for i in xs]) <= 1
    problema += lpSum([costosRes2[i] * x_vars[i] for i in xs]) <= 15
    problema += lpSum([costosRes3[i] * x_vars[i] for i in xs]) <= 10
    problema += lpSum([costosRes4[i] * x_vars[i] for i in xs]) <= 5

    problema.solve()

    # print(problema)

    # for variable in problema.variables():
    #         print(variable.name, "=", variable.varValue)

    # print(value(problema.objective))

    # print("Estatus: ", LpStatus[problema.status])

    # if LpStatus[problema.status] != 'Optimal':
    #     print("No se podrá resolver")

    pila_nodos = [] # nombres de los nodos (array de strings)

    arbol = Tree()

    resultado = {}
    resultado['obj'] = value(problema.objective) # Valor de z*
    resultado['vars'] = {}

    mejor_nodo = {} # Mejor nodo cada tiempo
    mejor_nodo['nodo'] = 'none'
    mejor_nodo['z']=-float('inf') # -infinito

    variables_no_enteras = [] # variables no enteras del problema actual (array de strings)
    solucion = True

    for v in problema.variables():
        resultado['vars'][v.name] = '{var}={value}'.format(var=v.name, value=v.varValue)
        resultado[v.name] = v.varValue
        
        # is_integer() devuelve True si los decimales del flotante son 0
        if not resultado[v.name].is_integer():
            # print(v.name, " no es entera")
            solucion = False
            variables_no_enteras.append(v.name)
            
    # print("Diccionario resultado: ", resultado)
    # print("Lista de variables no enteras: ", variables_no_enteras)

    if solucion == True:
        print('Automaticamente entero')
        mejor_nodo['nodo'] = 'original'
        mejor_nodo['z'] = value(problema.objective)
        mejor_nodo['resultado'] = resultado
    else:  # Se realizará arbol de decision
        # Agregamos el root a la lista de nodos
        pila_nodos.append('original')

    # NODO RAIZ del arbol de decision
    # El primero es un nombre para cuando se imprima, el segundo es un identificador,
    # el tercer parametro son los datos que gaurdará
    arbol.create_node('Original', 'original',
                    data={
                        'status': LpStatus[problema.status],
                        'problema': problema,
                        'no_enteros': variables_no_enteras,
                        'resultado': resultado
                    })
    
    p = 1 # Contador de problemas

    # **************** BRANCH AND BOUND *************

    while pila_nodos:
        solution = True

        # Para cada nodo creamos otros 2 nodos, con sus nuevas restricciones

        # FIFO. Para hacer el branching seleccionamos el ultimo nodo insertado en la pila
        nodo_ramificar = pila_nodos[0] # es un string

        # Lo removemos para que sea examinado
        pila_nodos.remove(nodo_ramificar) 

        variables_no_enteras = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['no_enteros']

        variable_ramificar = random.choice(variables_no_enteras)
        # print("Variable por la que se va a ramificar: ", variable_ramificar)

        # Aqui 3.5 pasa a 3
        piso = int(arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['resultado'][variable_ramificar])

        techo = math.ceil(arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['resultado'][variable_ramificar])

        # print("Piso: ", piso)
        # print("Techo: ", techo)

        # Copiar el original, porque le vamos a añadir una restriccion
        nodo = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['problema'].copy()

        x_elegida = xs[int(variable_ramificar.split('_')[1][1]) - 1] 

        # Añadir nueva restriccion
        nodo += x_vars[x_elegida] <= piso

        nueva_restriccion = '{x}<={piso}'.format(x=x_vars[x_elegida], piso=piso)
        # print(nodo) # subproblema 1

        nodo.solve()

        # for variable in nodo.variables():
                # print(variable.name, "=", variable.varValue)
        # print(value(nodo.objective)) # z* del subproblema 1

        # Inicializar resultado
        resultado = {}
        resultado['vars'] = {}
        variables_no_enteras = []

        # Lado izquierdo
        if LpStatus[nodo.status] == 'Optimal': # Si
            resultado['obj'] = value(nodo.objective) # 13.5
            
            for v in nodo.variables():
                resultado['vars'][v.name] = '{var}={value}'.format(var=v.name, value=v.varValue)
                resultado[v.name] = v.varValue
                if not resultado[v.name].is_integer(): # Por ej aqui, x1* = 2.25
                    solution = False
                    variables_no_enteras.append(v.name)
            
            if solution == False: # hay una variable NO entera. Habrá que ramificar
                    # print("Variables no enteras: ", variables_no_enteras)
                    
                    if mejor_nodo['nodo'] == 'none': # nuestro caso. Aun no tenemos una solucion
                        # print("Aun no tenemos una solucion")
                        pila_nodos.append('node{no}'.format(no = p))
                        # print("Pila nodos: ", pila_nodos)
                    else: 
                        if tipo == 'LpMaximize':
                            if resultado['obj'] > mejor_nodo['z']:
                                pila_nodos.append('node{no}'.format(no=p))
                        else:
                            if resultado['obj'] < mejor_nodo['z']:
                                pila_nodos.append('node{no}'.format(no=p))
            else: # todas las variables son enteras (una hoja)
                if tipo == 'LpMaximize':
                    if resultado['obj'] > mejor_nodo['z']:
                        mejor_nodo['node'] = 'node{no}'.format(no=p)
                        mejor_nodo['z'] = resultado['obj']
                        mejor_nodo['resultado'] = resultado
                else:
                    if resultado['obj'] < mejor_nodo['z']:
                        mejor_nodo['node'] = 'node{no}'.format(no=p)
                        mejor_nodo['z'] = resultado['obj']
                        mejor_nodo['resultado'] = resultado
            
            arbol.create_node('node{no}'.format(no=p), 'node{no}'.format(no=p), 
                            parent='{node}'.format(node=nodo_ramificar),
                            data={
                                'status': LpStatus[nodo.status],
                                'problema': nodo,
                                'no_enteros': variables_no_enteras,
                                'resultado': resultado,
                                'nueva_restriccion': nueva_restriccion
                            })
            
        else: # El status NO es optimal
            arbol.create_node('node{no}'.format(no=p), 'node{no}'.format(no=p), 
                            parent='{node}'.format(node=nodo_ramificar),
                            data={
                                'status': LpStatus[nodo.status],
                                'problema': nodo,
                                'no_enteros': variables_no_enteras,
                                'resultado': {'obj':LpStatus[nodo.status]},
                                'nueva_restriccion': nueva_restriccion
                            })
        p += 1

        # Lado derecho

        # Copiar el original, porque le vamos a añadir una restriccion
        nodo = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['problema'].copy()

        nodo += x_vars[x_elegida] >= techo

        nueva_restriccion = '{x}>={bs}'.format(x = x_vars[x_elegida], bs = techo)

        nodo.solve() # Infeasible

        # Volver a inicializar resultado
        resultado = {}
        resultado['vars'] = {}
        variables_no_enteras = []

        solution = True

        if LpStatus[nodo.status] == 'Optimal': # No
            resultado['obj'] = value(nodo.objective) 
            
            for v in nodo.variables():
                resultado['vars'][v.name] = '{var}={value}'.format(var=v.name, value=v.varValue)
                resultado[v.name] = v.varValue
                if not resultado[v.name].is_integer(): 
                    solution = False
                    variables_no_enteras.append(v.name)
            
            if solution == False: 
                    print("Variables no enteras: ", variables_no_enteras)
                    
                    if mejor_nodo['nodo'] == 'none': 
                        # print("Aun no tenemos una solucion")
                        pila_nodos.append('node{no}'.format(no = p))
                        # print("Pila nodos: ", pila_nodos)
                    else: 
                        if tipo == 'LpMaximize':
                            if resultado['obj'] > mejor_nodo['z']:
                                pila_nodos.append('node{no}'.format(no=p))
                        else:
                            if resultado['obj'] < mejor_nodo['z']:
                                pila_nodos.append('node{no}'.format(no=p))
            else: # todas las variables son enteras (una hoja)
                if tipo == 'LpMaximize':
                    if resultado['obj'] > mejor_nodo['z']:
                        mejor_nodo['node'] = 'node{no}'.format(no=p)
                        mejor_nodo['z'] = resultado['obj']
                        mejor_nodo['resultado'] = resultado
                else:
                    if resultado['obj'] < mejor_nodo['z']:
                        mejor_nodo['node'] = 'node{no}'.format(no=p)
                        mejor_nodo['z'] = resultado['obj']
                        mejor_nodo['resultado'] = resultado
            
            arbol.create_node('node{no}'.format(no=p), 'node{no}'.format(no=p), 
                            parent='{node}'.format(node=nodo_ramificar),
                            data={
                                'status': LpStatus[nodo.status],
                                'problema': nodo,
                                'no_enteros': variables_no_enteras,
                                'resultado': resultado,
                                'nueva_restriccion': nueva_restriccion
                            })
            
        else: # El status NO es optimal
            arbol.create_node('node{no}'.format(no=p), 'node{no}'.format(no=p), 
                            parent='{node}'.format(node=nodo_ramificar),
                            data={
                                'status': LpStatus[nodo.status],
                                'problema': nodo,
                                'no_enteros': variables_no_enteras,
                                'resultado': {'obj':LpStatus[nodo.status]},
                                'nueva_restriccion': nueva_restriccion
                            })
        p += 1

    # FIN DEL CICLO WHILE


    print(arbol.show())

    nodos_ordenados_indices = [0] # el original es 0
    nodos_ordenados = []

    for nombre in list(arbol.expand_tree(mode=Tree.DEPTH))[1:]:
         nodos_ordenados_indices.append(int(nombre[4]))


    for i in nodos_ordenados_indices:

        for j, nodo in enumerate(arbol.all_nodes()):
            if i == j:
                nodos_ordenados.append(nodo)
    
    # print("Indices  ordenados: ", nodos_ordenados_indices)

    for i, nodo in enumerate(nodos_ordenados):
        if i == 0:
            print("\n\n\t Problema original \n\n")
        else:
            print("\n\n\t Subproblema ", i, " \n\n")
        print(nodo)

    # print("Nodos ordenados: ", nodos_ordenados)

    print("\n\n\t Solucion óptima: \n")
    print("\n z* = ", int(mejor_nodo['z']))
    print("\n x1 = ", int(mejor_nodo['resultado']['v_x1']))
    print("\n x1 = ", int(mejor_nodo['resultado']['v_x2']))
    


if __name__ == '__main__':
    main()


