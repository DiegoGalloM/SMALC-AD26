# Guía del staff — Sesión 7: El cerebro del dron (máquinas de estados)

> Esta carpeta vive **solo en la rama `instructores`** (en `master` está en `.gitignore`).

## La idea de la clase

Los participantes **solo escriben la lógica de estados**: las flechas (`if condición: estado = "..."`). Todo lo demás —visión (Sesión 4), control P (Sesiones 5 y 6), simulador y Tello— está en `lecciones/dron.py`, que es igual en los 4 modos (`simulador`, `camara`, `tello_sin_volar`, `tello`). Así el mismo cerebro que prueban en el simulador vuela después en el Tello.

## Checklist antes de la clase

- [ ] En cada laptop: `pip install opencv-python djitellopy` con el **mismo** Python que usa VSCode.
- [ ] Correr `lecciones/02_dron_con_teclas.py` en cada laptop: debe abrir la ventana del simulador (si sale `The function is not implemented`, ver "Problemas comunes").
- [ ] Un Tello por equipo, **baterías cargadas** (y de repuesto).
- [ ] Objetos o tarjetas de colores vivos: **verde** (para seguir), **rojo** y **azul** (para el dron obediente). Cartulina tamaño carta funciona bien.
- [ ] Zona de vuelo despejada y marcada; un instructor por dron volando.
- [ ] Proyectar `presentacion/maquinas-de-estados.html`.

## Guion (4 horas)

| Hora | Diapositivas | Qué pasa |
|---|---|---|
| 0:00 – 0:30 | 1 – 8 | Repaso, gancho (semáforo, Mario, elevador), qué es un estado, transiciones (semáforo animado), "mismo evento, distinto estado", del dibujo al código |
| 0:30 – 0:45 | 9 | Lección 1: semáforo |
| 0:45 – 1:05 | 10 – 12 | Juego "sé la máquina" (en el proyector, que el grupo diga qué pasa antes de presionar) + Lección 2 |
| 1:05 – 1:25 | 13 – 14 | Lección 3: batería y prioridades |
| 1:25 – 1:40 | 15 – 16 | Lección 4: ojos con estados (webcam + objeto verde) |
| 1:40 – 2:00 | 17 – 18 | Lección 5: misión de rescate en el simulador |
| 2:00 – 2:15 | 19 | Receso. Formar equipos, repartir Tellos y tarjetas |
| 2:15 – 3:30 | 20 – 25 | Misión final: elegir, diseñar en papel (tabla de la diapositiva 24), programar, probar en simulador → `tello_sin_volar` → volar |
| 3:30 – 4:00 | 26 – 27 | Demos por equipo (~3 min c/u) y cierre |

## Cómo correr cada cosa

- **Lecciones:** abrir la carpeta `lecciones/` en VSCode y darle ▶. Las teclas solo funcionan si la **ventana del dron tiene el foco** (hacer clic en ella). `q` = salir.
- **Presentación:** abrir el HTML en el navegador; ← → o clicker. Con `#10` al final de la dirección abre directo la diapositiva 10. Los diagramas se animan solos; en la 10 los botones se presionan con el mouse.
- **Misiones de ejemplo** (`instructores/ejemplos_mision/`): cópialas a `lecciones/` (ahí está `dron.py`) y córrelas. Sirven para una demo del staff o para destrabar a un equipo.
- **Probar que todo funciona** (sin ventanas, con cámara y Tello falsos):
  ```bash
  python instructores/probar_soluciones.py
  ```
  Debe terminar en `TODO BIEN`.

## Soluciones

Solo cambian las flechas; las acciones ya venían escritas.

**01_semaforo.py**
```python
    elif estado == "AMARILLO":
        if segundos > 2:
            estado = "ROJO"
            inicio = time.time()

    elif estado == "ROJO":
        if segundos > 4:
            estado = "VERDE"
            inicio = time.time()
```
Mini-retos: peatones → en VERDE `if tecla == ord("p"): estado = "AMARILLO"; inicio = time.time()`. Modo noche → en cada color `if tecla == ord("n"): estado = "NOCHE"` y en NOCHE `if tecla == ord("n"): estado = "ROJO"`. Si olvidan `inicio = time.time()`, el reloj sigue contando y los estados se saltan de inmediato.

**02_dron_con_teclas.py**
```python
    elif estado == "DESPEGANDO":
        dron.despegar()
        if s.en_el_aire:
            estado = "VOLANDO"

    elif estado == "VOLANDO":
        dron.quieto()
        if s.tecla == "l":
            estado = "ATERRIZANDO"

    elif estado == "ATERRIZANDO":
        dron.aterrizar()
        if not s.en_el_aire:
            estado = "EN_TIERRA"
```
Mini-retos: GIRANDO → en VOLANDO `if s.tecla == "g": estado = "GIRANDO"` y el bloque `GIRANDO` con `dron.girar()` y `if s.segundos > 3: estado = "VOLANDO"`. EMERGENCIA → `if s.tecla == "e": estado = "EMERGENCIA"` en DESPEGANDO, VOLANDO y GIRANDO; bloque `EMERGENCIA` con `dron.aterrizar()` y `if not s.en_el_aire: estado = "EN_TIERRA"`.

**03_bateria.py**
```python
    elif estado == "PATRULLANDO":
        dron.patrullar()
        if s.bateria < 30:
            estado = "REGRESANDO"

    elif estado == "REGRESANDO":
        dron.regresar_a_base()
        if s.en_base:
            estado = "ATERRIZANDO"
```
Con 30 regresa y aterriza (aparece **MISIÓN CUMPLIDA**). Con 10 se le acaba la batería en el camino ("SIN BATERIA: aterrizaje forzoso"): de ahí la idea de margen. Mini-reto 2: en REGRESANDO `if s.bateria < 8: estado = "ATERRIZANDO"`. Mini-reto 3: la batería **sí** se gasta esperando en el aire.

**04_ojos_con_estados.py**
```python
    if estado == "BUSCANDO":
        dron.girar()
        if s.veo_color:
            estado = "SIGUIENDO"

    elif estado == "SIGUIENDO":
        dron.seguir_color()
        if not s.veo_color:
            estado = "PERDIDO"
        if s.centrado:
            estado = "CENTRADO"

    elif estado == "CENTRADO":
        dron.quieto()
        if not s.centrado:
            estado = "SIGUIENDO"

    elif estado == "PERDIDO":
        dron.quieto()
        if s.veo_color:
            estado = "SIGUIENDO"
        if s.segundos > 2:
            estado = "BUSCANDO"
```
Mini-reto 2 (MUY_CERCA): en SIGUIENDO y CENTRADO `if s.cerca: estado = "MUY_CERCA"`; bloque con `dron.retroceder()` y `if not s.cerca: estado = "SIGUIENDO"`.

**05_mision_rescate.py**
```python
    elif estado == "DESPEGANDO":
        dron.despegar()
        if s.en_el_aire:
            estado = "BUSCANDO"

    elif estado == "BUSCANDO":
        dron.girar()
        if s.veo_color:
            estado = "ACERCANDOSE"

    elif estado == "ACERCANDOSE":
        dron.acercarse()
        if not s.veo_color:
            estado = "BUSCANDO"
        elif s.cerca:
            estado = "RESCATANDO"

    elif estado == "RESCATANDO":
        dron.rescatar()
        if not s.cerca:
            if s.faltan > 0:
                estado = "BUSCANDO"
            else:
                estado = "REGRESANDO"

    elif estado == "REGRESANDO":
        dron.regresar_a_base()
        if s.en_base:
            estado = "ATERRIZANDO"
```
Rescata a las 3 en ~30 s y aterriza en la base (**MISIÓN CUMPLIDA**). Con `bateria=40` rescata a 2 y la revisión de seguridad lo trae de vuelta. Si la revisión de seguridad estuviera hasta abajo, un estado podría cambiar después de ella y el dron seguiría la misión aunque no tenga batería.

Errores típicos: olvidar el `elif` entre "lo pierde" y "cerca" (funciona igual, pero conviene); escribir mal un nombre de estado (`"ACERCANDOSE"` vs `"ACERCÁNDOSE"`): el dron se queda "flotando" porque ningún bloque coincide. El panel muestra el estado tal como lo escribieron: es la mejor pista.

## Misión final

**Ejemplos completos** en `ejemplos_mision/`:

| Archivo | Misión | Funciona con |
|---|---|---|
| `rescate.py` | Busca, se acerca, rescata y aterriza | simulador, Tello + objeto verde |
| `obediente.py` | Tarjetas: verde = avanza 2 s, azul = gira 2 s, rojo = aterriza | Tello + tarjetas |
| `guardaespaldas.py` | Sigue el color; si lo pierde lo busca; si en 10 s no aparece, aterriza; si se acerca demasiado, retrocede | Tello + objeto verde |
| `bailarin.py` | Coreografía por tiempo (no usa la cámara) | simulador y Tello: la más segura para el primer vuelo |

**Protocolo de vuelo por equipo:**
1. La misión funciona en `"simulador"`.
2. Con `"tello_sin_volar"`, alguien sostiene el Tello y mueve la tarjeta/objeto: el panel debe pasar por los estados esperados.
3. Con `"tello"`, en la zona de vuelo y con un instructor: `t` despega (en la plantilla), `e` aterriza, `q` aterriza y termina.

**Lo que `dron.py` hace solo en el Tello real (no se puede quitar desde el código de los alumnos):** aterriza con batería < 15% (y ya no deja despegar), aterriza a los 120 s de vuelo, aterriza al presionar `q`, al cerrar la ventana o si el programa truena. Velocidades limitadas (20 de 100). Estos valores están en la sección `AJUSTES` al inicio de `dron.py`.

**Ajustes útiles en `dron.py`** (si un equipo lo necesita):
- `AREA_CERCA`: qué tan grande se ve el objeto para decir que está "cerca" (depende del tamaño de la tarjeta).
- `TOLERANCIA_CENTRADO`, `KP_GIRO`, `KP_ALTURA`: los del servo visual de la Sesión 6.
- `COLORES`: rangos HSV (calibrar con las herramientas de la Sesión 4 si la luz del salón es difícil).

**Demo (≈3 min por equipo):** misión en una frase · diagrama y explicar UNA flecha · vuelo (el grupo dice en voz alta el estado) · qué falló y cómo lo arreglaron. No es competencia: reconozcan ideas originales, buenos planes B y buen manejo de la seguridad.

## Problemas comunes

- **`cv2.error: The function is not implemented. Rebuild the library with Windows, GTK+ 2.x or Cocoa support`**: hay un OpenCV "sin ventanas" (`opencv-python-headless`) encima del normal. Arreglo: `python -m pip install --force-reinstall --no-deps opencv-python`.
- **`ModuleNotFoundError: No module named 'djitellopy'`**: solo hace falta para los modos Tello: `python -m pip install djitellopy`.
- **Las teclas no hacen nada**: hagan clic en la ventana del dron (las teclas van a la ventana, no a la terminal).
- **El dron no ve el color en el Tello**: la luz cambia todo. Acerquen la tarjeta, eviten fondos del mismo color o ajusten `COLORES` en `dron.py`. Ojo: `djitellopy` entrega la imagen en RGB; `dron.py` ya la convierte a BGR (en los scripts de la Sesión 6 no, por eso allá el rojo y el azul salen invertidos).
- **"regresar_a_base() solo funciona en el simulador"**: el Tello no sabe dónde está la base (no tiene GPS). En vuelo real, la misión debe terminar en `ATERRIZANDO`.
- **La misión se queda atorada en un estado**: casi siempre es un estado sin flecha de salida o un nombre mal escrito. Revisen el historial de estados en el panel.
