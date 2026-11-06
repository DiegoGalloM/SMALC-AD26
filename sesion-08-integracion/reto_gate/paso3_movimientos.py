# ============================================================
#  PASO 3 — Prueba los MÚSCULOS del dron (movimientos.py)
# ============================================================
#  Este archivo NO lo modificas: solo córrelo con ▶.
#  Primero revisa qué manda cada función; si todo está bien, el dron del simulador
#  despega y hace una pequeña demostración (q = salir).

import time

import movimientos
from conexion import conectar, leer_foto, mostrar, terminar
from simulador import TelloSimulado

tello = TelloSimulado()
tello.is_flying = True  # para la revisión, hacemos como que ya está en el aire

pruebas = [
    ("girar(tello)", lambda: movimientos.girar(tello), (0, 0, 0, movimientos.VELOCIDAD_GIRO)),
    ("avanzar(tello)", lambda: movimientos.avanzar(tello), (0, movimientos.VELOCIDAD_AVANCE, 0, 0)),
    ("corregir(tello, giro=12, subir=-5, adelante=20)", lambda: movimientos.corregir(tello, 12, -5, 20), (0, 20, -5, 12)),
]

correctas = 0
for nombre, funcion, esperado in pruebas:
    funcion()
    bien = tello.ultimo_rc == esperado
    correctas = correctas + bien
    print(f"{'✅' if bien else '❌'}  {nombre} mandó send_rc_control{tello.ultimo_rc}   (debería ser {esperado})")

if correctas < len(pruebas):
    print("\nRevisa movimientos.py: ¿cada número está en su lugar? (lado, adelante, arriba, giro)")
    raise SystemExit

print("\n🎉 ¡Tus movimientos funcionan! Mira la demostración en la ventana...")

tello = conectar("simulador")
tello.takeoff()
inicio = time.time()
while time.time() - inicio < 9:
    segundos = time.time() - inicio
    if segundos < 3:
        movimientos.girar(tello)
        accion = "girar"
    elif segundos < 6:
        movimientos.avanzar(tello)
        accion = "avanzar"
    else:
        movimientos.corregir(tello, -15, 10, 15)
        accion = "corregir(giro=-15, subir=10, adelante=15)"
    foto = leer_foto(tello)
    if mostrar(tello, foto, foto[:, :, 0] * 0, accion, None) == "q":
        break
terminar(tello)
print("Sigue con mision.py")
