# Las condiciones para que tome los valores del archivo .txt correctamente son:
# 1. La primera línea debe de ser el número de variables.
# 2. Los beneficios de las variables tienen que ir separadas con un espacio.
# 3. En la segunda línea deben de ir los coeficientes de la función objetivo.
# 4. En la tercera línea deben de ir los coeficientes de la restricción.
# 5. La cuarta línea es el lado derecho de la restricción.

# NOTA: Los comentarios de ejemplo se refieren al problema de la mochila resuelto en clase (6.3 del Manual)

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
        
    # Expresión regular para encontrar números enteros.
    # Tambien se evalua el caso en que el numero sea negativo
    num_format = re.compile("[\-]?[0-9]+") 

     # Lista para guardar renglones de archivo
    lineas = []

    # Lista de todos los numeros del archivo
    numeros = [] 
        
    # Leyendo el archivo por renglón
    for linea in archivo:
        lineas.append(linea)

    archivo.close() 

    # Encontrar números en cada elemento de la lista
    # NOTA: Por el momento los numeros son strings
    for linea in lineas: 
        for numero_str in linea.split(): # split() separa un string por espacios. Devuelve un array. 

            es_numero = re.match(num_format, numero_str) # Devuelve un booleano si el número cumple con la expresión regular

            if es_numero: # Si la cadena es un número ENTERO, lo guarda
                numeros.append(numero_str)
    
    # Transforma lista de strings a lista de enteros
    numeros = list(map(int, numeros)) 

    # Cantidad de variables del problema
    num_variables = numeros[0] 
    
    i = 1 # Contador
    beneficios = {}
    for s in numeros[1 : num_variables + 1]: # For para guardar los beneficios
        aux = str(i)
        x = 'x' + aux
        i = i + 1
        beneficios.update({x : s}) # ej. { 'x1': 11, 'x2': 7, 'x3': 12}

    i = 1 #Contador
    pesos = {}
    for s in numeros[num_variables + 1 : -1]: # For para guardar los pesos
        aux = str(i)
        x = 'x' + aux
        i = i + 1
        pesos.update({x : s}) # ej. { 'x1': 4, 'x2': 3, 'x3': 5}

    xs = []
    for i in range(1, num_variables + 1): # For para guardar el nombre de las variables 
        aux = str(i)
        x = 'x' + aux
        xs.append(x) # ej. ['x1', 'x2', 'x3']

    return numeros, beneficios, pesos, xs


def proceso():

    problema = LpProblem("PIA", LpMaximize)

    numeros, beneficios, pesos, xs = ingresarDatos()

    # Crear variables para el problema, a partir de la lista xs
    # variable continuas >= 0
    x_vars = LpVariable.dicts("v", xs, 0) # ej. {'x1': v_x1, 'x2': v_x2, 'x3': v_x3 }
    
    # función objetivo
    problema += lpSum([beneficios[i] * x_vars[i] for i in xs]), 'funcion_objetivo' 

    # Restricción del límite de la mochila
    problema += lpSum([pesos[i] * x_vars[i] for i in xs]) <= numeros[-1]

    # Obtener solución del problema original
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
        if not resultado[v.name].is_integer(): # Si NO es entero, se agrega al array de variables_no_enteras
            solucion = False
            variables_no_enteras.append(v.name)

    # Inicializar mejor nodo
    mejor_nodo = {}
    mejor_nodo['nodo'] = 'none' # Nombre del mejor nodo
    mejor_nodo['z']=-float('inf') # -infinito
            
    
    if solucion == True:
        print('\n El problema es automáticamente entero, ya no es necesario realizar árbol de decisión. \n')
        mejor_nodo['nodo'] = 'original'
        mejor_nodo['z'] = value(problema.objective)
        mejor_nodo['resultado'] = resultado

        print("\n Solución optima: ")
        print("Z* = ", resultado["obj"])

        for i, variable in enumerate(mejor_nodo['resultado']['vars'].keys()):
            print("\n v_x{num} = ".format(num=i+1), int(mejor_nodo['resultado'][variable]))

    else: # Agregamos el nodo raiz a la pila de nodos
        print("\n Se realizará árbol de decisión, ya que la solucion del problema original contiene variables no enteras \n")
        pila_nodos.append('original')

    # NODO RAIZ del arbol de decision
    # Parámetros
    # El primero es un nombre para cuando se imprima, el segundo es un identificador,
    # el tercer parametro son los datos que guardará
    arbol.create_node('Original', 'original',
                    data={
                        'status': LpStatus[problema.status],
                        'problema': problema,
                        'no_enteros': variables_no_enteras,
                        'resultado': resultado
                    })
    
    p = 1 # Contador de subproblemas

    # **************** BRANCH AND BOUND *************

    while pila_nodos:
        
        # Para cada nodo creamos otros 2 nodos, con sus nuevas restricciones

        # LIFO. Para hacer la ramificacion seleccionamos el último nodo insertado en la pila
        nodo_ramificar = pila_nodos[-1] 

        # Lo removemos de la pila para que sea examinado
        pila_nodos.remove(nodo_ramificar) 

        # Obtener del arbol el nodo a ramificar, para tomar sus variables no enteras
        variables_no_enteras = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['no_enteros']

        # Se hace la ramificacion por alguna de las variables_no_enteras. ej. v_x1
        variable_ramificar = random.choice(variables_no_enteras)

        
        piso = int(arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['resultado'][variable_ramificar]) # ej. 2.5 -> 2

        techo = math.ceil(arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['resultado'][variable_ramificar]) # ej. 2.5 -> 3

        # Copiar el nodo, porque le vamos a añadir una restricción
        nodo = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['problema'].copy()

        # Obtener la variable por la que se va a ramificar, del array de variables xs. 
        # ej. 'v_x1' -> ['v', 'x1'] -> 'x1' -> '1' -> 1 - 1 -> 0. En el indice 0 está 'x1'
        x_elegida = xs[int(variable_ramificar.split('_')[1][1]) - 1] 

        ###### IZQUIERDA ######

        # Añadir nueva restricción
        nodo += x_vars[x_elegida] <= piso

        nueva_restriccion = '{x} <= {piso}'.format(x=x_vars[x_elegida], piso=piso)

        # Obtener solucion del subproblema
        nodo.solve()

        mejor_nodo, pila_nodos = evaluarNodo(nodo, p, mejor_nodo, nodo_ramificar, nueva_restriccion, pila_nodos)
        
        p += 1

        ###### DERECHA ######

        # Copiar el original, porque le vamos a añadir una restricción
        nodo = arbol.get_node('{nodo}'.format(nodo=nodo_ramificar)).data['problema'].copy()

        nodo += x_vars[x_elegida] >= techo

        nueva_restriccion = '{x} >= {bs}'.format(x = x_vars[x_elegida], bs = techo)

        # Obtener solucion del subproblema
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
                    
            if mejor_nodo['nodo'] == 'none': # Primer caso. Aun no tenemos una solución
                pila_nodos.append('node{no}'.format(no = p))
            else: 
                if resultado['obj'] > mejor_nodo['z']:
                    pila_nodos.append('node{no}'.format(no=p))
                        
        else: # Todas las variables son enteras (una hoja)
            if resultado['obj'] > mejor_nodo['z']:
                mejor_nodo['nodo'] = 'node{no}'.format(no=p)
                mejor_nodo['z'] = resultado['obj']
                mejor_nodo['resultado'] = resultado
                    
        # Agregar nodo al árbol
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

        # Agregar nodo al árbol
        arbol.create_node('node{no}'.format(no=p), 'node{no}'.format(no=p), 
                            parent='{node}'.format(node=nodo_ramificar),
                            data={
                                'status': LpStatus[nodo.status],
                                'problema': nodo,
                                'no_enteros': variables_no_enteras,
                                'resultado': {'obj': LpStatus[nodo.status] }, # En el resultado solo se pone 'Infeasible'
                                'nueva_restriccion': nueva_restriccion
                            })
        
    return mejor_nodo, pila_nodos



def mostrarResultado(mejor_nodo):

    nodos_ordenados_indices = [0] # el 'original' es 0
    nodos_ordenados = []

    # Con arbol.expand_tree(mode=Tree.DEPTH) se recorre el árbol en PREORDEN (raiz, izquierda, derecha)
    for nombre in list(arbol.expand_tree(mode=Tree.DEPTH))[1:]:
        # Obtener los numeros de los nombres. ej. node12 -> 12
        num_nodo_str = re.search("\d+", nombre)
        num_nodo = int(num_nodo_str.group(0))
        nodos_ordenados_indices.append(num_nodo)


    for i in nodos_ordenados_indices:
        # arbol.all_nodes() es una lista de los nodos en orden de guardado
        for j, nodo in enumerate(arbol.all_nodes()): 
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
            print("\n\t\tRestricción que se agrego: ", nodo.data.get('nueva_restriccion'))
            print("..................................................................................................")
        
        print("\n", nodo.data['problema'])
        print("..................................................................................................")
        print("Variables no enteras: ", nodo.data['no_enteros'])
        
        if nodo.data['resultado']['obj'] == 'Infeasible':
                print("\n Es Infactible \n")
        else:
            print("z: ", nodo.data['resultado']['obj'])

            for j, variable in enumerate(nodo.data['resultado']['vars']):
                print("v_x", end="")
                print(j + 1," = ", float(nodo.data['resultado'][variable]))
        
        print("~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")

    # Encontrar el numero de subproblema óptimo
    for j, nodo in enumerate(nodos_ordenados):
        if nodo.data['resultado']['obj'] == mejor_nodo['z']:
            num_subproblema_optimo = j

    print("\n\n----------------------------------")
    print("\n\n\t Solución óptima: \n")
    print("\n\t Subproblema ", num_subproblema_optimo)
    print("----------------------------------")
    print("\n z* = ", int(mejor_nodo['z']))

    for i, variable in enumerate(mejor_nodo['resultado']['vars'].keys()):
        print("\n v_x{num} = ".format(num=i+1), int(mejor_nodo['resultado'][variable]))

    print("----------------------------------")    


def presentacion():
    print("\n\n~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~~o~")
    print("\n\t PIA - Investigación de Operaciones \n Equipo: \n Leonardo Cardenas Torres - 1818209 \n Rodolfo Rivera Monjaras - 1813838 \n Natalia Alejandra Franco Ortega - 1887865 ")
    print(" Maria del Consuelo Meza Cano - 1746075 \n Alberto Baltazar Gutierrez Ortega - 1887970 \n")
    print("..................................................................................................\n\n")


if __name__ == '__main__':
    presentacion()

    mejor_nodo = proceso()
    
    mostrarResultado(mejor_nodo)
    


