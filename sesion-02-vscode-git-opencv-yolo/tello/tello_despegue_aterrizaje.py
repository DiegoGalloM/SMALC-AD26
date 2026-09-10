"""
Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
"""

from djitellopy import Tello
import time

# PARAMETROS
ALTURA_ADICIONAL_CM = 30      # cuanto sube el dron tras despegar (20-500)
SEGUNDOS_EN_EL_AIRE = 4         # cuanto tiempo flota antes de aterrizar

tello = Tello()
tello.connect()
print(f"Bateria: {tello.get_battery()}%")

tello.takeoff()
tello.move_up(ALTURA_ADICIONAL_CM)
time.sleep(SEGUNDOS_EN_EL_AIRE)
tello.land()
