# ============================================================
#  RETO 1 — Despegue con estilo                    100 puntos
# ============================================================
#  El dron despega, sube hasta 150 cm, da una vuelta de 4 segundos y aterriza.
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─en el aire─► SUBIENDO ─150 cm─► GIRANDO ─4 s─► ATERRIZANDO
#
#  📚 ¿Dónde lo vimos?
#     Sesión 7:  lecciones/01_semaforo.py          (cambiar de estado cuando pasa el tiempo)
#     Sesión 7:  lecciones/02_dron_con_teclas.py   (DESPEGANDO -> en el aire)
#     Sesión 10: actividad_1_zigzag_arucos.py      (el estado SUBIENDO)
#
#  Completa los ✏️, córrelo con ▶, haz clic en la ventana y presiona "t".
#  El juez revisa cuando el dron aterriza.   e = aterrizar ya,  q = salir.

from rally import Dron

dron = Dron(reto=1)
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
        # ✏️ 1) cuando ya esté en el aire (s.en_el_aire), cambia a "SUBIENDO"

    elif estado == "SUBIENDO":
        dron.subir()
        # ✏️ 2) cuando la altura (s.altura) llegue a 150 cm o más, cambia a "GIRANDO"

    elif estado == "GIRANDO":
        # ✏️ 3) dos cosas: que el dron gire (dron.girar()) y,
        #        cuando lleve 4 segundos en este estado (s.segundos), cambia a "ATERRIZANDO"
        pass

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # ==============================================================
