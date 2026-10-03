"""
ACTIVIDAD 02 - Volar en linea recta con control proporcional (P)

Problema: si mandamos "avanza" con send_rc_control, el dron casi nunca va derecho.
Se desvia (corrientes de aire, motores distintos, piso...). Con SLEEP no hay forma de enterarse.

Idea: el dron SI sabe hacia donde apunta (get_yaw). Si medimos el error entre el angulo
que QUEREMOS y el que TENEMOS, podemos corregir el giro en proporcion a ese error.

    error  = yaw_objetivo - yaw_actual
    salida = Kp * error          <- esto es un controlador P

Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
  3. Pon el dron en un lugar amplio, con al menos 3 m libres hacia el frente
"""

from djitellopy import Tello
import csv
import time

# PARAMETROS
VELOCIDAD_AVANCE = 30        # velocidad hacia adelante (0-100)
DURACION_SEGUNDOS = 5        # cuanto tiempo avanza
INTERVALO_SEGUNDOS = 0.05    # cada cuanto se repite el ciclo de control
KP_YAW = 0.0                 # TODO 1: empieza en 0 (sin control) y despues prueba otros valores
MAX_GIRO = 50                # limite de la salida de giro (0-100)

# Perturbacion: un "empujon" artificial al giro para ver como reacciona tu control
PERTURBAR = True
INSTANTE_PERTURBACION = 2.0  # segundos despues de empezar a avanzar
DURACION_PERTURBACION = 0.3  # segundos que dura el empujon
FUERZA_PERTURBACION = 50     # valor que se suma a la orden de giro


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def error_angular(objetivo, actual):
    """Diferencia entre dos angulos, siempre entre -180 y 180 (el camino mas corto)."""
    error = objetivo - actual
    while error > 180:
        error -= 360
    while error < -180:
        error += 360
    return error


tello = Tello()
tello.connect()
print(f"Bateria: {tello.get_battery()}%")

registro = []  # filas: tiempo, yaw, error, salida

try:
    tello.takeoff()
    time.sleep(1)

    yaw_objetivo = tello.get_yaw()  # "hacia adelante" es hacia donde apunta el dron ahora
    inicio = time.time()

    while (time.time() - inicio) < DURACION_SEGUNDOS:
        t = time.time() - inicio
        yaw_actual = tello.get_yaw()

        # TODO 2: calcula el error (usa la funcion error_angular)
        #   error = ...
        error = 0

        # TODO 3: calcula la salida del controlador P y limitala con la funcion limitar
        #   salida_giro = Kp * error
        #   (recuerda: giro positivo = a la derecha)
        salida_giro = 0

        # Perturbacion artificial (no la modifiques; es parte del experimento)
        if PERTURBAR and INSTANTE_PERTURBACION < t < INSTANTE_PERTURBACION + DURACION_PERTURBACION:
            salida_giro += FUERZA_PERTURBACION

        # izq/der, adelante/atras, arriba/abajo, giro
        tello.send_rc_control(0, VELOCIDAD_AVANCE, 0, int(limitar(salida_giro, -100, 100)))
        registro.append([round(t, 3), yaw_actual, error, salida_giro])
        time.sleep(INTERVALO_SEGUNDOS)

    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(1)
finally:
    try:
        tello.send_rc_control(0, 0, 0, 0)
        tello.land()
    except Exception:
        pass

with open("log_02_linea_recta.csv", "w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(["tiempo_s", "yaw_deg", "error_deg", "salida_giro"])
    escritor.writerows(registro)
print("Log guardado: log_02_linea_recta.csv  (grafica con: python graficar_csv.py log_02_linea_recta.csv)")

# PREGUNTAS PARA PENSAR (contestalas con tus graficas)
#  1. Corre con KP_YAW = 0 y luego con otros valores. Que cambia en la grafica del yaw?
#  2. Que pasa si Kp es muy pequeno? Y si es muy grande? Cual es el mejor valor para ti y por que?
#  3. Despues de la perturbacion, el yaw regresa EXACTAMENTE a 0 de error o se queda cerca? Por que?
#  4. Por que usamos error_angular en vez de restar directo? Que pasaria al cruzar de 179 a -179?
#  5. Si el dron se desvia hacia un lado sin girar (deriva lateral), este control lo detecta?
#     Que otro dato del dron (get_speed_y?) podria ayudarte a corregirlo?
