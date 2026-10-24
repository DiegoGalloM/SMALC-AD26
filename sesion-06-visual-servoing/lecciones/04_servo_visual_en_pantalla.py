import cv2

BAJO = (40, 70, 50)
ALTO = (85, 255, 255)
AREA_MINIMA = 500
KP_X = 0.08
KP_Y = 0.08
SALIDA_MAXIMA = 30

camara = cv2.VideoCapture(0)

while True:
    ok, frame = camara.read()
    if not ok:
        break

    alto, ancho = frame.shape[:2]
    centro_x = ancho // 2
    centro_y = alto // 2
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, BAJO, ALTO)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidatos = [c for c in contornos if cv2.contourArea(c) >= AREA_MINIMA]

    cv2.drawMarker(frame, (centro_x, centro_y), (255, 255, 255), cv2.MARKER_CROSS, 24, 2)
    if candidatos:
        x, y, w, h = cv2.boundingRect(max(candidatos, key=cv2.contourArea))
        objeto_x = x + w // 2
        objeto_y = y + h // 2
        error_x = objeto_x - centro_x
        error_y = objeto_y - centro_y
        # ✏️ COMPLETA: salida proporcional = ganancia * error, limitada por SALIDA_MAXIMA.
        salida_x = max(-SALIDA_MAXIMA, min(SALIDA_MAXIMA, KP_X * 1))
        salida_y = max(-SALIDA_MAXIMA, min(SALIDA_MAXIMA, KP_Y * 1))

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (objeto_x, objeto_y), 6, (0, 0, 255), -1)
        cv2.line(frame, (centro_x, centro_y), (objeto_x, objeto_y), (255, 0, 0), 2)
        cv2.putText(frame, f"Error x,y: {error_x}, {error_y}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Salida P x,y: {salida_x}, {salida_y}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No veo el color", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Practica de servo visual", frame)
    cv2.imshow("Mascara", mascara)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()
