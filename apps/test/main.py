from lib.arm import *

set_speed(1)

start_point = (130, -50, 0)
dest_point = (130, 50, 0)

grip_open()
movel(appro(start_point, (0, 0, 40)), 2000, hand_orientation_down=True)

kapla = 4
for i in range(kapla):
    # Move to next Kapla
    kapla_pos = appro(start_point, (0, 0, (kapla - i) * 8))
    kapla_lift = appro(kapla_pos, (0, 0, 10))

    movel(kapla_lift, 1000, hand_orientation_down=True)
    movel(kapla_pos, 1000, hand_orientation_down=True)

    grip_close()

    # Lifting to prevent colliding with other Kapla.
    movel(kapla_lift, 1000, hand_orientation_down=True)

    dest = appro(dest_point, (0, 0, i * 8))
    dest_lift = appro(dest, (0, 0, 10))

    movel(dest_lift, 1000, hand_orientation_down=True)
    movel(dest, 1000, hand_orientation_down=True)

    grip_open()

    # Lifting to prevent colliding with other Kapla.
    movel(dest_lift, 1000, hand_orientation_down=True)

movej((500, 500, 500, 500, 500), 2000)
power_off()
