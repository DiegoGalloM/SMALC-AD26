# ============================================================
#  PASO 1 — Prueba los OJOS del dron (vision.py)
# ============================================================
#  Este archivo NO lo modificas: solo córrelo con ▶ y mira si tu vision.py funciona.
#  Te enseña 4 fotos de la gate (presiona una tecla para pasar a la siguiente).

import cv2

import vision
from simulador import fotos_de_prueba

correctas = 0
fotos = fotos_de_prueba()

for nombre, foto, esperado in fotos:
    mascara = vision.mascara_azul(foto)
    gate = vision.encontrar_gate(mascara)

    if gate is None:
        centro = None
    else:
        centro = vision.centro_de(gate)
        x, y, ancho, alto = gate
        cv2.rectangle(foto, (x, y), (x + ancho, y + alto), (0, 255, 0), 3)
        cv2.circle(foto, centro, 7, (0, 0, 255), -1)

    if esperado is None:
        bien = gate is None
    else:
        bien = centro is not None and abs(centro[0] - esperado[0]) <= 8 and abs(centro[1] - esperado[1]) <= 8
    correctas = correctas + bien
    print(f"{'✅' if bien else '❌'}  {nombre}:  encontré el centro en {centro}   (debería ser {esperado})")

    cv2.imshow("foto (presiona una tecla)", foto)
    cv2.imshow("mascara", mascara)
    cv2.waitKey(0)

cv2.destroyAllWindows()

print()
if correctas == len(fotos):
    print("🎉 ¡Tus ojos funcionan! Sigue con paso2_control.py")
else:
    print("Revisa vision.py:")
    print("  - ¿La máscara sale toda negra?   -> completa mascara_azul()")
    print("  - ¿No dibuja el rectángulo?      -> completa encontrar_gate()")
    print("  - ¿El punto rojo está en una esquina? -> completa centro_de()")
