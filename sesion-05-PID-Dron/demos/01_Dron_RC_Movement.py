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

# PARAMETROS
ALTURA_ADICIONAL_CM = 30 # cuanto sube el dron tras despegar (20-500)
SEGUNDOS_EN_EL_AIRE = 4 # cuanto tiempo flota antes de aterrizar

tello = Tello() #Crea una instancia de la clase Tello
tello.connect() #Conecta con el dron

tello.takeoff() # Hace que el dron despegue

tello.move_up(ALTURA_ADICIONAL_CM) # Se eleva una altura adicional
time.sleep(SEGUNDOS_EN_EL_AIRE) # Espera el tiempo especificado (la telemetria se imprime sola)

tello.land() # Hace que el dron aterrice
