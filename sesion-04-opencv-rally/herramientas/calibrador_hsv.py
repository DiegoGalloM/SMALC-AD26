# ============================================================
#  CALIBRADOR HSV  (herramienta ya hecha: solo úsala)
# ============================================================
#  Encuentra el rango de color de tu objeto moviendo barritas.
#
#  Córrelo con el botón ▶ de VSCode:
#    - escribe el nombre de una imagen (por ejemplo reto_4), o
#    - presiona Enter para usar tu cámara.
#
#  Cómo calibrar:
#    1. Haz clic sobre tu objeto: en la terminal sale su color HSV (úsalo de guía).
#    2. Sube los "min" y baja los "max" hasta que en la máscara SOLO tu objeto quede blanco.
#    3. Presiona q: en la terminal aparecen BAJO y ALTO para copiarlos a tu código.

import os
import cv2

os.chdir(os.path.dirname(__file__))  # (no le muevas)
VENTANA = "calibrador"


def buscar_imagen(nombre):
    """Busca la imagen en las carpetas de lecciones y del rally."""
    if not nombre.endswith(".png"):
        nombre = nombre + ".png"
    for carpeta in ("../lecciones/imagenes", "../rally/imagenes"):
        ruta = os.path.join(carpeta, nombre)
        if os.path.exists(ruta):
            return ruta
    return None


def al_hacer_clic(evento, x, y, flags, parametro):
    if evento == cv2.EVENT_LBUTTONDOWN and x < foto.shape[1]:
        print("Color HSV donde hiciste clic:", hsv[y, x])


def barras():
    bajo = (cv2.getTrackbarPos("H min", VENTANA), cv2.getTrackbarPos("S min", VENTANA), cv2.getTrackbarPos("V min", VENTANA))
    alto = (cv2.getTrackbarPos("H max", VENTANA), cv2.getTrackbarPos("S max", VENTANA), cv2.getTrackbarPos("V max", VENTANA))
    return bajo, alto


nombre = input("¿Qué imagen quieres calibrar? (escribe su nombre, o Enter para usar la cámara): ").strip()
camara = None
if nombre == "":
    camara = cv2.VideoCapture(0)
else:
    ruta = buscar_imagen(nombre)
    if ruta is None:
        print("No encontré esa imagen. Escribe solo el nombre, por ejemplo: reto_4")
        raise SystemExit
    imagen = cv2.imread(ruta)

cv2.namedWindow(VENTANA)
for barra, inicial, maximo in [("H min", 0, 179), ("H max", 179, 179), ("S min", 0, 255),
                               ("S max", 255, 255), ("V min", 0, 255), ("V max", 255, 255)]:
    cv2.createTrackbar(barra, VENTANA, inicial, maximo, lambda valor: None)
cv2.setMouseCallback(VENTANA, al_hacer_clic)
print("Haz clic en tu objeto y mueve las barras. q = salir\n")

bajo, alto = (0, 0, 0), (179, 255, 255)
while True:
    if camara is not None:
        ok, foto = camara.read()
        foto = cv2.flip(foto, 1)
    else:
        foto = imagen.copy()
    # Si la imagen es muy grande, la hacemos más chica para que quepa junto a la máscara
    if foto.shape[1] > 640:
        foto = cv2.resize(foto, (640, int(foto.shape[0] * 640 / foto.shape[1])))

    hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    bajo, alto = barras()
    mascara = cv2.inRange(hsv, bajo, alto)
    cv2.imshow(VENTANA, cv2.hconcat([foto, cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)]))

    if cv2.waitKey(30) == ord("q") or cv2.getWindowProperty(VENTANA, cv2.WND_PROP_VISIBLE) < 1:
        break

print("\nCopia esto a tu código:")
print("BAJO =", bajo)
print("ALTO =", alto)
if camara is not None:
    camara.release()
cv2.destroyAllWindows()
