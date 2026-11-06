# ============================================================
#  vision.py — LOS OJOS del dron: encontrar la gate azul
# ============================================================
#  Aquí juntas lo de la Sesión 4 (HSV, máscaras, contornos) y la Sesión 6 (el centro).
#  Pruébalo con:  paso1_vision.py

import cv2

# ✏️ Calibra el azul de TU gate con herramientas/calibrador_hsv.py de la Sesión 4
AZUL_BAJO = (100, 120, 50)
AZUL_ALTO = (130, 255, 255)
AREA_MINIMA = 800  # manchas más chicas que esto son ruido


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): la máscara del azul
def mascara_azul(foto):
    hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    # Esta máscara está vacía: cambia los dos (0, 0, 0) por AZUL_BAJO y AZUL_ALTO
    return cv2.inRange(hsv, (0, 0, 0), (0, 0, 0))


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): el rectángulo que encierra a la gate
def encontrar_gate(mascara):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidatos = [c for c in contornos if cv2.contourArea(c) > AREA_MINIMA]
    if not candidatos:
        return None  # no veo ninguna gate
    gate = max(candidatos, key=cv2.contourArea)  # me quedo con la más grande
    # Pista: return cv2.boundingRect(gate)      <- regresa (x, y, ancho, alto)
    return None


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): el centro del rectángulo
def centro_de(gate):
    x, y, ancho, alto = gate
    # Pista: el centro está a la MITAD del ancho y a la MITAD del alto (Sesión 6)
    #        return x + ancho // 2, y + alto // 2
    return x, y
