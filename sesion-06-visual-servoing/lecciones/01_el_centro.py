ANCHO = 640
ALTO = 480

# ✏️ COMPLETA: calcula el centro horizontal y vertical del frame.
centro_x = 0
centro_y = 0

print("El frame mide", ANCHO, "por", ALTO, "pixeles")
print("Su centro esta en:", centro_x, centro_y)

objetos = [(100, 100), (320, 240), (500, 350)]
for x, y in objetos:
    print("Objeto en", (x, y), "| centro del frame:", (centro_x, centro_y))
