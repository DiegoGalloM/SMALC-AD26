"""
Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
"""

from djitellopy import Tello
import logging
import time

# djitellopy ya recibe la telemetria del dron varias veces por segundo.
# Con esta linea le decimos a su logger que la muestre en pantalla.
Tello.LOGGER.setLevel(logging.DEBUG)

tello = Tello() #Crea una instancia de la clase Tello
tello.connect() #Conecta con el dron

tello.takeoff() # Hace que el dron despegue

# Se mueve el dron con send_rc_control
tello.send_rc_control(0, 30, 0, 0)    # avanza
time.sleep(2)

tello.send_rc_control(0, 0, 0, 30)    # gira a la derecha
time.sleep(2)

tello.send_rc_control(30, 0, 0, 0)    # se mueve a la derecha
time.sleep(2)

tello.send_rc_control(0, 0, 0, 0)     # detente (importante)

tello.land() # Hace que el dron aterrice
