# Sesión 8 — Misión ArUco: atraviesa las gates

En esta sesión el Tello reconoce marcadores ArUco para encontrar una gate, alinearse con ella y atravesarla. Cada equipo completa una gate; como reto extra, navega una ruta de dos gates identificadas con IDs distintos.

**Duración sugerida: 2 horas.** La mayor parte del trabajo se hace con el Tello en tierra. Los vuelos son cortos, por turnos y supervisados por el staff.

## Qué aprenderás

- Un marcador ArUco tiene un patrón que la computadora reconoce y un ID que puede usar como nombre.
- La posición del marcador respecto al centro de la imagen ayuda a orientar el dron.
- El tamaño aparente del marcador sirve como una señal aproximada de cercanía.
- Una máquina de estados separa la misión en pasos: buscar, alinear, acercarse y cruzar.
- Si el dron pierde el marcador, debe dejar de avanzar.

## Preparación

Instala las dependencias en el entorno de Python que usarás para el taller:

```bash
pip install djitellopy opencv-contrib-python
```

`opencv-contrib-python` incluye `cv2.aruco`. Evita instalar a la vez `opencv-python` en el mismo entorno.

Genera e imprime los marcadores:

```bash
python herramientas/generar_marcadores.py
```

El programa guarda las imágenes en `marcadores/`. Imprime los marcadores sin cambiar su proporción. Coloca las hojas verticales, con buena iluminación y mirando hacia la cámara. Pon el marcador centrado horizontalmente sobre la abertura de su gate; el equipo debe mantener una altura de vuelo que permita atravesarla. Los IDs de la ruta inicial son `0`, `1` y `2`.

Conecta la computadora al WiFi del Tello antes de ejecutar las lecciones. Para que la detección funcione, el Tello debe estar encendido y conectado, pero no necesita despegar.

## Lección 1 — Ver los marcadores

Ejecuta `lecciones/01_ver_marcadores.py`.

1. Acerca y aleja el marcador de la cámara. Observa cómo cambia su tamaño en píxeles.
2. Mueve el marcador a izquierda y derecha. El punto amarillo indica su centro y la cruz blanca, el centro de la imagen.
3. Prueba los marcadores 0, 1 y 2. Comprueba que el ID que aparece en pantalla corresponde al impreso.
4. Presiona **q** para salir.

Esta lección solo muestra la cámara y los marcadores detectados. No despega ni envía controles de vuelo.

## Lección 2 — Proyecto final: explorador de gates

Ejecuta `lecciones/02_explorador_de_gates.py`. El programa muestra el plan de movimiento en pantalla, pero `MODO_VUELO` empieza en `False` y no manda órdenes al dron.

1. Revisen el orden de IDs en `RUTA_IDS`. El proyecto viene configurado para encontrar los marcadores 0, 1 y 2 en ese orden.
2. Presionen **t** para iniciar la misión de prueba. Muevan los marcadores frente a la cámara y observen los estados y controles propuestos.
3. Prueben qué ocurre al mostrar el ID incorrecto o al quitar el marcador de la imagen.
4. Ajusten `TOLERANCIA_CENTRADO`, `TAMANO_PARA_CRUZAR` y `SEGUNDOS_PARA_CRUZAR` para su montaje. El tamaño es una señal aproximada, no una distancia exacta.
5. Presionen **q** para salir.

Para volar, **solo el staff** debe preparar el área, revisar el programa y cambiar `MODO_VUELO` a `True`. El vuelo comienza al presionar **t**. La tecla **q** detiene los controles y aterriza. Si el marcador esperado no aparece durante varios segundos, la misión termina y el dron aterriza.

## Ruta de la sesión — 120 minutos

| Tiempo | Actividad | Resultado |
|---|---|---|
| 0–10 min | Presentar la misión y asignar roles: piloto de seguridad, programador, observador y registrador. | El equipo entiende la meta y las reglas del espacio de vuelo. |
| 10–25 min | Detectar los marcadores con la cámara. | Reconocen IDs, centro y tamaño aparente. |
| 25–40 min | Relacionar la imagen con los controles propuestos. | Identifican cuándo el dron debería girar o avanzar. |
| 40–60 min | Ejecutar la misión de prueba y ajustar la ruta. | Ven la máquina de estados y prueban pérdida o cambio de ID sin despegar. |
| 60–105 min | Vuelo supervisado por turnos; primero una gate y luego, si hay tiempo, dos. | Cada equipo intenta completar el reto. |
| 105–120 min | Demostraciones y reflexión. | Explican qué ID buscaron y qué hizo el programa al perderlo. |

## Reto y criterios de éxito

**Misión base:** localizar la gate con ID 0, centrarla en la imagen, acercarse hasta el umbral configurado y cruzarla lentamente.

**Reto extra:** completar la ruta de tres gates: ID 0, después ID 1 y finalmente ID 2.

El equipo completa la misión base si puede explicar y demostrar estas tres decisiones: qué marcador es el objetivo, qué significa estar centrado y qué condición permite cruzar. Si no ve el marcador esperado, el dron debe dejar de avanzar.

## Preparación y seguridad del vuelo

- Usa gates ligeras, estables y suficientemente amplias para el Tello; asegura las hojas para que no se muevan con el aire.
- Mantén despejada el área y a los participantes detrás de una línea de observación. Solo el staff manipula el dron y habilita el vuelo.
- Haz vuelos breves, a baja velocidad y a una altura fija que pase por el centro de la abertura.
- La cámara frontal no confirma por sí sola que el dron haya cruzado ni detecta todos los obstáculos. El cruce usa una orden por tiempo, así que requiere supervisión directa.
- Si hay pérdida de conexión, comportamiento inesperado o riesgo de colisión, el staff toma el control y termina la prueba.

## Archivos

- `lecciones/01_ver_marcadores.py`: vista de cámara y detección, sin vuelo.
- `lecciones/02_explorador_de_gates.py`: misión por estados, con vuelo desactivado por defecto.
- `lecciones/aruco_utils.py`: funciones compartidas para reconocer y medir marcadores.
- `herramientas/generar_marcadores.py`: crea imágenes imprimibles de los IDs 0, 1 y 2.
