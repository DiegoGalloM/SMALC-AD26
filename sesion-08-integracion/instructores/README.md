# Guía del staff — Sesión 8: Recap + Task 1 (la gate azul)

> Esta carpeta vive **solo en la rama `instructores`** (en `master` está en `.gitignore`).

## La idea

En la Sesión 7 los participantes solo escribían las flechas de la máquina de estados (`dron.py` hacía todo lo demás). Hoy **abren la caja**: completan cada módulo con huecos de 1 línea, del mismo nivel que los retos anteriores, y luego los unen en `mision.py`:

| Módulo | Qué completan | Sesiones |
|---|---|---|
| `vision.py` | máscara azul, rectángulo de la gate, centro | 4 y 6 |
| `control.py` | `error_x`, `error_y`, control P limitado | 5 y 6 |
| `movimientos.py` | `girar`, `avanzar`, `corregir` con `send_rc_control` | 3 y 5 |
| `mision.py` | 6 flechas de la máquina de estados | 7 |

Usan la **API real del Tello** (`takeoff`, `send_rc_control`, `land`). `simulador.py` imita esa API, así que el mismo código vuela cambiando `MODO = "tello"`.

## Checklist antes de la clase

- [ ] **La gate:** marco cuadrado hueco y azul, colgado. En el simulador mide 80 cm por fuera, 60 cm por dentro y tiene el centro a 100 cm del piso. Si la real es distinta, cambien las constantes al inicio de `reto_gate/simulador.py` (`GATE_LADO_EXTERIOR`, `GATE_LADO_INTERIOR`, `GATE_ALTURA_CENTRO`).
- [ ] Calibrar el azul de la gate con la luz del salón (`sesion-04-opencv-rally/herramientas/calibrador_hsv.py`) y anotar `AZUL_BAJO` / `AZUL_ALTO` para dárselos a los equipos.
- [ ] En cada laptop: `pip install opencv-python djitellopy` y correr `reto_gate/paso3_movimientos.py` (debe abrir el simulador cuando pasen los ✅; antes de completar solo marca ❌, y eso también confirma que corre).
- [ ] Tellos con baterías cargadas, zona de vuelo despejada frente a la gate.
- [ ] Para las demos del recap (diapositiva 12), tener a mano las soluciones de la Sesión 6 (`04_servo_visual_en_pantalla.py`) y la Sesión 7 (`05_mision_rescate.py`).

## Guion (4 horas)

| Hora | Diapositivas | Qué pasa |
|---|---|---|
| 0:00 – 0:10 | 1 – 4 | Agenda, la arena (las 3 tasks) y "cada sesión les dio una pieza" |
| 0:10 – 0:50 | 5 – 11 | Quiz "¿te acuerdas?": lean la pregunta, dejen que el grupo conteste en voz alta, clic para revelar |
| 0:50 – 1:00 | 12 | Demos en vivo: `demo_gancho.py` (S4), servo visual (S6), misión de rescate (S7) |
| 1:00 – 1:30 | 13 | Terminar la misión de la Sesión 7 (las soluciones están en `sesion-07-maquinas-de-estados/instructores/`) |
| 1:30 – 2:15 | 14 | Break |
| 2:15 – 2:35 | 15 – 19 | La gate, la demo interactiva (diapositiva 17), el plan y los módulos |
| 2:35 – 3:15 | 20 – 23 | Pasos 1 a 4 en el simulador |
| 3:15 – 3:55 | 24 – 25 | Vuelo real por equipos con el staff |
| 3:55 – 4:00 | 26 – 27 | Retos extra y cierre |

**Tip para la demo interactiva (diapositiva 17):** muevan "distancia" de 400 a 60 y pregunten qué estado toca. Al final la gate "ya no cabe" y aparece CRUZANDO (a ciegas): es la razón de `ANCHO_PARA_CRUZAR`.

## Soluciones

**vision.py**
```python
def mascara_azul(foto):
    hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, AZUL_BAJO, AZUL_ALTO)

def encontrar_gate(mascara):
    ...
    gate = max(candidatos, key=cv2.contourArea)
    return cv2.boundingRect(gate)

def centro_de(gate):
    x, y, ancho, alto = gate
    return x + ancho // 2, y + alto // 2
```

**control.py**
```python
def error_horizontal(centro_x, ancho_foto):
    return centro_x - ancho_foto // 2

def error_vertical(centro_y, alto_foto):
    return alto_foto // 2 - centro_y

def control_p(error, kp):
    return limitar(kp * error, VELOCIDAD_MAXIMA)
```

**movimientos.py**
```python
def girar(tello):
    tello.send_rc_control(0, 0, 0, VELOCIDAD_GIRO)

def avanzar(tello):
    tello.send_rc_control(0, VELOCIDAD_AVANCE, 0, 0)

def corregir(tello, giro, subir, adelante):
    tello.send_rc_control(0, adelante, subir, giro)
```

**mision.py**
```python
    elif estado == "BUSCANDO":
        movimientos.girar(tello)
        if veo_gate:
            estado = "CENTRANDO"

    elif estado == "CENTRANDO":
        movimientos.corregir(tello, giro, subir, 0)
        if not veo_gate:
            estado = "BUSCANDO"
        elif centrada:
            estado = "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        movimientos.corregir(tello, giro, subir, movimientos.VELOCIDAD_AVANCE)
        if not veo_gate:
            estado = "BUSCANDO"
        elif cerca:
            estado = "CRUZANDO"

    elif estado == "CRUZANDO":
        movimientos.avanzar(tello)
        if segundos > SEGUNDOS_CRUZANDO:
            estado = "ATERRIZANDO"
```
Con todo completo, en el simulador el dron cruza a ~3 cm del centro del hueco (el margen es ±22 cm).

**Errores típicos (y qué se ve):**
- `paso1` dice ❌ y la máscara está negra → no cambiaron los `(0, 0, 0)` de `mascara_azul`.
- El punto rojo queda en la esquina de la gate → falta `centro_de`.
- `paso2`: giro de 30 en vez de 25 → olvidaron `limitar`.
- `paso3`: `corregir` manda los números en otro orden → recordar "lado, adelante, arriba, giro".
- La misión gira sin parar → falta la flecha de BUSCANDO. Se queda centrando y no avanza → falta la de CENTRANDO (o `TOLERANCIA` muy chica en la vida real).
- Choca con el marco → casi siempre es que no estaba centrado al pasar a CRUZANDO, o que `ANCHO_PARA_CRUZAR` es tan grande que la gate ya no cabía en la cámara.

**Retos extra (respuestas):** PERDIDA → desde CENTRANDO/ACERCANDOSE `if not veo_gate: estado = "PERDIDA"`, y en PERDIDA `movimientos.detener(tello)`, `if veo_gate: estado = "CENTRANDO"`, `elif segundos > 1: estado = "BUSCANDO"`. Ida y vuelta → después de CRUZANDO, `DANDO_VUELTA` con `girar()` unos 4 s y regresar a BUSCANDO. Gate chica → en `encontrar_gate` elegir el candidato de menor área (o comparar anchos).

## Calibración para el vuelo real

1. **Azul:** con el calibrador de la Sesión 4 frente a la gate real, con la luz del salón.
2. **`ANCHO_PARA_CRUZAR`** (en `mision.py`): sostengan el Tello con `MODO = "tello"` sin despegar, frente a la gate a ~1 m, y vean "ancho gate" en la pantalla. Ese número (o un poco menos) es el bueno. Tiene que ser una distancia en la que **la gate todavía se ve completa**: si se acerca más, solo se ven los postes y el dron se desvía.
3. **`SEGUNDOS_CRUZANDO`:** suficiente para pasar desde esa distancia (empiecen con 4 y ajusten). Si se queda corto, aterriza dentro del marco; si es mucho, avanza de más.
4. Si el dron pasa siempre muy alto o muy bajo, revisen que la gate esté a la altura de vuelo (~1 m) o súbanla/bájenla.
5. `VELOCIDAD_MAXIMA` (25) y las velocidades de `movimientos.py` ya son bajas; no las suban en la primera prueba.

**Seguridad en vuelo:** `e` aterriza en cualquier estado, `q` aterriza y termina, y si el programa truena `conexion.py` intenta aterrizar. Un instructor junto a cada dron.

## Probar que todo funciona

```bash
python instructores/probar_soluciones.py
```
Copia `reto_gate/` a una carpeta temporal y corre todo sin ventanas: sin completar (debe correr y mostrar sus pistas), con las soluciones (pasos ✅ y misión que cruza la gate) y contra un Tello falso. Debe terminar en `TODO BIEN`.
