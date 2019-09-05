
class ButtplugException(Exception):
    """Base Exception for Buttplug Errors.
    """
    pass


class ButtplugHandshakeException(ButtplugException):
    """Exception thrown when errors happen during initial connection
    """
    pass


class ButtplugDeviceException(ButtplugException):
    """Exception thrown when errors happen during device operations, including
    discovery, sending commands, etc.
    """
    pass


class ButtplugMessageException(ButtplugException):
    pass


class ButtplugPingException(ButtplugException):
    pass


class ButtplugUnknownException(ButtplugException):
    pass
