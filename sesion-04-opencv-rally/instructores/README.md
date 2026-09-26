# Guía del staff — Sesión 4: OpenCV desde cero + Rally de visión

> Esta carpeta vive **solo en la rama `instructores`**. En `master` (lo que clonan los participantes) no existe y está en `.gitignore`.
> Ojo: si el repositorio es público, cualquiera puede ver esta rama en GitHub. Si quieren que las respuestas sean secretas de verdad, no suban esta rama y compártanla por otro lado.

## Checklist antes de la clase

- [ ] En cada laptop y en la del proyector: `python -m pip install opencv-python` (con el **mismo** Python que usa VSCode; ver "Problemas comunes").
- [ ] Correr `herramientas/prueba_camara.py` en cada laptop.
- [ ] Probar `demo/demo_gancho.py` en la laptop del proyector.
- [ ] Abrir `presentacion/taller-opencv.html` y `marcador.html` en el navegador del proyector.
- [ ] Tener a mano `instructores/respuestas.md` (claves del rally).
- [ ] Objetos de colores vivos para el reto 6 (una pelota roja, azul o verde por equipo, o una que mueva el staff).

## Cómo correr cada cosa

Todo se corre desde VSCode con la carpeta `sesion-04-opencv-rally` abierta (`Archivo → Abrir carpeta`), con el botón **▶**. En las ventanas con cámara se sale con **q**.

| Qué | Cómo | Notas |
|---|---|---|
| Presentación | Abrir `presentacion/taller-opencv.html` en el navegador | Flechas ← → o clicker. F11 = pantalla completa. `#12` al final de la dirección abre la diapositiva 12. Las barras de las demos se mueven con el mouse. |
| Demo de apertura | `demo/demo_gancho.py` | Teclas 1–8: normal, grises, threshold, bordes, caricatura, térmica, pixelado, rastreador (rojo). |
| Marcador | Abrir `marcador.html` en el navegador | Agrega equipos, clic en la casilla del reto = resuelto (otro clic lo quita), botón −10 = clave equivocada. **P** = modo proyector. Se guarda solo en ese navegador: usen la misma computadora todo el rally. |
| Lecciones | `lecciones/01_matriz.py` … `07_dibujar.py` | Cada una tiene UNA función marcada con ✏️. Sin completarla, igual corre. |
| Retos | `rally/reto_1_…py` … `reto_6_…py` | Mismo estilo. La clave sale en la terminal o en la ventana. |
| Inspector de pixeles | `herramientas/inspector_pixeles.py` | Pregunta el nombre de la imagen (`frutas`, `robot`, `reto_4`...). Clic = fila, columna, BGR y HSV. |
| Calibrador HSV | `herramientas/calibrador_hsv.py` | Pregunta la imagen (Enter = cámara). Al salir con q imprime `BAJO` y `ALTO` para copiar. |

## Guion sugerido (4 horas)

| Hora | Diapositivas | Qué pasa |
|---|---|---|
| 0:00 – 0:15 | 1 – 4 | Portada, agenda, demo en vivo (`demo_gancho.py`), la misión del dron |
| 0:15 – 2:00 | 5 – 21 | 7 lecciones de ~15 min: explicar con la diapositiva, luego cada quien completa su archivo |
| 2:00 – 2:15 | 22 | Receso. Formar equipos y cargarlos en el marcador |
| 2:15 – 3:40 | 23 – 31 | Reglas, un vistazo a cada reto y ¡arranca el cronómetro del marcador (85 min)! |
| 3:40 – 4:00 | 32 | Premiación y cierre (commit de su trabajo) |

## Cómo validar cada reto

Las claves de esta edición están en **`respuestas.md`** (se regenera con las claves que elijas). Antes de dar los puntos pueden pedir ver el código corriendo.

| Reto | Qué revisar |
|---|---|
| 1 | La terminal dice `🔑 Mensaje secreto: <CLAVE>`. |
| 2 | Que te enseñen la ventana **en blanco y negro** con la clave (la clave se alcanza a adivinar a simple vista con mucho brillo). |
| 3 | La ventana "canal rojo" muestra la clave. |
| 4 | La terminal dice `🔑 Pelotas encontradas: <número>` y en la máscara solo están las rojas. |
| 5 | Queda **un solo** círculo rojo en el mapa; la clave es su casilla. |
| 6 | Mueve el objeto 10 segundos frente a su cámara: la mira nunca lo pierde y el texto dice bien IZQUIERDA / CENTRO / DERECHA. |

## Soluciones

Cada bloque es la función ya completa. Los alumnos solo tocan esa función (y a veces un número de arriba).

### Lecciones

**01_matriz.py**
```python
def leer_pixel(imagen, fila, columna):
    return imagen[fila, columna]
```
Mini-reto: limón (fila 330, columna 330) ≈ `[48 157 61]` · mora (fila 470, columna 330) ≈ `[148 61 35]` · fondo ≈ `[201 223 237]`. La imagen misteriosa es la cara del robot de SMALC.

**02_colores_canales.py**
```python
def pintar(imagen, fila1, fila2, columna1, columna2, color):
    imagen[fila1:fila2, columna1:columna2] = color
    return imagen
```
Mini-reto (lentes): los ojos van de la fila 170 a la 225 y de la columna 230 a la 410 → `pintar(robot, 160, 235, 220, 420, (0, 0, 0))`.

**03_grises_threshold.py**
```python
def blanco_y_negro(gris, umbral):
    _, resultado = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
    return resultado
```
Mini-retos: un `UMBRAL` entre ~130 y ~170 deja la manzana completa sin la sombra. Con `cv2.THRESH_BINARY_INV` la manzana sale blanca. El hoyito es el brillo de la manzana.

**04_video_en_vivo.py**
```python
def efecto(foto):
    return cv2.flip(foto, 1)
```

**05_hsv_mascaras.py**
```python
def buscar_color(imagen, bajo, alto):
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, bajo, alto)
```

**06_contornos.py**
```python
def centro(x, y, ancho, alto):
    cx = x + ancho // 2
    cy = y + alto // 2
    return cx, cy
```
Mini-retos: con `AREA_MINIMA = 0` salen 8 objetos rojos (3 manzanas + 5 migajas); con `100` quedan 3. Hay 8 moras azules.

**07_dibujar.py**
```python
def dibujar_mira(foto, x, y, radio):
    cv2.circle(foto, (x, y), radio, (0, 255, 0), 3)
    cv2.circle(foto, (x, y), 5, (0, 0, 255), -1)
    cv2.putText(foto, "OBJETIVO", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
```

### Rally

**Reto 1 — Detective de pixeles**
```python
def leer_rojo(imagen, fila, columna):
    pixel = imagen[fila, columna]
    return pixel[2]
```
Si les sale `AZULAZUL...` leyeron `pixel[0]`; `VERDEVERDE...` es `pixel[1]`.

**Reto 2 — Mensaje en la oscuridad**
```python
def blanco_y_negro(gris, umbral):
    _, resultado = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
    return resultado
```
Y además `UMBRAL` entre **27 y 39**. Con umbral más alto salen los mensajes trampa ("NO ES AQUI", "CASI..."); más bajo, puro ruido.

**Reto 3 — El canal secreto**
```python
def canal_rojo(imagen):
    canal1, canal2, canal3 = cv2.split(imagen)
    return canal3
```
`canal1` dice "AQUI NO" (azul) y `canal2` dice "TAMPOCO" (verde).

**Reto 4 — Caza de colores**
```python
def contar(mascara):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contornos)
```
Y además un rango que deje solo las rojas brillantes, por ejemplo `BAJO = (0, 150, 150)`, `ALTO = (8, 255, 255)`. Si les salen de más, contaron guindas (V bajo) o naranjas (H 12–15).

**Reto 5 — Encuentra el tesoro**
```python
def es_grande(contorno):
    area = cv2.contourArea(contorno)
    return area > 100
```
Cualquier número entre ~20 y ~1000 funciona.

**Reto 6 — Jefe final**
```python
def dibujar_mira(foto, x, y, radio):
    cv2.circle(foto, (x, y), radio, (0, 255, 0), 3)
    cv2.circle(foto, (x, y), 5, (0, 0, 255), -1)
    cv2.putText(foto, "OBJETIVO", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


def donde_esta(x):
    if x < 213:
        return "IZQUIERDA"
    elif x < 426:
        return "CENTRO"
    else:
        return "DERECHA"
```
Y además `BAJO` / `ALTO` calibrados con su objeto real y la luz del salón.

## Cambiar las claves para otra edición

1. Edita `RESPUESTAS` (y si quieres `SEMILLA`) en `instructores/generar_material.py`.
2. Regenera las imágenes y la hoja de respuestas:
   ```bash
   python instructores/generar_material.py
   ```
3. Comprueba que todo sigue funcionando:
   ```bash
   python instructores/probar_soluciones.py
   ```
   Corre todas las lecciones, retos y herramientas sin abrir ventanas (con cámara falsa), sin completar y con las soluciones, y confirma que cada reto da su clave. Debe terminar en `TODO BIEN`.
4. Las imágenes nuevas (`lecciones/imagenes/` y `rally/imagenes/`) van a `master`; `respuestas.md` se queda en esta rama.

## Problemas comunes

- **`ModuleNotFoundError: No module named 'cv2'`**: VSCode está usando un Python donde no se instaló OpenCV. Abajo a la derecha (o `Ctrl+Shift+P → Python: Select Interpreter`) elige el Python donde lo instalaste, o instálalo en ese mismo con `python -m pip install opencv-python`.
- **`error: externally-managed-environment`** al instalar (Python del sistema en Linux o instalado con `uv`): crea un entorno virtual y elígelo en VSCode:
  ```bash
  python3 -m venv .venv
  .venv/bin/python -m pip install opencv-python
  ```
  (En Windows: `.venv\Scripts\python -m pip install opencv-python`).
- **La cámara no abre**: ciérrala en Zoom/Meet/Teams; cambia `cv2.VideoCapture(0)` por `1`; en Mac/Windows da permiso de cámara a VSCode o a la Terminal.
- **La ventana no se cierra con la X**: en las ventanas con cámara hay que salir con **q**.
- **Las ventanas salen encimadas**: arrástralas; es normal.
- **"No encuentra la imagen"**: no muevan los archivos de carpeta; cada archivo busca su carpeta `imagenes` junto a él.
- **Acentos en pantalla**: `cv2.putText` no sabe escribir acentos ni ñ.

## Mantener esta rama al día

Cuando cambie algo en `master`:
```bash
git checkout instructores
git merge master
```
