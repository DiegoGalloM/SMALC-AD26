# ============================================================
#  PASO 2 — Prueba el CONTROL P (control.py)
# ============================================================
#  Este archivo NO lo modificas: solo córrelo con ▶.
#  Prueba tus funciones con 5 posiciones de la gate en una foto de 640 x 480.
#  (Los números correctos son con KP_GIRO = 0.15, KP_ALTURA = 0.20 y VELOCIDAD_MAXIMA = 25)

import control

# centro de la gate,  y lo que debería salir:  error_x, error_y, giro, subir
pruebas = [
    ((320, 240), (0, 0, 0, 0)),  # justo al centro: nada que corregir
    ((520, 240), (200, 0, 25, 0)),  # a la derecha: gira a la derecha (¡limitado a 25!)
    ((320, 100), (0, 140, 0, 25)),  # arriba: sube
    ((400, 300), (80, -60, 12, -12)),  # un poco a la derecha y abajo
    ((100, 400), (-220, -160, -25, -25)),  # muy a la izquierda y abajo
]

correctas = 0
print(f"{'centro':>12} | {'error_x':>8} {'error_y':>8} | {'giro':>6} {'subir':>6}")
print("-" * 52)
for (cx, cy), esperado in pruebas:
    error_x = control.error_horizontal(cx, 640)
    error_y = control.error_vertical(cy, 480)
    giro = control.control_p(error_x, control.KP_GIRO)
    subir = control.control_p(error_y, control.KP_ALTURA)

    obtenido = (error_x, error_y, giro, subir)
    bien = all(abs(a - b) < 0.01 for a, b in zip(obtenido, esperado))
    correctas = correctas + bien
    print(f"{str((cx, cy)):>12} | {error_x:>8} {error_y:>8} | {giro:>6.1f} {subir:>6.1f}   {'✅' if bien else '❌ debería ser ' + str(esperado)}")

print()
if correctas == len(pruebas):
    print("🎉 ¡Tu control P funciona! Sigue con paso3_movimientos.py")
else:
    print("Revisa control.py:")
    print("  - ¿error_x o error_y salen en 0?  -> completa error_horizontal() y error_vertical()")
    print("  - ¿giro o subir salen en 0?       -> completa control_p()")
    print("  - ¿Pasan de 25?                   -> te falta limitar() en control_p()")
