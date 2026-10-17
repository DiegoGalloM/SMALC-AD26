import time

import cv2
from djitellopy import Tello

BAJO = (40, 70, 50)  # ajusta el rango HSV del objeto que seguiras.
ALTO = (85, 255, 255)
AREA_MINIMA = 700
KP_YAW = 0.12  # prueba una ganancia pequena y observa la correccion.
KP_ALTURA = 0.08
VELOCIDAD_MAXIMA = 20
DURACION_SEGUNDOS = 15
MODO_VUELO = False


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


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

    inicio = time.time()
    while time.time() - inicio < DURACION_SEGUNDOS:
        frame = lector.frame
        if frame is None:
            continue

        alto, ancho = frame.shape[:2]
        centro_x = ancho // 2
        centro_y = alto // 2
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mascara = cv2.inRange(hsv, BAJO, ALTO)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidatos = [c for c in contornos if cv2.contourArea(c) >= AREA_MINIMA]
        velocidad_vertical = 0
        velocidad_yaw = 0

        cv2.drawMarker(frame, (centro_x, centro_y), (255, 255, 255), cv2.MARKER_CROSS, 24, 2)
        if candidatos:
            x, y, w, h = cv2.boundingRect(max(candidatos, key=cv2.contourArea))
            objeto_x = x + w // 2
            objeto_y = y + h // 2
            error_x = objeto_x - centro_x
            error_y = centro_y - objeto_y
            # calcula las correcciones P y limitalas a VELOCIDAD_MAXIMA.
            velocidad_yaw = limitar(1 * KP_YAW, -VELOCIDAD_MAXIMA, VELOCIDAD_MAXIMA)
            velocidad_vertical = limitar(1 * KP_ALTURA, -VELOCIDAD_MAXIMA, VELOCIDAD_MAXIMA)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (objeto_x, objeto_y), 6, (0, 0, 255), -1)
            cv2.line(frame, (centro_x, centro_y), (objeto_x, objeto_y), (255, 0, 0), 2)
            cv2.putText(frame, f"Error x,y: {error_x}, {error_y}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Color perdido: controles en cero", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if MODO_VUELO:
            tello.send_rc_control(0, 0, int(velocidad_vertical), int(velocidad_yaw))
        cv2.imshow("Sigue el color", frame)
        cv2.imshow("Mascara", mascara)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

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
