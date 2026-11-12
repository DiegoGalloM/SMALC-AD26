# ============================================================
#  ACTIVIDAD 2 — ¡Rescaten a Blu!
# ============================================================
#  Blu está atrapado arriba de una pila de cajas. El dron tiene que despegar, buscarlo,
#  reconocerlo, acercarse, quedarse 3 segundos a UN METRO de él ("rescatándolo") y aterrizar.
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─► BUSCANDO ─ve a Blu─► RECONOCIENDO ─1 s viéndolo─► ACERCANDOSE
#                                     ▲                      │                           │
#                                     └────── lo pierde ─────┴───────────────────────────┤
#                                                                                        │ está a un metro
#                                     ATERRIZANDO ◄── pasan 3 s ── RESCATANDO ◄──────────┘
#
#  CÓMO SE HACE:
#   1) Completa las 7 funciones de  blu_funciones.py  y pruébalas con  blu_probar_funciones.py
#   2) Completa aquí la número 8: EL CEREBRO (busca ✏️ en la máquina de estados).
#   3) Córrelo con ▶, haz clic en la ventana y presiona "t".   e = aterrizar ya,  q = salir.
#
#  En el simulador Blu aparece en un lugar distinto cada vez. ¡Tu programa tiene que encontrarlo siempre!

from blu_funciones import (DISTANCIA_DE_RESCATE, KP_ALTURA, KP_AVANCE, KP_GIRO, calcular_error, centro_de,
                           control_p, distancia_a_blu, encontrar_a_blu, estoy_a_un_metro, mascara_azul)
from dron import Dron

SEGUNDOS_RECONOCIENDO = 1   # cuánto tiene que verlo seguido para estar seguros de que es Blu
SEGUNDOS_DE_RESCATE = 3     # cuánto se queda a un metro de Blu

dron = Dron("simulador", objetivo="blu")   # con el staff: cambia "simulador" por "tello"
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)

    # --- 👀 LOS OJOS: tus funciones buscan a Blu en la foto (ya está hecho) ---
    mascara = mascara_azul(s.foto)
    blu = encontrar_a_blu(mascara)
    veo_a_blu = blu is not None

    # --- 🎯 EL CONTROL: tus funciones calculan cuánto moverse (ya está hecho) ---
    giro, subir, adelante, distancia, a_un_metro = 0, 0, 0, 0, False
    if veo_a_blu:
        centro_x, centro_y = centro_de(blu)
        error_x, error_y = calcular_error(centro_x, centro_y)
        giro = control_p(error_x, KP_GIRO)                # si Blu está a la derecha, gira a la derecha
        subir = control_p(error_y, KP_ALTURA)             # si Blu está arriba, sube
        distancia = distancia_a_blu(blu[2])               # blu[2] es su ancho en pixeles
        if distancia > 0:
            adelante = control_p(distancia - DISTANCIA_DE_RESCATE, KP_AVANCE)   # lejos: avanza. Muy cerca: retrocede
            a_un_metro = estoy_a_un_metro(distancia)
    dron.mostrar(caja=blu, mascara=mascara, distancia=distancia)   # dibuja en la pantalla lo que encontraste

    # SEGURIDAD PRIMERO: con "e" el dron aterriza desde cualquier estado
    if s.tecla == "e" and s.en_el_aire:
        estado = "ATERRIZANDO"

    # ===================== ✏️ 8) EL CEREBRO: MÁQUINA DE ESTADOS =====================
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
        # ✏️ COMPLETA: ¿qué tiene que pasar para dejar de girar? Cuando pase, cambia a "RECONOCIENDO"

    elif estado == "RECONOCIENDO":
        dron.mover(giro=giro, subir=subir)   # lo pone en el centro sin avanzar, para verlo bien
        # ✏️ COMPLETA (2 flechas, fíjate en el dibujo de arriba):
        #    - Si lo deja de ver, era una falsa alarma: ¿a qué estado regresa?
        #    - Si ya lleva SEGUNDOS_RECONOCIENDO en este estado (s.segundos), sí es Blu: ¿a qué estado pasa?

    elif estado == "ACERCANDOSE":
        dron.mover(adelante=adelante, giro=giro, subir=subir)   # avanza sin dejar de centrarlo
        # ✏️ COMPLETA (2 flechas):
        #    - Si lo pierde de vista...
        #    - Si ya está a un metro...   (arriba ya se calculó una variable que te lo dice)

    elif estado == "RESCATANDO":
        dron.mover(adelante=adelante, giro=giro, subir=subir)   # se mantiene a un metro, viendo a Blu
        # ✏️ COMPLETA: el rescate dura SEGUNDOS_DE_RESCATE. Cuando se cumplan, cambia a "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # ================================================================================

# ✏️ MINI-RETOS (si te sobra tiempo)
# 1) Festejo: después de rescatar a Blu, antes de aterrizar pasa a "FESTEJANDO" y gira 4 segundos.
# 2) Si en BUSCANDO pasan 15 segundos y Blu no aparece, que el dron se rinda y aterrice.
# 3) Agrega el estado "PERDIDO": si deja de ver a Blu mientras se acerca, que espere 1 segundo quieto
#    antes de regresar a BUSCANDO (como en la Sesión 7). ¿Por qué eso hace al dron más rápido?
# 4) En RESCATANDO, ¿qué pasa si alguien mueve a Blu? ¿Tu dron lo sigue? ¿Por qué?
