#Las condiciones para que tome los valores del txt correctamente son:
#1. Los beneficios de las variables tienen que ir separadas con un espacio.
#2. Si el coeficiente es un 1, no dejar espacios en blanco.
#3. Si el coeficiente es negativo, dejar el signo junto al coeficiente sin pasar espacio.

from pulp import *
from treelib import Node, Tree
import math
import random
import re

arbol = Tree()

def ingresarDatos():

    nombre_archivo = ("inputGrande.txt")
    
     # Abrir el archivo a leer
    archivo = open(nombre_archivo, "r")
        
    #Expresión regular para encontrar números enteros.
    num_format = re.compile("^[\-]?[1-9]") 
     # Lista para guardar renglones de archivo
    lineas = []
    # Lista de coeficientes y costos
    numeros = [] 
        
    # Leyendo el archivo por renglon
    for line in archivo:
        lineas.append(line)

    archivo.close() 

    # Encontrar números en cada elemento de la lista
    for linea in lineas: 
        for str_aux in linea.split(): # Separa las cadenas por espacios

            isnumber = re.match(num_format, str_aux) # Devuelve un booleano si el número cumple con la expresión regular

            if isnumber: # Si la cadena es un número ENTERO, lo guarda
                numeros.append(str_aux)
    
    #Transforma lista de caracteres a lista de int
    numeros = list(map(int, numeros)) 

    # Cuantas variables tiene el problema
    num_variables = numeros[0] 
    
    i = 1 #Contador
    beneficios = {}
    for s in numeros[1 : num_variables + 1]: # For para guardar los beneficios
        x = 'x'
        aux = str(i)
        x = 'x' + aux
        i = i + 1
        beneficios.update({x : s})

    i = 1 #Contador
    pesos = {}
    for s in numeros[num_variables + 1 : -1]: # For para guardar los pesos
        x = 'x'
        aux = str(i)
        x = 'x' + aux
        i = i + 1
        pesos.update({x : s})

    xs = []
    for i in range(1, num_variables + 1): #For para guardar el nombre de las variables (x1, x2, etc.)
        x = 'x'
        aux = str(i)
        x = 'x' + aux
        xs.append(x)

    return numeros, beneficios, pesos, xs


def proceso():

    problema = LpProblem("PIA", LpMaximize)

    numeros, beneficios, pesos, xs = ingresarDatos()

    # Crear variables para el problema, a partir de la lista xs
    # variable continuas 
    x_vars = LpVariable.dicts("v", xs, 0) # v_x1, v_x2
    
    # funcion objetivo
    problema += lpSum([beneficios[i] * x_vars[i] for i in xs]), 'funcion_objetivo' 

    # Restriccion del limite de la mochila
    problema += lpSum([pesos[i] * x_vars[i] for i in xs]) <= numeros[-1]

    # Obtener solucion del problema original
    problema.solve()

    # Nombres de los nodos (array de strings) con variables no enteras
    pila_nodos = [] 

    # Inicializar resultado del nodo actual
    resultado = {}
    resultado['obj'] = value(problema.objective) # Valor de z*
    resultado['vars'] = {}


    variables_no_enteras = [] # variables no enteras del problema actual (array de strings)
    solucion = True

    # Comprobar si el problema original tiene variables no enteras 
    for v in problema.variables():
        resultado['vars'][v.name] = '{var}={value}'.format(var=v.name, value=v.varValue)
        resultado[v.name] = v.varValue
        
        # is_integer() devuelve True si los decimales del flotante son 0
        if not resultado[v.name].is_integer():
            solucion = False
            variables_no_enteras.append(v.name)

    mejor_nodo = {}
    mejor_nodo['nodo'] = 'none'
    mejor_nodo['z']=-float('inf') # -infinito
            
    
    if solucion == True:
        print('\n El problema es automaticamente entero, ya no es necesario realizar árbol de decisión. \n')
        mejor_nodo['nodo'] = 'original'
        mejor_nodo['z'] = value(problema.objective)
        mejor_nodo['resultado'] = resultado

        print("\n Solución optima: ")
        print("Z* = ", resultado["obj"])

        # Corregir Rodolfo

        print("X* = (",resultado["Xs_x1"],resultado["Xs_x2"],")")

    else: # Agregamos el root a la lista de nodos
        print("\n Se realizará árbol de decisión, ya que no hay variables no enteras \n")
        pila_nodos.append('original')

    # NODO RAIZ del arbol de decision
    # Parametros
    # El primero es un nombre para cuando se imprima, el segundo es un identificador,
    # el tercer parametro son los datos que guardará
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
        
        # Para cada nodo creamos otros 2 nodos, con sus nuevas restricciones

        # FIFO. Para hacer el branching seleccionamos el ultimo nodo insertado en la pila
        nodo_ramificar = pila_nodos[0] 

        # Lo removemos de la pila para que sea examinado
        pila_nodos.remove(nodo_ramificar) 

        variables_no_enteras = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['no_enteros']

        variable_ramificar = random.choice(variables_no_enteras)

        # Por ejemplo, aqui 3.5 pasa a 3
        piso = int(arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['resultado'][variable_ramificar])

        techo = math.ceil(arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['resultado'][variable_ramificar])

        # Copiar el nodo, porque le vamos a añadir una restriccion
        nodo = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['problema'].copy()

        x_elegida = xs[int(variable_ramificar.split('_')[1][1]) - 1] 

        ###### IZQUIERDA ######

        # Añadir nueva restriccion
        nodo += x_vars[x_elegida] <= piso

        nueva_restriccion = '{x}<={piso}'.format(x=x_vars[x_elegida], piso=piso)

        nodo.solve()

        mejor_nodo, pila_nodos = evaluarNodo(nodo, p, mejor_nodo, nodo_ramificar, nueva_restriccion, pila_nodos)
        
        p += 1

        ###### DERECHA ######

        # Copiar el original, porque le vamos a añadir una restriccion
        nodo = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['problema'].copy()

        nodo += x_vars[x_elegida] >= techo

        nueva_restriccion = '{x}>={bs}'.format(x = x_vars[x_elegida], bs = techo)

        nodo.solve()


        mejor_nodo, pila_nodos =  evaluarNodo(nodo, p, mejor_nodo, nodo_ramificar, nueva_restriccion, pila_nodos)

        p += 1

    # FIN DEL CICLO WHILE
    return mejor_nodo


def evaluarNodo(nodo, p, mejor_nodo, nodo_ramificar, nueva_restriccion, pila_nodos):
    # Inicializar resultado
        resultado = {}
        resultado['vars'] = {}
        variables_no_enteras = []

        solution = True

        if LpStatus[nodo.status] == 'Optimal':
            resultado['obj'] = value(nodo.objective)
            
            for v in nodo.variables():
                resultado['vars'][v.name] = '{var}={value}'.format(var=v.name, value=v.varValue)
                resultado[v.name] = v.varValue
                # Checar si contiene variables no enteras
                if not resultado[v.name].is_integer(): 
                    solution = False
                    variables_no_enteras.append(v.name)
            
            if solution == False: # Hay una variable NO entera. Habrá que ramificar
                    
                    if mejor_nodo['nodo'] == 'none': # Primer caso. Aun no tenemos una solucion
                        pila_nodos.append('node{no}'.format(no = p))
                    else: 
                        if resultado['obj'] > mejor_nodo['z']:
                            pila_nodos.append('node{no}'.format(no=p))
                        
            else: # Todas las variables son enteras (una hoja)
                if resultado['obj'] > mejor_nodo['z']:
                        mejor_nodo['node'] = 'node{no}'.format(no=p)
                        mejor_nodo['z'] = resultado['obj']
                        mejor_nodo['resultado'] = resultado
                    
            # Agregar nodo al arbol
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

            # Agregar nodo al arbol
            arbol.create_node('node{no}'.format(no=p), 'node{no}'.format(no=p), 
                            parent='{node}'.format(node=nodo_ramificar),
                            data={
                                'status': LpStatus[nodo.status],
                                'problema': nodo,
                                'no_enteros': variables_no_enteras,
                                'resultado': {'obj':LpStatus[nodo.status]},
                                'nueva_restriccion': nueva_restriccion
                            })
        
        return mejor_nodo, pila_nodos




def mostrarResultado(mejor_nodo):

    nodos_ordenados_indices = [0] # el original es 0
    nodos_ordenados = []

    # Se recorre el arbol en PREORDEN (root, izquierda, derecha)
    for nombre in list(arbol.expand_tree(mode=Tree.DEPTH))[1:]:
         nodos_ordenados_indices.append(int(nombre[4]))


    for i in nodos_ordenados_indices:
        for j, nodo in enumerate(arbol.all_nodes()): # Nodos en desorden
            if i == j:
                nodos_ordenados.append(nodo)
    

    for i, nodo in enumerate(nodos_ordenados):
        if i == 0:
            print("\n\n~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")
            print("\n\n\t Problema original \n")
            print("~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")
        else:
            print("\n\n~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")
            print("\n\n\t Subproblema ", i, " \n")
            print("~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")
        
        if i !=  0:
            print("\n\t\tRestriccion que se agrego: ", nodo.data.get('nueva_restriccion'))
            print("..................................................................................................")
        
        print("\n", nodo.data['problema'])
        print("..................................................................................................")
        print("Variables no enteras: ",nodo.data['no_enteros'])
        
        if nodo.data['resultado']['obj'] == 'Infeasible':
                print("\n Es Infactible \n")
        else:
            print("z: ",nodo.data['resultado']['obj'])
            for j, variable in enumerate(nodo.data['resultado']['vars']):
                print("v_x",end="")
                print(j + 1," = ",float(nodo.data['resultado'][variable]))
        #print(nodo)
        print("~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")

    # Encontrar el subproblema optimo
    for j, nodo in enumerate(nodos_ordenados):
        if nodo.data['resultado']['obj'] == mejor_nodo['z']:
            num_subproblema_optimo = j

    print("\n\n----------------------------------")
    print("\n\n\t Solucion óptima: \n")
    print("\n\t Subproblema ", num_subproblema_optimo)
    print("----------------------------------")
    print("\n z* = ", int(mejor_nodo['z']))

    for i, variable in enumerate(mejor_nodo['resultado']['vars'].keys()):
        print("\n v_x{num} = ".format(num=i+1), int(mejor_nodo['resultado'][variable]))

    print("----------------------------------")    


def presentacion():
    print("\n\n~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")
    print("\n\t PIA - Investigacion de Operaciones \n Equipo: \n Leonardo Cardenas Torres - 1818209 \n Rodolfo Rivera Monjaras - 1813838 \n Natalia Alejandra Franco Ortega - 1887865 ")
    print(" Maria del Consuelo Meza Cano - 1746075 \n Alberto Baltazar Gutierrez Ortega - 1887970 \n")
    print("..................................................................................................\n\n")


if __name__ == '__main__':
    presentacion()
    ingresarDatos()
    solucion_optima = proceso()
    mostrarResultado(solucion_optima)
    


