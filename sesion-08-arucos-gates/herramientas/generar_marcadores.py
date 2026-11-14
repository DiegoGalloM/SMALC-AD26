"""Genera imágenes imprimibles para los marcadores ArUco de esta sesión."""

from pathlib import Path

import cv2
import numpy as np


def crear_marcador(diccionario, id_marcador, lado_px):
    aruco = cv2.aruco
    if hasattr(aruco, "generateImageMarker"):
        return aruco.generateImageMarker(diccionario, id_marcador, lado_px, borderBits=1)
    imagen = cv2.aruco.drawMarker(diccionario, id_marcador, lado_px, borderBits=1)
    return imagen


def main():
    salida = Path(__file__).resolve().parents[1] / "marcadores"
    salida.mkdir(parents=True, exist_ok=True)
    diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    for id_marcador in (0, 1, 2):
        marcador = crear_marcador(diccionario, id_marcador, 700)
        hoja = 255 * np.ones((820, 700), dtype="uint8")
        hoja[:700, :] = marcador
        cv2.putText(
            hoja,
            f"ID {id_marcador} - ArUco 4x4_50",
            (150, 770),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            0,
            2,
        )
        ruta = salida / f"aruco_id_{id_marcador}.png"
        cv2.imwrite(str(ruta), hoja)
        print(f"Guardado: {ruta}")


if __name__ == "__main__":
    if not hasattr(cv2, "aruco"):
        raise SystemExit("Instala opencv-contrib-python para generar los marcadores.")
    main()
