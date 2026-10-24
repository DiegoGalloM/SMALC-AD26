import cv2

BAJO = (40, 70, 50)
ALTO = (85, 255, 255)
AREA_MINIMA = 500

camara = cv2.VideoCapture(0)

while True:
    ok, frame = camara.read()
    if not ok:
        break

    alto, ancho = frame.shape[:2]
    centro_frame = (ancho // 2, alto // 2)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, BAJO, ALTO)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawMarker(frame, centro_frame, (255, 255, 255), cv2.MARKER_CROSS, 24, 2)

    candidatos = [c for c in contornos if cv2.contourArea(c) >= AREA_MINIMA]
    if candidatos:
        contorno = max(candidatos, key=cv2.contourArea)
        x, y, ancho_objeto, alto_objeto = cv2.boundingRect(contorno)
        # ✏️ COMPLETA: calcula el centro del rectangulo detectado.
        centro_objeto = (x,y)
        cv2.rectangle(frame, (x, y), (x + ancho_objeto, y + alto_objeto), (0, 255, 0), 2)
        cv2.circle(frame, centro_objeto, 6, (0, 0, 255), -1)
        cv2.line(frame, centro_frame, centro_objeto, (255, 0, 0), 2)

    cv2.imshow("Objeto y centro del frame", frame)
    cv2.imshow("Mascara del color", mascara)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
