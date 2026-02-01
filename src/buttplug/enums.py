"""Enums for Buttplug protocol types."""

import sys
from enum import IntEnum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum for Python 3.10 compatibility."""

        pass


class OutputType(StrEnum):
    """Device output types for controlling actuators."""

    VIBRATE = "Vibrate"
    ROTATE = "Rotate"
    OSCILLATE = "Oscillate"
    CONSTRICT = "Constrict"
    SPRAY = "Spray"
    TEMPERATURE = "Temperature"
    LED = "Led"
    POSITION = "Position"
    POSITION_WITH_DURATION = "HwPositionWithDuration"


class InputType(StrEnum):
    """Device input types for reading sensors."""

    BATTERY = "Battery"
    RSSI = "RSSI"
    PRESSURE = "Pressure"
    BUTTON = "Button"


class InputCommandType(StrEnum):
    """Commands for input sensors."""

    READ = "Read"
    SUBSCRIBE = "Subscribe"
    UNSUBSCRIBE = "Unsubscribe"


class ErrorCode(IntEnum):
    """Protocol error codes."""

    UNKNOWN = 0
    INIT = 1
    PING = 2
    MSG = 3
    DEVICE = 4
