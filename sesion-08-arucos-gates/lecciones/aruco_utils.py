"""Funciones compartidas para detectar marcadores ArUco 4x4_50."""

import cv2
import numpy as np


def crear_detector():
    """Crea un detector compatible con versiones nuevas y anteriores de OpenCV."""
    if not hasattr(cv2, "aruco"):
        raise RuntimeError(
            "No encuentro cv2.aruco. Instala opencv-contrib-python en este entorno."
        )

    aruco = cv2.aruco
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    if hasattr(aruco, "DetectorParameters"):
        parametros = aruco.DetectorParameters()
    else:
        parametros = aruco.DetectorParameters_create()

    if hasattr(aruco, "ArucoDetector"):
        return ("nuevo", aruco.ArucoDetector(diccionario, parametros))
    return ("anterior", (diccionario, parametros))


def detectar_marcadores(frame, detector):
    """Regresa marcadores, esquinas e IDs detectados en un frame BGR."""
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    version, objeto = detector
    if version == "nuevo":
        esquinas, ids, rechazados = objeto.detectMarkers(gris)
    else:
        diccionario, parametros = objeto
        esquinas, ids, rechazados = cv2.aruco.detectMarkers(
            gris, diccionario, parameters=parametros
        )

    marcadores = []
    if ids is not None:
        for esquina, id_marcador in zip(esquinas, ids.flatten()):
            puntos = esquina.reshape(4, 2).astype(float)
            lados = [
                float(np.linalg.norm(puntos[i] - puntos[(i + 1) % 4]))
                for i in range(4)
            ]
            marcadores.append(
                {
                    "id": int(id_marcador),
                    "centro_x": float(puntos[:, 0].mean()),
                    "centro_y": float(puntos[:, 1].mean()),
                    "lado_px": sum(lados) / 4,
                    "esquinas": esquina,
                }
            )
    return marcadores, esquinas, ids
