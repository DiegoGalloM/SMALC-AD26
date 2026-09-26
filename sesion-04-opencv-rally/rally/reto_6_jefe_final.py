# ============================================================
#  RETO 6 — JEFE FINAL (en vivo)                ⭐⭐⭐⭐  500 puntos
# ============================================================
#  El dron de rescate tiene que seguir su objetivo sin perderlo.
#  El staff va a mover un objeto frente a tu cámara durante 10 segundos:
#    - la mira NUNCA debe perderlo, y
#    - la pantalla debe decir bien si está a la IZQUIERDA, al CENTRO o a la DERECHA.
#
#  1. Calibra el color del objeto con herramientas/calibrador_hsv.py y ponlo en BAJO y ALTO.
#  2. Completa las DOS funciones.
#  3. Llama al staff. q = salir.

import cv2

BAJO = (0, 120, 70)  # ✏️ el rango de TU objeto
ALTO = (8, 255, 255)


# ✏️ COMPLETA ESTA FUNCIÓN (3 líneas): dibuja la mira (¡igual que en la Lección 7!)
def dibujar_mira(foto, x, y, radio):
    pass


# ✏️ COMPLETA ESTA FUNCIÓN: ¿dónde está el objeto?
# La foto mide 640 de ancho:   IZQUIERDA  |  CENTRO  |  DERECHA
#                             0 ....... 213 ...... 426 ....... 640
def donde_esta(x):
    # Pista:
    #   if x < 213:
    #       return "IZQUIERDA"
    #   elif ...
    return "?"


camara = cv2.VideoCapture(0)
while True:
    ok, foto = camara.read()
    foto = cv2.flip(foto, 1)
    foto = cv2.resize(foto, (640, 480))  # siempre del mismo tamaño
    hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, BAJO, ALTO)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        if cv2.contourArea(contorno) > 500:
            (x, y), radio = cv2.minEnclosingCircle(contorno)
            dibujar_mira(foto, int(x), int(y), int(radio))
            cv2.putText(foto, donde_esta(x), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)

    cv2.imshow("jefe final", foto)
    if cv2.waitKey(1) == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
