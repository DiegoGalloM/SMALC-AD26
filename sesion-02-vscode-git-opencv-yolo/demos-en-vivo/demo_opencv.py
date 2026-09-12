"""
Muestra 5 "modos" de OpenCV en tiempo real desde la camara.

Modos (cambia con las teclas 1-5):
  1 = imagen original
  2 = mascara HSV (filtrado por color)
  3 = thresholding (blanco y negro puro)
  4 = contornos dibujados sobre la mascara HSV
  5 = kernel / desenfoque (GaussianBlur)

Presiona 'q' para salir.
"""


cap = cv2.VideoCapture(0)
mode = 1

def nothing(x):
    pass

cv2.namedWindow("Demo")
cv2.createTrackbar("H min", "Demo", 0, 179, nothing)
cv2.createTrackbar("H max", "Demo", 179, 179, nothing)
cv2.createTrackbar("S min", "Demo", 80, 255, nothing)
cv2.createTrackbar("V min", "Demo", 80, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("1"), ord("2"), ord("3"), ord("4"), ord("5")):
        mode = int(chr(key))
    elif key == ord("q"):
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h_min = cv2.getTrackbarPos("H min", "Demo")
    h_max = cv2.getTrackbarPos("H max", "Demo")
    s_min = cv2.getTrackbarPos("S min", "Demo")
    v_min = cv2.getTrackbarPos("V min", "Demo")
    mask = cv2.inRange(hsv, (h_min, s_min, v_min), (h_max, 255, 255))

    if mode == 1:
        out = frame
    elif mode == 2:
        out = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    elif mode == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        out = cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)
    elif mode == 4:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = frame.copy()
        cv2.drawContours(out, contours, -1, (0, 255, 0), 3)
    elif mode == 5:
        out = cv2.GaussianBlur(frame, (25, 25), 0)
    else:
        out = frame

    cv2.imshow("Demo", out)

cap.release()
cv2.destroyAllWindows()
