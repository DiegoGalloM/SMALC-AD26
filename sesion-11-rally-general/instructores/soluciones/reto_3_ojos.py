# ============================================================
#  RETO 3 — Los ojos del dron                      150 puntos
# ============================================================
#  Blu es AZUL. Completa estas 3 funciones (busca ✏️) para que el dron lo encuentre en una foto.
#  Después córrelo con ▶: el juez las revisa y te dice ✅ o ❌ en cada una.
#  ¡Ojo! Estas funciones son los ojos del Reto 6 (el jefe final).
#
#  📚 ¿Dónde lo vimos?
#     Sesión 4:  lecciones/05_hsv_mascaras.py   (cvtColor a HSV  e  inRange)
#     Sesión 4:  lecciones/06_contornos.py      (manchas grandes y ruido)
#     Sesión 6:  lecciones/01_el_centro.py      (el centro de un rectángulo)
#     Sesión 10: blu_funciones.py               (funciones 1, 2 y 3)

import cv2

AZUL_BAJO = (100, 120, 50)     # el azul de Blu en HSV
AZUL_ALTO = (130, 255, 255)
AREA_MINIMA = 600              # manchas más chicas que esto son ruido


# ✏️ 1) Una imagen en blanco y negro: BLANCO donde hay azul, NEGRO en todo lo demás.
def mascara_azul(foto):
    # Pista: los dos pasos de siempre de la Sesión 4:
    #   a) la foto viene en BGR: conviértela con  cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    #   b) quédate con los pixeles entre AZUL_BAJO y AZUL_ALTO con  cv2.inRange(hsv, ..., ...)
    hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, AZUL_BAJO, AZUL_ALTO)
    return mascara


def mancha_mas_grande(mascara):
    """Ya está hecha: la mancha blanca más grande de la máscara, como (x, y, ancho, alto, area).
    Si la máscara está toda negra, regresa None."""
    if mascara is None:
        return None
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contornos) == 0:
        return None
    mayor = max(contornos, key=cv2.contourArea)
    x, y, ancho, alto = cv2.boundingRect(mayor)
    return x, y, ancho, alto, cv2.contourArea(mayor)


# ✏️ 2) El rectángulo (x, y, ancho, alto) que encierra a Blu. Si no hay Blu, regresa None.
def encontrar_a_blu(mascara):
    mancha = mancha_mas_grande(mascara)
    if mancha is None:
        return None  # la máscara está toda negra: no hay nada azul
    x, y, ancho, alto, area = mancha
    # Pista: a) si el area es menor que AREA_MINIMA, es ruido: regresa None
    #        b) si no, regresa solo  x, y, ancho, alto   (SIN el área)
    if area < AREA_MINIMA:
        return None
    return x, y, ancho, alto


# ✏️ 3) El punto que está justo en medio del rectángulo.
def centro_de(caja):
    x, y, ancho, alto = caja  # (x, y) es la esquina de ARRIBA a la IZQUIERDA
    # Pista: desde la esquina camina la MITAD del ancho a la derecha y la MITAD del alto hacia abajo.
    #        Usa // para que salga un número entero.
    centro_x = x + ancho // 2
    centro_y = y + alto // 2
    return centro_x, centro_y


# ---------- No lo modifiques: cuando corres ESTE archivo con ▶, el juez revisa tus funciones ----------
if __name__ == "__main__":
    import rally
    rally.revisar(3)
