# ============================================================
#  ACTIVIDAD 1 — Zigzag de ArUcos
# ============================================================
#  Este programa YA FUNCIONA. Tu misión no es escribirlo: es ENTENDERLO.
#  Tienes 10 minutos para leerlo con tu equipo y después explicarnos su lógica.
#
#  El dron visita 3 ArUcos en orden (ID 0, luego 1, luego 2) y hace un zigzag:
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─► SUBIENDO ─► BUSCANDO ─ve el ArUco─► CENTRANDO ─centrado─► ACERCANDOSE
#                                                 ▲                        │                      │
#                                                 ├───── lo pierde ────────┴──────────────────────┤
#                                                 │                                               │ llegó
#                                                 └──── todavía faltan ArUcos (paso + 1) ─────────┤
#                                                                                                 │ era el último
#                                                                               ATERRIZANDO ◄─────┘
#
#  Córrelo con ▶, haz clic en la ventana y presiona "t".   e = aterrizar ya,  q = salir.

from dron import Dron

# ---------------- LA RUTA ----------------
RUTA = [0, 1, 2]                                   # los IDs de los ArUcos, en el orden en que se visitan
LADOS = ["izquierda", "derecha", "izquierda"]      # hacia dónde gira para buscar cada uno (¡el zigzag!)

# ---------------- AJUSTES ----------------
ALTURA_DE_VUELO = 110       # cm: sube hasta aquí antes de empezar a buscar
DISTANCIA_DE_LLEGADA = 90   # cm: si el ArUco está a menos de esto, ya "llegó"

dron = Dron("tello", objetivo="aruco")   # con el staff: cambia "simulador" por "tello"
estado = "EN_TIERRA"
paso = 0                    # en qué parte de la RUTA vamos (0 = el primer ArUco)

while dron.sigue():
    s = dron.sensores(estado, aruco=RUTA[paso])   # "dime qué sabes, y fíjate en ESTE ArUco"

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
        dron.buscar(LADOS[paso])          # gira hasta que el ArUco aparezca en la cámara
        if s.veo_aruco:
            estado = "CENTRANDO"

    elif estado == "CENTRANDO":
        dron.centrar()                    # control P: gira y sube/baja hasta que el error sea casi 0
        if not s.veo_aruco:
            estado = "BUSCANDO"
        elif s.centrado:
            estado = "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        dron.acercarse()                  # avanza sin dejar de corregir el error
        if not s.veo_aruco:
            estado = "BUSCANDO"
        elif s.distancia <= DISTANCIA_DE_LLEGADA:      # ¡llegó a este ArUco!
            if paso == len(RUTA) - 1:                  # ¿era el último de la RUTA?
                estado = "ATERRIZANDO"
            else:
                paso = paso + 1                        # ahora le toca al siguiente
                estado = "BUSCANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # ==============================================================

# ============================================================
#  🎤 PREGUNTAS PARA TU EXPLICACIÓN (10 minutos)
# ============================================================
#  Máquina de estados (Sesión 7)
#   1) ¿Cuántos estados tiene? Para cada uno di: ¿qué HACE el dron? y ¿qué lo hace CAMBIAR?
#   2) ¿Qué pasa si alguien tapa el ArUco mientras el dron se está acercando?
#   3) ¿Por qué la revisión de la tecla "e" está ANTES que todos los if de los estados?
#
#  ArUcos (Sesión 8)
#   4) ¿Para qué sirve la variable `paso`? ¿Cuánto vale al despegar y cuánto al aterrizar?
#   5) ¿Cómo sabe el dron que está viendo el ArUco correcto y no otro de la ruta?
#   6) Si quisieras recorrer la ruta al revés (2, 1, 0), ¿qué líneas cambiarías?
#
#  Visión y control (Sesiones 4, 5 y 6)
#   7) En la pantalla aparecen error_x y error_y. ¿Qué miden? ¿Cuánto valen si el ArUco está en el centro?
#   8) dron.centrar() usa un control P. ¿Qué hace el dron si error_x es grande y positivo? ¿Y si es chico?
#   9) El dron no tiene cinta para medir. ¿Cómo crees que calcula s.distancia con una sola cámara?
#      (Pista: fíjate qué le pasa al tamaño del ArUco en la imagen cuando el dron se acerca.)
#
#  Para pensar
#  10) En SUBIENDO hay DOS condiciones unidas con `or`. ¿Por qué no basta solo con la altura?
#  11) ¿Qué pasaría si DISTANCIA_DE_LLEGADA fuera 20? ¿Y si fuera 300?
