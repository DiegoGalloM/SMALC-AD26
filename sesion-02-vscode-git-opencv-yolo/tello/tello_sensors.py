"""
Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
"""

from djitellopy import Tello
import time

# PARAMETROS
ALTURA_ADICIONAL_CM = 45      # cuanto sube el dron tras despegar (20-500)
SEGUNDOS_EN_EL_AIRE = 4         # cuanto tiempo flota antes de aterrizar

tello = Tello() #Crea una instancia de la clase Tello
tello.connect() #COnecta con el dron
print(f"Bateria: {tello.get_battery()}%") # Obtiene el porcentaje de bateria restante y lo imprime en pantalla
print(f"Bater")
