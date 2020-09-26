from lib.arm import *
import math
import time

grip_open()
jDepart = (497, 426, 738, 55, 500)
movej(jDepart, 2000)

pA = get_position(True)

movel(appro(pA, (30, 0, 5)), 1000)
grip_close(850)

pAppr = appro(pA, (30, 0, 25))
movel(pAppr, 1000)

movel(appro(pA, (30, 0, 5)), 1000)

grip_open()

time.sleep(2)

movej((500, 500, 500, 500, 500), 2000)
power_off()
