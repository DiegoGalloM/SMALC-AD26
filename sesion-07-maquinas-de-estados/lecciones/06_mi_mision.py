# ============================================================
#  MISIÓN FINAL — ¡Diseñen el cerebro de su dron!
# ============================================================
#  1) Dibujen en papel su máquina de estados: bolitas (estados) y flechas (cuándo cambia).
#  2) Escríbanla aquí abajo. Prueben en este orden:
#        "simulador"  ->  "tello_sin_volar"  ->  "tello" (¡solo con el staff!)
#  3) Demo: expliquen su diagrama al grupo y vuelen su misión.
#
#  Teclas: "t" despega (en el ejemplo), "e" aterriza en cualquier momento, q = salir.

from dron import Dron

MODO = "simulador"  # "simulador", "camara", "tello_sin_volar" o "tello"
COLOR = "verde"  # el color que sigue su dron: "rojo", "verde" o "azul"

dron = Dron(MODO, color=COLOR)
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)

    # SEGURIDAD: con la tecla "e" el dron aterriza desde cualquier estado (no lo quiten)
    if s.tecla == "e" and s.en_el_aire:
        estado = "ATERRIZANDO"

    # ===================== SU MÁQUINA DE ESTADOS =====================
    # Ejemplo para empezar: despega, busca el color, lo sigue 10 segundos y aterriza.
    # ¡Cámbienlo por su propia misión!
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

    elif estado == "SIGUIENDO":
        dron.seguir_color()
        if not s.veo_color:
            estado = "BUSCANDO"
        if s.segundos > 10:
            estado = "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        if not s.en_el_aire:
            estado = "EN_TIERRA"
    # =================================================================


# ---------------------------------------------------------------------------
# MENÚ: lo que puede HACER su dron (una acción por estado)
#   dron.quieto()        dron.despegar()      dron.aterrizar()
#   dron.avanzar()       dron.retroceder()    dron.izquierda()     dron.derecha()
#   dron.subir()         dron.bajar()         dron.girar()
#   dron.seguir_color()  dron.acercarse()     dron.rescatar()      dron.patrullar()
#   dron.regresar_a_base()   <- solo funciona en el simulador
#
# MENÚ: lo que puede SABER su dron (para sus flechas / transiciones)
#   s.tecla == "x"     s.segundos > 3     s.en_el_aire     s.altura     s.bateria
#   s.veo_color        s.centrado         s.cerca          s.error_x
#   s.veo_rojo         s.veo_verde        s.veo_azul       s.faltan
#
# IDEAS DE MISIONES
#   🚑 Rescate:        busca el color, acércate, rescata y aterriza.
#   🚦 Dron obediente: tarjetas de colores: verde = avanza 2 s, azul = gira, rojo = aterriza.
#   🛡️ Guardaespaldas: sigue el color; si lo pierde, búscalo; si en 10 s no lo encuentra, aterriza.
#   🔭 Explorador:     patrulla hasta ver rojo; entonces se acerca y aterriza frente a él.
#   💃 Dron bailarín:  una coreografía por tiempo: sube, gira, baja, derecha, izquierda...
#   💡 ¡O inventen la suya!
# ---------------------------------------------------------------------------
