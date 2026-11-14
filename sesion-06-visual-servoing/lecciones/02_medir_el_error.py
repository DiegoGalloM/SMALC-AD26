ANCHO = 640
ALTO = 480
centro_x = ANCHO // 2
centro_y = ALTO // 2

posiciones = [(100, 100), (320, 240), (500, 350), (320, 100)]

for x, y in posiciones:
    # ✏️ COMPLETA: resta el centro a la posicion del objeto en cada eje.
    error_x = x - centro_x
    error_y = y - centro_y
    print("Objeto:", (x, y), " Error (x, y):", (error_x, error_y))
