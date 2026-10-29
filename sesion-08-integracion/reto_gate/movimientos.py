# ============================================================
#  movimientos.py — LOS MÚSCULOS del dron: mandarle órdenes
# ============================================================
#  Recuerda el orden de send_rc_control (Sesiones 3 y 5):
#
#      tello.send_rc_control( izquierda/derecha,  adelante/atrás,  arriba/abajo,  giro )
#                                    1°                 2°              3°           4°
#
#  Pruébalo con:  paso3_movimientos.py

VELOCIDAD_GIRO = 30  # qué tan rápido gira buscando la gate
VELOCIDAD_AVANCE = 25  # qué tan rápido avanza


def detener(tello):
    """Ya está hecha: todo en cero = quieto en el aire."""
    tello.send_rc_control(0, 0, 0, 0)


# ✏️ COMPLETA ESTA FUNCIÓN: gira a la derecha con VELOCIDAD_GIRO (el giro es el 4° número)
def girar(tello):
    tello.send_rc_control(0, 0, 0, 0)


# ✏️ COMPLETA ESTA FUNCIÓN: avanza derecho con VELOCIDAD_AVANCE (adelante es el 2° número)
def avanzar(tello):
    tello.send_rc_control(0, 0, 0, 0)


# ✏️ COMPLETA ESTA FUNCIÓN: manda las tres correcciones al mismo tiempo, cada una en su lugar
#    adelante va en el 2°, subir en el 3° y giro en el 4°
def corregir(tello, giro, subir, adelante):
    tello.send_rc_control(0, 0, 0, 0)
