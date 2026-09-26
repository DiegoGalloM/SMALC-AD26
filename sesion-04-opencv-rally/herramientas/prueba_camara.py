# ============================================================
#  PRUEBA DE CÁMARA  (herramienta ya hecha: solo úsala)
# ============================================================
#  Córrelo al inicio de la clase para ver si tu cámara funciona. q = salir.

import cv2

camara = cv2.VideoCapture(0)
ok, foto = camara.read()

if not ok:
    print("No pude usar la cámara 0.")
    print("Revisa que no la esté usando otra app (Zoom, Meet, Teams...)")
    print("o cambia el 0 por 1 en cv2.VideoCapture(0) y vuelve a probar.")
    raise SystemExit

print("¡Tu cámara funciona! Presiona q para salir.")
while True:
    ok, foto = camara.read()
    cv2.imshow("prueba de camara", foto)
    if cv2.waitKey(1) == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
