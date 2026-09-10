"""
Demo en vivo de deteccion de objetos con un modelo YOLO ya entrenado.
No requiere entrenar nada: usa un modelo pre-entrenado sobre objetos comunes
y lo apunta a la camara en vivo.

"""

from ultralytics import YOLO

model = YOLO("yolo26n.pt")
model.predict(source=0, show=True)
