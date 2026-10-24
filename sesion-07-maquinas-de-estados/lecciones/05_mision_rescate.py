# ============================================================
#  LECCIÓN 5 — Misión de rescate (¡todo junto!)
# ============================================================
#  En el simulador hay 3 personas (bolitas VERDES) que rescatar. El dron debe:
#  despegar, buscar, acercarse, rescatar a cada una, regresar a la base y aterrizar.
#
#   EN_TIERRA ─"t"─► DESPEGANDO ─► BUSCANDO ─► ACERCANDOSE ─► RESCATANDO
#                                     ▲             │              │
#                                     └── lo pierde ┘              │ ya no está cerca:
#                                     └──────── faltan > 0 ────────┤
#                                                                  │ faltan == 0
#                    ATERRIZANDO ◄── en la base ── REGRESANDO ◄────┘
#
#  Córrelo con ▶, haz clic en la ventana y presiona "t". q = salir.

from dron import Dron

dron = Dron("simulador", mundo="rescate")
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado)

    # SEGURIDAD PRIMERO: esta revisión va ANTES que todo lo demás.
    # Si la batería baja de 25 estando en el aire, se cancela la misión y regresa a casa.
    if s.en_el_aire and s.bateria < 25 and estado != "REGRESANDO" and estado != "ATERRIZANDO":
        estado = "REGRESANDO"

    # ===================== LÓGICA DE ESTADOS =====================
    if estado == "EN_TIERRA":
        dron.quieto()
        if s.tecla == "t":
            estado = "DESPEGANDO"

    elif estado == "DESPEGANDO":
        dron.despegar()
        # ✏️ COMPLETA: cuando esté en el aire, cambia a "BUSCANDO"

    elif estado == "BUSCANDO":
        dron.girar()
        # ✏️ COMPLETA: si ve el color, cambia a "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        dron.acercarse()  # sigue el color y avanza hacia él
        # ✏️ COMPLETA: si deja de ver el color, regresa a "BUSCANDO"
        # ✏️ COMPLETA: si ya está cerca (s.cerca), cambia a "RESCATANDO"

    elif estado == "RESCATANDO":
        dron.rescatar()  # se queda junto a la persona 2 segundos; luego la persona desaparece
        # ✏️ COMPLETA: cuando ya no esté cerca (not s.cerca), es que ya la rescató:
        #     si todavía faltan personas (s.faltan > 0)  -> "BUSCANDO"
        #     si ya no falta nadie                     -> "REGRESANDO"

    elif estado == "REGRESANDO":
        dron.regresar_a_base()
        # ✏️ COMPLETA: cuando esté en la base, cambia a "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
    # =============================================================

# ✏️ MINI-RETOS
# 1) Cambia la primera línea a  Dron("simulador", mundo="rescate", bateria=40).
#    ¿Rescata a todos? ¿Qué estado salva al dron?
# 2) Celebración: al llegar a la base sin que falte nadie, antes de aterrizar pasa a "FESTEJANDO"
#    (dron.girar()) durante 3 segundos.
# 3) ¿Qué pasaría si la revisión de SEGURIDAD estuviera hasta abajo, después de todos los if?
