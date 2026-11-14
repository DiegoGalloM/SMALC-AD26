"""
servidor_marcador.py — el MARCADOR EN VIVO del rally (solo corre en la compu del staff)

    python servidor_marcador.py          # puerto 8000
    python servidor_marcador.py 8080     # otro puerto

1. Abre en el navegador  http://localhost:8000  y proyéctalo.
2. Los equipos ponen en su equipo.py la dirección que aparece en la pantalla
   (por ejemplo  MARCADOR = "http://192.168.1.10:8000").
3. Cada vez que un equipo pasa un reto, su programa avisa solo y el marcador se actualiza.

Todo se guarda en marcador_datos.json: si cierras el servidor y lo vuelves a abrir, nada se pierde.
Los controles del staff (reloj, códigos manuales, quitar puntos) solo funcionan desde esta compu.
Solo usa la biblioteca estándar de Python: no hay que instalar nada.
"""

import hashlib
import json
import socket
import subprocess
import sys
import threading
import time
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SAL = "smalc-ad26-rally"  # la misma que en rally/rally.py
RETOS = [  # número, nombre, puntos, dónde lo vieron
    (1, "Despegue con estilo", 100, "Sesión 7"),
    (2, "El cuadrado", 150, "Sesiones 3, 6 y 7"),
    (3, "Los ojos", 150, "Sesiones 4 y 6"),
    (4, "El control", 150, "Sesiones 5 y 6"),
    (5, "Zigzag y de regreso", 200, "Sesiones 8 y 10"),
    (6, "Jefe final: rescate de Blu", 300, "Sesión 10"),
]
PUNTOS = {n: p for n, _, p, _ in RETOS}
NOMBRES = {n: nombre for n, nombre, _, _ in RETOS}
BONO_PRIMERO = 50          # el primer equipo en pasar cada reto se lleva esto extra
MINUTOS = 50               # duración del rally
MAXIMO_EQUIPOS = 40

CARPETA = Path(__file__).resolve().parent
ARCHIVO = CARPETA / "marcador_datos.json"
candado = threading.Lock()


# =====================================================================
# Los datos
# =====================================================================
def normalizar(nombre):
    sin_acentos = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    return " ".join(sin_acentos.lower().split())


def codigo(nombre, reto):
    return hashlib.sha256(f"{SAL}|{normalizar(nombre)}|{reto}".encode()).hexdigest()[:4].upper()


def datos_nuevos():
    return {"equipos": {}, "eventos": [], "siguiente": 1,
            "reloj": {"duracion": MINUTOS * 60, "inicio": None, "pausa": None}}


def cargar():
    try:
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return datos_nuevos()


def guardar():
    temporal = ARCHIVO.with_suffix(".tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    temporal.replace(ARCHIVO)


datos = cargar()


def restante():
    r = datos["reloj"]
    if r["pausa"] is not None:
        return r["pausa"]
    if r["inicio"] is None:
        return r["duracion"]
    return max(0.0, r["duracion"] - (time.time() - r["inicio"]))


def estado_del_reloj():
    r = datos["reloj"]
    if r["pausa"] is not None:
        return "pausado"
    if r["inicio"] is None:
        return "listo"
    return "corriendo" if restante() > 0 else "terminado"


def evento(tipo, equipo, **extra):
    datos["eventos"].append({"id": datos["siguiente"], "t": time.time(), "tipo": tipo, "equipo": equipo, **extra})
    datos["siguiente"] += 1
    datos["eventos"] = datos["eventos"][-200:]


def buscar_equipo(nombre, crear=True):
    """Regresa (clave, equipo). Crea el equipo si no existe."""
    clave = normalizar(nombre)
    if not clave or len(clave) > 40:
        return None, None
    if clave not in datos["equipos"]:
        if not crear or len(datos["equipos"]) >= MAXIMO_EQUIPOS:
            return None, None
        datos["equipos"][clave] = {"nombre": " ".join(str(nombre).split())[:30], "resueltos": {},
                                   "llego": time.time()}
        evento("llego", datos["equipos"][clave]["nombre"])
    return clave, datos["equipos"][clave]


def puntos_de(equipo):
    return sum(PUNTOS[int(n)] + (BONO_PRIMERO if r["primero"] else 0) for n, r in equipo["resueltos"].items())


def anotar(nombre, reto, clave_reto, manual=False):
    """Anota un reto resuelto. Regresa (ok, mensaje)."""
    try:
        reto = int(reto)
    except (TypeError, ValueError):
        return False, "Ese reto no existe"
    if reto not in PUNTOS:
        return False, "Ese reto no existe"
    if str(clave_reto).strip().upper() != codigo(nombre, reto):
        return False, "El código no es correcto para ese equipo y ese reto"
    if not manual and estado_del_reloj() == "terminado":
        return False, "⏰ Se acabó el tiempo del rally: ese reto ya no cuenta"
    clave, equipo = buscar_equipo(nombre)
    if equipo is None:
        return False, "No pude registrar al equipo (¿nombre muy largo?)"
    if str(reto) in equipo["resueltos"]:
        return True, f"El reto {reto} ya lo tenían anotado, {equipo['nombre']}: los puntos no se repiten"
    primero = not any(str(reto) in e["resueltos"] for e in datos["equipos"].values())
    puntos = PUNTOS[reto] + (BONO_PRIMERO if primero else 0)
    equipo["resueltos"][str(reto)] = {"t": time.time(), "primero": primero, "manual": manual}
    evento("resuelto", equipo["nombre"], reto=reto, puntos=puntos, primero=primero)
    guardar()
    print(f"[{time.strftime('%H:%M:%S')}]  ✅ {equipo['nombre']} pasó el reto {reto} (+{puntos})"
          + ("  ⚡ PRIMERO" if primero else "") + ("  (manual)" if manual else ""))
    extra = f"  ⚡ ¡Fueron los PRIMEROS: +{BONO_PRIMERO} extra!" if primero else ""
    return True, f"¡+{puntos} puntos para {equipo['nombre']}! Ya está en el marcador.{extra}"


def resumen(es_staff, direcciones):
    equipos = []
    for clave, e in datos["equipos"].items():
        ultimo = max([r["t"] for r in e["resueltos"].values()], default=e["llego"])
        equipos.append({"clave": clave, "nombre": e["nombre"], "puntos": puntos_de(e), "resueltos": e["resueltos"],
                        "ultimo": ultimo})
    # Más puntos arriba; si empatan, gana el que llegó primero a esos puntos
    equipos.sort(key=lambda e: (-e["puntos"], e["ultimo"] if e["puntos"] else 0, e["nombre"].lower()))
    primeros = {}
    for e in equipos:
        for n, r in e["resueltos"].items():
            if r["primero"]:
                primeros[n] = e["nombre"]
    return {
        "retos": [{"n": n, "nombre": nombre, "puntos": p, "sesion": s, "primero": primeros.get(str(n))}
                  for n, nombre, p, s in RETOS],
        "bono": BONO_PRIMERO,
        "equipos": equipos,
        "eventos": datos["eventos"][-40:],
        "reloj": {"restante": restante(), "duracion": datos["reloj"]["duracion"], "estado": estado_del_reloj()},
        "direcciones": direcciones,
        "staff": es_staff,
        "ahora": time.time(),
    }


def accion_del_staff(pedido):
    accion = pedido.get("accion")
    r = datos["reloj"]
    if accion == "iniciar":
        if r["pausa"] is not None:
            r["inicio"], r["pausa"] = time.time() - (r["duracion"] - r["pausa"]), None
        elif r["inicio"] is None:
            r["inicio"] = time.time()
        evento("reloj", "", texto="▶ ¡Arranca el rally!")
    elif accion == "pausar":
        if estado_del_reloj() == "corriendo":
            r["pausa"], r["inicio"] = restante(), None
            evento("reloj", "", texto="⏸ Rally en pausa")
    elif accion == "reiniciar_reloj":
        r["inicio"], r["pausa"] = None, None
    elif accion == "minutos":
        try:
            minutos = max(1, min(240, int(pedido.get("minutos"))))
        except (TypeError, ValueError):
            return False, "Minutos inválidos"
        corriendo = estado_del_reloj() == "corriendo"
        transcurrido = r["duracion"] - restante()
        r["duracion"] = minutos * 60
        if corriendo:
            r["inicio"] = time.time() - transcurrido
        elif r["pausa"] is not None:
            r["pausa"] = max(0.0, r["duracion"] - transcurrido)
    elif accion == "manual":
        return anotar(pedido.get("equipo", ""), pedido.get("reto"), pedido.get("codigo", ""), manual=True)
    elif accion == "quitar":
        equipo = datos["equipos"].get(normalizar(pedido.get("equipo", "")))
        if equipo is None or str(pedido.get("reto")) not in equipo["resueltos"]:
            return False, "No encontré ese reto en ese equipo"
        del equipo["resueltos"][str(pedido.get("reto"))]
        print(f"[{time.strftime('%H:%M:%S')}]  ↩️  Se le quitó el reto {pedido.get('reto')} a {equipo['nombre']}")
    elif accion == "borrar_equipo":
        if datos["equipos"].pop(normalizar(pedido.get("equipo", "")), None) is None:
            return False, "No encontré ese equipo"
    elif accion == "borrar_todo":
        datos.clear()
        datos.update(datos_nuevos())
        print(f"[{time.strftime('%H:%M:%S')}]  🧹 Marcador borrado")
    else:
        return False, "Acción desconocida"
    guardar()
    return True, "Listo"


# =====================================================================
# El servidor web
# =====================================================================
class Marcador(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # sin una línea por cada consulta: la terminal solo muestra lo importante

    def _responder(self, codigo_http, cuerpo, tipo="application/json; charset=utf-8"):
        if not isinstance(cuerpo, bytes):
            cuerpo = json.dumps(cuerpo, ensure_ascii=False).encode()
        self.send_response(codigo_http)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _es_staff(self):
        return self.client_address[0] in ("127.0.0.1", "::1", "::ffff:127.0.0.1")

    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta in ("/", "/index.html", "/marcador.html"):
            self._responder(200, (CARPETA / "marcador.html").read_bytes(), "text/html; charset=utf-8")
        elif ruta == "/estado":
            with candado:
                self._responder(200, resumen(self._es_staff(), self.server.direcciones))
        else:
            self._responder(404, {"ok": False, "mensaje": "No existe"})

    def do_POST(self):
        largo = int(self.headers.get("Content-Length") or 0)
        if largo > 10_000:
            self._responder(413, {"ok": False, "mensaje": "Mensaje demasiado grande"})
            return
        try:
            pedido = json.loads(self.rfile.read(largo).decode() or "{}")
            if not isinstance(pedido, dict):
                raise ValueError
        except ValueError:
            self._responder(400, {"ok": False, "mensaje": "No entendí el mensaje"})
            return
        ruta = self.path.split("?")[0]
        with candado:
            if ruta == "/hola":
                _, equipo = buscar_equipo(pedido.get("equipo", ""))
                if equipo is None:
                    self._responder(400, {"ok": False, "mensaje": "No pude registrar al equipo"})
                    return
                guardar()
                self._responder(200, {"ok": True, "mensaje": f"¡Hola, {equipo['nombre']}! Ya aparecen en el marcador."})
            elif ruta == "/entregar":
                ok, mensaje = anotar(pedido.get("equipo", ""), pedido.get("reto"), pedido.get("codigo", ""))
                self._responder(200 if ok else 400, {"ok": ok, "mensaje": mensaje})
            elif ruta == "/staff":
                if not self._es_staff():
                    self._responder(403, {"ok": False, "mensaje": "Los controles solo funcionan en la compu del staff"})
                    return
                ok, mensaje = accion_del_staff(pedido)
                self._responder(200 if ok else 400, {"ok": ok, "mensaje": mensaje})
            else:
                self._responder(404, {"ok": False, "mensaje": "No existe"})


def mis_direcciones():
    """Las IPs de esta compu en la red local (las que los equipos ponen en equipo.py). La principal va primero."""
    def validas(ips):
        return [ip for ip in ips if "." in ip and not ip.startswith(("127.", "169.254.", "0.", "172.17."))]

    try:  # la IP por la que esta compu sale a la red (no manda nada: solo pregunta la ruta)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            principal = validas([s.getsockname()[0]])
        if principal:
            return principal
    except OSError:
        pass
    otras = []  # sin ruta a internet (por ejemplo, si esta compu ES el hotspot): todas las que tenga
    if sys.platform.startswith("linux"):
        try:
            otras = subprocess.run(["hostname", "-I"], capture_output=True, text=True, timeout=2).stdout.split()
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        otras += socket.gethostbyname_ex(socket.gethostname())[2]
    except OSError:
        pass
    return list(dict.fromkeys(validas(otras)))


def main():
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    try:
        servidor = ThreadingHTTPServer(("0.0.0.0", puerto), Marcador)
    except OSError:
        raise SystemExit(f"El puerto {puerto} ya está ocupado (¿el marcador ya está abierto?). Prueba: "
                         f"python servidor_marcador.py {puerto + 1}")
    servidor.direcciones = [f"http://{ip}:{puerto}" for ip in mis_direcciones()]
    print("\n🏁 Marcador del rally listo")
    print(f"   Proyecta:  http://localhost:{puerto}")
    if servidor.direcciones:
        print("   En el equipo.py de cada equipo:")
        for direccion in servidor.direcciones:
            print(f'      MARCADOR = "{direccion}"')
    else:
        print("   ⚠️  No encontré la IP de esta compu. ¿Estás conectado al WiFi o al hotspot?")
    print(f"   Datos: {ARCHIVO.name} ({len(datos['equipos'])} equipos guardados)")
    print("   Ctrl+C para cerrar.\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nMarcador cerrado. Los puntos quedaron guardados.")


if __name__ == "__main__":
    main()
