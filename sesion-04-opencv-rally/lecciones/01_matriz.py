# ============================================================
#  LECCIÓN 1 — Una imagen es una tabla de números
# ============================================================
#  Córrelo con el botón ▶ de VSCode (arriba a la derecha).

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea)
def leer_pixel(imagen, fila, columna):
    # Pista: return imagen[fila, columna]
    return None


# ---- PARTE 1: ¿Qué ve la computadora? ----
misterio = cv2.imread("imagenes/misterio.png", 0)  # el 0 significa: cárgala en grises
print(misterio)
print("0 = negro      255 = blanco")
input("¿Qué crees que es? Dilo en voz alta y presiona Enter para verla...")

grande = cv2.resize(misterio, (400, 400), interpolation=cv2.INTER_NEAREST)  # la hacemos grande
cv2.imshow("misterio", grande)
cv2.waitKey(0)  # espera a que presiones una tecla


# ---- PARTE 2: ¿de qué tamaño es una imagen? ----
frutas = cv2.imread("imagenes/frutas.png")
print("Tamaño de frutas.png (alto, ancho, colores):", frutas.shape)


# ---- PARTE 3: leer UN pixel ----
# ✏️ MINI-RETO: cambia FILA y COLUMNA para encontrar un limón, una mora y el fondo.
#    Tip: corre herramientas/inspector_pixeles.py y haz clic en la imagen.
FILA = 400
COLUMNA = 610

pixel = leer_pixel(frutas, FILA, COLUMNA)
print("El pixel vale:", pixel)  # son 3 números: [azul, verde, rojo]

cv2.imshow("frutas", frutas)
cv2.waitKey(0)
