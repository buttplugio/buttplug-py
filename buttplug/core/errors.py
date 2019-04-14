class ButtplugException(Exception):
    pass

class ButtplugHandshakeException(ButtplugException):
    pass

class ButtplugDeviceException(ButtplugException):
    pass

class ButtplugMessageException(ButtplugException):
    pass

class ButtplugPingException(ButtplugException):
    pass

class ButtplugUnknownException(ButtplugException):
    pass
