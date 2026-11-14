# Sesión 11 — Rally general · Guía del staff

> Esta carpeta solo vive en la rama `instructores`. Aquí están las soluciones y el probador automático.

## Antes de la clase (10 minutos)

1. `git pull` en la compu del staff y `pip install opencv-contrib-python` (si no está).
2. Revisa que todo funcione, sin abrir ventanas (~1.5 minutos):
   ```bash
   python sesion-11-rally-general/instructores/probar_rally.py
   ```
   Corre las soluciones de los 6 retos, revisa que los archivos sin completar **no** den puntos (y qué pista dan), y prueba el marcador (bono, repetidos, códigos manuales, reloj). Debe terminar en `32 de 32 revisiones bien`.
3. Conecta la compu del staff al WiFi o al hotspot que van a usar los alumnos y prende el marcador:
   ```bash
   cd sesion-11-rally-general/marcador
   python servidor_marcador.py
   ```
   Imprime la dirección (por ejemplo `MARCADOR = "http://192.168.1.10:8000"`). Abre `http://localhost:8000` y proyéctalo: la dirección también sale abajo en la pantalla.
4. **Prueba desde OTRA compu** (la de un alumno o la tuya): abre la dirección en su navegador. Si carga el marcador, la red está bien. Si no, ve a *Problemas comunes*.
5. Si quieres empezar de cero (borrar la prueba): ⚙️ → *Borrar todo el marcador*, o borra `marcador/marcador_datos.json`.

## Plan de los 50 minutos

| Minuto | Qué pasa |
|---|---|
| 0 – 5 | Reglas en la pantalla del marcador (tarjeta *Cómo se juega*). Cada equipo llena `equipo.py` y corre cualquier reto: al hacerlo aparecen en el marcador con 0 puntos (así sabes que su red funciona). |
| 5 – 45 | ⚙️ → **▶ Iniciar**. Rally. El staff camina entre equipos: **no da respuestas, pregunta "¿en qué sesión lo vimos?"**. |
| 45 – 50 | Se acaba el tiempo (el servidor ya no acepta retos). Premiación con el marcador proyectado. |

Tiempos del simulador cuando el código está bien: reto 1 ≈ 12 s, reto 2 ≈ 17 s, reto 5 ≈ 33 s, reto 6 ≈ 20 s. Los retos 3 y 4 son instantáneos.

## Puntos

| Reto | Puntos | Cuántas líneas escriben |
|---|---|---|
| 1 Despegue con estilo | 100 | 7 (tres transiciones, una con `dron.girar()`) |
| 2 El cuadrado | 150 | 9 (tres lados copiando la idea de ADELANTE) |
| 3 Los ojos | 150 | 7 (tres funciones) |
| 4 El control | 150 | 5 (cuatro funciones de 1 línea) |
| 5 Zigzag y de regreso | 200 | ~14 (las flechas del zigzag + el estado nuevo REGRESANDO) |
| 6 Jefe final | 300 | ~15 (el cerebro de la actividad 2 + el estado nuevo FESTEJANDO) |

- **⚡ +50** al primer equipo que pasa cada reto (sale dorado en la tabla y en el festejo).
- Un reto solo cuenta una vez por equipo, aunque lo pasen desde varias compus. El equipo se identifica por su nombre: mayúsculas, acentos y espacios no importan (`"Los Halcónes"` = `"los halcones"`).
- Empates: queda arriba el que llegó primero a esos puntos.
- Cuando el reloj llega a 0, el servidor ya no acepta retos (los códigos manuales del staff sí).

## Lo que el juez revisa (`rally/rally.py`)

| Reto | Cuenta cuando… | Si falla, el alumno ve por ejemplo… |
|---|---|---|
| 1 | Pasó por DESPEGANDO > SUBIENDO > GIRANDO > ATERRIZANDO, llegó a ~150 cm, estuvo ≥ 3.7 s en GIRANDO y giró de verdad | *Estuvo 2.0 s en GIRANDO y tienen que ser 4 s (usa s.segundos).* |
| 2 | Pasó por los 4 lados en orden, en cada uno avanzó ≥ 50 cm hacia el lado correcto y aterrizó a < 45 cm de donde despegó | *En ATRAS el dron se fue AL REVÉS (89 cm). Revisa el signo de la velocidad…* |
| 3 / 4 | Pasan todas las pruebas de funciones (las mismas de `blu_probar_funciones.py` de la Sesión 10) | *❌ 2) control_p — con un error enorme no debe pasar de VELOCIDAD_MAXIMA…* |
| 5 | Visitó los 3 ArUcos, pasó por REGRESANDO y aterrizó en la base (H) | *Falta el estado "REGRESANDO": después del último ArUco el dron vuelve a la base (H).* |
| 6 | Blu rescatado (3 s en RESCATANDO a ~1 m, lo mide el simulador), después FESTEJANDO ≥ 2.7 s girando, y aterrizó | *Después de rescatar a Blu falta "FESTEJANDO"…* |

Los retos con dron se califican **al aterrizar**. Si el alumno cierra con `q` antes, el juez le recuerda que aterrice.

## Soluciones

Están completas en `instructores/soluciones/`. Lo que se escribe en cada ✏️:

**Reto 1**
```python
# DESPEGANDO                  # SUBIENDO                    # GIRANDO
if s.en_el_aire:              if s.altura >= 150:           dron.girar()
    estado = "SUBIENDO"           estado = "GIRANDO"        if s.segundos >= 4:
                                                                estado = "ATERRIZANDO"
```

**Reto 2** — cada lado es igual a ADELANTE, cambiando la velocidad:
`dron.mover(derecha=20)` · `dron.mover(adelante=-20)` · `dron.mover(derecha=-20)` (también valen `dron.derecha()`, `dron.retroceder()`, `dron.izquierda()`), cada uno con `if s.segundos >= 3:` hacia el siguiente estado.

**Reto 3**
```python
hsv = cv2.cvtColor(foto, cv2.COLOR_BGR2HSV)          # mascara_azul
mascara = cv2.inRange(hsv, AZUL_BAJO, AZUL_ALTO)

if area < AREA_MINIMA:                               # encontrar_a_blu
    return None
return x, y, ancho, alto

centro_x = x + ancho // 2                            # centro_de
centro_y = y + alto // 2
```

**Reto 4**
```python
error_x = centro_x - ANCHO_FOTO // 2                 # calcular_error  (¡error_y al revés!)
error_y = ALTO_FOTO // 2 - centro_y
return limitar(kp * error, VELOCIDAD_MAXIMA)         # control_p
return ANCHO_DE_BLU_CM * FOCAL / ancho_en_pixeles    # distancia_a_blu
return abs(distancia - DISTANCIA_DE_RESCATE) < TOLERANCIA_DISTANCIA   # estoy_a_un_metro
```

**Reto 5** — igual que la actividad 1 de la Sesión 10, salvo dos cambios: al llegar al último ArUco va a `"REGRESANDO"` (no a `"ATERRIZANDO"`), y el estado nuevo:
```python
elif estado == "REGRESANDO":
    dron.regresar_a_base()
    if s.en_base:
        estado = "ATERRIZANDO"
```

**Reto 6** — el cerebro de la actividad 2 de la Sesión 10, salvo que RESCATANDO va a `"FESTEJANDO"`, y el estado nuevo:
```python
elif estado == "FESTEJANDO":
    dron.girar()
    if s.segundos >= SEGUNDOS_DE_FESTEJO:
        estado = "ATERRIZANDO"
```

## Durante el rally

- **Código manual**: si un equipo no tiene red, su programa imprime `equipo: … reto: … código: XXXX`. En el marcador: ⚙️ → *Código manual* → Anotar. El código solo sirve para ese equipo y ese reto.
- **Quitar puntos**: en la compu del staff haz clic en un ✓ o ⚡ de la tabla. **Borrar un equipo** (por ejemplo, repetido con otro nombre): clic en su nombre.
- **Reloj**: ▶ Iniciar · ⏸ Pausar · ↺ Reiniciar · cambiar los minutos (si lo cambias mientras corre, respeta lo que ya pasó).
- **🔇/🔊**: sonido al resolver un reto (el navegador pide un clic antes de sonar).
- Si cierras el servidor (o se apaga la compu), al volver a abrirlo todo sigue: se guarda en `marcador_datos.json`.
- Otras compus pueden abrir el marcador para verlo, pero sin el ⚙️: los controles solo funcionan desde la compu del servidor.
- Es un sistema de honor: un alumno que lea `rally.py` podría inventar sus códigos. Si algo se ve raro (un equipo con el reto 6 en el minuto 2), pregunta y quita los puntos.

## Problemas comunes

| Problema | Qué hacer |
|---|---|
| El alumno ve *No encuentro el marcador* | ¿Misma red WiFi/hotspot? ¿Copió bien la dirección (con `http://` y el `:8000`)? Pídele abrir esa dirección en su navegador: si no carga, es la red o el firewall. Mientras tanto puede seguir: le sale un código manual. |
| Desde otras compus no carga el marcador | Firewall de la compu del staff. **Windows**: acepta el aviso "Permitir acceso" de Python (redes privadas *y* públicas). **macOS**: Ajustes → Red → Firewall → permitir Python. **Linux**: `sudo ufw allow 8000/tcp`. Algunas redes escolares aíslan a los clientes: usa un hotspot. |
| El servidor no muestra la IP o muestra varias | La primera es la principal. Si ninguna funciona: Linux `hostname -I`, Mac `ipconfig getifaddr en0`, Windows `ipconfig` (Dirección IPv4). |
| *El puerto 8000 ya está ocupado* | `python servidor_marcador.py 8080` y usen `:8080` en `equipo.py`. |
| *Antes de empezar, escriban el nombre de su equipo* | Falta `EQUIPO = "..."` en `equipo.py`. |
| `ModuleNotFoundError: No module named 'rally'` o `'equipo'` | Abrieron otra carpeta o movieron el archivo: los retos tienen que estar en la misma carpeta que `rally.py`, `dron.py` y `equipo.py`. |
| `AttributeError: module 'cv2' has no attribute 'aruco'` | `pip uninstall opencv-python` y `pip install opencv-contrib-python`. |
| Reto 6: el dron gira y nunca ve a Blu | Sus retos 3 y 4 no están completos: córranlos primero. |
| Dos compus del mismo equipo salen como dos renglones | Escribieron el nombre distinto (`"Halcones"` vs `"Los Halcones"`). Que lo corrijan en `equipo.py`; el staff borra el renglón sobrante haciendo clic en su nombre (y anota con código manual lo que hubieran pasado ahí). |
