# ============================================================
#  LECCIÓN 5 — Buscar un color (HSV y máscaras)
# ============================================================
#  Córrelo con el botón ▶ de VSCode. En la parte de la cámara, q = salir.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"

# Rangos HSV de algunos colores:
#   rojo:      BAJO = (0, 120, 70)     ALTO = (8, 255, 255)
#   naranja:   BAJO = (10, 120, 70)    ALTO = (20, 255, 255)
#   amarillo:  BAJO = (22, 120, 70)    ALTO = (35, 255, 255)
#   verde:     BAJO = (40, 70, 50)     ALTO = (85, 255, 255)
#   azul:      BAJO = (100, 120, 50)   ALTO = (130, 255, 255)
BAJO = (0, 120, 70)  # ✏️ cambia estos dos para buscar otro color
ALTO = (8, 255, 255)


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea)
def buscar_color(imagen, bajo, alto):
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)  # de BGR a HSV
    # Pista: return cv2.inRange(hsv, bajo, alto)
    return hsv


# ---- PARTE 1: con una foto ----
frutas = cv2.imread("imagenes/frutas.png")
mascara = buscar_color(frutas, BAJO, ALTO)
cv2.imshow("frutas", frutas)
cv2.imshow("mascara", mascara)  # blanco = SÍ es el color, negro = NO es
cv2.waitKey(0)
cv2.destroyAllWindows()


# ---- PARTE 2: con tu cámara ----
# ✏️ MINI-RETO: encuentra el rango de TU objeto con herramientas/calibrador_hsv.py
#    y escríbelo arriba en BAJO y ALTO.
camara = cv2.VideoCapture(0)
while True:
    ok, foto = camara.read()
    mascara = buscar_color(foto, BAJO, ALTO)
    cv2.imshow("camara", foto)
    cv2.imshow("mascara", mascara)
    if cv2.waitKey(1) == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
