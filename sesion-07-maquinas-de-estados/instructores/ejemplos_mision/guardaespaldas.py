# EJEMPLO DE MISIÓN FINAL — Guardaespaldas
# Sigue el color. Si lo pierde, lo busca girando. Si en 10 segundos no lo encuentra, aterriza.
# Si el color se acerca demasiado, el dron retrocede para no chocar.
# Para correrlo: cópialo a la carpeta lecciones/ (ahí está dron.py).

from dron import Dron

MODO = "simulador"  # "simulador", "camara", "tello_sin_volar" o "tello"
COLOR = "verde"

dron = Dron(MODO, color=COLOR)
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)

    if s.tecla == "e" and s.en_el_aire:
        estado = "ATERRIZANDO"

    if estado == "EN_TIERRA":
        dron.quieto()
        if s.tecla == "t":
            estado = "DESPEGANDO"

    elif estado == "DESPEGANDO":
        dron.despegar()
        if s.en_el_aire:
            estado = "BUSCANDO"

    elif estado == "BUSCANDO":
        dron.girar()
        if s.veo_color:
            estado = "SIGUIENDO"
        elif s.segundos > 10:
            estado = "ATERRIZANDO"

    elif estado == "SIGUIENDO":
        dron.seguir_color()
        if not s.veo_color:
            estado = "BUSCANDO"
        elif s.cerca:
            estado = "ALEJANDOSE"

    elif estado == "ALEJANDOSE":
        dron.retroceder()
        if not s.cerca:
            estado = "SIGUIENDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        if not s.en_el_aire:
            estado = "EN_TIERRA"
