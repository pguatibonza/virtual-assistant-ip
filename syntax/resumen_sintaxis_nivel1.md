
# Resumen de Sintaxis Python en Nivel 1

## **Archivo: N1_1_Descubriendo el mundo de la programación**
- **Operadores aritméticos:**
  - `+`, `-`, `*`, `/`, `//`, `%`, `**`
  - Ejemplo: `7 + 3`, `35 % 4`, `2 ** 5`
- **Operaciones con cadenas:**
  - Concatenación: `'Hello ' + 'world!'`
  - Repetición: `'Na'*16 + ' Batman!'`

---

## **Archivo: N1_2_Valores y tipos de dato**
- **Tipos básicos:**
  - `int`, `float`, `str`
- **Uso de comillas:**
  - Simples: `'Hola'`
  - Dobles: `"Hola"`
  - Triples: """Texto multilinea""", '''Texto multilinea'''
- **Función para identificar el tipo:**
  - `type(valor)`

---

## **Archivo: N1_3_Declaración de variables, instrucción de asignación y tipado dinámico**
- **Declaración y asignación:**
  - `variable = valor`
- **Tipado dinámico:**
  - Reasignación: `variable = otro_valor`
- **Restricciones en nombres de variables:**
  - No iniciar con dígitos ni usar palabras reservadas.

---

## **Archivo: N1_4_Expresiones, operadores aritméticos y operaciones sobre strings**
- **Expresiones con operadores aritméticos:**
  - `x + y`, `x - y`, `x * y`, `x / y`, `x // y`, `x % y`, `x ** y`
- **Asignaciones con operadores:**
  - `x += 5`, `x -= 3`, `x *= 2`
- **Operaciones con cadenas:**
  - Concatenación: `'Hola' + ' Mundo'`
  - Repetición: `'abc' * 3`

---

## **Archivo: N1_5_Conversión de tipos**
- **Funciones de conversión:**
  - `int()`, `float()`, `str()`
  - Ejemplo: `int('10')`, `float('3.14')`, `str(100)`

---

## **Archivo: N1_6_Funciones de Python (Matemáticas y de entrada-salida)**
- **Funciones matemáticas:**
  - `abs(valor)`, `round(valor, decimales)`, `min(valor1, valor2)`, `max(valor1, valor2)`, `pow(base, exponente)`
- **Funciones de cadenas:**
  - `ord(caracter)`, `chr(código)`
- **Entrada y salida:**
  - `input()`, `print()`
- **Ayuda sobre funciones:**
  - `help(función)`

---

## **Archivo: N1_7_Funciones y variables locales**
- **Definición de funciones:**
  ```python
  def nombre_función(parámetros):
      instrucciones
  ```
- **Ejemplo:**
  ```python
  def cuadrado(x):
      return x ** 2
  ```
- **Uso de variables locales dentro de funciones.**

---

## **Archivo: N1_8_Ejercicios de funciones**
- **Ejercicios con funciones:**
  - Convertir grados Fahrenheit a Centígrados:
    ```python
    def fahrenheit_a_centigrados(f):
        return (f - 32) * 5 / 9
    ```
  - Convertir grados a radianes:
    ```python
    def grados_a_radianes(grados):
        return grados * (3.14159 / 180)
    ```

---

## **Archivo: N1_9_Estilo de programación**
- **Buenas prácticas:**
  - Uso de nombres claros: `calcular_area()`
  - **Tipado opcional (type hints):**
    ```python
    def suma(a: int, b: int) -> int:
        return a + b
    ```

---

## **Archivo: N1_10_Construcción e importación de módulos**
- **Importación de módulos:**
  - Importar completo: `import módulo`
  - Alias: `import módulo as m`
  - Uso de funciones del módulo:
    ```python
    resultado = módulo.función()
    ```

---

## **Archivo: N1_11_Separación entre interfaz de usuario y lógica del programa**
- **Organización recomendada:**
  - **Separación de módulos:**
    - Lógica del programa en un módulo independiente.
    - Interfaz en un archivo aparte:
      - `print()` para salida de datos.
      - `input()` para entrada de datos.
- **Importación de módulos:**
  ```python
  import modulo_logica as ml
  ```
- **Estructura típica de la interfaz basada en consola:**
  - **Función principal de inicio:**
    ```python
    def iniciar_aplicacion():
        mostrar_menu()
    ```
  - **Función para el menú:**
    ```python
    def mostrar_menu():
        print("1. Opción A")
        print("2. Opción B")
        opcion = input("Seleccione una opción: ")
        return opcion
    ```
  - **Funciones específicas para conectar la interfaz y la lógica:**
    ```python
    def ejecutar_conversion():
        resultado = ml.funcion_logica()
        print(f"El resultado es: {resultado}")
    ```

---

## **Archivo: Nivel_1_Objetivos_Aprendizaje**
- **Resumen de objetivos relacionados con Python:**
  - Uso de funciones básicas (`print()`, `input()`).
  - Creación e importación de módulos:
    ```python
    import modulo
    from modulo import funcion
    ```
  - Uso de variables locales y parámetros en funciones:
    ```python
    def funcion(parametro):
        variable_local = parametro + 10
        return variable_local
    ```
  - Construcción de interfaces de consola con:
    - `print()` para mostrar menús.
    - `input()` para capturar opciones del usuario.
