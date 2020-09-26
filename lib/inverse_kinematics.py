# Based on the CGx-InverseK distribution (https://github.com/cgxeiji/CGx-InverseK).
# Copyright (c) 2017 Eiji Onchi.

import math

PI = math.pi
HALF_PI = math.pi / 2
DOUBLE_PI = math.pi * 2
DEGREE_STEP = 0.01745329251

BASE_LENGTH = 0
UPPERARM_LENGTH = 97
FOREARM_LENGTH = 95.5
HAND_LENGTH = 150

FREE_ANGLE = 999.9


class Link:

    def __init__(self, length: float, angle_low_limit: float, angle_high_limit: float) -> None:

        self.length = length
        self.angle = 0.0

        self._angleLow = angle_low_limit
        self._angleHigh = angle_high_limit

    def in_range(self, angle: float) -> bool:
        return self._angleLow <= angle <= self._angleHigh


class InverseK:

    def __init__(self, shoulder: Link, upperarm: Link, forearm: Link, hand: Link) -> None:

        self._L0 = shoulder  # Link 0: Shoulder
        self._L1 = upperarm  # Link 1: Upperarm
        self._L2 = forearm  # Link 2: Forearm
        self._L3 = hand  # Link 3: Hand

        self._currentPhi = -DOUBLE_PI

        self._shoulder = float()
        self._elbow = float()
        self._wrist = float()

    def solve(self, x: float, y: float, z: float, phi=FREE_ANGLE):

        # Solve the angle of the base
        _r = math.sqrt(x * x + y * y)
        _base = math.atan2(y, x)

        # Check the range of the base
        if not self._L0.in_range(_base):
            # If not in range, flip the angle
            _base += PI if _base < 0 else -PI
            _r *= -1

            if phi != FREE_ANGLE:
                phi = PI - phi

        # Solve XY(RZ) for the arm plane
        if phi == FREE_ANGLE:
            if not self._solve_free_angle(_r, z - self._L0.length):
                raise ValueError("Unreachable goal")
        else:
            if not self._solve(_r, z - self._L0.length, phi):
                raise ValueError("Unreachable goal")

        # If there is a solution, return the angles
        return _base, self._shoulder, self._elbow, self._wrist

    @staticmethod
    def _cosrule(opposite: float, adjacent1: float, adjacent2: float, angle: list) -> bool:

        delta = 2 * adjacent1 * adjacent2

        if delta == 0:
            return False

        cos = (adjacent1 * adjacent1 + adjacent2 * adjacent2 - opposite * opposite) / delta

        if cos > 1 or cos < -1:
            return False

        angle[0] = math.acos(cos)

        return True

    def _solve(self, x: float, y: float, phi: float) -> bool:

        # Adjust coordinate system for base as ground plane
        _r = math.sqrt(x * x + y * y)
        _theta = math.atan2(y, x)
        _x = _r * math.cos(_theta - HALF_PI)
        _y = _r * math.sin(_theta - HALF_PI)
        _phi = phi - HALF_PI

        # Find the coordinate for the wrist
        xw = _x - self._L3.length * math.cos(_phi)
        yw = _y - self._L3.length * math.sin(_phi)

        # Get polar system
        alpha = math.atan2(yw, xw)
        r = math.sqrt(xw * xw + yw * yw)

        # Calculate the inner angle of the shoulder
        beta = [float()]
        if not self._cosrule(self._L2.length, r, self._L1.length, beta):
            return False

        # Calculate the inner angle of the elbow
        gamma = [float()]
        if not self._cosrule(r, self._L1.length, self._L2.length, gamma):
            return False

        # Solve the angles of the arm
        _shoulder = alpha - beta[0]
        _elbow = PI - gamma[0]
        _wrist = _phi - _shoulder - _elbow

        # Check the range of each hinge
        if not self._L1.in_range(_shoulder) or not self._L2.in_range(_elbow) or not self._L3.in_range(_wrist):
            # If not in range, solve for the second solution
            _shoulder += 2 * beta[0]
            _elbow *= -1
            _wrist = _phi - _shoulder - _elbow

            # Check the range for the second solution
            if not self._L1.in_range(_shoulder) or not self._L2.in_range(_elbow) or not self._L3.in_range(_wrist):
                return False

        # Return the solution
        self._shoulder = _shoulder
        self._elbow = _elbow
        self._wrist = _wrist

        return True

    def _solve_free_angle(self, x: float, y: float) -> bool:
        if self._solve(x, y, self._currentPhi):
            return True

        phi = -DOUBLE_PI
        while phi < DOUBLE_PI:
            if self._solve(x, y, phi):
                _currentPhi = phi
                return True
            phi += DEGREE_STEP

        return False


_base = Link(BASE_LENGTH, -1.57, 1.57)
_upperarm = Link(UPPERARM_LENGTH, -1.75, 1.75)
_forearm = Link(FOREARM_LENGTH, -1.75, 1.75)
_hand = Link(HAND_LENGTH, -1.75, 1.75)

inverse_k = InverseK(_base, _upperarm, _forearm, _hand)
