"""
Demo en vivo de deteccion de objetos con un modelo YOLO ya entrenado.
No requiere entrenar nada: usa un modelo pre-entrenado sobre objetos comunes
y lo apunta a la camara en vivo.

Importante: corre este script una vez ANTES de la sesion para que el modelo
se descargue con anticipacion (la primera vez tarda un poco por la descarga).
"""

from ultralytics import YOLO

model = YOLO("yolo26n.pt")
model.predict(source=0, show=True)
