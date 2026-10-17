# Sesión 6 — Visual servoing

En esta sesión el dron usa su cámara para encontrar un objeto y corregir su movimiento. El punto importante es el **centro de la imagen**: medimos qué tan lejos está el objeto de ese centro, y ese error alimenta al controlador P de la Sesión 5.

## Para participantes

1. Abre esta carpeta en VSCode.
2. Sigue las lecciones en orden. Las primeras actividades se pueden hacer sin un Tello.
3. En cada archivo, busca `✏️ COMPLETA` o `TODO`: esas son las partes que debes modificar.
4. En las ventanas de cámara presiona **q** para salir.
5. Para las dos últimas actividades instala `opencv-python` y `djitellopy`. Conecta la computadora al WiFi del Tello.

Las dos lecciones finales inician en modo de prueba, sin despegar. Para volar, el staff debe preparar un espacio despejado y cambiar `MODO_VUELO` a `True` después de revisar los límites y el equipo.

## Actividades paso a paso

### 1. Encontrar el centro — `lecciones/01_el_centro.py`

1. Lean el ancho y alto del frame que aparecen en el archivo.
2. Completen las dos coordenadas del centro usando la mitad del ancho y la mitad del alto.
3. Ejecuten el archivo y comparen el centro con las tres posiciones de objeto que imprime.
4. Identifiquen cuál posición ya está centrada y cuáles quedan a la izquierda, derecha, arriba o abajo.

### 2. Medir el error — `lecciones/02_medir_el_error.py`

1. Observen que el centro del frame ya está calculado y que el programa propone cuatro posiciones de objeto.
2. Para cada posición, calculen cuánto se separa el objeto del centro horizontal y verticalmente.
3. Completen `error_x` y `error_y` con esas restas.
4. Ejecuten el archivo y comprueben que el punto `(320, 240)` tiene error `(0, 0)`.
5. Expliquen qué significa el signo positivo o negativo de cada error según el objeto esté a un lado u otro del centro.

### 3. Detectar y centrar — `lecciones/03_detectar_y_centrar.py`

1. Pongan frente a la cámara uno o varios objetos **verdes**. El rango HSV inicial (`BAJO = (40, 70, 50)` y `ALTO = (85, 255, 255)`) busca tonos verdes; la iluminación y la cámara pueden cambiar qué tonos reconoce.
2. Ejecuten el archivo y miren las ventanas de cámara y máscara. En la máscara, las zonas blancas son las que pasan el filtro de color.
3. Si el objeto no aparece en blanco, ajusten el rango HSV o usen el calibrador de la Sesión 4.
4. Completen `centro_objeto` usando la esquina superior izquierda y la mitad del ancho y alto del rectángulo detectado.
5. Si aparecen varios objetos verdes, el programa elige el de mayor área. El rectángulo verde muestra cuál eligió. Muevan ese objeto y observen el punto rojo (centro del objeto), la cruz blanca (centro del frame) y la línea que los conecta. Presionen **q** para salir.

### 4. Probar el servo visual en pantalla — `lecciones/04_servo_visual_en_pantalla.py`

1. Coloquen frente a la cámara uno o varios objetos **verdes**; usa el mismo rango HSV inicial que la actividad 3.
2. Ejecuten el archivo y muevan el objeto alrededor del centro de la imagen.
3. Completen las salidas proporcionales en x e y usando la ganancia correspondiente y el error calculado.
4. Limiten cada salida al intervalo entre `-SALIDA_MAXIMA` y `SALIDA_MAXIMA`.
5. El programa elige el objeto verde de mayor área; el rectángulo verde señala cuál está siguiendo. Observen los errores y las salidas impresas sobre la imagen. La salida P no es necesariamente igual al error: se calcula multiplicando el error por `KP_X` o `KP_Y` y se limita a `SALIDA_MAXIMA`. Prueben distintas ganancias y comenten qué cambia cuando son mayores o menores.

### 5. Sigue el color con el Tello — `lecciones/05_sigue_el_color.py`

1. Empiecen en modo de prueba: `MODO_VUELO` está en `False`, por lo que el programa muestra la cámara y calcula errores sin despegar.
2. Conecten la computadora al WiFi del Tello y ejecuten el archivo. El color inicial también es **verde**; ajusten `BAJO` y `ALTO` si hace falta.
3. Si hay varios objetos verdes, el Tello usa el de mayor área. Completen las velocidades P limitadas por `VELOCIDAD_MAXIMA`. La salida se calcula como ganancia por error; el error horizontal corrige el giro y el vertical corrige la altura.
4. Muevan el objeto verde y observen si los signos de las correcciones corresponden a la dirección en que se encuentra.
5. Para volar, el staff prepara el área y cambia `MODO_VUELO` a `True`. Con el dron a una altura segura, el objeto se mueve para observar el seguimiento. Presionen **q** para detener; el programa pone los controles en cero y aterriza.

### 6. Recorre un cuadrado mientras sigue el color — `lecciones/06_cuadrado_servoing.py`

1. Empiecen en modo de prueba. La trayectoria dura cuatro lados de `SEGUNDOS_POR_LADO` segundos cada uno.
2. Observen que `movimiento_del_cuadrado` cambia entre avanzar, moverse a la derecha, retroceder y moverse a la izquierda.
3. Mientras el color se detecta, el programa combina esa trayectoria con las correcciones de giro y altura del servo visual.
4. Si el color se pierde, las velocidades de traslación y las correcciones se ponen en cero hasta volver a detectarlo.
5. Para volar, el staff debe revisar el espacio, reducir las velocidades si hace falta y cambiar `MODO_VUELO` a `True`. El cuadrado es una trayectoria por tiempo; la deriva del dron puede deformarlo.

## Ideas clave

- El centro del frame está en `(ancho / 2, alto / 2)`.
- El error en cada eje se calcula como `posición_del_objeto - centro_del_frame`.
- Si el error es cero, el objeto está centrado. Si no, el controlador calcula una corrección.
- La cámara no mide directamente una distancia: esta actividad usa la posición del objeto en la imagen para centrarlo.
- Las actividades 3, 4 y 5 buscan verde al inicio. En la 5 se pueden cambiar `BAJO` y `ALTO` para seguir otro color.

## Requisitos

Para las lecciones con cámara local:

```bash
pip install opencv-python
```

Para las lecciones con Tello:

```bash
pip install djitellopy
```

La cámara debe estar disponible como dispositivo `0`. Las dos últimas lecciones usan la cámara del Tello y necesitan `opencv-python` y `djitellopy` instalados. Si el color no se detecta bien, calibra los valores HSV con las herramientas de la Sesión 4.
