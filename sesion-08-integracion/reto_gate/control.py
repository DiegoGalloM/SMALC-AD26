# ============================================================
#  control.py — EL CONTROL P: cuánto corregir
# ============================================================
#  Aquí juntas lo de la Sesión 5 (control P) y la Sesión 6 (el error respecto al centro).
#  Pruébalo con:  paso2_control.py

KP_GIRO = 0.15  # cuánto gira por cada pixel de error horizontal
KP_ALTURA = 0.20  # cuánto sube por cada pixel de error vertical
VELOCIDAD_MAXIMA = 25  # ninguna corrección pasa de aquí (seguridad)


def limitar(valor, maximo):
    """Ya está hecha: deja el valor entre -maximo y +maximo."""
    return max(-maximo, min(maximo, valor))


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea)
# ¿Qué tan lejos está la gate del centro de la foto, de izquierda a derecha?
# Positivo = la gate está a la DERECHA.
def error_horizontal(centro_x, ancho_foto):
    # Pista: return centro_x - ancho_foto // 2
    return 0


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea)
# ¿Qué tan lejos está la gate del centro de la foto, de arriba a abajo?
# Positivo = la gate está ARRIBA del centro (el dron tiene que subir).
def error_vertical(centro_y, alto_foto):
    # Pista: return alto_foto // 2 - centro_y
    return 0


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): el control P de la Sesión 5
def control_p(error, kp):
    # Pista: salida = kp * error, limitada a VELOCIDAD_MAXIMA
    #        return limitar(kp * error, VELOCIDAD_MAXIMA)
    return 0
