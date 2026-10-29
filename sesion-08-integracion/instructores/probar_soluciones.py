"""
PROBAR SOLUCIONES — solo para instructores (Sesión 8: reto de la gate).

Copia reto_gate/ a una carpeta temporal y corre todo SIN ventanas (teclado y reloj falsos):
  1. Sin completar: cada archivo corre sin errores y muestra sus pistas.
  2. Con las soluciones: los 3 pasos dan ✅ y la misión cruza la gate en el simulador.
  3. La misión también corre contra un Tello falso (modo "tello").

Cómo correrlo (desde la carpeta sesion-08-integracion):
  python instructores/probar_soluciones.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RETO = BASE / "reto_gate"

# (texto en el archivo del alumno, texto de la solución)
SOLUCIONES = {
    "vision.py": [
        ("    return cv2.inRange(hsv, (0, 0, 0), (0, 0, 0))", "    return cv2.inRange(hsv, AZUL_BAJO, AZUL_ALTO)"),
        ("    # Pista: return cv2.boundingRect(gate)      <- regresa (x, y, ancho, alto)\n    return None",
         "    return cv2.boundingRect(gate)"),
        ("        return x + ancho // 2, y + alto // 2\n    return x, y", "        return x + ancho // 2, y + alto // 2\n    return x + ancho // 2, y + alto // 2"),
    ],
    "control.py": [
        ("    # Pista: return centro_x - ancho_foto // 2\n    return 0", "    return centro_x - ancho_foto // 2"),
        ("    # Pista: return alto_foto // 2 - centro_y\n    return 0", "    return alto_foto // 2 - centro_y"),
        ("    #        return limitar(kp * error, VELOCIDAD_MAXIMA)\n    return 0", "    return limitar(kp * error, VELOCIDAD_MAXIMA)"),
    ],
    "movimientos.py": [
        ("def girar(tello):\n    tello.send_rc_control(0, 0, 0, 0)", "def girar(tello):\n    tello.send_rc_control(0, 0, 0, VELOCIDAD_GIRO)"),
        ("def avanzar(tello):\n    tello.send_rc_control(0, 0, 0, 0)", "def avanzar(tello):\n    tello.send_rc_control(0, VELOCIDAD_AVANCE, 0, 0)"),
        ("def corregir(tello, giro, subir, adelante):\n    tello.send_rc_control(0, 0, 0, 0)",
         "def corregir(tello, giro, subir, adelante):\n    tello.send_rc_control(0, adelante, subir, giro)"),
    ],
    "mision.py": [
        ('        # ✏️ COMPLETA: si ve la gate (veo_gate), cambia a "CENTRANDO"',
         '        if veo_gate:\n            estado = "CENTRANDO"'),
        ('        # ✏️ COMPLETA: si deja de ver la gate, regresa a "BUSCANDO"\n        # ✏️ COMPLETA: si ya está centrada, cambia a "ACERCANDOSE"',
         '        if not veo_gate:\n            estado = "BUSCANDO"\n        elif centrada:\n            estado = "ACERCANDOSE"'),
        ('        # ✏️ COMPLETA: si deja de ver la gate, regresa a "BUSCANDO"\n        # ✏️ COMPLETA: si ya está cerca, cambia a "CRUZANDO"',
         '        if not veo_gate:\n            estado = "BUSCANDO"\n        elif cerca:\n            estado = "CRUZANDO"'),
        ('        # ✏️ COMPLETA: si pasan SEGUNDOS_CRUZANDO segundos, cambia a "ATERRIZANDO"',
         '        if segundos > SEGUNDOS_CRUZANDO:\n            estado = "ATERRIZANDO"'),
    ],
}

T, NADA = ord("t"), -1
MISION = {"teclas": [NADA] * 5 + [T] + [NADA] * 1500}
PRUEBAS = [
    # (archivo, configuración, lo que debe salir sin completar, lo que debe salir con la solución)
    ("paso1_vision.py", {}, ["Revisa vision.py"], ["¡Tus ojos funcionan!"]),
    ("paso2_control.py", {}, ["Revisa control.py"], ["¡Tu control P funciona!"]),
    ("paso3_movimientos.py", {"teclas": [NADA] * 400}, ["Revisa movimientos.py"], ["¡Tus movimientos funcionan!", "Sigue con mision.py"]),
    ("mision.py", MISION, ["-> BUSCANDO"], ["-> CENTRANDO", "-> ACERCANDOSE", "-> CRUZANDO", "¡CRUZASTE LA GATE!", "-> ATERRIZANDO"]),
]

CORREDOR = r'''
import json, runpy, sys, time, types
import cv2

config = json.loads(sys.argv[2])
teclas = list(config.get("teclas", []))
cv2.imshow = lambda *a, **k: None
cv2.waitKey = lambda ms=0: teclas.pop(0) if teclas else ord("q")
cv2.namedWindow = lambda *a, **k: None
cv2.getWindowProperty = lambda *a, **k: 1.0
cv2.destroyAllWindows = lambda *a, **k: None
reloj = [1000.0]
def tiempo_falso():
    reloj[0] += 1 / 60
    return reloj[0]
time.time = tiempo_falso
time.sleep = lambda s: None

class TelloFalso:
    """Para probar el modo "tello": se comporta como el simulador, pero avisa cada orden."""
    def __init__(self):
        import simulador
        self._sim = simulador.TelloSimulado()
    def __getattr__(self, nombre):
        return getattr(self._sim, nombre)
    def takeoff(self):
        print("TELLO: takeoff"); self._sim.takeoff()
    def land(self):
        print("TELLO: land"); self._sim.land()
sys.modules["djitellopy"] = types.SimpleNamespace(Tello=TelloFalso)
sys.path.insert(0, config["carpeta"])
sys.argv = [sys.argv[1]]
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def correr(carpeta, archivo, config, corredor):
    config = {**config, "carpeta": str(carpeta)}
    r = subprocess.run([sys.executable, str(corredor), str(carpeta / archivo), json.dumps(config)], cwd=carpeta,
                       capture_output=True, text=True, encoding="utf-8", timeout=300,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return r.returncode, r.stdout + r.stderr


def revisar(nombre, codigo, salida, esperado):
    faltan = [e for e in esperado if e not in salida]
    ok = codigo == 0 and "Traceback" not in salida and not faltan
    print(f"{'OK ' if ok else 'MAL'}  {nombre}")
    if not ok:
        print(f"      esperaba ver: {faltan}")
        print(textwrap.indent(salida[-2000:], "      "))
    return ok


def main():
    fallas = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        corredor = tmp / "_corredor.py"
        corredor.write_text(CORREDOR, encoding="utf-8")
        sin_completar = tmp / "sin_completar"
        con_solucion = tmp / "con_solucion"
        shutil.copytree(RETO, sin_completar, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(RETO, con_solucion, ignore=shutil.ignore_patterns("__pycache__"))
        for archivo, cambios in SOLUCIONES.items():
            ruta = con_solucion / archivo
            texto = ruta.read_text(encoding="utf-8")
            for antes, despues in cambios:
                assert texto.count(antes) == 1, f"{archivo}: no encontré (una sola vez) el hueco:\n{antes}"
                texto = texto.replace(antes, despues)
            ruta.write_text(texto, encoding="utf-8")

        for archivo, config, esperado_sin, esperado_con in PRUEBAS:
            fallas += not revisar(f"sin completar   {archivo}", *correr(sin_completar, archivo, config, corredor), esperado_sin)
            fallas += not revisar(f"con solución    {archivo}", *correr(con_solucion, archivo, config, corredor), esperado_con)

        mision = con_solucion / "mision.py"
        mision.write_text(mision.read_text(encoding="utf-8").replace('MODO = "simulador"', 'MODO = "tello"'), encoding="utf-8")
        fallas += not revisar("Tello falso     mision.py", *correr(con_solucion, "mision.py", MISION, corredor),
                              ["TELLO: takeoff", "-> CRUZANDO", "TELLO: land"])

    print("\nTODO BIEN" if fallas == 0 else f"\n{fallas} PRUEBA(S) FALLARON")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
