# ============================================================
#  RETO 5 — Encuentra el tesoro                 ⭐⭐⭐  300 puntos
# ============================================================
#  imagenes/reto_5.png es un mapa con casillas (A1, B1, ... J7).
#  Hay 9 gemas verdes que se ven IGUALES, pero solo una es la esmeralda.
#  Ya te damos su color exacto... pero un pirata regó POLVO DE ESMERALDA
#  del mismo color por todo el mapa.
#
#  Completa la función. Cuando solo quede UN círculo rojo en el mapa,
#  la CLAVE es la casilla donde está (por ejemplo: B3).

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"

BAJO = (57, 200, 150)  # el color EXACTO de la esmeralda (ya te lo damos)
ALTO = (63, 255, 255)


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): regresa True si la mancha es GRANDE (no es polvo)
def es_grande(contorno):
    area = cv2.contourArea(contorno)
    # Pista: return area > ???      <- prueba con 10, con 100, con 1000...
    return True


mapa = cv2.imread("imagenes/reto_5.png")
hsv = cv2.cvtColor(mapa, cv2.COLOR_BGR2HSV)
mascara = cv2.inRange(hsv, BAJO, ALTO)
contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cuantos = 0
for contorno in contornos:
    if es_grande(contorno):
        cuantos = cuantos + 1
        (x, y), radio = cv2.minEnclosingCircle(contorno)
        cv2.circle(mapa, (int(x), int(y)), 40, (0, 0, 255), 3)

print("Círculos rojos en el mapa:", cuantos)
cv2.imshow("mapa del tesoro", mapa)
cv2.waitKey(0)
