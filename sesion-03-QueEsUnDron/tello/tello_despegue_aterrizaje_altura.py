"""
Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
"""

from djitellopy import Tello
import time

# PARAMETROS
ALTURA_ADICIONAL_CM = 30 # cuanto sube el dron tras despegar (20-500)
SEGUNDOS_EN_EL_AIRE = 4 # cuanto tiempo flota antes de aterrizar

tello = Tello() #Crea una instancia de la clase Tello
tello.connect() #Conecta con el dron

while True:
  #Sensores de altura
  print(f"Altura (cm): {tello.get_height()}") #Altura Calculada
  print(f"Distancia al suelo (ToF, cm): {tello.get_distance_tof()}") #Altura dada por el TOF sensor
  print(f"Presion barometrica: {tello.get_barometer()}") #Presion Barometrica

  print(f"Yaw: {tello.get_yaw()}") #Angulo de giro
  print(f"Pitch: {tello.get_pitch()}") #Angulo de inclinacion
  print(f"Roll: {tello.get_roll()}") #Angulo de inclinacion

  print(f"Aceleracion x: {tello.get_acceleration_x()}")
  print(f"aceleracion y: {tello.get_acceleration_y()}")
  print(f"aceleracion z: {tello.get_acceleration_z()}")


# tello.takeoff() # Hace que el dron despegue
# tello.move_up(ALTURA_ADICIONAL_CM) # Se eleva una altura adicional
# time.sleep(SEGUNDOS_EN_EL_AIRE) # Espera el tiempo especificado (la telemetria se imprime sola)
# tello.land() # Hace que el dron aterrice