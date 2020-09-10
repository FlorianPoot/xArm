from lib.servo_controller import *
from lib.cartesian import compute_ik, compute_fk


speed = 1


def set_speed(value: float) -> None:

    global speed

    if 0 < value <= 10:
        speed = value
    else:
        raise ValueError("speed must be greater than 0 and less or equal to 10")


def grip_open() -> None:
    move_servo(1, 200, int(1000 / speed))


def grip_close(value=None) -> None:

    if value is not None:

        if not 0 <= value <= 1000:
            raise ValueError("value must be between 0 and 1000")

        value = int((value - 0) * (650 - 200) / (1000 - 0) + 200)

        move_servo(1, value, int(1000 / speed))
    else:
        move_servo(1, 650, int(1000 / speed))


def precompute_moves() -> None:

    """Parse all application and if saved compute data is not present or different, pre-compute each moves (inverse kinematics)"""

    pass


def movej(joint: tuple, time: int) -> None:

    """Move each servomotors to joint position within time.

        joint: tuple(j1, j2, j3, j4, j5) | jx: 0-1000
        time: 0-65535 milliseconds

    """

    move_servos((2, 3, 4, 5, 6), joint[::-1], int(time / speed))


def movel(point: tuple, time: int, orientation=500, hand_orientation_down=False, waypoints=1, realtime=True) -> None:

    """Move arm to point position within time.

            point: tuple(x, y, z)
            time: 0-65535 milliseconds
            orientation: the orientation of the hand
            hand_orientation_down: keep the hand orientation down
            waypoints: number of points through which the arm will pass (Allows a more linear movement)
            realtime: computes inverse kinematics while moving

    """

    if waypoints > 1:
        current = get_position(cartesian=True)
        step_values = [abs(p - c) / waypoints for p, c in zip(point, current)]

        if realtime:
            for i in range(1, waypoints + 1):
                way = (current[0] + (i * step_values[0]), current[1] + (i * step_values[1]), current[2] + (i * step_values[2]))

                ik = compute_ik(way, orientation, hand_orientation_down)
                move_servos((2, 3, 4, 5, 6), ik[::-1], int(time / waypoints / speed))
        else:
            iks = list()
            for i in range(1, waypoints + 1):
                way = (current[0] + (i * step_values[0]), current[1] + (i * step_values[1]), current[2] + (i * step_values[2]))
                iks.append(compute_ik(way, orientation, hand_orientation_down))

            for ik in iks:
                move_servos((2, 3, 4, 5, 6), ik[::-1], int(time / waypoints / speed))
    else:
        move_servos((2, 3, 4, 5, 6), compute_ik(point, orientation, hand_orientation_down)[::-1], int(time / speed))


def appro(point: tuple, offset: tuple) -> tuple:

    """Add offset to point.

            point: tuple(x, y, z)
            offset: tuple(x, y, z)

            return: tuple(x, y, z)

    """

    new_point = list()
    for p, o in zip(point, offset):
        new_point.append(p + o)

    return tuple(new_point)


def get_position(cartesian=False) -> tuple:

    """Return each servos position or return position in cartesian referential.

            return: tuple(j1, j2, j3, j4, j5) | jx: 0-1000
            or
            return: tuple(x, y, z)
    """

    position = get_servos_position((6, 5, 4, 3, 2))

    if not cartesian:
        return position
    else:
        return tuple(compute_fk(list(position)))


def power_on() -> None:

    """Power on each servos motor"""

    sleep(0.1)

    position = get_position()
    movej(position, 100)


def power_off() -> None:

    """Power off each servos motor"""

    sleep(0.1)
    unload_servos((1, 2, 3, 4, 5, 6))
