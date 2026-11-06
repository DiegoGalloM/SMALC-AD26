# Sesión 8 — ¡Todo junto! Recap + Task 1: la gate azul

En esta sesión juntamos todo lo del curso. Primero un recap de las Sesiones 1 a 7; después, el reto: que el dron **despegue, encuentre la gate azul, se centre y la atraviese**. Es la Task 1 de la arena "Rescaten a Blue".

La diferencia con la Sesión 7: ahí el cuerpo del dron (`dron.py`) era una caja cerrada. **Hoy la abrimos**: ustedes programan los ojos, el control, los músculos y el cerebro.

## El reto (`reto_gate/`)

1. En VSCode abre la carpeta `sesion-08-integracion/reto_gate` (si no la tienes, `git pull`).
2. Instala lo necesario (una sola vez):
   ```bash
   pip install opencv-python djitellopy
   ```
3. Completa cada pieza (busca **✏️**) y pruébala con su paso. Cada paso te dice ✅ o ❌:

| Paso | Completas | Lo pruebas con | Qué junta |
|---|---|---|---|
| 1 · Los ojos | `vision.py`: `mascara_azul`, `encontrar_gate`, `centro_de` | `paso1_vision.py` | Sesiones 4 y 6 |
| 2 · El control P | `control.py`: `error_horizontal`, `error_vertical`, `control_p` | `paso2_control.py` | Sesiones 5 y 6 |
| 3 · Los músculos | `movimientos.py`: `girar`, `avanzar`, `corregir` | `paso3_movimientos.py` | Sesiones 3 y 5 |
| 4 · El cerebro | `mision.py`: las flechas de la máquina de estados | `mision.py` | Sesión 7 |

4. Corre `mision.py`, **haz clic en la ventana** y presiona **t**. Si el dron pasa por el hueco: **¡CRUZASTE LA GATE!**

### La máquina de estados

```
EN_TIERRA ─t─► BUSCANDO ─ve la gate─► CENTRANDO ─centrada─► ACERCANDOSE ─cerca─► CRUZANDO ─pasan 4 s─► ATERRIZANDO
                  ▲                       │                       │
                  └───── la pierde ───────┴───────────────────────┘
```

### Archivos que ya vienen hechos (no se tocan)

- `simulador.py`: un Tello de mentiras con una gate azul. Se usa igual que el Tello real (`takeoff`, `send_rc_control`, `land`...).
- `conexion.py`: conecta el dron (simulador o real), lee la cámara y dibuja la pantalla.

### Del simulador al Tello (con el staff)

1. Calibra el azul de la gate real con `herramientas/calibrador_hsv.py` de la Sesión 4 y escríbelo en `AZUL_BAJO` / `AZUL_ALTO` de `vision.py`.
2. En `mision.py` cambia `MODO = "simulador"` por `MODO = "tello"`.
3. Ajusta `ANCHO_PARA_CRUZAR` (cuándo ya está cerca) y `SEGUNDOS_CRUZANDO` (cuánto avanza para pasar).

**Teclas:** `t` despega · `e` aterriza en cualquier momento · `q` aterriza y termina.

## Para el staff

- **Presentación:** abre `presentacion/integracion.html` en el navegador (← → o clicker). Incluye el recap con preguntas que se revelan con un clic, una demo interactiva de cómo ve el dron la gate y la guía del reto.
- **Guía, tiempos y soluciones:** en la rama `instructores`.
