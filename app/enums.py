# app/enums.py
from enum import IntEnum


class Phase(IntEnum):
    STUDENT = 0
    PRACTITIONER = 1
    SENIOR = 2
    MASTER = 3


class Action(IntEnum):
    BUY = 0
    SELL = 1
