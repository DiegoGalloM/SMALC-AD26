# ============================================================
#  RETO 2 — Mensaje en la oscuridad             ⭐  100 puntos
# ============================================================
#  imagenes/reto_2.png parece una foto con la luz apagada...
#  pero tiene mensajes escritos con tinta "un poquito menos negra".
#  Solo el UMBRAL correcto los hace aparecer. ¡Y hay más de uno!
#
#  1. Completa la función (igual que en la Lección 3).
#  2. Cambia el UMBRAL y vuelve a correr hasta que aparezca la CLAVE.
#  3. Enséñale al staff tu ventana en blanco y negro con la clave.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"

UMBRAL = 127  # ✏️ cambia este número (entre 0 y 255)


# ✏️ COMPLETA ESTA FUNCIÓN (2 líneas)
def blanco_y_negro(gris, umbral):
    # Pista: es igual que en la Lección 3
    return gris


imagen = cv2.imread("imagenes/reto_2.png")
gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

resultado = blanco_y_negro(gris, UMBRAL)
cv2.imshow("reto 2", resultado)
cv2.waitKey(0)
