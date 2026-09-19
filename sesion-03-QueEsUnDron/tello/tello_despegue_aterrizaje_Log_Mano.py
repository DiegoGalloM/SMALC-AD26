"""
Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
"""

from djitellopy import Tello
import time

def telemetria():
    print(f"Bateria: {tello.get_battery()}%") # Obtiene el porcentaje de bateria restante y lo imprime en pantalla

    #Sensores de altura
    print(f"Altura (cm): {tello.get_height()}") #Altura Calculada
    print(f"Distancia al suelo (ToF, cm): {tello.get_distance_tof()}") #Altura dada por el TOF sensor
    print(f"Presion barometrica: {tello.get_barometer()}") #Presion Barometrica

    #Sensores de orientacion
    print(f"Yaw: {tello.get_yaw()}")
    print(f"Pitch: {tello.get_pitch()}")
    print(f"Roll: {tello.get_roll()}")


# PARAMETROS
ALTURA_ADICIONAL_CM = 30      # cuanto sube el dron tras despegar (20-500)
SEGUNDOS_EN_EL_AIRE = 4         # cuanto tiempo flota antes de aterrizar

tello = Tello() #Crea una instancia de la clase Tello
tello.connect() #COnecta con el dron

telemetria()

tello.takeoff() # Hace que el dron despegue
tello.move_up(ALTURA_ADICIONAL_CM) # Se eleva una altura adicional

telemetria()

time.sleep(SEGUNDOS_EN_EL_AIRE) # Espera el tiempo especificado
tello.land() # Hace que el dron aterrice

telemetria()