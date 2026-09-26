# ============================================================
#  RETO 1 — Detective de pixeles                ⭐  100 puntos
# ============================================================
#  En imagenes/reto_1.png hay una palabra secreta escondida.
#  En la FILA 237 (empezando en la columna 30 y brincando de 20 en 20)
#  el canal ROJO de cada pixel guarda una letra:
#      1 = A    2 = B    3 = C   ...   26 = Z        (0 = se acabó el mensaje)
#
#  Completa la función, corre el archivo y llévale la CLAVE al staff.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): regresa SOLO el número del canal ROJO
def leer_rojo(imagen, fila, columna):
    pixel = imagen[fila, columna]  # 3 números... ¿en qué ORDEN los guarda OpenCV? (Lección 2)
    # Pista: return pixel[?]       <- el primero es pixel[0]
    return 0


LETRAS = "?ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # LETRAS[1] es "A", LETRAS[2] es "B"...

imagen = cv2.imread("imagenes/reto_1.png")
mensaje = ""

for columna in range(30, 600, 20):
    numero = leer_rojo(imagen, 237, columna)
    if numero == 0:
        break
    mensaje = mensaje + LETRAS[numero]

print("🔑 Mensaje secreto:", mensaje)
