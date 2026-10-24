# EJEMPLO DE MISIÓN FINAL — Dron obediente (tarjetas de colores)
# Un compañero le enseña tarjetas al dron:
#   verde = avanza 2 segundos     azul = gira 2 segundos     rojo = aterriza
# Para correrlo: cópialo a la carpeta lecciones/ (ahí está dron.py).

from dron import Dron

MODO = "simulador"  # "simulador", "camara", "tello_sin_volar" o "tello"

dron = Dron(MODO)
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
            estado = "ESPERANDO"

    elif estado == "ESPERANDO":
        dron.quieto()
        if s.veo_verde:
            estado = "AVANZANDO"
        elif s.veo_azul:
            estado = "GIRANDO"
        elif s.veo_rojo:
            estado = "ATERRIZANDO"

    elif estado == "AVANZANDO":
        dron.avanzar()
        if s.segundos > 2:
            estado = "ESPERANDO"

    elif estado == "GIRANDO":
        dron.girar()
        if s.segundos > 2:
            estado = "ESPERANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        if not s.en_el_aire:
            estado = "EN_TIERRA"
