# ============================================================
#  INSPECTOR DE PIXELES  (herramienta ya hecha: solo úsala)
# ============================================================
#  Haz clic en cualquier parte de una imagen y te dice:
#  fila, columna, color BGR y color HSV de ese pixel.
#
#  Córrelo con el botón ▶ de VSCode y escribe el nombre de la imagen
#  (frutas, robot, manzana, reto_4, reto_5...). q = salir.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas)


def buscar_imagen(nombre):
    """Busca la imagen en las carpetas de lecciones y del rally."""
    nombre = nombre.strip() or "frutas"
    if not nombre.endswith(".png"):
        nombre = nombre + ".png"
    for carpeta in ("../lecciones/imagenes", "../rally/imagenes"):
        ruta = os.path.join(carpeta, nombre)
        if os.path.exists(ruta):
            return ruta
    return None


def al_hacer_clic(evento, x, y, flags, parametro):
    if evento == cv2.EVENT_LBUTTONDOWN:
        fila, columna = y, x
        print(f"fila {fila:4d}   columna {columna:4d}   |   BGR = {imagen[fila, columna]}   |   HSV = {hsv[fila, columna]}")


ruta = buscar_imagen(input("¿Qué imagen quieres inspeccionar? (Enter = frutas): "))
if ruta is None:
    print("No encontré esa imagen. Escribe solo el nombre, por ejemplo: robot")
    raise SystemExit

imagen = cv2.imread(ruta)
hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
print("Haz clic sobre la imagen. q = salir\n")

cv2.namedWindow("inspector")
cv2.setMouseCallback("inspector", al_hacer_clic)
while True:
    cv2.imshow("inspector", imagen)
    if cv2.waitKey(30) == ord("q") or cv2.getWindowProperty("inspector", cv2.WND_PROP_VISIBLE) < 1:
        break
cv2.destroyAllWindows()
