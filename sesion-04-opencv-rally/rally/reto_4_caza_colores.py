# ============================================================
#  RETO 4 — Caza de colores                     ⭐⭐  200 puntos
# ============================================================
#  En imagenes/reto_4.png hay muchas pelotas. ¿Cuántas son ROJAS?
#  Cuidado: las naranjas, las rosas y las guindas (rojo oscuro) NO cuentan.
#
#  1. Encuentra el rango de las pelotas rojas con herramientas/calibrador_hsv.py
#     (cuando te pregunte la imagen, escribe: reto_4)
#  2. Escribe ese rango en BAJO y ALTO.
#  3. Completa la función. La CLAVE es el número de pelotas rojas.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"

BAJO = (0, 0, 0)  # ✏️ el rango de las pelotas ROJAS
ALTO = (179, 255, 255)


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): regresa CUÁNTAS manchas hay
def contar(mascara):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Pista: len(lista) te dice cuántos elementos tiene una lista
    return 0


imagen = cv2.imread("imagenes/reto_4.png")
hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
mascara = cv2.inRange(hsv, BAJO, ALTO)

print("🔑 Pelotas encontradas:", contar(mascara))
cv2.imshow("pelotas", imagen)
cv2.imshow("mascara", mascara)  # revisa: ¿solo las rojas están en blanco?
cv2.waitKey(0)
