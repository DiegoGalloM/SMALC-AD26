# ============================================================
#  LECCIÓN 1 — El semáforo: tu primera máquina de estados
# ============================================================
#  Un semáforo siempre está en UN solo estado: VERDE, AMARILLO o ROJO.
#  Cambia de estado cuando pasa cierto tiempo:
#
#             4 s                 2 s             4 s
#     VERDE ───────► AMARILLO ───────► ROJO ───────► VERDE ...
#
#  Córrelo con el botón ▶ de VSCode. q = salir.

import time

import cv2
import numpy as np

estado = "VERDE"
inicio = time.time()  # cuándo empezó el estado actual

while True:
    tecla = cv2.waitKey(50)
    if tecla == ord("q"):
        break
    segundos = time.time() - inicio  # cuánto tiempo llevamos en el estado actual

    # ===================== LÓGICA DE ESTADOS =====================
    if estado == "VERDE":
        if segundos > 4:
            estado = "AMARILLO"
            inicio = time.time()  # ¡el reloj vuelve a empezar!

    elif estado == "AMARILLO":
        # ✏️ COMPLETA: si pasan 2 segundos, cambia a "ROJO" (copia la idea de VERDE)
        pass

    elif estado == "ROJO":
        # ✏️ COMPLETA: si pasan 4 segundos, regresa a "VERDE"
        pass

    # ✏️ MINI-RETO 2: el modo noche (descomenta y completa)
    # elif estado == "NOCHE":
    #     ...
    # =============================================================

    # Dibujar el semáforo (ya está hecho)
    lienzo = np.zeros((460, 300, 3), np.uint8)
    cv2.rectangle(lienzo, (90, 20), (210, 400), (60, 60, 60), -1)
    parpadeo = int(segundos * 2) % 2 == 0
    rojo = (0, 0, 255) if estado == "ROJO" else (40, 40, 40)
    amarillo = (0, 220, 255) if estado == "AMARILLO" or (estado == "NOCHE" and parpadeo) else (40, 40, 40)
    verde = (0, 220, 0) if estado == "VERDE" else (40, 40, 40)
    cv2.circle(lienzo, (150, 85), 45, rojo, -1)
    cv2.circle(lienzo, (150, 210), 45, amarillo, -1)
    cv2.circle(lienzo, (150, 335), 45, verde, -1)
    cv2.putText(lienzo, f"{estado}  {segundos:.1f} s", (20, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.imshow("semaforo (q = salir)", lienzo)

cv2.destroyAllWindows()

# ✏️ MINI-RETOS
# 1) Botón para peatones: si estás en VERDE y presionan la tecla "p", pasa a AMARILLO de inmediato.
#       Pista:  if tecla == ord("p"):
# 2) Modo noche: si presionan "n" (en cualquier color), el semáforo pasa a "NOCHE"
#    (el amarillo parpadea solo). Si en NOCHE presionan "n" otra vez, regresa a "ROJO".
# 3) ¿Qué pasa si se te olvida escribir  inicio = time.time()  al cambiar de estado?
