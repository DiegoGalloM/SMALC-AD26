# ============================================================
#  LECCIÓN 4 — Ojos con estados (tu webcam es la cámara del dron)
# ============================================================
#  Juntamos lo de las Sesiones 4 y 6 (ver un color y centrarlo) con estados:
#
#                ve el color            está centrado
#   BUSCANDO ─────────────► SIGUIENDO ◄─────────────► CENTRADO
#       ▲                     │   ▲      se descentra
#       │      2 s sin verlo  ▼   │ lo vuelve a ver
#       └──────────────── PERDIDO ┘
#
#  Aquí el dron NO se mueve: en la pantalla ves la orden que mandaría.
#  Pon un objeto VERDE frente a tu cámara y muévelo. q = salir.
#  ¿Tienes un Tello? Cambia "camara" por "tello_sin_volar" para usar su cámara.

from dron import Dron

dron = Dron("camara", color="verde")
estado = "BUSCANDO"

while dron.sigue():
    s = dron.sensores(estado)

    # ===================== LÓGICA DE ESTADOS =====================
    if estado == "BUSCANDO":
        dron.girar()
        # ✏️ COMPLETA: si ve el color (s.veo_color), cambia a "SIGUIENDO"

    elif estado == "SIGUIENDO":
        dron.seguir_color()  # el control P de la Sesión 6
        if not s.veo_color:
            estado = "PERDIDO"
        # ✏️ COMPLETA: si el color está centrado (s.centrado), cambia a "CENTRADO"

    elif estado == "CENTRADO":
        dron.quieto()
        # ✏️ COMPLETA: si deja de estar centrado, regresa a "SIGUIENDO"
        #    Pista:  if not s.centrado:

    elif estado == "PERDIDO":
        dron.quieto()  # espera un momento, a ver si lo vuelve a ver
        if s.veo_color:
            estado = "SIGUIENDO"
        # ✏️ COMPLETA: si pasan 2 segundos (s.segundos) sin verlo, regresa a "BUSCANDO"
    # =============================================================

# ✏️ MINI-RETOS
# 1) Tapa la cámara un segundo y destápala. ¿Por qué es útil el estado PERDIDO en vez de
#    regresar directo a BUSCANDO?
# 2) Agrega el estado "MUY_CERCA": desde SIGUIENDO o CENTRADO, si s.cerca, el dron hace
#    dron.retroceder(); cuando ya no está cerca, regresa a SIGUIENDO.
# 3) Cambia color="verde" por "rojo" o "azul" y prueba con otro objeto.
