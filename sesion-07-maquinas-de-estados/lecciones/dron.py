"""
dron.py — el CUERPO del dron (ya está hecho: no necesitas modificarlo)

Tu programa es el CEREBRO: decide en qué estado está el dron y cuándo cambia.
Este archivo sabe CÓMO moverse y CÓMO ver, en cualquiera de estos modos:

    "simulador"        un dron en la pantalla (para probar sin ningún riesgo)
    "camara"           tu webcam hace de ojos del dron; no se mueve nada, solo te dice qué haría
    "tello_sin_volar"  el Tello real prende su cámara y sus sensores, pero NO despega
    "tello"            el Tello real vuela de verdad (¡solo con el staff!)

Cómo se usa:

    from dron import Dron

    dron = Dron("simulador")
    estado = "EN_TIERRA"

    while dron.sigue():
        s = dron.sensores(estado)       # lo que el dron sabe en este momento

        if estado == "EN_TIERRA":
            dron.quieto()               # lo que HACE en este estado
            if s.tecla == "t":          # cuándo CAMBIA de estado
                estado = "DESPEGANDO"
        ...

ACCIONES (llama una en cada estado):
    dron.quieto()        dron.despegar()      dron.aterrizar()
    dron.avanzar()       dron.retroceder()    dron.izquierda()     dron.derecha()
    dron.subir()         dron.bajar()         dron.girar()
    dron.seguir_color()  dron.acercarse()     dron.rescatar()
    dron.patrullar()     dron.regresar_a_base()   <- este último solo en el simulador

SENSORES (s = dron.sensores(estado)):
    s.tecla       la tecla que presionaste ("" si ninguna)
    s.segundos    cuántos segundos llevas en el estado actual
    s.en_el_aire  True si está volando
    s.altura      altura en cm
    s.bateria     batería en %
    s.veo_color   True si ve el color objetivo
    s.error_x     qué tan lejos está el color del centro (pixeles, + = derecha)
    s.centrado    True si el color está casi en el centro
    s.cerca       True si el color se ve grande (está cerca)
    s.veo_rojo    s.veo_verde    s.veo_azul
    s.en_base     True si está sobre la base (simulador)
    s.faltan      cuántos objetos faltan por rescatar
"""

import atexit
import math
import time
import unicodedata

import cv2
import numpy as np

# =====================================================================
# AJUSTES (el staff los puede cambiar)
# =====================================================================
VELOCIDAD = 20                # avanzar, retroceder, izquierda, derecha, subir, bajar (0 a 100)
VELOCIDAD_GIRO = 30           # girar (0 a 100)
KP_GIRO = 0.12                # seguir_color: giro por cada pixel de error horizontal (Sesión 6)
KP_ALTURA = 0.10              # seguir_color: subida por cada pixel de error vertical (Sesión 6)
VELOCIDAD_MAXIMA = 25         # ninguna corrección pasa de aquí
TOLERANCIA_CENTRADO = 50      # pixeles: si |error_x| es menor, el color está "centrado"
AREA_MINIMA = 400             # manchas más chicas se ignoran (ruido, Sesión 4)
AREA_CERCA = 15000            # si la mancha mide más que esto, el objeto está "cerca"
SEGUNDOS_PARA_RESCATAR = 2    # rescatar(): cuánto hay que quedarse junto al objeto
VICTIMAS_REALES = 1           # con cámara o Tello: cuántos rescates cuentan para "faltan"
BATERIA_SEGURIDAD = 15        # Tello real: con menos batería aterriza solo
SEGUNDOS_MAXIMOS_VUELO = 120  # Tello real: después de este tiempo aterriza solo

COLORES = {  # rangos HSV de las Sesiones 4 y 6
    "rojo": [((0, 120, 70), (8, 255, 255)), ((170, 120, 70), (179, 255, 255))],
    "verde": [((40, 70, 50), (85, 255, 255))],
    "azul": [((100, 120, 50), (130, 255, 255))],
}

# Arena del simulador: 500 x 500 cm. La base está abajo al centro.
BASE = (250, 440)
MUNDOS = {
    "vacio": {"objetos": [], "consumo": 0.5},
    "patrulla": {"objetos": [], "consumo": 2.0},
    "rescate": {"objetos": [(110, 120, "verde"), (400, 170, "verde"), (330, 330, "verde")], "consumo": 0.6},
    "libre": {"objetos": [(120, 110, "verde"), (390, 120, "rojo"), (420, 330, "azul"), (140, 300, "verde")],
              "consumo": 0.7},
}

MODOS = ("simulador", "camara", "tello_sin_volar", "tello")
ANCHO, ALTO = 640, 480
DT = 1 / 30  # el simulador avanza 1/30 de segundo por vuelta
COLOR_BGR = {"rojo": (40, 40, 220), "verde": (60, 200, 60), "azul": (220, 100, 40)}
PALETA = [(57, 255, 20), (255, 166, 88), (102, 129, 247), (96, 204, 242), (255, 120, 210), (80, 220, 255),
          (150, 255, 150), (200, 160, 255)]
ACCIONES_EN_PANTALLA = {
    "quieto": "quieto", "despegar": "despegar", "aterrizar": "aterrizar", "avanzar": "avanzar ^",
    "retroceder": "retroceder v", "izquierda": "< izquierda", "derecha": "derecha >", "subir": "subir",
    "bajar": "bajar", "girar": "girar ->", "seguir_color": "seguir color", "acercarse": "acercarse",
    "rescatar": "rescatar", "patrullar": "patrullar", "regresar_a_base": "regresar a base",
}


def _limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def _ascii(texto):
    """putText no sabe escribir acentos: los quitamos solo para dibujar."""
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def _color_de_estado(nombre):
    return PALETA[sum(ord(c) for c in nombre) % len(PALETA)]


class Sensores:
    """Todo lo que el dron sabe en este momento."""

    def __init__(self, **datos):
        self.__dict__.update(datos)

    def __repr__(self):
        return "Sensores(" + ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items()) + ")"


class Dron:
    def __init__(self, modo="simulador", color="verde", mundo="libre", bateria=100):
        if modo not in MODOS:
            raise SystemExit(f"Modo '{modo}' no existe. Usa uno de estos: {', '.join(MODOS)}")
        if color not in COLORES:
            raise SystemExit(f"Color '{color}' no existe. Usa uno de estos: {', '.join(COLORES)}")
        if mundo not in MUNDOS:
            raise SystemExit(f"Mundo '{mundo}' no existe. Usa uno de estos: {', '.join(MUNDOS)}")

        self.modo, self.color = modo, color
        self._ventana = f"Dron - modo {modo}  (q = salir)"
        self._activo, self._terminado = True, False
        self._accion, self._rc = "quieto", (0, 0, 0, 0)
        self._estado, self._inicio_estado, self._historial = None, 0.0, []
        self._mensaje, self._mensaje_hasta = "", 0.0
        self._t, self._t0 = 0.0, time.time()
        self._tecla = ""
        self._vision = self._vision_vacia()
        self._en_el_aire, self._fase, self._fase_desde = False, "tierra", 0.0
        self._z, self._altura, self._bateria = 0.0, 0.0, float(bateria)  # _z = altura simulada
        self._dt, self._fondo = DT, None
        self._rescatados, self._progreso_rescate = 0, 0.0
        self._sin_despegar, self._t_despegue = False, None
        self._ya_volo, self._mision_cumplida = False, False

        if modo == "simulador":
            datos = MUNDOS[mundo]
            self._x, self._y, self._yaw = float(BASE[0]), float(BASE[1]), 0.0
            self._consumo = datos["consumo"]
            self._objetos = [{"x": x, "y": y, "color": c, "z": 60, "rescatado": False} for x, y, c in datos["objetos"]]
            self._victimas = sum(1 for o in self._objetos if o["color"] == color)
            self._rastro, self._punto_patrulla = [], 0
        else:
            self._victimas = VICTIMAS_REALES

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
        print(f"\nDron listo en modo '{modo}'. Color objetivo: {color}. Presiona q en la ventana para salir.\n")

    # -----------------------------------------------------------------
    # El ciclo
    # -----------------------------------------------------------------
    def sigue(self):
        """True mientras la misión siga. Se vuelve False al presionar q o cerrar la ventana."""
        if not self._activo:
            self._terminar()
        return self._activo

    def sensores(self, estado):
        estado = str(estado)
        anterior = self._t
        self._t = self._t + DT if self.modo == "simulador" else time.time() - self._t0
        self._dt = self._t - anterior

        # 1) Hacer lo que tu programa pidió en la vuelta anterior
        self._aplicar(self._accion)
        self._accion = "quieto"

        # 2) ¿Cambió el estado?
        if estado != self._estado:
            self._estado, self._inicio_estado = estado, self._t
            self._historial.append(estado)
            print(f"[{self._t:6.1f} s]  ->  {estado}")

        # 3) Ver y revisar la seguridad
        frame = self._leer_camara()
        self._vision = self._ver(frame)
        self._seguridad()
        self._revisar_mision()

        v = self._vision
        s = Sensores(
            tecla="", segundos=round(self._t - self._inicio_estado, 1), en_el_aire=self._en_el_aire,
            altura=int(self._altura), bateria=int(self._bateria),
            veo_color=v["veo"], error_x=v["error_x"], centrado=v["centrado"], cerca=v["cerca"],
            veo_rojo=v["rojo"] is not None, veo_verde=v["verde"] is not None, veo_azul=v["azul"] is not None,
            en_base=self._en_base(), faltan=max(0, self._victimas - self._rescatados),
        )

        # 4) Dibujar y leer el teclado
        cv2.imshow(self._ventana, self._dibujar(frame, s))
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
    def girar(self): self._accion = "girar"
    def seguir_color(self): self._accion = "seguir_color"
    def acercarse(self): self._accion = "acercarse"
    def rescatar(self): self._accion = "rescatar"
    def patrullar(self): self._accion = "patrullar"
    def regresar_a_base(self): self._accion = "regresar_a_base"

    # -----------------------------------------------------------------
    # Por dentro (no necesitas leer de aquí para abajo)
    # -----------------------------------------------------------------
    def _avisar(self, texto, segundos=3):
        if texto != self._mensaje or self._t > self._mensaje_hasta:
            print(f"[{self._t:6.1f} s]  {texto}")
        self._mensaje, self._mensaje_hasta = texto, self._t + segundos

    def _rc_para(self, accion):
        """Convierte una acción en (izquierda/derecha, adelante/atrás, arriba/abajo, giro), como send_rc_control."""
        v = self._vision
        seguir = (_limitar(KP_GIRO * v["error_x"], -VELOCIDAD_MAXIMA, VELOCIDAD_MAXIMA),
                  _limitar(KP_ALTURA * v["error_y"], -VELOCIDAD_MAXIMA, VELOCIDAD_MAXIMA)) if v["veo"] else (0, 0)
        if accion == "avanzar":
            return (0, VELOCIDAD, 0, 0)
        if accion == "retroceder":
            return (0, -VELOCIDAD, 0, 0)
        if accion == "izquierda":
            return (-VELOCIDAD, 0, 0, 0)
        if accion == "derecha":
            return (VELOCIDAD, 0, 0, 0)
        if accion == "subir":
            return (0, 0, VELOCIDAD, 0)
        if accion == "bajar":
            return (0, 0, -VELOCIDAD, 0)
        if accion == "girar":
            return (0, 0, 0, VELOCIDAD_GIRO)
        area = v["caja"][4] if v["veo"] else 0
        if accion == "seguir_color":
            return (0, 0, seguir[1], seguir[0])
        if accion == "acercarse":  # avanza hasta un poco después de "cerca", para no quedar en la orilla
            adelante = VELOCIDAD if v["veo"] and area < AREA_CERCA * 1.2 and abs(v["error_x"]) < 120 else 0
            return (0, adelante, seguir[1], seguir[0])
        if accion == "rescatar":  # se arrima despacito y se queda junto al objeto
            adelante = 10 if v["veo"] and area < AREA_CERCA * 1.1 and abs(v["error_x"]) < 120 else 0
            return (0, adelante, seguir[1], seguir[0])
        if accion == "patrullar":
            return (0, 15, 0, 20)  # en el Tello real: un círculo lento
        return (0, 0, 0, 0)

    def _aplicar(self, accion):
        rc = self._rc_para(accion)

        # Despegar y aterrizar
        if accion == "despegar" and not self._en_el_aire and self._fase == "tierra":
            self._iniciar_despegue()
        elif accion == "aterrizar" and self._en_el_aire:
            self._iniciar_aterrizaje()
        self._avanzar_fases()

        # Rescatar: quedarse junto al objeto, centrado y cerca, unos segundos
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
                rc = self._ir_hacia(*BASE, velocidad=30) if math.hypot(BASE[0] - self._x, BASE[1] - self._y) > 12 else (0, 0, 0, 0)
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
            cercanos = [o for o in self._objetos if not o["rescatado"] and o["color"] == self.color]
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

    def _revisar_mision(self):
        if self.modo == "simulador" and self._ya_volo and not self._mision_cumplida and self._fase == "tierra" \
                and self._en_base() and self._rescatados >= self._victimas:
            self._mision_cumplida = True
            self._avisar("MISION CUMPLIDA!", 10)

    def _en_base(self):
        return self.modo == "simulador" and math.hypot(BASE[0] - self._x, BASE[1] - self._y) < 30

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
        self._rastro = (self._rastro + [(self._x, self._y)])[-400:]

    def _camara_simulada(self):
        horizonte = ALTO // 2
        if self._fondo is None:
            self._fondo = np.zeros((ALTO, ANCHO, 3), np.uint8)
            self._fondo[:horizonte] = (70, 60, 52)
            for fila in range(horizonte, ALTO):
                tono = 60 + int(50 * (fila - horizonte) / (ALTO - horizonte))
                self._fondo[fila] = (tono, tono + 8, tono + 14)
        img = self._fondo.copy()
        f = (ANCHO / 2) / math.tan(math.radians(35))
        rad = math.radians(self._yaw)
        visibles = []
        for o in self._objetos:
            if o["rescatado"]:
                continue
            dx, dy = o["x"] - self._x, o["y"] - self._y
            frente = dx * math.sin(rad) - dy * math.cos(rad)
            lado = dx * math.cos(rad) + dy * math.sin(rad)
            if frente > 10:
                visibles.append((frente, lado, o))
        for frente, lado, o in sorted(visibles, key=lambda t: -t[0]):
            u = int(ANCHO / 2 + f * lado / frente)
            v = int(horizonte + f * (self._z - o["z"]) / frente)
            piso = int(horizonte + f * self._z / frente)
            r = max(2, int(f * 15 / frente))
            cv2.line(img, (u, v), (u, piso), (90, 90, 90), max(1, r // 6))
            cv2.circle(img, (u, v), r, COLOR_BGR[o["color"]], -1, cv2.LINE_AA)
            cv2.circle(img, (u - r // 3, v - r // 3), max(1, r // 5), (240, 240, 240), -1, cv2.LINE_AA)
        return img

    def _mapa(self):
        lado = 600
        k = lado / 500
        mapa = np.full((lado, lado, 3), (35, 27, 21), np.uint8)
        for i in range(0, 501, 50):
            cv2.line(mapa, (int(i * k), 0), (int(i * k), lado), (55, 45, 38), 1)
            cv2.line(mapa, (0, int(i * k)), (lado, int(i * k)), (55, 45, 38), 1)
        bx, by = int(BASE[0] * k), int(BASE[1] * k)
        cv2.circle(mapa, (bx, by), int(30 * k), (90, 90, 90), 2)
        cv2.putText(mapa, "H", (bx - 10, by + 10), cv2.FONT_HERSHEY_DUPLEX, 0.9, (150, 150, 150), 2)
        for o in self._objetos:
            p = (int(o["x"] * k), int(o["y"] * k))
            if o["rescatado"]:
                cv2.drawMarker(mapa, p, (110, 110, 110), cv2.MARKER_TILTED_CROSS, 22, 2)
            else:
                cv2.circle(mapa, p, int(15 * k), COLOR_BGR[o["color"]], -1, cv2.LINE_AA)
        if len(self._rastro) > 1:
            cv2.polylines(mapa, [np.int32([(x * k, y * k) for x, y in self._rastro])], False, (90, 140, 90), 1)
        x, y, rad = self._x * k, self._y * k, math.radians(self._yaw)
        for angulo in (-35, 35):
            a = rad + math.radians(angulo)
            cv2.line(mapa, (int(x), int(y)), (int(x + 170 * math.sin(a)), int(y - 170 * math.cos(a))), (80, 80, 60), 1)
        tamano = 12 + self._z / 20
        puntas = [(math.sin(rad) * tamano, -math.cos(rad) * tamano),
                  (math.sin(rad + 2.5) * tamano * 0.8, -math.cos(rad + 2.5) * tamano * 0.8),
                  (math.sin(rad - 2.5) * tamano * 0.8, -math.cos(rad - 2.5) * tamano * 0.8)]
        color = (20, 255, 57) if self._en_el_aire else (160, 160, 160)
        cv2.fillPoly(mapa, [np.int32([(x + dx, y + dy) for dx, dy in puntas])], color, cv2.LINE_AA)
        return mapa

    # ---------------- Cámara y visión ----------------
    def _leer_camara(self):
        if self.modo == "simulador":
            return self._camara_simulada()
        if self.modo == "camara":
            ok, frame = self._camara.read()
            frame = cv2.flip(frame, 1) if ok else np.zeros((ALTO, ANCHO, 3), np.uint8)
        else:
            frame = self._lector.frame
            if frame is None:
                return np.zeros((ALTO, ANCHO, 3), np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # djitellopy entrega la imagen en RGB
        return cv2.resize(frame, (ANCHO, ALTO))

    @staticmethod
    def _vision_vacia():
        return {"veo": False, "error_x": 0, "error_y": 0, "centrado": False, "cerca": False, "caja": None,
                "rojo": None, "verde": None, "azul": None}

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

    # ---------------- Dibujo ----------------
    def _dibujar(self, frame, s):
        camara = frame.copy()
        cx, cy = ANCHO // 2, ALTO // 2
        cv2.drawMarker(camara, (cx, cy), (255, 255, 255), cv2.MARKER_CROSS, 24, 2)
        for nombre in COLORES:
            caja = self._vision[nombre]
            if caja is not None and nombre != self.color:
                x, y, w, h, _ = caja
                cv2.rectangle(camara, (x, y), (x + w, y + h), COLOR_BGR[nombre], 2)
        if self._vision["veo"]:
            x, y, w, h, _ = self._vision["caja"]
            centro = (x + w // 2, y + h // 2)
            cv2.rectangle(camara, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.circle(camara, centro, 6, (0, 0, 255), -1)
            cv2.line(camara, (cx, cy), centro, (255, 0, 0), 2)
        orden = "send_rc_control" + str(tuple(int(x) for x in self._rc))
        cv2.rectangle(camara, (0, ALTO - 34), (ANCHO, ALTO), (0, 0, 0), -1)
        cv2.putText(camara, orden, (10, ALTO - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (120, 230, 255), 2, cv2.LINE_AA)

        hud = self._hud(s)
        if self.modo == "simulador":
            derecha = np.vstack([cv2.resize(camara, (480, 360)), hud])
            return np.hstack([self._mapa(), derecha])
        izquierda = np.full((600, 600, 3), (23, 17, 13), np.uint8)
        izquierda[:450] = cv2.resize(camara, (600, 450))
        consejos = ["q = salir" + (" (y aterrizar)" if self.modo == "tello" else ""),
                    f"modo: {self.modo}   color objetivo: {self.color}"]
        if self.modo != "tello":
            consejos.append("Aqui el dron NO se mueve: mira la orden que mandaria")
        for i, texto in enumerate(consejos):
            cv2.putText(izquierda, _ascii(texto), (14, 490 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)
        derecha = np.full((600, 480, 3), (23, 17, 13), np.uint8)
        derecha[:240] = hud
        self._historial_grande(derecha)
        return np.hstack([izquierda, derecha])

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
        banderas = [("en_el_aire", s.en_el_aire), ("veo_color", s.veo_color), ("centrado", s.centrado),
                    ("cerca", s.cerca), ("veo_rojo", s.veo_rojo), ("veo_verde", s.veo_verde),
                    ("veo_azul", s.veo_azul), ("en_base", s.en_base)]
        for i, (nombre, valor) in enumerate(banderas):
            x, y = 12 + (i % 4) * 117, 112 + (i // 4) * 26
            cv2.circle(hud, (x + 6, y - 5), 6, (57, 255, 20) if valor else (70, 70, 70), -1)
            cv2.putText(hud, nombre, (x + 17, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220) if valor else (120, 120, 120), 1, cv2.LINE_AA)

        accion = ACCIONES_EN_PANTALLA.get(getattr(self, "_accion_mostrada", "quieto"), "quieto")
        cv2.putText(hud, f"accion: {accion}   error_x: {s.error_x}   faltan: {s.faltan}", (12, 178),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 200, 120), 1, cv2.LINE_AA)
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
        if self._victimas:
            print(f"Rescatados: {self._rescatados} de {self._victimas}")
        if self._mision_cumplida:
            print("🏁 ¡MISIÓN CUMPLIDA!")
