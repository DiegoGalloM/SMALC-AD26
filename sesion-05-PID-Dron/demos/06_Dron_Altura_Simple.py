"""
ACTIVIDAD 06 - Mi primer control: que el dron se quede a la altura que yo le diga

Idea (se la puedes explicar a cualquiera):
  1. El dron MIRA hacia abajo con un sensor y sabe a cuantos cm del piso esta.
  2. Yo le digo a que altura QUIERO que este.
  3. El dron compara las dos y se mueve:
        - muy abajo  -> sube
        - muy arriba -> baja
        - justo      -> se queda quieto
     Mientras mas lejos este de la meta, mas rapido se mueve. (Eso es el control P)

     error     = altura_que_quiero - altura_que_mide
     velocidad = KP * error

Este codigo ya funciona completo. Solo cambia los dos numeros de abajo y observa.

Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
  3. Piso despejado y sin techo bajo (minimo 2 m de altura libre)
"""

from djitellopy import Tello
import time

# ---- LO QUE PUEDES CAMBIAR ----
ALTURA_QUE_QUIERO_CM = 100   # prueba 60, 100, 150
KP = 0.8                     # "fuerza" del control. Prueba 0.2, 0.8, 2.0
# -------------------------------

DURACION_SEGUNDOS = 15
VELOCIDAD_MAXIMA = 40        # el dron nunca va mas rapido que esto (seguridad)

tello = Tello()
tello.connect()
print(f"Bateria: {tello.get_battery()}%")

tello.takeoff()
time.sleep(1)
inicio = time.time()

while time.time() - inicio < DURACION_SEGUNDOS:
    altura = tello.get_distance_tof()          # sensor hacia abajo, en cm

    error = ALTURA_QUE_QUIERO_CM - altura      # cuanto me falta (negativo = me pase)
    velocidad = KP * error                     # mas error = mas velocidad
    velocidad = max(-VELOCIDAD_MAXIMA, min(VELOCIDAD_MAXIMA, velocidad))

    # izq/der, adelante/atras, arriba/abajo, giro
    tello.send_rc_control(0, 0, int(velocidad), 0)

    print(f"quiero: {ALTURA_QUE_QUIERO_CM:>3} cm | mido: {altura:>3} cm | velocidad: {int(velocidad):>3}")
    time.sleep(0.1)

tello.send_rc_control(0, 0, 0, 0)
tello.land()

# PARA PENSAR
#  1. Con KP = 0.2 el dron tarda mucho en llegar. Con KP = 2.0, que le pasa a la altura?
#  2. Pon la mano debajo del dron mientras vuela. Que hace? Por que?
#  3. Cambia ALTURA_QUE_QUIERO_CM a mitad de vuelo (mentalmente: a los 7 s, de 100 a 60). Como cambia la velocidad?
#  4. Por que la velocidad baja sola cuando se acerca a la meta?
