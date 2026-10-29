"""
conexion.py — conectar el dron, leer su cámara y dibujar la pantalla (ya está hecho: no necesitas modificarlo)

    tello = conectar("simulador")   o   conectar("tello")
    foto = leer_foto(tello)
    tecla = mostrar(tello, foto, mascara, estado, gate)
    terminar(tello)
"""

import atexit
import unicodedata

import cv2
import numpy as np

ANCHO, ALTO = 640, 480
VENTANA = "Reto de la gate (t = despegar, e = aterrizar, q = salir)"


def conectar(modo):
    """Regresa un Tello listo para usar: el de mentiras ("simulador") o el de verdad ("tello")."""
    if modo == "simulador":
        from simulador import TelloSimulado
        tello = TelloSimulado()
    elif modo == "tello":
        from djitellopy import Tello
        tello = Tello()
        atexit.register(terminar, tello)  # si el programa truena, el dron aterriza
    else:
        raise SystemExit('MODO debe ser "simulador" o "tello"')
    tello.connect()
    print(f"Batería: {tello.get_battery()}%")
    tello.streamon()
    tello._es_simulado = modo == "simulador"
    cv2.namedWindow(VENTANA)
    return tello


def leer_foto(tello):
    """Una foto de la cámara del dron, en BGR y de 640 x 480 (como en la Sesión 4)."""
    frame = tello.get_frame_read().frame
    if frame is None:
        return np.zeros((ALTO, ANCHO, 3), np.uint8)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # el Tello entrega RGB y OpenCV usa BGR
    return cv2.resize(frame, (ANCHO, ALTO))


def _ascii(texto):
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def mostrar(tello, foto, mascara, estado, gate):
    """Dibuja todo en la ventana y regresa la tecla que presionaste ("" si ninguna)."""
    camara = foto.copy()
    cx, cy = ANCHO // 2, ALTO // 2
    cv2.drawMarker(camara, (cx, cy), (255, 255, 255), cv2.MARKER_CROSS, 26, 2)
    if gate is not None:
        x, y, w, h = [int(v) for v in gate]
        centro = (x + w // 2, y + h // 2)
        cv2.rectangle(camara, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.circle(camara, centro, 7, (0, 0, 255), -1)
        cv2.line(camara, (cx, cy), centro, (255, 0, 0), 2)
        cv2.putText(camara, f"ancho gate: {w} px", (10, ALTO - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(camara, "no veo la gate", (10, ALTO - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 255), 2, cv2.LINE_AA)

    # El estado, grande y arriba
    cv2.rectangle(camara, (0, 0), (ANCHO, 50), (0, 0, 0), -1)
    cv2.putText(camara, _ascii(estado), (12, 36), cv2.FONT_HERSHEY_DUPLEX, 1.1, (57, 255, 20), 2, cv2.LINE_AA)
    cv2.putText(camara, f"bateria {tello.get_battery()}%", (ANCHO - 170, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (200, 200, 200), 1, cv2.LINE_AA)

    # La máscara chiquita en la esquina
    mini = cv2.resize(cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR), (160, 120))
    camara[58:178, ANCHO - 168:ANCHO - 8] = mini
    cv2.rectangle(camara, (ANCHO - 168, 58), (ANCHO - 8, 178), (200, 200, 200), 1)

    # A la derecha: el mapa (simulador) o la máscara grande (Tello real)
    if getattr(tello, "_es_simulado", False):
        derecha = np.full((ALTO, 420, 3), (23, 17, 13), np.uint8)
        derecha[:420] = tello.mapa(420)
        if tello.mensaje:
            color = (57, 255, 20) if tello.resultado == "cruzo" else (60, 60, 255)
            cv2.putText(derecha, _ascii(tello.mensaje), (10, 455), cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 2, cv2.LINE_AA)
    else:
        derecha = np.full((ALTO, 420, 3), (23, 17, 13), np.uint8)
        derecha[60:375] = cv2.resize(cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR), (420, 315))
        cv2.putText(derecha, "mascara del azul", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(derecha, f"altura: {tello.get_distance_tof()} cm", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (200, 200, 200), 1, cv2.LINE_AA)

    cv2.imshow(VENTANA, np.hstack([camara, derecha]))
    k = cv2.waitKey(30 if getattr(tello, "_es_simulado", False) else 1)
    if cv2.getWindowProperty(VENTANA, cv2.WND_PROP_VISIBLE) < 1:
        return "q"
    return chr(k).lower() if 0 <= k < 256 else ""


def terminar(tello):
    """Detiene y aterriza el dron (si está volando) y cierra todo."""
    if getattr(tello, "_terminado", False):
        return
    tello._terminado = True
    try:
        tello.send_rc_control(0, 0, 0, 0)
        if tello.is_flying:
            tello.land()
        tello.streamoff()
    except Exception:
        pass
    cv2.destroyAllWindows()
    resultado = getattr(tello, "mensaje", "")
    if resultado:
        print(f"\nResultado: {resultado}")
