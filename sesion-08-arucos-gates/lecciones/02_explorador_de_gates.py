"""LECCIÓN 2 — Proyecto final: busca y atraviesa gates con ArUco.

Con MODO_VUELO=False, el programa solo muestra los controles propuestos. Solo el
staff puede habilitar el vuelo con MODO_VUELO=True después de revisar el espacio.

Teclas: t = iniciar misión, q = detener y aterrizar.
"""

import time

import cv2
from djitellopy import Tello

from aruco_utils import crear_detector, detectar_marcadores

# CONFIGURACIÓN DE LA MISIÓN
RUTA_IDS = [0, 1, 2]  # ID de cada gate, en el orden que se deben atravesar
MODO_VUELO = False  # False = prueba; True = vuelo real (solo el staff)
BATERIA_MINIMA = 10

# AJUSTES PARA EL MONTAJE: el tamaño en píxeles depende de la cámara y la gate
TOLERANCIA_CENTRADO = 35  # píxeles desde el centro de la imagen
TOLERANCIA_REAJUSTE = 55  # margen mayor para evitar cambios de estado por ruido
TAMANO_PARA_CRUZAR = 170  # lado del marcador en píxeles; ajustar en la prueba
VELOCIDAD_GIRO_MAXIMA = 12
GANANCIA_GIRO = 0.05
VELOCIDAD_AVANCE = 10
VELOCIDAD_BUSQUEDA = 20
VELOCIDAD_SUBIDA = 60
VELOCIDAD_CORRECCION_VERTICAL = 20
GANANCIA_VERTICAL = 0.15
SEGUNDOS_SUBIDA = 2.0
SEGUNDOS_PARA_CRUZAR = 1.0
SEGUNDOS_BUSCANDO = 18.0  # permite una búsqueda girando de hasta casi 360 grados
SEGUNDOS_MAXIMOS_MISION = 45.0
INTERVALO_CONTROL = 0.05


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def marcador_con_id(marcadores, objetivo_id):
    for marcador in marcadores:
        if marcador["id"] == objetivo_id:
            return marcador
    return None


def main():
    tello = Tello()
    streaming = False
    despego = False
    try:
        tello.connect()
        bateria = tello.get_battery()
        print(f"Tello conectado. Batería: {bateria}%")
        tello.streamon()
        streaming = True
        lector = tello.get_frame_read()
        detector = crear_detector()
        time.sleep(2)

        estado = "ESPERA"
        indice_ruta = 0
        inicio_mision = None
        inicio_subida = None
        inicio_busqueda = None
        inicio_cruce = None
        frames_centrados = 0
        mensaje = "Presiona t para iniciar la prueba"

        while True:
            frame_rgb = lector.frame
            if frame_rgb is None:
                continue
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            marcadores, esquinas, ids = detectar_marcadores(frame, detector)
            alto, ancho = frame.shape[:2]
            centro_x = ancho // 2
            objetivo_id = RUTA_IDS[indice_ruta] if indice_ruta < len(RUTA_IDS) else None
            objetivo = marcador_con_id(marcadores, objetivo_id) if objetivo_id is not None else None
            ids_visibles = sorted(
                {m["id"] for m in marcadores if m["id"] in RUTA_IDS}
            )

            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)
            cv2.drawMarker(
                frame, (centro_x, alto // 2), (255, 255, 255), cv2.MARKER_CROSS, 28, 2
            )

            # Orden propuesta: izquierda/derecha, adelante/atrás, arriba/abajo, giro.
            rc = (0, 0, 0, 0)
            ahora = time.time()
            if estado == "SUBIR":
                if ahora - inicio_subida < SEGUNDOS_SUBIDA:
                    rc = (0, 0, VELOCIDAD_SUBIDA, 0)
                    mensaje = f"Subiendo: RC vertical {VELOCIDAD_SUBIDA} por {SEGUNDOS_SUBIDA:.0f} s"
                else:
                    estado = "BUSCAR"
                    inicio_busqueda = ahora
                    mensaje = f"Altura alcanzada; buscando ID {objetivo_id}"

            elif estado == "BUSCAR":
                if objetivo is not None:
                    estado = "ALINEAR"
                    frames_centrados = 0
                    mensaje = f"Encontré ID {objetivo_id}; alineando"
                elif ahora - inicio_busqueda >= SEGUNDOS_BUSCANDO:
                    estado = "ATERRIZAR"
                    mensaje = "No encontré la gate a tiempo; aterrizando"
                else:
                    # Gira en el sitio y detecta todos los IDs de la ruta; solo
                    # se acerca al ID esperado para conservar el orden de gates.
                    rc = (0, 0, 0, VELOCIDAD_BUSQUEDA)
                    if ids_visibles:
                        mensaje = f"Veo IDs {ids_visibles}; girando para buscar ID {objetivo_id}"
                    else:
                        mensaje = f"Buscando ID {objetivo_id}; girando"

            elif estado == "ALINEAR":
                if objetivo is None:
                    estado = "BUSCAR"
                    inicio_busqueda = ahora
                    mensaje = f"ID {objetivo_id} perdido; buscando de nuevo"
                else:
                    error_x = objetivo["centro_x"] - centro_x
                    error_y = objetivo["centro_y"] - alto // 2
                    if (
                        abs(error_x) <= TOLERANCIA_CENTRADO
                        and abs(error_y) <= TOLERANCIA_CENTRADO
                    ):
                        frames_centrados += 1
                        if frames_centrados >= 5:
                            estado = "ACERCARSE"
                            mensaje = f"ID {objetivo_id} centrado; acercándose"
                    else:
                        frames_centrados = 0
                        giro = int(
                            limitar(GANANCIA_GIRO * error_x, -VELOCIDAD_GIRO_MAXIMA, VELOCIDAD_GIRO_MAXIMA)
                        )
                        subir = int(
                            limitar(
                                -GANANCIA_VERTICAL * error_y,
                                -VELOCIDAD_CORRECCION_VERTICAL,
                                VELOCIDAD_CORRECCION_VERTICAL,
                            )
                        )
                        rc = (0, 0, subir, giro)
                        mensaje = (
                            f"Alineando ID {objetivo_id}; "
                            f"error x = {error_x:.0f} px, error y = {error_y:.0f} px"
                        )

            elif estado == "ACERCARSE":
                if objetivo is None:
                    estado = "BUSCAR"
                    inicio_busqueda = ahora
                    mensaje = f"ID {objetivo_id} perdido; buscando de nuevo"
                else:
                    error_x = objetivo["centro_x"] - centro_x
                    error_y = objetivo["centro_y"] - alto // 2
                    if (
                        abs(error_x) > TOLERANCIA_REAJUSTE
                        or abs(error_y) > TOLERANCIA_REAJUSTE
                    ):
                        estado = "ALINEAR"
                        frames_centrados = 0
                        mensaje = "Me desvié del centro; realineando"
                    elif objetivo["lado_px"] >= TAMANO_PARA_CRUZAR:
                        estado = "CRUZAR"
                        inicio_cruce = ahora
                        mensaje = f"ID {objetivo_id} cerca; cruzando despacio"
                    else:
                        subir = int(
                            limitar(
                                -GANANCIA_VERTICAL * error_y,
                                -VELOCIDAD_CORRECCION_VERTICAL,
                                VELOCIDAD_CORRECCION_VERTICAL,
                            )
                        )
                        giro = int(
                            limitar(GANANCIA_GIRO * error_x, -VELOCIDAD_GIRO_MAXIMA, VELOCIDAD_GIRO_MAXIMA)
                        )
                        rc = (0, VELOCIDAD_AVANCE, subir, giro)
                        mensaje = (
                            f"Acercándose a ID {objetivo_id}; "
                            f"tamaño {objetivo['lado_px']:.0f} px, "
                            f"error y = {error_y:.0f} px"
                        )

            elif estado == "CRUZAR":
                if ahora - inicio_cruce < SEGUNDOS_PARA_CRUZAR:
                    rc = (0, VELOCIDAD_AVANCE, 0, 0)
                else:
                    indice_ruta += 1
                    if indice_ruta >= len(RUTA_IDS):
                        estado = "ATERRIZAR"
                        mensaje = "Ruta completada; aterrizando"
                    else:
                        estado = "BUSCAR"
                        inicio_busqueda = ahora
                        mensaje = f"Gate cruzada; buscando ID {RUTA_IDS[indice_ruta]}"

            elif estado == "ATERRIZAR":
                rc = (0, 0, 0, 0)
                if despego:
                    tello.send_rc_control(0, 0, 0, 0)
                    time.sleep(0.5)
                    tello.land()
                    despego = False
                estado = "FIN"

            elif estado == "FIN":
                rc = (0, 0, 0, 0)

            if inicio_mision is not None and estado not in ("ATERRIZAR", "FIN"):
                if ahora - inicio_mision >= SEGUNDOS_MAXIMOS_MISION:
                    estado = "ATERRIZAR"
                    rc = (0, 0, 0, 0)
                    mensaje = "Tiempo máximo alcanzado; aterrizando"

            if MODO_VUELO and despego:
                tello.send_rc_control(*rc)

            if objetivo is not None:
                cv2.circle(
                    frame,
                    (int(objetivo["centro_x"]), int(objetivo["centro_y"])),
                    6,
                    (0, 255, 255),
                    -1,
                )
                cv2.line(
                    frame,
                    (centro_x, alto // 2),
                    (int(objetivo["centro_x"]), int(objetivo["centro_y"])),
                    (255, 100, 0),
                    2,
                )

            id_texto = str(objetivo_id) if objetivo_id is not None else "fin"
            cv2.putText(
                frame,
                f"Estado: {estado} | ID objetivo: {id_texto}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                frame,
                mensaje,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
            )
            modo = "VUELO" if MODO_VUELO else "PRUEBA SIN VOLAR"
            cv2.putText(
                frame,
                f"{modo} | RC propuesto: {rc} | t=iniciar, q=salir",
                (10, alto - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            cv2.imshow("Proyecto final - Explorador de gates", frame)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("q"):
                break
            if tecla == ord("t") and estado == "ESPERA":
                if MODO_VUELO and bateria < BATERIA_MINIMA:
                    mensaje = f"Batería baja ({bateria}%). No se inicia el vuelo."
                else:
                    if MODO_VUELO:
                        tello.takeoff()
                        despego = True
                        time.sleep(1)
                    estado = "SUBIR"
                    inicio_mision = time.time()
                    inicio_subida = inicio_mision
                    mensaje = f"Subiendo: RC vertical {VELOCIDAD_SUBIDA} por {SEGUNDOS_SUBIDA:.0f} s"
            time.sleep(INTERVALO_CONTROL)

    finally:
        if despego:
            try:
                tello.send_rc_control(0, 0, 0, 0)
                time.sleep(0.5)
                tello.land()
            except Exception:
                pass
        if streaming:
            try:
                tello.streamoff()
            except Exception:
                pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
