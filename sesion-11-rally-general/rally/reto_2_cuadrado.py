# ============================================================
#  RETO 2 — El cuadrado                            150 puntos
# ============================================================
#  El dron dibuja un cuadrado en el aire SIN GIRAR: adelante, derecha, atrás e izquierda,
#  3 segundos cada lado. Si lo hacen bien, aterriza justo donde despegó.
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─► ADELANTE ─3 s─► DERECHA ─3 s─► ATRAS ─3 s─► IZQUIERDA ─3 s─► ATERRIZANDO
#
#  📚 ¿Dónde lo vimos?
#     Sesión 3 y 5: send_rc_control(lado, adelante, arriba, giro)   (positivo = derecha / adelante / arriba)
#     Sesión 6:     lecciones/06_cuadrado_servoing.py               (un cuadrado por tiempo)
#     Sesión 7:     lecciones/01_semaforo.py                        (cambiar de estado con s.segundos)
#
#  dron.mover(adelante=0, derecha=0, subir=0, giro=0)  es como send_rc_control, pero cada número tiene nombre.
#  Completa los ✏️, córrelo con ▶, haz clic en la ventana y presiona "t".   e = aterrizar ya,  q = salir.

from rally import Dron

dron = Dron(reto=2)
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)

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
            estado = "ADELANTE"

    elif estado == "ADELANTE":
        dron.mover(adelante=20)       # <- así se hace un lado: velocidad 20 hacia adelante
        if s.segundos >= 3:
            estado = "DERECHA"

    elif estado == "DERECHA":
        # ✏️ 1) muévete a la DERECHA 3 segundos y luego cambia a "ATRAS"   (copia la idea de ADELANTE)
        pass

    elif estado == "ATRAS":
        # ✏️ 2) muévete hacia ATRÁS 3 segundos y luego cambia a "IZQUIERDA"
        #        Pista: no existe  atras=20 ... ¿qué pasa si a  adelante  le das una velocidad NEGATIVA?
        pass

    elif estado == "IZQUIERDA":
        # ✏️ 3) muévete a la IZQUIERDA 3 segundos y luego cambia a "ATERRIZANDO"
        pass

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # ==============================================================
