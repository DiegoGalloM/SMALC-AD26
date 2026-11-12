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

## Actividad 2 — ¡Rescaten a Blu! (`actividad_2_rescate_de_blu.py`)

Blu está atrapado arriba de una pila de cajas. El dron tiene que **despegar, buscarlo, reconocerlo, acercarse, quedarse 3 segundos a un metro de él y aterrizar**. Aquí el programa **no** está terminado: los ojos, el control y el cerebro los completan ustedes.

```
EN_TIERRA ─t─► DESPEGANDO ─► BUSCANDO ─ve a Blu─► RECONOCIENDO ─1 s viéndolo─► ACERCANDOSE
                                ▲                      │                           │
                                └────── lo pierde ─────┴───────────────────────────┤
                                ATERRIZANDO ◄── pasan 3 s ── RESCATANDO ◄─ a 1 m ──┘
```

Son 8 piezas (busca **✏️**). Cada una trae una pista de la lógica, no la respuesta:

| # | Completas | Archivo | Qué junta |
|---|---|---|---|
| 1 | `mascara_azul` | `blu_funciones.py` | Sesión 4: HSV y máscaras |
| 2 | `encontrar_a_blu` | `blu_funciones.py` | Sesión 4: manchas y ruido (`mancha_mas_grande` ya está hecha) |
| 3 | `centro_de` | `blu_funciones.py` | Sesión 6: el centro |
| 4 | `calcular_error` | `blu_funciones.py` | Sesión 6: el error |
| 5 | `control_p` | `blu_funciones.py` | Sesión 5: control P |
| 6 | `distancia_a_blu` | `blu_funciones.py` | Sesión 8: tamaño y distancia |
| 7 | `estoy_a_un_metro` | `blu_funciones.py` | Tolerancias |
| 8 | El cerebro: las flechas de la máquina de estados | `actividad_2_rescate_de_blu.py` | Sesión 7 |

**Cómo trabajar:**

1. Completa una función en `blu_funciones.py`.
2. Corre `blu_probar_funciones.py`: te dice ✅ o ❌ en cada una y qué salió mal. No necesita dron.
3. Cuando tengas las 7 en ✅, completa el cerebro y corre `actividad_2_rescate_de_blu.py`.

En el simulador Blu aparece en un lugar distinto cada vez. El círculo del mapa marca la zona de rescate (1 m) y la barra **rescate** se llena mientras el dron esté ahí en el estado `RESCATANDO`. Si se llena: **¡BLU RESCATADO!**

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

### Montaje de Blu

- Calibra el azul de la imagen real con `sesion-04-opencv-rally/herramientas/calibrador_hsv.py` y escríbelo en `AZUL_BAJO` / `AZUL_ALTO` de `blu_funciones.py`.
- **Mide el ancho de la parte azul de Blu** en la imagen impresa y escríbelo en `ANCHO_DE_BLU_CM`. Si la distancia en pantalla no coincide con la real, ajusta ese número (o `FOCAL`).
- Que no haya otras cosas azules a la vista: el dron persigue la mancha azul más grande.
- En el Tello real no hay forma de medir la distancia verdadera: la barra de rescate se llena mientras el estado sea `RESCATANDO` y las funciones sigan viendo a Blu.
- Las soluciones están en `instructores/` (esa carpeta no se sube a `master`, igual que en las otras sesiones).

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
