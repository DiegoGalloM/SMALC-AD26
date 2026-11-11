# Sesión 10 — Integración final

Dos actividades para cerrar el curso. Las dos usan el mismo `dron.py`: **el cuerpo del dron ya está hecho, tu programa es el cerebro**.

```python
from dron import Dron

dron = Dron("simulador", objetivo="aruco")
estado = "EN_TIERRA"

while dron.sigue():
    s = dron.sensores(estado, aruco=0)   # lo que el dron SABE
    if estado == "EN_TIERRA":
        dron.quieto()                    # lo que el dron HACE
        if s.tecla == "t":               # cuándo CAMBIA de estado
            estado = "DESPEGANDO"
```

## Antes de empezar

1. En VSCode abre la carpeta `sesion-10-integracion-final` (si no la tienes, `git pull`).
2. Instala lo necesario (una sola vez):
   ```bash
   pip install opencv-contrib-python djitellopy
   ```

**Teclas (en las dos actividades):** haz clic en la ventana · `t` despega · `e` aterriza ya · `q` aterriza y termina.

## Actividad 1 — Zigzag de ArUcos (`actividad_1_zigzag_arucos.py`)

El programa **ya funciona**. El reto es entenderlo: tienen **10 minutos** para leerlo en equipo y después explicarnos su lógica. Al final del archivo hay preguntas guía sobre máquinas de estados, ArUcos, visión y control.

```
EN_TIERRA ─t─► DESPEGANDO ─► SUBIENDO ─► BUSCANDO ─ve el ArUco─► CENTRANDO ─centrado─► ACERCANDOSE
                                            ▲                        │                      │
                                            ├───── lo pierde ────────┴──────────────────────┤
                                            └──── faltan ArUcos (paso + 1) ─────────────────┤
                                                                      ATERRIZANDO ◄─ último ┘
```

Córranlo en el simulador mientras lo leen: el estado, los sensores y la orden que se manda al dron se ven en la pantalla.

## Para el staff

### Pasar del simulador al Tello

En la primera línea de cada actividad cambia `"simulador"` por:

| Modo | Qué hace |
|---|---|
| `"camara"` | La webcam hace de ojos. Nada se mueve: en pantalla se ve la orden que se mandaría. |
| `"tello_sin_volar"` | Cámara y sensores del Tello real, sin despegar. **Úsalo para revisar el montaje.** |
| `"tello"` | Vuelo real. |

### Montaje del zigzag

- Marcadores `DICT_4X4_50` con IDs 0, 1 y 2 (se generan con `sesion-08-arucos-gates/herramientas/generar_marcadores.py`).
- **Mide el lado del cuadro negro del marcador impreso** y escríbelo en `ARUCO_LADO_CM` de `dron.py`. De ese número sale `s.distancia`.
- `LADOS` (en la actividad) dice hacia dónde gira el dron para buscar cada ArUco. Ajústalo a como hayan quedado los marcadores.
- `DISTANCIA_DE_LLEGADA` es qué tan cerca llega a cada marcador antes de buscar el siguiente.

### Qué cambió contra la Lección 2 de la Sesión 8

El vuelo anterior era lento y tardaba en reconocer. Lo que se cambió, todo en los `AJUSTES` de `dron.py`:

| Antes | Ahora |
|---|---|
| Avance fijo de 10 | Proporcional a la distancia: de 12 a 30 (`ARUCO_AVANCE_*`) |
| Había que estar centrado ±35 px (en 960) durante 5 frames | Tolerancia de ±45 / ±60 px (en 640), sin esperar frames |
| Al acercarse, si se descentraba regresaba a alinear | `acercarse()` corrige giro y altura mientras avanza |
| Un frame sin detección = volver a buscar girando | Recuerda el marcador 0.4 s (`ARUCO_MEMORIA`) |
| Siempre buscaba girando a la derecha | Gira hacia el lado de `LADOS`, o hacia donde lo vio por última vez |
| Pausa de 0.05 s en cada vuelta | Sin pausas |
| Subía 2 s a ciegas | Sube hasta `ALTURA_DE_VUELO` (o 3 s, lo que pase primero) |
| Giro de búsqueda a 20 | A 35 (`VELOCIDAD_BUSQUEDA`) |

Las ganancias del control P (`ARUCO_KP_GIRO`, `ARUCO_KP_ALTURA`) parten de las que ya habían ajustado en la Sesión 8. Si el dron oscila, bájalas; si la imagen sale muy movida al buscar, baja `VELOCIDAD_BUSQUEDA`.

> Estos valores están probados en el simulador, no en un Tello real: hagan un vuelo de prueba antes de la sesión.
