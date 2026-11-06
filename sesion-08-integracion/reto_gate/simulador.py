"""
simulador.py — un Tello DE MENTIRAS (ya está hecho: no necesitas modificarlo)

Se usa EXACTAMENTE igual que el Tello de verdad (djitellopy):
    tello.connect()  tello.takeoff()  tello.land()  tello.send_rc_control(lado, adelante, arriba, giro)
    tello.get_battery()  tello.get_distance_tof()  tello.get_frame_read().frame

Por eso tu misión funciona igual en el simulador y en el dron real.

LA ARENA (en centímetros, vista desde arriba):
    - El dron empieza abajo, mirando un poco hacia la izquierda (la gate NO se ve al inicio).
    - La gate azul es un marco cuadrado hueco colgado frente a él.
    - Si cruzas por el hueco: "¡CRUZASTE LA GATE!". Si pegas en el marco: "¡CHOCASTE!".
"""

import math
import time

import cv2
import numpy as np

# =====================================================================
# MEDIDAS DE LA GATE (el staff las cambia para que se parezcan a la gate real)
# =====================================================================
GATE_X, GATE_Y = 250, 200        # dónde está el centro de la gate (cm)
GATE_ALTURA_CENTRO = 100         # altura del centro de la gate sobre el piso (cm)
GATE_LADO_EXTERIOR = 80          # lado del marco por fuera (cm)
GATE_LADO_INTERIOR = 60          # lado del hueco por dentro (cm)
INICIO_X, INICIO_Y, INICIO_GIRO = 230, 450, -60   # dónde y hacia dónde mira el dron al empezar
ALTURA_DESPEGUE = 80             # a qué altura queda el dron después de takeoff() (cm)

ANCHO, ALTO = 640, 480
CAMPO_DE_VISION = 70             # grados (horizontal)
ESCALA_VELOCIDAD = 1.5           # cm/s por cada unidad de send_rc_control
RADIO_DRON = 8                   # cm: para saber si "cabe" por el hueco
AZUL = (220, 110, 30)            # BGR del marco


class _Lector:
    def __init__(self, tello):
        self._tello = tello

    @property
    def frame(self):
        """Igual que el Tello real: entrega la imagen en RGB."""
        self._tello._avanzar()
        return cv2.cvtColor(self._tello._camara(), cv2.COLOR_BGR2RGB)


class TelloSimulado:
    def __init__(self):
        self.is_flying = False
        self.x, self.y, self.giro, self.z = float(INICIO_X), float(INICIO_Y), float(INICIO_GIRO), 0.0
        self._rc = (0, 0, 0, 0)
        self._t = None
        self._bateria = 100.0
        self.ultimo_rc = (0, 0, 0, 0)  # para revisar tus funciones de movimientos.py
        self.mensaje, self.resultado = "", None  # resultado: "cruzo", "choco" o "fuera"
        self.rastro = []
        self._fondo = None

    # ---------------- La misma API que djitellopy ----------------
    def connect(self):
        print("Simulador: conectado (Tello de mentiras)")

    def streamon(self):
        pass

    def streamoff(self):
        pass

    def end(self):
        pass

    def get_frame_read(self):
        return _Lector(self)

    def get_battery(self):
        return int(self._bateria)

    def get_distance_tof(self):
        return int(self.z) if self.is_flying else 10

    def get_height(self):
        return int(self.z)

    def takeoff(self):
        self.is_flying, self.z = True, float(ALTURA_DESPEGUE)
        self._t = time.time()
        print("Simulador: takeoff()")

    def land(self):
        self.is_flying, self.z, self._rc = False, 0.0, (0, 0, 0, 0)
        print("Simulador: land()")

    def send_rc_control(self, lado, adelante, arriba, giro):
        self.ultimo_rc = (int(lado), int(adelante), int(arriba), int(giro))
        self._rc = self.ultimo_rc if self.is_flying else (0, 0, 0, 0)

    # ---------------- Física ----------------
    def _avanzar(self):
        ahora = time.time()
        dt = 0.0 if self._t is None else min(ahora - self._t, 0.1)
        self._t = ahora
        if not self.is_flying:
            return
        self._bateria = max(0.0, self._bateria - 0.2 * dt)
        lado, adelante, arriba, giro = self._rc
        self.giro = (self.giro + giro * ESCALA_VELOCIDAD * dt) % 360
        rad = math.radians(self.giro)
        y_antes = self.y
        self.x += (math.sin(rad) * adelante + math.cos(rad) * lado) * ESCALA_VELOCIDAD * dt
        self.y += (-math.cos(rad) * adelante + math.sin(rad) * lado) * ESCALA_VELOCIDAD * dt
        self.z = max(20.0, min(250.0, self.z + arriba * ESCALA_VELOCIDAD * dt))
        self.x, self.y = max(10.0, min(490.0, self.x)), max(10.0, min(490.0, self.y))
        self.rastro = (self.rastro + [(self.x, self.y)])[-500:]
        if self.resultado is None and y_antes > GATE_Y >= self.y:
            self._revisar_cruce()

    def _revisar_cruce(self):
        dx, dz = abs(self.x - GATE_X), abs(self.z - GATE_ALTURA_CENTRO)
        hueco = GATE_LADO_INTERIOR / 2 - RADIO_DRON
        marco = GATE_LADO_EXTERIOR / 2 + RADIO_DRON
        if dx < hueco and dz < hueco:
            self.resultado, self.mensaje = "cruzo", "¡CRUZASTE LA GATE!"
        elif dx < marco and dz < marco:
            self.resultado, self.mensaje = "choco", "¡CHOCASTE CON EL MARCO!"
            self.land()
        else:
            self.resultado, self.mensaje = "fuera", "Pasaste por FUERA de la gate"
        print(f"Simulador: {self.mensaje}")

    # ---------------- Lo que ve la cámara ----------------
    def _proyectar(self, X, Y, Z):
        rad = math.radians(self.giro)
        dx, dy = X - self.x, Y - self.y
        frente = dx * math.sin(rad) - dy * math.cos(rad)
        lado = dx * math.cos(rad) + dy * math.sin(rad)
        if frente < 5:
            return None
        f = (ANCHO / 2) / math.tan(math.radians(CAMPO_DE_VISION / 2))
        return (ANCHO / 2 + f * lado / frente, ALTO / 2 + f * (self.z - Z) / frente)

    def _cuadro(self, lado):
        m = lado / 2
        esquinas = [(GATE_X - m, GATE_ALTURA_CENTRO + m), (GATE_X + m, GATE_ALTURA_CENTRO + m),
                    (GATE_X + m, GATE_ALTURA_CENTRO - m), (GATE_X - m, GATE_ALTURA_CENTRO - m)]
        puntos = [self._proyectar(x, GATE_Y, z) for x, z in esquinas]
        return None if None in puntos else np.int32(puntos)

    def _camara(self):
        if self._fondo is None:
            self._fondo = np.zeros((ALTO, ANCHO, 3), np.uint8)
            for fila in range(ALTO):
                if fila < ALTO // 2:
                    self._fondo[fila] = (80, 72, 64)
                else:
                    tono = 70 + int(60 * (fila - ALTO / 2) / (ALTO / 2))
                    self._fondo[fila] = (tono, tono + 6, tono + 12)
        img = self._fondo.copy()
        exterior, interior = self._cuadro(GATE_LADO_EXTERIOR), self._cuadro(GATE_LADO_INTERIOR)
        if exterior is not None and interior is not None:
            arriba = self._proyectar(GATE_X, GATE_Y, 260)  # la cuerda de la que cuelga
            if arriba is not None:
                cv2.line(img, tuple(np.int32((exterior[0] + exterior[1]) / 2)), (int(arriba[0]), int(arriba[1])),
                         (150, 150, 150), 2)
            mascara = np.zeros((ALTO, ANCHO), np.uint8)
            cv2.fillPoly(mascara, [exterior], 255)
            cv2.fillPoly(mascara, [interior], 0)
            img[mascara > 0] = AZUL
        return img

    # ---------------- Dibujo del mapa (para la pantalla) ----------------
    def mapa(self, lado=420):
        k = lado / 500
        img = np.full((lado, lado, 3), (35, 27, 21), np.uint8)
        for i in range(0, 501, 50):
            cv2.line(img, (int(i * k), 0), (int(i * k), lado), (55, 45, 38), 1)
            cv2.line(img, (0, int(i * k)), (lado, int(i * k)), (55, 45, 38), 1)
        m = GATE_LADO_EXTERIOR / 2
        cv2.line(img, (int((GATE_X - m) * k), int(GATE_Y * k)), (int((GATE_X + m) * k), int(GATE_Y * k)), AZUL, 6)
        h = GATE_LADO_INTERIOR / 2
        cv2.line(img, (int((GATE_X - h) * k), int(GATE_Y * k)), (int((GATE_X + h) * k), int(GATE_Y * k)), (35, 27, 21), 4)
        cv2.circle(img, (int(INICIO_X * k), int(INICIO_Y * k)), int(25 * k), (90, 90, 90), 2)
        if len(self.rastro) > 1:
            cv2.polylines(img, [np.int32([(x * k, y * k) for x, y in self.rastro])], False, (90, 140, 90), 1)
        x, y, rad = self.x * k, self.y * k, math.radians(self.giro)
        for angulo in (-CAMPO_DE_VISION / 2, CAMPO_DE_VISION / 2):
            a = rad + math.radians(angulo)
            cv2.line(img, (int(x), int(y)), (int(x + 130 * math.sin(a)), int(y - 130 * math.cos(a))), (80, 80, 60), 1)
        t = 11
        puntas = [(math.sin(rad) * t, -math.cos(rad) * t), (math.sin(rad + 2.5) * t * .8, -math.cos(rad + 2.5) * t * .8),
                  (math.sin(rad - 2.5) * t * .8, -math.cos(rad - 2.5) * t * .8)]
        cv2.fillPoly(img, [np.int32([(x + a, y + b) for a, b in puntas])],
                     (20, 255, 57) if self.is_flying else (160, 160, 160), cv2.LINE_AA)
        cv2.putText(img, f"altura dron: {int(self.z)} cm   centro gate: {GATE_ALTURA_CENTRO} cm", (8, lado - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
        return img


def fotos_de_prueba():
    """Fotos de la gate tomadas desde distintos lugares, con el centro que deberías encontrar.
    Regresa una lista de (nombre, foto en BGR, centro esperado o None)."""
    lugares = [
        ("gate lejos y al centro", 250, 450, 0, 100),
        ("gate a la derecha y arriba", 190, 400, -8, 65),
        ("gate cerca", 250, 300, 0, 100),
        ("sin gate (mira a otro lado)", 230, 450, -90, 80),
    ]
    fotos = []
    for nombre, x, y, giro, z in lugares:
        dron = TelloSimulado()
        dron.x, dron.y, dron.giro, dron.z, dron.is_flying = x, y, giro, z, True
        foto = dron._camara()
        mascara = cv2.inRange(cv2.cvtColor(foto, cv2.COLOR_BGR2HSV), (100, 120, 50), (130, 255, 255))
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contornos:
            gx, gy, w, h = cv2.boundingRect(max(contornos, key=cv2.contourArea))
            esperado = (gx + w // 2, gy + h // 2)
        else:
            esperado = None
        fotos.append((nombre, foto, esperado))
    return fotos
