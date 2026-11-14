"""
rally.py — el JUEZ del rally (ya está hecho: no necesitas modificarlo)

Revisa si su reto quedó bien y, si sí, manda los puntos al marcador del staff.

    from rally import Dron          # en lugar de  "from dron import Dron"
    dron = Dron(reto=1)             # el mismo dron de la Sesión 10, en el simulador

Los retos 1, 2, 5 y 6 se califican cuando el dron ATERRIZA.
Los retos 3 y 4 se califican al correr su archivo (revisa las funciones).
"""

import hashlib
import json
import math
import sys
import threading
import unicodedata
import urllib.request

import cv2
import numpy as np

import dron as _cuerpo

SAL = "smalc-ad26-rally"  # la misma que en marcador/servidor_marcador.py
RETOS = {
    1: ("Despegue con estilo", 100),
    2: ("El cuadrado", 150),
    3: ("Los ojos", 150),
    4: ("El control", 150),
    5: ("Zigzag y de regreso", 200),
    6: ("Jefe final: rescate de Blu", 300),
}
MUNDOS = {1: "vacio", 2: "vacio", 5: "zigzag", 6: "blu"}
OBJETIVOS = {1: "color", 2: "color", 5: "aruco", 6: "blu"}


# =====================================================================
# El equipo y el marcador
# =====================================================================
def normalizar(nombre):
    """ "Los Halcónes " y "los halcones" son el mismo equipo."""
    sin_acentos = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    return " ".join(sin_acentos.lower().split())


def codigo(nombre, reto):
    """El código de 4 letras que prueba que el equipo resolvió el reto."""
    return hashlib.sha256(f"{SAL}|{normalizar(nombre)}|{reto}".encode()).hexdigest()[:4].upper()


def _equipo():
    try:
        import equipo
    except ImportError:
        raise SystemExit("No encuentro equipo.py: abre en VSCode la carpeta 'rally' completa.")
    nombre = " ".join(str(getattr(equipo, "EQUIPO", "")).split())
    if not normalizar(nombre):
        raise SystemExit('\n✏️  Antes de empezar, escriban el nombre de su equipo en equipo.py\n'
                         '    por ejemplo:   EQUIPO = "Los Halcones"\n')
    marcador = str(getattr(equipo, "MARCADOR", "")).strip().rstrip("/")
    if marcador and not marcador.startswith("http"):
        marcador = "http://" + marcador
    return nombre[:30], marcador


def _pedir(marcador, ruta, datos, espera=3):
    """Manda un mensaje al marcador (sin proxies: el marcador está en la misma red)."""
    abrir = urllib.request.build_opener(urllib.request.ProxyHandler({})).open
    pedido = urllib.request.Request(marcador + ruta, data=json.dumps(datos).encode(),
                                    headers={"Content-Type": "application/json"})
    with abrir(pedido, timeout=espera) as respuesta:
        return json.loads(respuesta.read().decode())


def saludar():
    """Al empezar: avisa al marcador que el equipo ya llegó (y prueba la conexión)."""
    nombre, marcador = _equipo()
    try:
        respuesta = _pedir(marcador, "/hola", {"equipo": nombre}, espera=2)
        print(f"📡 Marcador conectado: {respuesta.get('mensaje', 'listo')}")
    except Exception:
        print(f"⚠️  No encuentro el marcador en {marcador or '(vacío)'}. Revisen MARCADOR en equipo.py y que estén\n"
              f"    en la misma red WiFi. Pueden seguir: si resuelven el reto, les doy un código para el staff.")


def entregar(reto):
    """Manda los puntos al marcador. Si no hay conexión, enseña un código para el staff."""
    nombre, marcador = _equipo()
    titulo, puntos = RETOS[reto]
    print(f"\n🏆 ¡RETO {reto} SUPERADO!  {titulo}  ({puntos} puntos)")
    try:
        respuesta = _pedir(marcador, "/entregar", {"equipo": nombre, "reto": reto, "codigo": codigo(nombre, reto)})
        print("📡 " + respuesta.get("mensaje", "¡Ya está en el marcador!"))
    except Exception:
        print(f"📡 No pude llegar al marcador ({marcador or 'vacío'}). Enséñenle esto al staff:")
        print(f"      equipo: {nombre}    reto: {reto}    código: {codigo(nombre, reto)}")


# =====================================================================
# Retos 1, 2, 5 y 6: el mismo dron de la Sesión 10, con juez
# =====================================================================
class Dron(_cuerpo.Dron):
    def __init__(self, reto):
        if reto not in MUNDOS:
            raise SystemExit(f"El reto {reto} no usa el dron. Los retos con dron son: {', '.join(map(str, MUNDOS))}")
        _equipo()  # si falta el nombre del equipo, mejor saberlo antes de volar
        super().__init__("simulador", objetivo=OBJETIVOS[reto], mundo=MUNDOS[reto])
        self._reto, self._registro, self._superado = reto, [], False
        print(f"🏁 RALLY — Reto {reto}: {RETOS[reto][0]} ({RETOS[reto][1]} puntos)")
        threading.Thread(target=saludar, daemon=True).start()

    def sensores(self, estado, aruco=None):
        volando = self._fase != "tierra"
        s = super().sensores(estado, aruco)
        self._registro.append((self._estado, self._t, self._x, self._y, self._z, self._yaw))
        if volando and self._fase == "tierra" and not self._superado:  # acaba de aterrizar
            self._calificar()
        return s

    def _revisar_mision(self):
        pass  # en el rally, el juez es _calificar()

    def _calificar(self):
        problema = JUECES[self._reto](self)
        if problema:
            print(f"\n❌ Reto {self._reto}: todavía no cuenta. {problema}")
            self._avisar("Todavia no cuenta: lee la terminal", 15)
            return
        self._superado = self._mision_cumplida = True
        self._festejo = f"RETO {self._reto} SUPERADO! +{RETOS[self._reto][1]}"
        threading.Thread(target=entregar, args=(self._reto,)).start()

    def _terminar(self):
        if not self._terminado and not self._superado:
            if not self._ya_volo:
                print("\nℹ️  El dron nunca despegó: haz clic en la ventana del simulador y presiona t.")
            elif self._fase != "tierra":
                print("\nℹ️  El reto se califica cuando el dron ATERRIZA al final de la misión.")
        super()._terminar()


# ---------------- Herramientas del juez ----------------
def _falta_en_orden(historial, nombres):
    """El primer estado de la lista que NO aparece (en ese orden) en el historial, o None."""
    i = 0
    for estado in historial:
        if i < len(nombres) and estado == nombres[i]:
            i += 1
    return nombres[i] if i < len(nombres) else None


def _ultimo_tramo(dron, nombre):
    """Los renglones del registro de la ÚLTIMA vez que el dron estuvo en ese estado."""
    tramo, dentro = [], False
    for fila in dron._registro:
        if fila[0] == nombre:
            if not dentro:  # volvió a entrar: empieza un tramo nuevo
                tramo, dentro = [], True
            tramo.append(fila)
        else:
            dentro = False
    return tramo


def _duracion(tramo):
    return tramo[-1][1] - tramo[0][1] + _cuerpo.DT if tramo else 0.0


def _grados_girados(tramo):
    total = 0.0
    for antes, despues in zip(tramo, tramo[1:]):
        total += abs((despues[5] - antes[5] + 180) % 360 - 180)
    return total


def _juez_1(d):
    falta = _falta_en_orden(d._historial, ["DESPEGANDO", "SUBIENDO", "GIRANDO", "ATERRIZANDO"])
    if falta:
        return f'El dron nunca pasó por "{falta}". El orden es DESPEGANDO > SUBIENDO > GIRANDO > ATERRIZANDO.'
    altura = max(fila[4] for fila in d._registro)
    if altura < 142:
        return f"El dron solo subió a {altura:.0f} cm. En SUBIENDO tiene que llegar a 150 cm (usa s.altura)."
    girando = _ultimo_tramo(d, "GIRANDO")
    if _duracion(girando) < 3.7:
        return f"Estuvo {_duracion(girando):.1f} s en GIRANDO y tienen que ser 4 s (usa s.segundos)."
    if _grados_girados(girando) < 90:
        return "En GIRANDO el dron casi no giró: ¿le pusiste dron.girar()?"
    return ""


LADOS_DEL_CUADRADO = [("ADELANTE", (0, -1), "adelante"), ("DERECHA", (1, 0), "la derecha"),
                      ("ATRAS", (0, 1), "atrás"), ("IZQUIERDA", (-1, 0), "la izquierda")]


def _juez_2(d):
    orden = ["DESPEGANDO"] + [nombre for nombre, _, _ in LADOS_DEL_CUADRADO] + ["ATERRIZANDO"]
    falta = _falta_en_orden(d._historial, orden)
    if falta:
        return f'El dron nunca pasó por "{falta}". El orden es {" > ".join(orden)}.'
    for nombre, (ux, uy), hacia in LADOS_DEL_CUADRADO:
        tramo = _ultimo_tramo(d, nombre)
        avance = (tramo[-1][2] - tramo[0][2]) * ux + (tramo[-1][3] - tramo[0][3]) * uy
        if avance < -10:
            return f"En {nombre} el dron se fue AL REVÉS ({-avance:.0f} cm). Revisa el signo de la velocidad en dron.mover(...)."
        if avance < 10:
            return f"En {nombre} el dron no se movió hacia {hacia}. ¿Qué le pusiste a dron.mover(...)?"
        if avance < 50:
            return f"En {nombre} el dron solo avanzó {avance:.0f} cm hacia {hacia}: ¿duró 3 segundos?"
    inicio = d._base
    lejos = math.hypot(d._x - inicio[0], d._y - inicio[1])
    if lejos > 45:
        return f"Aterrizó a {lejos:.0f} cm de donde despegó: el cuadrado no cerró. ¿Todos los lados duran 3 s?"
    return ""


def _juez_5(d):
    faltan = d._faltan()
    if faltan:
        return f"Faltaron {faltan} ArUcos. El dron tiene que llegar a los 3, en orden: 0 > 1 > 2."
    if "REGRESANDO" not in d._historial:
        return 'Falta el estado "REGRESANDO": después del último ArUco el dron vuelve a la base (H).'
    if not d._en_base():
        lejos = math.hypot(d._x - d._base[0], d._y - d._base[1])
        return f"Aterrizó a {lejos:.0f} cm de la base (H). En REGRESANDO esperen a que s.en_base sea True."
    return ""


def _juez_6(d):
    if not d._rescatado:
        return ("Blu no fue rescatado: el estado RESCATANDO tiene que durar 3 s a un metro de Blu "
                "(mira la barra de rescate). ¿Ya pasaron los retos 3 y 4?")
    falta = _falta_en_orden(d._historial, ["RESCATANDO", "FESTEJANDO", "ATERRIZANDO"])
    if falta:
        return f'Después de rescatar a Blu falta "{falta}": RESCATANDO > FESTEJANDO > ATERRIZANDO.'
    festejo = _ultimo_tramo(d, "FESTEJANDO")
    if _duracion(festejo) < 2.7:
        return f"El festejo duró {_duracion(festejo):.1f} s y tienen que ser 3 s."
    if _grados_girados(festejo) < 60:
        return "En FESTEJANDO el dron casi no giró: ¿le pusiste dron.girar()?"
    return ""


JUECES = {1: _juez_1, 2: _juez_2, 5: _juez_5, 6: _juez_6}


# =====================================================================
# Retos 3 y 4: revisar funciones (como blu_probar_funciones.py de la Sesión 10)
# =====================================================================
def _foto_con_manchas(*manchas):
    foto = np.full((480, 640, 3), (90, 90, 90), np.uint8)
    for x, y, ancho, alto in manchas:
        cv2.rectangle(foto, (x, y), (x + ancho - 1, y + alto - 1), (220, 100, 30), -1)  # azul en BGR
    return foto


def _mascara_con_manchas(*manchas):
    mascara = np.zeros((480, 640), np.uint8)
    for x, y, ancho, alto in manchas:
        cv2.rectangle(mascara, (x, y), (x + ancho - 1, y + alto - 1), 255, -1)
    return mascara


def _casi(a, b, margen=2):
    try:
        return a is not None and abs(a - b) <= margen
    except TypeError:
        return False


def _prueba_mascara_azul(m):
    mascara = m.mascara_azul(_foto_con_manchas((200, 150, 120, 160)))
    if mascara is None:
        return "regresa None: todavía no calcula la máscara"
    if not isinstance(mascara, np.ndarray) or mascara.shape != (480, 640):
        return "la máscara debe ser una imagen en blanco y negro del mismo tamaño que la foto (¿usaste inRange?)"
    if mascara[230, 260] == 0:
        return "donde hay azul la máscara salió NEGRA (¿convertiste a HSV? ¿usaste AZUL_BAJO y AZUL_ALTO?)"
    if mascara[50, 50] != 0:
        return "donde NO hay azul la máscara salió BLANCA"
    return ""


def _prueba_encontrar_a_blu(m):
    grande, ruido = (200, 150, 120, 160), (500, 60, 12, 12)
    caja = m.encontrar_a_blu(_mascara_con_manchas(grande, ruido))
    if caja is None:
        return "hay una mancha grande en la máscara y regresó None"
    if len(caja) == 5:
        return "regresó 5 números: quita el área, solo regresa x, y, ancho, alto"
    if len(caja) != 4 or not all(_casi(a, b) for a, b in zip(caja, grande)):
        return f"regresó {tuple(caja)} y la mancha más grande está en {grande}"
    if m.encontrar_a_blu(_mascara_con_manchas(ruido)) is not None:
        return "una manchita de ruido (más chica que AREA_MINIMA) no es Blu: debe regresar None"
    if m.encontrar_a_blu(_mascara_con_manchas()) is not None:
        return "con la máscara toda negra debe regresar None"
    return ""


def _prueba_centro_de(m):
    centro = tuple(m.centro_de((100, 50, 80, 60)))
    if centro != (140, 80):
        return f"el centro de la caja (x=100, y=50, ancho=80, alto=60) es (140, 80) y regresó {centro}"
    return ""


def _prueba_calcular_error(m):
    centro = tuple(m.calcular_error(320, 240))
    if centro != (0, 0):
        return f"con Blu justo en el centro (320, 240) los errores deben ser (0, 0) y salió {centro}"
    error_x, error_y = m.calcular_error(420, 140)  # a la derecha y arriba
    if error_x != 100:
        return f"Blu está 100 pixeles a la DERECHA del centro: error_x debe ser 100 y salió {error_x}"
    if error_y != 100:
        return f"Blu está 100 pixeles ARRIBA del centro: error_y debe ser +100 y salió {error_y} (¡ojo con el signo!)"
    return ""


def _prueba_control_p(m):
    maxima = m.VELOCIDAD_MAXIMA
    if not _casi(m.control_p(100, 0.1), 10, 0.01):
        return f"control_p(100, 0.1) debe dar 10 y dio {m.control_p(100, 0.1)}"
    if not _casi(m.control_p(-50, 0.2), -10, 0.01):
        return f"control_p(-50, 0.2) debe dar -10 y dio {m.control_p(-50, 0.2)}"
    if not _casi(m.control_p(5000, 0.1), maxima, 0.01):
        return f"con un error enorme no debe pasar de VELOCIDAD_MAXIMA ({maxima}) y dio {m.control_p(5000, 0.1)}"
    if not _casi(m.control_p(-5000, 0.1), -maxima, 0.01):
        return f"con un error enorme negativo no debe bajar de -{maxima} y dio {m.control_p(-5000, 0.1)}"
    return ""


def _prueba_distancia_a_blu(m):
    pixeles_a_un_metro = m.ANCHO_DE_BLU_CM * m.FOCAL / 100
    for metros in (1, 2, 4):
        pixeles = pixeles_a_un_metro / metros
        distancia = m.distancia_a_blu(pixeles)
        if not _casi(distancia, 100 * metros, 1):
            return f"si Blu se ve de {pixeles:.0f} pixeles de ancho está a {100 * metros} cm, y regresó {distancia}"
    return ""


def _prueba_estoy_a_un_metro(m):
    meta, tolerancia = m.DISTANCIA_DE_RESCATE, m.TOLERANCIA_DISTANCIA
    if m.estoy_a_un_metro(meta) is not True:
        return f"a {meta} cm exactos debe regresar True"
    if m.estoy_a_un_metro(meta - tolerancia + 5) is not True or m.estoy_a_un_metro(meta + tolerancia - 5) is not True:
        return "si está dentro de la tolerancia (un poquito más cerca o más lejos) también es True"
    if m.estoy_a_un_metro(meta + tolerancia + 20) is not False:
        return f"a {meta + tolerancia + 20} cm está muy LEJOS: debe regresar False"
    if m.estoy_a_un_metro(meta - tolerancia - 20) is not False:
        return f"a {meta - tolerancia - 20} cm está muy CERCA: debe regresar False (¿usaste abs?)"
    return ""


PRUEBAS = {
    3: [("1) mascara_azul", _prueba_mascara_azul), ("2) encontrar_a_blu", _prueba_encontrar_a_blu),
        ("3) centro_de", _prueba_centro_de)],
    4: [("1) calcular_error", _prueba_calcular_error), ("2) control_p", _prueba_control_p),
        ("3) distancia_a_blu", _prueba_distancia_a_blu), ("4) estoy_a_un_metro", _prueba_estoy_a_un_metro)],
}


def revisar(reto):
    """Revisa las funciones del archivo que se está corriendo (reto 3 o 4)."""
    _equipo()
    modulo = sys.modules["__main__"]
    titulo, puntos = RETOS[reto]
    print(f"\n🏁 RALLY — Reto {reto}: {titulo} ({puntos} puntos)\n")
    buenas = 0
    for nombre, prueba in PRUEBAS[reto]:
        try:
            problema = prueba(modulo)
        except Exception as error:  # la función tronó: también cuenta como ❌
            problema = f"tronó con este error: {type(error).__name__}: {error}"
        buenas += problema == ""
        print(f"{'✅' if not problema else '❌'}  {nombre}" + (f"\n      {problema}" if problema else ""))
    print(f"\nLlevan {buenas} de {len(PRUEBAS[reto])}.")
    if buenas < len(PRUEBAS[reto]):
        return
    entregar(reto)
    if reto == 3:  # el premio: ver cómo encuentran a Blu sus funciones
        foto, _ = _cuerpo.foto_de_blu(distancia_cm=150, a_la_derecha_cm=25, arriba_cm=10)
        caja = modulo.encontrar_a_blu(modulo.mascara_azul(foto))
        if caja is not None:
            _cuerpo.Dron._apuntar(foto, tuple(int(n) for n in caja))
        print("\nAsí ven a Blu sus funciones. Presionen una tecla en la ventana para cerrarla.")
        cv2.imshow("Asi ven a Blu tus funciones (presiona una tecla)", foto)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
