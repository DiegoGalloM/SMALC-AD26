# ============================================================
#  LECCIÓN 3 — ¡Batería baja! Regresa a casa
# ============================================================
#  Ahora el dron cambia de estado por lo que MIDE (un sensor), no por una tecla.
#  En este mundo la batería se gasta MUY rápido.
#
#                 en el aire            batería < 30           en la base
#   DESPEGANDO ─────────────► PATRULLANDO ─────────► REGRESANDO ─────────► ATERRIZANDO
#
#  Córrelo con ▶ y observa la barra de batería. q = salir.

from dron import Dron

dron = Dron("simulador", mundo="patrulla")
estado = "DESPEGANDO"

while dron.sigue():
    s = dron.sensores(estado)

    # ===================== LÓGICA DE ESTADOS =====================
    if estado == "DESPEGANDO":
        dron.despegar()
        if s.en_el_aire:
            estado = "PATRULLANDO"

    elif estado == "PATRULLANDO":
        dron.patrullar()  # da vueltas por la arena
        # ✏️ COMPLETA: si la batería (s.bateria) baja de 30, cambia a "REGRESANDO"

    elif estado == "REGRESANDO":
        dron.regresar_a_base()
        # ✏️ COMPLETA: cuando esté sobre la base (s.en_base), cambia a "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # =============================================================

# ✏️ MINI-RETOS
# 1) Cambia el 30 por 10. ¿Alcanza a llegar a la base? ¿Por qué conviene dejar "margen"?
# 2) Aterrizaje de emergencia: si estás REGRESANDO y la batería baja de 8,
#    mejor aterriza donde estés (pasa directo a "ATERRIZANDO").
# 3) Pausa: en PATRULLANDO, con la tecla "p" pasa a "ESPERANDO" (dron.quieto());
#    en ESPERANDO, con "p" regresa a PATRULLANDO. ¿La batería se sigue gastando mientras esperas?
