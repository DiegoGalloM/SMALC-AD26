# Sesión 4 — OpenCV desde cero + Rally de visión

Clase de 4 horas: primero aprendemos OpenCV desde cero con 7 mini-lecciones, y después competimos por equipos en un **rally de 6 retos**. Cada reto esconde una **clave** que solo se descubre programando.

## Para los participantes

1. En VSCode abre **esta carpeta** (`Archivo → Abrir carpeta → sesion-04-opencv-rally`).
2. Instala OpenCV (una sola vez):
   ```bash
   pip install opencv-python
   ```
3. Abre un archivo, busca el lápiz **✏️ COMPLETA ESTA FUNCIÓN** y complétala. La pista casi te da la respuesta.
4. Córrelo con el botón **▶** (arriba a la derecha). Aunque no hayas completado la función, el programa corre: así ves qué le falta.
5. En las ventanas con cámara, presiona **q** para salir.

### Lecciones (`lecciones/`)

| Archivo | Qué aprendes | Qué completas |
|---|---|---|
| `01_matriz.py` | Una imagen es una tabla de números | `leer_pixel` |
| `02_colores_canales.py` | Colores BGR, canales, recortar y pintar | `pintar` (¡lentes para el robot!) |
| `03_grises_threshold.py` | Grises y blanco y negro (threshold) | `blanco_y_negro` |
| `04_video_en_vivo.py` | Video = muchas fotos | `efecto` (espejo) |
| `05_hsv_mascaras.py` | Buscar un color con HSV | `buscar_color` |
| `06_contornos.py` | Contar objetos y encontrar su centro | `centro` |
| `07_dibujar.py` | Dibujar y que una mira siga a tu objeto | `dibujar_mira` |

### Rally (`rally/`)

| Reto | Puntos | Qué completas |
|---|---|---|
| 1 · Detective de pixeles | 100 | `leer_rojo` |
| 2 · Mensaje en la oscuridad | 100 | `blanco_y_negro` + encontrar el UMBRAL |
| 3 · El canal secreto | 200 | `canal_rojo` |
| 4 · Caza de colores | 200 | calibrar el rojo + `contar` |
| 5 · Encuentra el tesoro | 300 | `es_grande` |
| 6 · Jefe final (en vivo) | 500 | `dibujar_mira` + `donde_esta` |

Bonus: **+50** al primer equipo en resolver cada reto. Clave equivocada: **−10**.

### Herramientas (`herramientas/`, ya hechas: solo úsalas)

- `prueba_camara.py`: revisa que tu cámara funcione.
- `inspector_pixeles.py`: haz clic en una imagen y te dice fila, columna, BGR y HSV.
- `calibrador_hsv.py`: mueve barras hasta que solo tu objeto quede en blanco y te da `BAJO` y `ALTO`.

Las dos últimas te preguntan qué imagen usar: escribe solo el nombre (`frutas`, `robot`, `reto_4`...) o presiona Enter para usar la cámara.

## Para el staff

- **Presentación:** abre `presentacion/taller-opencv.html` en el navegador y navega con las flechas ← → (o con el clicker).
- **Demo de apertura:** `demo/demo_gancho.py` (teclas 1–8 cambian el efecto).
- **Marcador del rally:** abre `marcador.html` en el proyector (tecla **P** = modo proyector).
- **Guía completa, claves y soluciones:** en la rama `instructores`.
