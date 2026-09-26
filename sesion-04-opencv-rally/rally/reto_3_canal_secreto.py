# ============================================================
#  RETO 3 — El canal secreto                    ⭐⭐  200 puntos
# ============================================================
#  En imagenes/reto_3.png hay TRES palabras encimadas, cada una en
#  un canal de color distinto. Juntas no se lee nada.
#  La CLAVE está en el canal ROJO. Los otros dos tienen trampas.
#
#  Completa la función, corre el archivo y llévale la CLAVE al staff.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): regresa SOLO el canal rojo
def canal_rojo(imagen):
    canal1, canal2, canal3 = cv2.split(imagen)  # los 3 canales, en el orden de OpenCV
    # Pista: ¿cuál de los tres es el rojo? (Lección 2)
    return canal1


imagen = cv2.imread("imagenes/reto_3.png")
cv2.imshow("reto 3", imagen)
cv2.imshow("canal rojo", canal_rojo(imagen))
cv2.waitKey(0)
