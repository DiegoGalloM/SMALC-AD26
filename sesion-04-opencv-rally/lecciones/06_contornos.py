# ============================================================
#  LECCIÓN 6 — Contornos: contar objetos y encontrar su centro
# ============================================================
#  Córrelo con el botón ▶ de VSCode.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas) para que encuentre la carpeta "imagenes"

BAJO = (0, 120, 70)  # rojo
ALTO = (8, 255, 255)
AREA_MINIMA = 0  # ✏️ MINI-RETO: ¿qué número deja SOLO las 3 manzanas?


# ✏️ COMPLETA ESTA FUNCIÓN (2 líneas)
# El centro está a la MITAD del ancho y a la MITAD del alto.
def centro(x, y, ancho, alto):
    # Pista:
    #   cx = x + ancho // 2
    #   cy = ...            <- ¡igual, pero con y y alto!
    #   return cx, cy
    return x, y


frutas = cv2.imread("imagenes/frutas.png")
hsv = cv2.cvtColor(frutas, cv2.COLOR_BGR2HSV)
mascara = cv2.inRange(hsv, BAJO, ALTO)

# Los CONTORNOS son las orillas de cada mancha blanca de la máscara
contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cuantos = 0
for contorno in contornos:
    area = cv2.contourArea(contorno)  # qué tan grande es la mancha
    if area >= AREA_MINIMA:  # las manchas muy chiquitas son "ruido"
        cuantos = cuantos + 1
        x, y, ancho, alto = cv2.boundingRect(contorno)  # el rectángulo que la encierra
        cx, cy = centro(x, y, ancho, alto)
        cv2.rectangle(frutas, (x, y), (x + ancho, y + alto), (0, 255, 0), 2)
        cv2.circle(frutas, (cx, cy), 6, (0, 0, 0), -1)
        print("Objeto", cuantos, "  área:", area, "  centro:", cx, cy)

print("Encontré", cuantos, "objetos")
cv2.imshow("contornos", frutas)
cv2.imshow("mascara", mascara)
cv2.waitKey(0)

# ✏️ MÁS MINI-RETOS
# 1) ¿Por qué con AREA_MINIMA = 0 salen más objetos que manzanas?
# 2) Busca el azul (BAJO = (100, 120, 50), ALTO = (130, 255, 255)). ¿Cuántas moras hay?
