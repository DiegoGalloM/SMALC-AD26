# ============================================================
#  LECCIÓN 7 — Dibujar (y que una mira siga a tu objeto)
# ============================================================
#  Córrelo con el botón ▶ de VSCode. En la parte de la cámara, q = salir.

import cv2
import numpy as np

BAJO = (0, 120, 70)  # ✏️ el rango de TU objeto (usa herramientas/calibrador_hsv.py)
ALTO = (8, 255, 255)


# ✏️ COMPLETA ESTA FUNCIÓN (3 líneas): dibuja una mira sobre el objeto
def dibujar_mira(foto, x, y, radio):
    # Pista (quita el pass y escribe):
    #   cv2.circle(foto, (x, y), radio, (0, 255, 0), 3)       <- círculo verde alrededor
    #   cv2.circle(foto, (x, y), 5, (0, 0, 255), -1)          <- punto rojo en el centro
    #   cv2.putText(foto, "OBJETIVO", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    pass


# ---- PARTE 1: dibujar en un lienzo negro ----
lienzo = np.zeros((400, 600, 3), np.uint8)  # una imagen negra de 400 x 600

cv2.line(lienzo, (50, 50), (550, 50), (255, 255, 255), 3)  # línea blanca
cv2.rectangle(lienzo, (50, 100), (250, 250), (0, 255, 0), 3)  # rectángulo verde
cv2.circle(lienzo, (400, 175), 75, (0, 0, 255), -1)  # círculo rojo (-1 = relleno)
cv2.putText(lienzo, "Hola SMALC", (50, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)

cv2.imshow("lienzo", lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()
# OJO 1: para DIBUJAR se usa (x, y) = (columna, fila).
# OJO 2: putText no sabe escribir acentos ni ñ.


# ---- PARTE 2: ¡la mira sigue a tu objeto! ----
camara = cv2.VideoCapture(0)
while True:
    ok, foto = camara.read()
    foto = cv2.flip(foto, 1)  # como espejo
    hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, BAJO, ALTO)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        if cv2.contourArea(contorno) > 500:  # ignora las manchas chiquitas
            (x, y), radio = cv2.minEnclosingCircle(contorno)  # el círculo que encierra la mancha
            dibujar_mira(foto, int(x), int(y), int(radio))

    cv2.imshow("sigue a tu objeto", foto)
    if cv2.waitKey(1) == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
