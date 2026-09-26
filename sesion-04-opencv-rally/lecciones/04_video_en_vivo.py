# ============================================================
#  LECCIÓN 4 — Video en vivo
# ============================================================
#  Un video son MUCHAS fotos, una tras otra.
#  Córrelo con el botón ▶ de VSCode. Presiona q para salir.

import cv2


# ✏️ COMPLETA ESTA FUNCIÓN (1 línea): voltea la foto como un espejo
def efecto(foto):
    # Pista: return cv2.flip(foto, 1)
    #
    # ✏️ MINI-RETO: cuando funcione el espejo, prueba estos efectos (uno a la vez):
    #   return cv2.cvtColor(foto, cv2.COLOR_BGR2GRAY)       -> grises
    #   return cv2.applyColorMap(foto, cv2.COLORMAP_JET)    -> cámara "térmica"
    #   return cv2.GaussianBlur(foto, (25, 25), 0)          -> borroso
    return foto


camara = cv2.VideoCapture(0)  # 0 = tu cámara (si no funciona, prueba con 1)

while True:
    ok, foto = camara.read()  # 1) LEER una foto de la cámara
    foto = efecto(foto)  # 2) CAMBIARLA
    cv2.imshow("camara", foto)  # 3) MOSTRARLA
    if cv2.waitKey(1) == ord("q"):  # 4) si presionas q, se acaba
        break

camara.release()
cv2.destroyAllWindows()
