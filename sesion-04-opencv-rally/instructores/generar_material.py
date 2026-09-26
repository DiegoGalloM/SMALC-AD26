"""
GENERADOR DE MATERIAL — solo para instructores (NO subir a la rama de alumnos)

Dibuja con OpenCV todas las imágenes del taller:
  - lecciones/imagenes/ -> las que usan las lecciones (misterio, manzana, frutas, robot)
  - rally/imagenes/     -> las imágenes de los retos 1 a 5, con las claves escondidas
  - instructores/respuestas.md -> hoja de respuestas para el staff

Para cambiar las claves entre ediciones, edita RESPUESTAS y vuelve a correr:
  python instructores/generar_material.py
Después corre probar_soluciones.py para confirmar que cada reto da su clave.
"""

from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE LA EDICIÓN
# ---------------------------------------------------------------------------
RESPUESTAS = {
    "reto_1": "VISION",   # solo letras A-Z, máximo 25 letras
    "reto_2": "RESCATE",  # letras, números y espacios
    "reto_3": "TOMATE",   # letras, números y espacios (máximo ~8 caracteres para que quepa)
    "reto_4": 23,         # cuántas pelotas rojas hay (entre 10 y 35)
    "reto_5": "G5",       # casilla del tesoro: columna A-J + fila 1-7
}
SEMILLA = 2026  # cambia la semilla para que el acomodo aleatorio también cambie

BASE = Path(__file__).resolve().parent.parent
CARPETA_IMAGENES = BASE / "lecciones" / "imagenes"
CARPETA_RETOS = BASE / "rally" / "imagenes"

# Estos valores también están escritos en los archivos de los retos.
# Si los cambias aquí, cámbialos allá.
RETO1_FILA_SECRETA = 237
RETO1_COLUMNAS = range(30, 600, 20)
RETO5_MARGEN = 50
RETO5_CELDA = 90
RETO5_LETRAS = "ABCDEFGHIJ"
RETO5_FILAS = 7
RETO5_TESORO_HSV = (60, 230, 200)  # el rango del reto 5 es H 57-63, S 200-255, V 150-255

rng = np.random.default_rng(SEMILLA)


def hsv_a_bgr(h, s, v):
    pixel = np.uint8([[[h, s, v]]])
    b, g, r = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)[0, 0]
    return int(b), int(g), int(r)


def guardar(ruta, imagen):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(ruta), imagen)
    print(f"  {ruta.relative_to(BASE)}")


def fruta_sombreada(imagen, centro, radio, color_bgr, brillo=True):
    """Círculo con sombreado radial: el color cambia de oscuro a claro pero el tono (H) se queda igual."""
    alto, ancho = imagen.shape[:2]
    yy, xx = np.mgrid[0:alto, 0:ancho]
    cx, cy = centro
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dentro = dist <= radio
    # Luz que viene de arriba a la izquierda
    luz = 1.0 - 0.35 * np.clip(((xx - cx + radio * 0.35) ** 2 + (yy - cy + radio * 0.35) ** 2) ** 0.5 / (radio * 1.4), 0, 1)
    color = np.array(color_bgr, dtype=np.float32)
    for c in range(3):
        canal = imagen[:, :, c].astype(np.float32)
        canal[dentro] = color[c] * luz[dentro]
        imagen[:, :, c] = np.clip(canal, 0, 255).astype(np.uint8)
    if brillo:
        bx, by = int(cx - radio * 0.38), int(cy - radio * 0.38)
        cv2.circle(imagen, (bx, by), max(2, radio // 6), (245, 245, 245), -1, cv2.LINE_AA)


# ---------------------------------------------------------------------------
# IMÁGENES DE LAS LECCIONES
# ---------------------------------------------------------------------------
def generar_misterio():
    # 16x16: la cara del robot de SMALC en pixel art
    dibujo = [
        "                ",
        "      oooo      ",
        "       ||       ",
        "  ############  ",
        "  #iiiiiiiiii#  ",
        "  #iEEiiiiEEi#  ",
        "  #iEEiiiiEEi#  ",
        "  #iiiiiiiiii#  ",
        "  #iiiiiiiiii#  ",
        "  #iSiiiiiiSi#  ",
        "  #iiSSSSSSii#  ",
        "  #iiiiiiiiii#  ",
        "  ############  ",
        "     |    |     ",
        "    ###  ###    ",
        "                ",
    ]
    grises = {" ": 20, "#": 180, "i": 70, "E": 255, "S": 230, "o": 255, "|": 180}
    # Números "redondos" para que el juego de adivinar sea claro
    gris = np.zeros((16, 16), np.uint8)
    for fila, renglon in enumerate(dibujo):
        for columna, letra in enumerate(renglon):
            gris[fila, columna] = grises[letra]
    guardar(CARPETA_IMAGENES / "misterio.png", gris)


def generar_manzana():
    alto, ancho = 480, 640
    fondo = np.linspace(242, 226, alto, dtype=np.float32)[:, None].repeat(ancho, axis=1)
    imagen = np.dstack([fondo, fondo, fondo]).astype(np.uint8)
    # Sombra suave debajo de la manzana
    sombra = np.zeros((alto, ancho), np.uint8)
    cv2.ellipse(sombra, (335, 395), (150, 28), 0, 0, 360, 255, -1)
    sombra = cv2.GaussianBlur(sombra, (41, 41), 0).astype(np.float32) / 255.0
    imagen = (imagen * (1 - 0.25 * sombra[:, :, None])).astype(np.uint8)
    # Cuerpo de la manzana: dos círculos que se juntan
    fruta_sombreada(imagen, (280, 265), 120, (45, 40, 205), brillo=False)
    fruta_sombreada(imagen, (365, 265), 120, (45, 40, 205), brillo=False)
    cv2.circle(imagen, (270, 215), 22, (215, 215, 245), -1, cv2.LINE_AA)  # brillo
    # Rabito y hoja
    cv2.line(imagen, (322, 160), (338, 110), (30, 55, 90), 10, cv2.LINE_AA)
    cv2.ellipse(imagen, (380, 125), (46, 20), -25, 0, 360, (50, 150, 60), -1, cv2.LINE_AA)
    guardar(CARPETA_IMAGENES / "manzana.png", imagen)


def generar_frutas():
    alto, ancho = 540, 800
    imagen = np.full((alto, ancho, 3), (200, 222, 236), np.uint8)
    ruido = rng.integers(-6, 7, (alto, ancho, 1))
    imagen = np.clip(imagen.astype(np.int16) + ruido, 0, 255).astype(np.uint8)
    rojo, verde, naranja, azul = (40, 40, 210), (55, 180, 70), (20, 140, 250), (170, 70, 40)
    # Manzanas rojas (grande, mediana, chica)
    fruta_sombreada(imagen, (170, 170), 85, rojo)
    fruta_sombreada(imagen, (610, 400), 60, rojo)
    fruta_sombreada(imagen, (420, 110), 38, rojo)
    # Limones verdes
    fruta_sombreada(imagen, (330, 330), 50, verde)
    fruta_sombreada(imagen, (700, 150), 42, verde)
    # Naranja
    fruta_sombreada(imagen, (160, 420), 70, naranja)
    # Plátano (un arco grueso)
    cv2.ellipse(imagen, (470, 300), (130, 95), 0, 20, 140, (40, 210, 240), 36, cv2.LINE_AA)
    # Moras azules
    for (x, y) in [(330, 470), (365, 490), (395, 460), (430, 500), (520, 470), (555, 505), (300, 505), (470, 460)]:
        fruta_sombreada(imagen, (x, y), int(rng.integers(12, 16)), azul)
    # Migajas rojas: sirven para hablar de ruido y área mínima en la lección 6
    for (x, y) in [(290, 90), (560, 250), (720, 300), (260, 250), (520, 60)]:
        cv2.circle(imagen, (x, y), 3, rojo, -1)
    guardar(CARPETA_IMAGENES / "frutas.png", imagen)


def generar_robot():
    alto, ancho = 480, 640
    imagen = np.full((alto, ancho, 3), (238, 236, 232), np.uint8)
    verde, neon, oscuro = (80, 185, 63), (20, 255, 57), (35, 27, 21)
    # Antena
    cv2.line(imagen, (320, 95), (320, 45), verde, 10, cv2.LINE_AA)
    cv2.circle(imagen, (320, 38), 17, (60, 60, 230), -1, cv2.LINE_AA)
    # Cabeza (rectángulo redondeado)
    x1, y1, x2, y2, r = 170, 95, 470, 355, 45
    cv2.rectangle(imagen, (x1 + r, y1), (x2 - r, y2), oscuro, -1)
    cv2.rectangle(imagen, (x1, y1 + r), (x2, y2 - r), oscuro, -1)
    for cx, cy in [(x1 + r, y1 + r), (x2 - r, y1 + r), (x1 + r, y2 - r), (x2 - r, y2 - r)]:
        cv2.circle(imagen, (cx, cy), r, oscuro, -1, cv2.LINE_AA)
    cv2.line(imagen, (x1 + r, y1), (x2 - r, y1), verde, 8, cv2.LINE_AA)
    cv2.line(imagen, (x1 + r, y2), (x2 - r, y2), verde, 8, cv2.LINE_AA)
    cv2.line(imagen, (x1, y1 + r), (x1, y2 - r), verde, 8, cv2.LINE_AA)
    cv2.line(imagen, (x2, y1 + r), (x2, y2 - r), verde, 8, cv2.LINE_AA)
    for (cx, cy), inicio in [((x1 + r, y1 + r), 180), ((x2 - r, y1 + r), 270), ((x2 - r, y2 - r), 0), ((x1 + r, y2 - r), 90)]:
        cv2.ellipse(imagen, (cx, cy), (r, r), 0, inicio, inicio + 90, verde, 8, cv2.LINE_AA)
    # Ojos (aquí van los lentes del mini-reto de la lección 2)
    cv2.rectangle(imagen, (230, 170), (285, 225), neon, -1)
    cv2.rectangle(imagen, (355, 170), (410, 225), neon, -1)
    # Sonrisa
    cv2.ellipse(imagen, (320, 270), (70, 35), 0, 20, 160, (243, 237, 230), 9, cv2.LINE_AA)
    # Cuerpo
    cv2.rectangle(imagen, (230, 370), (410, 470), oscuro, -1)
    cv2.rectangle(imagen, (230, 370), (410, 470), verde, 6)
    cv2.circle(imagen, (320, 420), 18, (60, 60, 230), -1, cv2.LINE_AA)
    guardar(CARPETA_IMAGENES / "robot.png", imagen)


# ---------------------------------------------------------------------------
# IMÁGENES DEL RALLY
# ---------------------------------------------------------------------------
def texto_centrado(lienzo, texto, centro_y, escala, grosor, valor, fuente=cv2.FONT_HERSHEY_DUPLEX):
    (w, h), _ = cv2.getTextSize(texto, fuente, escala, grosor)
    x = (lienzo.shape[1] - w) // 2
    cv2.putText(lienzo, texto, (x, centro_y + h // 2), fuente, escala, valor, grosor, cv2.LINE_8)


def generar_reto_1():
    """Confeti de colores. En la FILA_SECRETA, el canal ROJO guarda la clave (A=1, B=2, ... Z=26)."""
    clave = RESPUESTAS["reto_1"].upper()
    assert clave.isalpha() and clave.isascii() and len(clave) < len(RETO1_COLUMNAS), "reto_1: solo letras A-Z"
    bloques = rng.integers(0, 256, (60, 60, 3), dtype=np.uint8)
    imagen = cv2.resize(bloques, (600, 600), interpolation=cv2.INTER_NEAREST)
    trampa_azul, trampa_verde = "AZUL" * 10, "VERDE" * 10
    for i, columna in enumerate(RETO1_COLUMNAS):
        azul = ord(trampa_azul[i]) - 64
        verde = ord(trampa_verde[i]) - 64
        if i < len(clave):
            rojo = ord(clave[i]) - 64
        elif i == len(clave):
            rojo = 0  # fin del mensaje
        else:
            rojo = int(rng.integers(30, 256))
        imagen[RETO1_FILA_SECRETA, columna] = (azul, verde, rojo)
    guardar(CARPETA_RETOS / "reto_1.png", imagen)


def generar_reto_2():
    """Imagen casi negra. Cada texto tiene un brillo distinto y solo aparece con el umbral correcto."""
    alto, ancho = 500, 900
    gris = rng.integers(12, 28, (alto, ancho), dtype=np.uint8)  # ruido de fondo: 12 a 27
    # (texto, altura, escala, grosor, brillo). Umbral correcto para la clave: 27 a 39
    capas = [
        ("NO ES AQUI, SIGUE BAJANDO", 80, 1.1, 2, 110),
        ("CASI... BAJA MAS EL UMBRAL", 400, 1.1, 2, 65),
        (f"CLAVE: {RESPUESTAS['reto_2'].upper()}", 240, 2.2, 5, 40),
    ]
    for texto, y, escala, grosor, brillo in capas:
        mascara = np.zeros_like(gris)
        texto_centrado(mascara, texto, y, escala, grosor, 255)
        # Texto "punteado": solo 35% de sus pixeles se encienden. A simple vista casi no se nota,
        # pero con el umbral correcto las letras aparecen clarísimas.
        punteado = (mascara > 0) & (rng.random(gris.shape) < 0.35)
        gris[punteado] = brillo
    guardar(CARPETA_RETOS / "reto_2.png", cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR))


def generar_reto_3():
    """Cada canal guarda una palabra en 255, escondida entre ruido de 0 a 235.
    Juntos, las letras se enciman y no se lee nada; hay que separar canales y aplicar threshold (> 235)."""
    alto, ancho = 500, 900
    palabras = {0: "AQUI NO", 1: "TAMPOCO", 2: RESPUESTAS["reto_3"].upper()}  # 0=azul 1=verde 2=rojo
    canales = []
    for indice in range(3):
        bloques = rng.integers(0, 236, (alto // 10, ancho // 10), dtype=np.uint8)
        canal = cv2.resize(bloques, (ancho, alto), interpolation=cv2.INTER_NEAREST)
        mascara = np.zeros((alto, ancho), np.uint8)
        texto_centrado(mascara, palabras[indice], alto // 2, 4.2, 22, 255, cv2.FONT_HERSHEY_SIMPLEX)
        canal[mascara > 0] = 255
        canales.append(canal)
    guardar(CARPETA_RETOS / "reto_3.png", cv2.merge(canales))


def colocar_circulos(cantidad_total, alto, ancho, radio_min, radio_max, margen):
    circulos = []
    intentos = 0
    while len(circulos) < cantidad_total:
        intentos += 1
        assert intentos < 200000, "No cupieron todos los círculos; baja la cantidad"
        r = int(rng.integers(radio_min, radio_max + 1))
        x = int(rng.integers(margen + r, ancho - margen - r))
        y = int(rng.integers(margen + r, alto - margen - r))
        if all((x - cx) ** 2 + (y - cy) ** 2 > (r + cr + 6) ** 2 for cx, cy, cr in circulos):
            circulos.append((x, y, r))
    return circulos


def generar_reto_4():
    """Pelotas de muchos colores. Solo hay que contar las ROJAS brillantes."""
    rojas = int(RESPUESTAS["reto_4"])
    alto, ancho = 720, 1080
    imagen = np.full((alto, ancho, 3), 226, np.uint8)
    # (nombre, cantidad, rango H, rango S, rango V)
    tipos = [
        ("rojo", rojas, (0, 3), (200, 240), (210, 245)),
        ("naranja", 12, (12, 15), (220, 245), (235, 255)),
        ("guinda", 10, (0, 3), (200, 235), (90, 120)),
        ("rosa", 10, (168, 172), (80, 110), (240, 255)),
        ("amarillo", 8, (26, 30), (200, 240), (230, 255)),
        ("verde", 8, (55, 65), (180, 230), (150, 200)),
        ("azul", 8, (105, 115), (180, 230), (180, 230)),
        ("morado", 8, (135, 145), (150, 200), (150, 200)),
    ]
    lista = [t for t in tipos for _ in range(t[1])]
    rng.shuffle(lista)
    circulos = colocar_circulos(len(lista), alto, ancho, 12, 26, 12)
    for (x, y, r), (nombre, _, hr, sr, vr) in zip(circulos, lista):
        color = hsv_a_bgr(int(rng.integers(hr[0], hr[1] + 1)), int(rng.integers(sr[0], sr[1] + 1)),
                          int(rng.integers(vr[0], vr[1] + 1)))
        cv2.circle(imagen, (x, y), r, color, -1, cv2.LINE_8)  # sin antialias: bordes limpios
        cv2.circle(imagen, (x - r // 3, y - r // 3), max(2, r // 5), (255, 255, 255), -1, cv2.LINE_8)
    guardar(CARPETA_RETOS / "reto_4.png", imagen)


def generar_reto_5():
    """Mapa del tesoro: 9 gemas verdes casi iguales, solo una es esmeralda. Y hay polvo de esmeralda por todos lados."""
    casilla = RESPUESTAS["reto_5"].upper()
    columnas, filas = len(RETO5_LETRAS), RETO5_FILAS
    assert len(casilla) == 2 and casilla[0] in RETO5_LETRAS and casilla[1] in "1234567", "reto_5: casilla tipo G5"
    ancho = RETO5_MARGEN * 2 + RETO5_CELDA * columnas
    alto = RETO5_MARGEN + RETO5_CELDA * filas + 20
    imagen = np.full((alto, ancho, 3), (150, 196, 222), np.uint8)
    ruido = rng.integers(-14, 15, (alto, ancho, 1))
    imagen = np.clip(imagen.astype(np.int16) + ruido, 0, 255).astype(np.uint8)
    tinta = (40, 60, 95)
    # Cuadrícula y etiquetas
    for i in range(columnas + 1):
        x = RETO5_MARGEN + i * RETO5_CELDA
        cv2.line(imagen, (x, RETO5_MARGEN), (x, RETO5_MARGEN + filas * RETO5_CELDA), tinta, 2)
    for j in range(filas + 1):
        y = RETO5_MARGEN + j * RETO5_CELDA
        cv2.line(imagen, (RETO5_MARGEN, y), (RETO5_MARGEN + columnas * RETO5_CELDA, y), tinta, 2)
    for i, letra in enumerate(RETO5_LETRAS):
        cv2.putText(imagen, letra, (RETO5_MARGEN + i * RETO5_CELDA + 36, 38), cv2.FONT_HERSHEY_DUPLEX, 1.0, tinta, 2, cv2.LINE_AA)
    for j in range(filas):
        cv2.putText(imagen, str(j + 1), (14, RETO5_MARGEN + j * RETO5_CELDA + 56), cv2.FONT_HERSHEY_DUPLEX, 1.0, tinta, 2, cv2.LINE_AA)
    # Muchas X falsas (en tinta roja, no estorban a la máscara verde)
    for _ in range(14):
        x, y = int(rng.integers(70, ancho - 70)), int(rng.integers(70, alto - 50))
        cv2.line(imagen, (x - 12, y - 12), (x + 12, y + 12), (40, 40, 170), 4, cv2.LINE_AA)
        cv2.line(imagen, (x - 12, y + 12), (x + 12, y - 12), (40, 40, 170), 4, cv2.LINE_AA)
    # Gemas: la verdadera + 8 impostoras que se ven casi igual
    # Cada una se sale del rango por poquito (H 57-63, S 200+, V 150+): a simple vista son iguales
    impostoras = [(54, 230, 200), (66, 230, 200), (60, 188, 200), (60, 230, 138),
                  (53, 225, 205), (67, 225, 195), (59, 185, 215), (62, 190, 160)]
    celdas_libres = [(c, f) for c in range(columnas) for f in range(filas)]
    verdadera = (RETO5_LETRAS.index(casilla[0]), int(casilla[1]) - 1)
    celdas_libres.remove(verdadera)
    orden = rng.permutation(len(celdas_libres))[:len(impostoras)]
    gemas = [(verdadera, RETO5_TESORO_HSV)] + [(celdas_libres[k], hsv) for k, hsv in zip(orden, impostoras)]
    for (c, f), hsv in gemas:
        cx = RETO5_MARGEN + c * RETO5_CELDA + RETO5_CELDA // 2 + int(rng.integers(-12, 13))
        cy = RETO5_MARGEN + f * RETO5_CELDA + RETO5_CELDA // 2 + int(rng.integers(-12, 13))
        r = 24
        rombo = np.array([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], np.int32)
        cv2.fillPoly(imagen, [rombo], hsv_a_bgr(*hsv), cv2.LINE_8)
    # Polvo de esmeralda: del MISMO color que el tesoro, pero diminuto
    polvo = hsv_a_bgr(*RETO5_TESORO_HSV)
    for _ in range(450):
        x, y = int(rng.integers(RETO5_MARGEN, ancho - RETO5_MARGEN)), int(rng.integers(RETO5_MARGEN, alto - 20))
        cv2.circle(imagen, (x, y), int(rng.integers(1, 3)), polvo, -1, cv2.LINE_8)
    guardar(CARPETA_RETOS / "reto_5.png", imagen)


def escribir_respuestas():
    texto = f"""# Hoja de respuestas del rally (solo staff)

Generada por `generar_material.py` con semilla `{SEMILLA}`.

| Reto | Nombre | Clave | Puntos |
|---|---|---|---|
| 1 | Detective de pixeles | **{RESPUESTAS['reto_1'].upper()}** | 100 |
| 2 | Mensaje en la oscuridad | **{RESPUESTAS['reto_2'].upper()}** | 100 |
| 3 | El canal secreto | **{RESPUESTAS['reto_3'].upper()}** | 200 |
| 4 | Caza de colores | **{RESPUESTAS['reto_4']}** pelotas rojas | 200 |
| 5 | Encuentra el tesoro | casilla **{RESPUESTAS['reto_5'].upper()}** | 300 |
| 6 | Jefe final (en vivo) | el staff mueve el objeto y cuenta 10 s: la mira nunca debe perderlo | 500 |

Bonus: +50 al primer equipo que resuelva cada reto. Clave incorrecta: -10.

## Respuestas equivocadas típicas (para dar pistas)

- Reto 1: `AZULAZUL...` = leyeron el canal azul (índice 0). `VERDEVERDE...` = canal verde. Letras raras con `?` = voltearon fila y columna.
- Reto 2: `NO ES AQUI` o `CASI...` = el umbral todavía está muy alto. Pantalla llena de puntos = umbral muy bajo. El umbral correcto está entre 27 y 39.
- Reto 3: `AQUI NO` / `TAMPOCO` = están viendo el canal azul o verde; OpenCV guarda B, G, R.
- Reto 4: un número mayor a {RESPUESTAS['reto_4']} casi siempre es porque contaron las guindas (V bajo) o las naranjas (H 12-15).
- Reto 5: si les salen cientos de círculos, les falta subir AREA_MINIMA (con 100 queda solo la esmeralda). La clave es la casilla donde cae el círculo.
"""
    ruta = BASE / "instructores" / "respuestas.md"
    ruta.write_text(texto, encoding="utf-8")
    print(f"  {ruta.relative_to(BASE)}")


if __name__ == "__main__":
    print("Generando imágenes de las lecciones...")
    generar_misterio()
    generar_manzana()
    generar_frutas()
    generar_robot()
    print("Generando retos del rally...")
    generar_reto_1()
    generar_reto_2()
    generar_reto_3()
    generar_reto_4()
    generar_reto_5()
    escribir_respuestas()
    print("Listo.")
