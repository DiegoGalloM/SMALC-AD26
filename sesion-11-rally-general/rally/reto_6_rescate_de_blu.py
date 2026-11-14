# ============================================================
#  RETO 6 — JEFE FINAL: ¡Rescaten a Blu!           300 puntos
# ============================================================
#  Antes de este, pasen los retos 3 y 4: aquí el dron usa SUS ojos y SU control.
#
#  El dron despega, busca a Blu, lo reconoce, se acerca, se queda 3 s a UN METRO de él
#  ("rescatándolo"), FESTEJA girando 3 segundos y aterriza.
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─► BUSCANDO ─ve a Blu─► RECONOCIENDO ─1 s viéndolo─► ACERCANDOSE
#                                     ▲                      │                           │
#                                     └────── lo pierde ─────┴───────────────────────────┤
#                                                                                        │ está a un metro
#                ATERRIZANDO ◄── 3 s ── FESTEJANDO ◄── 3 s ── RESCATANDO ◄───────────────┘
#                                       ¡NUEVO!
#
#  📚 ¿Dónde lo vimos?
#     Sesión 10: actividad_2_rescate_de_blu.py   (el cerebro, y el mini-reto 1: el festejo)
#
#  Completa los ✏️, córrelo con ▶, haz clic en la ventana y presiona "t".   e = aterrizar ya,  q = salir.
#  Blu aparece en un lugar distinto cada vez: ¡su programa tiene que encontrarlo siempre!

from rally import Dron
from reto_3_ojos import centro_de, encontrar_a_blu, mascara_azul
from reto_4_control import DISTANCIA_DE_RESCATE, calcular_error, control_p, distancia_a_blu, estoy_a_un_metro

KP_GIRO = 0.08              # cuánto gira por cada pixel de error horizontal
KP_ALTURA = 0.18            # cuánto sube por cada pixel de error vertical
KP_AVANCE = 0.4             # cuánto avanza por cada cm que le falta para llegar
SEGUNDOS_RECONOCIENDO = 1   # cuánto tiene que verlo seguido para estar seguros de que es Blu
SEGUNDOS_DE_RESCATE = 3     # cuánto se queda a un metro de Blu
SEGUNDOS_DE_FESTEJO = 3     # cuánto gira festejando

dron = Dron(reto=6)
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)

    # --- 👀 LOS OJOS: sus funciones del Reto 3 buscan a Blu en la foto (ya está hecho) ---
    mascara = mascara_azul(s.foto)
    blu = encontrar_a_blu(mascara)
    veo_a_blu = blu is not None

    # --- 🎯 EL CONTROL: sus funciones del Reto 4 calculan cuánto moverse (ya está hecho) ---
    giro, subir, adelante, distancia, a_un_metro = 0, 0, 0, 0, False
    if veo_a_blu:
        centro_x, centro_y = centro_de(blu)
        error_x, error_y = calcular_error(centro_x, centro_y)
        giro = control_p(error_x, KP_GIRO)
        subir = control_p(error_y, KP_ALTURA)
        distancia = distancia_a_blu(blu[2])               # blu[2] es su ancho en pixeles
        if distancia > 0:
            adelante = control_p(distancia - DISTANCIA_DE_RESCATE, KP_AVANCE)   # lejos: avanza. Muy cerca: retrocede
            a_un_metro = estoy_a_un_metro(distancia)
    dron.mostrar(caja=blu, mascara=mascara, distancia=distancia)

    # SEGURIDAD PRIMERO: con "e" el dron aterriza desde cualquier estado
    if s.tecla == "e" and s.en_el_aire:
        estado = "ATERRIZANDO"

    # ===================== 🧠 EL CEREBRO: MÁQUINA DE ESTADOS =====================
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
        # ✏️ 1) cuando vea a Blu (veo_a_blu), cambia a "RECONOCIENDO"

    elif estado == "RECONOCIENDO":
        dron.mover(giro=giro, subir=subir)   # lo pone en el centro sin avanzar
        # ✏️ 2) dos flechas:  si lo deja de ver -> "BUSCANDO"
        #                     si ya lleva SEGUNDOS_RECONOCIENDO (s.segundos) -> "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        dron.mover(adelante=adelante, giro=giro, subir=subir)   # avanza sin dejar de centrarlo
        # ✏️ 3) dos flechas:  si lo deja de ver -> "BUSCANDO"
        #                     si ya está a un metro (a_un_metro) -> "RESCATANDO"

    elif estado == "RESCATANDO":
        dron.mover(adelante=adelante, giro=giro, subir=subir)   # se mantiene a un metro, viendo a Blu
        # ✏️ 4) cuando pasen SEGUNDOS_DE_RESCATE, cambia a "FESTEJANDO"   (¡ya no a ATERRIZANDO!)

    elif estado == "FESTEJANDO":
        # ✏️ 5) ¡NUEVO! que gire (dron.girar()) y, cuando pasen SEGUNDOS_DE_FESTEJO, cambia a "ATERRIZANDO"
        pass

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # =============================================================================
