
# Resumen del uso de sintaxis de Python por archivo

## Archivo: N4_1_Introducción
- **No contiene ejemplos claros de sintaxis específica en Python**. El documento parece ser introductorio y conceptual.

## Archivo: N4_2_Tuplas
- **Tipo de dato `tuple`**: Introducción y uso de tuplas en Python.
- **Creación de tuplas**: 
  ```python
  mi_tupla = (1, 2, 3)
  ```
- **Empaquetado y desempaquetado**:
  ```python
  a, b, c = mi_tupla
  ```
- **Tuplas como valores de retorno**:
  ```python
  def ejemplo():
      return 1, 2, 3
  ```

## Archivo: N4_3_Estructuras de datos con tuplas
- **Uso de tuplas en diccionarios**: 
  ```python
  diccionario = {
      "esquina": (0, 0),
      "tamaño": (100, 200)
  }
  ```

## Archivo: N4_4_Matrices
- **Representación de matrices** como listas de listas:
  ```python
  matriz = [
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]
  ]
  ```
- **Acceso a elementos con doble indexación**:
  ```python
  elemento = matriz[0][1]
  ```
- **Creación de matrices dinámicas**:
  ```python
  matriz = [[0] * 3 for _ in range(4)]
  ```
- **Funciones relacionadas con matrices**:
  ```python
  filas = len(matriz)
  columnas = len(matriz[0])
  ```

## Archivo: N4_5_Más sobre matrices
- **Recorridos de matrices** con bucles:
  ```python
  for fila in matriz:
      for elemento in fila:
          print(elemento)
  ```
- **Manipulación de elementos individuales**:
  ```python
  matriz[6][8] = nuevo_valor
  ```
- **Estructuras de datos anidadas**:
  ```python
  matriz = [
      [(x, y) for y in range(10)]
      for x in range(10)
  ]
  ```


## Archivo: N4_7 Introducción a visualizaciones con Matplotlib
- **Carga y visualización de imágenes**:
  ```python
  import matplotlib.pyplot as plt
  import matplotlib.image as mpimg
  img = mpimg.imread('imagen.jpg')
  plt.imshow(img)
  ```
- **Creación de gráficos básicos**:
  ```python
  import matplotlib.pyplot as plt
  plt.plot([1, 2, 3], [4, 5, 6])
  plt.show()
  ```

## Archivo: N4_8 Pandas (Series y operaciones sobre series)
- **Creación de Series**:
  ```python
  import pandas as pd
  serie = pd.Series([1, 2, 3], name="Ejemplo")
  ```
- **Acceso a valores**:
  ```python
  valor = serie.iloc[0]
  rango = serie.loc[1:2]
  ```
- **Operaciones estadísticas**:
  ```python
  maximo = serie.max()
  minimo = serie.min()
  ```

## Archivo: N4_9 DataFrames
- **Creación de DataFrames**:
  ```python
  df = pd.DataFrame({'Columna1': [1, 2], 'Columna2': [3, 4]})
  ```
- **Carga desde CSV**:
  ```python
  df = pd.read_csv('archivo.csv')
  ```
- **Selección de datos**:
  ```python
  columna = df['Columna1']
  ```
- **Filtros**:
  ```python
  filtro = df[df['Columna1'] > 2]
  ```

## Archivo: N4_10 Visualización con Pandas
- **Histograma**:
  ```python
  serie.plot(kind="hist", bins=10)
  ```
- **Gráfico de dispersión**:
  ```python
  df.plot(kind="scatter", x='ColumnaX', y='ColumnaY')
  ```
- **Boxplot**:
  ```python
  df.boxplot(column=['Columna1'], by='Categoría')
  ```
- **Guardar gráfico**:
  ```python
  fig = plt.gcf()
  fig.savefig('grafico.png')
  ```
