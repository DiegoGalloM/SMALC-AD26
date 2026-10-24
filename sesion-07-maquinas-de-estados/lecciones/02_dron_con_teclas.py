# ============================================================
#  LECCIÓN 2 — Un dron que obedece teclas
# ============================================================
#  El dron del simulador tiene 4 estados:
#
#                  "t"                  ya en el aire
#   EN_TIERRA ──────────► DESPEGANDO ──────────────► VOLANDO
#       ▲                                               │ "l"
#       └──────────── ATERRIZANDO ◄─────────────────────┘
#           ya no en el aire
#
#  Cada estado tiene DOS partes:
#    1) lo que HACE el dron   (ya está escrito: dron.despegar(), dron.quieto()...)
#    2) cuándo CAMBIA         (eso lo escribes tú)
#
#  Córrelo con ▶. Haz clic en la ventana del simulador y usa las teclas. q = salir.

from dron import Dron  # el cuerpo del dron (ya está hecho)

dron = Dron("simulador", mundo="vacio")
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)  # todo lo que el dron sabe ahora (s.tecla, s.en_el_aire, ...)

    # ===================== LÓGICA DE ESTADOS =====================
    if estado == "EN_TIERRA":
        dron.quieto()
        if s.tecla == "t":
            estado = "DESPEGANDO"

    elif estado == "DESPEGANDO":
        dron.despegar()
        # ✏️ COMPLETA: cuando ya esté en el aire (s.en_el_aire), cambia a "VOLANDO"

    elif estado == "VOLANDO":
        dron.quieto()  # flota en su lugar
        # ✏️ COMPLETA: si presionan la tecla "l", cambia a "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        # ✏️ COMPLETA: cuando ya NO esté en el aire, regresa a "EN_TIERRA"
        #    Pista:  if not s.en_el_aire:

    # ✏️ MINI-RETO 2: el estado GIRANDO (descomenta y completa)
    # elif estado == "GIRANDO":
    #     dron.girar()
    #     if ...:
    #         estado = "VOLANDO"
    # =============================================================

# ✏️ MINI-RETOS
# 1) Presiona "t" mientras el dron VUELA. ¿Pasa algo? ¿Y "l" mientras está EN_TIERRA? ¿Por qué?
# 2) Agrega el estado "GIRANDO": desde VOLANDO con la tecla "g"; después de 3 segundos
#    (s.segundos > 3) regresa a VOLANDO.
# 3) EMERGENCIA: con la tecla "e", desde DESPEGANDO, VOLANDO o GIRANDO, pasa a "EMERGENCIA"
#    (que hace dron.aterrizar()). De EMERGENCIA solo se sale cuando ya no está en el aire.
