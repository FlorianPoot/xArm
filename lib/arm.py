from lib.servo_controller import *
from lib.cartesian import compute_ik, compute_fk
from lib.inverse_kinematics import FREE_ANGLE

import math

speed = 1


def set_speed(value: float) -> None:
    """
    Divide move time by the given value.

    :param value: 0-10
    """

    global speed

    if 0 < value <= 10:
        speed = value
    else:
        raise ValueError("speed must be greater than 0 and less or equal to 10")


def grip_open() -> None:

    """Open the grip."""

    move_servo(1, 200, int(1000 / speed))


def grip_close(value=650) -> None:
    """
    Close the grip with the given value.

    :param value: 0-1000
    """

    if not 0 <= value <= 1000:
        raise ValueError("value must be between 0 and 1000")

    move_servo(1, value, int(1000 / speed))


def movej(joint: tuple, time: int) -> None:
    """
    Move each servomotors to joint position within time.

    :param joint: tuple(j1, j2, j3, j4, j5) | jx: 0-1000
    :param time: 0-65535 milliseconds
    """

    move_servos((2, 3, 4, 5, 6), joint[::-1], int(time / speed))


def movel(point: tuple, time: int, hand_orientation=500, approach_angle=FREE_ANGLE, waypoints=1) -> None:
    """
    Move arm to point position within time.

    :param point: tuple(x, y, z)
    :param time: 0-65535 milliseconds
    :param hand_orientation: orientation of the hand
    :param approach_angle: calculates the angles considering a specific approach angle (degrees)
    :param waypoints: number of points through which the arm will pass (Allows a more linear movement)
    """

    if approach_angle != FREE_ANGLE:
        approach_angle = math.radians(approach_angle)

    if waypoints > 1:
        current = get_position(cartesian=True)
        step_values = [abs(p - c) / waypoints for p, c in zip(point, current)]

        iks = list()
        for i in range(1, waypoints + 1):
            way = (current[0] + (i * step_values[0]), current[1] + (i * step_values[1]), current[2] + (i * step_values[2]))
            iks.append(compute_ik(way, hand_orientation, approach_angle))

        for ik in iks:
            move_servos((6, 5, 4, 3, 2), ik, int(time / waypoints / speed))
    else:
        move_servos((6, 5, 4, 3, 2), compute_ik(point, hand_orientation, approach_angle), int(time / speed))


def appro(point: tuple, offset: tuple) -> tuple:
    """
    Add offset to point.

    :param point: tuple(x, y, z)
    :param offset: tuple(x, y, z)
    :return: tuple(x, y, z)
    """

    new_point = list()
    for p, o in zip(point, offset):
        new_point.append(p + o)

    return tuple(new_point)


def get_position(cartesian=False) -> tuple:
    """
    Return each servos position or return position in cartesian referential.

    :param cartesian: cartesian position ?
    :return: tuple(x, y, z) or tuple(j1, j2, j3, j4, j5) | jx: 0-1000
    """

    position = get_servos_position((6, 5, 4, 3, 2))

    for pos in position:
        if not 0 <= pos <= 1000:
            raise ValueError(f"unexpected value {pos}")

    if not cartesian:
        return position
    else:
        return compute_fk(position)


def motors_on() -> None:

    """Power on each servos motor"""

    sleep(0.1)

    position = get_position()
    movej(position, 100)


def motors_off() -> None:

    """Power off each servos motor"""

    sleep(0.1)
    unload_servos((1, 2, 3, 4, 5, 6))
