"""
ACTIVIDAD 04 - Mantener una altura sobre el piso con control proporcional (P)

El Tello tiene un sensor de distancia hacia ABAJO (ToF, get_distance_tof) que mide la
distancia al piso en cm. Ese es nuestro sensor de realimentacion:

    error  = altura_objetivo - altura_medida
    salida = Kp * error          <- velocidad vertical (positiva = sube)

Reto del experimento:
  - El dron debe llegar a ALTURA_1 y mantenerse.
  - A los CAMBIO_A_SEGUNDOS la meta cambia a ALTURA_2 (un "escalon" en la referencia).
  - Durante el vuelo, pasa con cuidado una caja o un libro grueso bajo el dron. Que mide el ToF?

Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
  3. Piso despejado y sin techo bajo (min. 2 m de altura libre)
"""

from djitellopy import Tello
import csv
import time

# PARAMETROS
ALTURA_1_CM = 120
ALTURA_2_CM = 70
CAMBIO_A_SEGUNDOS = 10       # momento en que la meta pasa de ALTURA_1 a ALTURA_2
DURACION_SEGUNDOS = 20
INTERVALO_SEGUNDOS = 0.05
KP = 0.0                     # TODO 1: velocidad vertical por cada cm de error. Prueba 0.3, 0.8, 1.5...
VELOCIDAD_MAXIMA = 40        # limite de seguridad de la salida
ALTURA_MINIMA_SEGURA_CM = 30   # si baja de aqui, se aborta por seguridad
ALTURA_MAXIMA_SEGURA_CM = 200  # si sube de aqui, se aborta por seguridad


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


tello = Tello()
tello.connect()
print(f"Bateria: {tello.get_battery()}%")

registro = []  # filas: tiempo, objetivo, altura, salida

try:
    tello.takeoff()
    time.sleep(1)
    inicio = time.time()

    while (time.time() - inicio) < DURACION_SEGUNDOS:
        t = time.time() - inicio
        altura_cm = tello.get_distance_tof()

        # Seguridad (no la quites): si la lectura es absurda, abortamos
        if altura_cm < ALTURA_MINIMA_SEGURA_CM or altura_cm > ALTURA_MAXIMA_SEGURA_CM:
            print(f"Altura fuera de limites seguros ({altura_cm} cm). Abortando.")
            break

        # TODO 2: elige el objetivo segun el tiempo (ALTURA_1 antes de CAMBIO_A_SEGUNDOS, ALTURA_2 despues)
        objetivo_cm = ALTURA_1_CM

        # TODO 3: calcula el error y la salida P (limitada a +-VELOCIDAD_MAXIMA)
        error_cm = 0
        velocidad_vertical = 0

        # izq/der, adelante/atras, arriba/abajo, giro
        tello.send_rc_control(0, 0, int(velocidad_vertical), 0)
        registro.append([round(t, 3), objetivo_cm, altura_cm, velocidad_vertical])
        time.sleep(INTERVALO_SEGUNDOS)

    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(1)
finally:
    try:
        tello.send_rc_control(0, 0, 0, 0)
        tello.land()
    except Exception:
        pass

with open("log_04_altura.csv", "w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(["tiempo_s", "objetivo_cm", "altura_tof_cm", "salida_vertical"])
    escritor.writerows(registro)
print("Log guardado: log_04_altura.csv  (grafica con: python graficar_csv.py log_04_altura.csv)")

# PREGUNTAS PARA PENSAR
#  1. Con KP bajo, el dron llega a la altura exacta o se queda un poco corto? Por que?
#     (pista: si el error es 3 cm, cuanta velocidad vertical manda tu control?)
#  2. Con KP alto, que pasa con la altura? Dibuja a mano como se veria la grafica.
#  3. Cuando pusiste la caja bajo el dron, que hizo el dron? Tenia razon? El ToF mide
#     "altura" o "distancia a lo que hay debajo"? Que otro sensor (get_barometer, get_height)
#     usarias para no confundirse?
#  4. Esta misma idea sirve para mantener distancia a una PARED. Que sensor necesitarias que
#     el Tello NO tiene? Como lo resolverias con lo que si tiene (hint: actividad 05)?
#  5. Que pasa en el escalon de ALTURA_1 a ALTURA_2: sube o baja mas rapido? Por que?
