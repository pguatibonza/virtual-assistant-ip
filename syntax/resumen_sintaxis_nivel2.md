
# Resumen de Sintaxis de Python por Archivo

---

## **N2_1_Introducción**
Este archivo no contiene ejemplos explícitos de código Python, sino conceptos introductorios sobre el uso de datos booleanos, condicionales, y estructuras para manejar datos (por ejemplo, diccionarios).

---

## **N2_2_Booleanos y sus operadores**
- **Operadores relacionales:**
  - `==` (igual que): `x == y`
  - `!=` (diferente de): `x != y`
  - `<` (menor que): `x < y`
  - `>` (mayor que): `x > y`
  - `<=` (menor o igual que): `x <= y`
  - `>=` (mayor o igual que): `x >= y`

- **Operadores de identidad:**
  - `is`: Verifica si dos objetos son idénticos.
  - `is not`: Verifica si dos objetos no son idénticos.

- **Operadores lógicos:**
  - `and` (conjunción): `x > 0 and x < 10`
  - `or` (disyunción): `x < 0 or x > 10`
  - `not` (negación): `not x`

Ejemplos:
- `n % 2 == 0 or n % 3 == 0`
- `not (x > y)`

---

## **N2_3_Tablas de verdad y álgebra booleana**
- **Tablas de verdad** con `and`, `or`, y `not`:
  - `a and b`
  - `a or b`
  - `not a`

- **Reglas del álgebra booleana:**
  - Con `and`:
    - `x and y == y and x`
    - `x and (y and z) == (x and y) and z`
    - `x and True == x`
    - `x and False == False`
  - Con `or`:
    - `x or y == y or x`
    - `x or (y or z) == (x or y) or z`
    - `x or False == x`
    - `x or True == True`
  - Con `not`:
    - `not not (x) == x`

Ejercicios:
- `(a > b and b > c) or (b < c and a > b)`
- `a * b < a * b / c`

---

## **N2_4_Condicionales**
- **Estructuras condicionales:**
  - `if`:
    ```python
    if condición:
        # bloque de código
    ```
  - `if-else`:
    ```python
    if condición:
        # bloque si verdadero
    else:
        # bloque si falso
    ```
  - `if-elif-else` (en cascada):
    ```python
    if condición1:
        # acción1
    elif condición2:
        # acción2
    else:
        # acción3
    ```

- **Condicionales consecutivos** (no excluyentes):
  ```python
  if condición1:
      # acción1
  if condición2:
      # acción2
  ```

Ejemplos:
- Verificar número positivo:
  ```python
  if x > 0 and x < 10:
      return True
  ```
- Identificar un número con varias condiciones:
  ```python
  if x < 0:
      return -1
  elif 0 <= x < 1000:
      return 0
  ```

---

## **N2_5_Leyes de De Morgan**
- **Transformación de expresiones booleanas**:
  - `not (x and y) == (not x) or (not y)`
  - `not (x or y) == (not x) and (not y)`

Ejemplo:
```python
if not (x > 90 and y > 100):
    # acción
```
Se transforma en:
```python
if x <= 90 or y <= 100:
    # acción
```

---

## **N2_6_Cadenas de caracteres**
- **Caracteres de control:**
  - `\n`: salto de línea.
  - `\t`: tabulación.
  - `\\`: barra invertida.
  - `\'`: comilla simple.
  - `\"`: comilla doble.

- **Funciones y métodos relacionados con cadenas:**
  - `len(cadena)`: retorna la longitud de una cadena.
  - Métodos:
    - `cadena.lower()`: convierte a minúsculas.
    - `cadena.upper()`: convierte a mayúsculas.
    - `cadena.title()`: convierte a formato título.
    - `cadena.swapcase()`: intercambia mayúsculas y minúsculas.
    - `cadena.replace(patrón, reemplazo)`: reemplaza el patrón con otro texto.
    - `cadena.find(subcadena)`: busca la subcadena y retorna su índice o `-1`.
    - `cadena.count(subcadena)`: cuenta ocurrencias de una subcadena.

---

## **N2_7_Operaciones sobre cadenas de caracteres**
- **Operadores para cadenas:**
  - `+`: concatenación.
  - `*`: repetición.
  - `in`: verifica si una subcadena está presente.
  - `not in`: verifica si una subcadena no está presente.

- **Conversiones:**
  - `int(cadena)`: convierte una cadena a entero.
  - `float(cadena)`: convierte una cadena a flotante.
  - `str(valor)`: convierte un número a cadena.
  - `ord(carácter)`: convierte un carácter a su código ASCII.
  - `chr(código)`: convierte un código ASCII a su carácter.

- **Método `format`:**
  - `"{0} texto {1}".format(valor1, valor2)`: formatea cadenas con marcadores `{}`.

---

## **N2_8_Diccionarios operaciones básicas**
- **Creación:**
  - Diccionario vacío: `{}`.
  - Con elementos: `{"clave": valor, "clave2": valor2}`.

- **Operaciones básicas:**
  - Agregar/modificar elementos: `diccionario[clave] = valor`.
  - Consultar valor: `diccionario[clave]`.
  - Eliminar pareja: `del diccionario[clave]`.

- **Operadores:**
  - `in`: verifica si una clave existe en el diccionario.
  - `not in`: verifica si una clave no existe.

- **Métodos:**
  - `diccionario.get(clave, valor_por_defecto)`: busca una clave y retorna un valor por defecto si no existe.
  - `len(diccionario)`: retorna la cantidad de parejas clave-valor.

---

## **N2_9_Diccionarios mutabilidad, borrado de datos y parámetros por referencia**
- **Mutabilidad:**
  - Los diccionarios se pasan como referencia, no como copia.
  - Métodos para trabajar con copias:
    - `diccionario.copy()`: crea una copia superficial.

- **Borrado de elementos:**
  - `del diccionario[clave]`.

- **Parámetros en funciones:**
  - Los diccionarios pueden ser modificados dentro de funciones, ya que son pasados por referencia.

---
