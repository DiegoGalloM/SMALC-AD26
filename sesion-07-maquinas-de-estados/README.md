# Sesión 7 — El cerebro del dron: máquinas de estados

Hasta ahora el dron sabe **volar** (Sesión 3), **ver colores** (Sesión 4), **corregirse solo** (Sesión 5) y **centrar lo que ve** (Sesión 6). Hoy le damos un **cerebro**: una máquina de estados que decide qué hacer y cuándo cambiar de plan.

- Primeras ~2 horas: conceptos y 5 lecciones (sin riesgo: simulador y webcam).
- Últimas ~2 horas: cada equipo diseña su propia misión, la vuela en el Tello y la presenta en una demo.

## Para los participantes

1. En VSCode abre la carpeta `sesion-07-maquinas-de-estados/lecciones`.
2. Instala lo necesario (una sola vez):
   ```bash
   pip install opencv-python djitellopy
   ```
3. En cada archivo, busca **✏️ COMPLETA**: solo escribes las **flechas** (`if ...: estado = "..."`). Lo que hace el dron en cada estado ya viene escrito.
4. Córrelo con **▶**. Para usar las teclas, **haz clic en la ventana** del dron primero. **q** = salir.

### Lecciones

| Archivo | Qué aprendes | Modo |
|---|---|---|
| `01_semaforo.py` | Estados y transiciones por tiempo | ventana propia |
| `02_dron_con_teclas.py` | Transiciones por teclas: el mismo botón hace cosas distintas según el estado | simulador |
| `03_bateria.py` | Transiciones por sensores y el "margen" de seguridad | simulador |
| `04_ojos_con_estados.py` | Estados + visión: BUSCANDO, SIGUIENDO, CENTRADO, PERDIDO | webcam |
| `05_mision_rescate.py` | Todo junto: una misión de rescate completa y la seguridad primero | simulador |
| `06_mi_mision.py` | **Misión final**: la máquina de estados de tu equipo | simulador → Tello |

### `dron.py`: el cuerpo del dron

Tu archivo es el **cerebro**; `dron.py` es el **cuerpo** (no necesitas modificarlo). Funciona igual en 4 modos:

| Modo | Qué hace |
|---|---|
| `"simulador"` | Un dron en la pantalla: mapa, cámara simulada y panel con el estado |
| `"camara"` | Tu webcam hace de ojos del dron; no se mueve nada, solo muestra la orden que mandaría |
| `"tello_sin_volar"` | El Tello real prende su cámara y sensores, pero **no despega** (pruébalo en la mano) |
| `"tello"` | Vuela de verdad. **Solo con el staff** |

**Acciones** (una por estado): `dron.quieto()`, `dron.despegar()`, `dron.aterrizar()`, `dron.avanzar()`, `dron.retroceder()`, `dron.izquierda()`, `dron.derecha()`, `dron.subir()`, `dron.bajar()`, `dron.girar()`, `dron.seguir_color()`, `dron.acercarse()`, `dron.rescatar()`, `dron.patrullar()`, `dron.regresar_a_base()` (solo simulador).

**Sensores** (`s = dron.sensores(estado)`): `s.tecla`, `s.segundos` (en el estado actual), `s.en_el_aire`, `s.altura`, `s.bateria`, `s.veo_color`, `s.error_x`, `s.centrado`, `s.cerca`, `s.veo_rojo`, `s.veo_verde`, `s.veo_azul`, `s.en_base`, `s.faltan`.

### Misión final

1. Elijan una misión: rescate, dron obediente (tarjetas de colores), guardaespaldas, explorador, dron bailarín... o la suya.
2. Dibújenla en papel: bolitas (estados) y flechas (cuándo cambia).
3. Escríbanla en `06_mi_mision.py` y pruébenla en este orden: `"simulador"` → `"tello_sin_volar"` → `"tello"` (con el staff).
4. Demo: expliquen su diagrama y vuelen su misión.

**Seguridad de vuelo:** tecla **e** = aterriza · **q** = aterriza y termina. Con menos de 15% de batería o después de 2 minutos en el aire, el dron aterriza solo.

## Para el staff

- **Presentación:** abre `presentacion/maquinas-de-estados.html` en el navegador y navega con ← → (o con el clicker). Tiene diagramas animados y un juego interactivo ("juega a ser la máquina").
- **Guía completa, tiempos y soluciones:** en la rama `instructores`.
