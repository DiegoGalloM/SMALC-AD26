# Hoja de respuestas del rally (solo staff)

Generada por `generar_material.py` con semilla `2026`.

| Reto | Nombre | Clave | Puntos |
|---|---|---|---|
| 1 | Detective de pixeles | **VISION** | 100 |
| 2 | Mensaje en la oscuridad | **RESCATE** | 100 |
| 3 | El canal secreto | **TOMATE** | 200 |
| 4 | Caza de colores | **23** pelotas rojas | 200 |
| 5 | Encuentra el tesoro | casilla **G5** | 300 |
| 6 | Jefe final (en vivo) | el staff mueve el objeto y cuenta 10 s: la mira nunca debe perderlo | 500 |

Bonus: +50 al primer equipo que resuelva cada reto. Clave incorrecta: -10.

## Respuestas equivocadas típicas (para dar pistas)

- Reto 1: `AZULAZUL...` = leyeron el canal azul (índice 0). `VERDEVERDE...` = canal verde. Letras raras con `?` = voltearon fila y columna.
- Reto 2: `NO ES AQUI` o `CASI...` = el umbral todavía está muy alto. Pantalla llena de puntos = umbral muy bajo. El umbral correcto está entre 27 y 39.
- Reto 3: `AQUI NO` / `TAMPOCO` = están viendo el canal azul o verde; OpenCV guarda B, G, R.
- Reto 4: un número mayor a 23 casi siempre es porque contaron las guindas (V bajo) o las naranjas (H 12-15).
- Reto 5: si les salen cientos de círculos, les falta subir AREA_MINIMA (con 100 queda solo la esmeralda). La clave es la casilla donde cae el círculo.
