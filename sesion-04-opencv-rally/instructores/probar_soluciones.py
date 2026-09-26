"""
PROBAR SOLUCIONES — solo para instructores.

Corre cada lección, reto y herramienta SIN ventanas (con cámara y teclado falsos) para confirmar que:
  1. Sin completar, el archivo corre sin errores (el alumno ve que "algo falta", no un error feo).
  2. Con la solución puesta, cada reto da la clave de instructores/respuestas.md.
  3. Las imágenes de los retos esconden las claves correctas.
Las soluciones legibles para el staff están en instructores/README.md.

Cómo correrlo (desde la carpeta sesion-04-opencv-rally), después de generar_material.py:
  python instructores/probar_soluciones.py
  python instructores/probar_soluciones.py --guardar-ventanas   (guarda lo que mostraría cada ventana)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import cv2

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_material import RESPUESTAS, RETO5_CELDA, RETO5_LETRAS, RETO5_MARGEN  # noqa: E402

# ---------------------------------------------------------------------------
# SOLUCIONES: la función completa que reemplaza a la del alumno
# ---------------------------------------------------------------------------
SOLUCIONES = {
    "lecciones/01_matriz.py": ["""
def leer_pixel(imagen, fila, columna):
    return imagen[fila, columna]
"""],
    "lecciones/02_colores_canales.py": ["""
def pintar(imagen, fila1, fila2, columna1, columna2, color):
    imagen[fila1:fila2, columna1:columna2] = color
    return imagen
"""],
    "lecciones/03_grises_threshold.py": ["""
def blanco_y_negro(gris, umbral):
    _, resultado = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
    return resultado
"""],
    "lecciones/04_video_en_vivo.py": ["""
def efecto(foto):
    return cv2.flip(foto, 1)
"""],
    "lecciones/05_hsv_mascaras.py": ["""
def buscar_color(imagen, bajo, alto):
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, bajo, alto)
"""],
    "lecciones/06_contornos.py": ["""
def centro(x, y, ancho, alto):
    cx = x + ancho // 2
    cy = y + alto // 2
    return cx, cy
"""],
    "lecciones/07_dibujar.py": ["""
def dibujar_mira(foto, x, y, radio):
    cv2.circle(foto, (x, y), radio, (0, 255, 0), 3)
    cv2.circle(foto, (x, y), 5, (0, 0, 255), -1)
    cv2.putText(foto, "OBJETIVO", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
"""],
    "rally/reto_1_detective_pixeles.py": ["""
def leer_rojo(imagen, fila, columna):
    pixel = imagen[fila, columna]
    return pixel[2]
"""],
    "rally/reto_2_mensaje_oscuridad.py": ["""
def blanco_y_negro(gris, umbral):
    _, resultado = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
    return resultado
"""],
    "rally/reto_3_canal_secreto.py": ["""
def canal_rojo(imagen):
    canal1, canal2, canal3 = cv2.split(imagen)
    return canal3
"""],
    "rally/reto_4_caza_colores.py": ["""
def contar(mascara):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contornos)
"""],
    "rally/reto_5_encuentra_tesoro.py": ["""
def es_grande(contorno):
    area = cv2.contourArea(contorno)
    return area > 100
"""],
    "rally/reto_6_jefe_final.py": ["""
def dibujar_mira(foto, x, y, radio):
    cv2.circle(foto, (x, y), radio, (0, 255, 0), 3)
    cv2.circle(foto, (x, y), 5, (0, 0, 255), -1)
    cv2.putText(foto, "OBJETIVO", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
""", """
def donde_esta(x):
    if x < 213:
        return "IZQUIERDA"
    elif x < 426:
        return "CENTRO"
    else:
        return "DERECHA"
"""],
}

# Números que el alumno también tiene que cambiar
CAMBIOS = {
    "lecciones/02_colores_canales.py": {"pintar(robot, 0, 60, 0, 120,": "pintar(robot, 160, 235, 220, 420,"},
    "lecciones/03_grises_threshold.py": {"UMBRAL = 127": "UMBRAL = 150"},
    "lecciones/06_contornos.py": {"AREA_MINIMA = 0 ": "AREA_MINIMA = 100 "},
    "rally/reto_2_mensaje_oscuridad.py": {"UMBRAL = 127": "UMBRAL = 30"},
    "rally/reto_4_caza_colores.py": {"BAJO = (0, 0, 0)": "BAJO = (0, 150, 150)",
                                     "ALTO = (179, 255, 255)": "ALTO = (8, 255, 255)"},
}

NADA = -1
# Cómo se corre cada archivo: teclas simuladas, lo que se escribe en input(),
# y qué texto DEBE aparecer en la terminal con la solución puesta.
PRUEBAS = {
    "lecciones/01_matriz.py": {"esperado": ["El pixel vale: ["]},
    "lecciones/02_colores_canales.py": {"esperado": ["Un pixel de la manzana roja: ["]},
    "lecciones/03_grises_threshold.py": {},
    "lecciones/04_video_en_vivo.py": {"teclas": [NADA, NADA]},
    "lecciones/05_hsv_mascaras.py": {"teclas": [13, NADA, NADA]},
    "lecciones/06_contornos.py": {"esperado": ["Encontré 3 objetos"]},
    "lecciones/07_dibujar.py": {"teclas": [13, NADA, NADA]},
    "rally/reto_1_detective_pixeles.py": {"esperado": [f"Mensaje secreto: {RESPUESTAS['reto_1'].upper()}\n"]},
    "rally/reto_2_mensaje_oscuridad.py": {},
    "rally/reto_3_canal_secreto.py": {},
    "rally/reto_4_caza_colores.py": {"esperado": [f"Pelotas encontradas: {RESPUESTAS['reto_4']}\n"]},
    "rally/reto_5_encuentra_tesoro.py": {"esperado": ["Círculos rojos en el mapa: 1\n"]},
    "rally/reto_6_jefe_final.py": {"teclas": [NADA] * 20},
    "herramientas/inspector_pixeles.py": {"entradas": ["robot"], "esperado": ["Haz clic"]},
    "herramientas/calibrador_hsv.py": {"entradas": ["reto_4"], "esperado": ["BAJO = (0, 0, 0)"]},
    "herramientas/prueba_camara.py": {"esperado": ["¡Tu cámara funciona!"]},
    "demo/demo_gancho.py": {"teclas": [ord(str(n)) for n in range(1, 9)] + [NADA]},
}

# ---------------------------------------------------------------------------
# El "corredor": finge ventanas, teclado, input() y cámara para correr sin pantalla
# ---------------------------------------------------------------------------
CORREDOR = r'''
import builtins, json, runpy, sys
from pathlib import Path
import cv2, numpy as np

config = json.loads(sys.argv[2])
teclas = list(config.get("teclas", []))
entradas = list(config.get("entradas", []))
carpeta_ventanas = config.get("carpeta_ventanas")
ventanas, barras = {}, {}

def imshow(nombre, imagen):
    ventanas[nombre] = imagen.copy()

class CamaraFalsa:
    """Una pelota roja que da vueltas sobre un fondo gris."""
    def __init__(self, *args, **kwargs):
        self.cuadro = 0
    def isOpened(self):
        return True
    def read(self):
        self.cuadro += 1
        frame = np.full((480, 640, 3), 128, np.uint8)
        x = int(320 + 200 * np.cos(self.cuadro / 3))
        cv2.circle(frame, (x, 240), 50, (40, 40, 220), -1)
        return True, frame
    def release(self):
        pass

cv2.imshow = imshow
cv2.waitKey = lambda ms=0: teclas.pop(0) if teclas else ord("q")
cv2.namedWindow = lambda *a, **k: None
cv2.createTrackbar = lambda nombre, ventana, inicial, maximo, f: barras.setdefault(nombre, inicial)
cv2.getTrackbarPos = lambda nombre, ventana: barras[nombre]
cv2.setMouseCallback = lambda *a, **k: None
cv2.getWindowProperty = lambda *a, **k: 1.0
cv2.destroyAllWindows = lambda *a, **k: None
cv2.VideoCapture = CamaraFalsa
builtins.input = lambda *a, **k: entradas.pop(0) if entradas else ""

sys.argv = [sys.argv[1]]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
finally:
    if carpeta_ventanas:
        Path(carpeta_ventanas).mkdir(parents=True, exist_ok=True)
        for nombre, imagen in ventanas.items():
            limpio = "".join(ch if ch.isalnum() else "_" for ch in nombre)[:60]
            cv2.imwrite(str(Path(carpeta_ventanas) / f"{limpio}.png"), imagen)
'''


def reemplazar_funcion(codigo, solucion):
    """Cambia la función del alumno (desde su 'def' hasta el siguiente renglón sin sangría) por la solución."""
    solucion = textwrap.dedent(solucion).strip("\n")
    nombre = re.match(r"def (\w+)\(", solucion).group(1)
    lineas = codigo.split("\n")
    inicio = next(i for i, linea in enumerate(lineas) if linea.startswith(f"def {nombre}("))
    fin = inicio + 1
    while fin < len(lineas) and (lineas[fin] == "" or lineas[fin][0] in " \t"):
        fin += 1
    return "\n".join(lineas[:inicio] + solucion.split("\n") + ["", ""] + lineas[fin:])


def correr(ruta_script, config, corredor):
    resultado = subprocess.run([sys.executable, str(corredor), str(ruta_script), json.dumps(config)],
                               cwd=BASE, capture_output=True, text=True, encoding="utf-8", timeout=120,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return resultado.returncode, resultado.stdout + resultado.stderr


def revisar_imagenes_de_retos():
    """Comprueba directo en las imágenes que las claves estén bien escondidas."""
    fallas = []
    carpeta = BASE / "rally" / "imagenes"
    # Reto 2: con umbral 30 hay texto; con umbral 15 todo es ruido; con 127 no hay nada
    gris = cv2.cvtColor(cv2.imread(str(carpeta / "reto_2.png")), cv2.COLOR_BGR2GRAY)
    blancos = {u: int((gris > u).sum()) for u in (15, 30, 127)}
    if not (blancos[127] == 0 and 2000 < blancos[30] < 60000 and blancos[15] > 100000):
        fallas.append(f"reto_2: pixeles blancos por umbral {blancos}")
    # Reto 5: la única mancha grande de color esmeralda cae en la casilla de la respuesta
    hsv = cv2.cvtColor(cv2.imread(str(carpeta / "reto_5.png")), cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, (57, 200, 150), (63, 255, 255))
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    grandes = [c for c in contornos if cv2.contourArea(c) > 100]
    if len(grandes) != 1:
        fallas.append(f"reto_5: hay {len(grandes)} manchas grandes, debería haber 1")
    else:
        (x, y), _ = cv2.minEnclosingCircle(grandes[0])
        casilla = f"{RETO5_LETRAS[int(x - RETO5_MARGEN) // RETO5_CELDA]}{int(y - RETO5_MARGEN) // RETO5_CELDA + 1}"
        if casilla != RESPUESTAS["reto_5"].upper():
            fallas.append(f"reto_5: el tesoro está en {casilla}, no en {RESPUESTAS['reto_5']}")
    return fallas


def main():
    guardar = "--guardar-ventanas" in sys.argv
    fallas = 0
    with tempfile.TemporaryDirectory() as tmp:
        corredor = Path(tmp) / "_corredor.py"
        corredor.write_text(CORREDOR, encoding="utf-8")
        for archivo, prueba in PRUEBAS.items():
            config = {k: v for k, v in prueba.items() if k != "esperado"}

            # 1) Sin completar: debe correr sin errores
            if archivo in SOLUCIONES:
                codigo, salida = correr(BASE / archivo, config, corredor)
                ok = codigo == 0 and "Traceback" not in salida
                fallas += not ok
                print(f"{'OK ' if ok else 'MAL'}  sin completar   {archivo}")
                if not ok:
                    print(textwrap.indent(salida[-1500:], "      "))

            # 2) Con la solución: debe correr sin errores y dar lo esperado
            codigo_fuente = (BASE / archivo).read_text(encoding="utf-8")
            for solucion in SOLUCIONES.get(archivo, []):
                codigo_fuente = reemplazar_funcion(codigo_fuente, solucion)
            for antes, despues in CAMBIOS.get(archivo, {}).items():
                assert antes in codigo_fuente, f"{archivo}: no encontré '{antes}'"
                codigo_fuente = codigo_fuente.replace(antes, despues)
            # La copia vive junto al original para que las rutas relativas sigan funcionando
            copia = (BASE / archivo).with_name(f"_prueba_{Path(archivo).name}")
            copia.write_text(codigo_fuente, encoding="utf-8")
            try:
                if guardar:
                    config["carpeta_ventanas"] = str(BASE / "instructores" / "_ventanas" / Path(archivo).stem)
                codigo, salida = correr(copia, config, corredor)
            finally:
                copia.unlink()
            faltantes = [e for e in prueba.get("esperado", []) if e not in salida]
            ok = codigo == 0 and not faltantes and "Traceback" not in salida
            fallas += not ok
            print(f"{'OK ' if ok else 'MAL'}  con solución    {archivo}")
            if not ok:
                print(f"      esperaba: {faltantes}")
                print(textwrap.indent(salida[-1500:], "      "))

    problemas = revisar_imagenes_de_retos()
    for problema in problemas:
        print(f"MAL  imágenes          {problema}")
    if not problemas:
        print("OK   imágenes          las claves de los retos 2 y 5 están bien escondidas")
    fallas += len(problemas)

    print("\nTODO BIEN" if fallas == 0 else f"\n{fallas} PRUEBA(S) FALLARON")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
