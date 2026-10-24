"""
PROBAR SOLUCIONES — solo para instructores (Sesión 7: máquinas de estados).

Corre cada lección SIN ventanas, con teclado, reloj, cámara y Tello falsos, y confirma que:
  1. Sin completar, cada archivo corre sin errores.
  2. Con la solución, la máquina de estados pasa por los estados esperados
     (dron.py imprime cada cambio de estado en la terminal).
  3. Los ejemplos de misión final también funcionan en simulador y con un Tello falso.

Cómo correrlo (desde la carpeta sesion-07-maquinas-de-estados):
  python instructores/probar_soluciones.py
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LECCIONES = BASE / "lecciones"
EJEMPLOS = BASE / "instructores" / "ejemplos_mision"

# ---------------------------------------------------------------------------
# SOLUCIONES: (texto que hay en el archivo del alumno, texto que lo reemplaza)
# ---------------------------------------------------------------------------
SOLUCIONES = {
    "01_semaforo.py": [
        ('''        # ✏️ COMPLETA: si pasan 2 segundos, cambia a "ROJO" (copia la idea de VERDE)
        pass''', '''        if segundos > 2:
            estado = "ROJO"
            inicio = time.time()'''),
        ('''        # ✏️ COMPLETA: si pasan 4 segundos, regresa a "VERDE"
        pass''', '''        if segundos > 4:
            estado = "VERDE"
            inicio = time.time()'''),
    ],
    "02_dron_con_teclas.py": [
        ('''        # ✏️ COMPLETA: cuando ya esté en el aire (s.en_el_aire), cambia a "VOLANDO"''',
         '''        if s.en_el_aire:
            estado = "VOLANDO"'''),
        ('''        # ✏️ COMPLETA: si presionan la tecla "l", cambia a "ATERRIZANDO"''',
         '''        if s.tecla == "l":
            estado = "ATERRIZANDO"'''),
        ('''        # ✏️ COMPLETA: cuando ya NO esté en el aire, regresa a "EN_TIERRA"
        #    Pista:  if not s.en_el_aire:''', '''        if not s.en_el_aire:
            estado = "EN_TIERRA"'''),
    ],
    "03_bateria.py": [
        ('''        # ✏️ COMPLETA: si la batería (s.bateria) baja de 30, cambia a "REGRESANDO"''',
         '''        if s.bateria < 30:
            estado = "REGRESANDO"'''),
        ('''        # ✏️ COMPLETA: cuando esté sobre la base (s.en_base), cambia a "ATERRIZANDO"''',
         '''        if s.en_base:
            estado = "ATERRIZANDO"'''),
    ],
    "04_ojos_con_estados.py": [
        ('''        # ✏️ COMPLETA: si ve el color (s.veo_color), cambia a "SIGUIENDO"''',
         '''        if s.veo_color:
            estado = "SIGUIENDO"'''),
        ('''        # ✏️ COMPLETA: si el color está centrado (s.centrado), cambia a "CENTRADO"''',
         '''        if s.centrado:
            estado = "CENTRADO"'''),
        ('''        # ✏️ COMPLETA: si deja de estar centrado, regresa a "SIGUIENDO"
        #    Pista:  if not s.centrado:''', '''        if not s.centrado:
            estado = "SIGUIENDO"'''),
        ('''        # ✏️ COMPLETA: si pasan 2 segundos (s.segundos) sin verlo, regresa a "BUSCANDO"''',
         '''        if s.segundos > 2:
            estado = "BUSCANDO"'''),
    ],
    "05_mision_rescate.py": [
        ('''        # ✏️ COMPLETA: cuando esté en el aire, cambia a "BUSCANDO"''',
         '''        if s.en_el_aire:
            estado = "BUSCANDO"'''),
        ('''        # ✏️ COMPLETA: si ve el color, cambia a "ACERCANDOSE"''',
         '''        if s.veo_color:
            estado = "ACERCANDOSE"'''),
        ('''        # ✏️ COMPLETA: si deja de ver el color, regresa a "BUSCANDO"
        # ✏️ COMPLETA: si ya está cerca (s.cerca), cambia a "RESCATANDO"''',
         '''        if not s.veo_color:
            estado = "BUSCANDO"
        elif s.cerca:
            estado = "RESCATANDO"'''),
        ('''        # ✏️ COMPLETA: cuando ya no esté cerca (not s.cerca), es que ya la rescató:
        #     si todavía faltan personas (s.faltan > 0)  -> "BUSCANDO"
        #     si ya no falta nadie                     -> "REGRESANDO"''',
         '''        if not s.cerca:
            if s.faltan > 0:
                estado = "BUSCANDO"
            else:
                estado = "REGRESANDO"'''),
        ('''        # ✏️ COMPLETA: cuando esté en la base, cambia a "ATERRIZANDO"''',
         '''        if s.en_base:
            estado = "ATERRIZANDO"'''),
    ],
}

T, L, NADA = ord("t"), ord("l"), -1
# Cómo se corre cada archivo y qué DEBE aparecer en la terminal con la solución puesta.
PRUEBAS = {
    "01_semaforo.py": {"teclas": [NADA] * 400, "reloj": 0.05, "esperado": []},
    "02_dron_con_teclas.py": {"teclas": [NADA] * 5 + [T] + [NADA] * 150 + [L] + [NADA] * 150,
                              "esperado": ["->  DESPEGANDO", "->  VOLANDO", "->  ATERRIZANDO", "->  EN_TIERRA"]},
    "03_bateria.py": {"teclas": [NADA] * 1500,
                      "esperado": ["->  PATRULLANDO", "->  REGRESANDO", "->  ATERRIZANDO", "MISIÓN CUMPLIDA"]},
    "04_ojos_con_estados.py": {"teclas": [NADA] * 400, "reloj": 1 / 30, "camara": "aparece_y_desaparece",
                               "esperado": ["->  SIGUIENDO", "->  CENTRADO", "->  PERDIDO", "->  BUSCANDO"]},
    "05_mision_rescate.py": {"teclas": [NADA] * 5 + [T] + [NADA] * 4000,
                             "esperado": ["->  RESCATANDO", "Rescatados: 3 de 3", "MISIÓN CUMPLIDA"]},
    "06_mi_mision.py": {"teclas": [NADA] * 5 + [T] + [NADA] * 1200,
                        "esperado": ["->  SIGUIENDO", "->  ATERRIZANDO"]},
}
# La plantilla de misión final también se prueba con un Tello falso (modos reales)
PRUEBAS_TELLO = {
    "tello_sin_volar": {"esperado": ["->  SIGUIENDO", "->  ATERRIZANDO"], "no_esperado": ["TELLO: takeoff"]},
    "tello": {"esperado": ["TELLO: takeoff", "->  SIGUIENDO", "TELLO: land"]},
}
# Ejemplos de misión final: (modo en que se prueban, guion de la cámara falsa, lo que debe aparecer)
EJEMPLOS_ESPERADO = {
    "rescate.py": ("simulador", "centro", ["Rescatados: 2 de 2", "->  ATERRIZANDO"]),
    "obediente.py": ("camara", "tarjetas", ["->  AVANZANDO", "->  GIRANDO", "->  ATERRIZANDO"]),
    "guardaespaldas.py": ("camara", "se_va", ["->  SIGUIENDO", "->  BUSCANDO", "->  ATERRIZANDO"]),
    "bailarin.py": ("simulador", "centro", ["->  GIRANDO", "->  ATERRIZANDO"]),
}

# ---------------------------------------------------------------------------
# El "corredor": finge ventanas, teclado, reloj, webcam y Tello para correr sin pantalla
# ---------------------------------------------------------------------------
CORREDOR = r'''
import builtins, json, runpy, sys, time, types
import cv2, numpy as np

config = json.loads(sys.argv[2])
teclas = list(config.get("teclas", []))
paso_reloj = config.get("reloj")

cv2.imshow = lambda *a, **k: None
cv2.waitKey = lambda ms=0: teclas.pop(0) if teclas else ord("q")
cv2.namedWindow = lambda *a, **k: None
cv2.getWindowProperty = lambda *a, **k: 1.0
cv2.destroyAllWindows = lambda *a, **k: None

if paso_reloj:
    reloj = [1000.0]
    def tiempo_falso():
        reloj[0] += paso_reloj
        return reloj[0]
    time.time = tiempo_falso
time.sleep = lambda s: None

def escena(cuadro, guion):
    """Lo que ve la cámara falsa en cada cuadro, según el guion de la prueba."""
    img = np.full((480, 640, 3), 90, np.uint8)
    if guion == "tarjetas":  # verde, luego azul, luego rojo
        for desde, hasta, color in [(80, 140, (60, 200, 60)), (200, 260, (220, 100, 40)), (320, 99999, (40, 40, 220))]:
            if desde <= cuadro < hasta:
                cv2.rectangle(img, (240, 160), (400, 320), color, -1)
        return img
    if guion == "aparece_y_desaparece":  # entra por la izquierda, se centra, desaparece y regresa
        if cuadro < 20 or 200 <= cuadro < 300:
            return img
        x = 120 if cuadro < 80 else 320
    elif guion == "se_va":  # se ve al centro y luego desaparece para siempre
        if cuadro >= 150:
            return img
        x = 320
    else:
        x = 320
    cv2.circle(img, (x, 240), 60, (60, 200, 60), -1)
    return img

class CamaraFalsa:
    def __init__(self, *a, **k):
        self.cuadro = 0
    def isOpened(self):
        return True
    def read(self):
        self.cuadro += 1
        return True, escena(self.cuadro, config.get("camara", "centro"))
    def release(self):
        pass
cv2.VideoCapture = CamaraFalsa

class LectorFalso:
    def __init__(self):
        self.cuadro = 0
    @property
    def frame(self):
        self.cuadro += 1
        return cv2.cvtColor(escena(self.cuadro, "centro"), cv2.COLOR_BGR2RGB)  # el Tello entrega RGB

class TelloFalso:
    def __init__(self):
        self.volando = False
    def connect(self): print("TELLO: connect")
    def get_battery(self): return 80
    def streamon(self): pass
    def streamoff(self): pass
    def get_frame_read(self): return LectorFalso()
    def takeoff(self):
        print("TELLO: takeoff"); self.volando = True
    def land(self):
        print("TELLO: land"); self.volando = False
    def send_rc_control(self, *rc): pass
    def get_distance_tof(self): return 80 if self.volando else 10

sys.modules["djitellopy"] = types.SimpleNamespace(Tello=TelloFalso)
sys.argv = [sys.argv[1]]
sys.path.insert(0, config["carpeta"])
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def reemplazar(codigo, cambios, archivo):
    for antes, despues in cambios:
        assert antes in codigo, f"{archivo}: no encontré el hueco:\n{antes}"
        codigo = codigo.replace(antes, despues)
    return codigo


def correr(ruta, config, corredor):
    config = {**config, "carpeta": str(LECCIONES)}
    r = subprocess.run([sys.executable, str(corredor), str(ruta), json.dumps(config)], cwd=LECCIONES,
                       capture_output=True, text=True, encoding="utf-8", timeout=300,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return r.returncode, r.stdout + r.stderr


def revisar(nombre, codigo, salida, esperado, no_esperado=()):
    faltan = [e for e in esperado if e not in salida]
    sobran = [e for e in no_esperado if e in salida]
    ok = codigo == 0 and "Traceback" not in salida and not faltan and not sobran
    print(f"{'OK ' if ok else 'MAL'}  {nombre}")
    if not ok:
        if faltan:
            print(f"      esperaba ver: {faltan}")
        if sobran:
            print(f"      no debía ver: {sobran}")
        print(textwrap.indent(salida[-2000:], "      "))
    return ok


def main():
    fallas = 0
    with tempfile.TemporaryDirectory() as tmp:
        corredor = Path(tmp) / "_corredor.py"
        corredor.write_text(CORREDOR, encoding="utf-8")

        for archivo, prueba in PRUEBAS.items():
            config = {k: v for k, v in prueba.items() if k != "esperado"}
            original = (LECCIONES / archivo).read_text(encoding="utf-8")

            codigo, salida = correr(LECCIONES / archivo, config, corredor)
            fallas += not revisar(f"sin completar   {archivo}", codigo, salida, [])

            copia = LECCIONES / f"_prueba_{archivo}"
            copia.write_text(reemplazar(original, SOLUCIONES.get(archivo, []), archivo), encoding="utf-8")
            try:
                codigo, salida = correr(copia, config, corredor)
            finally:
                copia.unlink()
            fallas += not revisar(f"con solución    {archivo}", codigo, salida, prueba["esperado"])

        plantilla = (LECCIONES / "06_mi_mision.py").read_text(encoding="utf-8")
        for modo, prueba in PRUEBAS_TELLO.items():
            copia = LECCIONES / "_prueba_tello.py"
            copia.write_text(plantilla.replace('MODO = "simulador"', f'MODO = "{modo}"'), encoding="utf-8")
            try:
                codigo, salida = correr(copia, {"teclas": [NADA] * 5 + [T] + [NADA] * 400, "reloj": 1 / 30}, corredor)
            finally:
                copia.unlink()
            fallas += not revisar(f"Tello falso     06_mi_mision.py ({modo})", codigo, salida,
                                  prueba["esperado"], prueba.get("no_esperado", ()))

        for archivo, (modo, guion, esperado) in EJEMPLOS_ESPERADO.items():
            copia = LECCIONES / f"_prueba_ejemplo_{archivo}"
            texto = (EJEMPLOS / archivo).read_text(encoding="utf-8")
            assert 'MODO = "simulador"' in texto, f"{archivo}: debe empezar en MODO = \"simulador\""
            copia.write_text(texto.replace('MODO = "simulador"', f'MODO = "{modo}"'), encoding="utf-8")
            try:
                codigo, salida = correr(copia, {"teclas": [NADA] * 5 + [T] + [NADA] * 2500, "reloj": 1 / 30,
                                                "camara": guion}, corredor)
            finally:
                copia.unlink()
            fallas += not revisar(f"ejemplo         {archivo} ({modo})", codigo, salida, esperado)

    print("\nTODO BIEN" if fallas == 0 else f"\n{fallas} PRUEBA(S) FALLARON")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
