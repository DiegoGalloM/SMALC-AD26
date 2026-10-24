# EJEMPLO DE MISIÓN FINAL — Dron bailarín
# Una coreografía: cada paso es un estado que dura unos segundos (como el semáforo).
#   SUBIENDO 2 s -> GIRANDO 4 s -> BAJANDO 2 s -> DERECHA 2 s -> IZQUIERDA 2 s -> ATERRIZANDO
# No necesita ver colores, así que es la más fácil de probar en el Tello.
# Para correrlo: cópialo a la carpeta lecciones/ (ahí está dron.py).

from dron import Dron

MODO = "simulador"  # "simulador", "camara", "tello_sin_volar" o "tello"

dron = Dron(MODO, mundo="vacio")
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
            estado = "SUBIENDO"

    elif estado == "SUBIENDO":
        dron.subir()
        if s.segundos > 2:
            estado = "GIRANDO"

    elif estado == "GIRANDO":
        dron.girar()
        if s.segundos > 4:
            estado = "BAJANDO"

    elif estado == "BAJANDO":
        dron.bajar()
        if s.segundos > 2:
            estado = "DERECHA"

    elif estado == "DERECHA":
        dron.derecha()
        if s.segundos > 2:
            estado = "IZQUIERDA"

    elif estado == "IZQUIERDA":
        dron.izquierda()
        if s.segundos > 2:
            estado = "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        if not s.en_el_aire:
            estado = "EN_TIERRA"
