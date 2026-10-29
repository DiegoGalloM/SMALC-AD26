# ============================================================
#  MISIÓN — Task 1: ¡cruza la gate azul!
# ============================================================
#  Aquí se junta TODO: tus ojos (vision.py), tu control P (control.py),
#  tus músculos (movimientos.py) y el cerebro: la máquina de estados.
#
#              "t"            ve la gate          centrada          ancho > ANCHO_PARA_CRUZAR
#  EN_TIERRA ─────► BUSCANDO ───────────► CENTRANDO ────────► ACERCANDOSE ────────────────► CRUZANDO
#                      ▲                     │                    │                           │ pasan
#                      └──── pierde la gate ─┴────────────────────┘                           │ SEGUNDOS_CRUZANDO
#                                                                         ATERRIZANDO ◄──────┘
#
#  1) Pruébalo en "simulador". 2) Con el staff, cambia MODO a "tello".
#  Haz clic en la ventana. Teclas: t = despegar, e = aterrizar ya, q = salir.

import time

import control
import movimientos
import vision
from conexion import conectar, leer_foto, mostrar, terminar

MODO = "simulador"  # "simulador" o "tello" (¡solo con el staff!)
ANCHO_PARA_CRUZAR = 380  # pixeles: si la gate se ve así de ancha, ya está muy cerca
TOLERANCIA = 30  # pixeles: si los dos errores son menores, la gate está centrada
SEGUNDOS_CRUZANDO = 4  # cuánto avanza "a ciegas" para atravesar la gate

tello = conectar(MODO)
estado = "EN_TIERRA"
estado_anterior = ""

while True:
    # --- El reloj del estado (ya está hecho) ---
    if estado != estado_anterior:
        print("->", estado)
        inicio = time.time()
        estado_anterior = estado
    segundos = time.time() - inicio

    # --- LOS OJOS: usa TUS funciones de vision.py (ya está hecho) ---
    foto = leer_foto(tello)
    mascara = vision.mascara_azul(foto)
    gate = vision.encontrar_gate(mascara)
    veo_gate = gate is not None

    # --- EL CONTROL P: usa TUS funciones de control.py (ya está hecho) ---
    giro, subir, centrada, cerca = 0, 0, False, False
    if veo_gate:
        centro_x, centro_y = vision.centro_de(gate)
        error_x = control.error_horizontal(centro_x, 640)
        error_y = control.error_vertical(centro_y, 480)
        giro = control.control_p(error_x, control.KP_GIRO)
        subir = control.control_p(error_y, control.KP_ALTURA)
        centrada = abs(error_x) < TOLERANCIA and abs(error_y) < TOLERANCIA
        cerca = gate[2] > ANCHO_PARA_CRUZAR  # gate[2] es el ancho de la gate

    tecla = mostrar(tello, foto, mascara, estado, gate)
    if tecla == "q":
        break

    # SEGURIDAD (no la quiten): con "e" el dron aterriza desde cualquier estado
    if tecla == "e" and estado != "EN_TIERRA":
        estado = "ATERRIZANDO"

    # ===================== MÁQUINA DE ESTADOS =====================
    if estado == "EN_TIERRA":
        if tecla == "t":
            tello.takeoff()
            estado = "BUSCANDO"

    elif estado == "BUSCANDO":
        movimientos.girar(tello)
        # ✏️ COMPLETA: si ve la gate (veo_gate), cambia a "CENTRANDO"

    elif estado == "CENTRANDO":
        movimientos.corregir(tello, giro, subir, 0)  # se centra sin avanzar
        # ✏️ COMPLETA: si deja de ver la gate, regresa a "BUSCANDO"
        # ✏️ COMPLETA: si ya está centrada, cambia a "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        movimientos.corregir(tello, giro, subir, movimientos.VELOCIDAD_AVANCE)  # avanza sin dejar de centrarse
        # ✏️ COMPLETA: si deja de ver la gate, regresa a "BUSCANDO"
        # ✏️ COMPLETA: si ya está cerca, cambia a "CRUZANDO"

    elif estado == "CRUZANDO":
        movimientos.avanzar(tello)  # ¡a ciegas! la gate ya no cabe en la cámara
        # ✏️ COMPLETA: si pasan SEGUNDOS_CRUZANDO segundos, cambia a "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        movimientos.detener(tello)
        tello.land()
        estado = "EN_TIERRA"
    # ==============================================================

terminar(tello)

# ✏️ RETOS EXTRA
# 1) ¿Por qué CENTRANDO va antes de ACERCANDOSE? Prueba quitarlo (que BUSCANDO pase directo a ACERCANDOSE).
# 2) Si la gate se pierde un instante, el dron regresa a BUSCANDO y gira. Agrega un estado "PERDIDA"
#    que espere 1 segundo quieto antes de rendirse (como en la Sesión 7).
# 3) Después de cruzar, que el dron gire 180° (estado "DANDO_VUELTA", unos 4 s girando)
#    y vuelva a BUSCANDO para cruzar la gate de regreso.
