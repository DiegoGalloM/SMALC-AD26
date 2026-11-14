# ============================================================
#  RETO 5 — Zigzag... ¡y de regreso a casa!        200 puntos
# ============================================================
#  El dron visita los 3 ArUcos en orden (ID 0, luego 1, luego 2) y, en vez de aterrizar ahí,
#  REGRESA a la base (la H del mapa) y aterriza en ella.
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─► SUBIENDO ─► BUSCANDO ─ve el ArUco─► CENTRANDO ─centrado─► ACERCANDOSE
#                                                 ▲                        │                      │
#                                                 ├───── lo pierde ────────┴──────────────────────┤
#                                                 └──── todavía faltan ArUcos (paso + 1) ─────────┤
#                                                                                                 │ era el último
#                                          ATERRIZANDO ◄── en la base ── REGRESANDO ◄─────────────┘   ¡NUEVO!
#
#  📚 ¿Dónde lo vimos?
#     Sesión 10: actividad_1_zigzag_arucos.py   (¡casi todo está ahí!)
#     Sesión 7:  lecciones/05_mision_rescate.py (el estado REGRESANDO)
#
#  Completa los ✏️, córrelo con ▶, haz clic en la ventana y presiona "t".   e = aterrizar ya,  q = salir.

from rally import Dron

RUTA = [0, 1, 2]                                   # los IDs de los ArUcos, en orden
LADOS = ["izquierda", "derecha", "izquierda"]      # hacia dónde gira para buscar cada uno
ALTURA_DE_VUELO = 110       # cm
DISTANCIA_DE_LLEGADA = 90   # cm: si el ArUco está a menos de esto, ya "llegó"

dron = Dron(reto=5)
estado = "EN_TIERRA"
paso = 0                    # en qué parte de la RUTA vamos (0 = el primer ArUco)

while dron.sigue():
    s = dron.sensores(estado, aruco=RUTA[paso])

    # SEGURIDAD PRIMERO: con "e" el dron aterriza desde cualquier estado
    if s.tecla == "e" and s.en_el_aire:
        estado = "ATERRIZANDO"

    # ===================== MÁQUINA DE ESTADOS =====================
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
        if s.altura >= ALTURA_DE_VUELO or s.segundos >= 3:
            estado = "BUSCANDO"

    elif estado == "BUSCANDO":
        dron.buscar(LADOS[paso])
        # ✏️ 1) si ve el ArUco (s.veo_aruco), cambia a "CENTRANDO"
        if s.veo_aruco:
            estado = "CENTRANDO"

    elif estado == "CENTRANDO":
        dron.centrar()
        # ✏️ 2) dos flechas:  si lo deja de ver -> "BUSCANDO"      si ya está centrado (s.centrado) -> "ACERCANDOSE"
        if not s.veo_aruco:
            estado = "BUSCANDO"
        elif s.centrado:
            estado = "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        dron.acercarse()
        if not s.veo_aruco:
            estado = "BUSCANDO"
        elif s.distancia <= DISTANCIA_DE_LLEGADA:      # ¡llegó a este ArUco!
            # ✏️ 3) ¿era el último de la RUTA?  (paso == len(RUTA) - 1)
            #        sí -> "REGRESANDO"          no -> paso = paso + 1   y   "BUSCANDO"
            if paso == len(RUTA) - 1:
                estado = "REGRESANDO"
            else:
                paso = paso + 1
                estado = "BUSCANDO"

    elif estado == "REGRESANDO":
        # ✏️ 4) ¡NUEVO! vuelve a casa con dron.regresar_a_base() y, cuando esté en la base (s.en_base),
        #        cambia a "ATERRIZANDO"
        dron.regresar_a_base()
        if s.en_base:
            estado = "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # ==============================================================
