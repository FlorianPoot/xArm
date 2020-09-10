from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink

import math
import ikpy.utils.geometry


armChain = Chain(name="arm", links=[
    OriginLink(),
    URDFLink(
        name="joint 1",
        bounds=(-math.pi / 2, math.pi / 2),
        translation_vector=[0, 0, 10],
        orientation=[0, 0, 0],
        rotation=[0, 0, 1]
    ),
    URDFLink(
        name="joint 2",
        bounds=(-math.pi / 2, math.pi / 2),
        translation_vector=[0, 0, 45],
        orientation=[0, 0, 0],
        rotation=[0, 1, 0]
    ),
    URDFLink(
        name="joint 3",
        bounds=(-1.75, 1.75),
        translation_vector=[0, 0, 97],
        orientation=[0, 0, 0],
        rotation=[0, 1, 0]
    ),
    URDFLink(
        name="joint 4",
        bounds=(-1.75, 1.75),
        translation_vector=[0, 0, 95.5],
        orientation=[0, 0, 0],
        rotation=[0, 1, 0]
    ),
    URDFLink(
        name="joint 5",
        bounds=(-math.pi / 2, math.pi / 2),
        translation_vector=[0, 0, 150],
        orientation=[0, 0, 0],
        rotation=[0, 0, 1]
    )
])

armChainHandDown = Chain(name="arm_hand_down", links=[
    OriginLink(),
    URDFLink(
        name="joint 1",
        bounds=(-math.pi / 2, math.pi / 2),
        translation_vector=[0, 0, 10],
        orientation=[0, 0, 0],
        rotation=[0, 0, 1]
    ),
    URDFLink(
        name="joint 2",
        bounds=(-math.pi / 2, math.pi / 2),
        translation_vector=[0, 0, 45],
        orientation=[0, 0, 0],
        rotation=[0, 1, 0]
    ),
    URDFLink(
        name="joint 3",
        bounds=(-1.75, 1.75),
        translation_vector=[0, 0, 97],
        orientation=[0, 0, 0],
        rotation=[0, 1, 0]
    ),
    URDFLink(
        name="joint 4",
        bounds=(-1.75, 1.75),
        translation_vector=[0, 0, 95.5],
        orientation=[0, 0, 0],
        rotation=[0, 1, 0]
    ),
    URDFLink(
        name="joint 5",
        bounds=(-math.pi / 2, math.pi / 2),
        translation_vector=[0, 0, 0],
        orientation=[0, 0, 0],
        rotation=[0, 0, 1]
    )
])


def compute_ik(target: tuple, orientation=500, hand_orientation_down=False) -> tuple:

    """Computes the inverse kinematics on a full 3D referencial"""

    if not hand_orientation_down:
        ik = armChain.inverse_kinematics(target)
    else:
        # Add height corresponding at joint 4 position
        target = list(target)
        target[2] += 150

        ik = armChainHandDown.inverse_kinematics(target)
        ik[4] = -ik[2] - ik[3] + math.pi

    # Convert radian angles to servo position
    pos = [round(math.degrees(elem) / 0.24) for elem in ik[1:]]

    # Offsets
    for i in (0, 1, 3):
        pos[i] += 500
    pos[2] = 500 - pos[2]

    # Keep joint 5 align with joint 1 (base)
    if pos[3] > 500:
        pos[4] = pos[0] + (500 - orientation)
    else:
        pos[4] = (1000 - pos[0]) + (500 - orientation)

    # Check if arm is on target
    fk = compute_fk(list(pos), hand_orientation_down)

    for i in range(3):
        if abs(fk[i] - target[i]) > 2:
            raise ValueError("Unreachable goal")

    return tuple(pos)


def compute_fk(joint: list, hand_orientation_down=False) -> list:

    """Computes forward kinematics"""

    # Offsets
    for i in (0, 1, 3):
        joint[i] -= 500
    joint[2] = 500 - joint[2]

    ik = [math.radians(elem * 0.24) for elem in joint]
    ik.insert(0, 0.)

    if not hand_orientation_down:
        fk = [round(elem, 0) for elem in ikpy.utils.geometry.from_transformation_matrix(armChain.forward_kinematics(ik))[0][:3]]
    else:
        fk = [round(elem, 0) for elem in ikpy.utils.geometry.from_transformation_matrix(armChainHandDown.forward_kinematics(ik))[0][:3]]

    return fk
