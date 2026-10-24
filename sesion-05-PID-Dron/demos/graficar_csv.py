"""
Grafica el CSV que genera cualquiera de las actividades (02, 03, 04 o 05).

Uso:
  pip install matplotlib
  python graficar_csv.py log_02_linea_recta.csv

La primera columna del CSV es el tiempo; cada columna siguiente se dibuja en su propia grafica.
"""

import csv
import sys
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print("Uso: python graficar_csv.py archivo.csv")
    sys.exit(1)

with open(sys.argv[1]) as f:
    lector = csv.reader(f)
    encabezado = next(lector)
    columnas = list(zip(*[[float(x) for x in fila] for fila in lector]))

tiempo = columnas[0]
fig, ejes = plt.subplots(len(columnas) - 1, 1, sharex=True, figsize=(8, 2.5 * (len(columnas) - 1)))
if len(columnas) == 2:
    ejes = [ejes]
for eje, nombre, datos in zip(ejes, encabezado[1:], columnas[1:]):
    eje.plot(tiempo, datos)
    eje.set_ylabel(nombre)
    eje.grid(True)
ejes[-1].set_xlabel(encabezado[0])
plt.tight_layout()
plt.show()
