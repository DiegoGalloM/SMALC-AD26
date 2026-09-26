# ============================================================
#  LECCIÓN 3 — Grises y blanco y negro (threshold)
# ============================================================
#  Córrelo con el botón ▶ de VSCode.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"

UMBRAL = 127  # ✏️ prueba con otros números entre 0 y 255 y vuelve a correr


# ✏️ COMPLETA ESTA FUNCIÓN (2 líneas)
# Los pixeles MÁS CLAROS que el umbral se vuelven blancos; los demás, negros.
def blanco_y_negro(gris, umbral):
    # Pista:
    #   _, resultado = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
    #   return resultado
    return gris


manzana = cv2.imread("imagenes/manzana.png")
gris = cv2.cvtColor(manzana, cv2.COLOR_BGR2GRAY)  # de color a grises

resultado = blanco_y_negro(gris, UMBRAL)

cv2.imshow("color", manzana)
cv2.imshow("grises", gris)
cv2.imshow("blanco y negro", resultado)
cv2.waitKey(0)

# ✏️ MINI-RETOS
# 1) ¿Con qué UMBRAL queda la manzana completa pero SIN la sombra?
# 2) Cambia cv2.THRESH_BINARY por cv2.THRESH_BINARY_INV. ¿Qué pasó?
# 3) ¿Por qué queda un hoyito blanco dentro de la manzana?
