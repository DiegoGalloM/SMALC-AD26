# ============================================================
#  blu_funciones.py — TUS funciones para rescatar a Blu
# ============================================================
#  Blu es AZUL: para encontrarlo usas lo mismo que en la gate azul.
#  Aquí hay 7 funciones por completar (busca ✏️). Casi todas son de 1 o 2 líneas.
#
#     👀 Los ojos      1) mascara_azul      2) encontrar_a_blu     3) centro_de
#     🎯 El control    4) calcular_error    5) control_p
#     📏 La distancia  6) distancia_a_blu   7) estoy_a_un_metro
#
#  Pruébalas con:  blu_probar_funciones.py   (te dice ✅ o ❌ en cada una)

import cv2

# ---------------- AJUSTES ----------------
AZUL_BAJO = (100, 120, 50)     # el azul de Blu en HSV (con el staff: calíbralo con la herramienta de la Sesión 4)
AZUL_ALTO = (130, 255, 255)
AREA_MINIMA = 600              # manchas más chicas que esto son ruido

ANCHO_FOTO, ALTO_FOTO = 640, 480   # tamaño de la foto que entrega el dron

KP_GIRO = 0.08                 # cuánto gira por cada pixel de error horizontal
KP_ALTURA = 0.18               # cuánto sube por cada pixel de error vertical
KP_AVANCE = 0.4                # cuánto avanza por cada cm que le falta para llegar
VELOCIDAD_MAXIMA = 25          # ninguna corrección pasa de aquí (seguridad)

ANCHO_DE_BLU_CM = 20           # ¡mídelo! ancho REAL de la parte azul de Blu, en cm
FOCAL = 610                    # el "zoom" de la cámara del Tello (ya está medido)
DISTANCIA_DE_RESCATE = 100     # cm: el rescate se hace a un metro de Blu
TOLERANCIA_DISTANCIA = 15      # cm: nadie se queda en 100 exactos; entre 85 y 115 cuenta


# ============================================================
#  👀 LOS OJOS (Sesiones 4 y 6)
# ============================================================

# ✏️ 1) Una imagen en blanco y negro: BLANCO donde hay azul, NEGRO en todo lo demás.
def mascara_azul(foto):
    # Pista: son los dos pasos de siempre (Sesión 4).
    #   a) La foto viene en BGR: conviértela a HSV con  cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    #   b) Quédate solo con los pixeles ENTRE AZUL_BAJO y AZUL_ALTO con  cv2.inRange(...)
    hsv = None
    mascara = None
    return mascara


def mancha_mas_grande(mascara):
    """Ya está hecha: la mancha blanca más grande de la máscara, como (x, y, ancho, alto, area).
    Si la máscara está toda negra, regresa None."""
    if mascara is None:
        return None
    # findContours encuentra el BORDE de cada mancha blanca:
    #   RETR_EXTERNAL       -> solo el borde de afuera (si la mancha tiene huecos, los ignora)
    #   CHAIN_APPROX_SIMPLE -> guarda solo las esquinas del borde, no cada pixel (ahorra memoria)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contornos) == 0:
        return None
    mayor = max(contornos, key=cv2.contourArea)       # el borde que encierra más área
    x, y, ancho, alto = cv2.boundingRect(mayor)       # el rectángulo que lo encierra
    return x, y, ancho, alto, cv2.contourArea(mayor)


# ✏️ 2) El rectángulo (x, y, ancho, alto) que encierra a Blu. Si no hay Blu, regresa None.
def encontrar_a_blu(mascara):
    mancha = mancha_mas_grande(mascara)
    if mancha is None:
        return None  # la máscara está toda negra: no hay nada azul
    x, y, ancho, alto, area = mancha
    # Pista: la mancha más grande no siempre es Blu: si es muy chiquita, es ruido de la cámara.
    #   a) Si su area es menor que AREA_MINIMA, no es Blu: regresa None.
    #   b) Si no, sí es Blu: regresa solo el rectángulo (x, y, ancho, alto), SIN el área.
    return None


# ✏️ 3) El punto que está justo en medio del rectángulo.
def centro_de(caja):
    x, y, ancho, alto = caja  # (x, y) es la esquina de ARRIBA a la IZQUIERDA
    # Pista: desde esa esquina, ¿cuánto hay que caminar a la derecha y cuánto hacia abajo
    #        para quedar en medio? Usa // para que el resultado sea un número entero.
    centro_x = 0
    centro_y = 0
    return centro_x, centro_y


# ============================================================
#  🎯 EL CONTROL (Sesiones 5 y 6)
# ============================================================

# ✏️ 4) ¿Qué tan lejos está Blu del centro de la foto?
#       error_x POSITIVO = Blu está a la DERECHA.    error_y POSITIVO = Blu está ARRIBA.
def calcular_error(centro_x, centro_y):
    # Pista: error = dónde ESTÁ  menos  dónde lo QUIERO. Lo quieres en el centro de la foto,
    #        que mide ANCHO_FOTO x ALTO_FOTO.
    #        ¡Ojo con error_y! En una imagen la y crece hacia ABAJO: ¿qué tienes que restarle a qué
    #        para que salga positivo cuando Blu está arriba?
    error_x = 0
    error_y = 0
    return error_x, error_y


def limitar(valor, maximo):
    """Ya está hecha: deja el valor entre -maximo y +maximo."""
    return max(-maximo, min(maximo, valor))


# ✏️ 5) El control P: convierte un error en una velocidad.
def control_p(error, kp):
    # Pista: error grande -> corrección grande; error chico -> corrección chica. Eso es una multiplicación.
    #        Y por seguridad, el resultado nunca debe pasar de VELOCIDAD_MAXIMA: usa limitar().
    return 0


# ============================================================
#  📏 LA DISTANCIA (Sesión 8: mientras más cerca, más grande se ve)
# ============================================================

# ✏️ 6) ¿A cuántos cm está Blu, si en la foto se ve de `ancho_en_pixeles` de ancho?
def distancia_a_blu(ancho_en_pixeles):
    # Pista: a 1 metro, Blu se ve de unos 122 pixeles de ancho. A 2 metros, de 61. A 4 metros, de 30.
    #        Si la distancia se duplica, los pixeles se parten a la mitad: los pixeles van DIVIDIENDO.
    #        Arriba va lo que nunca cambia: ANCHO_DE_BLU_CM multiplicado por FOCAL.
    return 0


# ✏️ 7) True si el dron ya está a un metro de Blu (con un poquito de tolerancia). Si no, False.
def estoy_a_un_metro(distancia):
    # Pista: ¿cuántos cm le sobran o le faltan para DISTANCIA_DE_RESCATE? Esa diferencia, sin importar
    #        su signo (abs), tiene que ser menor que TOLERANCIA_DISTANCIA.
    return False
