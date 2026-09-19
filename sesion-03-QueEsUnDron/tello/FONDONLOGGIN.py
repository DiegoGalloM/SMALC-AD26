"""
Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello 
"""

from djitellopy import Tello
import time
import threading

# PARAMETROS
ALTURA_ADICIONAL_CM = 45        # cuanto sube el dron tras despegar (20-500)
SEGUNDOS_EN_EL_AIRE = 4          # cuanto tiempo flota antes de aterrizar
INTERVALO_LOG_SEGUNDOS = 0.5     # cada cuanto se imprime el estado de los sensores

tello = Tello() #Crea una instancia de la clase Tello
tello.connect() #Conecta con el dron
print(f"Bateria: {tello.get_battery()}%") # Obtiene el porcentaje de bateria restante y lo imprime en pantalla

leyendo_sensores = True # Bandera para controlar el hilo de lectura

def formatear_panel(estado):
    # Arma un panel legible (varias lineas agrupadas) con el estado de los sensores.
    return (
        f"  Orientacion   pitch: {estado['pitch']:>4}deg   roll: {estado['roll']:>4}deg   yaw: {estado['yaw']:>4}deg\n"
        f"  Velocidad     vgx: {estado['vgx']:>4}   vgy: {estado['vgy']:>4}   vgz: {estado['vgz']:>4}  cm/s\n"
        f"  Aceleracion   agx: {estado['agx']:>7.1f}   agy: {estado['agy']:>7.1f}   agz: {estado['agz']:>7.1f}  mg\n"
        f"  Altura        h: {estado['h']:>4}cm   tof: {estado['tof']:>4}cm   baro: {estado['baro']:>7.1f}cm\n"
        f"  Estado        bateria: {estado['bat']:>3}%   temp: {estado['templ']}-{estado['temph']}C"
    )

def imprimir_sensores():
    """Corre en un hilo aparte y redibuja un panel con el estado de los sensores cada INTERVALO_LOG_SEGUNDOS."""
    while leyendo_sensores:
        estado = tello.get_current_state() # Diccionario con la ultima lectura de sensores del dron
        print("\033[H\033[J", end="") # Limpia la pantalla y regresa el cursor arriba (dibuja encima, no hace scroll)
        print("=== Sensores Tello (Ctrl+C para forzar salida) ===\n")
        print(formatear_panel(estado))
        time.sleep(INTERVALO_LOG_SEGUNDOS)

hilo_sensores = threading.Thread(target=imprimir_sensores, daemon=True) # Hilo en segundo plano
hilo_sensores.start() # Empieza a imprimir sensores mientras el dron vuela

# RUTINA DE VUELO
tello.takeoff() # Hace que el dron despegue
tello.move_up(ALTURA_ADICIONAL_CM) # Se eleva una altura adicional
tello.move_right(ALTURA_ADICIONAL_CM)
tello.move_down(ALTURA_ADICIONAL_CM)
tello.move_left(ALTURA_ADICIONAL_CM)
time.sleep(SEGUNDOS_EN_EL_AIRE) # Espera el tiempo especificado
tello.land() # Hace que el dron aterrice

leyendo_sensores = False # Detiene el hilo de lectura de sensores
hilo_sensores.join() # Espera a que el hilo termine antes de cerrar el programa
