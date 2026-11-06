
from djitellopy import Tello
import time
import logging


ALTURA_QUE_QUIERO_LLEGAR = 150
KP = 0.67
error = 1


Tello.LOGGER.setLevel(logging.DEBUG)


tello = Tello()
tello.connect()

tello.takeoff()
time.sleep(1)


while (error > 0.2):
    altura = tello.get_distance_tof()

    error = ALTURA_QUE_QUIERO_LLEGAR - int(altura)

    output = KP * error

    tello.send_rc_control(0,0,int(output),0)

    time.sleep(0.1)

tello.send_rc_control(0,0,0,0)
tello.land()

















