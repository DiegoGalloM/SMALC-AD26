"""
dron.py — el CUERPO del dron (ya está hecho: no necesitas modificarlo)

Tu programa es el CEREBRO: decide en qué estado está el dron y cuándo cambia.
Este archivo sabe CÓMO moverse y CÓMO ver, en cualquiera de estos modos:

    "simulador"        un dron en la pantalla (para probar sin ningún riesgo)
    "camara"           tu webcam hace de ojos del dron; no se mueve nada, solo te dice qué haría
    "tello_sin_volar"  el Tello real prende su cámara y sus sensores, pero NO despega
    "tello"            el Tello real vuela de verdad (¡solo con el staff!)

y puede perseguir tres cosas distintas (objetivo):

    "color"   una mancha de color, como en las Sesiones 6 y 7
    "aruco"   un marcador ArUco, como en la Sesión 8   <- Actividad 1: zigzag
    "blu"     aquí los ojos los programas TÚ           <- Actividad 2: rescate de Blu

Cómo se usa:

    from dron import Dron

    dron = Dron("simulador", objetivo="aruco")
    estado = "EN_TIERRA"

    while dron.sigue():
        s = dron.sensores(estado, aruco=0)   # lo que el dron sabe en este momento

        if estado == "EN_TIERRA":
            dron.quieto()                    # lo que HACE en este estado
            if s.tecla == "t":               # cuándo CAMBIA de estado
                estado = "DESPEGANDO"
        ...

ACCIONES (llama una en cada estado):
    dron.quieto()        dron.despegar()      dron.aterrizar()
    dron.avanzar()       dron.retroceder()    dron.izquierda()     dron.derecha()
    dron.subir()         dron.bajar()         dron.girar()         dron.girar("izquierda")
    dron.buscar("izquierda")   gira buscando el objetivo. Si lo acaba de perder, gira hacia donde lo vio.
    dron.centrar()             gira y sube/baja con control P hasta dejar el objetivo en el centro
    dron.acercarse()           avanza hacia el objetivo sin dejar de centrarlo
    dron.mover(adelante=0, derecha=0, subir=0, giro=0)    tú decides cada velocidad (de -30 a 30)
    dron.seguir_color()  dron.rescatar()  dron.patrullar()  dron.regresar_a_base()   <- los de la Sesión 7

SENSORES (s = dron.sensores(estado)):
    s.tecla       la tecla que presionaste ("" si ninguna)
    s.segundos    cuántos segundos llevas en el estado actual
    s.en_el_aire  True si está volando
    s.altura      altura en cm
    s.bateria     batería en %
    s.foto        lo que ve la cámara en este momento (una imagen de 640 x 480)

    s.veo_aruco   True si ve el ArUco que le pediste con  dron.sensores(estado, aruco=ID)
    s.ids_visibles  lista con los IDs de todos los ArUcos que ve
    s.veo_color   True si ve el color objetivo        s.veo_rojo   s.veo_verde   s.veo_azul

    s.error_x     qué tan lejos está el objetivo del centro (pixeles, + = derecha)
    s.error_y     lo mismo pero en vertical (pixeles, + = arriba)
    s.centrado    True si el objetivo está casi en el centro
    s.distancia   a cuántos cm está el ArUco (999 si no lo ve)
    s.cerca       True si el objetivo ya está cerca

    s.en_base     True si está sobre la base (simulador)
    s.faltan      cuántos objetivos faltan
    s.rescatado   True cuando Blu ya fue rescatado
"""

import atexit
import math
import random
import time
import unicodedata

import cv2
import numpy as np

# =====================================================================
# AJUSTES (el staff los puede cambiar)
# =====================================================================
# --- Movimientos simples ---
VELOCIDAD = 20                # avanzar, retroceder, izquierda, derecha, bajar (0 a 100)
VELOCIDAD_SUBIR = 40          # subir
VELOCIDAD_GIRO = 30           # girar
VELOCIDAD_BUSQUEDA = 35       # buscar: más rápido = encuentra antes, pero la imagen sale más movida
VELOCIDAD_MAXIMA_MOVER = 30   # dron.mover(): ninguna velocidad pasa de aquí
ALTURA_MAXIMA = 220           # cm: arriba de esto el dron ya no sube más

# --- Objetivo "color" (Sesiones 6 y 7) ---
KP_GIRO = 0.12                # giro por cada pixel de error horizontal
KP_ALTURA = 0.10              # subida por cada pixel de error vertical
VELOCIDAD_MAXIMA = 25         # ninguna corrección pasa de aquí
TOLERANCIA_CENTRADO = 50      # pixeles: si |error_x| es menor, el color está "centrado"
AREA_MINIMA = 400             # manchas más chicas se ignoran (ruido, Sesión 4)
AREA_CERCA = 15000            # si la mancha mide más que esto, el objeto está "cerca"
SEGUNDOS_PARA_RESCATAR = 2    # rescatar(): cuánto hay que quedarse junto al objeto
VICTIMAS_REALES = 1           # con cámara o Tello: cuántos rescates cuentan para "faltan"

# --- Objetivo "aruco" (Sesión 8) ---
ARUCO_LADO_CM = 17            # ¡MÍDELO! lado del cuadro negro del marcador impreso, en cm
FOCAL = 610                   # "zoom" de la cámara del Tello en pixeles (para imágenes de 640 de ancho)
ARUCO_KP_GIRO = 0.08          # giro por cada pixel de error horizontal
ARUCO_KP_ALTURA = 0.18        # subida por cada pixel de error vertical
ARUCO_VELOCIDAD_MAXIMA = 20   # ninguna corrección de giro o altura pasa de aquí
ARUCO_ZONA_MUERTA = 8         # pixeles: errores más chicos no se corrigen (evita el temblor)
ARUCO_TOLERANCIA_X = 45       # pixeles: "centrado" si |error_x| es menor...
ARUCO_TOLERANCIA_Y = 60       # ...y |error_y| es menor
ARUCO_KP_AVANCE = 0.25        # acercarse: velocidad por cada cm de distancia (lejos = rápido)
ARUCO_AVANCE_MINIMO = 12      # acercarse: nunca más lento que esto
ARUCO_AVANCE_MAXIMO = 30      # acercarse: nunca más rápido que esto
ARUCO_CERCA_CM = 90           # s.cerca es True si el ArUco está a menos de esto
ARUCO_MEMORIA = 0.4           # segundos que "recuerda" el ArUco si la cámara lo pierde un instante

# --- Objetivo "blu" ---
DISTANCIA_RESCATE = 100       # cm: a esta distancia de Blu se hace el rescate
TOLERANCIA_RESCATE = 30       # cm: el simulador acepta entre 70 y 130 cm
SEGUNDOS_RESCATE = 3          # cuánto hay que quedarse ahí, en el estado "RESCATANDO"
BLU_ANCHO_CM = 20             # simulador: ancho de la parte azul de Blu

# --- Seguridad del Tello real ---
BATERIA_SEGURIDAD = 15        # con menos batería aterriza solo
SEGUNDOS_MAXIMOS_VUELO = 120  # después de este tiempo aterriza solo

COLORES = {  # rangos HSV de las Sesiones 4 y 6
    "rojo": [((0, 120, 70), (8, 255, 255)), ((170, 120, 70), (179, 255, 255))],
    "verde": [((40, 70, 50), (85, 255, 255))],
    "azul": [((100, 120, 50), (130, 255, 255))],
}

# Arena del simulador: 500 x 500 cm.
BASE = (250, 440)
MUNDOS = {
    "vacio": {"objetos": [], "consumo": 0.5},
    "patrulla": {"objetos": [], "consumo": 2.0},
    "rescate": {"objetos": [(110, 120, "verde"), (400, 170, "verde"), (330, 330, "verde")], "consumo": 0.6},
    "libre": {"objetos": [(120, 110, "verde"), (390, 120, "rojo"), (420, 330, "azul"), (140, 300, "verde")],
              "consumo": 0.7},
    # Tres ArUcos en zigzag: (x, y, ID)
    "zigzag": {"arucos": [(110, 300, 0), (390, 200, 1), (110, 90, 2)], "consumo": 0.4},
    # Blu aparece en un lugar distinto cada vez; el dron empieza en el centro
    "blu": {"blu": True, "base": (250, 250), "consumo": 0.4},
}

MODOS = ("simulador", "camara", "tello_sin_volar", "tello")
OBJETIVOS = {"color": "libre", "aruco": "zigzag", "blu": "blu"}  # objetivo -> su mundo de siempre
ANCHO, ALTO = 640, 480
DT = 1 / 30  # el simulador avanza 1/30 de segundo por vuelta
COLOR_BGR = {"rojo": (40, 40, 220), "verde": (60, 200, 60), "azul": (220, 100, 40)}
PALETA = [(57, 255, 20), (255, 166, 88), (102, 129, 247), (96, 204, 242), (255, 120, 210), (80, 220, 255),
          (150, 255, 150), (200, 160, 255)]
ACCIONES_EN_PANTALLA = {
    "quieto": "quieto", "despegar": "despegar", "aterrizar": "aterrizar", "avanzar": "avanzar ^",
    "retroceder": "retroceder v", "izquierda": "< izquierda", "derecha": "derecha >", "subir": "subir",
    "bajar": "bajar", "girar": "girar", "buscar": "buscar", "centrar": "centrar", "mover": "mover",
    "seguir_color": "seguir color", "acercarse": "acercarse", "rescatar": "rescatar", "patrullar": "patrullar",
    "regresar_a_base": "regresar a base",
}


def _limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def _ascii(texto):
    """putText no sabe escribir acentos: los quitamos solo para dibujar."""
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def _color_de_estado(nombre):
    return PALETA[sum(ord(c) for c in nombre) % len(PALETA)]


def _numero(valor):
    """Convierte lo que le pasen a dron.mover() en una velocidad segura."""
    try:
        return _limitar(float(valor), -VELOCIDAD_MAXIMA_MOVER, VELOCIDAD_MAXIMA_MOVER)
    except (TypeError, ValueError):
        return 0.0


def _detector_de_arucos():
    """Regresa una función  gris -> (esquinas, ids)  que sirve en versiones nuevas y viejas de OpenCV."""
    if not hasattr(cv2, "aruco"):
        raise SystemExit("No encuentro cv2.aruco. Instala:  pip install opencv-contrib-python")
    aruco = cv2.aruco
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parametros = aruco.DetectorParameters() if hasattr(aruco, "DetectorParameters") else aruco.DetectorParameters_create()
    # Ventanas más variadas y bordes más tolerantes: aguanta mejor la imagen movida y los cambios de luz
    parametros.adaptiveThreshWinSizeMin = 5
    parametros.adaptiveThreshWinSizeMax = 35
    parametros.adaptiveThreshWinSizeStep = 10
    parametros.polygonalApproxAccuracyRate = 0.05
    if hasattr(aruco, "ArucoDetector"):
        detector = aruco.ArucoDetector(diccionario, parametros)
        return lambda gris: detector.detectMarkers(gris)[:2]
    return lambda gris: aruco.detectMarkers(gris, diccionario, parameters=parametros)[:2]


def _imagen_aruco(id_marcador):
    """El marcador con su orilla blanca (sin orilla blanca no se puede detectar)."""
    aruco = cv2.aruco
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    if hasattr(aruco, "generateImageMarker"):
        marcador = aruco.generateImageMarker(diccionario, id_marcador, 200, borderBits=1)
    else:
        marcador = aruco.drawMarker(diccionario, id_marcador, 200, borderBits=1)
    hoja = np.full((260, 260), 255, np.uint8)
    hoja[30:230, 30:230] = marcador
    return cv2.cvtColor(hoja, cv2.COLOR_GRAY2BGR), ARUCO_LADO_CM * 260 / 200  # imagen, ancho en cm


def _imagen_blu():
    """Blu en su caja, dibujado con puras figuras de OpenCV (Sesión 4). Regresa imagen y su ancho en cm."""
    img = np.full((360, 300, 3), (215, 232, 240), np.uint8)
    cv2.rectangle(img, (0, 0), (299, 359), (60, 80, 110), 6)
    azul, oscuro = (205, 105, 25), (150, 65, 15)
    cv2.fillPoly(img, [np.int32([(128, 270), (172, 270), (162, 338), (138, 338)])], oscuro)  # cola
    cv2.ellipse(img, (150, 205), (60, 88), 0, 0, 360, azul, -1, cv2.LINE_AA)  # cuerpo
    cv2.ellipse(img, (182, 215), (26, 66), -12, 0, 360, oscuro, -1, cv2.LINE_AA)  # ala
    for dx in (-22, 0, 22):
        cv2.ellipse(img, (150 + dx, 48), (9, 22), dx, 0, 360, azul, -1, cv2.LINE_AA)  # cresta
    cv2.circle(img, (150, 100), 54, azul, -1, cv2.LINE_AA)  # cabeza
    for x in (128, 172):
        cv2.circle(img, (x, 92), 15, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (x + (3 if x < 150 else -3), 94), 7, (20, 20, 20), -1, cv2.LINE_AA)
    cv2.fillPoly(img, [np.int32([(136, 112), (164, 112), (150, 142)])], (50, 50, 50), cv2.LINE_AA)  # pico
    bajo, alto = COLORES["azul"][0]
    _, _, ancho_azul, _ = cv2.boundingRect(cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), bajo, alto))
    return img, BLU_ANCHO_CM * img.shape[1] / ancho_azul


def _pegar(img, estampa, u, v, ancho_px):
    """Pega una imagen (estampa) centrada en (u, v) con el ancho indicado, recortando lo que se salga."""
    escala = ancho_px / estampa.shape[1]
    w, h = int(round(ancho_px)), int(round(estampa.shape[0] * escala))
    if w < 2 or h < 2 or w > 2500:
        return
    x0, y0 = int(round(u - w / 2)), int(round(v - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(img.shape[1], x0 + w), min(img.shape[0], y0 + h)
    if xa >= xb or ya >= yb:
        return
    chica = cv2.resize(estampa, (w, h), interpolation=cv2.INTER_AREA if escala < 1 else cv2.INTER_LINEAR)
    img[ya:yb, xa:xb] = chica[ya - y0:yb - y0, xa - x0:xb - x0]


def _fondo_simulado():
    horizonte = ALTO // 2
    fondo = np.zeros((ALTO, ANCHO, 3), np.uint8)
    fondo[:horizonte] = (70, 60, 52)
    for fila in range(horizonte, ALTO):
        tono = 60 + int(50 * (fila - horizonte) / (ALTO - horizonte))
        fondo[fila] = (tono, tono + 8, tono + 14)
    return fondo


def foto_de_blu(distancia_cm=150, a_la_derecha_cm=0, arriba_cm=0):
    """Una foto de prueba: Blu visto desde cierta distancia. Regresa (foto, ancho de la parte azul en pixeles)."""
    foto = _fondo_simulado()
    estampa, ancho_cm = _imagen_blu()
    k = FOCAL / distancia_cm
    _pegar(foto, estampa, ANCHO / 2 + k * a_la_derecha_cm, ALTO / 2 - k * arriba_cm, k * ancho_cm)
    return foto, k * BLU_ANCHO_CM


class Sensores:
    """Todo lo que el dron sabe en este momento."""

    def __init__(self, **datos):
        self.__dict__.update(datos)

    def __repr__(self):
        return "Sensores(" + ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if k != "foto") + ")"


class Dron:
    def __init__(self, modo="simulador", color="verde", mundo=None, bateria=100, objetivo="color"):
        if modo not in MODOS:
            raise SystemExit(f"Modo '{modo}' no existe. Usa uno de estos: {', '.join(MODOS)}")
        if color not in COLORES:
            raise SystemExit(f"Color '{color}' no existe. Usa uno de estos: {', '.join(COLORES)}")
        if objetivo not in OBJETIVOS:
            raise SystemExit(f"Objetivo '{objetivo}' no existe. Usa uno de estos: {', '.join(OBJETIVOS)}")
        mundo = OBJETIVOS[objetivo] if mundo is None else mundo
        if mundo not in MUNDOS:
            raise SystemExit(f"Mundo '{mundo}' no existe. Usa uno de estos: {', '.join(MUNDOS)}")

        self.modo, self.color, self.objetivo = modo, color, objetivo
        self._ventana = f"Dron - modo {modo}  (q = salir)"
        self._activo, self._terminado = True, False
        self._accion, self._args, self._rc = "quieto", {}, (0, 0, 0, 0)
        self._accion_mostrada = "quieto"
        self._estado, self._inicio_estado, self._historial = None, 0.0, []
        self._mensaje, self._mensaje_hasta, self._festejo = "", 0.0, ""
        self._t, self._t0 = 0.0, time.time()
        self._tecla = ""
        self._vision = self._vision_vacia()
        self._en_el_aire, self._fase, self._fase_desde = False, "tierra", 0.0
        self._z, self._altura, self._bateria = 0.0, 0.0, float(bateria)  # _z = altura simulada
        self._dt, self._fondo, self._nativo = DT, None, None
        self._rescatados, self._progreso_rescate = 0, 0.0
        self._sin_despegar, self._t_despegue = False, None
        self._ya_volo, self._mision_cumplida = False, False
        self._base, self._objetos, self._victimas = BASE, [], 0

        # ArUco
        self._aruco_id, self._aruco, self._aruco_memoria = None, self._aruco_vacio(), None
        self._ultimo_lado, self._ultimo_visto = 0, -99.0
        self._detectar = _detector_de_arucos() if objetivo == "aruco" else None
        # Blu
        self._marca, self._rescatado, self._progreso_blu = {}, False, 0.0

        if modo == "simulador":
            datos = MUNDOS[mundo]
            self._base = datos.get("base", BASE)
            self._x, self._y, self._yaw = float(self._base[0]), float(self._base[1]), 0.0
            self._consumo = datos["consumo"]
            self._objetos = [{"tipo": "bola", "x": x, "y": y, "color": c, "z": 60, "rescatado": False}
                             for x, y, c in datos.get("objetos", [])]
            for x, y, id_marcador in datos.get("arucos", []):
                estampa, ancho_cm = _imagen_aruco(id_marcador)
                self._objetos.append({"tipo": "aruco", "x": x, "y": y, "z": 120, "id": id_marcador,
                                      "visitado": False, "estampa": estampa, "ancho_cm": ancho_cm})
            if datos.get("blu"):
                angulo, radio = math.radians(random.uniform(40, 320)), random.uniform(160, 205)
                estampa, ancho_cm = _imagen_blu()
                self._objetos.append({"tipo": "blu", "x": self._base[0] + radio * math.sin(angulo),
                                      "y": self._base[1] - radio * math.cos(angulo), "z": 115,
                                      "estampa": estampa, "ancho_cm": ancho_cm})
            self._rastro, self._punto_patrulla = [], 0
        if objetivo == "color":
            self._victimas = sum(1 for o in self._objetos if o.get("color") == color) if modo == "simulador" \
                else VICTIMAS_REALES

        if modo == "camara":
            self._camara = cv2.VideoCapture(0)
            if not self._camara.isOpened():
                raise SystemExit("No pude abrir la webcam. ¿Otra app la está usando?")
        elif modo in ("tello_sin_volar", "tello"):
            from djitellopy import Tello  # solo se necesita para el Tello real
            self._tello = Tello()
            self._tello.connect()
            self._bateria = float(self._tello.get_battery())
            print(f"Tello conectado. Batería: {self._bateria:.0f}%")
            self._tello.streamon()
            self._lector = self._tello.get_frame_read()
            time.sleep(2)
            atexit.register(self._terminar)  # si el programa truena, el dron aterriza

        cv2.namedWindow(self._ventana)
        que = {"color": f"el color {color}", "aruco": "ArUcos", "blu": "a Blu (con TUS funciones)"}[objetivo]
        print(f"\nDron listo en modo '{modo}'. Busca {que}. Presiona q en la ventana para salir.\n")

    # -----------------------------------------------------------------
    # El ciclo
    # -----------------------------------------------------------------
    def sigue(self):
        """True mientras la misión siga. Se vuelve False al presionar q o cerrar la ventana."""
        if not self._activo:
            self._terminar()
        return self._activo

    def sensores(self, estado, aruco=None):
        """Regresa lo que el dron sabe. Con aruco=ID le dices cuál marcador te interesa."""
        estado = str(estado)
        if aruco is not None and aruco != self._aruco_id:
            self._aruco_id, self._aruco_memoria, self._ultimo_lado = aruco, None, 0
        anterior = self._t
        self._t = self._t + DT if self.modo == "simulador" else time.time() - self._t0
        self._dt = self._t - anterior

        # 1) Hacer lo que tu programa pidió en la vuelta anterior
        self._aplicar(self._accion)
        self._accion, self._args = "quieto", {}

        # 2) ¿Cambió el estado?
        if estado != self._estado:
            self._estado, self._inicio_estado = estado, self._t
            self._historial.append(estado)
            print(f"[{self._t:6.1f} s]  ->  {estado}")

        # 3) Ver y revisar la seguridad
        frame = self._leer_camara()
        self._vision = self._ver(frame) if self.objetivo == "color" else self._vision_vacia()
        self._aruco = self._ver_arucos() if self.objetivo == "aruco" else self._aruco_vacio()
        self._seguridad()
        self._revisar_blu()
        self._revisar_mision()

        v, a = self._vision, self._aruco
        veo, error_x, error_y, distancia = self._blanco()
        s = Sensores(
            tecla="", segundos=round(self._t - self._inicio_estado, 1), en_el_aire=self._en_el_aire,
            altura=int(self._altura), bateria=int(self._bateria), foto=frame.copy(),
            veo_aruco=a["veo"], ids_visibles=a["visibles"],
            veo_color=v["veo"], veo_rojo=v["rojo"] is not None, veo_verde=v["verde"] is not None,
            veo_azul=v["azul"] is not None,
            error_x=error_x, error_y=error_y, distancia=distancia,
            centrado=a["centrado"] if self.objetivo == "aruco" else v["centrado"],
            cerca=(veo and distancia <= ARUCO_CERCA_CM) if self.objetivo == "aruco" else v["cerca"],
            en_base=self._en_base(), faltan=self._faltan(), rescatado=self._rescatado,
        )

        # 4) Dibujar y leer el teclado
        cv2.imshow(self._ventana, self._dibujar(frame, s))
        self._marca = {}
        k = cv2.waitKey(30 if self.modo == "simulador" else 1)
        self._tecla = chr(k).lower() if 0 <= k < 256 else ""
        s.tecla = self._tecla
        if self._tecla == "q" or cv2.getWindowProperty(self._ventana, cv2.WND_PROP_VISIBLE) < 1:
            self._activo = False
        return s

    # -----------------------------------------------------------------
    # Acciones: cada una solo anota qué quieres hacer en esta vuelta
    # -----------------------------------------------------------------
    def quieto(self): self._accion = "quieto"
    def despegar(self): self._accion = "despegar"
    def aterrizar(self): self._accion = "aterrizar"
    def avanzar(self): self._accion = "avanzar"
    def retroceder(self): self._accion = "retroceder"
    def izquierda(self): self._accion = "izquierda"
    def derecha(self): self._accion = "derecha"
    def subir(self): self._accion = "subir"
    def bajar(self): self._accion = "bajar"
    def seguir_color(self): self._accion = "seguir_color"
    def centrar(self): self._accion = "centrar"
    def acercarse(self): self._accion = "acercarse"
    def rescatar(self): self._accion = "rescatar"
    def patrullar(self): self._accion = "patrullar"
    def regresar_a_base(self): self._accion = "regresar_a_base"

    def girar(self, lado="derecha"):
        """Gira sobre su lugar hacia "derecha" o "izquierda"."""
        self._accion, self._args = "girar", {"sentido": -1 if str(lado).lower().startswith("i") else 1}

    def buscar(self, lado="derecha"):
        """Gira buscando el objetivo. Si lo acaba de perder, gira hacia donde lo vio por última vez."""
        self._accion, self._args = "buscar", {"sentido": -1 if str(lado).lower().startswith("i") else 1}

    def mover(self, adelante=0, derecha=0, subir=0, giro=0):
        """Tú decides cada velocidad. Positivo = adelante / derecha / arriba / giro a la derecha."""
        self._accion = "mover"
        self._args = {"rc": (_numero(derecha), _numero(adelante), _numero(subir), _numero(giro))}

    def mostrar(self, caja=None, mascara=None, distancia=0):
        """Actividad de Blu: dibuja en la pantalla lo que encontraron TUS funciones."""
        marca = {"caja": None, "mascara": None, "distancia": 0, "llamado": True}
        try:
            if caja is not None and len(caja) == 4:
                marca["caja"] = tuple(int(n) for n in caja)
            if isinstance(mascara, np.ndarray) and mascara.ndim == 2:
                marca["mascara"] = mascara.astype(np.uint8)
            marca["distancia"] = float(distancia or 0)
        except (TypeError, ValueError):
            pass
        self._marca = marca

    # -----------------------------------------------------------------
    # Por dentro (no necesitas leer de aquí para abajo)
    # -----------------------------------------------------------------
    def _avisar(self, texto, segundos=3):
        if texto != self._mensaje or self._t > self._mensaje_hasta:
            print(f"[{self._t:6.1f} s]  {texto}")
        self._mensaje, self._mensaje_hasta = texto, self._t + segundos

    def _blanco(self):
        """Lo que el dron persigue: (lo veo, error_x, error_y, distancia en cm)."""
        if self.objetivo == "aruco":
            a = self._aruco
            return a["veo"], a["error_x"], a["error_y"], a["distancia"]
        v = self._vision
        return v["veo"], v["error_x"], v["error_y"], 999

    def _faltan(self):
        if self.objetivo == "aruco":
            return sum(1 for o in self._objetos if o["tipo"] == "aruco" and not o["visitado"])
        if self.objetivo == "blu":
            return 0 if self._rescatado else 1
        return max(0, self._victimas - self._rescatados)

    def _rc_para(self, accion):
        """Convierte una acción en (izquierda/derecha, adelante/atrás, arriba/abajo, giro), como send_rc_control."""
        veo, error_x, error_y, distancia = self._blanco()
        if self.objetivo == "aruco":
            kp_giro, kp_altura, maxima, zona = ARUCO_KP_GIRO, ARUCO_KP_ALTURA, ARUCO_VELOCIDAD_MAXIMA, ARUCO_ZONA_MUERTA
        else:
            kp_giro, kp_altura, maxima, zona = KP_GIRO, KP_ALTURA, VELOCIDAD_MAXIMA, 0
        # El control P de la Sesión 5: corrección = KP * error (sin pasarse de la máxima)
        giro = _limitar(kp_giro * error_x, -maxima, maxima) if veo and abs(error_x) > zona else 0
        subir = _limitar(kp_altura * error_y, -maxima, maxima) if veo and abs(error_y) > zona else 0

        if accion == "avanzar":
            return (0, VELOCIDAD, 0, 0)
        if accion == "retroceder":
            return (0, -VELOCIDAD, 0, 0)
        if accion == "izquierda":
            return (-VELOCIDAD, 0, 0, 0)
        if accion == "derecha":
            return (VELOCIDAD, 0, 0, 0)
        if accion == "subir":
            return (0, 0, VELOCIDAD_SUBIR, 0)
        if accion == "bajar":
            return (0, 0, -VELOCIDAD, 0)
        if accion == "girar":
            return (0, 0, 0, self._args.get("sentido", 1) * VELOCIDAD_GIRO)
        if accion == "buscar":
            sentido = self._args.get("sentido", 1)
            if self._ultimo_lado and self._t - self._ultimo_visto < 3:
                sentido = self._ultimo_lado  # lo acaba de perder: regresa hacia donde lo vio
            return (0, 0, 0, sentido * VELOCIDAD_BUSQUEDA)
        if accion == "mover":
            return self._args.get("rc", (0, 0, 0, 0))
        if accion in ("seguir_color", "centrar"):
            return (0, 0, subir, giro)
        if accion == "acercarse" and self.objetivo == "aruco":
            if not veo:
                return (0, 0, 0, 0)
            # Lejos avanza rápido, cerca avanza despacio; si está muy descentrado, frena para corregir
            adelante = _limitar(ARUCO_KP_AVANCE * distancia, ARUCO_AVANCE_MINIMO, ARUCO_AVANCE_MAXIMO)
            return (0, adelante * max(0.3, 1 - abs(error_x) / 200), subir, giro)
        area = self._vision["caja"][4] if self._vision["veo"] else 0
        if accion == "acercarse":  # avanza hasta un poco después de "cerca", para no quedar en la orilla
            adelante = VELOCIDAD if veo and area < AREA_CERCA * 1.2 and abs(error_x) < 120 else 0
            return (0, adelante, subir, giro)
        if accion == "rescatar":  # se arrima despacito y se queda junto al objeto
            adelante = 10 if veo and area < AREA_CERCA * 1.1 and abs(error_x) < 120 else 0
            return (0, adelante, subir, giro)
        if accion == "patrullar":
            return (0, 15, 0, 20)  # en el Tello real: un círculo lento
        return (0, 0, 0, 0)

    def _aplicar(self, accion):
        rc = self._rc_para(accion)
        if rc[2] > 0 and self._altura >= ALTURA_MAXIMA:
            rc = (rc[0], rc[1], 0, rc[3])
            self._avisar(f"Altura máxima ({ALTURA_MAXIMA} cm): ya no sube más")

        # Despegar y aterrizar
        if accion == "despegar" and not self._en_el_aire and self._fase == "tierra":
            self._iniciar_despegue()
        elif accion == "aterrizar" and self._en_el_aire:
            self._iniciar_aterrizaje()
        self._avanzar_fases()

        # Rescatar (Sesión 7): quedarse junto al objeto, centrado y cerca, unos segundos
        if accion == "rescatar" and self._en_el_aire:
            v = self._vision
            if v["veo"] and v["centrado"] and v["caja"][4] >= AREA_CERCA * 0.8:
                self._progreso_rescate += self._dt
                if self._progreso_rescate >= SEGUNDOS_PARA_RESCATAR:
                    self._completar_rescate()
            else:
                self._progreso_rescate = 0.0
        else:
            self._progreso_rescate = 0.0

        if self.modo == "simulador":
            if accion == "patrullar":
                rc = self._ir_hacia(*self._puntos_patrulla()[self._punto_patrulla])
                if math.hypot(*np.subtract(self._puntos_patrulla()[self._punto_patrulla], (self._x, self._y))) < 30:
                    self._punto_patrulla = (self._punto_patrulla + 1) % 4
            elif accion == "regresar_a_base":
                lejos = math.hypot(self._base[0] - self._x, self._base[1] - self._y) > 12
                rc = self._ir_hacia(*self._base, velocidad=30) if lejos else (0, 0, 0, 0)
            self._mover_simulador(rc)
        elif accion == "regresar_a_base":
            rc = (0, 0, 0, 0)
            self._avisar("regresar_a_base() solo funciona en el simulador: el dron se queda quieto")

        if self.modo in ("camara", "tello_sin_volar"):
            self._rc = rc  # aquí nada se mueve: solo mostramos la orden que se mandaría
        else:
            self._rc = rc if self._en_el_aire and self._fase == "aire" else (0, 0, 0, 0)
        self._accion_mostrada = accion
        if self.modo == "tello" and self._en_el_aire and self._fase == "aire":
            self._tello.send_rc_control(*[int(x) for x in self._rc])

    def _iniciar_despegue(self):
        if self._sin_despegar:
            self._avisar("Despegue bloqueado por seguridad (batería o tiempo de vuelo)")
            return
        if self.modo == "tello":
            if self._bateria < BATERIA_SEGURIDAD + 5:
                self._avisar("Batería muy baja para despegar")
                return
            self._avisar("Despegando...")
            try:
                self._tello.takeoff()
            except Exception as error:
                self._avisar(f"El Tello no pudo despegar: {error}")
                return
            self._fase, self._en_el_aire, self._t_despegue, self._ya_volo = "aire", True, self._t, True
        else:
            self._fase, self._fase_desde = "despegando", self._t

    def _iniciar_aterrizaje(self):
        if self.modo == "tello":
            self._tello.send_rc_control(0, 0, 0, 0)
            try:
                self._tello.land()
            except Exception as error:
                self._avisar(f"Error al aterrizar: {error}")
            self._fase, self._en_el_aire = "tierra", False
        else:
            self._fase, self._fase_desde = "aterrizando", self._t

    def _avanzar_fases(self):
        """Despegar y aterrizar toman unos segundos (excepto en el Tello real, que lo hace él solo)."""
        if self.modo == "tello":
            self._altura = self._tello.get_distance_tof() if self._en_el_aire else 0
            return
        paso = 40 * self._dt
        if self._fase == "despegando":
            self._z = min(80, self._z + paso)
            if self._z >= 80:
                self._fase, self._en_el_aire, self._ya_volo = "aire", True, True
        elif self._fase == "aterrizando":
            self._z = max(0, self._z - paso)
            if self._z <= 0:
                self._fase, self._en_el_aire = "tierra", False
        # El sensor de altura: en tello_sin_volar es el ToF real; en los demás, la altura simulada
        self._altura = self._tello.get_distance_tof() if self.modo == "tello_sin_volar" else self._z

    def _completar_rescate(self):
        self._progreso_rescate = 0.0
        if self.modo == "simulador":
            cercanos = [o for o in self._objetos if o["tipo"] == "bola" and not o["rescatado"] and o["color"] == self.color]
            if not cercanos:
                return
            objetivo = min(cercanos, key=lambda o: math.hypot(o["x"] - self._x, o["y"] - self._y))
            objetivo["rescatado"] = True
        self._rescatados += 1
        self._avisar(f"RESCATADO! Faltan {max(0, self._victimas - self._rescatados)}")

    def _seguridad(self):
        if self.modo in ("tello", "tello_sin_volar"):
            self._bateria = float(self._tello.get_battery())
        if self.modo != "tello" or not self._en_el_aire:
            return
        if self._bateria < BATERIA_SEGURIDAD:
            self._avisar("Batería en nivel de seguridad: aterrizaje automático", 6)
        elif self._t - self._t_despegue > SEGUNDOS_MAXIMOS_VUELO:
            self._avisar("Tiempo máximo de vuelo: aterrizaje automático", 6)
        else:
            return
        self._sin_despegar = True
        self._iniciar_aterrizaje()

    def _revisar_blu(self):
        """El rescate cuenta mientras el estado se llame RESCATANDO y el dron esté a ~1 m viendo a Blu."""
        if self.objetivo != "blu" or self._rescatado:
            return
        if self._estado != "RESCATANDO":
            self._progreso_blu = 0.0
            return
        if self.modo == "simulador":
            en_posicion = self._fase == "aire" and self._frente_a_blu()
        else:  # en la vida real no hay forma de medirlo: confiamos en lo que ven tus funciones
            en_posicion = self._en_el_aire and self._marca.get("caja") is not None
        if en_posicion:
            self._progreso_blu += self._dt
        if self._progreso_blu >= SEGUNDOS_RESCATE - 0.3:
            self._rescatado, self._festejo = True, "BLU RESCATADO!"
            self._avisar("BLU RESCATADO! Ahora aterriza", 10)

    def _distancia_real_a_blu(self):
        blu = next((o for o in self._objetos if o["tipo"] == "blu"), None)
        return None if blu is None else math.hypot(blu["x"] - self._x, blu["y"] - self._y)

    def _frente_a_blu(self):
        blu = next((o for o in self._objetos if o["tipo"] == "blu"), None)
        if blu is None:
            return False
        rumbo = math.degrees(math.atan2(blu["x"] - self._x, -(blu["y"] - self._y)))
        desviado = abs((rumbo - self._yaw + 180) % 360 - 180)
        return desviado < 20 and abs(self._distancia_real_a_blu() - DISTANCIA_RESCATE) <= TOLERANCIA_RESCATE

    def _revisar_arucos(self):
        """Simulador: un ArUco cuenta como visitado cuando el dron llega cerca de él, en orden."""
        pendientes = [o for o in self._objetos if o["tipo"] == "aruco" and not o["visitado"]]
        if not pendientes or self._fase != "aire":
            return
        siguiente = pendientes[0]
        if math.hypot(siguiente["x"] - self._x, siguiente["y"] - self._y) < 130:
            siguiente["visitado"] = True
            if len(pendientes) == 1:
                self._festejo = "ZIGZAG COMPLETO!"
                self._avisar("ZIGZAG COMPLETO! Ahora aterriza", 10)
            else:
                self._avisar(f"Llegaste al ArUco {siguiente['id']}. Faltan {len(pendientes) - 1}")

    def _revisar_mision(self):
        if self.modo != "simulador" or self._mision_cumplida or not self._ya_volo or self._fase != "tierra":
            return
        if self.objetivo == "color":
            lista = self._en_base() and self._rescatados >= self._victimas
        else:
            lista = self._faltan() == 0
        if lista:
            self._mision_cumplida = True
            self._avisar("MISION CUMPLIDA!", 10)

    def _en_base(self):
        return self.modo == "simulador" and math.hypot(self._base[0] - self._x, self._base[1] - self._y) < 30

    # ---------------- Simulador ----------------
    @staticmethod
    def _puntos_patrulla():
        return [(110, 110), (390, 110), (390, 350), (110, 350)]

    def _ir_hacia(self, x, y, velocidad=VELOCIDAD):
        dx, dy = x - self._x, y - self._y
        rumbo = math.degrees(math.atan2(dx, -dy))
        error = (rumbo - self._yaw + 180) % 360 - 180
        giro = _limitar(1.2 * error, -40, 40)
        adelante = min(velocidad, math.hypot(dx, dy)) if abs(error) < 25 else 0
        return (0, adelante, 0, giro)

    def _mover_simulador(self, rc):
        if self._en_el_aire:
            self._bateria = max(0.0, self._bateria - self._consumo * DT)
            if self._bateria <= 0 and self._fase == "aire":
                self._avisar("SIN BATERIA: aterrizaje forzoso", 6)
                self._iniciar_aterrizaje()
        if self._fase != "aire":
            return
        lado, adelante, arriba, giro = rc
        self._yaw = (self._yaw + giro * 1.5 * DT) % 360
        rad = math.radians(self._yaw)
        self._x += (math.sin(rad) * adelante + math.cos(rad) * lado) * 1.5 * DT
        self._y += (-math.cos(rad) * adelante + math.sin(rad) * lado) * 1.5 * DT
        self._x, self._y = _limitar(self._x, 15, 485), _limitar(self._y, 15, 485)
        self._z = _limitar(self._z + arriba * 1.5 * DT, 30, 250)
        self._altura = self._z
        self._rastro = (self._rastro + [(self._x, self._y)])[-600:]
        self._revisar_arucos()

    def _camara_simulada(self):
        horizonte = ALTO // 2
        if self._fondo is None:
            self._fondo = _fondo_simulado()
        img = self._fondo.copy()
        rad = math.radians(self._yaw)
        visibles = []
        for o in self._objetos:
            if o.get("rescatado"):
                continue
            dx, dy = o["x"] - self._x, o["y"] - self._y
            frente = dx * math.sin(rad) - dy * math.cos(rad)
            lado = dx * math.cos(rad) + dy * math.sin(rad)
            if frente > 25:
                visibles.append((frente, lado, o))
        for frente, lado, o in sorted(visibles, key=lambda t: -t[0]):  # primero lo más lejano
            k = FOCAL / frente  # pixeles por cada cm, a esa distancia
            u = int(ANCHO / 2 + k * lado)
            v = int(horizonte + k * (self._z - o["z"]))
            piso = int(horizonte + k * self._z)
            if o["tipo"] == "bola":
                r = max(2, int(k * 15))
                cv2.line(img, (u, v), (u, piso), (90, 90, 90), max(1, r // 6))
                cv2.circle(img, (u, v), r, COLOR_BGR[o["color"]], -1, cv2.LINE_AA)
                cv2.circle(img, (u - r // 3, v - r // 3), max(1, r // 5), (240, 240, 240), -1, cv2.LINE_AA)
                continue
            ancho = k * o["ancho_cm"]
            alto = ancho * o["estampa"].shape[0] / o["estampa"].shape[1]
            abajo = int(v + alto / 2)
            if o["tipo"] == "aruco":  # un letrero sobre un poste
                cv2.line(img, (u, abajo), (u, piso), (90, 90, 90), max(2, int(k * 3)))
            else:  # Blu está sobre una pila de cajas
                mitad = int(ancho * 0.42)
                cv2.rectangle(img, (u - mitad, abajo), (u + mitad, piso), (70, 105, 150), -1)
                for nivel in range(1, 4):
                    y = abajo + (piso - abajo) * nivel // 4
                    cv2.line(img, (u - mitad, y), (u + mitad, y), (45, 70, 105), max(1, int(k)))
            _pegar(img, o["estampa"], u, v, ancho)
        return img

    def _mapa(self):
        lado = 600
        k = lado / 500
        mapa = np.full((lado, lado, 3), (35, 27, 21), np.uint8)
        for i in range(0, 501, 50):
            cv2.line(mapa, (int(i * k), 0), (int(i * k), lado), (55, 45, 38), 1)
            cv2.line(mapa, (0, int(i * k)), (lado, int(i * k)), (55, 45, 38), 1)
        bx, by = int(self._base[0] * k), int(self._base[1] * k)
        cv2.circle(mapa, (bx, by), int(30 * k), (90, 90, 90), 2)
        cv2.putText(mapa, "H", (bx - 10, by + 10), cv2.FONT_HERSHEY_DUPLEX, 0.9, (150, 150, 150), 2)
        for o in self._objetos:
            p = (int(o["x"] * k), int(o["y"] * k))
            if o["tipo"] == "aruco":
                color = (60, 200, 60) if o["visitado"] else (235, 235, 235)
                cv2.rectangle(mapa, (p[0] - 16, p[1] - 16), (p[0] + 16, p[1] + 16), color, -1)
                cv2.putText(mapa, str(o["id"]), (p[0] - 8, p[1] + 9), cv2.FONT_HERSHEY_DUPLEX, 0.8, (20, 20, 20), 2)
            elif o["tipo"] == "blu":
                color = (60, 200, 60) if self._rescatado else (120, 120, 120)
                cv2.circle(mapa, p, int(DISTANCIA_RESCATE * k), color, 1, cv2.LINE_AA)  # la zona de rescate: 1 m
                cv2.rectangle(mapa, (p[0] - 13, p[1] - 13), (p[0] + 13, p[1] + 13), (70, 105, 150), -1)
                cv2.circle(mapa, p, 9, (205, 105, 25), -1, cv2.LINE_AA)
                cv2.putText(mapa, "Blu", (p[0] - 16, p[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 170, 90), 1, cv2.LINE_AA)
            elif o["rescatado"]:
                cv2.drawMarker(mapa, p, (110, 110, 110), cv2.MARKER_TILTED_CROSS, 22, 2)
            else:
                cv2.circle(mapa, p, int(15 * k), COLOR_BGR[o["color"]], -1, cv2.LINE_AA)
        if len(self._rastro) > 1:
            cv2.polylines(mapa, [np.int32([(x * k, y * k) for x, y in self._rastro])], False, (90, 140, 90), 1)
        x, y, rad = self._x * k, self._y * k, math.radians(self._yaw)
        campo = math.degrees(math.atan((ANCHO / 2) / FOCAL))  # lo que alcanza a ver la cámara
        for angulo in (-campo, campo):
            a = rad + math.radians(angulo)
            cv2.line(mapa, (int(x), int(y)), (int(x + 190 * math.sin(a)), int(y - 190 * math.cos(a))), (80, 80, 60), 1)
        tamano = 12 + self._z / 20
        puntas = [(math.sin(rad) * tamano, -math.cos(rad) * tamano),
                  (math.sin(rad + 2.5) * tamano * 0.8, -math.cos(rad + 2.5) * tamano * 0.8),
                  (math.sin(rad - 2.5) * tamano * 0.8, -math.cos(rad - 2.5) * tamano * 0.8)]
        color = (20, 255, 57) if self._en_el_aire else (160, 160, 160)
        cv2.fillPoly(mapa, [np.int32([(x + dx, y + dy) for dx, dy in puntas])], color, cv2.LINE_AA)
        real = self._distancia_real_a_blu()
        if real is not None:
            cv2.putText(mapa, f"distancia real a Blu: {real:.0f} cm", (12, lado - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (200, 200, 200), 1, cv2.LINE_AA)
        return mapa

    # ---------------- Cámara y visión ----------------
    def _leer_camara(self):
        if self.modo == "simulador":
            frame = self._camara_simulada()
        elif self.modo == "camara":
            ok, frame = self._camara.read()
            if not ok:
                frame = np.zeros((ALTO, ANCHO, 3), np.uint8)
            elif self.objetivo == "color":
                frame = cv2.flip(frame, 1)  # como espejo (con ArUcos no: al revés no se pueden leer)
        else:
            frame = self._lector.frame
            if frame is None:
                frame = np.zeros((ALTO, ANCHO, 3), np.uint8)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # djitellopy entrega la imagen en RGB
        self._nativo = frame  # los ArUcos se buscan en la imagen completa: así se reconocen desde más lejos
        return frame if frame.shape[:2] == (ALTO, ANCHO) else cv2.resize(frame, (ANCHO, ALTO))

    @staticmethod
    def _vision_vacia():
        return {"veo": False, "error_x": 0, "error_y": 0, "centrado": False, "cerca": False, "caja": None,
                "rojo": None, "verde": None, "azul": None}

    @staticmethod
    def _aruco_vacio():
        return {"veo": False, "fresco": False, "error_x": 0, "error_y": 0, "centrado": False, "distancia": 999,
                "centro": None, "visibles": [], "todos": []}

    def _ver(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        vision = self._vision_vacia()
        for nombre, rangos in COLORES.items():
            mascara = None
            for bajo, alto in rangos:
                m = cv2.inRange(hsv, bajo, alto)
                mascara = m if mascara is None else cv2.bitwise_or(mascara, m)
            contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            grandes = [c for c in contornos if cv2.contourArea(c) >= AREA_MINIMA]
            if grandes:
                mayor = max(grandes, key=cv2.contourArea)
                vision[nombre] = (*cv2.boundingRect(mayor), cv2.contourArea(mayor))
        caja = vision[self.color]
        if caja is not None:
            x, y, w, h, area = caja
            vision.update(veo=True, caja=caja, error_x=int(x + w / 2 - ANCHO / 2), error_y=int(ALTO / 2 - (y + h / 2)))
            vision["centrado"] = abs(vision["error_x"]) < TOLERANCIA_CENTRADO
            vision["cerca"] = area > AREA_CERCA
        return vision

    def _ver_arucos(self):
        nativo = self._nativo
        esquinas, ids = self._detectar(cv2.cvtColor(nativo, cv2.COLOR_BGR2GRAY))
        escala = (ANCHO / nativo.shape[1], ALTO / nativo.shape[0])  # a coordenadas de la imagen de 640 x 480
        a = self._aruco_vacio()
        if ids is not None:
            a["todos"] = [(int(i), e.reshape(4, 2).astype(float) * escala) for e, i in zip(esquinas, ids.flatten())]
        a["visibles"] = sorted({i for i, _ in a["todos"]})
        puntos = next((p for i, p in a["todos"] if i == self._aruco_id), None)
        if puntos is not None:
            # El lado más largo es el que menos se deforma cuando el marcador se ve chueco
            lado = max(float(np.linalg.norm(puntos[i] - puntos[(i + 1) % 4])) for i in range(4))
            cx, cy = puntos.mean(axis=0)
            datos = {"veo": True, "error_x": int(cx - ANCHO / 2), "error_y": int(ALTO / 2 - cy),
                     "centro": (int(cx), int(cy)),
                     # Mientras más lejos, más chico se ve:  distancia = tamaño real x focal / tamaño en pixeles
                     "distancia": int(ARUCO_LADO_CM * FOCAL / max(lado, 1))}
            a.update(datos, fresco=True)
            self._aruco_memoria = (self._t, datos)
            if abs(datos["error_x"]) > 20:
                self._ultimo_lado = 1 if datos["error_x"] > 0 else -1
            self._ultimo_visto = self._t
        elif self._aruco_memoria is not None and self._t - self._aruco_memoria[0] <= ARUCO_MEMORIA:
            a.update(self._aruco_memoria[1])  # se perdió un instante: seguimos con lo último que vimos
        a["centrado"] = a["veo"] and abs(a["error_x"]) < ARUCO_TOLERANCIA_X and abs(a["error_y"]) < ARUCO_TOLERANCIA_Y
        return a

    # ---------------- Dibujo ----------------
    def _dibujar(self, frame, s):
        camara = frame.copy()
        cx, cy = ANCHO // 2, ALTO // 2
        cv2.drawMarker(camara, (cx, cy), (255, 255, 255), cv2.MARKER_CROSS, 24, 2)
        if self.objetivo == "color":
            for nombre in COLORES:
                caja = self._vision[nombre]
                if caja is not None and nombre != self.color:
                    x, y, w, h, _ = caja
                    cv2.rectangle(camara, (x, y), (x + w, y + h), COLOR_BGR[nombre], 2)
            if self._vision["veo"]:
                x, y, w, h, _ = self._vision["caja"]
                self._apuntar(camara, (x, y, w, h))
        elif self.objetivo == "aruco":
            for id_marcador, puntos in self._aruco["todos"]:
                es_el_buscado = id_marcador == self._aruco_id
                color = (0, 255, 0) if es_el_buscado else (170, 170, 170)
                cv2.polylines(camara, [np.int32(puntos)], True, color, 3 if es_el_buscado else 2)
                x, y = np.int32(puntos.min(axis=0))
                cv2.putText(camara, f"ID {id_marcador}", (int(x), max(20, int(y) - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
            if self._aruco["veo"]:
                cv2.circle(camara, self._aruco["centro"], 6, (0, 0, 255), -1)
                cv2.line(camara, (cx, cy), self._aruco["centro"], (255, 0, 0), 2)
        else:
            self._dibujar_blu(camara)
        if self._festejo:
            cv2.rectangle(camara, (0, 0), (ANCHO, 54), (40, 150, 40), -1)
            cv2.putText(camara, self._festejo, (14, 40), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
        orden = "send_rc_control" + str(tuple(int(x) for x in self._rc))
        cv2.rectangle(camara, (0, ALTO - 34), (ANCHO, ALTO), (0, 0, 0), -1)
        cv2.putText(camara, orden, (10, ALTO - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (120, 230, 255), 2, cv2.LINE_AA)

        hud = self._hud(s)
        if self.modo == "simulador":
            derecha = np.vstack([cv2.resize(camara, (480, 360)), hud])
            return np.hstack([self._mapa(), derecha])
        izquierda = np.full((600, 600, 3), (23, 17, 13), np.uint8)
        izquierda[:450] = cv2.resize(camara, (600, 450))
        busca = {"color": f"color {self.color}", "aruco": "ArUcos", "blu": "Blu"}[self.objetivo]
        consejos = ["q = salir" + (" (y aterrizar)" if self.modo == "tello" else ""),
                    f"modo: {self.modo}   objetivo: {busca}"]
        if self.modo != "tello":
            consejos.append("Aqui el dron NO se mueve: mira la orden que mandaria")
        for i, texto in enumerate(consejos):
            cv2.putText(izquierda, _ascii(texto), (14, 490 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)
        derecha = np.full((600, 480, 3), (23, 17, 13), np.uint8)
        derecha[:240] = hud
        self._historial_grande(derecha)
        return np.hstack([izquierda, derecha])

    @staticmethod
    def _apuntar(camara, caja):
        x, y, w, h = caja
        centro = (x + w // 2, y + h // 2)
        cv2.rectangle(camara, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.circle(camara, centro, 6, (0, 0, 255), -1)
        cv2.line(camara, (ANCHO // 2, ALTO // 2), centro, (255, 0, 0), 2)

    def _dibujar_blu(self, camara):
        """Dibuja lo que encontraron las funciones del alumno (lo que mandó con dron.mostrar)."""
        marca = self._marca
        if marca.get("caja") is not None:
            self._apuntar(camara, marca["caja"])
            x, y, w, h = marca["caja"]
            texto = f"Blu a {marca['distancia']:.0f} cm" if marca["distancia"] > 0 else "Blu (falta la distancia)"
            cv2.putText(camara, texto, (max(0, x), max(24, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        if marca.get("mascara") is not None:  # la máscara chiquita en la esquina
            mini = cv2.resize(cv2.cvtColor(marca["mascara"], cv2.COLOR_GRAY2BGR), (160, 120))
            camara[62:182, ANCHO - 168:ANCHO - 8] = mini
            cv2.rectangle(camara, (ANCHO - 168, 62), (ANCHO - 8, 182), (200, 200, 200), 1)
        elif marca.get("llamado"):
            cv2.putText(camara, "Sin mascara: completa mascara_azul()", (10, ALTO - 48), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (80, 80, 255), 2, cv2.LINE_AA)

    def _hud(self, s):
        hud = np.full((240, 480, 3), (23, 17, 13), np.uint8)
        estado = _ascii(self._estado or "")
        color = _color_de_estado(estado)
        cv2.rectangle(hud, (0, 0), (480, 52), color, -1)
        cv2.putText(hud, estado[:22], (12, 38), cv2.FONT_HERSHEY_DUPLEX, 1.05, (13, 17, 23), 2, cv2.LINE_AA)
        cv2.putText(hud, f"{s.segundos:4.1f} s", (395, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (13, 17, 23), 2, cv2.LINE_AA)

        # Batería
        cv2.putText(hud, "bateria", (12, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.rectangle(hud, (90, 66), (250, 84), (90, 90, 90), 1)
        color_bateria = (57, 255, 20) if s.bateria > 40 else (40, 200, 240) if s.bateria > 20 else (60, 60, 255)
        cv2.rectangle(hud, (91, 67), (91 + int(158 * s.bateria / 100), 83), color_bateria, -1)
        cv2.putText(hud, f"{s.bateria}%", (258, 81), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_bateria, 1, cv2.LINE_AA)
        cv2.putText(hud, f"altura {s.altura} cm", (330, 81), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

        # Sensores sí / no, con los mismos nombres que usas en tu código
        accion = ACCIONES_EN_PANTALLA.get(self._accion_mostrada, "quieto")
        if self.objetivo == "aruco":
            banderas = [("en_el_aire", s.en_el_aire), ("veo_aruco", s.veo_aruco), ("centrado", s.centrado),
                        ("cerca", s.cerca)]
            distancia = f"{s.distancia} cm" if s.veo_aruco else "---"
            lineas = [f"busco el ID: {self._aruco_id}    veo los IDs: {s.ids_visibles}",
                      f"distancia: {distancia}   error_x: {s.error_x}   error_y: {s.error_y}",
                      f"accion: {accion}"]
        elif self.objetivo == "blu":
            marca = self._marca
            banderas = [("en_el_aire", s.en_el_aire), ("veo_a_blu", marca.get("caja") is not None),
                        ("rescatado", s.rescatado)]
            distancia = f"{marca['distancia']:.0f} cm" if marca.get("distancia", 0) > 0 else "---"
            lineas = [f"distancia segun tus funciones: {distancia}", f"accion: {accion}"]
            # La barra del rescate: se llena en el estado RESCATANDO, a 1 m de Blu
            avance = 1.0 if s.rescatado else min(1.0, self._progreso_blu / max(0.1, SEGUNDOS_RESCATE - 0.3))
            cv2.putText(hud, "rescate", (12, 141), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.rectangle(hud, (90, 128), (460, 144), (90, 90, 90), 1)
            cv2.rectangle(hud, (91, 129), (91 + int(368 * avance), 143), (57, 255, 20), -1)
        else:
            banderas = [("en_el_aire", s.en_el_aire), ("veo_color", s.veo_color), ("centrado", s.centrado),
                        ("cerca", s.cerca), ("veo_rojo", s.veo_rojo), ("veo_verde", s.veo_verde),
                        ("veo_azul", s.veo_azul), ("en_base", s.en_base)]
            lineas = [f"accion: {accion}   error_x: {s.error_x}   faltan: {s.faltan}"]
        for i, (nombre, valor) in enumerate(banderas):
            x, y = 12 + (i % 4) * 117, 112 + (i // 4) * 26
            cv2.circle(hud, (x + 6, y - 5), 6, (57, 255, 20) if valor else (70, 70, 70), -1)
            cv2.putText(hud, nombre, (x + 17, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220) if valor else (120, 120, 120), 1, cv2.LINE_AA)
        for i, texto in enumerate(lineas):
            y = 178 - 22 * (len(lineas) - 1 - i)
            cv2.putText(hud, _ascii(texto)[:56], (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 200, 120), 1, cv2.LINE_AA)
        camino = " > ".join(_ascii(e) for e in self._historial[-4:])
        cv2.putText(hud, camino[-62:], (12, 204), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)
        if self._t <= self._mensaje_hasta:
            cv2.putText(hud, _ascii(self._mensaje)[:48], (12, 230), cv2.FONT_HERSHEY_DUPLEX, 0.6, (60, 220, 255), 1, cv2.LINE_AA)
        return hud

    def _historial_grande(self, panel):
        cv2.putText(panel, "Historial de estados:", (12, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
        for i, estado in enumerate(self._historial[-10:]):
            nombre = _ascii(estado)
            cv2.putText(panel, f"{len(self._historial) - min(10, len(self._historial)) + i + 1}. {nombre}", (24, 305 + 28 * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, _color_de_estado(nombre), 1, cv2.LINE_AA)

    # ---------------- Al terminar ----------------
    def _terminar(self):
        if self._terminado:
            return
        self._terminado = True
        if self.modo == "tello":
            try:
                self._tello.send_rc_control(0, 0, 0, 0)
                if self._en_el_aire:
                    self._tello.land()
            except Exception:
                pass
        if self.modo in ("tello", "tello_sin_volar"):
            try:
                self._tello.streamoff()
            except Exception:
                pass
        if self.modo == "camara":
            self._camara.release()
        cv2.destroyAllWindows()
        print(f"\nFin. Estados que visitaste: {' > '.join(self._historial)}")
        if self.objetivo == "color" and self._victimas:
            print(f"Rescatados: {self._rescatados} de {self._victimas}")
        if self.objetivo == "blu":
            print("💙 ¡Blu fue rescatado!" if self._rescatado else "Blu sigue esperando en su pila...")
        if self._mision_cumplida:
            print("🏁 ¡MISIÓN CUMPLIDA!")
