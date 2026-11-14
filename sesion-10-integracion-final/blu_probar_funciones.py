# ============================================================
#  blu_probar_funciones.py — ¿ya funcionan tus funciones?
# ============================================================
#  Este archivo NO lo modificas: solo córrelo con ▶ cada vez que completes una función.
#  Te dice ✅ o ❌ en cada una. No necesita dron.

import cv2
import numpy as np

import blu_funciones as f
from dron import foto_de_blu

GRIS = (90, 90, 90)
AZUL = (220, 100, 30)  # en BGR


def foto_con_manchas(*manchas):
    """Una foto gris con rectángulos azules en (x, y, ancho, alto)."""
    foto = np.full((480, 640, 3), GRIS, np.uint8)
    for x, y, ancho, alto in manchas:
        cv2.rectangle(foto, (x, y), (x + ancho - 1, y + alto - 1), AZUL, -1)
    return foto


def mascara_con_manchas(*manchas):
    mascara = np.zeros((480, 640), np.uint8)
    for x, y, ancho, alto in manchas:
        cv2.rectangle(mascara, (x, y), (x + ancho - 1, y + alto - 1), 255, -1)
    return mascara


def casi(a, b, margen=2):
    return a is not None and abs(a - b) <= margen


# ---------------- Las pruebas: cada una regresa "" si todo bien, o qué salió mal ----------------
def prueba_mascara_azul():
    mascara = f.mascara_azul(foto_con_manchas((200, 150, 120, 160)))
    if mascara is None:
        return "regresa None: todavía no calcula la máscara"
    if not isinstance(mascara, np.ndarray) or mascara.shape != (480, 640):
        return "la máscara debe ser una imagen en blanco y negro del mismo tamaño que la foto"
    if mascara[230, 260] == 0:
        return "donde hay azul la máscara salió NEGRA (¿convertiste a HSV? ¿usaste AZUL_BAJO y AZUL_ALTO?)"
    if mascara[50, 50] != 0:
        return "donde NO hay azul la máscara salió BLANCA"
    return ""


def prueba_encontrar_a_blu():
    grande, ruido = (200, 150, 120, 160), (500, 60, 12, 12)
    caja = f.encontrar_a_blu(mascara_con_manchas(grande, ruido))
    if caja is None:
        return "hay una mancha grande en la máscara y regresó None"
    if len(caja) == 5:
        return "regresó 5 números: quita el área, solo regresa x, y, ancho, alto"
    if len(caja) != 4 or not all(casi(a, b) for a, b in zip(caja, grande)):
        return f"regresó {tuple(caja)} y la mancha más grande está en {grande}"
    if f.encontrar_a_blu(mascara_con_manchas(ruido)) is not None:
        return "una manchita de ruido (más chica que AREA_MINIMA) no es Blu: debe regresar None"
    if f.encontrar_a_blu(mascara_con_manchas()) is not None:
        return "con la máscara toda negra debe regresar None"
    return ""


def prueba_centro_de():
    centro = tuple(f.centro_de((100, 50, 80, 60)))
    if centro != (140, 80):
        return f"el centro de la caja (x=100, y=50, ancho=80, alto=60) es (140, 80) y regresó {centro}"
    return ""


def prueba_calcular_error():
    if tuple(f.calcular_error(320, 240)) != (0, 0):
        return f"con Blu justo en el centro (320, 240) los errores deben ser (0, 0) y salió {tuple(f.calcular_error(320, 240))}"
    error_x, error_y = f.calcular_error(420, 140)  # a la derecha y arriba
    if error_x != 100:
        return f"Blu está 100 pixeles a la DERECHA del centro: error_x debe ser 100 y salió {error_x}"
    if error_y != 100:
        return f"Blu está 100 pixeles ARRIBA del centro: error_y debe ser +100 y salió {error_y}"
    return ""


def prueba_control_p():
    if not casi(f.control_p(100, 0.1), 10, 0.01):
        return f"control_p(100, 0.1) debe dar 10 y dio {f.control_p(100, 0.1)}"
    if not casi(f.control_p(-50, 0.2), -10, 0.01):
        return f"control_p(-50, 0.2) debe dar -10 y dio {f.control_p(-50, 0.2)}"
    if not casi(f.control_p(5000, 0.1), f.VELOCIDAD_MAXIMA, 0.01):
        return f"con un error enorme no debe pasar de VELOCIDAD_MAXIMA ({f.VELOCIDAD_MAXIMA}) y dio {f.control_p(5000, 0.1)}"
    if not casi(f.control_p(-5000, 0.1), -f.VELOCIDAD_MAXIMA, 0.01):
        return f"con un error enorme negativo no debe bajar de -{f.VELOCIDAD_MAXIMA} y dio {f.control_p(-5000, 0.1)}"
    return ""


def prueba_distancia_a_blu():
    pixeles_a_un_metro = f.ANCHO_DE_BLU_CM * f.FOCAL / 100
    for metros in (1, 2, 4):
        pixeles = pixeles_a_un_metro / metros
        distancia = f.distancia_a_blu(pixeles)
        if not casi(distancia, 100 * metros, 1):
            return f"si Blu se ve de {pixeles:.0f} pixeles de ancho está a {100 * metros} cm, y regresó {distancia}"
    return ""


def prueba_estoy_a_un_metro():
    meta, tolerancia = f.DISTANCIA_DE_RESCATE, f.TOLERANCIA_DISTANCIA
    if f.estoy_a_un_metro(meta) is not True:
        return f"a {meta} cm exactos debe regresar True"
    if f.estoy_a_un_metro(meta - tolerancia + 5) is not True or f.estoy_a_un_metro(meta + tolerancia - 5) is not True:
        return "si está dentro de la tolerancia (un poquito más cerca o más lejos) también es True"
    if f.estoy_a_un_metro(meta + tolerancia + 20) is not False:
        return f"a {meta + tolerancia + 20} cm está muy LEJOS: debe regresar False"
    if f.estoy_a_un_metro(meta - tolerancia - 20) is not False:
        return f"a {meta - tolerancia - 20} cm está muy CERCA: debe regresar False (¿usaste abs?)"
    return ""


PRUEBAS = [("1) mascara_azul", prueba_mascara_azul), ("2) encontrar_a_blu", prueba_encontrar_a_blu),
           ("3) centro_de", prueba_centro_de), ("4) calcular_error", prueba_calcular_error),
           ("5) control_p", prueba_control_p), ("6) distancia_a_blu", prueba_distancia_a_blu),
           ("7) estoy_a_un_metro", prueba_estoy_a_un_metro)]

print()
buenas = []
for nombre, prueba in PRUEBAS:
    try:
        problema = prueba()
    except Exception as error:  # la función tronó: también cuenta como ❌
        problema = f"tronó con este error: {type(error).__name__}: {error}"
    buenas.append(problema == "")
    print(f"{'✅' if not problema else '❌'}  {nombre}" + (f"\n      {problema}" if problema else ""))

print(f"\nLlevas {sum(buenas)} de {len(PRUEBAS)}.")
if all(buenas):
    print("🎉 ¡Todas funcionan! Ahora completa EL CEREBRO en actividad_2_rescate_de_blu.py")

# Si los ojos ya funcionan, mira cómo ven a Blu tus funciones
if all(buenas[:3]):
    foto, _ = foto_de_blu(distancia_cm=150, a_la_derecha_cm=25, arriba_cm=10)
    caja = f.encontrar_a_blu(f.mascara_azul(foto))
    if caja is not None:
        x, y, ancho, alto = caja
        cv2.rectangle(foto, (x, y), (x + ancho, y + alto), (0, 255, 0), 3)
        cv2.circle(foto, tuple(int(n) for n in f.centro_de(caja)), 7, (0, 0, 255), -1)
        if buenas[5]:
            texto = f"Blu a {f.distancia_a_blu(ancho):.0f} cm (la verdad: 150 cm)"
            cv2.putText(foto, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    print("\nAsí ven a Blu tus funciones. Presiona una tecla en la ventana para cerrar.")
    cv2.imshow("Asi ven a Blu tus funciones (presiona una tecla)", foto)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
