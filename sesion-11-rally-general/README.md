# Sesión 11 — Rally general 🏁

**50 minutos, 6 retos, un marcador en vivo.** Todo lo del curso en un solo rally: máquinas de estados, movimientos del dron, visión con OpenCV, control P, ArUcos y el rescate de Blu. Todo pasa en el **simulador**.

Ningún reto es nuevo de verdad: **la respuesta de cada uno está en el código de sus sesiones anteriores**. Cada archivo les dice dónde buscar (📚). Gana el equipo que mejor sepa encontrar, entender y adaptar lo que ya hizo.

## Antes de empezar

1. `git pull` y en VSCode abran la carpeta **`sesion-11-rally-general/rally`** (esa carpeta, no otra).
2. Si no lo tienen (es lo mismo de la Sesión 10):
   ```bash
   pip install opencv-contrib-python
   ```
3. Abran `equipo.py` y escriban:
   - `EQUIPO`: el nombre de su equipo, **igual en todas sus compus**.
   - `MARCADOR`: la dirección que aparece abajo en la pantalla del marcador.

## Cómo se juega

- Completen los **✏️** de un reto y córranlo con **▶**.
- Los retos con dron se califican **cuando el dron aterriza**: haz clic en la ventana y presiona `t` para despegar (`e` aterriza ya, `q` sale).
- Los retos 3 y 4 revisan sus funciones al correr el archivo: ✅ o ❌ en cada una.
- Si el reto quedó bien, **los puntos llegan solos al marcador**. Si no, el juez les dice en la terminal qué faltó.
- ¿Sin red? El programa imprime un **código de 4 letras**: enséñenselo al staff.

## Los retos

| # | Reto | Puntos | Qué hacen | 📚 Dónde lo vimos |
|---|---|---|---|---|
| 1 | `reto_1_despegue.py` | 100 | Despegar, subir a 150 cm, girar 4 s y aterrizar | Sesión 7: `01_semaforo.py`, `02_dron_con_teclas.py` |
| 2 | `reto_2_cuadrado.py` | 150 | Un cuadrado en el aire con `dron.mover(...)` | Sesiones 3 y 5 (`send_rc_control`), Sesión 6: `06_cuadrado_servoing.py` |
| 3 | `reto_3_ojos.py` | 150 | Máscara azul, encontrar a Blu y su centro | Sesión 4: `05_hsv_mascaras.py`, `06_contornos.py` · Sesión 10: `blu_funciones.py` |
| 4 | `reto_4_control.py` | 150 | Error, control P, distancia y "¿ya estoy a un metro?" | Sesión 6: `02_medir_el_error.py` · Sesión 5: `ejercicio_P.py` · Sesión 10 |
| 5 | `reto_5_zigzag.py` | 200 | Zigzag de ArUcos **y regresar a la base** | Sesión 10: `actividad_1_zigzag_arucos.py` · Sesión 7: `05_mision_rescate.py` |
| 6 | `reto_6_rescate_de_blu.py` | 300 | Jefe final: rescatar a Blu con **sus** ojos y **su** control, y festejar | Sesión 10: `actividad_2_rescate_de_blu.py` |

⚡ **El primer equipo en pasar cada reto gana 50 puntos extra.** Los puntos de un reto no se repiten: pasarlo dos veces cuenta una. El reto 6 usa sus funciones de los retos 3 y 4: pásenlos primero.

## Qué hay en la carpeta

```
sesion-11-rally-general/
├── rally/                      ← los equipos abren ESTA carpeta
│   ├── equipo.py               ✏️ nombre del equipo y dirección del marcador
│   ├── reto_1_despegue.py … reto_6_rescate_de_blu.py
│   ├── dron.py                 el mismo cuerpo del dron de la Sesión 10 (no se toca)
│   └── rally.py                el juez: califica y manda los puntos (no se toca)
└── marcador/                   ← solo la compu del staff
    ├── servidor_marcador.py    python servidor_marcador.py  →  http://localhost:8000
    └── marcador.html           la página que se proyecta (se actualiza sola)
```

## Para el staff: el marcador

```bash
cd sesion-11-rally-general/marcador
python servidor_marcador.py
```

Abran `http://localhost:8000` y proyéctenlo. La dirección que los equipos ponen en `equipo.py` aparece abajo en la pantalla. Todas las compus deben estar en el **mismo WiFi o hotspot**. Los controles (reloj, códigos manuales, quitar puntos) están en el ⚙️ y solo funcionan en la compu del servidor. No hay que instalar nada: es Python puro.
