"""LECCIÓN 1 — Ver IDs ArUco con la cámara del Tello. Este programa no vuela."""

import time

import cv2
from djitellopy import Tello

from aruco_utils import crear_detector, detectar_marcadores


def main():
    tello = Tello()
    streaming = False
    try:
        tello.connect()
        print(f"Tello conectado. Batería: {tello.get_battery()}%")
        tello.streamon()
        streaming = True
        lector = tello.get_frame_read()
        detector = crear_detector()
        time.sleep(2)

        while True:
            frame_rgb = lector.frame
            if frame_rgb is None:
                continue
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            marcadores, esquinas, ids = detectar_marcadores(frame, detector)

            alto, ancho = frame.shape[:2]
            centro_imagen = (ancho // 2, alto // 2)
            cv2.drawMarker(
                frame, centro_imagen, (255, 255, 255), cv2.MARKER_CROSS, 28, 2
            )
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)

            for marcador in marcadores:
                x = int(marcador["centro_x"])
                y = int(marcador["centro_y"])
                cv2.circle(frame, (x, y), 6, (0, 255, 255), -1)
                cv2.putText(
                    frame,
                    f"ID {marcador['id']} | lado {marcador['lado_px']:.0f} px",
                    (max(10, x - 100), max(25, y - 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2,
                )

            texto = "Marcador detectado" if marcadores else "Buscando marcador..."
            cv2.putText(
                frame,
                texto + " | q = salir (sin despegar)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0) if marcadores else (0, 0, 255),
                2,
            )
            cv2.imshow("Leccion 1 - ArUco", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        if streaming:
            try:
                tello.streamoff()
            except Exception:
                pass
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
