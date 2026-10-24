# EJEMPLO DE MISIÓN FINAL — Rescate
# Busca el color, se acerca, rescata y, cuando ya no falta nadie, aterriza.
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
            estado = "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        dron.acercarse()
        if not s.veo_color:
            estado = "BUSCANDO"
        elif s.cerca:
            estado = "RESCATANDO"

    elif estado == "RESCATANDO":
        dron.rescatar()
        if not s.cerca:
            if s.faltan > 0:
                estado = "BUSCANDO"
            else:
                estado = "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        if not s.en_el_aire:
            estado = "EN_TIERRA"
