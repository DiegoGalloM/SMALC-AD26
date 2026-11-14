# ============================================================
#  RETO 4 — El control                             150 puntos
# ============================================================
#  Ya sabes DÓNDE está Blu en la foto. Ahora: ¿cuánto se tiene que mover el dron?
#  Completa estas 4 funciones (busca ✏️) y córrelo con ▶: el juez las revisa.
#  ¡Ojo! Estas funciones son el control del Reto 6 (el jefe final).
#
#  📚 ¿Dónde lo vimos?
#     Sesión 6:  lecciones/02_medir_el_error.py   (error = dónde está - dónde lo quiero)
#     Sesión 5:  demos/ejercicio_P.py             (output = KP * error)
#     Sesión 10: blu_funciones.py                 (funciones 4, 5, 6 y 7)

ANCHO_FOTO, ALTO_FOTO = 640, 480   # tamaño de la foto del dron
VELOCIDAD_MAXIMA = 25              # ninguna corrección pasa de aquí (seguridad)

ANCHO_DE_BLU_CM = 20               # ancho REAL de la parte azul de Blu, en cm
FOCAL = 610                        # el "zoom" de la cámara del Tello (ya está medido)
DISTANCIA_DE_RESCATE = 100         # cm: el rescate se hace a un metro de Blu
TOLERANCIA_DISTANCIA = 15          # cm: entre 85 y 115 cuenta como "a un metro"


# ✏️ 1) ¿Qué tan lejos está Blu del centro de la foto?
#       error_x POSITIVO = Blu está a la DERECHA.    error_y POSITIVO = Blu está ARRIBA.
def calcular_error(centro_x, centro_y):
    # Pista: error = dónde ESTÁ  menos  dónde lo QUIERO (el centro: ANCHO_FOTO // 2, ALTO_FOTO // 2).
    #        ¡Ojo con error_y! En una imagen la y crece hacia ABAJO: aquí va al revés,
    #        (ALTO_FOTO // 2) menos centro_y.
    error_x = 0
    error_y = 0
    return error_x, error_y


def limitar(valor, maximo):
    """Ya está hecha: deja el valor entre -maximo y +maximo."""
    return max(-maximo, min(maximo, valor))


# ✏️ 2) El control P: convierte un error en una velocidad.
def control_p(error, kp):
    # Pista: velocidad = kp * error   (como en la Sesión 5)
    #        y por seguridad regrésala pasada por  limitar(velocidad, VELOCIDAD_MAXIMA)
    return 0


# ✏️ 3) ¿A cuántos cm está Blu, si en la foto se ve de `ancho_en_pixeles` de ancho?
def distancia_a_blu(ancho_en_pixeles):
    # Pista: mientras más lejos, más chico se ve.  distancia = ANCHO_DE_BLU_CM * FOCAL / ancho_en_pixeles
    return 0


# ✏️ 4) True si el dron ya está a un metro de Blu (con tolerancia). Si no, False.
def estoy_a_un_metro(distancia):
    # Pista: la diferencia entre distancia y DISTANCIA_DE_RESCATE, sin importar el signo (abs),
    #        tiene que ser menor que TOLERANCIA_DISTANCIA.    return abs(...) < ...
    return False


# ---------- No lo modifiques: cuando corres ESTE archivo con ▶, el juez revisa tus funciones ----------
if __name__ == "__main__":
    import rally
    rally.revisar(4)
