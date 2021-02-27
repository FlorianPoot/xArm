from lib.inverse_kinematics import *
import math


base = Link(0, -1.57, 1.57)
upperarm = Link(97, -1.75, 1.75)
forearm = Link(95.5, -1.75, 1.75)
hand = Link(150, -2, 2)

inverse_k = InverseK(base, upperarm, forearm, hand)


def compute_ik(target: tuple, hand_orientation=500, approach_angle=FREE_ANGLE) -> tuple:

    """Computes the inverse kinematics on a full 3D referencial"""

    ik = inverse_k.solve(target[0], target[1], target[2], approach_angle)

    # Convert radian angles to servo position
    pos = [round(math.degrees(elem) / 0.24) for elem in ik]

    # Offsets
    for i in (0, 1, 3):
        pos[i] += 500
    pos[2] = 500 - pos[2]

    if approach_angle != FREE_ANGLE:
        # Keep joint 5 align with joint 1 (base)
        pos.append(pos[0] + (500 - hand_orientation))
        """if pos[2] > 500:
            pos.append(pos[0] + (500 - orientation))
        else:
            pos.append((1000 - pos[0]) + (500 - orientation))"""
    else:
        pos.append(hand_orientation)

    # Check if arm is on target
    """fk = compute_fk(list(pos), hand_orientation_down)

    for i in range(3):
        if abs(fk[i] - target[i]) > 2:
            raise ValueError("Unreachable goal")"""

    return tuple(pos)


def compute_fk(joint: tuple) -> tuple:

    """Computes forward kinematics"""

    joint = list(joint)

    # Offsets
    for i in (0, 1, 3):
        joint[i] -= 500
    joint[2] = 500 - joint[2]

    ik = [math.radians(elem * 0.24) for elem in joint]

    # Get X and Z pos
    points = list()
    points.append((math.cos(ik[1]) * UPPERARM_LENGTH, -math.sin(ik[1]) * UPPERARM_LENGTH))
    points.append((math.cos(ik[1] + ik[2]) * FOREARM_LENGTH, -math.sin(ik[1] + ik[2]) * FOREARM_LENGTH))
    points.append((math.cos(ik[1] + ik[2] + ik[3]) * HAND_LENGTH, -math.sin(ik[1] + ik[2] + ik[3]) * HAND_LENGTH))

    fk = [0.0, 0.0, 0.0]
    for p in points:
        fk[0] += p[0]
        fk[2] += p[1]

    fk.reverse()

    # Get Y
    fk[1] = math.sin(ik[0]) * fk[0]
    # Fix X
    fk[0] = math.cos(ik[0]) * fk[0]

    return tuple([round(f) for f in fk])
