"""
DEMO DEL GANCHO — para abrir la clase: "¿cómo ve una computadora?"

El instructor lo proyecta con la webcam al inicio de la sesión. Al final del día
los alumnos van a entender (y haber programado) casi todos estos modos.

Teclas:
  1 = normal         2 = grises          3 = threshold      4 = bordes (Canny)
  5 = caricatura     6 = visión térmica  7 = pixelado       8 = rastreador de color rojo
  q = salir

Cómo correrlo (desde la carpeta sesion-04-opencv-rally):
  python demo/demo_gancho.py
"""

import cv2

MODOS = {
    ord("1"): "normal",
    ord("2"): "grises",
    ord("3"): "threshold",
    ord("4"): "bordes",
    ord("5"): "caricatura",
    ord("6"): "termica",
    ord("7"): "pixelado",
    ord("8"): "rastreador",
}
ROJO_BAJO, ROJO_ALTO = (0, 120, 70), (8, 255, 255)


def procesar(frame, modo):
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if modo == "grises":
        return cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)
    if modo == "threshold":
        _, binaria = cv2.threshold(gris, 120, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(binaria, cv2.COLOR_GRAY2BGR)
    if modo == "bordes":
        bordes = cv2.Canny(cv2.GaussianBlur(gris, (5, 5), 0), 50, 150)
        return cv2.cvtColor(bordes, cv2.COLOR_GRAY2BGR)
    if modo == "caricatura":
        colores = cv2.bilateralFilter(frame, 9, 150, 150)
        lineas = cv2.adaptiveThreshold(cv2.medianBlur(gris, 7), 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 9, 5)
        return cv2.bitwise_and(colores, colores, mask=lineas)
    if modo == "termica":
        return cv2.applyColorMap(gris, cv2.COLORMAP_JET)
    if modo == "pixelado":
        alto, ancho = frame.shape[:2]
        chica = cv2.resize(frame, (ancho // 16, alto // 16), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(chica, (ancho, alto), interpolation=cv2.INTER_NEAREST)
    if modo == "rastreador":
        salida = frame.copy()
        mascara = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), ROJO_BAJO, ROJO_ALTO)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        grandes = [c for c in contornos if cv2.contourArea(c) > 500]
        if grandes:
            (x, y), radio = cv2.minEnclosingCircle(max(grandes, key=cv2.contourArea))
            cv2.circle(salida, (int(x), int(y)), int(radio), (0, 255, 0), 3)
            cv2.circle(salida, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.putText(salida, "OBJETIVO", (int(x) - 60, int(y - radio) - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        return salida
    return frame


camara = cv2.VideoCapture(0)
if not camara.isOpened():
    print("\nNo pude abrir la cámara. Prueba: python herramientas/prueba_camara.py\n")
    raise SystemExit

VENTANA = "Como ve una computadora? (1-8 cambia de modo, q = salir)"
modo = "normal"
print("\nTeclas: 1 normal  2 grises  3 threshold  4 bordes  5 caricatura  6 termica  7 pixelado  8 rastreador  q salir\n")

while True:
    ok, frame = camara.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    salida = procesar(frame, modo)
    cv2.rectangle(salida, (0, 0), (260, 42), (0, 0, 0), -1)
    cv2.putText(salida, f"modo: {modo}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (57, 255, 20), 2, cv2.LINE_AA)
    cv2.imshow(VENTANA, salida)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord("q") or cv2.getWindowProperty(VENTANA, cv2.WND_PROP_VISIBLE) < 1:
        break
    modo = MODOS.get(tecla, modo)

camara.release()
cv2.destroyAllWindows()
