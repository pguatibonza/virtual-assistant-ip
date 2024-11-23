
### **Resumen de la sintaxis Python en los documentos**

#### **Archivo: N3_1_Introducción al módulo**
- Uso de instrucciones iterativas para repetir ejecuciones.
- Algoritmos iterativos sobre estructuras de datos como listas, cadenas y diccionarios.
- Uso de estructuras compuestas para manejar datos.

---

#### **Archivo: N3_2_Instrucciones iterativas (while)**
- **Instrucción `while`:**
  - Estructura básica:
    ```python
    while condición:
        # Acciones a realizar
    ```
  - Ejemplo de cálculo de sumatoria usando `while`.
  - Precaución sobre ciclos infinitos si no se actualiza la condición.
- Ejemplo para obligar a un usuario a ingresar un número positivo:
  ```python
  while número < 0:
      print("Error, ingrese un número positivo")
      número = int(input("Número: "))
  ```

---

#### **Archivo: N3_3_Uso del centinela**
- **Uso del centinela:**
  - Variable booleana para controlar la salida de un ciclo.
  - Ejemplo con inicialización:
    ```python
    centinela = False
    while not centinela:
        # Acciones dentro del ciclo
        if condición_de_parada:
            centinela = True
    ```
- Leyes de De Morgan para construir condiciones lógicas:
  - Ejemplo: iterar mientras una condición no se cumpla.
- Ejercicios que incluyen:
  - Contar dígitos en un número.
  - Calcular factorial (`n!`).
  - Implementar la conjetura de Collatz.
  - Modelar la población de hormigas en una isla.

---

#### **Archivo: N3_4_Más sobre strings**
- Operadores:
  - Concatenación: `+`.
  - Repetición: `*`.
  - Contenido: `in`, `not in`.
- Funciones:
  - Conversión: `int()`, `float()`, `str()`, `ord()`, `chr()`.
  - Longitud: `len()`.
- Métodos de strings:
  - Manipulación: `.lower()`, `.upper()`, `.title()`, `.swapcase()`.
  - Reemplazo: `.replace(str1, str2)`.
  - Búsqueda: `.find(str1)`, `.count(str1)`.
  - Formato: `.format()`.
- Subcadenas:
  - Indexación: `cadena[i]`.
  - Slicing: `cadena[n:m]`.
- Uso de índices negativos para acceder desde el final.

---

#### **Archivo: N3_5_Instrucciones iterativas (for)**
- **Instrucción `for-in`:**
  - Iteración sobre secuencias:
    ```python
    for elemento in secuencia:
        # Acciones
    ```
  - Ejemplo con cadenas: contar ocurrencias de un carácter.
  - Ejemplo con `range` para iteraciones con un número fijo de repeticiones:
    ```python
    for i in range(1, 11):
        print(i)
    ```
- Uso de `range` para crear secuencias:
  ```python
  range(inicio, fin, paso)
  ```
- Ejercicios que incluyen:
  - Determinar si un número es primo.
  - Verificar si una cadena es palíndroma.

---

#### **Archivo: N3_6_Introducción a listas**
- **Listas (`list`):**
  - Creación:
    ```python
    lista = [1, 2, 3]
    lista_vacia = []
    ```
  - Acceso:
    - Indexación: `lista[i]`.
    - Slicing: `lista[n:m]`.
  - Operaciones:
    - Concatenación: `+`.
    - Longitud: `len(lista)`.
    - Mínimo y máximo: `min(lista)`, `max(lista)`.
  - Iteración:
    ```python
    for elemento in lista:
        # Acciones
    ```
- Creación mediante `range`:
  ```python
  lista = list(range(5))
  ```
- Repetición de elementos con `*`:
  ```python
  lista = [0] * 10
  ```

--- 

#### **Archivo: N3_7_Operaciones sobre listas**
- Comparación de listas con operadores:
  - Igualdad: `==`, Diferencia: `!=`.
  - Comparación de tamaño o contenido: `<`, `>`, `<=`, `>=`.
- Modificación de listas:
  - Indexación: `lista[indice] = valor`.
  - Slicing para modificar sublistas: `lista[n:m] = nueva_lista`.
  - Eliminación de elementos con `del`:
    ```python
    del lista[indice]
    del lista[n:m]
    ```
- Métodos de listas:
  - Adición: `append()`, `insert()`, `extend()`.
  - Eliminación: `remove()`, `pop()`, `clear()`.
  - Ordenamiento: `sort()`, inversión: `reverse()`.
  - Búsqueda: `index()`, `count()`.
  - Copia de listas: `copy()`, slicing (`lista[:]`).
- Conversión entre cadenas y listas:
  - Separación: `split()`.
  - Unión: `join()`.
- Construcción de listas con `list()`:
  ```python
  lista = list(range(5))
  ```

---

#### **Archivo: N3_8_Patrones de recorrido**
- Recorrido total de listas:
  - Con `while`:
    ```python
    i = 0
    while i < len(lista):
        elemento = lista[i]
        i += 1
    ```
  - Con `for-in`:
    ```python
    for elemento in lista:
        # Acciones
    ```
  - Con `for-in` y `range`:
    ```python
    for i in range(len(lista)):
        elemento = lista[i]
    ```
- Recorrido parcial con condición:
  - Con centinela:
    ```python
    i = 0
    encontrado = False
    while i < len(lista) and not encontrado:
        if lista[i] == valor_buscado:
            encontrado = True
        i += 1
    ```
  - Sin centinela:
    ```python
    i = 0
    while i < len(lista) and lista[i] != valor_buscado:
        i += 1
    ```

---

#### **Archivo: N3_9_Recorrido de diccionarios**
- Recorrido de diccionarios:
  - Llaves:
    ```python
    for llave in diccionario:
        valor = diccionario[llave]
    ```
    O con `keys()`:
    ```python
    for llave in diccionario.keys():
        # Acciones
    ```
  - Valores:
    ```python
    for valor in diccionario.values():
        # Acciones
    ```
  - Llaves y valores:
    ```python
    for llave, valor in diccionario.items():
        # Acciones
    ```

---

#### **Archivo: N3_10_Manejo de archivos**
- Apertura de archivos:
  ```python
  archivo = open("ruta", "modo")
  ```
  Modos:
  - Lectura (`r`), escritura (`w`), adición (`a`).
- Lectura de archivos:
  ```python
  linea = archivo.readline()
  ```
- Escritura de archivos:
  ```python
  archivo.write("texto")
  ```
- Cierre de archivos:
  ```python
  archivo.close()
  ```

---

#### **Archivo: N3_11_Estructura de datos compuestos**
- Diccionarios de diccionarios:
  - Creación:
    ```python
    diccionario = {
        "llave1": {"subllave1": valor, "subllave2": valor},
        "llave2": {"subllave1": valor, "subllave2": valor},
    }
    ```
  - Acceso:
    ```python
    valor = diccionario["llave1"]["subllave1"]
    ```
- Lectura de datos desde archivos para construir estructuras complejas:
  - Uso de archivos CSV.
  - Separación de datos con delimitadores (coma): `linea.split(",")`.

---

#### **Archivo: N3_12_Ejercicios**
- Ejercicios que involucran:
  - Funciones con parámetros como listas, diccionarios y cadenas.
  - Búsqueda y manejo de información en diccionarios complejos.
  - Optimización de recorridos:
    - Doble recorrido.
    - Uso de histogramas con estructuras auxiliares (`diccionarios`).
    - Resolución en un solo ciclo.

---
