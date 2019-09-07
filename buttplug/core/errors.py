class ButtplugError(Exception):
    """Base Error for Buttplug Errors.

    Attributes:

        message (str): Describes the nature of the exception
    """
    def __init__(self, message: str):
        self.message = message


class ButtplugHandshakeError(ButtplugError):
    """Error thrown when errors happen during initial connection
    """
    pass


class ButtplugDeviceError(ButtplugError):
    """Error thrown when errors happen during device operations, including
    discovery, sending commands, etc.
    """
    pass


class ButtplugMessageError(ButtplugError):
    """Error thrown when a message is incomplete or incorrectly formed."""
    pass


class ButtplugPingError(ButtplugError):
    """Error thrown when a ping timeout request from the server is not met."""
    pass


class ButtplugUnknownError(ButtplugError):
    """Unknown error, see message for more info."""
    pass
