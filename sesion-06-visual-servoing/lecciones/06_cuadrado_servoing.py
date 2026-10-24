"""
LECCION 6 - Recorrer un cuadrado mientras centra un color

Empieza en modo de prueba. Para volar, el staff debe revisar el espacio y
cambiar MODO_VUELO a True.

send_rc_control recibe: izquierda/derecha, adelante/atras, arriba/abajo, giro.
El cuadrado es una trayectoria por tiempo: el servo visual sigue corrigiendo
el giro y la altura, pero no garantiza que el dron dibuje un cuadrado perfecto.
"""

import time

import cv2
from djitellopy import Tello

BAJO = (40, 70, 50)
ALTO = (85, 255, 255)
AREA_MINIMA = 700

KP_YAW = 0.12
KP_ALTURA = 0.08
VELOCIDAD_MAXIMA = 20

VELOCIDAD_LATERAL = 20
VELOCIDAD_AVANCE = 20
SEGUNDOS_POR_LADO = 3
INTERVALO_CONTROL = 0.05
MODO_VUELO = False


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def movimiento_del_cuadrado(tiempo):
    """Devuelve (lateral, avance) para el lado actual del cuadrado."""
    lado = int(tiempo // SEGUNDOS_POR_LADO) % 4
    movimientos = [
        (0, VELOCIDAD_AVANCE),
        (VELOCIDAD_LATERAL, 0),
        (0, -VELOCIDAD_AVANCE),
        (-VELOCIDAD_LATERAL, 0),
    ]
    return movimientos[lado]


tello = Tello()
despego = False

try:
    tello.connect()
    print(f"Bateria: {tello.get_battery()}%")
    tello.streamon()
    lector = tello.get_frame_read()
    time.sleep(2)

    if MODO_VUELO:
        tello.takeoff()
        despego = True

    duracion = SEGUNDOS_POR_LADO * 4
    inicio = time.time()
    while time.time() - inicio < duracion:
        frame = lector.frame
        if frame is None:
            continue

        tiempo = time.time() - inicio
        alto, ancho = frame.shape[:2]
        centro_x = ancho // 2
        centro_y = alto // 2
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mascara = cv2.inRange(hsv, BAJO, ALTO)
        contornos, _ = cv2.findContours(
            mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        candidatos = [c for c in contornos if cv2.contourArea(c) >= AREA_MINIMA]

        lateral = 0
        avance = 0
        velocidad_vertical = 0
        velocidad_yaw = 0
        mensaje = "Color perdido: dron detenido"

        cv2.drawMarker(
            frame, (centro_x, centro_y), (255, 255, 255), cv2.MARKER_CROSS, 24, 2
        )

        if candidatos:
            x, y, w, h = cv2.boundingRect(max(candidatos, key=cv2.contourArea))
            objeto_x = x + w // 2
            objeto_y = y + h // 2
            error_x = objeto_x - centro_x
            error_y = centro_y - objeto_y
            velocidad_yaw = int(
                limitar(KP_YAW * error_x, -VELOCIDAD_MAXIMA, VELOCIDAD_MAXIMA)
            )
            velocidad_vertical = int(
                limitar(KP_ALTURA * error_y, -VELOCIDAD_MAXIMA, VELOCIDAD_MAXIMA)
            )
            lateral, avance = movimiento_del_cuadrado(tiempo)
            lado = int(tiempo // SEGUNDOS_POR_LADO) % 4 + 1
            mensaje = f"Lado {lado}/4 | Error x,y: {error_x}, {error_y}"

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (objeto_x, objeto_y), 6, (0, 0, 255), -1)
            cv2.line(frame, (centro_x, centro_y), (objeto_x, objeto_y), (255, 0, 0), 2)

        cv2.putText(
            frame, mensaje, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0, 255, 0) if candidatos else (0, 0, 255), 2
        )
        cv2.putText(
            frame, f"RC lateral, avance: {lateral}, {avance}", (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2
        )

        if MODO_VUELO:
            tello.send_rc_control(lateral, avance, velocidad_vertical, velocidad_yaw)
        cv2.imshow("Cuadrado con servo visual", frame)
        cv2.imshow("Mascara", mascara)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time.sleep(INTERVALO_CONTROL)

finally:
    if despego:
        try:
            tello.send_rc_control(0, 0, 0, 0)
            time.sleep(0.5)
            tello.land()
        except Exception:
            pass
    try:
        tello.streamoff()
    except Exception:
        pass
    cv2.destroyAllWindows()
