"""
ACTIVIDAD 05 - Mantener una distancia fija a un ArUco usando la camara

El Tello no tiene sensor de distancia hacia el frente, pero SI tiene camara. Un ArUco es
un cuadro de tamano CONOCIDO: entre mas lejos esta, mas pequeno se ve en la imagen.
Con el modelo de camara "pinhole" (geometria de triangulos semejantes):

    distancia = (FOCAL_PX * LADO_REAL_CM) / lado_en_pixeles

Con esa distancia hacemos control P:

    error  = distancia_medida - distancia_objetivo
    salida = Kp * error          <- positivo = adelante (esta muy lejos), negativo = atras

Antes de correrlo:
  1. pip install djitellopy opencv-contrib-python
  2. Conecta tu computadora al WiFi del Tello (aparece como TELLO-XXXXX)
  3. Imprime un ArUco (diccionario 4x4_50, ID 0) y MIDE su lado real en cm. Pegalo en una pared
     o sostenlo con un companero a la altura del dron.
  4. Primero corre con MODO_CALIBRACION = True (el dron NO vuela) para obtener FOCAL_PX.
"""

from djitellopy import Tello
import cv2
import csv
import time

# PARAMETROS
LADO_REAL_CM = 15.0          # TODO 1: mide el lado de tu marcador impreso (solo lo negro, en cm)
DISTANCIA_OBJETIVO_CM = 100
FOCAL_PX = 920.0             # TODO 2: calibrala con MODO_CALIBRACION (el valor de aqui es solo aproximado)
KP = 0.0                     # TODO 4: velocidad (rc) por cada cm de error
VELOCIDAD_MAXIMA = 30
TOLERANCIA_CM = 5
DURACION_SEGUNDOS = 40
ID_MARCADOR = 0
DISTANCIA_CALIBRACION_CM = 100  # a que distancia (medida con flexometro) pones el marcador al calibrar

# Ponlo en True para NO volar: pon el marcador a DISTANCIA_CALIBRACION_CM y lee el FOCAL_PX sugerido.
MODO_CALIBRACION = True


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


# --- Deteccion de ArUco (ya esta lista; solo lee como se usa) ---
diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
detector = cv2.aruco.ArucoDetector(diccionario, cv2.aruco.DetectorParameters())


def lado_marcador_px(frame):
    """Regresa (lado en pixeles, centro_x) del marcador ID_MARCADOR, o (None, None) si no lo ve."""
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    esquinas, ids, _ = detector.detectMarkers(gris)
    if ids is None:
        return None, None
    for esquina, id_ in zip(esquinas, ids.flatten()):
        if id_ == ID_MARCADOR:
            puntos = esquina[0]  # 4 esquinas (x, y)
            lados = [((puntos[i] - puntos[(i + 1) % 4]) ** 2).sum() ** 0.5 for i in range(4)]
            return sum(lados) / 4, puntos[:, 0].mean()
    return None, None


tello = Tello()
tello.connect()
print(f"Bateria: {tello.get_battery()}%")
tello.streamon()
lector = tello.get_frame_read()
time.sleep(2)  # espera a que llegue el primer cuadro de video

if MODO_CALIBRACION:
    # TODO 2: con el marcador a DISTANCIA_CALIBRACION_CM, despeja FOCAL_PX de la formula:
    #   FOCAL_PX = lado_en_pixeles * distancia_real / LADO_REAL_CM
    # Imprimelo, anota el valor estable y ponlo arriba. Luego cambia MODO_CALIBRACION a False.
    print("Calibrando. Presiona 'q' en la ventana de video para terminar.")
    while True:
        frame = lector.frame
        lado_px, _ = lado_marcador_px(frame)
        if lado_px is not None:
            focal_sugerida = 0  # <- TODO 2: calculala aqui
            print(f"lado: {lado_px:.1f} px   FOCAL_PX sugerido: {focal_sugerida:.1f}")
        cv2.imshow("Tello", frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    tello.streamoff()
    cv2.destroyAllWindows()
    raise SystemExit

registro = []  # filas: tiempo, distancia_cm, error_cm, salida

try:
    tello.takeoff()
    time.sleep(1)
    inicio = time.time()

    while (time.time() - inicio) < DURACION_SEGUNDOS:
        frame = lector.frame
        lado_px, _ = lado_marcador_px(frame)

        if lado_px is None:
            # TODO 5: que debe hacer el dron si NO ve el marcador? (pista: no adivines, ve la pregunta 4)
            velocidad = 0
            distancia_cm = float("nan")
            error_cm = float("nan")
        else:
            # TODO 3: calcula la distancia con la formula pinhole
            distancia_cm = 0

            # TODO 4: error y salida P (limitada a +-VELOCIDAD_MAXIMA). Si |error| <= TOLERANCIA_CM, salida = 0
            error_cm = 0
            velocidad = 0

        tello.send_rc_control(0, int(velocidad), 0, 0)
        registro.append([round(time.time() - inicio, 3), distancia_cm, error_cm, velocidad])

        cv2.putText(frame, f"dist: {distancia_cm:.0f} cm", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Tello", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' = aterrizar
            break

    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(1)
finally:
    try:
        tello.send_rc_control(0, 0, 0, 0)
        tello.land()
        tello.streamoff()
    except Exception:
        pass
    cv2.destroyAllWindows()

with open("log_05_aruco.csv", "w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(["tiempo_s", "distancia_cm", "error_cm", "salida_velocidad"])
    escritor.writerows(registro)
print("Log guardado: log_05_aruco.csv  (grafica con: python graficar_csv.py log_05_aruco.csv)")

# PREGUNTAS PARA PENSAR
#  1. Mueve el marcador hacia ti y alejalo. El dron lo sigue? Con que retardo? De que depende?
#  2. La camara toma ~30 cuadros por segundo, el sensor ToF/estado ~10 veces por segundo. Cual
#     realimentacion es mas rapida? Afecta eso el Kp maximo que puedes usar sin oscilar?
#  3. Que le pasa a la distancia medida si el marcador esta inclinado (no de frente)? Es un error
#     de medicion o de control?
#  4. Si pierdes el marcador, que es mas seguro: quedarte quieto, seguir con la ultima velocidad,
#     o aterrizar? Por que? Cuanto tiempo esperarias?
#  5. RETO EXTRA: tambien centra el marcador en la imagen girando el dron (yaw). Es OTRO
#     controlador P: error = centro_x_marcador - centro_x_imagen (la imagen mide 960 px de ancho).
#  6. RETO EXTRA 2: agrega un limite para que el dron nunca se acerque a menos de 50 cm.
