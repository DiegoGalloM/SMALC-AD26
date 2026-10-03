"""
ACTIVIDAD 03 - Avanzar exactamente 1 metro con control proporcional (P)

Problema: con SLEEP el dron avanza "mas o menos" un metro, y cambia con la bateria.

El Tello NO tiene un sensor que mida cuanto ha avanzado hacia el frente, pero SI mide su
velocidad (get_speed_x). Si la multiplicamos por el tiempo transcurrido y la vamos sumando
obtenemos la distancia recorrida (esto se llama integrar la velocidad u "odometria"):

    recorrido += velocidad * dt

Con esa distancia ya podemos hacer control P:

    error  = distancia_objetivo - recorrido
    salida = Kp * error          <- la velocidad baja sola conforme te acercas a la meta

Antes de correrlo:
  1. pip install djitellopy
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
  3. Deja al menos 3 m libres hacia el frente y marca el piso con cinta a 1 m del punto de inicio
"""

from djitellopy import Tello
import csv
import time

# PARAMETROS
DISTANCIA_OBJETIVO_CM = 100
KP = 0.0                     # TODO 1: velocidad (rc) por cada cm de error. Prueba valores entre 0.2 y 1.5
VELOCIDAD_MAXIMA = 40        # limite de seguridad de la salida (0-100)
VELOCIDAD_MINIMA = 0         # TODO 4: velocidad minima con la que el dron realmente se mueve
TOLERANCIA_CM = 5            # si el error es menor a esto, consideramos que llegamos
CICLOS_ESTABLES = 10         # cuantos ciclos seguidos dentro de la tolerancia para darlo por terminado
TIEMPO_MAXIMO_SEGUNDOS = 15  # seguridad: si no llega, se detiene de todos modos
INTERVALO_SEGUNDOS = 0.05
FACTOR_VELOCIDAD_A_CM_S = 10 # TODO 2: la velocidad del sensor, esta en cm/s? Calibra con el modo de abajo
KP_YAW = 2.0                 # mantiene el dron derecho (lo que hiciste en la actividad 02)

# Ponlo en True para NO volar: sostén el dron en la mano (o empujalo en el piso) y mira que
# numeros da get_speed_x al moverlo hacia adelante. Lo necesitas para el TODO 2.
MODO_CALIBRACION = False


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def error_angular(objetivo, actual):
    error = objetivo - actual
    while error > 180:
        error -= 360
    while error < -180:
        error += 360
    return error


tello = Tello()
tello.connect()
print(f"Bateria: {tello.get_battery()}%")

if MODO_CALIBRACION:
    for _ in range(150):
        print(f"vgx: {tello.get_speed_x():>4}   vgy: {tello.get_speed_y():>4}")
        time.sleep(0.1)
    raise SystemExit

registro = []  # filas: tiempo, recorrido_cm, error_cm, salida

try:
    tello.takeoff()
    time.sleep(1)

    yaw_objetivo = tello.get_yaw()
    recorrido_cm = 0.0
    ciclos_en_meta = 0
    inicio = time.time()
    t_anterior = inicio

    while (time.time() - inicio) < TIEMPO_MAXIMO_SEGUNDOS:
        ahora = time.time()
        dt = ahora - t_anterior
        t_anterior = ahora

        # TODO 2: actualiza el recorrido integrando la velocidad
        #   velocidad_cm_s = tello.get_speed_x() * FACTOR_VELOCIDAD_A_CM_S
        #   recorrido_cm  += velocidad_cm_s * dt
        # (si al avanzar el recorrido sale NEGATIVO, que signo hay que cambiar?)

        # TODO 3: calcula el error y la salida P
        #   error = objetivo - recorrido
        #   velocidad = Kp * error, limitada a +-VELOCIDAD_MAXIMA
        error_cm = DISTANCIA_OBJETIVO_CM - recorrido_cm
        velocidad = 0

        # TODO 4 (despues de probar TODO 3): el motor no se mueve con valores muy bajos.
        # Si la salida es distinta de 0 pero menor a VELOCIDAD_MINIMA, subela a VELOCIDAD_MINIMA
        # (conservando el signo). Cuando |error| <= TOLERANCIA_CM la salida debe ser 0.

        # Mantiene el rumbo (misma idea que la actividad 02)
        giro = limitar(KP_YAW * error_angular(yaw_objetivo, tello.get_yaw()), -50, 50)

        tello.send_rc_control(0, int(velocidad), 0, int(giro))
        registro.append([round(ahora - inicio, 3), round(recorrido_cm, 1), round(error_cm, 1), velocidad])

        # Termina cuando lleva CICLOS_ESTABLES seguidos dentro de la tolerancia
        ciclos_en_meta = ciclos_en_meta + 1 if abs(error_cm) <= TOLERANCIA_CM else 0
        if ciclos_en_meta >= CICLOS_ESTABLES:
            break

        time.sleep(INTERVALO_SEGUNDOS)

    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(1)
finally:
    try:
        tello.send_rc_control(0, 0, 0, 0)
        tello.land()
    except Exception:
        pass

print(f"Recorrido estimado: {recorrido_cm:.0f} cm.  MIDE con un flexometro cuanto avanzo de verdad.")
with open("log_03_un_metro.csv", "w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(["tiempo_s", "recorrido_cm", "error_cm", "salida_velocidad"])
    escritor.writerows(registro)
print("Log guardado: log_03_un_metro.csv  (grafica con: python graficar_csv.py log_03_un_metro.csv)")

# PREGUNTAS PARA PENSAR
#  1. Cuanto midio realmente el flexometro vs. lo que "cree" el dron? De donde sale la diferencia?
#  2. Como cambia el comportamiento con Kp = 0.3, 0.8 y 1.5? Se pasa de la meta (sobretiro)? Oscila?
#  3. Por que la velocidad baja sola al acercarse? Que ventaja tiene sobre "avanza 3 s y para"?
#  4. Para que sirve VELOCIDAD_MINIMA? Que pasa en la grafica cuando el error es pequeno y la
#     salida tambien (zona muerta)? Y si la quitas?
#  5. Si repites 5 veces, el error final es igual? Que pasa si la bateria esta al 100% vs. al 30%?
#  6. Este metodo acumula error (deriva). Que pasaria si el objetivo fueran 10 metros?
