# Sesión 2 — VSCode, GitHub, OpenCV y YOLO

Materiales de la Sesión 2 del taller de programación de SMALC.
Por el profesor: Gallo.

## Qué hay aquí

- `presentacion/` — la presentación interactiva de la sesión (HTML, se navega con las flechas del teclado, como un PPT).
- `demos-en-vivo/` — scripts de OpenCV y YOLO para las demostraciones en vivo durante la presentación.
- `tello/` — código base para la actividad de cierre (vuelo con dron Tello).
- `actividad-participantes/` — archivo donde cada participante practica su primer commit.

## Cómo abrir la presentación

Abre `presentacion/sesion2-taller.html` en cualquier navegador. Se navega con las flechas ← →.

## Cómo correr los demos en vivo

```bash
pip install opencv-python
python demos-en-vivo/demo_opencv.py
```

```bash
pip install ultralytics
python demos-en-vivo/demo_yolo.py
```

*(Corre `demo_yolo.py` una vez antes de la sesión para que el modelo se descargue con anticipación.)*

## Cómo correr el script del Tello

```bash
pip install djitellopy
python tello/tello_despegue_aterrizaje.py
```

Conecta tu computadora al WiFi del dron (`TELLO-XXXXX`) antes de ejecutarlo.

## Actividad de los participantes

Cada participante:
1. Clona este repositorio.
2. Agrega su nombre a `actividad-participantes/participantes.md`.
3. Hace su primer commit + push.
4. Hace 2-3 commits más y revisa su historial con `git log`.
