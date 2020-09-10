from time import sleep

import struct
import hid


FRAME_HEADER = 0x55
CMD_SERVO_MOVE = 0x03
CMD_MULT_SERVO_UNLOAD = 0x14
CMD_MULT_SERVO_POS_READ = 0x15


device = hid.device()
device.open(0x0483, 0x5750)  # LOBOT VendorID/ProductID

print(f"Manufacturer: {device.get_manufacturer_string()}")
print(f"Product: {device.get_product_string()}")
print(f"Serial No: {device.get_serial_number_string()}")


def move_servo(servo_id: int, position: int, time: int) -> None:

    if not time > 0:
        raise ValueError("time must be greater than 0")

    position = struct.pack("<H", position)
    _time = struct.pack("<H", time)

    buf = bytearray(11)

    buf[0] = 0x00  # Hid id
    buf[1] = FRAME_HEADER
    buf[2] = FRAME_HEADER
    buf[3] = 8  # Length
    buf[4] = CMD_SERVO_MOVE
    buf[5] = 1  # Number of servo
    buf[6] = _time[0]
    buf[7] = _time[1]
    buf[8] = servo_id
    buf[9] = position[0]
    buf[10] = position[1]

    device.write(buf)
    sleep(time / 1000)


def move_servos(servos_id: tuple, positions: tuple, time: int) -> None:

    if not time > 0:
        raise ValueError("time must be greater than 0")

    length = (len(servos_id) * 3) + 6
    _time = struct.pack("<H", time)

    buf = bytearray(length + 2)  # HEADER doesn't count for length

    buf[0] = 0x00  # Hid id
    buf[1] = FRAME_HEADER
    buf[2] = FRAME_HEADER
    buf[3] = length
    buf[4] = CMD_SERVO_MOVE
    buf[5] = len(servos_id)  # Number of servo
    buf[6] = _time[0]
    buf[7] = _time[1]

    for pos, index in enumerate(range(0, len(servos_id) * 3, 3)):

        position = struct.pack("<H", positions[pos])

        buf[8 + index] = servos_id[pos]
        buf[9 + index] = position[0]
        buf[10 + index] = position[1]

    device.write(buf)
    sleep(time / 1000)


def unload_servos(servos_id: tuple) -> None:

    buf = bytearray(6 + len(servos_id))

    buf[0] = 0x00  # Hid id
    buf[1] = FRAME_HEADER
    buf[2] = FRAME_HEADER
    buf[3] = 3 + len(servos_id)
    buf[4] = CMD_MULT_SERVO_UNLOAD
    buf[5] = len(servos_id)

    for index, servo in enumerate(servos_id):
        buf[6 + index] = servo

    device.write(buf)


def get_servos_position(servos_id: tuple) -> tuple:

    buf = bytearray(6 + len(servos_id))

    buf[0] = 0x00  # Hid id
    buf[1] = FRAME_HEADER
    buf[2] = FRAME_HEADER
    buf[3] = 3 + len(servos_id)
    buf[4] = CMD_MULT_SERVO_POS_READ
    buf[5] = len(servos_id)

    for index, servo in enumerate(servos_id):
        buf[6 + index] = servo

    device.write(buf)
    sleep(0.2)

    data = bytearray(device.read(64))
    if data[:2] != b"\x55\x55" or data is None:
        raise ValueError("data don't match with what excepted")

    positions = list()
    for i in range(len(servos_id)):
        pos = data[5 + (i * 3):8 + (i * 3)]
        pos = struct.unpack("<H", pos[1:])

        positions.append(pos[0])

    return tuple(positions)
