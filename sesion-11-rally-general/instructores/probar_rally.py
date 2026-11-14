"""
probar_rally.py — revisa TODO el rally sin abrir ventanas (para el staff, antes de la clase)

    python instructores/probar_rally.py

1. Levanta el servidor del marcador en un puerto libre (con datos temporales).
2. Corre las soluciones de los 6 retos con el teclado "simulado" (presiona t solo).
3. Corre los archivos de los alumnos SIN completar y revisa que NO den puntos.
4. Revisa el marcador: puntos, bono al primero, repetidos, códigos manuales y el reloj.
"""

import contextlib
import io
import json
import random
import runpy
import sys
import tempfile
import threading
import types
import urllib.request
from pathlib import Path

import cv2

AQUI = Path(__file__).resolve().parent
RALLY = AQUI.parent / "rally"
SOLUCIONES = AQUI / "soluciones"
MARCADOR = AQUI.parent / "marcador"
EQUIPO = "Equipo de Prueba"

# ---------------- Sin ventanas: el teclado presiona "t" solito ----------------
cuadros = {"n": 0, "maximo": 0, "calificado": None}


def _wait_key(espera=0):
    cuadros["n"] += 1
    if espera == 0:
        return -1
    if cuadros["n"] == 5:
        return ord("t")
    if cuadros["calificado"] is not None and cuadros["n"] > cuadros["calificado"] + 10:
        return ord("q")  # el juez ya calificó: cerramos como lo haría el alumno
    return ord("q") if cuadros["n"] >= cuadros["maximo"] else -1


cv2.imshow = lambda *a, **k: None
cv2.namedWindow = lambda *a, **k: None
cv2.destroyAllWindows = lambda *a, **k: None
cv2.getWindowProperty = lambda *a, **k: 1
cv2.waitKey = _wait_key

# ---------------- El servidor del marcador, con datos temporales ----------------
sys.path.insert(0, str(MARCADOR))
import servidor_marcador as sm  # noqa: E402

sm.ARCHIVO = Path(tempfile.mkdtemp()) / "marcador_datos.json"
sm.datos.clear()
sm.datos.update(sm.datos_nuevos())
servidor = sm.ThreadingHTTPServer(("127.0.0.1", 0), sm.Marcador)
servidor.direcciones = []
PUERTO = servidor.server_address[1]
threading.Thread(target=servidor.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{PUERTO}"


def pedir(ruta, datos=None):
    abrir = urllib.request.build_opener(urllib.request.ProxyHandler({})).open
    cuerpo = None if datos is None else json.dumps(datos).encode()
    pedido = urllib.request.Request(URL + ruta, data=cuerpo, headers={"Content-Type": "application/json"})
    try:
        with abrir(pedido, timeout=3) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as error:
        return json.loads(error.read().decode())


def puntos_del_equipo():
    estado = pedir("/estado")
    equipo = next((e for e in estado["equipos"] if e["nombre"] == EQUIPO), None)
    return (0, {}) if equipo is None else (equipo["puntos"], equipo["resueltos"])


# ---------------- Correr un reto ----------------
def correr(carpeta, archivo, marcador=URL, maximo=6000, semilla=None):
    """Corre un archivo de reto. Regresa (salida de la terminal, variables del programa)."""
    for nombre in ("equipo", "rally", "dron", "reto_3_ojos", "reto_4_control"):
        sys.modules.pop(nombre, None)
    sys.modules["equipo"] = types.SimpleNamespace(EQUIPO=EQUIPO, MARCADOR=marcador)
    sys.path[:0] = [str(carpeta), str(RALLY)]
    cuadros.update(n=0, maximo=maximo, calificado=None)
    import rally
    calificar = rally.Dron._calificar

    def calificar_y_avisar(dron):
        calificar(dron)
        if dron._superado:
            cuadros["calificado"] = cuadros["n"]
    rally.Dron._calificar = calificar_y_avisar
    if semilla is not None:
        random.seed(semilla)
    salida = io.StringIO()
    variables = {}
    try:
        with contextlib.redirect_stdout(salida):
            variables = runpy.run_path(str(carpeta / archivo), run_name="__main__")
            for hilo in threading.enumerate():  # esperar a que se manden los puntos
                if hilo is not threading.current_thread() and not hilo.daemon:
                    hilo.join(5)
    except SystemExit as fin:
        salida.write(f"\n[SystemExit] {fin}")
    finally:
        del sys.path[:2]
    return salida.getvalue(), variables


ARCHIVOS = {1: "reto_1_despegue.py", 2: "reto_2_cuadrado.py", 3: "reto_3_ojos.py", 4: "reto_4_control.py",
            5: "reto_5_zigzag.py", 6: "reto_6_rescate_de_blu.py"}
resultados = []


def revisar(nombre, bien, detalle=""):
    resultados.append(bien)
    print(f"{'✅' if bien else '❌'}  {nombre}" + (f"   ({detalle})" if detalle else ""))


print(f"\nMarcador de prueba en {URL}\n")
print("— Los archivos de los alumnos, SIN completar, no deben dar puntos —")
for reto, archivo in ARCHIVOS.items():
    texto, _ = correr(RALLY, archivo, maximo=1500)
    ultima = [linea for linea in texto.splitlines() if "❌" in linea or "ℹ️" in linea]
    revisar(f"Reto {reto} sin completar", "SUPERADO" not in texto, ultima[-1].strip()[:90] if ultima else "")
revisar("El marcador sigue en 0", puntos_del_equipo()[0] == 0)

print("\n— Las soluciones sí deben pasar y mandar los puntos —")
esperado = 0
for reto, archivo in ARCHIVOS.items():
    texto, variables = correr(SOLUCIONES, archivo, semilla=reto)
    esperado += sm.PUNTOS[reto] + sm.BONO_PRIMERO
    tiempo = variables.get("dron")._t if variables.get("dron") is not None else 0
    llego = "Ya está en el marcador" in texto
    revisar(f"Reto {reto} resuelto", "SUPERADO" in texto and llego,
            f"{tiempo:.0f} s de simulador" if tiempo else "revisión de funciones")
    if "SUPERADO" not in texto or not llego:
        print(texto[-1500:])
puntos, resueltos = puntos_del_equipo()
revisar("El marcador tiene los 6 retos con bono de primeros", puntos == esperado and len(resueltos) == 6,
        f"{puntos} de {esperado} puntos")

print("\n— Blu aparece en otro lugar cada vez: el Reto 6 debe salir siempre —")
for semilla in range(10, 16):
    texto, variables = correr(SOLUCIONES, ARCHIVOS[6], semilla=semilla)
    revisar(f"Reto 6, Blu en el lugar #{semilla}", "SUPERADO" in texto, f"{variables['dron']._t:.0f} s")

print("\n— El marcador —")
texto, _ = correr(SOLUCIONES, ARCHIVOS[1])
revisar("Un reto repetido no suma otra vez", "no se repiten" in texto and puntos_del_equipo()[0] == esperado)
r = pedir("/entregar", {"equipo": "Los Pumas", "reto": 1, "codigo": "ZZZZ"})
revisar("Un código falso no cuenta", not r["ok"], r["mensaje"])
r = pedir("/staff", {"accion": "manual", "equipo": "los  pumas", "reto": 3, "codigo": sm.codigo("Los Pumas", 3)})
revisar("El staff anota un código manual", r["ok"], r["mensaje"])
r = pedir("/entregar", {"equipo": "LOS PUMAS", "reto": 3, "codigo": sm.codigo("Los Pumas", 3)})
revisar("Mayúsculas/espacios: es el mismo equipo", "no se repiten" in r["mensaje"])
pumas = next(e for e in pedir("/estado")["equipos"] if e["clave"] == "los pumas")
revisar("Segundo lugar en un reto: sin bono", pumas["puntos"] == sm.PUNTOS[3], f"{pumas['puntos']} puntos")
r = pedir("/staff", {"accion": "quitar", "equipo": "Los Pumas", "reto": 3})
revisar("El staff le quita un reto a un equipo", r["ok"] and next(
    e for e in pedir("/estado")["equipos"] if e["clave"] == "los pumas")["puntos"] == 0)
pedir("/staff", {"accion": "iniciar"})
revisar("El reloj arranca", pedir("/estado")["reloj"]["estado"] == "corriendo")
pedir("/staff", {"accion": "pausar"})
revisar("El reloj se pausa", pedir("/estado")["reloj"]["estado"] == "pausado")
sm.datos["reloj"].update(inicio=1.0, pausa=None)  # como si hubiera empezado hace muchísimo
r = pedir("/entregar", {"equipo": "Los Pumas", "reto": 2, "codigo": sm.codigo("Los Pumas", 2)})
revisar("Con el tiempo terminado ya no se aceptan retos", not r["ok"], r["mensaje"])
pedir("/staff", {"accion": "reiniciar_reloj"})
revisar("Los datos se guardan en el archivo", sm.ARCHIVO.exists() and "Equipo de Prueba" in sm.ARCHIVO.read_text())
html = urllib.request.build_opener(urllib.request.ProxyHandler({})).open(URL + "/").read().decode()
revisar("La página del marcador se sirve", "Marcador del Rally" in html)

print("\n— Sin red: el alumno recibe un código para el staff —")
texto, _ = correr(SOLUCIONES, ARCHIVOS[3], marcador="http://127.0.0.1:9")
codigo = sm.codigo(EQUIPO, 3)
revisar("Sin marcador se imprime el código", f"código: {codigo}" in texto, codigo)

print(f"\n{sum(resultados)} de {len(resultados)} revisiones bien.")
servidor.shutdown()
sys.exit(0 if all(resultados) else 1)
