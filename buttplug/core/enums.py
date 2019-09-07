from enum import IntEnum


class ButtplugErrorCode(IntEnum):
    ERROR_UNKNOWN = 0
    ERROR_INIT = 1
    ERROR_PING = 2
    ERROR_MSG = 3
    ERROR_DEVICE = 4


class ButtplugLogLevel(object):
    off: str = "Off"
    fatal: str = "Fatal"
    error: str = "Error"
    warn: str = "Warn"
    info: str = "Info"
    debug: str = "Debug"
    trace: str = "Trace"
