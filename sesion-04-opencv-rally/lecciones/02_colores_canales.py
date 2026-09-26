# ============================================================
#  LECCIÓN 2 — Colores y canales
# ============================================================
#  Córrelo con el botón ▶ de VSCode.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): pinta un rectángulo de un color
def pintar(imagen, fila1, fila2, columna1, columna2, color):
    # Pista: escribe esta línea ARRIBA del return:
    #   imagen[fila1:fila2, columna1:columna2] = color
    return imagen


# ---- PARTE 1: un pixel de color son 3 números ----
frutas = cv2.imread("imagenes/frutas.png")
print("Un pixel de la manzana roja:", frutas[170, 190])
print("¡OpenCV guarda los colores AL REVÉS!  [azul, verde, rojo]")


# ---- PARTE 2: separar los 3 canales ----
azul, verde, rojo = cv2.split(frutas)
cv2.imshow("original", frutas)
cv2.imshow("canal azul", azul)
cv2.imshow("canal verde", verde)
cv2.imshow("canal rojo", rojo)  # ¿en qué canal brillan las manzanas? ¿y las moras?
cv2.waitKey(0)
cv2.destroyAllWindows()


# ---- PARTE 3: recortar ----
manzana = frutas[85:255, 85:255]  # [filas, columnas]
cv2.imshow("recorte", manzana)
cv2.waitKey(0)
cv2.destroyAllWindows()


# ---- PARTE 4 — MINI-RETO: ¡ponle lentes de sol al robot! ----
# ✏️ Cambia los 4 números para que el rectángulo negro tape los ojos.
#    Tip: corre herramientas/inspector_pixeles.py, escribe robot y haz clic en los ojos.
robot = cv2.imread("imagenes/robot.png")
robot = pintar(robot, 0, 60, 0, 120, (0, 0, 0))
cv2.imshow("robot", robot)
cv2.waitKey(0)
